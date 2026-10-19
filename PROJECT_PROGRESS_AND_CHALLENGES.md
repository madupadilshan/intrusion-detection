# Project Progress and Engineering Challenges Report

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**Repository:** `d:\intrusion detection`  
**Current Status:** Step A (Database Layer & Workspace Restructuring) Completed and Verified  
**Document Generation Date:** October 19, 2026  

---

## 1. Executive Summary

This document provides a detailed technical record of all work completed to date, the architectural decisions taken, the engineering challenges encountered, and the precise solutions implemented to align the codebase with the official research project proposal.

---

## 2. Chronological Progress of Completed Work

### Phase 1: Research Proposal Analysis and Scope Definition
1. **Document Review:** Conducted a comprehensive audit of the 26-page research proposal (*Bachelor of Information and Communication Technology Honours Degree, University of Sri Jayewardenepura*).
2. **Architecture Mapping:** Identified all core system requirements:
   * **Dataset:** IoT-23 (v1.0.0 official labelled flows).
   * **ML Classifier:** Random Forest (with 10 standardized connection flow features).
   * **Traffic Processing:** Zeek (`conn.log`) connection flow generator.
   * **Active Response:** Linux `nftables` / `iptables` drop rules with static management allowlists and manual unblocking.
   * **Backend:** Unified Python Flask with Flask-SocketIO.
   * **Frontend:** React web dashboard.
   * **Database:** MongoDB maintaining 5 standard collections (Proposal Figure 4).
   * **Discovery:** Nmap subnet scanning.

---

### Phase 2: Repository Audit and Legacy Code Analysis
Examined all existing files in `d:\intrusion detection` to determine what could be salvaged versus what had to be refactored:
* **Preserved Useful Assets:**
  * React dashboard in `my-app/` (UI components, Chart.js views, forms, styling).
  * Nmap scanning logic from `network_scan.py`.
  * Flask-SocketIO event handling patterns from `iot23_attacks.py`.
  * Model training references in `iot23_attacks/iot23/`.
* **Identified Critical Defects in Legacy Code:**
  * Scapy sniffer used hardcoded dummy values (`conn_state=6, history=22, service=0, duration=0`).
  * No firewall blocking logic existed (alerts were only logged, not mitigated).
  * Backend was fragmented across two ports (5005 and 5012) using two separate databases (`intrusion_detection` and `iot_security`).
  * Legacy Nmap scanner inserted random numbers for vulnerability counts.
  * Legacy Random Forest model (`random_forest_model.pkl`) was excessively large (820 MB) due to unpruned trees and improper feature scaling.

---

