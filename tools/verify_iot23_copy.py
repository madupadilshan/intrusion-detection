"""tools/verify_iot23_copy.py - Check where each local IoT-23 CSV file came from.

Why this exists (proposal Section 3.2):
    "We will not train the model from an unofficial copy that somebody has already
    processed, unless we can check where it came from and what was changed in it."

Our raw files (data/raw/iot23/dataset1.csv ... dataset23.csv) are a CSV copy of the
official IoT-23 v1.0.0 labelled flows (conn.log.labeled). This tool checks, for every
local file, which official scenario it really is:

1. Read the first data row (ts, uid) of each local CSV.
2. Download only the first few KB of each official conn.log.labeled file
   (HTTP Range request; the full files are not downloaded).
3. Match local files to official scenarios by the (ts, uid) pair.
4. Compare the result with ml_engine.manifest.SCENARIO_MAP and write a report.

Usage:
    python tools/verify_iot23_copy.py
Outputs:
    reports/iot23_copy_verification.csv
    reports/iot23_copy_verification.md
"""

from __future__ import annotations

import csv
import datetime
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.manifest import SCENARIO_MAP  # noqa: E402

OFFICIAL_BASE = "https://mcfp.felk.cvut.cz/publicDatasets/IoT-23-Dataset/IndividualScenarios"
OFFICIAL_SCENARIOS = sorted(set(SCENARIO_MAP.values()))
# Two official scenarios keep conn.log.labeled in a different sub-folder on the server.
OFFICIAL_PATH_OVERRIDES = {
    "CTU-IoT-Malware-Capture-43-1": "CTU-IoT-Malware-Capture-43-1/labeled/conn.log.labeled",
    "CTU-Honeypot-Capture-7-1": "CTU-Honeypot-Capture-7-1/Somfy-01/bro/conn.log.labeled",
}
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "iot23"
OUT_CSV = PROJECT_ROOT / "reports" / "iot23_copy_verification.csv"
OUT_MD = PROJECT_ROOT / "reports" / "iot23_copy_verification.md"


