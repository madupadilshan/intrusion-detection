# Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning

**Bachelor of Information and Communication Technology Honours Degree**  
Department of Information and Communication Technology  
Faculty of Technology, University of Sri Jayewardenepura  

---

## Overview

This repository contains the prototype implementation of a real-time network intrusion detection and automated response system (NIDS/IPS) tailored for small IP-camera IoT networks.

* **Traffic Analytics:** Zeek (`conn.log`) connection flow processing.
* **Classifier:** Random Forest model trained on the IoT-23 benchmark dataset.
* **Target Classes (5):** Benign, DDoS/DoS, Port Scan, Command & Control (C&C), Malware/Download.
* **Active Response:** `nftables` rules on the lab router (passive mode) or on the sensor (inline mode), only when the safety rules pass (`docs/response_policy.md`); every rule expires and the admin can unblock by hand. Automatic response is off by default.
* **Management & Visualization:** Unified Flask & Socket.IO backend with a real-time React dashboard and MongoDB audit store.

---

## Documentation

* [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md): the master guide (Steps 0-42), from setup to evaluation. Follow the steps in order.
* [`PROJECT_EXPLANATION_EN.md`](PROJECT_EXPLANATION_EN.md) (English) and [`PROJECT_EXPLANATION.md`](PROJECT_EXPLANATION.md) (Sinhala): what the system is and why it is designed this way. Rewritten on 19 Oct 2026 to follow the proposal.
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
On the Linux sensor, Zeek must write `conn.log` to the path in `zeek.conn_log_path` (`sensor/run_zeek.sh`). Copy `ml_engine/models/ids_bundle_v1.joblib` to the sensor (it is not in Git).

### 4. Follow the Step-by-Step Guide
Refer to [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md) to proceed through each milestone systematically.

