#!/usr/bin/env python3
"""
lab_hardware/pack_for_sensor.py - Pack the files the sensor needs that are NOT in Git.

Run on the development PC (where the model was trained):
    .venv\\Scripts\\python.exe lab_hardware\\pack_for_sensor.py

It writes dist/sensor_files.zip with:
  - ml_engine/models/ids_bundle_v3.joblib     the trained model bundle (Step 18)
  - data/processed/train_features.parquet     the training features, for the Step 22 schema check
  - my-app/build/                             the built dashboard (served by the backend on port 5000)
  - SHA256SUMS.txt                            a checksum for every file
Copy the zip to the sensor (USB stick), then in the project folder on the sensor:
    unzip -o sensor_files.zip && sha256sum -c SHA256SUMS.txt
The lab is not connected to the internet, so the sensor cannot download these.
"""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / "ml_engine" / "models" / "ids_bundle_v3.joblib", ROOT / "data" / "processed" / "train_features.parquet"]
BUILD = ROOT / "my-app" / "build"
OUT = ROOT / "dist" / "sensor_files.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    missing = [str(p) for p in FILES if not p.exists()]
    if not (BUILD / "index.html").exists():
        missing.append(f"{BUILD} (run: cd my-app && npm run build)")
    if missing:
        sys.exit("Missing:\n  " + "\n  ".join(missing))
    items = list(FILES) + sorted(p for p in BUILD.rglob("*") if p.is_file())
    OUT.parent.mkdir(exist_ok=True)
    sums = []
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in items:
            rel = p.relative_to(ROOT).as_posix()
            z.write(p, rel)
            sums.append(f"{sha256(p)}  {rel}")
        z.writestr("SHA256SUMS.txt", "\n".join(sums) + "\n")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB, {len(items)} files)")
    for line in sums[:2]:
        print("  " + line)


if __name__ == "__main__":
    main()
