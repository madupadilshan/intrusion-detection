#!/usr/bin/env python3
"""
IoT-23 Dataset Manifest Generator (Step 7)
==========================================

This script processes all raw IoT-23 dataset files in `data/raw/iot23/`,
computes cryptographic SHA-256 checksums, counts flow rows, extracts label
distributions, maps each file to its corresponding official CTU scenario ID,
and outputs the definitive audit record: `reports/dataset_manifest.csv`.

Memory Safety:
  Processes all files using line-by-line streaming chunks so peak RAM
  utilization remains under 100 MB, safely within the 11.7 GB host RAM limit.

Research Proposal Alignment:
  - Objective O1: Standardized, reproducible flow-based dataset pipeline.
  - Section 3.2: Formal dataset audit and scenario tracking.
"""

import os
import sys
import time
import json
import hashlib
import datetime
from pathlib import Path
from collections import Counter
from typing import Dict, Tuple, Any, List

# Official 1-to-1 mapping between Kaggle/extracted CSVs and CTU IoT-23 scenarios
SCENARIO_MAP: Dict[str, str] = {
    "dataset1.csv": "CTU-Honeypot-Capture-4-1",
    "dataset2.csv": "CTU-Honeypot-Capture-5-1",
    "dataset3.csv": "CTU-Honeypot-Capture-7-1",
    "dataset4.csv": "CTU-IoT-Malware-Capture-8-1",
    "dataset5.csv": "CTU-IoT-Malware-Capture-9-1",
    "dataset6.csv": "CTU-IoT-Malware-Capture-7-1",
    "dataset7.csv": "CTU-IoT-Malware-Capture-60-1",
    "dataset8.csv": "CTU-IoT-Malware-Capture-52-1",
    "dataset9.csv": "CTU-IoT-Malware-Capture-49-1",
    "dataset10.csv": "CTU-IoT-Malware-Capture-48-1",
    "dataset11.csv": "CTU-IoT-Malware-Capture-44-1",
    "dataset12.csv": "CTU-IoT-Malware-Capture-43-1",
    "dataset13.csv": "CTU-IoT-Malware-Capture-42-1",
    "dataset14.csv": "CTU-IoT-Malware-Capture-39-1",
    "dataset15.csv": "CTU-IoT-Malware-Capture-35-1",
    "dataset16.csv": "CTU-IoT-Malware-Capture-36-1",
    "dataset17.csv": "CTU-IoT-Malware-Capture-34-1",
    "dataset18.csv": "CTU-IoT-Malware-Capture-33-1",
    "dataset19.csv": "CTU-IoT-Malware-Capture-3-1",
    "dataset20.csv": "CTU-IoT-Malware-Capture-21-1",
    "dataset21.csv": "CTU-IoT-Malware-Capture-20-1",
    "dataset22.csv": "CTU-IoT-Malware-Capture-17-1",
    "dataset23.csv": "CTU-IoT-Malware-Capture-1-1",
}


def process_dataset_file(file_path: Path) -> Dict[str, Any]:
    """
    Process a single dataset file line-by-line to compute:
      - SHA-256 hash across the exact byte stream
      - Total data flow rows
      - Exact counts per (label, detailed-label)
      - Date of first flow
    """
    hasher = hashlib.sha256()
    label_counter: Counter = Counter()
    total_rows = 0
    first_ts = None
    file_size_bytes = file_path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    start_time = time.time()
    print(f"--> Processing {file_path.name} ({file_size_mb:,.2f} MB)...", flush=True)

    with open(file_path, "rb") as f:
        # 1. Header line
        header = f.readline()
        hasher.update(header)

        # 2. Stream all data rows
        for line in f:
            hasher.update(line)
            total_rows += 1

            # Extract last comma section containing label and detailed-label
            last_comma = line.rfind(b",")
            if last_comma != -1:
                tail = line[last_comma + 1:].split()
                if len(tail) >= 2:
                    lbl = tail[1].decode("utf-8", errors="ignore")
                    det = b" ".join(tail[2:]).decode("utf-8", errors="ignore") if len(tail) > 2 else "-"
                    label_counter[(lbl, det)] += 1

            # Check timestamp on first row
            if first_ts is None and total_rows == 1:
                try:
                    parts = line.split(b",", 1)
                    first_ts = float(parts[0])
                except Exception:
                    pass

    elapsed = time.time() - start_time
    rate = total_rows / elapsed if elapsed > 0 else 0
    sha256_hex = hasher.hexdigest()

    date_str = (
        datetime.datetime.fromtimestamp(first_ts).strftime("%Y-%m-%d")
        if first_ts
        else "N/A"
    )

    benign_count = sum(
        count for (lbl, _), count in label_counter.items()
        if lbl.lower() == "benign"
    )
    malicious_count = total_rows - benign_count

    # Format detailed label breakdown
    breakdown = {
        f"{lbl}::{det}": count
        for (lbl, det), count in sorted(label_counter.items())
    }

    print(
        f"    Done {file_path.name}: {total_rows:,} rows in {elapsed:.1f}s "
        f"({rate:,.0f} rows/s) | SHA256: {sha256_hex[:12]}...",
        flush=True
    )

    scenario_id = SCENARIO_MAP.get(file_path.name, file_path.stem)

    return {
        "scenario_id": scenario_id,
        "file_name": file_path.name,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "sha256": sha256_hex,
        "total_rows": total_rows,
        "benign_rows": benign_count,
        "malicious_rows": malicious_count,
        "start_date": date_str,
        "label_breakdown": json.dumps(breakdown),
    }


