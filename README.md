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
* **Active Response:** Linux `nftables` / `iptables` drop rules with static management allowlists and reversible manual unblocking.
* **Management & Visualization:** Unified Flask & Socket.IO backend with a real-time React dashboard and MongoDB audit store.

---

## Documentation

* [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md): the master guide (Steps 0-42), from setup to evaluation. Follow the steps in order.
* [`PROJECT_EXPLANATION_EN.md`](PROJECT_EXPLANATION_EN.md) (English) and [`PROJECT_EXPLANATION.md`](PROJECT_EXPLANATION.md) (Sinhala): what the system is and why it is designed this way. Rewritten on 19 Oct 2026 to follow the proposal.

Note: these documentation files are listed in `.gitignore`, so they are not shared through Git. Share them with the team another way, or remove them from `.gitignore`.

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

### 3. Follow the Step-by-Step Guide
Refer to [`STEP_BY_STEP_GUIDE.md`](STEP_BY_STEP_GUIDE.md) to proceed through each milestone systematically.

