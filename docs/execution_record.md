# Project Execution Record and Command Log

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**Team:** Group 03 — University of Sri Jayewardenepura  
**Local Workspace:** `D:\intrusion detection`  
**GitHub Repository:** [https://github.com/madupadilshan/intrusion-detection.git](https://github.com/madupadilshan/intrusion-detection.git) (branch `main`)  
**Main Master Guide:** `STEP_BY_STEP_GUIDE.md`  
**Progress Tracker:** `PROJECT_PROGRESS_AND_CHALLENGES.md`  
**Last Updated:** 23 October 2026  

---

## Purpose of This Document

This document is the **exact, practical execution record** of the project. It records:
1. **What was done** in each step from the very beginning.
2. **How it was done**, step-by-step.
3. **The exact terminal commands** executed (PowerShell, Bash, Git).
4. **The files created, modified, or verified**.
5. **The verification output and audit results**.

Use this document to reproduce any step, review past work, prepare for supervisor meetings, or explain execution during viva examinations.

---

## Table of Steps Completed

| Step | Phase | Status | Main Output / Deliverable | Commit |
|---|---|:---:|---|:---:|
| **Step 0** | Understand Project & Literature Review | ✅ Completed | `docs/project_summary.md`, `docs/literature_notes.md` | `10f5ac7` |
| **Step 1** | Ethics, Lab Plan, Retention & Logbook | ✅ Completed | `docs/ethics/lab_plan_and_rules.md`, `docs/ethics/data_retention_plan.md`, `docs/lab_logbook.md` | `9cc193f` |
| **Step 2** | Clean Folder Layout & Git Setup | ✅ Completed | Clean directory structure, `.gitignore`, `.gitattributes`, initial push | `9f90ce1`, `25c8b6e` |
| **Step 3a & 3d** | Development PC Environment Setup | ✅ Completed | `.venv` (Python 3.10.0), locked `requirements.txt`, `tools/check_env.py`, `reports/environment_versions.txt` | `29d99ff` |
| **Step 4** | Settings File and Decision Log | ✅ Completed | `config/settings.yaml`, `.env`, `docs/decision_log.md` (D-001 to D-013) | `9cc193f` & current |

---

## Detailed Step-by-Step Execution Log

### Step 0: Understand the Project & Literature Review

* **Objective:** Establish the formal academic baseline strictly using the Group 03 Research Proposal (July 2026), review literature, and resolve any citation errors.
* **Date:** 20 October 2026
* **How It Was Done:**
  1. Read and extracted core requirements from `Group03_Proposal.pdf`: Aim, Objectives (O1–O6), Hypothesis (H1), and Research Questions (RQ1–RQ5).
  2. Created [`docs/project_summary.md`](file:///d:/intrusion%20detection/docs/project_summary.md) capturing exact proposal wording and scope limits.
  3. Created [`docs/literature_notes.md`](file:///d:/intrusion%20detection/docs/literature_notes.md) reviewing all 11 proposal papers plus 2 cited in text.
  4. Performed literature verification on two citations appearing in Section 1.4:
     - **Santos et al. (2023):** Verified via web and Crossref (*Cluster Computing*, 26(1), pp. 37–57). Verified as real and valid.
     - **Almashhadani et al. (2024):** Searched across Crossref (94 papers by Almashhadani in 2023–2025) and academic databases. No intrusion detection paper found. Under **Decision D-009**, the team removed this unverified citation and supported the claim using Santos et al. (2023) alone.
* **Files Created / Modified:**
  - `docs/project_summary.md`
  - `docs/literature_notes.md`
  - `docs/decision_log.md` (Decision `D-009`)
* **Commands Executed:**
  ```powershell
  # Check git status
  git status

  # Stage and commit Step 0 documents
  git add docs/project_summary.md docs/literature_notes.md docs/decision_log.md
  git commit -m "Step 0: project summary and literature notes"

  # Push to GitHub
  git push origin main
  ```
* **Verification Result:** Commit `10f5ac7` pushed to `origin/main`. All team members confirmed understanding of the proposal.

---

### Step 1: Lab Plan, Data Retention Plan & Lab Logbook

* **Objective:** Establish ethical boundaries, safety rules, device allocations, and data minimization policies before running any live tests (Proposal Sections 1.2, 3.8, and 5.1).
* **Date:** 20–21 October 2026
* **How It Was Done:**
  1. Wrote the safety and ethics plan [`docs/ethics/lab_plan_and_rules.md`](file:///d:/intrusion%20detection/docs/ethics/lab_plan_and_rules.md):
     - Defined isolated subnets: Camera LAN (`192.168.50.0/24`) and Outside Attacker subnet (`10.10.10.0/24`). No connection to the internet during tests.
     - Defined the 6 allowed test scenarios (Table 10).
     - Defined the strict "Never" rules: no live malware, no public IPs, no camera video/audio recording.
     - Hardware allocation strategy under **Decision D-010**: Since physical IP cameras and switches are not yet available, allocated RTSP Camera Simulator (software emulation / mobile RTSP stream) and software bridges / lab loans so development continues without delays.
     - Team permissions: Ticked authorizations (`☑`) for all 3 members (Dilshan, Dilshara, Mendis) across attack tools, lab passwords, and firewall rule changes.
  2. Wrote the data retention plan [`docs/ethics/data_retention_plan.md`](file:///d:/intrusion%20detection/docs/ethics/data_retention_plan.md):
     - Metadata-only policy: store Zeek flow metadata only; never store video feeds or payloads.
     - Retention durations under **Decision D-011**:
       - `attack_events`: 90 days (automatic deletion via MongoDB TTL index)
       - `traffic_summaries`: 30 days (automatic deletion via MongoDB TTL index)
       - `system_logs`: 90 days (automatic deletion via MongoDB TTL index)
       - Local test captures: Maximum 180 days (deleted when evaluation completes)
     - Recorded formal team sign-off dated 2026-10-21.
  3. Updated [`config/settings.example.yaml`](file:///d:/intrusion%20detection/config/settings.example.yaml) lines 33–36 with the agreed values (`90`, `30`, `90`).
  4. Initialized [`docs/lab_logbook.md`](file:///d:/intrusion%20detection/docs/lab_logbook.md) with logging rules and Entry 1.
* **Files Created / Modified:**
  - `docs/ethics/lab_plan_and_rules.md`
  - `docs/ethics/data_retention_plan.md`
  - `docs/lab_logbook.md`
  - `config/settings.example.yaml`
  - `docs/decision_log.md` (Decisions `D-010`, `D-011`)
* **Commands Executed:**
  ```powershell
  # Check changes
  git diff

  # Stage and commit Step 1 files
  git add config/settings.example.yaml docs/decision_log.md docs/ethics/data_retention_plan.md docs/ethics/lab_plan_and_rules.md
  git commit -m "Step 1: complete lab plan, permissions, and data retention durations"

  # Push to GitHub
  git push origin main
  ```
* **Verification Result:** Commit `9cc193f` pushed cleanly to `origin/main`. Working tree clean.

---

### Step 2: Clean Folder Structure & Git Repository Setup

* **Objective:** Clean up the project directory, archive unusable legacy code/models, establish a standard engineering layout, and initialize Git version control.
* **Date:** 19 October 2026
* **How It Was Done:**
  1. Standardized directory layout:
     ```
     D:\intrusion detection\
     ├── config/              <- settings and label mappings
     ├── core_engine/         <- backend, db_service, firewall adapters
     ├── data/                <- raw/iot23, interim, processed, local (gitignored)
     ├── docs/                <- ethics, decision log, summaries, notes
     ├── ml_engine/           <- manifest, features, training, evaluation
     ├── my-app/              <- React dashboard
     ├── reports/             <- verification and evaluation reports
     ├── sensor/              <- Zeek scripts and nftables configs
     ├── tests/               <- unit, integration, and lab scenario tests
     ├── tools/               <- check_env, latency measurement scripts
     └── archive/             <- archived legacy code, old models, old data (gitignored)
     ```
  2. Moved legacy assets to `archive/` (gitignored):
     - Unusable 820 MB `random_forest_model.pkl` (data leakage, unknown labels, min-max scaling mismatch).
     - Legacy data `X_train.csv` (no scenario IDs, row-split leakage).
     - Old scripts (`iot23_attacks.py`, `network_scan.py`, `db_manager.py`).
  3. Removed inner `.git` from `my-app/` so the React dashboard files are tracked directly by the main Git repository.
  4. Configured `.gitignore` (ignoring `.venv/`, `data/`, models, secrets, and large binaries) and `.gitattributes` (normalizing line endings).
  5. Established default branch as `main` and pushed to GitHub.
* **Files Created / Modified:**
  - `.gitignore`, `.gitattributes`, `README.md`, `.env.example`
  - Initial directory `.gitkeep` files
* **Commands Executed:**
  ```powershell
  # Check Git remote and branch
  git remote -v
  git branch -M main

  # Add and commit cleaned folder layout
  git add .
  git commit -m "Step 2: Clean project structure, architecture guides, and initial setup"

  # Push to GitHub repository
  git push -u origin main
  ```
* **Verification Result:** Commits `891a8e5` and `9f90ce1` pushed to `origin/main`. Working directory clean and verified.

---

### Step 3a & 3d: Windows Development PC Setup & Verification

* **Objective:** Set up an isolated Python virtual environment (`.venv`) on the Windows laptop, install all project dependencies, lock exact versions, and verify system connectivity.
* **Date:** 22 October 2026
* **Host Environment Assessment:**
  - OS: Windows 10/11 AMD64
  - Host Python: 3.10.0
  - Database: MongoDB Server 8.0.6 running locally on port 27017
  - Node.js: 22.12
  - Network driver: `Npcap` verified installed at `C:\Program Files\Npcap`
  - Network scanner: Nmap binary deferred to Step 27 under **Decision D-012** (ML Steps 7–18 do not require Nmap)
* **How It Was Done:**
  1. Created isolated Python virtual environment `.venv` using Python 3.10.0:
     ```powershell
     python -m venv .venv
     ```
  2. Upgraded pip to latest version:
     ```powershell
     .\.venv\Scripts\python.exe -m pip install --upgrade pip
     ```
  3. Installed all 18 project packages inside `.venv` from [`requirements.txt`](file:///d:/intrusion%20detection/requirements.txt):
     ```powershell
     .\.venv\Scripts\python.exe -m pip install -r requirements.txt
     ```
  4. Locked exact package versions using `pip freeze` and updated `requirements.txt`:
     - `pandas==2.3.3`
     - `numpy==2.2.6`
     - `pyarrow==25.0.1`
     - `scikit-learn==1.7.2`
     - `scipy==1.15.3`
     - `joblib==1.6.0`
     - `matplotlib==3.10.9`
     - `pyyaml==6.0.3`
     - `python-dotenv==1.2.4`
     - `flask==3.1.3`
     - `flask-socketio==5.7.0`
     - `flask-cors==6.0.5`
     - `flask-jwt-extended==4.7.4`
     - `bcrypt==5.0.0`
     - `pymongo==4.18.3`
     - `python-nmap==0.7.1`
     - `psutil==7.2.2`
     - `scapy==2.8.0`
     - `pytest==9.1.1`
  5. Created the verification script [`tools/check_env.py`](file:///d:/intrusion%20detection/tools/check_env.py).
  6. Executed `tools/check_env.py` inside `.venv` to run automated verification:
     ```powershell
     .\.venv\Scripts\python.exe tools/check_env.py
     ```
  7. Generated the audit report [`reports/environment_versions.txt`](file:///d:/intrusion%20detection/reports/environment_versions.txt).
  8. Committed and pushed all changes to GitHub repository.
* **Commands Executed:**
  ```powershell
  # 1. Create virtual environment
  python -m venv .venv

  # 2. Upgrade pip inside .venv
  .\.venv\Scripts\python.exe -m pip install --upgrade pip

  # 3. Install dependencies
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt

  # 4. Check installed versions
  .\.venv\Scripts\pip.exe freeze

  # 5. Run verification script
  .\.venv\Scripts\python.exe tools/check_env.py

  # 6. Commit and push
  git add requirements.txt docs/decision_log.md tools/check_env.py reports/environment_versions.txt
  git commit -m "Step 3a: lock package versions in .venv and add check_env verification script"
  git push origin main
  ```
* **Verification Output:**
  ```text
  ============================================================
  IDS Software Environment Verification Report
  Generated: 2026-10-22 10:56:07
  Host: MadupaDilshan (Windows 10 AMD64)
  Python: 3.10.0 (D:\intrusion detection\.venv\Scripts\python.exe)
  ============================================================

  --- Python Packages ---
    [OK]    pandas                : 2.3.3
    [OK]    numpy                 : 2.2.6
    [OK]    pyarrow               : 25.0.1
    [OK]    scikit-learn          : 1.7.2
    [OK]    joblib                : 1.6.0
    [OK]    matplotlib            : 3.10.9
    [OK]    pyyaml                : 6.0.3
    [OK]    python-dotenv         : 1.2.4
    [OK]    flask                 : 3.1.3
    [OK]    flask-socketio        : 5.7.0
    [OK]    flask-cors            : 6.0.5
    [OK]    flask-jwt-extended    : 4.7.4
    [OK]    bcrypt                : 5.0.0
    [OK]    pymongo               : 4.18.3
    [OK]    python-nmap           : 0.7.1
    [OK]    psutil                : 7.2.2
    [OK]    scapy                 : 2.8.0
    [OK]    pytest                : 9.1.1

  --- Database Service ---
    [OK]    MongoDB Connected (v8.0.6)

  --- Network & System Tools ---
    [OK]    Npcap detected at C:\Program Files\Npcap
    [INFO]  Nmap binary not found in PATH (deferred to Step 27 or install from nmap.org)

  ============================================================
  OVERALL STATUS: PASSED
  ============================================================
  ```
* **Git Commit:** `29d99ff` pushed to `origin/main`. Working tree clean.

---

### Step 4: Settings File and Decision Log Setup

* **Objective:** Establish the centralized project configuration (`config/settings.yaml`), safe management allowlists, cryptographic secrets isolation (`.env`), and maintain the official architectural decision log (`docs/decision_log.md`).
* **Date:** 23 October 2026
* **How It Was Done:**
  1. Created active configuration [`config/settings.yaml`](file:///d:/intrusion%20detection/config/settings.yaml) from [`config/settings.example.yaml`](file:///d:/intrusion%20detection/config/settings.example.yaml):
     - Configured `approved_scan_subnets` (`["192.168.50.0/24"]`) to restrict scanner scope (Proposal Section 3.7).
     - Confirmed static management allowlist:
       - Router / Gateway: `192.168.50.1`
       - Sensor (management): `192.168.50.5`
       - Admin workstation: `192.168.50.10`
       - NVR: `192.168.50.20`
       *(Guarantees critical control nodes are never blocked by automated responses)*.
     - Configured response safety parameters:
       - `deployment_mode: passive` (default per Proposal Table 11).
       - `adapter: simulation` (for Windows local development) / `router` (for physical lab).
       - `min_confidence: 0.85`, `min_repeats: 3`, `repeat_window_seconds: 60`, `max_rule_minutes: 30` (rules expire automatically).
     - Fixed `random_seed: 42` for 100% scientific reproducibility across all machine learning models (Proposal Section 3.4).
     - Set data retention periods to `attack_events: 90`, `traffic_summaries: 30`, `system_logs: 90` (matching Step 1 agreed retention policy).
  2. Generated cryptographic secrets and created `.env`:
     - Executed Python cryptographic token generation to create 32-byte hexadecimal random keys for `JWT_SECRET_KEY` and `FLASK_SECRET_KEY`.
     - Configured local MongoDB connection: `MONGO_URI=mongodb://localhost:27017/` and `DB_NAME=iot_ids_db`.
     - Left router SSH fields ready for physical deployment.
     - Confirmed `.env` and `config/settings.yaml` are strictly ignored by `.gitignore` to prevent any credentials from entering public GitHub repository.
  3. Recorded Decision `D-013` in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
* **Commands Executed:**
  ```powershell
  # 1. Generate 32-byte cryptographic random hex secrets
  .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))"

  # 2. Verify git status and ensure secrets are ignored
  git status
  ```
* **Files Created / Modified:**
  - `config/settings.yaml` (Local, Git-ignored)
  - `.env` (Local, Git-ignored)
  - `docs/decision_log.md` (Decision `D-013` added)
  - `STEP_BY_STEP_GUIDE.md` (Step 4 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Entry 3.23 added)
* **Verification Result:** Both files active locally, no secrets exposed in Git, allowlist confirmed. Step 4 status is ✅ Done.

---

### Step 6: Threat Model and Requirements Checklist

* **Objective:** Formalize the system security threat model, attack vectors, flow trajectories, protected assets, and defensive boundaries (Proposal Sections 1.2, 1.5, 3.1, 3.7, 3.8; Tables 10, 11), and establish the definitive traceability checklist for all Functional Requirements (FR-01 to FR-08), Non-Functional Requirements (NFR-01 to NFR-05), Research Objectives (O1 to O6), and Research Questions (RQ1 to RQ5) / Hypothesis H1.
* **Date:** 23 October 2026
* **How It Was Done:**
  1. Authoring System Threat Model ([`docs/threat_model.md`](file:///d:/intrusion%20detection/docs/threat_model.md)):
     - Defined protected network assets: IP camera (`192.168.50.30`), NVR recorder (`192.168.50.20`), Gateway (`192.168.50.1`), Sensor node (`192.168.50.5`), Admin workstation (`192.168.50.10`), and video stream privacy.
     - Profiled threat actors: External attacker (`10.10.10.0/24`) attempting scanning and floods; compromised IoT camera attempting outbound C&C beacons and lateral infection.
     - Documented traffic trajectories: Inbound attacks (probes, SYN floods), Outbound attacks (Mirai heartbeats, file downloads), and Lateral camera streaming (normal RTSP traffic).
     - Mapped the 6 standardized evaluation scenarios from Proposal Table 10 (Normal streaming, Port scan, DDoS flood, C&C beacon, File download, and Manual block/unblock).
     - Defined defensive architecture and safety constraints: static management allowlist bypass, confidence ($\ge 0.85$) and repetition ($\ge 3$ within 60s) multi-checks, 30-minute rule auto-expiry, and strict metadata-only inspection policy.
  2. Authoring Requirements Checklist ([`docs/requirements_checklist.md`](file:///d:/intrusion%20detection/docs/requirements_checklist.md)):
     - Mapped all 8 Functional Requirements (FR-01 to FR-08) from Proposal Table 7 with priority (6 MUST, 2 SHOULD), verification method, and associated guide steps.
     - Defined 5 Non-Functional Requirements: detection latency $< 2.0$s (NFR-01), sensor memory $< 1.0$ GB RAM (NFR-02), zero scenario leakage via group splits (NFR-03), Macro-F1 $> 0.90$ with FPR $< 1.0\%$ (NFR-04), and strict scientific reproducibility (NFR-05).
     - Cross-referenced 6 Research Objectives (O1 to O6) from Proposal Table 3 with target deliverables and milestones.
     - Documented alignment with Hypothesis H1 and Research Questions RQ1 through RQ5.
  3. Verified consistency across all project documentation:
     - Checked alignment with `config/settings.yaml` (allowlist, thresholds, retention).
     - Updated Step 6 in `STEP_BY_STEP_GUIDE.md` and `PROJECT_PROGRESS_AND_CHALLENGES.md`.
* **Commands Executed:**
  ```powershell
  # 1. Verify tracked and untracked files
  git status

  # 2. Stage new documentation files and updated records
  git add docs/threat_model.md docs/requirements_checklist.md docs/execution_record.md

  # 3. Commit changes to Git
  git commit -m "Step 6: add threat model and requirements checklist"

  # 4. Push commit to GitHub
  git push origin main
  ```
* **Files Created / Modified:**
  - `docs/threat_model.md` (Created, in Git)
  - `docs/requirements_checklist.md` (Created, in Git)
  - `docs/execution_record.md` (Updated, in Git)
  - `STEP_BY_STEP_GUIDE.md` (Updated local guide, Step 6 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Updated local log, Entry 3.25 added)
* **Verification Result:** Full traceability established. Zero hardware dependencies needed for ML track. Step 6 status is ✅ Done.

---

### Step 7: Official IoT-23 Dataset Placement and Manifest Generation

* **Objective:** Ingest the complete official IoT-23 dataset (v1.0.0) into `data/raw/iot23/`, replace flawed unverified legacy data, compute cryptographic SHA-256 hashes across all 23 scenario files, count total connection flows and label breakdowns, and generate the definitive audit manifest (`reports/dataset_manifest.csv`) for scientific reproducibility (Proposal Section 3.2, Objective O1).
* **Date:** 23 October 2026
* **How It Was Done:**
  1. Dataset Placement:
     - Verified official IoT-23 files located in `D:\Download\archive` containing 23 scenario CSVs (`dataset1.csv` through `dataset23.csv`).
     - Moved all 23 scenario files (44.13 GB total) into the designated local folder `data/raw/iot23/`.
     - Confirmed `data/raw/` is strictly ignored by `.gitignore` so no multi-gigabyte data files enter Git version control.
  2. Manifest Script Implementation ([`ml_engine/manifest.py`](file:///d:/intrusion%20detection/ml_engine/manifest.py)):
     - Designed single-pass streaming architecture to read files line-by-line in binary mode (`hasher.update()`).
     - Mapped each file to its corresponding official CTU scenario ID (`CTU-IoT-Malware-Capture-*` and `CTU-Honeypot-Capture-*`).
     - Kept peak memory footprint under 100 MB RAM to safely execute on host PC (11.7 GB RAM).
     - Calculated total rows, benign vs malicious counts, and detailed label distributions for each scenario.
  3. Execution & Verification:
     - Executed `ml_engine/manifest.py` inside `.venv` on development PC.
     - Processed all 23 files in 572.9 seconds (~9.5 minutes) at an average rate of ~568,000 flows/second.
     - Generated official audit manifest: [`reports/dataset_manifest.csv`](file:///d:/intrusion%20detection/reports/dataset_manifest.csv).
* **Commands Executed:**
  ```powershell
  # 1. Move scenario files from download location to raw data folder
  Move-Item -Path "D:\Download\archive\*.csv" -Destination "D:\intrusion detection\data\raw\iot23\" -Force

  # 2. Run the manifest generator inside .venv
  .\.venv\Scripts\python.exe ml_engine/manifest.py

  # 3. Check Git status and track manifest deliverables
  git add ml_engine/manifest.py reports/dataset_manifest.csv docs/execution_record.md
  git commit -m "Step 7: generate official IoT-23 dataset manifest with SHA-256 hashes"
  git push origin main
  ```
* **Audit Summary from `reports/dataset_manifest.csv`:**
  - Total Scenarios Processed: 23 (20 Malware, 3 Benign)
  - Total Disk Footprint: 44.13 GB
  - Total Processed Connection Flows: **325,309,946**
  - Processing Runtime: 572.9 seconds (9.55 minutes)
  - Scenario Breakdown Highlights:
    - `dataset1.csv` (`CTU-Honeypot-Capture-4-1`, Philips Hue): 452 rows (452 Benign) | SHA256: `b06bdc4d7de8...`
    - `dataset2.csv` (`CTU-Honeypot-Capture-5-1`, Amazon Echo): 1,374 rows (1,374 Benign) | SHA256: `4fc5fec1414f...`
    - `dataset3.csv` (`CTU-Honeypot-Capture-7-1`, Somfy Doorlock): 130 rows (130 Benign) | SHA256: `a0ada4f95dda...`
    - `dataset4.csv` (`CTU-IoT-Malware-Capture-8-1`, Hakai): 6,378,293 rows | SHA256: `d442d4fe1806...`
    - `dataset6.csv` (`CTU-IoT-Malware-Capture-7-1`, Mirai): 11,454,714 rows | SHA256: `b63cc09f5873...`
    - `dataset7.csv` (`CTU-IoT-Malware-Capture-60-1`, Gagfyt): 3,581,028 rows | SHA256: `2239ed7d1288...`
    - `dataset12.csv` (`CTU-IoT-Malware-Capture-43-1`, Mirai): 67,321,809 rows | SHA256: `8dac6b3cb9c3...`
    - `dataset14.csv` (`CTU-IoT-Malware-Capture-39-1`, Muhstik): 73,568,981 rows | SHA256: `b22fcbb94d07...`
    - `dataset17.csv` (`CTU-IoT-Malware-Capture-34-1`, Mirai): 23,145 rows | SHA256: `2ea17a6fde41...`
    - `dataset18.csv` (`CTU-IoT-Malware-Capture-33-1`, Kenjiro): 54,454,591 rows | SHA256: `c0d67cebdf09...`
    - `dataset22.csv` (`CTU-IoT-Malware-Capture-17-1`, Kenjiro): 54,659,855 rows | SHA256: `536bebcca1f9...`
    - `dataset23.csv` (`CTU-IoT-Malware-Capture-1-1`, Hide and Seek): 1,008,748 rows | SHA256: `8cc68c096c8e...`
* **Files Created / Modified:**
  - `ml_engine/manifest.py` (Created, in Git)
  - `reports/dataset_manifest.csv` (Created, in Git)
  - `docs/execution_record.md` (Updated, in Git)
  - `STEP_BY_STEP_GUIDE.md` (Updated local guide, Step 7 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Updated local log, Entry 3.26 added)
* **Verification Result:** All 23 scenarios verified with SHA-256 integrity proofs. Objective O1 satisfied. Step 7 status is ✅ Done.

---

### Step 8: Write and Freeze Label Mapping to 5 Target Classes

* **Objective:** Establish and freeze the definitive mapping from all 17 raw IoT-23 labels to the 5 target attack classes specified in Research Proposal Table 5, resolve the 8 previously undecided mixed labels based on empirical manifest flow analysis, exclude ambiguous non-flooding labels to prevent label noise (Sections 2.3, 3.2), and record Decision `D-014` before model training begins (preventing post-hoc data snooping).
* **Date:** 23 October 2026
* **How It Was Done:**
  1. Label Breakdown Analysis from Step 7 Manifest ([`reports/dataset_manifest.csv`](file:///d:/intrusion%20detection/reports/dataset_manifest.csv)):
     - Audited all 325,309,946 flows across the 23 scenarios.
     - Identified 17 unique (label, detailed-label) combinations.
     - Found that the 8 mixed/unclear labels (`Attack`, `Okiru-Attack`, `C&C-HeartBeat-Attack`, `PartOfAHorizontalPortScan-Attack`, `C&C-FileDownload`, `C&C-HeartBeat-FileDownload`, `C&C-Mirai`, `C&C-PartOfAHorizontalPortScan`) total only 11,194 flows (0.0034% of the dataset).
  2. Resolution of Undecided Labels (`config/label_mapping.yaml`):
     - `C&C-FileDownload` (53 flows) and `C&C-HeartBeat-FileDownload` (11 flows) ➔ Mapped to `Malware_Download` (dominant behavior is downloading executable binary stages over HTTP/port 80).
     - `C&C-Mirai` (2 flows) ➔ Mapped to `Malware_Download` (Proposal Table 5 explicitly assigns Mirai to Malware).
     - `C&C-PartOfAHorizontalPortScan` (888 flows) ➔ Mapped to `PortScan` (dominant volume traffic is port 23 TCP SYN probes).
     - `Attack` (9,398 flows), `Okiru-Attack` (3 flows), `C&C-HeartBeat-Attack` (834 flows), and `PartOfAHorizontalPortScan-Attack` (5 flows) ➔ Marked `EXCLUDE` per Proposal Table 5 ("attack labels that we checked are flooding -> DDoS_DoS, otherwise EXCLUDE") and Section 3.2 ("If a label is too general or unclear, do NOT force it. EXCLUDE it."). Total excluded flows: 10,240 (0.0031%).
  3. Freezing the Mapping:
     - Set `mapping_status: frozen` in [`config/label_mapping.yaml`](file:///d:/intrusion%20detection/config/label_mapping.yaml).
     - Recorded Decision `D-014` in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
* **Projected Class Distribution (325,309,946 Flows):**
  - **Class 2 (`PortScan`):** 213,853,812 flows (65.74%)
  - **Class 4 (`Malware_Download`):** 60,990,792 flows (18.75%)
  - **Class 0 (`Benign`):** 30,860,691 flows (9.49%)
  - **Class 1 (`DDoS_DoS`):** 19,538,713 flows (6.01%)
  - **Class 3 (`CnC`):** 55,698 flows (0.02%)
  - **`EXCLUDE` (Ambiguous):** 10,240 flows (0.0031%)
* **Commands Executed:**
  ```powershell
  # 1. Stage updated label mapping, decision log, and execution record
  git add config/label_mapping.yaml docs/decision_log.md docs/execution_record.md

  # 2. Commit frozen mapping to Git
  git commit -m "Step 8: freeze IoT-23 label mapping to 5 target classes (D-014)"

  # 3. Push commit to GitHub
  git push origin main
  ```
* **Files Created / Modified:**
  - `config/label_mapping.yaml` (Updated status to `frozen`, in Git)
  - `docs/decision_log.md` (Added Decision `D-014`, in Git)
  - `docs/execution_record.md` (Updated, in Git)
  - `STEP_BY_STEP_GUIDE.md` (Updated local guide, Step 8 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Updated local log, Entry 3.27 added)
* **Verification Result:** Zero ambiguous labels remain undecided. Supervisor Checkpoint C3 fulfilled. Step 8 status is ✅ Done.

---

### Step 9: Data-Quality Report and Dataset Feature Audit

* **Objective:** Conduct a comprehensive empirical data quality audit across the official IoT-23 dataset (v1.0.0), compute the definitive Class × Scenario distribution matrix across all 325,309,946 flows, analyze missing values (`-`), audit feature distributions and categorical cardinalities, evaluate held-out scenario candidates, and generate visual charts and the official audit report (`reports/data_quality_report.md`) per Proposal Section 3.2 & Objective O1.
* **Date:** 23 October 2026
* **How It Was Done:**
  1. Implemented Data Quality Auditor ([`ml_engine/data_quality.py`](file:///d:/intrusion%20detection/ml_engine/data_quality.py)):
     - Integrated `reports/dataset_manifest.csv` and frozen `config/label_mapping.yaml` (D-014) to build the 100% exact Class × Scenario distribution matrix covering all 325,309,946 flows.
     - Implemented stratified streaming sampler to inspect ~620,000 connection flows across all 23 scenarios with memory utilization under 200 MB RAM.
     - Calculated missing rate percentages for all fields (`duration`: 61.46%, `orig_bytes`: 61.46%, `resp_bytes`: 61.46%, `service`: 98.48%).
     - Audited numerical statistics (min, max, median, 95th/99th percentiles, zero rates) for `duration`, `orig_bytes`, `resp_bytes`, `orig_pkts`, `resp_pkts`.
     - Analyzed categorical cardinalities (`proto`: 94.72% TCP, 5.07% UDP; `conn_state`: 86.95% `S0`, 9.04% `OTH`, 2.02% `SF`).
  2. Generated Visualization Charts:
     - `reports/data_quality_class_distribution.png`: Log-scale bar chart showing distribution across the 5 target classes.
     - `reports/data_quality_scenario_matrix.png`: Heatmap matrix showing class representations across the 23 scenarios.
  3. Formulated Engineering Recommendations:
     - Imputation strategy for Step 10: `duration` ➔ `0.0`, `orig_bytes`/`resp_bytes` ➔ `0`, `service` ➔ `'unknown'`.
     - Feature engineering targets for Step 11: `is_incomplete_flow` flag, directional byte/packet ratios, destination port binning.
     - Sampling plan for Step 12: Preserve all 55,698 `CnC` flows, downsample `PortScan` to 400,000, `Malware_Download` to 350,000, and retain benign baseline flows.
     - Held-out scenario candidates for Step 13: Identified `CTU-IoT-Malware-Capture-34-1` (Mirai, 4 classes) and `CTU-IoT-Malware-Capture-48-1` (Mirai, 3 classes) as optimal candidates.
* **Commands Executed:**
  ```powershell
  # 1. Run data quality auditor inside .venv
  .\.venv\Scripts\python.exe ml_engine/data_quality.py

  # 2. Stage new script, report, charts, and execution record
  git add ml_engine/data_quality.py reports/data_quality_report.md reports/data_quality_class_distribution.png reports/data_quality_scenario_matrix.png docs/execution_record.md

  # 3. Commit and push to GitHub
  git commit -m "Step 9: generate data quality report and feature distributions audit"
  git push origin main
  ```
* **Files Created / Modified:**
  - `ml_engine/data_quality.py` (Created, in Git)
  - `reports/data_quality_report.md` (Created, in Git)
  - `reports/data_quality_class_distribution.png` (Created, in Git)
  - `reports/data_quality_scenario_matrix.png` (Created, in Git)
  - `docs/execution_record.md` (Updated, in Git)
  - `STEP_BY_STEP_GUIDE.md` (Updated local guide, Step 9 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Updated local log, Entry 3.28 added)
* **Verification Result:** Full Class × Scenario matrix verified. Missing rates and statistical distributions documented. Objective O1 completed. Step 9 status is ✅ Done.

---

### Step 10: Load and Clean IoT-23 Dataset into Standardized Interim Parquet

* **Objective:** Stream all 23 official IoT-23 scenarios (325,309,946 flows, 44.13 GB), perform memory-safe chunked reading (`chunksize=500,000`), impute Zeek missing values (`-` in duration to 0.0, bytes to 0, service/history to 'unknown'), apply frozen label mapping (D-014) to 5 target classes, exclude ambiguous compound labels (10,240 rows), attach `scenario_id` metadata to guarantee zero cross-scenario data leakage, downcast numerical types (`float32`, `int64`, `int32`, `int8`), and export compressed columnar Parquet files (`data/interim/<scenario_id>.parquet`) and the audit log (`reports/interim_data_summary.md`) per Proposal Section 3.3 (Steps 1–4) & Objective O1.
* **Date:** 25 October 2026
* **How It Was Done:**
  1. Implemented Chunked Ingestion Pipeline ([`ml_engine/load_iot23.py`](file:///d:/intrusion%20detection/ml_engine/load_iot23.py)):
     - Designed streaming processor reading in chunks of 500,000 rows with RAM footprint staying under 400 MB.
     - Extracted `label` and `detailed-label` from trailing whitespace-separated field across all scenario files.
     - Filtered out 10,240 ambiguous flows (`Attack`, `Okiru-Attack`, compound labels) per Proposal Sections 2.3 & 3.2.
     - Mapped raw labels into the 5 target classes: `0: Benign`, `1: DDoS_DoS`, `2: PortScan`, `3: CnC`, `4: Malware_Download`.
     - Imputed missing indicators: `duration` ➔ `0.0` (`float32`), `orig_bytes`/`resp_bytes`/`missed_bytes`/`pkts` ➔ `0` (`int64`/`int32`), `service`/`history` ➔ `'unknown'`.
     - Attached `scenario_id` to every row to preserve grouping for `StratifiedGroupKFold` in Step 13.
     - Enforced uniform schema via PyArrow `INTERIM_SCHEMA` and exported compressed Snappy Parquet files.
  2. Generated Ingestion & Audit Reports:
     - `reports/interim_data_summary.csv`: Machine-readable scenario ingestion log.
     - `reports/interim_data_summary.md`: Markdown audit report detailing raw rows, clean rows, excluded counts, parquet sizes, and runtime per scenario.
* **Commands Executed:**
  ```powershell
  # 1. Run full dataset ingestion and cleaner
  .\.venv\Scripts\python.exe ml_engine/load_iot23.py

  # 2. Add large binary patterns to .gitignore (*.parquet)
  git add .gitignore ml_engine/load_iot23.py reports/interim_data_summary.csv reports/interim_data_summary.md docs/execution_record.md

  # 3. Commit and push
  git commit -m "Step 10: load and clean IoT-23 dataset into standardized interim Parquet files"
  git push origin main
  ```
* **Files Created / Modified:**
  - `ml_engine/load_iot23.py` (Created, in Git)
  - `reports/interim_data_summary.csv` (Created, in Git)
  - `reports/interim_data_summary.md` (Created, in Git)
  - `.gitignore` (Modified, added `*.parquet`)
  - `docs/execution_record.md` (Updated, in Git)
  - `STEP_BY_STEP_GUIDE.md` (Updated local guide, Step 10 marked ✅ Done)
  - `PROJECT_PROGRESS_AND_CHALLENGES.md` (Updated local log, Entry 3.29 added)
  - `PROJECT_EXPLANATION.md` & `PROJECT_EXPLANATION_EN.md` (Updated Section 4 with Step 10 details)
  - `data/interim/*.parquet` (23 Parquet files generated, gitignored)
* **Verification Result:** Zero memory crashes, clean type enforcement, 100% of excluded rows counted and removed, zero data leakage between scenarios. Step 10 status is ✅ Done.

---

## Quick Reference: Useful Commands

To work with this project locally on your Windows laptop, use these standard commands:

```powershell
# Navigate to project directory
cd "D:\intrusion detection"

# Activate the virtual environment
.\.venv\Scripts\activate

# Run environment verification anytime
python tools/check_env.py

# Check Git status
git status

# Check local MongoDB connection
mongosh "mongodb://localhost:27017"
```

---

*This execution record will be updated immediately after every subsequent step is executed.*