def generate_manifest(raw_dir: Path, output_file: Path) -> List[Dict[str, Any]]:
    """
    Scan raw_dir, process all dataset CSV files in order, and write manifest.
    """
    raw_files = sorted(
        raw_dir.glob("dataset*.csv"),
        key=lambda p: int(p.stem.replace("dataset", "")) if p.stem.replace("dataset", "").isdigit() else p.name
    )

    if not raw_files:
        # Check for conn.log.labeled files
        raw_files = sorted(raw_dir.rglob("conn.log.labeled*"))

    if not raw_files:
        print(f"[ERROR] No dataset files found in {raw_dir}")
        sys.exit(1)

    print(f"\n============================================================")
    print(f"IoT-23 Dataset Manifest Generation")
    print(f"Raw Directory: {raw_dir}")
    print(f"Found {len(raw_files)} scenario files to process.")
    print(f"============================================================\n")

    overall_start = time.time()
    manifest_records: List[Dict[str, Any]] = []

    for idx, fpath in enumerate(raw_files, start=1):
        print(f"[{idx}/{len(raw_files)}]", end=" ")
        record = process_dataset_file(fpath)
        manifest_records.append(record)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV output
    headers = [
        "scenario_id",
        "file_name",
        "file_size_bytes",
        "file_size_mb",
        "sha256",
        "total_rows",
        "benign_rows",
        "malicious_rows",
        "start_date",
        "label_breakdown",
    ]

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(",".join(headers) + "\n")
        for rec in manifest_records:
            # Escape JSON string for CSV
            breakdown_escaped = '"' + rec["label_breakdown"].replace('"', '""') + '"'
            row = [
                rec["scenario_id"],
                rec["file_name"],
                str(rec["file_size_bytes"]),
                str(rec["file_size_mb"]),
                rec["sha256"],
                str(rec["total_rows"]),
                str(rec["benign_rows"]),
                str(rec["malicious_rows"]),
                rec["start_date"],
                breakdown_escaped,
            ]
            out.write(",".join(row) + "\n")

    overall_elapsed = time.time() - overall_start
    total_all_rows = sum(r["total_rows"] for r in manifest_records)
    total_all_bytes = sum(r["file_size_bytes"] for r in manifest_records)

    print(f"\n============================================================")
    print(f"Manifest Generated Successfully: {output_file}")
    print(f"Total Scenarios Processed: {len(manifest_records)}")
    print(f"Total Disk Size:           {total_all_bytes / (1024**3):.2f} GB")
    print(f"Total Connection Flows:    {total_all_rows:,}")
    print(f"Total Processing Time:     {overall_elapsed:.1f} seconds ({overall_elapsed/60:.2f} minutes)")
    print(f"============================================================\n")

    return manifest_records


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    raw_directory = project_root / "data" / "raw" / "iot23"
    manifest_csv = project_root / "reports" / "dataset_manifest.csv"

    records = generate_manifest(raw_directory, manifest_csv)

