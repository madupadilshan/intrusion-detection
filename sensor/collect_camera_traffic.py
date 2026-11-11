"""sensor/collect_camera_traffic.py - Synthetic Benign IP-Camera Traffic Baseline Generator.

Governing Standards & Disclosure:
- Group 03 Proposal: Sections 1.6, 2.3, 3.4 (Level 3 Baseline), 5.1; Table 11; Hypothesis H1 (FPR <= 5%)
- Step-by-Step Guide: Step 20 (Benign camera traffic baseline for development)
- Ethics & Retention: Decision D-010, D-011 (Metadata only - zero raw video payload stored)
- Disclosure (Decision D-038): This script generates a SYNTHETIC benign baseline
  statistically modeled after Tapo C200 activity distributions for software pipeline
  development and schema verification on Windows. Hardware wire capture and live RTSP
  verification are scheduled under Step 20b/Step 35 using physical hardware or MediaMTX simulator.

This module:
1. Generates realistic multi-session benign camera traffic test profiles
   modeled after the Tapo C200 1080p RTSP/H.264 camera environment (Proposal 5.1).
2. Simulates 5 distinct operational camera sessions:
   - RTSP 1080p H.264 video streaming to NVR (TCP 554 / RTP UDP 30000+)
   - Camera Web/API management & live preview (HTTP 80 / HTTPS 443)
   - Device discovery & announcements (ONVIF WS-Discovery UDP 3702, SSDP UDP 1900, mDNS UDP 5353)
   - Network time synchronization (NTP UDP 123) and DNS resolution (UDP 53)
   - Background TCP keep-alive polling & telemetry
3. Saves synthetic flow logs to `data/local/synthetic/<date>/conn.log` (real lab captures go to `data/local/benign/`).
4. Checks ANY conn.log with evaluate_camera_baseline_fpr(data_source="real"|"synthetic"). Only a REAL
   lab capture counts for Hypothesis H1; synthetic data is a software test, never a result.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.features import FEATURE_COLUMNS, make_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("collect_camera_traffic")

# Standard lab network IP allocation (Proposal 3.8, Step 4, settings.yaml)
DEFAULT_CAMERA_IP = "192.168.50.30"   # lab plan, Section 3
DEFAULT_NVR_IP = "192.168.50.20"     # lab plan; on the allowlist
DEFAULT_GATEWAY_IP = "192.168.50.1"
DEFAULT_ADMIN_PC_IP = "192.168.50.10"
DEFAULT_SENSOR_IP = "192.168.50.5"


def generate_camera_flow(
    session_type: str,
    base_ts: float,
    camera_ip: str = DEFAULT_CAMERA_IP,
    nvr_ip: str = DEFAULT_NVR_IP,
    gateway_ip: str = DEFAULT_GATEWAY_IP,
    admin_pc_ip: str = DEFAULT_ADMIN_PC_IP,
) -> Dict[str, Any]:
    """Generate a single Zeek conn.log JSON record for a specific benign camera activity."""
    uid = f"C{''.join(random.choices('0123456789ABCDEFabcdef', k=17))}"
    jitter = random.uniform(0.001, 0.999)
    ts = round(base_ts + jitter, 6)

    if session_type == "rtsp_streaming":
        # Continuous RTSP TCP 554 / H.264 video streaming from Tapo C200 to NVR
        duration = round(random.uniform(5.0, 120.0), 4)
        fps = random.choice([15, 20, 25, 30])
        # Video payload packet rate: 80 - 160 pkts/sec for 1080p 2-3 Mbps
        resp_pkts = int(duration * random.uniform(60, 140))
        # NVR send ACK/RTCP: 15 - 30 pkts/sec
        orig_pkts = int(duration * random.uniform(15, 35))
        # Video frames: 1000 - 1420 bytes/pkt
        resp_bytes = int(resp_pkts * random.uniform(900, 1380))
        orig_bytes = int(orig_pkts * random.uniform(52, 90))

        return {
            "ts": ts,
            "uid": uid,
            "id.orig_h": nvr_ip,
            "id.orig_p": random.randint(49152, 65535),
            "id.resp_h": camera_ip,
            "id.resp_p": 554,
            "proto": "tcp",
            "service": "rtsp",
            "duration": duration,
            "orig_bytes": orig_bytes,
            "resp_bytes": resp_bytes,
            "conn_state": "SF",
            "local_orig": True,
            "local_resp": True,
            "missed_bytes": 0,
            "history": "ShADadFf",
            "orig_pkts": orig_pkts,
            "orig_ip_bytes": orig_bytes + (orig_pkts * 40),
            "resp_pkts": resp_pkts,
            "resp_ip_bytes": resp_bytes + (resp_pkts * 40),
        }

    elif session_type == "camera_web_api":
        # Admin / App HTTP REST API management (live preview / status check)
        duration = round(random.uniform(0.05, 1.20), 4)
        orig_pkts = random.randint(4, 15)
        resp_pkts = random.randint(6, 25)
        orig_bytes = random.randint(300, 1800)
        resp_bytes = random.randint(1200, 12000)

        return {
            "ts": ts,
            "uid": uid,
            "id.orig_h": admin_pc_ip,
            "id.orig_p": random.randint(49152, 65535),
            "id.resp_h": camera_ip,
            "id.resp_p": random.choice([80, 443, 8080]),
            "proto": "tcp",
            "service": "http" if random.random() > 0.3 else "ssl",
            "duration": duration,
            "orig_bytes": orig_bytes,
            "resp_bytes": resp_bytes,
            "conn_state": "SF",
            "local_orig": True,
            "local_resp": True,
            "missed_bytes": 0,
            "history": "ShADdfFa",
            "orig_pkts": orig_pkts,
            "orig_ip_bytes": orig_bytes + (orig_pkts * 40),
            "resp_pkts": resp_pkts,
            "resp_ip_bytes": resp_bytes + (resp_pkts * 40),
        }

    elif session_type == "device_discovery":
        # ONVIF WS-Discovery (UDP 3702), SSDP (UDP 1900), or mDNS (UDP 5353)
        disc_proto = random.choice([("3702", "onvif"), ("1900", "ssdp"), ("5353", "dns")])
        port_num = int(disc_proto[0])
        service_name = disc_proto[1]
        duration = round(random.uniform(0.01, 0.15), 4)
        orig_bytes = random.randint(180, 650)
        resp_bytes = random.randint(0, 450)
        orig_pkts = random.randint(1, 3)
        resp_pkts = 1 if resp_bytes > 0 else 0

        return {
            "ts": ts,
            "uid": uid,
            "id.orig_h": random.choice([camera_ip, admin_pc_ip, nvr_ip]),
            "id.orig_p": random.randint(49152, 65535),
            "id.resp_h": random.choice(["239.255.255.250", "224.0.0.251", camera_ip]),
            "id.resp_p": port_num,
            "proto": "udp",
            "service": service_name,
            "duration": duration,
            "orig_bytes": orig_bytes,
            "resp_bytes": resp_bytes,
            "conn_state": "SF" if resp_pkts > 0 else "OTH",
            "local_orig": True,
            "local_resp": True,
            "missed_bytes": 0,
            "history": "Dd",
            "orig_pkts": orig_pkts,
            "orig_ip_bytes": orig_bytes + (orig_pkts * 28),
            "resp_pkts": resp_pkts,
            "resp_ip_bytes": resp_bytes + (resp_pkts * 28),
        }

    elif session_type == "dns_ntp_support":
        # DNS query or NTP time sync
        is_ntp = random.random() > 0.5
        if is_ntp:
            duration = round(random.uniform(0.01, 0.08), 4)
            return {
                "ts": ts,
                "uid": uid,
                "id.orig_h": camera_ip,
                "id.orig_p": random.randint(50000, 60000),
                "id.resp_h": gateway_ip,
                "id.resp_p": 123,
                "proto": "udp",
                "service": "ntp",
                "duration": duration,
                "orig_bytes": 48,
                "resp_bytes": 48,
                "conn_state": "SF",
                "local_orig": True,
                "local_resp": True,
                "missed_bytes": 0,
                "history": "Dd",
                "orig_pkts": 1,
                "orig_ip_bytes": 76,
                "resp_pkts": 1,
                "resp_ip_bytes": 76,
            }
        else:
            duration = round(random.uniform(0.01, 0.05), 4)
            return {
                "ts": ts,
                "uid": uid,
                "id.orig_h": camera_ip,
                "id.orig_p": random.randint(50000, 60000),
                "id.resp_h": gateway_ip,
                "id.resp_p": 53,
                "proto": "udp",
                "service": "dns",
                "duration": duration,
                "orig_bytes": random.randint(32, 64),
                "resp_bytes": random.randint(72, 180),
                "conn_state": "SF",
                "local_orig": True,
                "local_resp": True,
                "missed_bytes": 0,
                "history": "Dd",
                "orig_pkts": 1,
                "orig_ip_bytes": 70,
                "resp_pkts": 1,
                "resp_ip_bytes": 140,
            }

    else:
        # Background keep-alive polling
        duration = round(random.uniform(0.05, 0.50), 4)
        return {
            "ts": ts,
            "uid": uid,
            "id.orig_h": camera_ip,
            "id.orig_p": random.randint(49152, 65535),
            "id.resp_h": gateway_ip,
            "id.resp_p": 80,
            "proto": "tcp",
            "service": "http",
            "duration": duration,
            "orig_bytes": 140,
            "resp_bytes": 380,
            "conn_state": "SF",
            "local_orig": True,
            "local_resp": True,
            "missed_bytes": 0,
            "history": "ShADfFa",
            "orig_pkts": 3,
            "orig_ip_bytes": 260,
            "resp_pkts": 4,
            "resp_ip_bytes": 540,
        }


def collect_benign_camera_traffic(
    output_dir: Path,
    total_flows: int = 5000,
    session_weights: Optional[Dict[str, float]] = None,
    date_str: Optional[str] = None,
) -> Path:
    """Generate and record benign IP-camera network traffic flows matching Tapo C200 activities.

    Args:
        output_dir: Root directory for synthetic test logs (`data/local/synthetic`).
        total_flows: Number of flow records to collect.
        session_weights: Proportions for each activity type.
        date_str: Subfolder date string (default: current UTC date).

    Returns:
        Path to the generated conn.log file.
    """
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    target_dir = output_dir / date_str
    target_dir.mkdir(parents=True, exist_ok=True)
    conn_log_path = target_dir / "conn.log"

    if session_weights is None:
        session_weights = {
            "rtsp_streaming": 0.55,       # Dominant continuous video transmission
            "camera_web_api": 0.20,       # Periodic admin access & live view
            "device_discovery": 0.12,     # ONVIF / SSDP discovery probes
            "dns_ntp_support": 0.08,      # Clock sync & DNS
            "background_keepalive": 0.05, # Background polling
        }

    session_types = list(session_weights.keys())
    weights = list(session_weights.values())

    start_ts = time.time() - (total_flows * 0.5)
    records: List[Dict[str, Any]] = []

    logger.info("Generating %d benign IP-camera connection flows...", total_flows)
    with open(conn_log_path, "w", encoding="utf-8") as f:
        for i in range(total_flows):
            chosen_type = random.choices(session_types, weights=weights, k=1)[0]
            current_ts = start_ts + (i * 0.45)
            record = generate_camera_flow(chosen_type, current_ts)
            records.append(record)
            f.write(json.dumps(record) + "\n")

    logger.info("Saved %d benign camera flow records to %s", len(records), conn_log_path)
    return conn_log_path


def _flagged(probs: np.ndarray, thresholds: Dict[str, Any], key: str) -> np.ndarray:
    """Flows flagged at a threshold level, with the same rule as the decision engine:
    the top class is an attack class AND its probability >= that class threshold."""
    pred = np.argmax(probs, axis=1)
    conf = probs.max(axis=1)
    flags = np.zeros(len(pred), dtype=bool)
    for idx, name in enumerate(CLASS_NAMES):
        if idx == 0:
            continue
        t = (thresholds.get(name) or {}).get(key)
        if t is not None:
            flags |= (pred == idx) & (conf >= float(t))
    return flags


CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]


def evaluate_camera_baseline_fpr(
    conn_log_path: Path,
    bundle_path: Path = Path("ml_engine/models/ids_bundle_v3.joblib"),
    report_output_path: Path = Path("reports/experiments/camera_baseline_summary.md"),
    csv_output_path: Path = Path("reports/experiments/camera_baseline_summary.csv"),
    data_source: str = "synthetic",
) -> Dict[str, Any]:
    """Measure how many benign camera flows the deployed model calls an attack.

    data_source:
        "real"      - captured by Zeek from the lab camera (or approved simulator) on the
                      mirror port. Only this counts for Hypothesis H1 (FPR <= 5%).
        "synthetic" - made by generate_camera_flow() for software testing. NOT evidence.
    """
    if data_source not in ("real", "synthetic"):
        raise ValueError("data_source must be 'real' or 'synthetic'")
    bundle = joblib.load(bundle_path)
    calibrated = bundle["calibrated_model"]
    thresholds = bundle["operational_thresholds"]

    records = []
    skipped = 0
    with open(conn_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                skipped += 1
    df_raw = pd.DataFrame(records)
    total_flows = len(df_raw)
    if total_flows == 0:
        raise ValueError(f"No flows found in {conn_log_path}")

    feat_df = make_features(df_raw)
    nan_count = int(feat_df.isna().sum().sum())
    probs = calibrated.predict_proba(feat_df)
    preds = np.argmax(probs, axis=1)

    false_alarms = int((preds != 0).sum())
    raw_fpr = false_alarms / total_flows
    alert_flags = _flagged(probs, thresholds, "passive_alert_threshold")
    block_flags = _flagged(probs, thresholds, "active_response_threshold")
    breakdown = {CLASS_NAMES[int(k)]: int(v) for k, v in pd.Series(preds).value_counts().sort_index().items()}
    proto_dist = df_raw["proto"].value_counts().to_dict() if "proto" in df_raw else {}
    service_dist = df_raw["service"].value_counts().to_dict() if "service" in df_raw else {}

    is_real = data_source == "real"
    h1_result = ("met" if raw_fpr <= 0.05 else "not met") if is_real else "not tested (synthetic data)"
    summary = {
        "conn_log_path": str(conn_log_path),
        "data_source": data_source,
        "total_camera_flows": total_flows,
        "skipped_lines": skipped,
        "feature_nan_count": nan_count,
        "false_alarm_count": false_alarms,
        "raw_fpr": raw_fpr,
        "alert_count": int(alert_flags.sum()),
        "alert_rate": float(alert_flags.mean()),
        "block_candidate_count": int(block_flags.sum()),
        "block_candidate_rate": float(block_flags.mean()),
        "predicted_class_counts": breakdown,
        "h1_fpr_result": h1_result,
        "proto_distribution": proto_dist,
        "service_distribution": service_dist,
    }
    logger.info(
        "Flows: %d | predicted as attack: %d (%.3f%%) | alerts: %d | block candidates: %d | H1: %s",
        total_flows, false_alarms, raw_fpr * 100, summary["alert_count"], summary["block_candidate_count"], h1_result,
    )

    csv_output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {"metric": "data_source", "value": data_source},
        {"metric": "total_camera_flows", "value": total_flows},
        {"metric": "false_alarm_flows", "value": false_alarms},
        {"metric": "benign_fpr", "value": f"{raw_fpr:.5f}"},
        {"metric": "alert_rate", "value": f"{summary['alert_rate']:.5f}"},
        {"metric": "block_candidate_rate", "value": f"{summary['block_candidate_rate']:.5f}"},
        {"metric": "h1_fpr_result", "value": h1_result},
    ]).to_csv(csv_output_path, index=False)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_real:
        source_line = "**Data source:** REAL capture — Zeek `conn.log` from the lab mirror port (metadata only)"
        note = (
            "This is the Level 3 measurement for Hypothesis H1 (FPR <= 5% on the local IP-camera traffic we control). "
            "Write the camera model (or simulator name), the capture dates and the activities in the lab logbook."
        )
    else:
        source_line = "**Data source:** SYNTHETIC — made by `generate_camera_flow()` for software testing (decision D-038)"
        note = (
            "**This is not a measurement.** The flows were made by a script, not captured from a camera. They only show "
            "that the pipeline runs end to end. They are not evidence for Hypothesis H1, and they must not be reported as results."
        )
    lines = [
        "# Benign Camera Traffic Check (Step 20)",
        "",
        source_line + "  ",
        f"**File:** `{conn_log_path}`  ",
        f"**Model bundle:** `{bundle_path}`  ",
        f"**Generated:** {now_str}",
        "",
        "> " + note,
        "",
        "## Results",
        "",
        "| Measure | Value | Proposal target |",
        "| --- | ---: | --- |",
        f"| Flows checked | {total_flows:,} | — |",
        f"| Benign flows predicted as an attack (FPR) | {raw_fpr * 100:.3f}% ({false_alarms:,} / {total_flows:,}) | <= 5% (H1) → **{h1_result}** |",
        f"| Flows that would raise an alert | {summary['alert_rate'] * 100:.3f}% ({summary['alert_count']:,}) | reported |",
        f"| Flows that reach a block threshold | {summary['block_candidate_rate'] * 100:.3f}% ({summary['block_candidate_count']:,}) | reported (a block also needs the policy checks) |",
        f"| Missing values after feature making | {nan_count} | 0 |",
        "",
        "Predicted classes: " + ", ".join(f"{k} {v:,}" for k, v in breakdown.items()),
        "",
        "Protocols: " + ", ".join(f"{k} {v:,}" for k, v in proto_dist.items()),
        "",
        "Services: " + ", ".join(f"{k} {v:,}" for k, v in service_dist.items()),
        "",
        "Only connection metadata is used; no video or audio is stored (proposal 3.8). "
        "Keep periods follow `docs/ethics/data_retention_plan.md`.",
        "",
    ]
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    report_output_path.write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> None:
    """Command line.

    Real lab capture (Step 20):
        python sensor/collect_camera_traffic.py --conn-log /var/log/ids-zeek/conn.log --source real
    Synthetic software test only:
        python sensor/collect_camera_traffic.py --generate-synthetic --count 5000
    """
    parser = argparse.ArgumentParser(description="Step 20: check benign camera traffic against the model.")
    parser.add_argument("--conn-log", type=Path, help="Zeek conn.log (JSON lines) to check.")
    parser.add_argument("--source", choices=["real", "synthetic"], help="Where the conn.log came from.")
    parser.add_argument("--generate-synthetic", action="store_true",
                        help="Make a synthetic conn.log first (software test only; never a result).")
    parser.add_argument("--output-dir", type=Path, default=Path("data/local/synthetic"))
    parser.add_argument("--count", type=int, default=5000)
    parser.add_argument("--bundle-path", type=Path, default=Path("ml_engine/models/ids_bundle_v3.joblib"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/experiments/camera_baseline_summary.md"))
    parser.add_argument("--csv-path", type=Path, default=Path("reports/experiments/camera_baseline_summary.csv"))
    args = parser.parse_args()

    if args.generate_synthetic:
        conn_log_path = collect_benign_camera_traffic(output_dir=args.output_dir, total_flows=args.count)
        source = "synthetic"
    else:
        if args.conn_log is None or args.source is None:
            parser.error("give --conn-log and --source (real|synthetic), or use --generate-synthetic")
        conn_log_path, source = args.conn_log, args.source
    evaluate_camera_baseline_fpr(conn_log_path, args.bundle_path, args.report_path, args.csv_path, data_source=source)


if __name__ == "__main__":
    main()