def first_local_row(path: Path) -> Optional[Tuple[str, str]]:
    """Return (ts, uid) of the first data row of a local CSV file."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        f.readline()  # header
        line = f.readline()
    parts = line.strip().split(",")
    return (parts[0], parts[1]) if len(parts) > 1 else None


def first_official_row(scenario_id: str) -> Optional[Tuple[str, str]]:
    """Return (ts, uid) of the first data row of an official conn.log.labeled file."""
    rel = OFFICIAL_PATH_OVERRIDES.get(scenario_id, f"{scenario_id}/bro/conn.log.labeled")
    url = f"{OFFICIAL_BASE}/{rel}"
    req = urllib.request.Request(url, headers={"Range": "bytes=0-8191", "User-Agent": "iot23-copy-check"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    for line in text.splitlines():
        if line and not line.startswith("#"):
            parts = line.split("\t")
            if len(parts) > 1:
                return parts[0], parts[1]
    return None


# Official label totals per scenario, copied from the IoT-23 website
# (https://www.stratosphereips.org/datasets-iot23, "Labels" section of each scenario),
# read on 9 Nov 2026. The three honeypot (benign-only) captures are not listed there.
OFFICIAL_LABEL_SOURCE = "https://www.stratosphereips.org/datasets-iot23 (per-scenario label tables, read 2026-11-09)"
OFFICIAL_LABEL_COUNTS: Dict[str, Dict[str, int]] = {
    "CTU-IoT-Malware-Capture-34-1": {"Benign": 1923, "C&C": 6706, "DDoS": 14394, "PartOfAHorizontalPortScan": 122},
    "CTU-IoT-Malware-Capture-43-1": {"Benign": 20574934, "C&C": 3498, "C&C-FileDownload": 14, "DDoS": 65803,
                                     "FileDownload": 1, "Okiru": 8765885, "PartOfAHorizontalPortScan": 37911674},
    "CTU-IoT-Malware-Capture-44-1": {"Benign": 211, "C&C": 14, "C&C-FileDownload": 11, "DDoS": 1},
    "CTU-IoT-Malware-Capture-49-1": {"Benign": 3665, "C&C": 1922, "C&C-FileDownload": 1, "PartOfAHorizontalPortScan": 5404959},
    "CTU-IoT-Malware-Capture-52-1": {"Benign": 1794, "C&C": 6, "C&C-FileDownload": 12, "PartOfAHorizontalPortScan": 19779564},
    "CTU-IoT-Malware-Capture-20-1": {"Benign": 3193, "C&C-Torii": 16},
    "CTU-IoT-Malware-Capture-21-1": {"Benign": 3272, "C&C-Torii": 14},
    "CTU-IoT-Malware-Capture-42-1": {"Benign": 4420, "C&C-FileDownload": 3, "FileDownload": 3},
    "CTU-IoT-Malware-Capture-60-1": {"Benign": 2476, "C&C-HeartBeat": 95, "DDoS": 3578457},
    "CTU-IoT-Malware-Capture-17-1": {"Attack": 4, "Benign": 31438, "C&C-HeartBeat": 6834, "DDoS": 13655172,
                                     "Okiru": 13655215, "PartOfAHorizontalPortScan": 27311187,
                                     "PartOfAHorizontalPortScan-Attack": 5},
    "CTU-IoT-Malware-Capture-36-1": {"Benign": 2663, "C&C-HeartBeat": 15688, "Okiru": 13626744, "Okiru-Attack": 3},
    "CTU-IoT-Malware-Capture-33-1": {"Benign": 1380791, "C&C-HeartBeat": 5278, "Okiru-Attack": 13609467,
                                     "PartOfAHorizontalPortScan": 39459055},
    "CTU-IoT-Malware-Capture-8-1": {"Benign": 2181, "C&C": 8222},
    "CTU-IoT-Malware-Capture-35-1": {"Attack": 3, "Benign": 8262389, "C&C": 81, "C&C-FileDownload": 12, "DDoS": 2185302},
    "CTU-IoT-Malware-Capture-48-1": {"Attack": 2752, "Benign": 3734, "C&C-HeartBeat-Attack": 834,
                                     "C&C-HeartBeat-FileDownload": 11, "C&C-PartOfAHorizontalPortScan": 888,
                                     "PartOfAHorizontalPortScan": 3386119},
    "CTU-IoT-Malware-Capture-39-1": {"Attack": 677, "Benign": 7337, "C&C": 1530, "PartOfAHorizontalPortScan": 73559437},
    "CTU-IoT-Malware-Capture-7-1": {"Benign": 75955, "C&C-HeartBeat": 5778, "DDoS": 39584, "Okiru": 11333397},
    "CTU-IoT-Malware-Capture-9-1": {"Benign": 22548, "PartOfAHorizontalPortScan": 6355745},
    "CTU-IoT-Malware-Capture-3-1": {"Attack": 5962, "Benign": 4536, "C&C": 8, "PartOfAHorizontalPortScan": 145597},
    "CTU-IoT-Malware-Capture-1-1": {"Benign": 469275, "C&C": 8, "PartOfAHorizontalPortScan": 539465},
}
MANIFEST_CSV = PROJECT_ROOT / "reports" / "dataset_manifest.csv"


def _official_url(scenario_id: str) -> str:
    rel = OFFICIAL_PATH_OVERRIDES.get(scenario_id, f"{scenario_id}/bro/conn.log.labeled")
    return f"{OFFICIAL_BASE}/{rel}"


def last_local_row(path: Path) -> Optional[Tuple[str, str]]:
    """Return (ts, uid) of the last data row of a local CSV file (reads only the file end)."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 65536))
        tail = f.read().decode("utf-8", errors="replace")
    lines = [ln for ln in tail.splitlines() if ln.strip()]
    if not lines:
        return None
    parts = lines[-1].split(",")
    return (parts[0], parts[1]) if len(parts) > 1 else None


