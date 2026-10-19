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

* [**`STEP_BY_STEP_GUIDE.md`**](file:///d:/intrusion%20detection/STEP_BY_STEP_GUIDE.md): The definitive master guide covering all 43 execution steps from setup to evaluation.
* [**`PROJECT_EXPLANATION.md`**](file:///d:/intrusion%20detection/PROJECT_EXPLANATION.md): Complete architectural breakdown and gap analysis (Sinhala).
* [**`PROJECT_EXPLANATION_EN.md`**](file:///d:/intrusion%20detection/PROJECT_EXPLANATION_EN.md): Complete architectural breakdown and gap analysis (English).

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
├── docs/                    # Ethics clearance, retention plan, lab logbook, and research notes
└── archive/                 # Preserved legacy prototypes and baseline materials
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and adjust your network interface and MongoDB parameters:
```bash
cp .env.example .env
```

### 3. Follow the Step-by-Step Guide
Refer to [**`STEP_BY_STEP_GUIDE.md`**](file:///d:/intrusion%20detection/STEP_BY_STEP_GUIDE.md) to proceed through each milestone systematically.
