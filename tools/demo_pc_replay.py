"""tools/demo_pc_replay.py - Show the whole detection and response path on the development PC.

THIS IS A PC DEMONSTRATION, NOT A LAB RESULT.

What it does:
  1. Takes real Zeek records from IoT-23 scenario CTU-IoT-Malware-Capture-34-1. This is the
     held-out scenario: the model never trained on it.
  2. Writes them as a Zeek JSON conn.log, in Zeek's own line order (empty fields are left out,
     as Zeek does), with the times moved to "now".
  3. Sends the file through the real project code:
        ZeekAdapter (read, direction, window memory)  ->  Detector (26 features: 19 one-flow +
        7 window, D-051; then the model)  ->  DecisionEngine (alert / block thresholds)
        ->  ResponsePolicy (safety checks)  ->  SimulationAdapter (firewall; nothing is really
        blocked)  ->  MongoDB
  4. Prints what happened, step by step.

The window features describe what the same source did in the last 60 seconds, so the demo
replays whole streams, not a thin sample (a sample would remove the pattern the model looks for).

Scenarios:
  A. The whole scenario 34-1 (23,145 records), as the live sensor would receive it. The infected
     device is shown as the lab camera 192.168.50.30; its attacks go OUT to the internet, as in IoT-23.
  B. Like proposal Table 10, row 2: an outside host probes the camera network (IN to the network).
     All 122 real PortScan records of 34-1 are used, with their original timing; the source becomes
     the outside host and each original target becomes a lab address. Note: in 34-1 these records
     go to only 2 targets, so this is NOT a real network-wide (Nmap) scan; that is tested in the lab.
  C. Safety: the same records from the allowlisted admin PC must never be blocked.

Only IP addresses and times are changed; the other fields are the original IoT-23 values.
Results are written to a separate MongoDB database (default `iot_ids_demo`), which is emptied
at the start. The real project database is not touched.

Run:  .venv\\Scripts\\python.exe tools\\demo_pc_replay.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging  # noqa: E402

logging.disable(logging.WARNING)  # keep the demo output readable; errors still show

from core_engine.db_service import DatabaseService  # noqa: E402
from core_engine.decision_engine import DecisionEngine  # noqa: E402
from core_engine.detector import Detector  # noqa: E402
from core_engine.firewall.simulation_adapter import SimulationAdapter  # noqa: E402
from core_engine.zeek_adapter import ZeekAdapter  # noqa: E402

SCENARIO = ROOT / "data" / "interim" / "CTU-IoT-Malware-Capture-34-1.parquet"
SETTINGS = ROOT / "config" / "settings.yaml"

CAMERA = "192.168.50.30"       # lab camera (local network)
ROUTER = "192.168.50.1"        # lab router (allowlisted)
ADMIN_PC = "192.168.50.10"     # admin workstation (allowlisted)
ATTACKER = "10.10.10.50"       # attack computer on the "outside" lab network (not in local_networks)
IP_MAP = {"192.168.1.195": CAMERA, "192.168.1.1": ROUTER}
LAB_TARGETS = [f"192.168.50.{i}" for i in range(100, 250)]  # scan targets inside the camera LAN

ZEEK_FIELDS = ["ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p", "proto", "service",
               "duration", "orig_bytes", "resp_bytes", "conn_state", "local_orig", "local_resp",
               "missed_bytes", "history", "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes"]
CLASS_ORDER = ["Benign", "PortScan", "DDoS_DoS", "CnC", "Malware_Download"]
PRESENT = ["Benign", "PortScan", "DDoS_DoS", "CnC"]


def zeek_json_line(row: dict) -> str:
    """One Zeek JSON conn.log line. Zeek leaves out fields that are not set ('-')."""
    out = {}
    for k in ZEEK_FIELDS:
        v = row.get(k)
        if v is None or (isinstance(v, float) and math.isnan(v)) or v in ("-", "unknown", "(empty)"):
            continue
        if isinstance(v, (np.integer,)):
            v = int(v)
        elif isinstance(v, (np.floating,)):
            v = float(v)
        out[k] = v
    return json.dumps(out)


def write_conn_log(rows: pd.DataFrame, path: Path, start_ts: float) -> None:
    """Write rows as a Zeek conn.log in the given order, keeping their spacing in time (moved to now)."""
    first = float(rows["ts"].min())
    with open(path, "w", encoding="utf-8") as fh:
        for rec in rows.to_dict("records"):
            rec["ts"] = start_ts + (float(rec["ts"]) - first)
            fh.write(zeek_json_line(rec) + "\n")


def build_engine(db, auto_response: bool):
    """The real DecisionEngine with the real model, the lab settings and the simulation firewall."""
    settings = yaml.safe_load(open(SETTINGS, encoding="utf-8"))
    settings.setdefault("response", {})["auto_response"] = auto_response  # in memory only
    settings["response"]["adapter"] = "simulation"
    tmp = Path(tempfile.mkdtemp(prefix="ids_demo_")) / "settings.yaml"
    tmp.write_text(yaml.safe_dump(settings), encoding="utf-8")
    detector = Detector()
    firewall = SimulationAdapter(allowlist=set(settings.get("allowlist", [])),
                                 max_rule_minutes=int(settings["response"].get("max_rule_minutes", 30)))
    engine = DecisionEngine(db_service=db, settings_path=tmp, detector=detector, firewall_adapter=firewall)
    return engine, firewall, settings


def new_adapter() -> ZeekAdapter:
    """A fresh Zeek adapter (empty window memory), as after starting the sensor."""
    return ZeekAdapter(settings_path=SETTINGS, enable_state_persistence=False)


def run_file(engine: DecisionEngine, adapter: ZeekAdapter, path: Path, batch=100):
    """Like the live runner: read up to `batch` lines, decide on them, then read the next lines."""
    flows, outcomes, pending = [], [], []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            rec = adapter.parse_and_enrich(raw)
            if rec:
                pending.append(rec)
            if len(pending) >= batch:
                flows.extend(pending)
                outcomes.extend(engine.process_flows(pending))
                pending = []
    if pending:
        flows.extend(pending)
        outcomes.extend(engine.process_flows(pending))
    return flows, outcomes


def line(char="-"):
    print(char * 78)


def show_thresholds(engine: DecisionEngine):
    print("Thresholds from the model bundle (Step 17; D-040, D-046, D-051):")
    print(f"  {'class':18s} {'alert at':>9s} {'block at':>9s}")
    for c in CLASS_ORDER[1:]:
        t = engine.thresholds.get(c, {}) or {}
        a, b = t.get("passive_alert_threshold"), t.get("active_response_threshold")
        print(f"  {c:18s} {a if a is not None else '-':>9} {b if b is not None else 'alert only':>9}")
    p = engine.policy
    print(f"  Block rule: same target {p.min_repeats} times within {p.repeat_window_seconds} s; "
          f"rule ends after {p.max_rule_minutes} min. Allowlist: {', '.join(sorted(p.allowlist))}")


def scenario_a(engine, firewall, df):
    line("=")
    print("SCENARIO A - The whole held-out scenario 34-1, as the live sensor would receive it")
    print(f"  The infected device {list(IP_MAP)[0]} is shown as the lab camera {CAMERA}.")
    print("  In IoT-23 its attacks go OUT from the infected device to the internet.")
    line("=")
    rows = df[df["class_name"].isin(CLASS_ORDER)].reset_index(drop=True)  # Zeek's own line order
    for col in ("id.orig_h", "id.resp_h"):
        rows[col] = rows[col].map(lambda ip: IP_MAP.get(ip, ip))
    path = Path(tempfile.mkdtemp(prefix="ids_demo_")) / "conn_A.log"
    write_conn_log(rows, path, time.time())
    print(f"Wrote all {len(rows):,} records as a Zeek log: {path}")

    t0 = time.time()
    flows, outs = run_file(engine, new_adapter(), path)
    secs = time.time() - t0
    print(f"Processed {len(outs):,} flows in {secs:.1f} s ({len(outs) / max(secs, 1e-9):,.0f} flows/s, "
          f"MongoDB writes included). Direction: {dict(Counter(f['traffic_direction'] for f in flows))}")

    true = rows["class_name"].tolist()
    pred = [o.predicted_class for o in outs]
    print("\n1) What the MODEL said (rows = true IoT-23 label, columns = model's class):")
    print(f"  {'true / predicted':18s}" + "".join(f"{c[:9]:>10s}" for c in CLASS_ORDER) + f"{'correct':>9s}")
    for c in PRESENT:
        idx = [i for i, t in enumerate(true) if t == c]
        cnt = Counter(pred[i] for i in idx)
        print(f"  {c:18s}" + "".join(f"{cnt.get(k, 0):>10,d}" for k in CLASS_ORDER)
              + f"{cnt.get(c, 0) / max(1, len(idx)):>8.0%}")

    print("\n2) What the SYSTEM did with each flow (by true label):")
    acts = ["BENIGN_SUMMARY", "LOW_CONFIDENCE_IGNORE", "ALERT_ONLY", "ACTIVE_BLOCK_CANDIDATE"]
    names = {"BENIGN_SUMMARY": "benign", "LOW_CONFIDENCE_IGNORE": "too unsure",
             "ALERT_ONLY": "alert", "ACTIVE_BLOCK_CANDIDATE": "block cand."}
    print(f"  {'true label':18s}" + "".join(f"{names[a]:>13s}" for a in acts))
    for c in PRESENT:
        idx = [i for i, t in enumerate(true) if t == c]
        cnt = Counter(outs[i].action for i in idx)
        print(f"  {c:18s}" + "".join(f"{cnt.get(a, 0):>13,d}" for a in acts))

    print("\n3) Block candidates and the safety checks (by model class -> result):")
    reasons = Counter((o.predicted_class, getattr(o, "response_reason", None) or "-", o.response_status)
                      for o in outs if o.action == "ACTIVE_BLOCK_CANDIDATE")
    if not reasons:
        print("  (no block candidates)")
    for (cls, r, st), n in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {n:6,d} x {cls:10s} -> {r:32s} status={st}")

    rules = firewall.list_active()
    print(f"\n4) Firewall rules made (simulation; nothing really blocked): {len(rules)}")
    for r in rules[:10]:
        # The TRUE IoT-23 labels of the flows to/from this address, so a wrong-class block is visible.
        to_ip = rows[(rows["id.resp_h"] == r["ip"]) | (rows["id.orig_h"] == r["ip"])]["class_name"]
        labels = ", ".join(f"{k} {v:,d}" for k, v in to_ip.value_counts().items())
        print(f"  BLOCK {r['ip']:16s} direction={r['direction']:4s} for {r['duration_minutes']} min  reason={r['reason']}")
        print(f"        true IoT-23 labels of its flows: {labels or '-'}")
    if len(rules) > 10:
        print(f"  ... and {len(rules) - 10} more")
    cam_blocked = any(r["ip"] == CAMERA for r in rules)
    print(f"  The camera {CAMERA} itself blocked: {'YES (wrong!)' if cam_blocked else 'no (correct: local devices are protected)'}")

    lat = [o.pipeline_latency_ms for o in outs if o.pipeline_latency_ms is not None]
    if lat:
        print(f"\n5) Time from reading a flow to the decision (on this PC, batches of 100 as in the live runner): "
              f"median {np.median(lat):.0f} ms, 95th percentile {np.percentile(lat, 95):.0f} ms "
              f"(proposal target: < 2 s and < 5 s)")
    return outs


def scan_rows(df, src):
    """All real PortScan records of 34-1 (Zeek order, original timing); source -> src; target -> lab address."""
    rows = df[df["class_name"] == "PortScan"].copy().reset_index(drop=True)
    targets = {ip: LAB_TARGETS[i % len(LAB_TARGETS)] for i, ip in enumerate(dict.fromkeys(rows["id.resp_h"]))}
    rows["id.orig_h"] = src
    rows["id.resp_h"] = rows["id.resp_h"].map(targets)
    return rows


def scenario_scan(engine, firewall, df, src, title):
    line("=")
    print(title)
    line("=")
    rows = scan_rows(df, src)
    span = rows["ts"].max() - rows["ts"].min()
    print(f"  {len(rows)} real PortScan records to {rows['id.resp_h'].nunique()} different lab addresses, over {span:,.0f} s.")
    path = Path(tempfile.mkdtemp(prefix="ids_demo_")) / "conn_scan.log"
    write_conn_log(rows, path, time.time())
    flows, outs = run_file(engine, new_adapter(), path, batch=1)
    conf = np.array([o.confidence for o in outs if o.predicted_class == "PortScan"])
    print(f"  Model said PortScan for {len(conf)} of {len(outs)} records "
          f"(confidence: median {np.median(conf) if len(conf) else 0:.2f}, max {conf.max() if len(conf) else 0:.2f}).")
    print(f"  Actions: {dict(Counter(o.action for o in outs))}")
    shown = 0
    for i, (f, o) in enumerate(zip(flows, outs), 1):
        if o.action == "ACTIVE_BLOCK_CANDIDATE" or i <= 3:
            res = o.response_status
            if getattr(o, "response_reason", None):
                res = f"{o.response_status} ({o.response_reason})"
            print(f"  #{i:<3d} {f['traffic_direction']:8s} {o.predicted_class:10s} conf {o.confidence:.2f}  "
                  f"{o.action:23s} {res}")
            shown += 1
            if shown >= 8:
                break
    rules = [r for r in firewall.list_active() if r["ip"] == src]
    print(f"  Firewall rules for {src}: {len(rules)}")
    for r in rules:
        print(f"  BLOCK {r['ip']} direction={r['direction']} for {r['duration_minutes']} min  reason={r['reason']}")
    return outs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db-name", default="iot_ids_demo", help="MongoDB database for the demo (emptied first)")
    args = ap.parse_args()
    if args.db_name == "iot_ids_db":
        sys.exit("Refusing to use the main database. Choose another --db-name.")

    df = pd.read_parquet(SCENARIO)
    db = DatabaseService(db_name=args.db_name)
    if db.client is None:
        sys.exit("MongoDB is not running. Start the MongoDB service and try again.")
    db.client.drop_database(args.db_name)
    db = DatabaseService(db_name=args.db_name)  # reconnect: creates the collections and indexes

    engine, firewall, settings = build_engine(db, auto_response=True)

    line("=")
    print("PC DEMONSTRATION - not a lab result (see the notes at the end)")
    print(f"Model bundle: {engine.detector.get_model_info().get('model_version', '?')}   "
          f"Firewall: {firewall.name} (simulated)   Database: {args.db_name}")
    print("auto_response is switched ON for this run only (settings.yaml is not changed).")
    show_thresholds(engine)

    scenario_a(engine, firewall, df)
    scenario_scan(engine, firewall, df, ATTACKER,
                  f"SCENARIO B - Outside host {ATTACKER} probes the camera LAN (the 122 PortScan records of 34-1)")
    scenario_scan(engine, firewall, df, ADMIN_PC,
                  f"SCENARIO C - The same records from the allowlisted admin PC {ADMIN_PC} (must never be blocked)")

    line("=")
    blocks = db.get_active_blocks()
    print(f"Saved in MongoDB `{args.db_name}`: active blocks: {len(blocks)}")
    for b in blocks[:10]:
        print(f"  {b.get('ip')}  direction={b.get('direction')}  reason={b.get('reason')}  expires={b.get('expires_at')}")
    line("=")
    print("NOTES")
    print("  - Real IoT-23 records from the held-out scenario; only IPs and times were changed.")
    print("  - Zeek itself did not run here; the records are written in Zeek's JSON format.")
    print("  - The firewall is the simulation adapter: no real traffic was blocked.")
    print("  - The real test is in the lab (Steps 19-22 and 35-39): real camera, real Zeek, real attacks.")


if __name__ == "__main__":
    main()
