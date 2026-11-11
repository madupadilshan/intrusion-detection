# Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning

**Bachelor of Information and Communication Technology Honours Degree**  
Department of Information and Communication Technology  
Faculty of Technology, University of Sri Jayewardenepura  

---

## Overview

This repository contains the prototype implementation of a real-time network intrusion detection and automated response system (NIDS/IPS) tailored for small IP-camera IoT networks.

* **Traffic Analytics:** Zeek (`conn.log`) connection flow processing.
* **Classifier:** Random Forest model trained on the IoT-23 benchmark dataset, with 19 one-flow features and 8 window features (what the same source did in the last 60 s, and failed tries to the same destination in the last hour; decisions D-051, D-052). Model v3.0.0: held-out macro-F1 0.66 (5 classes) / 0.82 (classes present); the proposal target 0.85 is not met. Program downloads are checked by a separate rule on Zeek's files.log (D-052). A virtual lab (`lab_virtual/`, D-053) runs the whole system on real packets with Docker.
* **Target Classes (5):** Benign, DDoS/DoS, Port Scan, Command & Control (C&C), Malware/Download.
* **Active Response:** `nftables` rules on the lab router (passive mode) or on the sensor (inline mode), only when the safety rules pass (`docs/response_policy.md`); every rule expires and the admin can unblock by hand. Automatic response is off by default.
* **Management & Visualization:** Unified Flask & Socket.IO backend with a real-time React dashboard and MongoDB audit store.

---

## See it work on the PC

With MongoDB running, this sends real IoT-23 records (held-out scenario 34-1) through the whole system
(Zeek reader, features, model, decision, safety checks, simulation firewall, MongoDB) and prints each step:

```
.venv\Scripts\python.exe tools\demo_pc_replay.py
```

It uses a separate database (`iot_ids_demo`) and does not change `config/settings.yaml`. It is a demonstration,
not a lab result (decision D-050).

## Documentation

* [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md): the master guide (Steps 0-42), from setup to evaluation. Follow the steps in order.
* [`docs/requirements_checklist.md`](docs/requirements_checklist.md): the proposal requirements and their status.
* [`reports/experiments/model_card.md`](reports/experiments/model_card.md): the current model results.
* [`docs/archive/`](docs/archive/README.md): old explanation documents and the old command log, kept only as a record (out of date; archived 9 Nov 2026, D-049).
* [`PROJECT_PROGRESS_AND_CHALLENGES.md`](PROJECT_PROGRESS_AND_CHALLENGES.md): dated work log, open issues and next steps.
* [`docs/decision_log.md`](docs/decision_log.md): every project decision (D-001 onward).

**Status (8 Nov 2026):** the software is built and tested on the development PC. The lab parts are not done yet: Zeek on the Linux sensor, our own benign camera traffic (Level 3), and the 6 test scenarios of proposal Table 10. The only camera traffic file so far is synthetic test data and is not a result.

---

## Directory Structure

```
.
├── config/                  # Lab settings, allowlists, and frozen label mapping
├── data/                    # Dataset storage (raw IoT-23, interim, processed, local captures)
├── ml_engine/               # Feature extraction, training, validation, and exported models
├── core_engine/             # Unified Flask backend, Socket.IO, DB service, and firewall manager
├── sensor/                  # Zeek and nftables configuration scripts
├── tools/                   # Schema validation, admin creation, and latency benchmarks
├── tests/                   # Unit tests, integration tests, and attack simulation scripts
├── my-app/                  # React dashboard web application
├── reports/                 # Evaluation metrics, data-quality reports, and figures
├── docs/                    # Lab plan and rules, data retention plan, lab logbook, decision log, research notes
└── archive/                 # Old code and files we no longer use (local only, not in Git)
```

---

## Quick Start

### 1. Install Dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in the secrets (never commit `.env`).
Copy `config/settings.example.yaml` to `config/settings.yaml` and fill in your lab plan (guide Steps 4 and 5).
```powershell
copy .env.example .env
copy config\settings.example.yaml config\settings.yaml
```

### 3. Run the system (development PC)
```powershell
python core_engine/app.py           # backend + live pipeline on port 5000
cd my-app; npm start                # dashboard on port 3000
```
On the Linux sensor, Zeek must write `conn.log` to the path in `zeek.conn_log_path` (`sensor/run_zeek.sh`). Copy `ml_engine/models/ids_bundle_v3.joblib` to the sensor (it is not in Git).

### 4. Follow the Step-by-Step Guide
Refer to [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md) to proceed through each milestone systematically.

