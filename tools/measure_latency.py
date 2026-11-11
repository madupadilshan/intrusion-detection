#!/usr/bin/env python3
"""
tools/measure_latency.py - Measure speed and resource use (guide Step 37; proposal Table 9, RQ4, O6).

Run on the sensor while the system runs, once under normal load and once under attack load:
    .venv/bin/python tools/measure_latency.py --label normal --seconds 600
    .venv/bin/python tools/measure_latency.py --label attack --seconds 300   (start a Table 10 attack meanwhile)

It logs in like the dashboard and listens to the live Socket.IO messages, so "dashboard" times are
the times a logged-in dashboard really received the alert. Every second it also records the flows
per second (pipeline status) and the CPU and memory of Zeek and the IDS backend (psutil).

Times reported (median and 95th percentile; proposal target: median decision < 2 s, 95th < 5 s):
  A. Zeek wait:            flow end (ts + duration) -> the adapter reads the Zeek line.
                           Zeek writes a flow only when the connection ends or times out (guide Step 19).
  B. Read -> decision:     adapter read -> detector -> decision engine.
  C. Decision -> dashboard: decision -> the Socket.IO message arrives here.
  D. Read -> dashboard:    B + C (the system's own part of the delay).
  E. Flow end -> dashboard: A + D (what an operator sees after a connection ends).
  F. First alert -> rule active: first alert of an event -> its block/rate-limit message
                           (includes waiting for the repeats in the time window, proposal 3.4).
Dropped events: Zeek's capture_loss.log and stats.log (sensor/local.zeek), and the adapter counters.
Clocks: all times come from the sensor's own clock, so no clock sync is needed.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.lab_common import Api, SocketWatcher, read_login, utc_now  # noqa: E402

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


def pct(vals: List[float], q: float) -> Optional[float]:
    if not vals:
        return None
    v = sorted(vals)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def fmt(v: Optional[float]) -> str:
    return "—" if v is None else f"{v:.3f}"


def find_procs() -> Dict[str, List[Any]]:
    out: Dict[str, List[Any]] = {"zeek": [], "ids_backend": []}
    if psutil is None:
        return out
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            cmd = " ".join(p.info.get("cmdline") or [])
            if (p.info.get("name") or "").startswith("zeek"):
                out["zeek"].append(p)
            elif "core_engine.app" in cmd:
                out["ids_backend"].append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    for plist in out.values():
        for p in plist:
            try:
                p.cpu_percent(None)
            except psutil.Error:
                pass
    return out


def zeek_loss(log_dir: Path, since: float) -> Dict[str, Any]:
    res: Dict[str, Any] = {"capture_loss_max_percent": None, "pkts_dropped": None, "files_found": []}
    for name in ("capture_loss.log", "stats.log"):
        f = log_dir / name
        if not f.exists():
            continue
        res["files_found"].append(name)
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if float(r.get("ts", 0)) < since:
                continue
            if name == "capture_loss.log" and r.get("percent_lost") is not None:
                res["capture_loss_max_percent"] = max(res["capture_loss_max_percent"] or 0.0, float(r["percent_lost"]))
            if name == "stats.log" and r.get("pkts_dropped") is not None:
                res["pkts_dropped"] = (res["pkts_dropped"] or 0) + int(r["pkts_dropped"])
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="e.g. normal, attack-scan, attack-ddos")
    ap.add_argument("--seconds", type=float, default=300)
    ap.add_argument("--api", default="http://127.0.0.1:5000")
    ap.add_argument("--login-file", type=Path, default=ROOT / "lab_hardware" / "keys" / "dashboard_login.txt")
    ap.add_argument("--zeek-log-dir", type=Path, default=Path("/var/log/ids-zeek"))
    ap.add_argument("--out-dir", type=Path, default=ROOT / "reports" / "performance")
    args = ap.parse_args()
    args.out_dir = (args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir).resolve()
    args.zeek_log_dir = args.zeek_log_dir if args.zeek_log_dir.is_absolute() else ROOT / args.zeek_log_dir
    args.login_file = args.login_file if args.login_file.is_absolute() else ROOT / args.login_file

    api = Api(args.api)
    api.login(*read_login(args.login_file))
    watcher = SocketWatcher(args.api, api.token)
    if not watcher.start():
        sys.exit(f"Socket.IO connection refused: {watcher.refused}")
    procs = find_procs()
    t0, start = time.time(), utc_now()
    samples: List[Dict[str, Any]] = []
    last_flows: Optional[int] = None
    print(f"measuring '{args.label}' for {args.seconds:.0f} s (processes: "
          f"zeek {len(procs['zeek'])}, backend {len(procs['ids_backend'])}) ...")
    while time.time() - t0 < args.seconds:
        time.sleep(1.0)
        code, st = api.call("GET", "/api/v1/pipeline/status")
        m = st.get("metrics", {}) or {}
        flows = int(m.get("flows_processed") or 0)
        row: Dict[str, Any] = {"t": round(time.time() - t0, 1),
                               "flows_per_s": (flows - last_flows) if last_flows is not None else None}
        last_flows = flows
        for key, plist in procs.items():
            cpu = mem = 0.0
            for p in plist:
                try:
                    cpu += p.cpu_percent(None)
                    mem += p.memory_info().rss / 1e6
                except Exception:
                    pass
            row[f"{key}_cpu_percent"], row[f"{key}_mem_mb"] = round(cpu, 1), round(mem, 1)
        samples.append(row)
    watcher.stop()

    A: List[float] = []
    B: List[float] = []
    C: List[float] = []
    first_alert: Dict[str, float] = {}
    for recv, name, data in watcher.received("new_event"):
        ts = (data or {}).get("timestamps") or {}
        feats = (data or {}).get("features") or {}
        try:
            adapter, decision = float(ts["adapter_ts"]), float(ts["decision_ts"])
        except (KeyError, TypeError, ValueError):
            continue
        B.append(decision - adapter)
        C.append(recv - decision)
        if ts.get("zeek_ts") is not None:
            flow_end = float(ts["zeek_ts"]) + float(feats.get("duration") or 0.0)
            A.append(max(0.0, adapter - flow_end))
        if data.get("event_id"):
            first_alert.setdefault(str(data["event_id"]), recv)
    D = [b + c for b, c in zip(B, C)]
    E = [a + d for a, d in zip(A, D)] if len(A) == len(D) else []
    F = [recv - first_alert[str(d.get("event_id"))] for recv, _, d in watcher.received("blocklist_update")
         if d and str(d.get("event_id")) in first_alert]
    summaries = watcher.received("summary_update")
    loss = zeek_loss(args.zeek_log_dir, t0)
    code, st = api.call("GET", "/api/v1/pipeline/status")

    fps = [s["flows_per_s"] for s in samples if s["flows_per_s"] is not None]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = f"{start:%Y%m%d_%H%M%S}"
    csv_path = args.out_dir / f"samples_{args.label}_{stamp}.csv"
    keys = list(samples[0].keys()) if samples else ["t"]
    csv_path.write_text(",".join(keys) + "\n" + "\n".join(",".join("" if s.get(k) is None else str(s.get(k))
                                                                     for k in keys) for s in samples) + "\n",
                        encoding="utf-8")
    md = [f"# Speed and resource use: {args.label} ({start:%Y-%m-%d %H:%M} UTC, {args.seconds:.0f} s)", "",
          "Guide Step 37; proposal Table 9 (latency, throughput/resources), RQ4. Measured on the sensor's own clock; "
          "the dashboard times are when a logged-in Socket.IO client (this tool) received the message.", "",
          "| Time (seconds) | Alerts | Median | 95th percentile | Max |", "| --- | ---: | ---: | ---: | ---: |"]
    for label, vals in (("A. Zeek wait (flow end -> line read)", A), ("B. Read -> decision", B),
                        ("C. Decision -> dashboard", C), ("D. Read -> dashboard (system part)", D),
                        ("E. Flow end -> dashboard", E), ("F. First alert -> rule active", F)):
        md.append(f"| {label} | {len(vals)} | {fmt(pct(vals, 0.5))} | {fmt(pct(vals, 0.95))} | "
                  f"{fmt(max(vals) if vals else None)} |")
    med_d, p95_d = pct(D, 0.5), pct(D, 0.95)
    md += ["", f"- Proposal target (median decision < 2 s, 95th percentile < 5 s) on D: "
           + ("**not measured (no alerts in this run)**" if med_d is None else
              f"**{'met' if med_d < 2 and p95_d < 5 else 'not met'}** (median {med_d:.3f} s, 95th {p95_d:.3f} s)"),
           f"- Flows per second: median {fmt(pct(fps, 0.5))}, max {fmt(max(fps) if fps else None)}; "
           f"flows processed in total: {(st.get('metrics') or {}).get('flows_processed')}",
           f"- Dashboard summary messages received: {len(summaries)} (FR-04: the Overview updates without refresh)",
           f"- Zeek capture loss (max % in the run): {loss['capture_loss_max_percent']}; packets dropped (stats.log): "
           f"{loss['pkts_dropped']}; Zeek logs found: {', '.join(loss['files_found']) or 'none'}",
           "", "| Process | CPU % median | CPU % max | Memory MB max |", "| --- | ---: | ---: | ---: |"]
    for key in ("zeek", "ids_backend"):
        cpu = [s[f"{key}_cpu_percent"] for s in samples]
        mem = [s[f"{key}_mem_mb"] for s in samples]
        md.append(f"| {key} | {fmt(pct(cpu, 0.5))} | {fmt(max(cpu) if cpu else None)} | {fmt(max(mem) if mem else None)} |")
    md += ["", f"Raw samples (every second): `{csv_path.relative_to(ROOT.resolve()).as_posix() if str(csv_path).startswith(str(ROOT.resolve())) else csv_path}`.",
           "Note: A depends on Zeek's timeouts (a long video stream is written only when it ends); it is reported, "
           "not hidden (guide Step 37 item 3)."]
    out = args.out_dir / f"performance_{args.label}_{stamp}.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nreport: {out}")


if __name__ == "__main__":
    main()