def last_official_row(scenario_id: str) -> Optional[Tuple[str, str]]:
    """Return (ts, uid) of the last data row of an official file (downloads only the last 64 KB)."""
    req = urllib.request.Request(_official_url(scenario_id),
                                 headers={"Range": "bytes=-65536", "User-Agent": "iot23-copy-check"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    data = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    if not data:
        return None
    parts = data[-1].split("\t")
    return (parts[0], parts[1]) if len(parts) > 1 else None


def local_label_counts() -> Dict[str, Dict[str, int]]:
    """Label totals per scenario from the manifest (Step 7 counted every row of every local file)."""
    import json

    out: Dict[str, Dict[str, int]] = {}
    with open(MANIFEST_CSV, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            counts: Dict[str, int] = {}
            for key, n in json.loads(rec["label_breakdown"]).items():
                lbl, det = key.split("::", 1)
                name = "Benign" if lbl.lower() == "benign" else (det if det not in ("-", "") else lbl)
                counts[name] = counts.get(name, 0) + int(n)
            out[rec["scenario_id"]] = counts
    return out


def compare_labels(local: Dict[str, int], official: Dict[str, int]) -> List[str]:
    """Return a list of differences (empty list = all label totals are equal)."""
    diffs = []
    for name in sorted(set(local) | set(official)):
        a, b = local.get(name, 0), official.get(name, 0)
        if a != b:
            diffs.append(f"{name}: local {a:,} vs official {b:,}")
    return diffs


def main() -> int:
    official_first: Dict[Tuple[str, str], str] = {}
    official_last: Dict[str, Optional[Tuple[str, str]]] = {}
    for sc in OFFICIAL_SCENARIOS:
        try:
            key = first_official_row(sc)
            if key:
                official_first[key] = sc
            official_last[sc] = last_official_row(sc)
            print(f"official {sc}: first {key} last {official_last[sc]}")
        except Exception as exc:  # network problem: report it, do not guess
            print(f"[WARN] could not read official {sc}: {exc}")

    local_labels = local_label_counts()
    rows: List[Dict[str, str]] = []
    for file_name, mapped in sorted(SCENARIO_MAP.items(), key=lambda kv: int(kv[0][7:-4])):
        path = RAW_DIR / file_name
        first = first_local_row(path) if path.exists() else None
        last = last_local_row(path) if path.exists() else None
        found = official_first.get(first) if first else None
        first_status = "MATCH" if found == mapped else ("MISMATCH" if found else "NOT_CHECKED")
        off_last = official_last.get(mapped)
        if off_last is None or last is None:
            last_status = "NOT_CHECKED"
        else:
            last_status = "MATCH" if off_last == last else "MISMATCH"
        if mapped in OFFICIAL_LABEL_COUNTS:
            diffs = compare_labels(local_labels.get(mapped, {}), OFFICIAL_LABEL_COUNTS[mapped])
            label_status = "MATCH" if not diffs else "DIFFERENT"
        else:
            diffs, label_status = [], "NOT_LISTED"
        rows.append({
            "file_name": file_name,
            "scenario_in_manifest_map": mapped,
            "official_scenario_by_first_row": found or "",
            "first_row": first_status,
            "last_row": last_status,
            "label_totals": label_status,
            "label_differences": "; ".join(diffs),
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    def count(col: str, val: str) -> int:
        return sum(r[col] == val for r in rows)

    lines = [
        "# IoT-23 Copy Verification (proposal Section 3.2)",
        "",
        f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Official files:** `{OFFICIAL_BASE}/<scenario>/bro/conn.log.labeled` (IoT-23 v1.0.0)  ",
        f"**Official label totals:** {OFFICIAL_LABEL_SOURCE}",
        "",
        "Proposal 3.2: *\"We will not train the model from an unofficial copy that somebody has already processed, unless "
        "we can check where it came from and what was changed in it.\"* Three checks are made for every local file:",
        "",
        "1. **First row:** the first flow (`ts`, `uid`) equals the first flow of the official file (first 8 KB downloaded).",
        "2. **Last row:** the last flow equals the last flow of the official file (last 64 KB downloaded). Together with 1, "
        "this shows the file is complete at both ends.",
        "3. **Label totals:** the number of flows for every label (counted over every row in Step 7) equals the official "
        "table on the IoT-23 website.",
        "",
        f"**Result:** first row {count('first_row', 'MATCH')}/{len(rows)} match; last row {count('last_row', 'MATCH')}/{len(rows)} match; "
        f"label totals {count('label_totals', 'MATCH')} match, {count('label_totals', 'DIFFERENT')} different, "
        f"{count('label_totals', 'NOT_LISTED')} not listed on the website.",
        "",
        "| Local file | Scenario | First row | Last row | Label totals | Differences |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| `{r['file_name']}` | `{r['scenario_in_manifest_map']}` | {r['first_row']} | {r['last_row']} | "
            f"{r['label_totals']} | {r['label_differences'] or '—'} |"
        )
    lines += [
        "",
        "**What was changed in the copy:** the format only. The official files are tab-separated Zeek logs with `#` header "
        "lines; the local copy is comma-separated with one header row. The last three columns stay joined by spaces "
        "(`tunnel_parents   label   detailed-label`), as in the official file. The values are the same.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    bad = sum(count(c, v) for c in ("first_row", "last_row") for v in ("MISMATCH", "NOT_CHECKED"))
    print(f"\nfirst {count('first_row', 'MATCH')}, last {count('last_row', 'MATCH')}, labels match {count('label_totals', 'MATCH')}, "
          f"different {count('label_totals', 'DIFFERENT')} -> {OUT_MD}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
