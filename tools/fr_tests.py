#!/usr/bin/env python3
"""
tools/fr_tests.py - Functional requirement tests on the RUNNING system (guide Step 36; proposal Table 7).

Run on the sensor (hardware lab) or the PC (virtual lab) while the backend, Zeek and the router run:
    .venv/bin/python tools/fr_tests.py --where hardware --login-file lab_hardware/keys/dashboard_login.txt \
        --conn-log /var/log/ids-zeek/conn.log --subnet 192.168.50.0/24 --camera 192.168.50.30

One test per requirement; each result is PASS, FAIL or MANUAL (a person must look), with its evidence.
The report goes to reports/fr_tests.md (and a copy with the time in reports/fr_tests/).

FR-01 Capture and flows ........ schema check of the live conn.log (tools/schema_check.py --source real)
FR-02 Class, confidence, version  every recent event has a class, a confidence in [0, 1] and the model version
FR-03 Save summaries, attacks, actions  traffic summaries, attack events and response actions exist in MongoDB
FR-04 Live dashboard ............ a logged-in Socket.IO client gets pushed messages without asking (no refresh);
                                   a client without a valid login is refused
FR-05 Inventory (Nmap) .......... an approved scan finds the lab devices; a scan outside the approved subnet is refused
FR-06 Rules: add, list, expire, remove  on the real firewall/router (a 1-minute rule on a test address)
FR-07 Allowlist, thresholds, audit  blocking an allowlisted address is refused; thresholds visible; audit records
FR-08 Export .................... filtered CSV and JSON export
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.lab_common import Api, SocketWatcher, read_login, utc_now  # noqa: E402

Result = Tuple[str, str, str, str]  # (FR, test, PASS/FAIL/MANUAL, evidence)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api", default="http://127.0.0.1:5000")
    ap.add_argument("--login-file", type=Path, required=True)
    ap.add_argument("--conn-log", type=Path, required=True, help="the live Zeek conn.log")
    ap.add_argument("--subnet", default="192.168.50.0/24", help="the approved lab subnet")
    ap.add_argument("--camera", default="192.168.50.30", help="a device the scan must find")
    ap.add_argument("--allowlisted", default="192.168.50.10", help="an allowlisted address (admin PC)")
    ap.add_argument("--test-ip", default="10.10.10.99", help="unused outside address for the rule test")
    ap.add_argument("--skip-scan", action="store_true")
    ap.add_argument("--where", choices=["hardware", "virtual"], required=True,
                    help="hardware lab or virtual lab; only a hardware-lab run writes reports/fr_tests.md")
    ap.add_argument("--source", choices=["real", "synthetic"], default="real",
                    help="where the conn.log came from (virtual lab = real Zeek on real packets)")
    args = ap.parse_args()

    api = Api(args.api)
    api.login(*read_login(args.login_file))
    res: List[Result] = []
    start = utc_now()

    # FR-01 -----------------------------------------------------------------------------------
    md = ROOT / "reports" / "fr_tests" / f"schema_check_{args.where}_{start:%Y%m%d_%H%M%S}.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "tools/schema_check.py", "--live-path", str(args.conn_log), "--source",
                        args.source, "--output-md", str(md), "--output-csv", str(md.with_suffix(".csv"))],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800)
    res.append(("FR-01", "Zeek conn.log -> adapter -> features: schema check (columns, types, nulls, ranges)",
                "PASS" if r.returncode == 0 else "FAIL",
                f"`{md.relative_to(ROOT).as_posix()}`; " + (r.stderr or r.stdout).strip().splitlines()[-1][:200]
                if (r.stderr or r.stdout).strip() else ""))

    # FR-02 -----------------------------------------------------------------------------------
    code, ev = api.call("GET", "/api/events?limit=200")
    events = ev.get("events", [])
    bad = [e.get("event_id") for e in events if not e.get("predicted_class") or e.get("confidence") is None
           or not 0.0 <= float(e["confidence"]) <= 1.0 or not e.get("model_version") or e.get("model_version") == "unknown"]
    versions = sorted({str(e.get("model_version")) for e in events})
    res.append(("FR-02", "each event has class, confidence and model version",
                "PASS" if events and not bad else ("MANUAL" if not events else "FAIL"),
                f"{len(events)} recent events; versions {versions}; incomplete: {len(bad)}"
                + ("" if events else " (run a Table 10 attack first)")))

    # FR-03 -----------------------------------------------------------------------------------
    code, s = api.call("GET", "/api/summary")
    benign = (s.get("metrics") or {}).get("benign_flows_24h", 0)
    code, acts = api.call("GET", "/api/logs/export?type=actions&format=json&limit=50", raw=True)
    try:
        n_actions = len(json.loads(acts)) if isinstance(json.loads(acts), list) else len(json.loads(acts).get("records", []))
    except (ValueError, TypeError, AttributeError):
        n_actions = -1
    res.append(("FR-03", "benign traffic summaries, attack events and response actions are saved",
                "PASS" if benign > 0 and events and n_actions != 0 else "FAIL",
                f"benign flows in 24 h: {benign:,}; attack events: {len(events)}; response actions exported: {n_actions}"))

    # FR-04 -----------------------------------------------------------------------------------
    # A real change (a manual block of an unused test address) must reach a logged-in client by
    # itself: the blocklist message at once, the Overview numbers within the 5 s push period.
    w = SocketWatcher(args.api, api.token)
    ok = w.start()
    probe_ip = "10.10.10.98"
    t0 = time.time()
    api.call("POST", "/api/blocklist", body={"ip": probe_ip, "direction": "source", "duration_minutes": 1,
                                             "reason": "FR-04 live push test"})
    while ok and time.time() - t0 < 15 and not (w.received("blocklist_update") and w.received("summary_update")):
        time.sleep(0.2)
    got_block = [e for e in w.received("blocklist_update") if (e[2] or {}).get("ip") == probe_ip]
    got_sum = w.received("summary_update")
    api.call("DELETE", f"/api/blocklist/{probe_ip}", body={"reason": "FR-04 live push test done"})
    w.stop()
    bad_w = SocketWatcher(args.api, "invalid-token")
    refused = not bad_w.start(wait=3)
    bad_w.stop()
    res.append(("FR-04", "logged-in dashboard client gets live pushes without refresh; no login = refused",
                "PASS" if ok and got_block and got_sum and refused else "FAIL",
                f"connected: {ok}; blocklist push after "
                + (f"{got_block[0][0] - t0:.2f} s" if got_block else "NONE")
                + "; summary push after " + (f"{got_sum[0][0] - t0:.2f} s" if got_sum else "NONE")
                + f"; invalid login refused: {refused}. Alert latency: tools/measure_latency.py (Step 37)."))

    # FR-05 -----------------------------------------------------------------------------------
    if args.skip_scan:
        res.append(("FR-05", "Nmap inventory of the approved subnet", "MANUAL", "skipped (--skip-scan)"))
    else:
        code_bad, _ = api.call("POST", "/api/scans", body={"subnet": "8.8.8.0/24"})
        code, sc = api.call("POST", "/api/scans", body={"subnet": args.subnet})
        scan_id = (sc.get("scan") or {}).get("scan_id")
        status = None
        for _ in range(180):
            time.sleep(5)
            code, st = api.call("GET", f"/api/scans/{scan_id}")
            status = (st.get("scan") or st).get("status")
            if status in ("completed", "failed", "error"):
                break
        code, dv = api.call("GET", "/api/devices")
        ips = sorted(d.get("ip") for d in dv.get("devices", []))
        res.append(("FR-05", "approved scan finds the lab devices; unapproved subnet refused",
                    "PASS" if status == "completed" and args.camera in ips and code_bad in (400, 403) else "FAIL",
                    f"scan status {status}; devices {ips}; scan of 8.8.8.0/24 answered {code_bad}"))

    # FR-06 -----------------------------------------------------------------------------------
    code_add, _ = api.call("POST", "/api/blocklist", body={"ip": args.test_ip, "direction": "source",
                                                           "duration_minutes": 1, "reason": "FR-06 test"})
    code, bl = api.call("GET", "/api/blocklist")
    listed = any(b.get("ip") == args.test_ip for b in bl.get("blocks", []))
    code, sync = api.call("GET", "/api/v1/firewall/sync")
    on_fw = any(r.get("ip") == args.test_ip for r in sync.get("firewall_rules", []))
    code_del, _ = api.call("DELETE", f"/api/blocklist/{args.test_ip}", body={"reason": "FR-06 remove test"})
    code, bl2 = api.call("GET", "/api/blocklist")
    removed = not any(b.get("ip") == args.test_ip for b in bl2.get("blocks", []))
    api.call("POST", "/api/blocklist", body={"ip": args.test_ip, "direction": "source", "duration_minutes": 1,
                                             "reason": "FR-06 expiry test"})
    time.sleep(85)
    code, hist = api.call("GET", f"/api/blocklist?ip={args.test_ip}")
    statuses = [h.get("status") for h in hist.get("history", [])]
    code, sync2 = api.call("GET", "/api/v1/firewall/sync")
    gone = not any(r.get("ip") == args.test_ip for r in sync2.get("firewall_rules", []))
    res.append(("FR-06", "add, list, remove, expire a rule on the firewall/router",
                "PASS" if code_add in (200, 201) and listed and on_fw and code_del == 200 and removed
                and "expired" in statuses and gone else "FAIL",
                f"add {code_add}; listed {listed}; on firewall {on_fw}; "
                f"remove {code_del}, removed {removed}; after 85 s: statuses {statuses}, gone from firewall {gone}"))

    # FR-07 -----------------------------------------------------------------------------------
    code_allow, body = api.call("POST", "/api/blocklist", body={"ip": args.allowlisted, "direction": "source",
                                                                "duration_minutes": 1, "reason": "FR-07 allowlist test"})
    code, st = api.call("GET", "/api/settings")
    sett = st.get("settings", {})
    code, logs = api.call("GET", "/api/logs?limit=200")
    evs = {l.get("event") for l in logs.get("logs", [])}
    need = {"MANUAL_BLOCK", "MANUAL_UNBLOCK"}
    res.append(("FR-07", "allowlisted address cannot be blocked; thresholds visible; audit history kept",
                "PASS" if code_allow in (400, 403, 409) and sett.get("allowlist") and need <= evs else "FAIL",
                f"block of {args.allowlisted} answered {code_allow}; allowlist {sett.get('allowlist')}; "
                f"block thresholds {sett.get('block_thresholds')}, rate-limit {sett.get('rate_limit_thresholds')}; "
                f"audit events seen: {sorted(e for e in evs if e)[:12]}"))

    # FR-08 -----------------------------------------------------------------------------------
    code_c, csv_body = api.call("GET", "/api/logs/export?type=events&format=csv&limit=100", raw=True)
    code_j, json_body = api.call("GET", f"/api/logs/export?type=system_logs&format=json&event=MANUAL_BLOCK&limit=50",
                                 raw=True)
    header = csv_body.decode("utf-8", "replace").splitlines()[0] if code_c == 200 and csv_body else ""
    res.append(("FR-08", "filtered export as CSV and JSON",
                "PASS" if code_c == 200 and "predicted_class" in header and code_j == 200 else "FAIL",
                f"CSV {code_c} ({len(csv_body or b'')} bytes, header: {header[:90]}); JSON (MANUAL_BLOCK only) {code_j}"))

    lines = [f"# Functional requirement tests, {args.where} lab (guide Step 36; proposal Table 7) - {start:%Y-%m-%d %H:%M} UTC", "",
             f"System: {args.api}; model {(s.get('system') or {}).get('model_version')}; firewall "
             f"{(s.get('system') or {}).get('firewall')} (simulated: {(s.get('system') or {}).get('firewall_simulated')}); "
             f"conn.log `{args.conn_log}` ({args.source}).", "",
             "| FR | Test | Result | Evidence |", "| --- | --- | --- | --- |"]
    lines += [f"| {fr} | {t} | **{r_}** | {e} |" for fr, t, r_, e in res]
    must = [r_ for fr, _, r_, _ in res if fr in ("FR-01", "FR-02", "FR-03", "FR-04", "FR-06", "FR-07")]
    lines += ["", f"Every \"Must\" requirement (FR-01, 02, 03, 04, 06, 07) passed: **{'yes' if all(m == 'PASS' for m in must) else 'no'}**",
              "", "A simulated firewall does not count for FR-06 (guide Part E: do not report simulation-mode blocks as real)."]
    out_dir = ROOT / "reports" / "fr_tests"
    out_dir.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines) + "\n"
    (out_dir / f"fr_tests_{args.where}_{start:%Y%m%d_%H%M%S}.md").write_text(text, encoding="utf-8")
    if args.where == "hardware":
        (ROOT / "reports" / "fr_tests.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