### Phase 3: Project Architecture & Execution Planning
1. **Master Guides Created:**
   * Authored [`PROJECT_EXPLANATION.md`](file:///d:/intrusion%20detection/PROJECT_EXPLANATION.md) (Sinhala).
   * Authored [`PROJECT_EXPLANATION_EN.md`](file:///d:/intrusion%20detection/PROJECT_EXPLANATION_EN.md) (English).
2. **Adoption of Master Operational Guide:**
   * Reviewed and adopted [`STEP_BY_STEP_GUIDE.md`](file:///d:/intrusion%20detection/STEP_BY_STEP_GUIDE.md) (1,782 lines, 43 steps, mapped to the 32-week project schedule) as the single source of truth for implementation.

---

### Phase 4: Workspace Restructuring & Version Control (Step 2 of Guide)
1. **Safe Archiving of Legacy Artifacts:**
   * Moved all legacy scripts, datasets, and presentation files into `archive/` without data loss:
     * `archive/legacy_code/`: `db_manager.py`, `iot23_attacks.py`, `network_scan.py`, `attack_logs.db`, `devices.db`.
     * `archive/legacy_datasets/`: `CICID2017/`, `KDD/`, `iot23_attacks/`.
     * `archive/legacy_docs/`: Presentation decks, `.zip` archives, screenshots, video project files.
2. **Directory Tree Construction:**
   * Created standard project directories:
     * `config/`: Configuration templates and frozen label mappings.
     * `core_engine/firewall/`: Backend services and firewall adapters.
     * `ml_engine/models/`: Training scripts and model artifacts.
     * `data/` (`raw/`, `interim/`, `processed/`, `local/`): Protected data directories.
     * `sensor/`: Zeek scripts and nftables rules.
     * `tools/`: Verification and benchmarking scripts.
     * `tests/` (`unit/`, `integration/`, `lab_scenarios/`): Test suites.
     * `reports/`: Evaluation reports and generated figures.
     * `docs/ethics/`: Ethics permission notes, data retention plan, and lab logbook.
3. **Core Configuration Files Established:**
   * [`.gitignore`](file:///d:/intrusion%20detection/.gitignore): Protects datasets, model binaries, logs, `.env`, and dependencies.
   * [`.env.example`](file:///d:/intrusion%20detection/.env.example): Environment variable template.
   * [`requirements.txt`](file:///d:/intrusion%20detection/requirements.txt): Unified dependency list.
   * [`config/settings.example.yaml`](file:///d:/intrusion%20detection/config/settings.example.yaml): Network, allowlist, and threshold settings.
   * [`config/label_mapping.yaml`](file:///d:/intrusion%20detection/config/label_mapping.yaml): Frozen 5-class mapping for IoT-23.
   * [`README.md`](file:///d:/intrusion%20detection/README.md): Project overview and quick-start guide.
4. **Git Repository Setup:**
   * Initialized Git repository (`git init`).
   * Configured tracking of the root project and resolved nested submodule conflicts.

---

### Phase 5: Database Layer Implementation (Step A / Guide Step 23)
1. **File Implemented:** [`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py).
2. **Database Target:** Local MongoDB server running on port 27017, database `iot_ids_db`.
3. **Collections and Indexes Implemented:**
   * `devices`: Unique index on `ip`, indexed on `last_seen`.
   * `attack_events`: Indexed on `timestamp`, `src_ip`, and `predicted_class`.
   * `response_actions`: Indexed on `executed_at` and `target_ip`.
   * `blocklist`: Unique index on `ip`, indexed on `status` and `expires_at`.
   * `system_logs`: Indexed on `timestamp`.
   * `users`: Unique index on `username`.
4. **Verification:**
   * Executed live automated self-tests directly against MongoDB:
     * MongoDB Connection: **PASS**
     * Device Upsert & Retrieval: **PASS**
     * Attack Event Insertion: **PASS**
     * IP Block Execution: **PASS**
     * IP Unblock Execution: **PASS**
     * Test Record Cleanup: **PASS**
5. **Git Commit:** Committed and verified clean working tree.

---

## 3. Challenges Encountered and Resolutions

| # | Challenge Encountered | Root Cause | Impact | Resolution Applied |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Scope Discrepancy (Alerts)** | Proposal Section 3.6 & Table 7 (FR-05) originally included Telegram Bot API and SMTP Email alerts. | Unnecessary complexity; supervisors advised the team to drop external alerts. | Formally excluded Telegram and Email alert scripts from the codebase. Scope was adjusted to rely exclusively on WebSockets (`socketio.emit`) pushing to the React dashboard and audit records in MongoDB. |
| **2** | **Hardware vs. Simulation Ambiguity** | Team was unsure whether expensive physical enterprise hardware (managed switches, physical NVRs) was required immediately. | Caused hesitation in starting development. | Clarified using Proposal Section 5.1: Development can occur 100% locally using simulated traffic and virtual environments. For the final demonstration, a zero-cost Android/iPhone running "IP Webcam" over a local Wi-Fi router fulfills all requirements. |
| **3** | **Synthetic / Dummy Flow Features** | Legacy `iot23_attacks.py` used Scapy to process raw packets, but hardcoded dummy values (`conn_state=6, history=22, service=0, duration=0`) because Scapy does not track full TCP connection state by default. | The ML model received invalid inputs, undermining detection validity. | Scheduled implementation of **Zeek (`conn.log`)** as the primary flow extractor, which natively tracks TCP/UDP/ICMP connection states identical to how the IoT-23 dataset was constructed. Scapy was relegated to attack simulation only. |
| **4** | **Database Fragmentation** | The repository had two separate scripts connecting to two different MongoDB databases (`intrusion_detection` and `iot_security`). `db_manager.py` was also missing required functions. | Prevented unified queries linking detected attacks to discovered devices or blocked IPs. | Consolidated all storage into a single database (`iot_ids_db`) and implemented [`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py) with standardized schema models. |
| **5** | **Embedded Submodule Conflict in Git** | Running `git add .` triggered a warning: `adding embedded git repository: my-app`. `my-app` was not being tracked by the main repository. | `create-react-app` initializes its own `.git` directory by default. Outer Git repositories treat this as an uncommitted submodule, leaving React source files unversioned. | Removed `my-app/.git`, cleared the cached submodule reference with `git rm --cached my-app`, and re-added `my-app/` as a standard directory inside the root repository. |
| **6** | **Missing Python Dependencies** | Running `python core_engine/db_service.py` resulted in `ModuleNotFoundError: No module named 'pymongo'`. | Local Python environment lacked the necessary database, network, and web libraries. | Ran `python -m pip install pymongo flask-socketio python-nmap scapy` to install all missing dependencies. |
| **7** | **CRLF / LF Line Ending Mismatches** | Windows PowerShell git commands reported line ending differences (`LF will be replaced by CRLF`). | Cross-platform text file formatting differences between Linux and Windows tools. | Normalized line endings and committed clean state across all configuration and documentation files. |

---

## 4. Current State of the Codebase

```
d:\intrusion detection\
│
├── config/
│   ├── settings.example.yaml     # Lab settings, allowlists, and response thresholds
│   └── label_mapping.yaml        # Frozen 5-class mapping for IoT-23
│
├── core_engine/
│   ├── db_service.py             # Verified MongoDB service (devices, attacks, blocks)
│   └── firewall/                 # Firewall adapter directory
│
├── data/                         # Isolated dataset directory (ignored by Git)
├── docs/ethics/                  # Ethics and lab documentation directory
├── ml_engine/models/             # ML training and model directory
├── reports/                      # Evaluation reports directory
├── sensor/                       # Zeek and nftables configuration directory
├── tests/                        # Test suite directory
├── tools/                        # Utility scripts directory
├── my-app/                       # Fully tracked React web dashboard
├── archive/                      # Preserved legacy prototypes and datasets
│   ├── legacy_code/
│   ├── legacy_datasets/
│   └── legacy_docs/
│
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore file protecting large/secret files
├── requirements.txt              # Standardized Python dependencies
├── README.md                     # Root project documentation
├── STEP_BY_STEP_GUIDE.md         # Master operational guide (43 steps)
├── PROJECT_EXPLANATION.md        # Architectural guide (Sinhala)
├── PROJECT_EXPLANATION_EN.md     # Architectural guide (English)
└── PROJECT_PROGRESS_AND_CHALLENGES.md # This comprehensive report
```

---

## 5. Next Immediate Engineering Steps

Following the roadmap in `STEP_BY_STEP_GUIDE.md`:

1. **Step B: Network Device Scanner (`core_engine/scanner_service.py`)**
   * Extract working Nmap logic from `archive/legacy_code/network_scan.py`.
   * Eliminate fake random vulnerability counts.
   * Accurately classify devices as IP cameras based on RTSP (port 554), HTTP (port 80), and vendor MAC OUIs (Hikvision, Dahua).
   * Persist scan results into MongoDB via `DatabaseService.upsert_device()`.
2. **Step C: Unified Backend API Server (`core_engine/app.py`)**
   * Build a single Flask application running on **Port 5000**.
   * Wire REST endpoints: `/api/devices`, `/api/scan`, `/api/attacks/history`, `/api/firewall/blocked`, `/api/firewall/unblock`.
   * Enable WebSocket broadcasting via `flask-socketio`.
3. **Step D: Active Firewall Engine (`core_engine/firewall/`)**
   * Build `firewall_manager.py` implementing static allowlists, confidence thresholds, and system command execution for IP blocking and unblocking.
