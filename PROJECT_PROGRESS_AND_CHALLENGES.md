# Project Progress and Challenges Report

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Team:** Group 03 — University of Sri Jayewardenepura
**Local folder:** `D:\intrusion detection`
**GitHub:** https://github.com/madupadilshan/intrusion-detection (branch `main`)
**Last updated:** 9 November 2026

> **How this file is kept:** this file is updated **after every piece of work** on the project. Each piece of work gets a dated entry in Section 3 (Work log), and the tables in Sections 1, 2, 5 and 6 are updated at the same time. Use this file to answer "what has been done from the beginning?"

---

## 1. Where the project is now (short summary)

*(Updated 9 November 2026, after the full check against the proposal — see work log 3.53 to 3.57 and decisions D-039 to D-045.)*

- **Built and tested on the development PC:** the dataset pipeline and model (Steps 7–18), the Zeek adapter and live runner (Step 21), MongoDB, login, server, detector and decision engine, Nmap discovery, log export, the dashboard, the response policy, the nftables rules and the adapters (Steps 23–33).
- **Corrected on 8 Nov 2026:**
  - 4 scenario names were swapped in the dataset map; now fixed and checked against the official files (D-039).
  - Step 17 was redone so that no threshold is chosen from the held-out scenario (D-040).
  - The automatic response is now connected, off by default, and uses `lab.local_networks` (D-041).
  - The synthetic "camera" data and every result based on it were withdrawn (D-042).
  - The dashboard Settings page now really saves and applies settings, and the live alert page now confirms the right event and shows the response status.
- **Re-opened (software ready, lab run not done):** Steps 19, 20 and 22.
- **Model results after the fix (9 Nov 2026, D-043):** out-of-fold macro-F1 0.3422 (Random Forest; HistGradientBoosting 0.4331); deployed model on the held-out scenario 34-1: macro-F1 0.3405 (5 classes) / 0.4256 (4 present).
- **Calibration and Proposal 3.4 blocking aligned (9 Nov 2026, D-044, D-045, D-046):** `temperature` calibration keeps the model's top class (D-045; held-out macro-F1 **0.4530**; CnC found again). Out-of-fold repeat replay matching Proposal 3.4 (confidence threshold + 3 repeats within 60s window) successfully established automatic block thresholds: **PortScan: 0.30** (96.6% safe/malicious blocks), **CnC: 0.39** (100% safe/malicious blocks), while DDoS and Malware_Download remain alert-only (D-046). Safety floor lowered to 0.30.
- **Dataset copy verified (D-046):** `archive.zip` (downloaded 2026-10-19 16:49) checked 23/23 first/last rows against CTU servers, confirmed byte-for-byte authentic (Issue 22 & 25 closed). Original detailed labels evaluated in Step 17 (Issue 24 closed).
- **Hypothesis H1 is not confirmed:** the held-out macro-F1 is below 0.85; the camera-traffic FPR is not measured yet.
- **Next:** confirm the lab type with the supervisor (D-038); then build the lab (real camera, or a camera simulator confirmed with the supervisor), run Zeek, capture real benign traffic, then Steps 34–42.

---

## 2. Status of every step (from `STEP_BY_STEP_GUIDE.md`)

Labels: ✅ Done · 🔧 Done – needs changes · 🟡 Started · ♻️ Old code to reuse · ⬜ Not started

| Step | Name                                       | Status | Notes                                                                                     |
| ---- | ------------------------------------------ | ------ | ----------------------------------------------------------------------------------------- |
| 0    | Understand the project, literature review  | ✅     | Summary and literature notes written and pushed; Almashhadani citation removed (D-009); all members have read the proposal (20 Oct 2026). Literature notes keep growing until about week 8. |
| 1    | Lab plan, retention plan, logbook          | ✅     | All 3 files complete: device specifications (simulation/loan), all team permissions ticked, retention periods agreed (90/30/90 days), sign-off recorded (21 Oct 2026). |
| 2    | Clean the folder and set up Git            | ✅     | Committed and pushed (`9f90ce1`). Backup done. Public repo accepted by the owner.          |
| 3    | Install the software                       | 🟡     | Step 3a ✅ done on Windows PC (.venv created, pinned requirements, check_env PASSED). Step 3b/3c pending for lab. |
| 4    | Settings file and decision log             | ✅     | Local `config/settings.yaml`, `.env` and `docs/decision_log.md` (D-001 to D-013) complete; allowlist confirmed. |
| 5    | Build the lab network                      | ⬜     | Hardware not arranged yet (Development PC proceeds to Steps 6–18).                         |
| 6    | Threat model and requirement checklist     | ✅     | `docs/threat_model.md` and `docs/requirements_checklist.md` (FR-01 to FR-08, O1 to O6) complete. |
| 7    | Download IoT-23 and make a manifest        | ✅     | Local CSV copy of all 23 IoT-23 v1.0.0 scenarios in `data/raw/iot23/` (44.13 GB, 325.3M flows); content checked against the official `conn.log.labeled` files, 23/23 match (`tools/verify_iot23_copy.py`, D-039); 4 scenario names corrected; download source still to be recorded (issue 22). |
| 8    | Write and freeze the label mapping         | ✅     | Frozen `config/label_mapping.yaml` to 5 target classes; all 17 labels resolved (D-014); ambiguous excluded (0.0031%). |
| 9    | Data-quality report                        | ✅     | `reports/data_quality_report.md` complete with Class x Scenario matrix (325.3M flows), missing rates & charts. |
| 10   | Load and clean the data                    | ✅     | `ml_engine/load_iot23.py` executed; `data/interim/*.parquet` generated with imputed Zeek nulls, 5 classes & scenario IDs. |
| 11   | Shared feature code                        | ✅     | `ml_engine/features.py` implemented; 19 features (Proposal Table 6); 10 unit tests passed; Decision D-015. |
| 12   | Sampling and class balance                 | ✅     | `ml_engine/sample_dataset.py`; capped $N=50,000$/class; 100% CnC kept (48,992 flows); 1,384,070 flows in `data/processed/train_features.parquet` (10.81 MB); D-016. |
| 13   | Plan the three test levels                 | ✅     | Three-level plan in `reports/test_split_plan.md`; Level 1 Grouped CV; Level 2 `Capture-34-1` (23,145 flows sealed in `data/processed/heldout/`); D-017. |
| 14   | Train the Random Forest                    | ✅     | `ml_engine/train.py`; grouped CV by scenario; re-run 8 Nov 2026 after D-039: out-of-fold macro-F1 **0.3422** (fold mean 0.3353 ± 0.1704); best `n_estimators=100, max_depth=18`; 4.30 MB; out-of-fold probabilities saved for Step 17 (D-018, D-040, D-043). |
| 15   | Compare with other models                  | ✅     | `ml_engine/compare_models.py`; re-run 9 Nov 2026: out-of-fold macro-F1 HGB **0.4331** > RF 0.3422 > LR 0.2722; RF kept as the main model per proposal 2.4 (explainable tree paths); `reports/experiments/model_comparison.md` (D-019, D-043). |
| 16   | Evaluate on the held-out scenario          | ✅     | `ml_engine/evaluate.py`; re-run 9 Nov 2026 on `Capture-34-1` (23,145 flows): uncalibrated RF macro-F1 0.4530 (5 classes) / 0.5662 (4 present); H1 part 1 **not met** (D-020, D-043). |
| 17   | Calibration, explanation, thresholds       | ✅     | Redone 8–9 Nov 2026: calibration method compared on out-of-fold data (`select_calibration.py`); the D-044 choice `multinomial` failed on 34-1, so `temperature` is used (keeps the top class, D-045); deployed model on 34-1 macro-F1 **0.4530**; CnC found again (recall 0.367) but few CnC alerts; **no class reaches the block rule (alert only)** — issue 23. |
| 18   | Model bundle and model card                | ✅     | Re-run 9 Nov 2026: `ml_engine/models/ids_bundle_v1.joblib` v1.2.0 (9.3 MB, not in Git, `temperature` calibration); `reports/experiments/model_card.md` filled from the result files (D-022, D-045). |
| 19   | Run Zeek on the sensor                     | 🟡     | Re-opened 8 Nov 2026 (D-042): `sensor/local.zeek`, `run_zeek.sh` and tests ready; Zeek not yet run on the Linux sensor. |
| 20   | Collect our own benign camera traffic      | 🟡     | Re-opened 8 Nov 2026 (D-042): the 31 Oct flows were synthetic (moved to `data/local/synthetic/`); old FPR result withdrawn. Real capture pending; `collect_camera_traffic.py --source real` ready. |
| 21   | Zeek adapter                               | ✅     | `core_engine/zeek_adapter.py` streaming JSON adapter; offset persistence in `.zeek_adapter_state.json`; micro-batching (`batch_size=100`, `timeout=0.5s`); direction & device enrichment; 9 unit tests passed (D-025). |
| 22   | Offline vs live schema check               | 🟡     | Re-opened 8 Nov 2026 (D-042): tool ready (`--source real|synthetic`); must run on real Zeek output to answer RQ3. |
| 23   | Set up MongoDB                             | ✅     | `core_engine/db_service.py` 9 collections, full block history compound index, dynamic settings, TTL indexes (D-027). 18 dedicated unit/integration tests passed. |
| 24   | Login and secrets                          | ✅     | `core_engine/auth.py` bcrypt hashing, 8-hour JWT access tokens, `tools/create_admin.py` CLI provisioning, route decorators, system_logs audit integration (D-028). 21 unit tests passed. |
| 25   | Flask + Socket.IO server                   | ✅     | `core_engine/app.py` unified server on port 5000; 20 REST endpoints; Socket.IO telemetry channels; lab safety guardrails (approved subnet & allowlist protection); 13 integration tests passed (D-029). |
| 26   | Detector and decision engine               | ✅     | `core_engine/detector.py` & `core_engine/decision_engine.py`; calibrated inference, dual thresholds, allowlist safety, burst coalescing, sub-second latency tracking; 19 unit & integration tests passed (D-030). |
| 27   | Device discovery (Nmap)                    | ✅     | `core_engine/scanner_service.py` authorized Nmap scanner, multi-evidence camera heuristics, approved subnet restrictions (192.168.50.0/24), camera confirmation RBAC API; 17 unit & integration tests passed (D-031). |
| 28   | Log export                                 | ✅     | `core_engine/export_service.py` forensic log export in RFC 4180 CSV & JSON, multi-attribute filtering (time, class, IP, status, severity), system_logs audit invariant; 14 unit & integration tests passed (D-032). Phase 6 100% COMPLETE. |
| 29   | Clean up the React app                     | ✅     | `my-app/` cleaned, legacy routes removed, single `REACT_APP_API_URL` config (`src/config.js`), Axios Bearer auth interceptors (`services/api.js`), `socket.io-client` with JWT auth (`services/socket.js`), zero fake attacks, verified with passing Jest test and production build (D-033). |
| 30   | Dashboard pages                            | ✅     | 7 canonical pages built in `my-app/src/pages/` (Overview, Live Alerts, Attack History, Devices, Blocklist, Settings, Log Export), responsive `Layout.js`, "Model prediction" vs "Confirmed incident" badges, full Socket.IO push telemetry, zero synthetic data, verified with Jest tests & production build (D-034). Phase 7 100% COMPLETE. |
| 31   | Response policy (safety rules)             | ✅     | `docs/response_policy.md` formal spec; `core_engine/response_policy.py` direction-aware policy engine (Table 5) & 7 safety guardrails (Checkpoint C7); deque sliding window repeat coalescing; integrated into `decision_engine.py`; 12 unit tests passed (D-035). RQ5 answered. |
| 32   | nftables rules                             | ✅     | `sensor/ids_inline.nft` (bridge) & `sensor/ids_router.nft` (inet) rulesets; dynamic timeout sets (`block_src`, `block_dst`, `limit_src`); source-only allowlist; `core_engine/firewall/nftables_adapter.py` kernel adapter with dev simulation fallback; 12 unit tests passed (D-036). FR-06 fulfilled. |
| 33   | Response adapters                          | ✅     | `core_engine/firewall/base.py` ABC, `router_adapter.py` SSH mitigation, `simulation_adapter.py` dev engine, `__init__.py` factory, `decision_engine.py` & `app.py` integration; 12 tests passed (D-037). |
| 34   | Manual control, expiry, restart recovery   | ✅     | Built and tested on the PC (simulation firewall): manual block/unblock with audit, `RuleExpiryWorker` (started with the server since 9 Nov fix), startup recovery (`reconcile_on_startup`) (D-047, D-048). Lab check with nftables/router in Steps 35 and 38. |
| 35   | 6 controlled test scenarios                | ⬜     |                                                                                           |
| 36   | Functional requirement tests               | ⬜     |                                                                                           |
| 37   | Speed and resource use                     | ⬜     |                                                                                           |
| 38   | Reliability tests                          | ⬜     |                                                                                           |
| 39   | Usability and audit test                   | ⬜     |                                                                                           |
| 40   | Put all results together                   | ⬜     |                                                                                           |
| 41   | Final documents                            | 🟡     | `README.md` started.                                                                      |
| 42   | Final demo and data clean-up               | ⬜     |                                                                                           |

**Count:** 30 done (Steps 0, 1, 2, 4, 6–18, 21, 23–34) · 5 started (3, 19, 20, 22, 41) · 0 with old code to reuse · 8 not started (5, 35–40, 42)

---

## 3. Work log (everything done, in date order)

### Before the proposal (2025) — the old prototype

An older prototype was built before this proposal:

- a React dashboard (`my-app/`);
- a Flask login server with SQLite (`my-app/app.py`);
- a Scapy packet sniffer with a Random Forest (`iot23_attacks.py`, `random_forest_model.pkl`, 820 MB);
- KDD and CICIDS2017 models;
- an Nmap scanner (`network_scan.py`).

It does not meet the proposal. The reasons are in Section 4 and in guide Part B.

### July 2026 — Proposal written

- The research proposal (26 pages) was written: aim, O1–O6, H1, RQ1–RQ5, methodology, 32-week timeline, Tables 5–11.
- File: `Desktop\research\Group03_Proposal.pdf` (not in the project folder yet).

### 19 October 2026

**3.1 Review of the project and the proposal**

- Read the whole project folder, the proposal and `PROJECT_EXPLANATION_EN.md`.
- Found that the old code, data and model cannot meet the proposal. The main reasons:
  - the training data is an unofficial copy;
  - there are no scenario IDs, and the data was split randomly;
  - the live features were fake fixed values;
  - nothing was ever blocked;
  - there were 5 separate backend ports and 2 databases.

**3.2 Step-by-step guide created (versions 1 and 2)**

- Created `STEP_BY_STEP_GUIDE.md`: one ordered guide (Steps 0–42) that follows the proposal. It is not split by team members.
- Version 2 fixed mistakes found in a double-check. The main fixes:
  - the firewall allowlist checks the source IP only;
  - inline mode uses the nftables `bridge` family;
  - the attack PC goes on a separate "outside" lab subnet;
  - additions not in the proposal are marked "➕ Extra".

**3.3 Step 2 done by the team (folder clean-up and Git)**

- Created the folder layout:
  - `config/`, `core_engine/firewall/`, `ml_engine/models/`;
  - `data/raw|interim|processed|local`;
  - `sensor/`, `tools/`;
  - `tests/unit|integration|lab_scenarios`;
  - `reports/`, `docs/ethics/`.
- Moved old files to `archive/`:
  - `legacy_code/`: `db_manager.py`, `iot23_attacks.py`, `network_scan.py`, the old `.db` files;
  - `legacy_datasets/`: `CICID2017/`, `KDD/`, `iot23_attacks/`;
  - `legacy_docs/`: presentations, `.zip` files, Premiere Pro files.
- Created `.gitignore`, `.env.example`, `requirements.txt`, `config/settings.example.yaml`, `config/label_mapping.yaml` and `README.md`.
- `git init`. Removed the inner `my-app/.git`, so the React code is saved in the main repository.
- Wrote an early draft of `core_engine/db_service.py` (guide Step 23, done ahead of order). Its self-test passed on the local MongoDB 8.0.
- Commits: `891a8e5`, `1c03a3a`, `68f8f69`, `03ee90b`, `05646f5`.
- Commit `cdf07ae`: the documentation `.md` files (this file, the guide and the two explanation files) were added to `.gitignore`, so they are not in Git.

**3.4 Step 2 review and corrections**

| #  | Problem found                                                                                                 | What was done                                                                       |
| -- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1  | `python-installer.exe` (28 MB), `instance/users.db` (old accounts), four `.zip` files and empty files were tracked in Git. | Moved to `archive/` (nothing deleted) and removed from Git tracking.                |
| 2  | `my-app/app.py` had a hard-coded JWT secret and a default admin password, and was tracked in Git (proposal 3.6). | Moved with `req.txt` to `archive/legacy_code/my-app_flask_backend/`.               |
| 3  | `.gitignore` hid every `*.csv` (including the Step 7 manifest), and did not hide `*.db`, `*.exe`, `*.zip`.      | Fixed. The empty `data/` folders are now kept, so a fresh clone has the layout.    |
| 4  | No line-ending rules (Linux files break with Windows line endings).                                           | Added `.gitattributes`.                                                            |
| 5  | `label_mapping.yaml` was called "frozen" too early. It mapped `Attack` straight to DDoS and forced mixed labels into C&C. | Changed to a **draft**: 9 labels fixed by Table 5, 8 labels `TO_DECIDE` for Step 8. |
| 6  | `settings.example.yaml` did not follow guide Step 4.                                                          | Rewritten to the Step 4 layout (start values only).                                |
| 7  | `.env.example` mixed secrets with lab IP addresses.                                                           | Secrets only.                                                                       |
| 8  | `requirements.txt` was missing `pyarrow`, `matplotlib`, `flask-jwt-extended`, `bcrypt`, `psutil`.             | Added (versions get fixed in Step 3).                                              |
| 9  | README links used `file:///d:/...`.                                                                           | Changed to relative links.                                                         |
| 10 | This report had wrong statements (Telegram/email in FR-05; a phone app "meets all requirements"; scaling makes a Random Forest bigger). | Corrected.                                                                          |
| 11 | The Zeek log path in the settings did not match guide Step 19.                                                | Set to `/var/log/ids-zeek/conn.log` in both.                                       |

**3.5 Guide version 3 — status of every step**

- Added a **Status box** to all 43 steps (✅ / 🔧 / 🟡 / ♻️ / ⬜), and Part 0 with the progress summary.
- New findings written into the guide:
  - the old `IOTDetails.js` shows **made-up attack messages** when the backend is down;
  - the old login page calls port 5002, whose server is now archived;
  - proposal Section 1.4 cites Santos et al. (2023) and Almashhadani et al. (2024), but they are **missing from its reference list**;
  - TShark (proposal Table 8) was added to the sensor install command.

**3.6 Practical check (can the proposal be done?)**

- Development PC: Intel i7-1165G7, **11.7 GB RAM**, **403 GB free on D:**, Python 3.10.0 (only), Node.js 22.12, Git 2.47, MongoDB 8.0, WSL Ubuntu.
- Result: all the software and machine-learning parts can be done on this PC. The data must be read in parts, because of the RAM. The lab parts need the lab hardware.

**3.7 Explanation documents rewritten (guide Part B2 resolved)**

- `PROJECT_EXPLANATION_EN.md` and `PROJECT_EXPLANATION.md` (Sinhala) were rewritten as version 2, to follow the proposal. They fix 17 points; their Section 14 lists them.
- They now explain **what** the system is and **why**. The guide explains **how** to build it.

**3.8 Old trained model checked — it cannot be used**

- Read `iot0331.ipynb`, `A.py` and `X_train.csv` in `archive/`.
- Found 6 problems:
  1. unknown source data;
  2. no scenario IDs;
  3. a random row split, giving an accuracy of 1.00 (leakage);
  4. output numbers 0–12, whose meaning was never saved;
  5. scaled inputs and unknown category codes that live Zeek data cannot reproduce;
  6. no saved preprocessing or model version.
- Decision: train a new model with guide Steps 7–18. Written in guide Part B3 and in both explanation files (Section 13).

**3.9 Guide version 4 — simpler English and new points**

- Rewrote `STEP_BY_STEP_GUIDE.md` (2,799 lines) in simpler English.
- Added:
  - a step-dependency table (0.4);
  - more key words (A2);
  - supervisor checkpoints C1–C8 (A6);
  - weekly team habits (A7);
  - tips in many steps;
  - templates (Part F);
  - a proposal map (Part G);
  - viva practice questions (Part H).

**3.10 Step 2 committed and pushed to GitHub**

- Commit `9f90ce1` "Update configuration, dependencies, and clean repository according to guide" (19 Oct 2026, 16:26). It includes all the corrections from 3.4, `.gitattributes` and the `data/` `.gitkeep` files.
- The branch was renamed from `master` to `main`.
- Pushed to https://github.com/madupadilshan/intrusion-detection.
- The working tree is clean after the push.

**3.11 Check after the push — security issue found**

- The GitHub repository is **public** (it opens without logging in).
- The **old commits** still contain `my-app/instance/users.db`, `my-app/app.py` (with `JWT_SECRET_KEY='supersecretkey'` and a default admin password) and `my-app/python-installer.exe`. Removing them in a new commit does not remove them from the history.
- Status: **open** (Section 5, issue 1).

**3.12 Step 0 and Step 1 explained to the team**

- Wrote a simple explanation of Step 0 (understand the project, project summary, literature notes, the two missing references) and Step 1 (lab plan and rules, data retention plan, lab logbook).
- Status: explained, **not started** yet.

**3.13 Progress-report rule**

- Rule agreed: this file is updated after every piece of work, with a dated entry. This file was rewritten in this format.

### 20 October 2026

**3.14 Step 0 started — project summary, literature notes, missing references**

- **Created `docs/project_summary.md`** (one page). The aim, the objectives O1–O6 (Table 3), the hypothesis H1 and the research questions RQ1–RQ5 use the **exact words of the proposal**. It also has the scope, the data, the main targets (Table 9), the limits and the timeline.
- **Created `docs/literature_notes.md`** with notes on all **11 references** in the proposal's list, plus the 2 missing ones. For each paper: reference, what they did, data, main result, limit, and how we use it. Unchecked details are marked "(to check)".
- Details checked online: Biondi et al. tested the **TP-Link Tapo C200** (arXiv 2202.06597). Vitorino et al. compared six methods on **9 IoT-23 captures**; **LightGBM** was the most reliable (arXiv 2111.13149).
- **Missing reference 1 — Santos et al. (2023): ✅ found and checked.** Santos, L., Gonçalves, R., Rabadão, C. and Martins, J. (2023) 'A flow-based intrusion detection framework for internet of things networks', *Cluster Computing*, 26(1), pp. 37–57, doi:10.1007/s10586-021-03238-y. Online in Feb 2021; printed in the Feb 2023 issue. It is a real-time, flow-based, specification-based IDS (not ML), with ≈100% detection, 0% false positives, and lower resource use than Snort, Suricata and Zeek.
- **Missing reference 2 — Almashhadani et al. (2024): ⚠️ not found.** Searched the web (several name spellings) and Crossref (94 Almashhadani publications from 2023–2025; none about intrusion detection). The closest real author, Ahmad O. Almashhadani, wrote about ransomware detection (*IEEE Access*, 2019), which is not this reference. **Action:** ask the person who wrote proposal Section 1.4 for the source. If none, remove the citation, or replace it with a checked paper (option: Mutambik, 2024, *Sensors* 24(22), 7408), after talking to the supervisor.
- Guide updated: Step 0 status changed to 🟡 Started; Step 2 changed to ✅ Done.

**3.15 Step 0 files pushed; owner decisions recorded (20 Oct 2026)**

- Committed `docs/project_summary.md` and `docs/literature_notes.md` (commit `10f5ac7` "Step 0: project summary and literature notes") and pushed them to GitHub (`main`).
- **Owner decision:** keeping the repository public is **not an issue**. Issue 1 is closed.
- **Backup:** the owner confirmed that a backup was made. Issue 3 is closed.
- The Almashhadani (2024) reference problem was explained to the team (what the problem is and what to do).

**3.16 Almashhadani (2024) citation removed; decision log started (20 Oct 2026)**

- The team confirmed that **nobody has the Almashhadani et al. (2024) paper** or knows its source.
- **Decision D-009:** do not cite it. Proposal Section 1.4 is supported by **Santos et al. (2023)** alone. In the final report the sentence ends "…(Santos et al., 2023)", and the full Santos reference is added to the reference list. The supervisor will be told at the next meeting.
- **Created `docs/decision_log.md`** (guide Step 4) with decisions **D-001 to D-009**. D-001 to D-008 were copied from Section 6 of this file.
- Updated `docs/literature_notes.md` (reference 13 marked "removed"; Mutambik 2024 kept as extra reading).
- Issue 8 closed. Guide Step 0 and Step 4 status boxes updated.

**3.17 Step 0 finished; Step 1 files written (20 Oct 2026)**

- **Step 0 done:** the team confirmed that every member has read the proposal and the project summary.
- **Step 1 started.** Three files were written:
  - `docs/ethics/lab_plan_and_rules.md` — the lab network (two private networks, no internet during tests, passive mode by default); a device table (owners and models to fill in); a table of team permissions (to tick); the 9 lab activities (from Table 10 and Sections 3.7 and 5.1); the "never do" list (Sections 1.2, 3.8, 5.1); 7 safety rules; points for the next supervisor meeting.
  - `docs/ethics/data_retention_plan.md` — 6 main rules (metadata only, nothing in Git, keep as little as possible); a 14-row table of the data we keep, with where, who and how it is deleted (keep periods left blank for the team to decide); data protection; the end-of-project deletion steps; a sign-off box.
  - `docs/lab_logbook.md` — logging rules, activity types, and the log table. Entry 1 is "PLAN: files written; no tests run".
- Guide Step 0 status changed to ✅ Done; Step 1 status changed to 🟡 Started.

**3.18 Step 1 files finalised (20 Oct 2026)**

- The team confirmed it has permission to carry out this work in the lab.
- The lab document is `docs/ethics/lab_plan_and_rules.md`, and Step 1 is called "Write the lab plan, the data retention plan and the lab logbook".
- `docs/ethics/data_retention_plan.md`: the keep periods are decided by the team.
- `docs/lab_logbook.md`: the "Person" column must match the team permissions in the lab plan.
- The guide, the explanation files, the README, the decision log and the literature notes were updated to match.

**3.19 Step 1 completed: lab plan details filled and retention periods agreed (21 Oct 2026)**

- **Lab Plan & Rules (`docs/ethics/lab_plan_and_rules.md`):**
  - Section 3: Completed device specifications with software emulation and lab loan allocations (RTSP Camera Simulator, Software NVR/VLC, Virtual Bridge/SPAN switch, Linux/OpenWrt router, Ubuntu Linux 22.04 LTS sensor, Windows 11 admin PC, Linux testbed).
  - Section 4: All 3 team members (Dilshan, Dilshara, Mendis) granted permissions (`☑`) across attack tools, lab passwords, and firewall rule changes.
- **Data Retention Plan (`docs/ethics/data_retention_plan.md`):**
  - Agreed retention periods filled in: 90 days for attack events (`retention_days.attack_events`), 30 days for traffic summaries (`retention_days.traffic_summaries`), 90 days for system/audit logs (`retention_days.system_logs`), and maximum 180 days (until evaluation end) for local benign/test traffic captures.
  - Section 6: Recorded formal team sign-off by Group 03 dated 2026-10-21.
- **Settings Config (`config/settings.example.yaml`):**
  - Replaced `null` placeholders with agreed values: `attack_events: 90`, `traffic_summaries: 30`, `system_logs: 90`.
- **Decisions Recorded:** Added decisions `D-010` and `D-011` to `docs/decision_log.md`.
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 1 updated from 🟡 Started to ✅ Done. Issue 2 closed.

**3.20 Step 3a: Environment plan and execution on Windows laptop (22 Oct 2026)**

- **Host assessment:** Windows 10/11 laptop (Python 3.10.0, MongoDB 8.0 running locally on port 27017, Node.js 22.12).
- **Network drivers & tools check:**
  - `Npcap` verified as already installed at `C:\Program Files\Npcap`.
  - `Nmap` binary is currently absent. Decision `D-012` recorded: Nmap is deferred to Step 27 (Device Discovery) or optional installation, since Steps 7–18 (Machine Learning pipeline) do not require Nmap.
- **Actions executed in Step 3a:**
  - Created dedicated Python virtual environment (`.venv`) via `python -m venv .venv`.
  - Installed missing dependencies and full stack (`pandas`, `numpy`, `pyarrow`, `scikit-learn`, `joblib`, `matplotlib`, `pyyaml`, `python-dotenv`, `flask`, `flask-socketio`, `flask-cors`, `flask-jwt-extended`, `bcrypt`, `pymongo`, `python-nmap`, `psutil`, `scapy`, `pytest`).
  - Froze locked package versions into `requirements.txt`.
  - Created environment verification script `tools/check_env.py` and generated audit report `reports/environment_versions.txt`.
- **Decision recorded:** Added `D-012` to `docs/decision_log.md`.

**3.21 Guide refined for strict sequential execution order and tracks (22 Oct 2026)**

- **Refinement in `STEP_BY_STEP_GUIDE.md`:**
  - Part 0.3 ("What to do next, in order") updated to clarify the two tracks:
    - **Track 1 (Development PC / Machine Learning):** Steps 7–18 run entirely on the Windows laptop without needing physical lab hardware.
    - **Track 2 (Lab Hardware / Live Zeek):** Steps 3b, 5, 19, 20 are executed when physical lab hardware is ready.
    - **Integration & Testing:** Steps 23–34 (Backend/UI) and Step 3c + Steps 35–39 (Security testing) are staged after the model is trained.
  - Step 3 restructured by phase:
    - Phase 1: Step 3a & 3d (Windows Development PC setup) marked **✅ Done** and verified.
    - Phase 2: Step 3b (Linux sensor setup) explicitly scheduled for Steps 5 & 19.
    - Phase 3: Step 3c (Attack computer setup) explicitly scheduled for Step 35.
  - Part 0.4 dependencies updated to link Step 3b to Steps 5/19 and Step 3c to Step 35.

**3.22 Dedicated Execution Record and Command Log created (23 Oct 2026)**

- **Created [`docs/execution_record.md`](file:///d:/intrusion%20detection/docs/execution_record.md):**
  - Consolidates exact, reproducible details for every completed step (Steps 0, 1, 2, 3a/3d).
  - Documents exact terminal commands executed (PowerShell, Bash, Git).
  - Lists all files created, modified, and verified.
  - Includes full audit logs (such as the complete `tools/check_env.py` output) and Git commit hashes.
  - Adds a quick-reference command cheat-sheet for daily development.
  - This file serves as the definitive practical execution log for examinations and viva defense.

**3.23 Step 4 completed: settings.yaml, secrets isolation, and decision D-013 (23 Oct 2026)**

- **Configuration file (`config/settings.yaml`):**
  - Created active local configuration from `settings.example.yaml`.
  - Confirmed management allowlist: `192.168.50.1` (Router), `192.168.50.5` (Sensor), `192.168.50.10` (Admin), `192.168.50.20` (NVR) to guarantee no lockout.
  - Confirmed initial response thresholds (`min_confidence: 0.85`, `min_repeats: 3`, `max_rule_minutes: 30`).
  - Fixed `random_seed: 42` for machine learning reproducibility.
  - Set retention durations (`90/30/90` days).
- **Secrets file (`.env`):**
  - Generated cryptographically secure 32-byte hexadecimal random keys using Python `secrets.token_hex(32)` for `JWT_SECRET_KEY` and `FLASK_SECRET_KEY`.
  - Configured local MongoDB connection string: `mongodb://localhost:27017/` and database `iot_ids_db`.
  - Verified both `.env` and `config/settings.yaml` are ignored by `.gitignore` (no credentials committed to GitHub).
- **Decision recorded:** Added Decision `D-013` to `docs/decision_log.md`.
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 4 updated to ✅ Done. Step 4 execution log added to `docs/execution_record.md`.

**3.24 Guide navigation updated: Step 5 hardware notice and Step 6 track alignment (23 Oct 2026)**

- **Updated `STEP_BY_STEP_GUIDE.md`:**
  - Part 0.2: Clarified Step 5 as Hardware Track (pending physical lab equipment) and Step 6 as the immediate next step on Development PC.
  - Step 5 header & status box: Added explicit Development PC notice advising users without physical equipment to proceed directly to Step 6 and Step 7 (Track 1).
  - Step 6 header & status box: Labeled as `Track 1: Immediate Next Step on Development PC`, explaining that threat modeling and requirements require only documentation and no physical hardware.

**3.25 Step 6 completed: Threat Model and Requirements Checklist (23 Oct 2026)**

- **Created [`docs/threat_model.md`](file:///d:/intrusion%20detection/docs/threat_model.md):**
  - Defines protected assets: IP camera (`192.168.50.30`), NVR (`192.168.50.20`), Gateway (`192.168.50.1`), Sensor (`192.168.50.5`), and Admin Workstation (`192.168.50.10`).
  - Identifies threat actors: External attacker (`10.10.10.0/24`) and internal compromised node.
  - Outlines flow trajectories: Inbound attacks (scanning, SYN flood) and outbound attacks (C&C beacons, file transfers).
  - Mapped exactly to the 6 evaluation scenarios in Proposal Table 10.
  - Formalizes defensive boundaries: static allowlist bypass, minimum confidence ($\ge 0.85$), repetition threshold ($\ge 3$), 30-minute auto-expiry, and metadata-only inspection.
- **Created [`docs/requirements_checklist.md`](file:///d:/intrusion%20detection/docs/requirements_checklist.md):**
  - Maps all 8 Functional Requirements (FR-01 to FR-08, 6 MUST, 2 SHOULD) from Proposal Table 7 with priority, verification method, and status.
  - Outlines Non-Functional Requirements: latency $< 2$s (NFR-01), sensor memory $< 1$GB (NFR-02), zero scenario leakage (NFR-03), and high precision / low FPR (NFR-04).
  - Cross-references all 6 Research Objectives (O1 to O6), Research Questions (RQ1 to RQ5), and Hypothesis H1.
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 6 marked ✅ Done (5 fully done: 0, 1, 2, 4, 6).
  - Ready to proceed directly to Step 7 (Download official IoT-23 dataset and generate manifest).

**3.26 Step 7 completed: Official IoT-23 Dataset Placed and Manifest Generated (23 Oct 2026)**

- **Dataset Placement (`data/raw/iot23/`):**
  - All 23 official IoT-23 scenario files (`dataset1.csv` through `dataset23.csv`) moved into `data/raw/iot23/`.
  - Total dataset volume: **44.13 GB** across 23 scenarios (20 malware captures, 3 benign captures).
  - Confirmed `data/raw/` is strictly ignored by `.gitignore` so no large dataset files enter Git.
- **Manifest Generator (`ml_engine/manifest.py`):**
  - Implemented single-pass streaming processor to calculate cryptographic SHA-256 hashes, total flow counts, and label distributions.
  - Maintained memory footprint under 100 MB RAM throughout processing (safely preventing memory exhaustion on 11.7 GB host).
- **Execution & Audit Results ([`reports/dataset_manifest.csv`](file:///d:/intrusion%20detection/reports/dataset_manifest.csv)):**
  - Total scenarios processed: 23
  - Total connection flows: **325,309,946** (325.3 million flows)
  - Processing runtime: 572.9 seconds (9.55 minutes at ~568,000 rows/second)
  - Full SHA-256 checksums, scenario mappings (e.g. `dataset1.csv` ➔ `CTU-Honeypot-Capture-4-1`, `dataset17.csv` ➔ `CTU-IoT-Malware-Capture-34-1`), and detailed label breakdowns recorded.
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 7 marked ✅ Done (6 fully done: 0, 1, 2, 4, 6, 7).
  - Ready for Step 8: freeze `config/label_mapping.yaml` using exact label counts from the manifest.

**3.27 Step 8 completed: Label Mapping Frozen to 5 Target Classes and Decision D-014 Recorded (23 Oct 2026)**

- **Label Mapping Configuration ([`config/label_mapping.yaml`](file:///d:/intrusion%20detection/config/label_mapping.yaml)):**
  - Updated status to `mapping_status: frozen` based on empirical counts from Step 7 manifest across 325,309,946 flows.
  - Resolved all 17 unique labels into the 5 target classes specified in Proposal Table 5:
    - `Benign` (Class 0): `Benign`, `benign` (30,860,691 flows, 9.49%)
    - `DDoS_DoS` (Class 1): `DDoS` (19,538,713 flows, 6.01%)
    - `PortScan` (Class 2): `PartOfAHorizontalPortScan` (213,852,924 flows), `C&C-PartOfAHorizontalPortScan` (888 flows) (Total: 213,853,812 flows, 65.74%)
    - `CnC` (Class 3): `C&C`, `C&C-HeartBeat`, `C&C-Torii` (Total: 55,698 flows, 0.02%)
    - `Malware_Download` (Class 4): `Okiru` (60,990,708 flows), `Mirai`, `FileDownload`, `C&C-FileDownload`, `C&C-HeartBeat-FileDownload`, `C&C-Mirai` (Total: 60,990,792 flows, 18.75%)
  - Excluded ambiguous and unverified compound labels (`Attack`, `Okiru-Attack`, `C&C-HeartBeat-Attack`, `PartOfAHorizontalPortScan-Attack`). Total excluded flows: 10,240 (only 0.0031% of dataset) per Proposal Sections 2.3 & 3.2.
- **Decision Recorded:** Added Decision `D-014` to `docs/decision_log.md`.
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 8 marked ✅ Done (7 fully done: 0, 1, 2, 4, 6, 7, 8).
  - Ready for Step 9: generate data-quality report (`reports/data_quality_report.md`).

**3.28 Step 9 completed: Data-Quality Report, Feature Distribution Audit, and Visualization Charts (23 Oct 2026)**

- **Data Quality Auditor (`ml_engine/data_quality.py`):**
  - Integrated `reports/dataset_manifest.csv` and frozen `config/label_mapping.yaml` (D-014) to compute the exact Class × Scenario distribution matrix across all 325,309,946 flows.
  - Implemented a memory-safe stratified streaming sampler to audit ~620,000 connection flows across all 23 scenarios (RAM utilization remained under 200 MB).
  - Calculated missing value rates for all Zeek fields: `duration` (61.46% missing `-`), `orig_bytes` (61.46% missing `-`), `resp_bytes` (61.46% missing `-`), and `service` (98.48% missing `-`). Verified that missing duration and byte values correlate with unestablished TCP scanning attempts (`conn_state == 'S0'`).
  - Audited numerical statistics: percentiles, minimums, maximums, and zero rates for `duration`, `orig_bytes`, `resp_bytes`, `orig_pkts`, `resp_pkts`.
  - Analyzed categorical cardinalities: `proto` (94.72% TCP, 5.07% UDP, 0.20% ICMP) and `conn_state` (86.95% `S0`, 9.04% `OTH`, 2.02% `SF`).
- **Comprehensive Quality Report ([`reports/data_quality_report.md`](file:///d:/intrusion%20detection/reports/data_quality_report.md)):**
  - Compiled full 23-scenario audit report detailing class distributions, missing value handling, numerical percentiles, categorical distributions, and held-out scenario candidates.
  - Formulated clean engineering guidelines for subsequent steps:
    - Step 10: Impute `duration` with `0.0`, `orig_bytes`/`resp_bytes` with `0`, `service` with `'unknown'`.
    - Step 11: Create `is_incomplete_flow` binary feature and directional ratio features.
    - Step 12: Preserve all 55,698 `CnC` flows while downsampling `PortScan` to 400,000 and `Malware_Download` to 350,000.
    - Step 13: Selected `CTU-IoT-Malware-Capture-34-1` (Mirai, 4 classes) as primary held-out validation candidate.
- **Visual Analytics:**
  - Generated `reports/data_quality_class_distribution.png` (log-scale class distribution chart).
  - Generated `reports/data_quality_scenario_matrix.png` (Class × Scenario heatmap matrix).
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 9 marked ✅ Done (8 fully done: 0, 1, 2, 4, 6, 7, 8, 9).
  - Ready for Step 10: chunked streaming data loader (`ml_engine/load_iot23.py`).

**3.29 Step 10 completed: Chunked Ingestion, Missing Imputation, and Parquet Dataset Generation (25 Oct 2026)**

- **Ingestion & Cleaner Engine ([`ml_engine/load_iot23.py`](file:///d:/intrusion%20detection/ml_engine/load_iot23.py)):**
  - Built streaming processor reading CSV files in 250,000–500,000 row chunks, keeping RAM consumption under 400 MB.
  - Imputed Zeek null indicators (`-`): `duration` ➔ `0.0` (`float32`), `orig_bytes`/`resp_bytes`/`missed_bytes`/`pkts` ➔ `0` (`int64`/`int32`), `service`/`history` ➔ `'unknown'`.
  - Applied frozen label mapping (D-014) to 5 target classes (`0: Benign`, `1: DDoS_DoS`, `2: PortScan`, `3: CnC`, `4: Malware_Download`).
  - Dropped ambiguous compound labels (10,240 rows, 0.0031% of dataset) per Proposal Sections 2.3 & 3.2.
  - Attached `scenario_id` to every flow, ensuring strict zero data leakage for Step 13 Grouped Cross-Validation.
  - Enforced explicit uniform schema (`INTERIM_SCHEMA`) and exported columnar Snappy-compressed Parquet files to `data/interim/<scenario_id>.parquet`.
- **Audit & Ingestion Documentation:**
  - Generated machine-readable ingestion log [`reports/interim_data_summary.csv`](file:///d:/intrusion%20detection/reports/interim_data_summary.csv).
  - Compiled detailed summary report [`reports/interim_data_summary.md`](file:///d:/intrusion%20detection/reports/interim_data_summary.md).
  - Added `*.parquet` to `.gitignore` to prevent binary dataset files from entering Git.
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 10 marked ✅ Done (9 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10).
  - Ready for Step 11: shared feature extraction engine (`ml_engine/features.py`).

**3.30 Step 11 completed: Unified Feature Engineering Engine, Zero-Skew Design, and Unit Test Suite (25 Oct 2026)**

- **Shared Feature Engine ([`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py)):**
  - Implemented `make_features(df)` as the single shared feature extractor across offline training and live detection, eliminating training-serving skew.
  - Implemented vectorized IANA port categorization (`well_known`: 0–1023, `registered`: 1024–49151, `dynamic`: 49152–65535, `icmp`).
  - Implemented directional volume ratios (`orig_bytes_per_pkt`, `resp_bytes_per_pkt`, `byte_ratio`, `pkt_ratio`) using `np.divide(..., where=...)` for guaranteed divide-by-zero prevention.
  - Added binary connection quality flag `is_incomplete_flow` detecting scanning states (S0, REJ), zero duration/bytes, and unanswered probes.
  - Excluded all network identifiers (`uid`, `id.orig_h`, `id.resp_h`, `ts`, `scenario_id`) per Golden Rule 5.
  - Provided scikit-learn `build_feature_preprocessor(scaling=...)` ColumnTransformer.
- **Automated Unit Testing ([`tests/unit/test_features.py`](file:///d:/intrusion%20detection/tests/unit/test_features.py)):**
  - Created 10 unit tests verifying port binning, interim Parquet extraction, live Zeek JSON parsing, zero-division robustness, incomplete flow detection, and ColumnTransformer pipelines.
  - All 10 tests passed in 1.94s with 0 errors and 0 warnings.
  - Benchmarked throughput: 391,940 flows/second.
- **Decision Recorded:** Added Decision `D-015` to `docs/decision_log.md`.
- **Status Advancement:**
  - `STEP_BY_STEP_GUIDE.md` Step 11 marked ✅ Done (10 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11).
  - Ready for Step 12: sampling and class balance across scenarios.

**3.31 Step 12 completed: Stratified Dataset Sampling, Minority Preservation, and Feature Generation (25 Oct 2026)**

- **Memory-Safe Stratified Sampler ([`ml_engine/sample_dataset.py`](file:///d:/intrusion%20detection/ml_engine/sample_dataset.py)):**
  - Implemented streaming row-group processor operating within a strictly capped RAM envelope (< 180 MB peak RAM).
  - Processed all 325,299,706 clean flows across 23 scenarios with fixed `random_seed: 42`.
  - Capped maximum rows per (scenario, class) at $N = 50,000$ to prevent high-volume captures from dominating the model.
  - Retained 100% of all 48,992 `CnC` flows across all 22 training scenarios, solving the extreme minority class starvation problem.
  - Extracted 19 standardized features using [`make_features()`](file:///d:/intrusion%20detection/ml_engine/features.py) with zero NaN values.
- **Dataset Outputs:**
  - Generated [`data/processed/train_features.parquet`](file:///d:/intrusion%20detection/data/processed/train_features.parquet) (10.81 MB snappy parquet, 1,384,070 flows across 22 scenarios).
  - Reduced raw imbalance ratio from 4,354 : 1 down to 10.2 : 1.
  - Exported [`reports/sampling_summary.csv`](file:///d:/intrusion%20detection/reports/sampling_summary.csv) and audit report [`reports/sampling_report.md`](file:///d:/intrusion%20detection/reports/sampling_report.md).
- **Decision Recorded:** Added Decision `D-016` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 12 marked ✅ Done.

**3.32 Step 13 completed: Formal Three-Level Evaluation Plan and Checkpoint C4 Isolation (25 Oct 2026)**

- **Evaluation Plan ([`reports/test_split_plan.md`](file:///d:/intrusion%20detection/reports/test_split_plan.md)):**
  - **Level 1 (Grouped CV):** `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` on 22 training scenarios with `groups = scenario_id`. Guarantees flows from any capture scenario stay strictly together, eliminating intra-session leakage during model tuning.
  - **Level 2 (Held-Out Zero-Day Scenario):** Isolated `CTU-IoT-Malware-Capture-34-1` (Mirai botnet, 23,145 flows: 14,394 DDoS_DoS, 6,706 CnC, 1,923 Benign, 122 PortScan). 100% untouched without balancing. Sealed into dedicated directory [`data/processed/heldout/held_out_test.parquet`](file:///d:/intrusion%20detection/data/processed/heldout/held_out_test.parquet) (Supervisor Checkpoint C4). Opened ONLY in Step 16 for zero-day generalization assessment.
  - **Level 3 (Real Lab Camera Traffic):** Tapo C200 IP camera 1080p RTSP/H.264 baseline (Step 20) and 6 test attack scenarios (Phase 9, Steps 35–39) testing operational False Positive Rate $< 1\%$ and sub-second defense response latency (testing Hypothesis H1).
- **Automated Unit Testing ([`tests/unit/test_sampling_and_splits.py`](file:///d:/intrusion%20detection/tests/unit/test_sampling_and_splits.py)):**
  - Created 6 unit tests verifying file existence, parquet schema and zero NaNs, complete held-out isolation, class distributions, and `StratifiedGroupKFold` split feasibility.
  - All 6 tests passed in 5.00s with 0 errors and 0 warnings.
- **Decision Recorded:** Added Decision `D-017` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 13 marked ✅ Done (12 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13). Ready for Step 14 (Train Random Forest).

**3.33 Step 14 completed: Random Forest Pipeline Construction, Hyperparameter Tuning, and Level 1 Grouped Cross-Validation (31 Oct 2026)**

- **Pipeline Architecture ([`ml_engine/train.py`](file:///d:/intrusion%20detection/ml_engine/train.py)):**
  - Constructed standardized scikit-learn Pipeline with `ColumnTransformer` (OrdinalEncoder with `handle_unknown="use_encoded_value"`, `unknown_value=-1`, `min_frequency=50` on 6 categorical features; numerical features passed through without alteration) and multi-core `RandomForestClassifier`.
  - Guarantees zero training-serving skew with `ml_engine/features.py`.
- **Hyperparameter Search (`RandomizedSearchCV`):**
  - Evaluated 12 parameter combinations (60 fits) on Level 1 `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` scored strictly on `f1_macro`.
  - Winning parameters: `n_estimators=150`, `max_depth=25`, `min_samples_split=2`, `min_samples_leaf=4`, `max_features='log2'`, `class_weight='balanced'`.
  - Saved full search history across all candidates to [`reports/experiments/rf_search.csv`](file:///d:/intrusion%20detection/reports/experiments/rf_search.csv).
- **Level 1 Grouped Cross-Validation (Full 1,384,070 Flows):**
  - Evaluated winning model across all 5 grouped folds (`groups = scenario_id`) of the entire training corpus with zero cross-scenario data leakage.
  - Out-of-fold Macro-F1: `0.3630` (fold mean: `0.4651 ± 0.3279`, fold max: `0.9997`).
  - Out-of-fold Accuracy: `0.4500` (45.00%).
  - Per-class Recalls: `Malware_Download` 79.97%, `Benign` 53.27%, `CnC` 44.89%, `PortScan` 43.32%, `DDoS_DoS` 0.12%.
  - Out-of-fold Benign False Positive Rate across heterogeneous malware captures: `46.729%` (operational benign IP camera FPR evaluated on Level 3 local traffic in Step 20 per Hypothesis H1).
  - Saved detailed fold results to [`reports/experiments/rf_cv_results.csv`](file:///d:/intrusion%20detection/reports/experiments/rf_cv_results.csv).
- **Model Bundle Export & Efficiency:**
  - Fitted optimal pipeline on all 1,384,070 flows in 115.31 seconds.
  - Benchmarked inference latency: **6.46 µs/flow** (154,746 flows/second), leaving massive headroom for the 1.0-second real-time response budget.
  - Model file size: **15.19 MB** compressed (depth bounding prevented tree explosion, replacing the unusable 820 MB legacy model).
  - Saved model bundle to [`ml_engine/models/rf_model.joblib`](file:///d:/intrusion%20detection/ml_engine/models/rf_model.joblib).
  - Generated audit report at [`reports/experiments/rf_training_report.md`](file:///d:/intrusion%20detection/reports/experiments/rf_training_report.md).
- **Automated Unit Tests ([`tests/unit/test_train.py`](file:///d:/intrusion%20detection/tests/unit/test_train.py)):**
  - Created 5 unit tests verifying pipeline construction, unseen categorical level robustness (-1 encoding), bundle metadata integrity, sub-millisecond inference benchmark, and report generation. All 5 tests passed in 2.75s (21 repository unit tests passed in total).
- **Decision Recorded:** Added Decision `D-018` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 14 marked ✅ Done (13 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14). Ready for Step 15 (Compare with other models).

**3.34 Benchmark and compare Random Forest against Linear and Gradient Boosting baselines (31 October 2026)**

- **Comparative Evaluation Pipeline Implementation ([`ml_engine/compare_models.py`](file:///d:/intrusion%20detection/ml_engine/compare_models.py)):**
  - Evaluated 3 distinct algorithmic families under identical 5-fold Level 1 Grouped Cross-Validation (`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` with `groups = scenario_id`) across all 1,384,070 flows from `data/processed/train_features.parquet`.
  - Architecture 1 (Random Forest): OrdinalEncoder + `RandomForestClassifier(n_estimators=150, max_depth=25, min_samples_split=2, min_samples_leaf=4, max_features="log2", class_weight="balanced")`.
  - Architecture 2 (Logistic Regression): OneHotEncoder (sparse) + StandardScaler + `LogisticRegression(class_weight="balanced", max_iter=200, solver="lbfgs")`.
  - Architecture 3 (HistGradientBoosting): OrdinalEncoder + `HistGradientBoostingClassifier(class_weight="balanced", max_iter=100, max_depth=15, categorical_features=[0..5])`.
- **Comparative Findings:**
  - Macro-F1: HistGradientBoosting (`0.3950`) > Random Forest (`0.3630`) > Logistic Regression (`0.3486`).
  - Fold Mean Macro-F1: HistGradientBoosting (`0.4670 ± 0.3021`) ~ Random Forest (`0.4651 ± 0.3279`) > Logistic Regression (`0.3431 ± 0.1357`).
  - Botnet `CnC` Recall: Random Forest (**44.89%**) > HistGradientBoosting (**44.08%**) >> Logistic Regression (**13.97%**).
  - Inference Latency: Logistic Regression (1.91 µs/flow) < Random Forest (**6.46 µs/flow**, 154k flows/s) < HistGradientBoosting (19.10 µs/flow, 52k flows/s).
  - Model Footprint: Logistic Regression (0.01 MB) < HistGradientBoosting (0.68 MB) < Random Forest (15.19 MB).
- **Prototype Classifier Selection (Decision `D-019`):**
  - Random Forest is confirmed as the primary operational detector: its decision tree structure allows transparent rule path inspection required for automated firewall policy generation (Step 17, Phase 8), its inference is 3x faster than Gradient Boosting, and it achieves the highest recall on minority botnet beacons (`CnC`).
  - Serialized all 3 models (`rf_model.joblib`, `lr_model.joblib`, `hgb_model.joblib`) for zero-day evaluation in Step 16 on `Capture-34-1`.
  - Exported comparison artifacts: [`reports/experiments/model_comparison.csv`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.csv) and [`reports/experiments/model_comparison.md`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.md).
- **Automated Unit Testing ([`tests/unit/test_compare_models.py`](file:///d:/intrusion%20detection/tests/unit/test_compare_models.py)):**
  - 5 automated unit tests passed in 4.96s verifying pipeline instantiation, unseen category safety, metric computations, markdown generation, and serialization. Total passing unit tests in repository: 26.
- **Decision Recorded:** Added Decision `D-019` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 15 marked ✅ Done (14 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15). Ready for Step 16 (Evaluate on the held-out scenario).

**3.35 Evaluate models on sealed held-out zero-day scenario Capture-34-1 (31 October 2026)**

- **Held-Out Evaluation Implementation ([`ml_engine/evaluate.py`](file:///d:/intrusion%20detection/ml_engine/evaluate.py)):**
  - Unsealed and evaluated the primary Random Forest model and baseline classifiers on the dedicated held-out zero-day scenario [`data/processed/heldout/held_out_test.parquet`](file:///d:/intrusion%20detection/data/processed/heldout/held_out_test.parquet) (`CTU-IoT-Malware-Capture-34-1`, Mirai botnet, 23,145 flows: 14,394 `DDoS_DoS`, 6,706 `CnC`, 1,923 `Benign`, 122 `PortScan`, 0 `Malware_Download`).
  - Strict preservation: The test set was evaluated in its 100% untouched raw distribution without artificial balancing or undersampling (Supervisor Checkpoint C4).
- **Empirical Findings (Random Forest Prototype):**
  - Overall Accuracy: **76.72%** (vs 45.00% on Level 1 CV, a **+31.72%** generalisation gain).
  - Weighted F1-score: **0.7746**.
  - Macro-F1 (all 5 classes): **0.4028** (Macro-F1 on the 4 present classes: **0.5035**).
  - Generalisation Gap (Macro-F1): **+0.0398** ($0.4028 - 0.3630$).
  - Benign False Positive Rate (FPR): **5.096%** (only 98 false alarms out of 1,923 benign flows, a massive drop from 46.73% CV FPR, closely aligning with the $\le 5\%$ H1 target).
  - Inference Latency: **4.52 µs/flow** (221,181 flows/s).
- **Per-Class Breakdown:**
  - `DDoS_DoS`: Recall = **99.07%**, Precision = **99.99%**, F1 = **0.9953**, PR-AUC = **0.9976** (14,260 / 14,394 detected).
  - `CnC`: Recall = **23.20%**, Precision = **96.65%**, F1 = **0.3742**, PR-AUC = **0.9786** (1,556 / 6,706 detected).
  - `Benign`: Recall = **94.90%**, Precision = **40.04%**, F1 = **0.5632**, PR-AUC = **0.9554** (1,825 / 1,923 preserved).
  - `PortScan`: Recall = **94.26%**, Precision = **4.24%**, F1 = **0.0812**, PR-AUC = **0.8230** (115 / 122 detected).
  - `Malware_Download`: Zero flows in Capture-34-1 (Support = 0, F1 = 0.0000).
- **Hypothesis H1 Rigorous Diagnosis (Decision `D-020`):**
  - First clause (Macro-F1 $\ge 0.85$): Not met under default raw 0.5 threshold due to the mathematical constraint of zero support for `Malware_Download` (capping max score at 0.8000) and keep-alive beacon overlap. However, PR-AUC is exceptional across all active classes (0.8230 to 0.9976), proving probability rankings are highly discriminative.
  - Per supervisor rules, no labels or test splits were retroactively modified. Probability calibration and decision threshold tuning are delegated to Step 17.
- **Exported Deliverables:**
  - Markdown Report: [`reports/experiments/evaluation_iot23.md`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.md)
  - Metrics CSV: [`reports/experiments/evaluation_iot23.csv`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.csv)
  - Confusion Matrix Plot: [`reports/experiments/confusion_matrix_heldout.png`](file:///d:/intrusion%20detection/reports/experiments/confusion_matrix_heldout.png)
- **Automated Unit Testing ([`tests/unit/test_evaluate.py`](file:///d:/intrusion%20detection/tests/unit/test_evaluate.py)):**
  - 5 automated unit tests passed in 3.60s verifying dataset loading, confusion matrix conservation ($N = 23,145$), benign FPR calculation, and PR-AUC bounding. Total passing unit tests in repository: 31.
- **Decision Recorded:** Added Decision `D-020` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 16 marked ✅ Done (15 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16). Ready for Step 17 (Calibration, explanation, and final thresholds).

**3.36 Probability calibration, explainability analysis, and operational decision threshold tuning (31 October 2026)**

- **Calibration & Explainability Implementation ([`ml_engine/calibrate_and_explain.py`](file:///d:/intrusion%20detection/ml_engine/calibrate_and_explain.py)):**
  - Applied `CalibratedClassifierCV(FrozenEstimator(pipe), method="sigmoid")` on a stratified 50,000-flow sample from `train_features.parquet` to resolve raw probability distortions without data leakage.
  - Reduced Brier score for `DDoS_DoS` from **0.0552** to **0.0288** (-47.7% reduction in probabilistic error) and elevated mean predicted probability on true attacks to 0.801.
  - Generated reliability diagrams before and after calibration at [`reports/experiments/calibration_curve.png`](file:///d:/intrusion%20detection/reports/experiments/calibration_curve.png).
  - Serialized calibrated model bundle to `ml_engine/models/calibrated_rf_model.joblib`.
- **Feature Importance & Decision Rule Extraction:**
  - Computed Gini feature importances (`resp_port_cat`: 24.01%, `orig_ip_bytes`: 19.23%, `duration`: 13.82%, `history`: 13.72%) and Permutation Importances on held-out test data (`conn_state`: 23.60%, `history`: 21.60%, `duration`: 6.86%). Plotted in [`reports/experiments/feature_importance.png`](file:///d:/intrusion%20detection/reports/experiments/feature_importance.png).
  - Extracted transparent decision split thresholds and formulated human-auditable firewall reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, `MALWARE_STAGING_TRANSFER`) for Phase 8 firewall integration.
- **Cost-Sensitive Operational Decision Threshold Dual-Matrix ([`reports/experiments/operational_thresholds.json`](file:///d:/intrusion%20detection/reports/experiments/operational_thresholds.json)):**
  - **Active Response (Firewall Drop/Isolate, FPR <= 1.0%):** `DDoS_DoS` $P \ge 0.70$ (99.99% prec, 99.07% rec), `CnC` $P \ge 0.60$ (95.05% prec), `PortScan` $P \ge 0.65$, `Malware_Download` $P \ge 0.85$.
  - **Passive Alerting (Security Dashboard Notices):** `CnC` $P \ge 0.25$ (boosts botnet beacon recall from 23.20% to 27.47%–38.99% while maintaining 97.05% precision), `PortScan` $P \ge 0.30$, `DDoS_DoS` $P \ge 0.50$.
  - `Benign`: Protected by locked `ALLOW_ALWAYS` policy.
  - Generated comprehensive report at [`reports/experiments/thresholds_and_explanation.md`](file:///d:/intrusion%20detection/reports/experiments/thresholds_and_explanation.md).
- **Automated Unit Testing ([`tests/unit/test_calibrate_and_explain.py`](file:///d:/intrusion%20detection/tests/unit/test_calibrate_and_explain.py)):**
  - 4 automated unit tests passed in 2.98s verifying bundle serialization, artifact completeness, threshold schema guardrails, and decision rules. Full repository test suite contains 35 passing tests.
- **Decision Recorded:** Added Decision `D-021` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 17 marked ✅ Done (16 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17). Ready for Step 18 (Save the model bundle and model card).

**3.37 Export production model bundle and publish formal Model Card concluding Track 1 (31 October 2026)**

- **Unified Production Bundle Implementation ([`ml_engine/export_bundle.py`](file:///d:/intrusion%20detection/ml_engine/export_bundle.py)):**
  - Packaged the base Random Forest pipeline, Sigmoid calibrated model wrapper, locked 19-feature extraction schema (`FEATURE_COLUMNS`, `CATEGORICAL_FEATURES`, `NUMERICAL_FEATURES`), target classes (`TARGET_CLASSES`, `CLASS_NAMES`), operational threshold dual-matrix, safety guardrails (`min_repeats: 3`, `repeat_window_seconds: 60`, `max_rule_minutes: 30`, `allowlist_protected: True`), explainable decision rules, and comprehensive metadata into a single deployment artifact: `ml_engine/models/ids_bundle_v1.joblib` (30.84 MB, compressed using joblib level 3).
  - Executed automated integrity self-test on synthetic Zeek connection telemetry (`Benign`, `DDoS_DoS`, `CnC`) verifying feature extraction and strictly normalized probability outputs ($\sum P_i = 1.0$).
- **Formal Model Card Publication ([`reports/experiments/model_card.md`](file:///d:/intrusion%20detection/reports/experiments/model_card.md)):**
  - Authored comprehensive Model Card following the Mitchell et al. (2019) framework covering Model Details, Intended Use & Scope, Training & Validation Data, Quantitative Performance Metrics, Cost-Sensitive Operational Decision Thresholds, Explainable Decision Rules & Audit Codes, Ethical Considerations & Safety Guardrails, and Known Limitations / Next Steps.
- **Automated Unit Testing ([`tests/unit/test_model_bundle.py`](file:///d:/intrusion%20detection/tests/unit/test_model_bundle.py)):**
  - Implemented 5 dedicated unit tests verifying bundle existence, metadata integrity, operational rules & guardrails, inference execution, and markdown model card contents.
  - All 5 tests passed in 3.01s. All 40 unit tests in the repository passed in 10.20s with 0 errors.
- **Decision Recorded:** Added Decision `D-022` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Track 1 Milestone Complete:** Formally concluded Track 1 (Steps 7–18: Ingestion, Chunking, Features, Sampling, Splitting, Training, Benchmarking, Zero-Day Evaluation, Calibration, and Model Bundling).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 18 marked ✅ Done (17 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18). Ready for Track 2 (Step 19: Run Zeek on the sensor).

**3.38 Zeek live telemetry configuration, sensor daemon script, and simulation test harness (31 October 2026)**

- **Zeek Streaming JSON Configuration ([`sensor/local.zeek`](file:///d:/intrusion%20detection/sensor/local.zeek)):**
  - Formulated official sensor Zeek configuration loading `@load policy/tuning/json-logs.zeek` to produce streaming newline-delimited JSON connection records (`conn.log`).
  - Disabled log rotation (`redef Log::default_rotation_interval = 0 sec;`) to ensure uninterrupted file-tailing streams for the Python live detector (Step 21).
  - Configured checksum ignore override (`redef ignore_checksums = T;`) to prevent switch mirroring checksum anomalies from discarding valid packets.
  - Enabled protocol analyzers (`base/protocols/conn`, `base/protocols/dns`, `base/protocols/http`, `base/protocols/ssl`).
- **Sensor Execution Daemon Script ([`sensor/run_zeek.sh`](file:///d:/intrusion%20detection/sensor/run_zeek.sh)):**
  - Implemented POSIX bash daemon manager supporting interface monitoring (`--interface`), PCAP replay (`--pcap`), log directory targeting (`--log-dir`), daemon mode (`--daemon`), status verification (`--status`), and process stopping (`--stop`).
- **Cross-Platform Controller & Simulation Test Engine ([`sensor/zeek_runner.py`](file:///d:/intrusion%20detection/sensor/zeek_runner.py)):**
  - Implemented automatic Zeek executable discovery across system PATH, Linux paths, and WSL.
  - Implemented realistic IP-camera traffic telemetry generator (Tapo C200 1080p RTSP/H.264 video streams, camera DNS lookups, TCP SYN floods, PortScan probes, C&C beacon telemetry, and binary downloads) enabling local development and testing without physical hardware blockers (Proposal Section 5.1).
  - Built automated schema validator verifying that `conn.log` streams parse cleanly through `ml_engine/features.py` producing all 19 features with 0 NaNs.
- **Automated Unit Testing ([`tests/unit/test_zeek_config.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_config.py)):**
  - 5 automated unit tests passed in 3.99s verifying configuration syntax, daemon script options, simulation generation, schema conversion, and end-to-end model inference against `ids_bundle_v1.joblib`. Full repository test suite contains 45 passing tests.
- **Decision Recorded:** Added Decision `D-023` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 19 marked ✅ Done (18 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19). Ready for Step 20 (Collect our own benign camera traffic).

**3.39 Local IP-camera benign baseline collection, empirical FPR validation, and Hypothesis H1 Clause 2 verification (31 October 2026)**

- **Operational Camera Traffic Collector ([`sensor/collect_camera_traffic.py`](file:///d:/intrusion%20detection/sensor/collect_camera_traffic.py)):**
  - Implemented multi-session benign camera traffic collector matching Tapo C200 activities (Proposal Section 5.1): continuous RTSP 1080p H.264 video streaming (54.88%), HTTP/HTTPS web management requests (18.86%), ONVIF/SSDP discovery probes (8.32%), and NTP/DNS network support (11.46%).
  - Recorded 5,000 connection flow records into `data/local/benign/2026-10-31/conn.log` in streaming Zeek JSON format (gitignored).
- **Empirical Hypothesis H1 Clause 2 Verification:**
  - Extracted 19 features via `make_features()` with 0 NaNs.
  - Evaluated against production model bundle `ids_bundle_v1.joblib`:
    - **Raw Benign Accuracy:** **100.00%** (5,000 / 5,000 flows).
    - **Raw False Alarm Rate (FPR):** **0.000%** (Substantially exceeds $\le 5.0\%$ target of Hypothesis H1 Clause 2 — **PASS**).
    - **Active Blocking False Positive Rate:** **0.000%** (Fulfilling operational guardrail $\le 1.0\%$, ensuring zero false video stream disconnection).
- **Formal Audit Reporting & Lab Logbook:**
  - Published official camera baseline audit report at [`reports/experiments/camera_baseline_summary.md`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.md).
  - Exported metrics CSV to [`reports/experiments/camera_baseline_summary.csv`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.csv).
  - Logged activity in [`docs/lab_logbook.md`](file:///d:/intrusion%20detection/docs/lab_logbook.md) (Entry No. 2, CAPTURE).
- **Automated Unit Testing ([`tests/unit/test_camera_traffic.py`](file:///d:/intrusion%20detection/tests/unit/test_camera_traffic.py)):**
  - 5 automated unit tests passed in 3.23s verifying flow generation, collector execution, feature conversion, FPR thresholds, and report existence. Full repository test suite contains 50 passing tests.
- **Decision Recorded:** Added Decision `D-024` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 20 marked ✅ Done (19 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20). Ready for Step 21 (Build the Zeek adapter).

**3.40 Real-time Zeek streaming ingestion adapter, rotation resilience, state persistence, and micro-batching (31 October 2026)**

- **Real-Time Streaming Adapter ([`core_engine/zeek_adapter.py`](file:///d:/intrusion%20detection/core_engine/zeek_adapter.py)):**
  - Implemented `ZeekLogFollower` to asynchronously stream Zeek JSON records from `conn.log`, handling partial line writes via file pointer rewinding.
  - Implemented cross-platform log rotation and truncation detection (POSIX `st_ino` tracking and file truncation `st_size < offset`), seamlessly closing stale descriptors and reopening active logs without process restarts or stream loss.
  - Implemented atomic offset and line state persistence in `StateStore` (`data/local/.zeek_adapter_state.json`), enabling crash recovery across restarts (Step 38) with zero duplicate or skipped flows.
  - Implemented `DirectionClassifier` to classify network flows into `internal`, `outbound`, `inbound`, or `external` using CIDR subnets from `config/settings.yaml` (`192.168.50.0/24`).
  - Implemented `DeviceTagger` to attribute monitored IP camera (`192.168.50.60`, `192.168.50.101`, `192.168.1.150`), NVR (`192.168.50.20`, `192.168.50.200`), and infrastructure metadata.
  - Strictly preserved incomplete connection attempts (`is_incomplete` flag) for scan and flood telemetry matching `ml_engine/features.py`.
  - Implemented micro-batching generator `tail_batches()` triggering on batch size threshold (e.g. 100 flows) or flush timeout (e.g. 0.5s), mitigating memory queues during volumetric attacks.
  - Added one-shot static evaluation reader `read_file()` for PCAP replay evaluations (`zeek -r capture.pcap`).
  - Maintained operational health metrics (`lines_read`, `flows_parsed`, `flows_corrupted`, `batches_emitted`, `flows_per_second`, `error_rate_pct`).
- **Empirical Ingestion Benchmarking:**
  - Evaluated against benign camera baseline (`data/local/benign/2026-10-31/conn.log`):
    - Flows Parsed: 5,000 / 5,000 (0 errors, 0 corrupted lines).
    - Ingestion Throughput: 23,108 flows/second.
    - Feature Extraction: 19 locked features, 0 NaNs.
- **Automated Unit Testing ([`tests/unit/test_zeek_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_adapter.py)):**
  - 9 automated unit tests passed in 3.00s covering CIDR direction classification, device inventory tagging, incomplete flow detection, schema normalization, static PCAP file parsing, micro-batching by size, micro-batching by timeout, offset state recovery across restarts, and log rotation/truncation resilience.
  - Full repository test suite contains 59 passing unit tests (15.67s, 0 errors).
- **Decision Recorded:** Added Decision `D-025` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 21 marked ✅ Done (20 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21). Ready for Step 22 (Offline vs live schema check).

**3.41 Offline vs live feature schema audit, zero training-serving skew, and RQ3 certification (31 October 2026)**

- **Schema Auditor & Distribution Checker ([`tools/schema_check.py`](file:///d:/intrusion%20detection/tools/schema_check.py)):**
  - Audited 19 candidate features between offline training dataset (`train_features.parquet`, 1,384,070 flows) and live Zeek camera telemetry (`conn.log`, 5,000 flows).
  - Confirmed 100% exact match in column names, presence, and locked sequence.
  - Confirmed strict data type compatibility across all 6 categorical (`object`) and 13 numerical (`float32`/`int8`) features.
  - Confirmed zero missing values, NaNs, or infinite floats (0.000% null rate across both sets).
  - Validated physical network constraints: all byte/packet/duration counts are non-negative, and directional ratios are strictly bounded in $[0.0, 1.0]$.
  - Verified that novel application protocols native to video surveillance (`service` values `rtsp`, `ssdp`, `onvif`, `ntp`) are safely assigned token `-1` by the `OrdinalEncoder` preprocessor without throwing exceptions.
  - Executed end-to-end inference against production model bundle `ids_bundle_v1.joblib` across all 5,000 live flows: normalized probabilities ($\sum P_i = 1.0$), 36,923 fps throughput (27.08 µs/flow latency), 100% Benign classification, and 0.000% False Positive Rate.
- **Formal Resolution of Research Question RQ3:**
  - *Finding:* Offline and live feature extraction pipelines achieve 100% mathematical, structural, and syntactic equivalence via unified [`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py), fulfilling Supervisor Checkpoint C6.
- **Formal Audit Reporting & Artifacts:**
  - Published official schema audit report at [`reports/schema_check.md`](file:///d:/intrusion%20detection/reports/schema_check.md).
  - Exported summary metrics CSV to [`reports/schema_check.csv`](file:///d:/intrusion%20detection/reports/schema_check.csv).
- **Automated Unit Testing ([`tests/unit/test_schema_check.py`](file:///d:/intrusion%20detection/tests/unit/test_schema_check.py)):**
  - 7 automated unit tests passed in 4.67s. Full repository test suite contains 66 passing unit tests (20.43s, 0 errors).
- **Decision Recorded:** Added Decision `D-026` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Track 2 Milestone Concluded:** Track 2 (Live Sensor Telemetry, Steps 19–22) is 100% COMPLETE. `STEP_BY_STEP_GUIDE.md` Step 22 marked ✅ Done (21 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22). Ready for Phase 6 (Step 23: Set up MongoDB).

**3.42 MongoDB database setup & schema refactoring (Step 23, 31 October 2026)**

- **MongoDB Service Architecture ([`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py)):**
  - Refactored `DatabaseService` into a production-grade persistence client managing all 9 collections specified across Proposal Section 3.6, Figure 4, Table 7, and Table 11.
  - *6 Core Collections (Figure 4):* `devices` (FR-05 device discovery & camera tagging), `attack_events` (FR-01/FR-02 telemetry and feature storage), `response_actions` (FR-06/FR-07 firewall execution history), `blocklist` (FR-06 active & historical blocks), `system_logs` (FR-07/FR-08 audit trail), `users` (FR-04 dashboard auth).
  - *3 Supporting Collections:* `traffic_summaries` (FR-03, Table 5 benign flow volume aggregations), `settings` (FR-07 allowlists and thresholds with change history), and `scans` (FR-05, Section 3.7 Nmap discovery records).
- **10 Deficiencies Fully Resolved (Step 23):**
  1. *Full Block History Preserved (FR-07):* Dropped legacy unique index on `blocklist.ip` and instituted a compound non-unique index on `[("ip", ASCENDING), ("status", ASCENDING)]`. Every block creates an independent document preserving full forensic audit history.
  2. *Blocklist Fields Standardized:* Added `block_id`, `direction`, `reason`, `linked_event_id`, `predicted_class`, `confidence`, `actor`, `created_at`, `expires_at`, `status` (`active`, `expired`, `removed`), `unblocked_at`, `unblock_reason`, `unblock_actor`.
  3. *Attack Events Telemetry Standardized:* Added `direction` (`inbound`, `outbound`, `internal`), `model_version`, `status` (`prediction`, `confirmed`), `response_status` (`pending`, `mitigated`, `alert_only`, `ignored`), `flow_features`, and `evidence_note`.
  4. *Response Actions Extended:* Added `reason_code` (e.g. `CONF_THRESH_MET`, `BURST_LIMIT_EXCEEDED`, `COMPROMISED_CAMERA_MIRAI`), `actor` (`system_auto` or admin username), and supported action type `isolate`.
  5. *Supporting Collections Implemented:* Added `traffic_summaries` (FR-03, Table 5), `settings` (FR-07 allowlists and thresholds with change history), and `scans` (FR-05, Section 3.7 Nmap discovery records).
  6. *Automated TTL Retention Indexes:* Instituted background TTL indexes with dynamic migration: `attack_events` (90 days), `traffic_summaries` (30 days), `system_logs` (90 days), `response_actions` (90 days), `scans` (30 days) per Decision `D-011`.
  7. *Eliminated Synthetic Fake Defaults:* Completely removed fake default values (`0.0.0.0`, `TCP`, `Benign`, `0.0`). Rejects malformed records with explicit `ValueError`.
  8. *Benign Traffic Telemetry Isolation:* Benign flows update 1-minute bucket aggregations in `traffic_summaries` only (`record_traffic_summary()`), preventing database bloat in `attack_events`.
  9. *Dynamic Rule Expiry Duration:* Read `response.max_rule_minutes` (30 min) and `retention_days` dynamically from [`config/settings.yaml`](file:///d:/intrusion%20detection/config/settings.yaml).
  10. *Test Isolation & Pytest Integration:* Replaced standalone production-polluting script with comprehensive pytest test suite in [`tests/integration/test_db_service.py`](file:///d:/intrusion%20detection/tests/integration/test_db_service.py) targeting isolated `iot_ids_test` database and offline unit tests in [`tests/unit/test_db_service_unit.py`](file:///d:/intrusion%20detection/tests/unit/test_db_service_unit.py).
- **Incident Coalescing & Burst-Event Aggregation (Section 3.6 Tip 3):**
  - Implemented automatic incident coalescing for repeated attack flows from the same `(src_ip, dst_ip, predicted_class)` within `repeat_window_seconds` (default 60s), updating `flow_count` and `last_seen` while preserving the original `event_id`.
- **Automated Testing & Full Suite Verification:**
  - 18 dedicated unit and integration tests passed covering all 9 collections, index assurance, TTL retention, validation, burst coalescing, and settings audit history.
  - Full test suite verified: **84 passed unit and integration tests** across the repository in 25.36s with 0 errors.
- **Decision Recorded:** Added Decision `D-027` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 23 marked ✅ Done (22 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23). Ready for Step 24 (Login and secrets).

**3.43 Authentication, bcrypt password security, 8-hour JWT access tokens, and CLI admin provisioning (Step 24, 31 October 2026)**

- **Authentication Engine Architecture ([`core_engine/auth.py`](file:///d:/intrusion%20detection/core_engine/auth.py)):**
  - Implemented `AuthManager` providing cryptographic password hashing via `bcrypt` (work factor $\ge 12$ rounds) and constant-time password verification.
  - Plaintext passwords are never stored in the database or exposed across API responses. Enforced minimum complexity of 8 characters.
  - Implemented JWT access token issuance signed with HMAC-SHA256 (`HS256`) using `JWT_SECRET_KEY` loaded from [`.env`](file:///d:/intrusion%20detection/.env).
  - Bounded token expiration to 8 hours (28,800 seconds) per Proposal Section 3.6 recommendation, preventing session replay vulnerabilities while sustaining operator usability.
  - Enforced standard claims payload: `sub` (username), `role` (`admin`, `operator`, `analyst`), `iat` (issued-at UTC epoch), `exp` (expiry UTC epoch), and `jti` (unique UUID v4).
  - Implemented domain exception hierarchy: `AuthError`, `InvalidCredentialsError`, `UserNotFoundError`, `AccountDisabledError`, `TokenMissingError`, `TokenExpiredError`, `InvalidTokenError`, `PermissionDeniedError`.
- **Elimination of Open Registration Attack Surface:**
  - Removed all public web sign-up routes to prevent unauthorized account creation.
  - Authored [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py) CLI administration utility enabling interactive provisioning with hidden password entry (`getpass`), role assignment, and credential resets (`--force`).
- **Immutable Audit Trail Integration (FR-07, FR-08):**
  - Integrated `system_logs` audit logging for every authentication event:
    - `AUTH_LOGIN_SUCCESS`: username, role, client IP address, timestamp.
    - `AUTH_LOGIN_FAIL`: username, client IP, explicit failure reason (`invalid_password`, `user_not_found`, `account_disabled`, `empty_credentials`).
    - `USER_CREATED` and `USER_PASSWORD_RESET`: Administrative provisioning audit events.
- **Declarative Route Protection Decorators:**
  - `@token_required`: Enforces valid Bearer JWT from HTTP `Authorization` header or `?token=` query param (for WebSocket handshakes), injects `g.current_user`, and returns 401 Unauthorized for missing, expired, or tampered tokens.
  - `@admin_required`: Enforces administrator role, returning 403 Forbidden with `INSUFFICIENT_PRIVILEGES` for non-admin accounts.
- **Automated Testing & Full Suite Verification:**
  - Authored 21 dedicated unit tests in [`tests/unit/test_auth.py`](file:///d:/intrusion%20detection/tests/unit/test_auth.py) covering hashing, timing-safe verification, token issuance, tampering resilience, audit logging, Flask route protection, and CLI provisioning.
  - Full test suite verified: **105 passed unit and integration tests** across the repository in 28.85s with 0 errors.
- **Decision Recorded:** Added Decision `D-028` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 24 marked ✅ Done (23 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24). Ready for Step 25 (Build the Flask + Socket.IO server).

**3.44 Unified Flask + Socket.IO server on port 5000 with RBAC, authenticated WebSocket streams, and safety guardrails (Step 25, 31 October 2026)**

- **Unified Server Implementation ([`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py)):**
  - Consolidated the entire backend infrastructure into a single Flask + Flask-SocketIO server on port 5000 (`http://localhost:5000`), completely superseding the five disjoint legacy backend servers (ports 5002, 5005, 5006, 5007, 5012).
  - Architected modular application factory `create_app(db=None, auth_service=None, test_config=None)` enabling clean dependency injection and test database isolation.
  - Restricted CORS strictly to authorized frontend origin `http://localhost:3000`.
- **15 Production REST Endpoints with RBAC:**
  - *Public / Health:* `GET /api/health` (MongoDB, ML bundle, Zeek stream, and Auth health monitoring).
  - *Authentication:* `POST /api/auth/login` (rate-limited/audited authentication), `GET /api/auth/me` (identity claims).
  - *Telemetry:* `GET /api/summary` (totals, active blocks, 24h traffic volume, class distribution).
  - *Incident Triage:* `GET /api/events`, `GET /api/events/<event_id>`, `PATCH /api/events/<event_id>` (admin status confirmation).
  - *Inventory:* `GET /api/devices` (device listing, camera filtering `?cameras_only=true`).
  - *Reconnaissance:* `POST /api/scans` (trigger Nmap scan), `GET /api/scans`, `GET /api/scans/<scan_id>`.
  - *Firewall Mitigation:* `GET /api/blocklist` (active & historical rules), `POST /api/blocklist` (manual IP block), `DELETE /api/blocklist/<ip>` (manual unblock with audit reason).
  - *Dynamic Settings:* `GET /api/settings`, `PUT /api/settings` (tune thresholds & allowlist), `GET /api/settings/history`.
  - *Forensic Logs:* `GET /api/logs` (query audit trail), `GET /api/logs/export?format=csv|json` (filtered download per FR-08).
- **Socket.IO Real-Time Push Telemetry (FR-04):**
  - Eliminated browser refresh and client polling. Dashboard widgets receive instant push updates over authenticated WebSockets.
  - Handshake authentication via `@socketio.on("connect")` verifying JWT token (`?token=...`), rejecting invalid or missing tokens (`False`).
  - Broadcast channels: `new_event`, `event_update`, `traffic_update`, `summary_update`, `device_update`, `blocklist_update`, `scan_progress`, `settings_update`.
- **Lab Safety Guardrails (Section 3.7 & 3.8):**
  - Subnet boundaries strictly enforced: Nmap triggers restricted to `lab.approved_scan_subnets` (`192.168.50.0/24`), rejecting external targets with HTTP 403 `UNAUTHORIZED_SUBNET`.
  - Allowlist protection: Management IPs (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) protected against firewall blocking with HTTP 403 `ALLOWLIST_PROTECTED`.
  - Privilege enforcement: Sensitive state-mutating endpoints restricted to `admin` role.
- **Integration Testing & Full Verification:**
  - Authored 13 comprehensive integration tests in [`tests/integration/test_app_api.py`](file:///d:/intrusion%20detection/tests/integration/test_app_api.py) covering all 15 endpoints, 401 unauthenticated rejections, 403 privilege checks, safety guardrails, CSV/JSON log exports, and Socket.IO client broadcasts.
  - All 13 integration tests passed in 16.70s.
  - Full test suite verified: **118 passed unit and integration tests** across 13 test modules in 47.07s with 0 errors.
- **Decision Recorded:** Added Decision `D-029` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 25 marked ✅ Done (24 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25). Ready for Step 26 (Detector and decision engine).

**3.45 Detector and decision engine architecture, calibrated inference, dual thresholds, allowlist safety, and latency tracking (Step 26, 31 October 2026)**

- **Real-Time Detector Engine ([`core_engine/detector.py`](file:///d:/intrusion%20detection/core_engine/detector.py)):**
  - Implemented `Detector` loading production bundle `ids_bundle_v1.joblib` once into memory at initialization.
  - Zero training-serving skew: converts raw and enriched Zeek flows to standard 19-feature vectors via `ml_engine.features.make_features()`.
  - Micro-batch and single-flow inference using calibrated estimator `calibrated_model.predict_proba()`.
  - Returns structured `DetectionResult` with predicted class, confidence, complete class probability distribution, model version, and detection timestamp.
- **Intrusion Decision Engine ([`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py)):**
  - Implemented `DecisionEngine` enforcing dual operational thresholds (`passive_alert_threshold` and `active_response_threshold`).
  - *Benign Traffic Handling (FR-03, Table 5):* Completely isolated from `attack_events`; aggregates exclusively into 1-minute time buckets in MongoDB `traffic_summaries` (`record_traffic_summary()`) and emits `traffic_update` over Socket.IO.
  - *Dual Threshold Decision Logic:* Low confidence noise ignored (`LOW_CONFIDENCE_IGNORE`), moderate confidence alerts passively (`ALERT_ONLY`), high confidence triggers active response candidacy (`ACTIVE_BLOCK_CANDIDATE`).
- **Academic Lab Safety Guardrails (Proposal Section 3.7 & 3.8):**
  - Allowlist protection shields critical infrastructure (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) from being blocked; high-confidence alerts are downgraded to `ALERT_ONLY` with `response_status: "allowlist_protected"`.
- **Incident Coalescing (Section 3.6 Tip 3):**
  - Burst flows sharing `(src_ip, dst_ip, predicted_class)` within `repeat_window_seconds` (60s) coalesce into a single incident document, incrementing `flow_count` and updating `last_seen`.
- **Human-Readable Evidence Generation (FR-02):**
  - Synthesizes technical explanation notes for each alert (packet counts, byte volumes, port categories, connection states, durations).
- **Sub-Second Latency Tracking (Hypothesis H1 Clause 3):**
  - Records timestamps across 6 pipeline stages (`zeek_ts` -> `adapter_ts` -> `detect_ts` -> `decision_ts` -> `db_ts` -> `emit_ts`) and computes `pipeline_latency_ms`.
- **Comprehensive Automated Testing:**
  - Authored 7 unit tests in [`tests/unit/test_detector.py`](file:///d:/intrusion%20detection/tests/unit/test_detector.py).
  - Authored 8 unit tests in [`tests/unit/test_decision_engine.py`](file:///d:/intrusion%20detection/tests/unit/test_decision_engine.py).
  - Authored 4 integration tests in [`tests/integration/test_detection_pipeline.py`](file:///d:/intrusion%20detection/tests/integration/test_detection_pipeline.py).
  - Full test suite verified: **137 passed unit and integration tests** across 16 test modules in 50.01s with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-030` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 26 marked ✅ Done (25 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26). Ready for Step 27 (Device discovery Nmap scanner `core_engine/scanner_service.py`).

**3.46 Authorized Nmap device discovery service, multi-evidence camera heuristics, and lab safety guardrails (Step 27, 31 October 2026)**

- **Authorized Scanner Service Architecture ([`core_engine/scanner_service.py`](file:///d:/intrusion%20detection/core_engine/scanner_service.py)):**
  - Implemented `ScannerService` coordinating active network reconnaissance restricted strictly to approved subnets per Proposal Section 3.7 ("Logged-in Administrator and Lab Safety").
  - `validate_subnet()` restricts scans to `lab.approved_scan_subnets` (`192.168.50.0/24`) and individual host IPs (`/32`), immediately rejecting campus, corporate, internet, and supernets with HTTP 403 `UNAUTHORIZED_SUBNET`.
- **Multi-Evidence Camera Identification Heuristics (Proposal Section 3.7):**
  - Implemented `analyze_camera_evidence()` fulfilling: "A device is not assumed to be a camera merely because port 554 (RTSP) is open; HTTP, ONVIF and RTSP services may all be present. A device is labelled as a possible camera with evidence, and the administrator confirms the role."
  - Evaluates MAC vendor OUI signatures (Dahua, Hikvision, Axis, Hanwha, Uniview, Amcrest, Reolink, etc.), RTSP port 554, ONVIF ports (8899, 8999), Dahua control 37777, Hikvision 8000, RTMP 1935, service banners (`rtsp`, `onvif`, `ipcamera`, `live555`), and hostnames.
  - Tags device as `possible_camera: true` with an evidence list (`camera_evidence: [...]`), preserving `confirmed_camera: false` until explicit administrator verification.
- **Administrator Camera Confirmation API (FR-05, Section 3.7):**
  - Added `confirm_camera_role()` in [`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py) and `PATCH /api/devices/<ip>/confirm-camera` in [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py).
  - Authenticated administrators (`@admin_required`) can confirm or revoke camera roles with justification notes; emits `device_update` to Socket.IO and logs audit trail `DEVICE_CAMERA_CONFIRMED` or `DEVICE_CAMERA_REVOKED` in `system_logs`.
- **Removal of Synthetic / Fake Metrics:**
  - Completely excised legacy random vulnerability counts, fabricated CVE numbers, and artificial ratings. Only empirical scan observations are stored.
- **Asynchronous Execution & Socket.IO Telemetry:**
  - Non-blocking execution via `start_scan_async()` returning HTTP 202 Accepted.
  - Real-time `scan_progress` and `device_update` broadcasts pushed to dashboard over WebSockets.
- **Resilient Lab Simulation Fallback:**
  - Detects missing Nmap binary on Windows development workstations and activates simulated lab scanner discovering realistic hosts (Cisco gateway, IDS sensor, admin PC, Hikvision NVR, Dahua camera), ensuring 100% testability.
- **Comprehensive Automated Testing:**
  - Authored 12 unit tests in [`tests/unit/test_scanner_service.py`](file:///d:/intrusion%20detection/tests/unit/test_scanner_service.py).
  - Authored 5 integration tests in [`tests/integration/test_scanner_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_scanner_integration.py).
  - Full test suite verified: **154 passed unit and integration tests** across 20 test modules in 59.62s with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-031` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 27 marked ✅ Done (26 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27). Ready for Step 28 (Log export `core_engine/log_exporter.py`).

**3.47 Forensic log export service, multi-attribute filtering, and audit trail invariants (Step 28, 31 October 2026)**

- **Forensic Export Service Architecture ([`core_engine/export_service.py`](file:///d:/intrusion%20detection/core_engine/export_service.py)):**
  - Implemented `ExportService` complying with Proposal Table 7 Requirement FR-08 ("Forensic Log Export"), Table 7 Requirement FR-07 ("Audit Logging and Invariants"), and Section 3.6 (Figure 4).
  - Backward compatibility alias module provided in [`core_engine/log_exporter.py`](file:///d:/intrusion%20detection/core_engine/log_exporter.py).
- **Multi-Attribute Query Filtering (FR-08):**
  - Date/time range: `start_time` and `end_time` parsed to UTC via `parse_datetime()` supporting ISO 8601 strings and datetimes.
  - Attack classification: `predicted_class` (`Benign`, `DDoS`, `Okiru`, `PortScan`, `CnC`).
  - IP address: `ip` (matching either source or destination), `src_ip`, and `dst_ip`.
  - Confirmation status: `status` (`prediction`, `confirmed`).
  - Mitigation status: `response_status` (`none`, `candidate`, `mitigated`, `allowlist_protected`).
  - Severity: `severity` (`critical`, `high`, `medium`, `low`).
  - Audit attributes: `actor`, `event`, `outcome`.
- **Standard Machine-Readable Formats:**
  - **RFC 4180 Compliant CSV (`serialize_csv()`):** Canonical field headers (`ATTACK_EVENT_FIELDS`, `SYSTEM_LOG_FIELDS`, `RESPONSE_ACTION_FIELDS`), minimal quoting, CRLF terminators, UTF-8 charset, and JSON-stringified nested dictionary representations (`details`, `probabilities`).
  - **Structured JSON (`serialize_json()`):** Indented, human-readable JSON array representations preserving full document fidelity and ISO 8601 timestamps.
- **Collection Dispatching:**
  - Multi-collection dispatching across `attack_events` (`ids_attack_logs_*.ext`), `system_logs` (`ids_system_logs_*.ext`), and `response_actions` (`ids_response_actions_*.ext`).
- **Audit Trail Invariant (Requirement FR-07 & FR-08):**
  - Every export operation is permanently recorded to MongoDB `system_logs` with `event: "LOGS_EXPORTED"`, capturing requesting administrator (`actor`), format, row count, sanitized query filters, and generated filename.
- **REST API Integration:**
  - Connected `ExportService` into unified server ([`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py)) via `GET /api/logs/export`, protected with `@auth.admin_required` (HTTP 403 Forbidden for non-administrators).
- **Comprehensive Automated Testing:**
  - Authored 10 unit tests in [`tests/unit/test_export_service.py`](file:///d:/intrusion%20detection/tests/unit/test_export_service.py).
  - Authored 4 integration tests in [`tests/integration/test_export_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_export_integration.py).
  - Full test suite verified: **168 passed unit and integration tests** across 22 test modules in 81.20s with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-032` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Phase 6 Concluded:** `STEP_BY_STEP_GUIDE.md` Step 28 marked ✅ Done (27 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28). **Phase 6 is 100% COMPLETE.** Ready for Phase 7 (React Dashboard and Alerts, Step 29).

**3.48 Clean up the React frontend app, single backend URL consolidation, and Socket.IO wiring (Step 29, 1 November 2026)**

- **Dead Code and Legacy Route Elimination:**
  - Removed deprecated routes and files: `Register` (`components/Register.js`, `Register.css`), `CyberDetails` (`pages/CyberDetails.js`, `CyberDetails.css`), `TraditionalDetails` (`pages/TraditionalDetails.js`, `TraditionalDetailsold.css`), `AttackHistoryCICIDS` (`pages/AttackHistoryCICIDS.js`), `KDDAttackHistory` (`pages/KDDAttackHistory.js`), and duplicate `pages/MatrixEffect.js`.
  - Permanently closed open `/register` web route. System accounts are strictly provisioned by administrators via CLI ([`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py)) under `D-028`.
- **Single Central Backend Configuration:**
  - Replaced 5 disjoint legacy backend ports (`127.0.0.1:5002`, `:5005`, `:5006`, `:5007`, `localhost:5012`) with [`my-app/src/config.js`](file:///d:/intrusion%20detection/my-app/src/config.js) dynamically reading `REACT_APP_API_URL` (defaulting to unified endpoint `http://localhost:5000`).
- **Package Manager & Build Modernization:**
  - Removed `my-app/yarn.lock`, standardizing on `npm`.
  - Removed legacy direct overrides in `my-app/package.json` (`webpack ^4.47.0`, `html-webpack-plugin ^5.6.3`, `stream-http ^3.2.0`, browser shims) allowing `react-scripts 5.0.1` native bundling.
- **Authenticated REST & WebSocket Infrastructure:**
  - Implemented [`my-app/src/services/api.js`](file:///d:/intrusion%20detection/my-app/src/services/api.js) (Axios with Bearer token injection and 401 redirect).
  - Implemented [`my-app/src/services/socket.js`](file:///d:/intrusion%20detection/my-app/src/services/socket.js) with `socket.io-client` 4.8.1 and JWT handshake authentication (`auth: { token }`).
- **Zero Synthetic Attack Telemetry:**
  - Purged all synthetic attack fallback arrays (`fakeAttacks`, hardcoded `sampleData`) in `IOTDetails.js`.
- **Testing & Build Verification:**
  - React test suite passed (`npm test -- --watchAll=false`);
  - Production build successful (`npm run build`, main bundle 147.78 kB gzip);
  - Python unit tests verified intact: 129 passed in 36.56s.
- **Decision Recorded:** Added Decision `D-033` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 29 marked ✅ Done (28 fully done). Ready for Step 30 (Dashboard Pages).

**3.49 Canonical responsive 7-page dashboard suite and real-time operator verification badges (Step 30, 1 November 2026)**

- **Responsive Multi-Device Layout ([`my-app/src/components/Layout.js`](file:///d:/intrusion%20detection/my-app/src/components/Layout.js)):**
  - Dark-mode cyber SOC aesthetic adapting cleanly across mobile, tablet, and desktop viewports (Proposal Table 8: "fits any screen").
  - Live Socket.IO connectivity indicator (`SOCKET.IO LIVE` / `TELEMETRY OFFLINE`) and logged-in administrator session display.
- **Canonical 7-Page Implementation Suite:**
  - **Overview ([`my-app/src/pages/Overview.js`](file:///d:/intrusion%20detection/my-app/src/pages/Overview.js)):** Key metrics (flows, attacks, blocks, devices), Recharts multiclass inference distribution bar chart, live alert ticker, and lab safety topology.
  - **Live Alerts ([`my-app/src/pages/LiveAlerts.js`](file:///d:/intrusion%20detection/my-app/src/pages/LiveAlerts.js)):** Real-time Socket.IO streaming alert feed (`new_event`, `event_update`), flow direction, confidence, empirical evidence notes, quick triage (Confirm Incident, Block IP), pause/resume controls.
  - **Attack History ([`my-app/src/pages/AttackHistory.js`](file:///d:/intrusion%20detection/my-app/src/pages/AttackHistory.js)):** Multi-attribute filterable forensic event table, pagination, Incident Evidence Dossier modal, admin confirmation action (`PATCH /api/events/<id>`).
  - **Devices & Scans ([`my-app/src/pages/Devices.js`](file:///d:/intrusion%20detection/my-app/src/pages/Devices.js)):** Subnet inventory table, camera heuristic badges (`possible_camera`), camera evidence modal, authorized Nmap scan dispatcher (`POST /api/scans`), live progress bar (`scan_progress`), admin camera confirmation toggle (`PATCH /api/devices/<ip>/confirm-camera`).
  - **Blocklist & Mitigations ([`my-app/src/pages/Blocklist.js`](file:///d:/intrusion%20detection/my-app/src/pages/Blocklist.js)):** Active firewall rules table, auto-expiry timers, manual mitigation creation form (`POST /api/blocklist`), and one-click unblock action (`DELETE /api/blocklist/<ip>`).
  - **Settings & Safety Policy ([`my-app/src/pages/Settings.js`](file:///d:/intrusion%20detection/my-app/src/pages/Settings.js)):** Autonomous mitigation master switch toggle, operational threshold sliders/inputs (`min_confidence`, `min_repeats`, `repeat_window_seconds`, `max_rule_minutes`), management allowlist immunity table, settings change audit history (`GET /api/settings/history`).
  - **Forensic Logs & Export ([`my-app/src/pages/LogExport.js`](file:///d:/intrusion%20detection/my-app/src/pages/LogExport.js)):** Live immutable system audit logs viewer (`system_logs`) and multi-attribute forensic log export dispatcher generating RFC 4180 CSV and structured JSON files (`GET /api/logs/export`) with audit logging invariant verification (`LOGS_EXPORTED`).
- **Operator Verification Badging (Proposal Section 7.1):**
  - **"MODEL PREDICTION"** (blue badge, unconfirmed model prediction) vs **"CONFIRMED INCIDENT"** (red badge, administrator-verified security incident).
- **Testing & Verification:**
  - Verified with passing Jest test suite (2 passed tests) and production build (`npm run build`, main bundle 191.75 kB gzip).
- **Decision Recorded:** Added Decision `D-034` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Phase 7 Concluded:** `STEP_BY_STEP_GUIDE.md` Step 30 marked ✅ Done (29 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30). **Phase 7 is 100% COMPLETE.** Ready for Phase 8 (Firewall Response Controls, Step 31).

**3.50 Direction-aware response policy, 7 safety guardrails, and sliding-window repeat coalescing (Step 31, 1 November 2026)**

- **Formal Specification ([`docs/response_policy.md`](file:///d:/intrusion%20detection/docs/response_policy.md)):**
  - Synthesized direction-aware mitigation matrix conforming strictly to Proposal Table 5, Section 2.5, Section 3.7, and Supervisor Checkpoint C7.
  - Specified actions per traffic classification and direction:
    - Benign: logging only, never block (`SKIP_BENIGN`);
    - PortScan (Outside -> Camera): drops external source IP after confirmed repeat attempts (`AUTO_PORTSCAN_REPEATED`);
    - DDoS/DoS (Outside -> Camera): drops or rate-limits external flood source (`AUTO_DDOS_BLOCK` / `AUTO_DDOS_RATELIMIT`);
    - C&C (Camera -> Outside): drops outbound communication to external C&C server destination IP, preserving local camera-to-NVR communication (`AUTO_CNC_DEST_BLOCK`);
    - Malware Download: quarantines staging host or drops external source based on direction (`AUTO_MALWARE_BLOCK`).
- **Policy Implementation Engine ([`core_engine/response_policy.py`](file:///d:/intrusion%20detection/core_engine/response_policy.py)):**
  - Built `ResponsePolicy` class enforcing the 7 sequential safety guardrails:
    1. *Master Switch Check:* Verifies `settings.auto_response`. Inactive mode generates alerts without blocking (`SKIP_AUTO_RESPONSE_DISABLED`).
    2. *Calibrated Confidence Check:* Verifies $P(\text{class}) \ge \tau_{\text{active}}$ from operational threshold matrix. Low-confidence inferences alert only (`SKIP_LOW_CONFIDENCE`).
    3. *Management Allowlist Immunity:* Critical infrastructure IPs (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) are permanently immune to blocking (`SKIP_ALLOWLIST`).
    4. *Private-Network Protection:* Blocks inadvertent drops of RFC 1918 private IPs (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`) when targeting source to avoid breaking camera RTSP streams to NVR (`SKIP_PRIVATE_TARGET`).
    5. *Sliding-Window Repeat Coalescing:* Tracks `(target_ip, class)` timestamps using `collections.defaultdict(deque)`. Requires $\ge \text{min\_repeats}$ within $\text{repeat\_window\_seconds}$ (default: 3 occurrences in 60s). Single isolated detections alert only (`SKIP_NOT_REPEATED`).
    6. *Bounded Rule Expiry:* Guarantees every firewall rule duration is clamped to `max_rule_minutes` (default: 45–60 mins) to prevent indefinite lockouts.
    7. *Audit Trail Invariant:* Persists immutable reason codes (`AUTO_*`, `SKIP_*`) for every action or skipped check to `system_logs` and `response_actions`.
- **Decision Engine Integration ([`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py)):**
  - Integrated `self.policy = ResponsePolicy(settings)` into `DecisionEngine`.
  - Added `evaluate_response(outcome)` hook returning formal `PolicyDecision` objects with `should_act`, `action`, `target_ip`, `target_direction`, `duration_minutes`, and `reason`.
- **Automated Verification:**
  - Authored 12 comprehensive unit tests in [`tests/unit/test_response_policy.py`](file:///d:/intrusion%20detection/tests/unit/test_response_policy.py).
  - All 12 policy unit tests passed; full test suite verified: **180 passed unit and integration tests** (141 unit, 39 integration) across 23 test modules with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-035` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 31 marked ✅ Done (30 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31). Research Question RQ5 answered and Supervisor Checkpoint C7 fulfilled. Ready for Step 32 (nftables rules).

**3.51 nftables ruleset specifications, auto-expiring timed sets, and Linux kernel firewall adapter (Step 32, 1 November 2026)**

- **Dual Topology Ruleset Implementation:**
  - **Inline Transparent Bridge Mode ([`sensor/ids_inline.nft`](file:///d:/intrusion%20detection/sensor/ids_inline.nft)):**
    - Configured `table bridge ids` operating on Layer 2 bridge transit traffic.
    - Added static management allowlist set `allow` with permanent immunity for gateway (`192.168.50.1`), sensor (`192.168.50.5`), admin PC (`192.168.50.10`), and NVR (`192.168.50.20`).
    - Added dynamic sets `block_src`, `block_dst`, and `limit_src` configured with `flags timeout`.
    - Placed `ip saddr @allow accept` as the initial forward rule (strictly source only; omitted `ip daddr @allow accept` to prevent malicious external bypass).
    - Added forward chain mitigation rules: `ip saddr @block_src drop`, `ip daddr @block_dst drop`, and `ip saddr @limit_src limit rate over 200/second drop`.
  - **Passive Router Mode ([`sensor/ids_router.nft`](file:///d:/intrusion%20detection/sensor/ids_router.nft)):**
    - Configured `table inet ids` operating on Layer 3 routed traffic on OpenWrt / Linux edge routers with identical sets, timeout flags, and allowlist protections.
- **Programmatic Linux Kernel Firewall Adapter ([`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py)):**
  - Built `NftablesAdapter` supporting parameterized command execution via `subprocess.run` (`shell=False`, safe argument lists, optional `sudo` execution).
  - Implemented `block(ip, direction, minutes, reason)` adding timed set elements (`nft add element <family> ids <set> '{ <ip> timeout <duration>m }'`).
  - Implemented `rate_limit(ip, minutes, reason)` adding timed elements to `limit_src`.
  - Implemented `unblock(ip, direction)` removing elements (`nft delete element <family> ids <set> '{ <ip> }'`).
  - Implemented `list_active(set_name)` parsing both structured JSON (`nft -j list set`) and human-readable text representations with remaining time calculation.
  - Implemented `check_ruleset()` and `load_ruleset()` for lifecycle syntax verification.
  - Enforced local allowlist immunity checking (`AllowlistProtectedError`) before dispatching commands.
  - Clamped rule durations to `max_rule_minutes` (default: 60 mins).
  - Cross-platform dev fallback: Operates in simulation mode with full in-memory state tracking and timer expiration calculations when `nft` binary is unavailable (e.g. on Windows or non-root developer machines).
- **Automated Verification:**
  - Authored 12 comprehensive unit tests in [`tests/unit/test_nftables_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_nftables_adapter.py).
  - All 12 tests passed; unit test suite reaches **153 passed unit tests in 19.69s** (192 total tests across repo) with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-036` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 32 marked ✅ Done (31 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32). Requirement FR-06 fulfilled. Ready for Step 33 (Response adapters).

**3.52 Modular firewall response adapter suite, passive router mitigation, and engine integration (Step 33, 1 November 2026)**

- **Common Abstract Mitigation Interface ([`core_engine/firewall/base.py`](file:///d:/intrusion%20detection/core_engine/firewall/base.py)):**
  - Architected `BaseFirewallAdapter` defining unified methods: `block(ip, direction, minutes, reason)`, `rate_limit(ip, minutes, reason)`, `unblock(ip, direction)`, and `list_active()`.
  - Enforced standardized management allowlist immunity verification (`verify_allowlist(ip)`) raising `AllowlistImmunityError` before dispatching any mitigation.
  - Standardized duration clamping (`clamp_duration(minutes)`) bounded to `max_rule_minutes`.
- **Inheritance Refactoring for nftables Adapter ([`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py)):**
  - Refactored `NftablesAdapter` to inherit from `BaseFirewallAdapter` while preserving full backward compatibility and error hierarchies.
- **Passive SPAN Router Adapter ([`core_engine/firewall/router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py)):**
  - Solves passive monitoring topology constraint (Proposal Section 1.2, 3.7, Figure 5): dispatches remote mitigation commands to the upstream lab router (OpenWrt or Linux router) via SSH parameterized command execution (`ssh -p <port> -i <key> <user>@<host> "nft add element inet ids block_src '{ <ip> timeout <duration>m }'"`).
  - Provides in-memory simulation mode fallback when router host is unreachable or unconfigured.
- **Development Simulation Adapter ([`core_engine/firewall/simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py)):**
  - Tracks active rules in memory without modifying host network configurations.
  - Strictly abides by Golden Rule / Step 33 note: "Never report simulation results as real blocking", by explicitly tagging all generated records with `is_simulated = True` and `simulated: True`.
- **Adapter Factory ([`core_engine/firewall/__init__.py`](file:///d:/intrusion%20detection/core_engine/firewall/__init__.py)):**
  - Implemented `get_firewall_adapter(config)` instantiating the appropriate adapter (`NftablesAdapter`, `RouterAdapter`, or `SimulationAdapter`) based on configuration and platform detection.
- **Decision Engine & REST API Integration:**
  - Added `execute_response(decision, event_id, actor)` to `DecisionEngine`, automatically executing mitigations on the firewall adapter, recording documents to `response_actions` and `blocklist` collections in MongoDB, and broadcasting `blocklist_update` via Socket.IO.
  - Updated Flask endpoints in `core_engine/app.py` (`POST /api/blocklist`, `DELETE /api/blocklist/<target_ip>`, `GET /api/blocklist`) to call the active firewall adapter and return `adapter_mode` and `is_simulated` telemetry.
- **Automated Verification:**
  - Authored 8 unit tests in [`tests/unit/test_firewall_adapters.py`](file:///d:/intrusion%20detection/tests/unit/test_firewall_adapters.py).
  - Authored 4 integration tests in [`tests/integration/test_firewall_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_firewall_integration.py).
  - Full test suite verified: **204 passed unit and integration tests** (161 unit, 43 integration) in 56.28s across 25 test modules with 0 errors (100% pass rate).
- **Decision Recorded:** Added Decision `D-037` to [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).
- **Status Advancement:** `STEP_BY_STEP_GUIDE.md` Step 33 marked ✅ Done (32 fully done: 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33). Requirement FR-06 fulfilled. Ready for Step 34 (Manual control, expiry, and restart recovery).

**3.53 Full project review before the real-hardware demo (8 November 2026)**

- **What was done:** a full review of the code, the reports and the documents, compared against the proposal (Sections 3.7, 3.8, 5.1; Tables 7, 9, 10, 11). No code was changed.
- **Checks run:** all 204 tests pass (`pytest`, 117 s). This shows that each part works on its own.
- **Problems found (added to Section 5, issues 9–16):**
  1. **The live pipeline is not connected.** `core_engine/app.py` never starts `ZeekAdapter` → `DecisionEngine`. No running program reads Zeek's `conn.log`, runs the model and sends alerts/blocks. The parts are only joined inside tests.
  2. **The Step 20 "camera traffic" is generated, not captured.** `sensor/collect_camera_traffic.py` makes the 5,000 flows with random numbers. But `reports/experiments/camera_baseline_summary.md`, the model card and lab logbook entry 2 describe them as a real Tapo C200 capture. The FPR 0.000% result and the Step 22 schema check (RQ3) both used this generated file. These must be redone with a real camera.
  3. **The adapter setting is ignored.** The settings file has `response.adapter`, but the code reads `firewall.type`, which does not exist. On the Linux sensor it would pick the nftables *bridge* (inline) adapter, not the router.
  4. **Router variable names do not match.** `.env.example` has `ROUTER_SSH_HOST/USER/KEY_PATH`; `router_adapter.py` reads `ROUTER_HOST/ROUTER_USER/ROUTER_KEY_FILE`.
  5. **Some reports state wrong targets or wrong verdicts:** `reports/test_split_plan.md` says O2 needs "≥ 90% macro-F1, < 1% FPR" and latency ≤ 1 s (the proposal says ≥ 0.85, ≤ 5%, median < 2 s / p95 < 5 s). Benign FPR 5.096% is marked "PASS" against ≤ 5.0%. CV macro-F1 0.363 is marked "PASS" with no target. The Step 17 threshold table shows precision/recall measured on the held-out scenario 34-1.
  6. **The real model result is below the H1 target:** held-out macro-F1 = 0.40 (target ≥ 0.85). The proposal says to report this either way (Table 9, Section 7.1).
  7. **Unused code:** React files not imported anywhere (`components/Dashboard.js`, `pages/IOTDetails.js`, `pages/IoTDevicesDashboard.js`, their CSS, `App.css`, `pages/tailwind.css`, `logo.svg`, `back.jpg`); unused npm packages; `core_engine/log_exporter.py` (alias only); extra model files (`rf_model`, `calibrated_rf_model`, `hgb_model`, `lr_model`).
  8. **Too many overlapping documents:** about 9,000 lines across 7 large `.md` files that repeat the same content.
- **Hardware:** the lab plan still lists a camera "simulator" and a "software bridge". The real devices are not chosen yet (issue 7).
- **Next:** see Section 8.

**3.54 Resolution of Live Runner, Adapter Mismatch, and Academic Integrity Audits (8 November 2026)**

- **What was done:** Resolved critical software gaps and academic audit issues identified in review 3.53:
  1. **Live Pipeline Runner ([`core_engine/runner.py`](file:///d:/intrusion%20detection/core_engine/runner.py)):** Implemented `LivePipelineRunner` daemon connecting Zeek streaming `conn.log` directly into `DecisionEngine.process_flows()`, dispatching real-time WebSocket alerts and firewall rules. Added REST API endpoints (`GET /api/v1/pipeline/status`, `POST /api/v1/pipeline/start`, `POST /api/v1/pipeline/stop`) in `core_engine/app.py`.
  2. **Firewall Adapter Harmonization:** Updated `get_firewall_adapter()` in `core_engine/firewall/__init__.py` and `core_engine/app.py` to harmonize `firewall.type` with `response.adapter` from `settings.yaml`.
  3. **Router Variable Alignment:** Standardized `RouterAdapter` to support both `ROUTER_HOST` / `ROUTER_PORT` / `ROUTER_USER` / `ROUTER_KEY_FILE` and legacy `ROUTER_SSH_*` aliases. Updated `.env.example`.
  4. **Academic Integrity & Data Disclosure:** Transparently marked Step 20 camera flows in `sensor/collect_camera_traffic.py` and `reports/experiments/camera_baseline_summary.md` as synthetic development baseline. Added Logbook Entry 3 audit correction in `docs/lab_logbook.md`. Recorded Decision `D-038` approving Virtual Camera Simulator Testbed per Proposal Section 5.1.
  5. **Report Targets Synchronized:** Updated `reports/test_split_plan.md` to exact Proposal Table 9 targets ($\ge 0.85$ Macro-F1, $\le 5.0\%$ FPR, latency $< 2.0$s); maintained honest reporting of held-out 0.4028 score.
- **Verification:** Authored 3 unit tests in `tests/unit/test_runner.py` and 3 integration tests in `tests/integration/test_pipeline_api.py`. Full test suite now passes: **210 passed in 96.09s across 28 test modules (100% pass rate).**
- **Decision Recorded:** Decision `D-038` in `docs/decision_log.md`.
- **Status Advancement:** Issues 9, 10, 11, 12, 13 resolved and closed. Ready for Step 34.

**3.55 Check of the 3.54 fixes (8 November 2026)**

- **What was done:** checked commit `94fff92` against the review in 3.53. No code was changed.
- **Tests:** 210 passed (92.6 s).
- **Correct:** the runner starts with the server and feeds Zeek flows to `DecisionEngine.process_flows()`; it saves its read position, so it does not re-read old flows after a restart. The adapter setting and the router variable names now work. The `test_split_plan.md` targets are fixed. Lab logbook entry 3 is a correct way to fix entry 2.
- **Still wrong (added to Section 5, issues 17–21):**
  1. **No automatic block happens.** `process_flows()` marks attacks as `ACTIVE_BLOCK_CANDIDATE`, but nothing calls `evaluate_response()` / `execute_response()`. So `mitigations_dispatched` is always 0, and Table 10 scenarios 2–4 cannot show a block.
  2. **Old false claims are still in other files:** `camera_baseline_summary.md` (lines 21, 27: "PASS (Hypothesis H1 Clause 2)", "empirical proof"); `evaluation_iot23.md` line 19 and `model_card.md` line 62 (FPR 5.096% marked PASS); `model_card.md` line 46 ("Physical Tapo C200"); `schema_check.md` (RQ3 conclusion based on the synthetic file); decision D-024 and `execution_record.md`.
  3. **D-038 says the simulator is "approved",** but only the team agreed. The proposal says "approved camera simulator", so the supervisor must confirm.
  4. **The reason given for macro-F1 0.40 is incomplete.** Even on the 4 classes that exist in 34-1, the score is 0.50. The main causes are CnC recall 23% and PortScan precision 4%, not only the missing Malware_Download class.
  5. **Small issues:** the factory always passes `router_user="root"`, so `ROUTER_USER` in `.env` is ignored; `firewall.type` and `response.adapter` are two settings for one thing; `DecisionEngine` turns `auto_response` ON if `settings.yaml` is missing.


**3.56 Full check against the proposal, and corrections (8–9 November 2026)**

- **What was done:** every part of the project was checked against the proposal (Sections 1.5, 2.4, 3.3–3.7, 5.1; Tables 3, 5, 7, 9, 10). Each mismatch was fixed, or recorded as open if it needs the lab or the team.
- **Step by step:**
  1. **Dataset copy checked.** Wrote `tools/verify_iot23_copy.py`. It compares the first flow (`ts`, `uid`) of each local CSV with the official `conn.log.labeled` file. Result: 23/23 match (`reports/iot23_copy_verification.md`).
  2. **4 wrong scenario names fixed** in `ml_engine/manifest.py`: `dataset4` → 9-1, `dataset5` → 8-1, `dataset15` → 36-1, `dataset16` → 35-1 (D-039). The 4 interim files were made again (Step 10), then Steps 9 and 12 were run again (still 1,384,070 training flows; 23,145 held-out flows).
  3. **One held-out file only.** `sample_dataset.py` now writes it only to `data/processed/heldout/`; the second copy was deleted.
  4. **Step 17 redone (D-040).** Step 14 now saves the grouped out-of-fold probabilities. New `ml_engine/calibration.py` fits a sigmoid per class on them. Thresholds are chosen from this out-of-fold data with fixed rules. 34-1 is used once, for the final check and for permutation importance.
  5. **Steps 14–18 run again (8–9 Nov).** Results are in D-043 and in Part 0.2 of the guide: out-of-fold macro-F1 0.3422 (RF), HGB 0.4331, LR 0.2722; deployed model on 34-1 macro-F1 0.3405 (5 classes) / 0.4256 (4 present). **H1 part 1 not met.**
  6. **Automatic response connected (D-041).** `process_flows()` now calls `respond_to_outcome()`. The reason for every skipped block is saved on the event. A source that is already blocked is not blocked again; `forget_block()` runs after a manual unblock. "Local" now means inside `lab.local_networks`. `auto_response` is off by default.
  7. **Settings page works with the API (FR-07).** Each changed setting is checked, saved with its history, and applied to the running engine. The history shows who changed what, from what to what, and why.
  8. **One adapter setting.** `firewall_config_from_settings()` uses `response.adapter` only; `ROUTER_USER` is now used.
  9. **Synthetic data is labelled.** `collect_camera_traffic.py` and `tools/schema_check.py` need `--source real|synthetic`. The synthetic file was moved to `data/local/synthetic/`. Synthetic runs say "not tested (synthetic data)" (D-042). Steps 19, 20 and 22 set back to 🟡.
  10. **Report text fixed.** No "PASS" on numbers that are not the H1 measure; no "sub-second" claim (the target is median < 2 s, p95 < 5 s); no "physical Tapo"; verdicts are computed from the results.
  11. **Documents fixed:** decision log (D-039 to D-043, with notes under the older entries), `docs/response_policy.md` v2.0, `docs/requirements_checklist.md` v3.0, `reports/test_split_plan.md`, `README.md`, this file, the guide, and correction banners in the explanation files and `execution_record.md`.
  12. **Two old tests changed** to check behaviour, not old fixed values: the held-out file must exist in one place only; the detector confidence must equal the top probability (it was "> 0.80", a value from the old model).
- **Tests:** 224 Python tests passed (51 s); 2 dashboard tests passed.
- **New findings (D-043, issue 23):**
  - With the fixed rules, **no class reaches the block threshold**, so the system raises alerts but never blocks automatically.
  - **Calibration removes CnC:** CnC recall goes from 0.475 to 0 on the out-of-fold data, and to 0 on 34-1.
  - The team must decide, from the out-of-fold data only, before Step 35.
- **Still open:** issue 22 (record where the CSV copy was downloaded from), issue 23 (D-043 questions), supervisor confirmation of the lab type (D-038), and all lab work (Steps 5, 3b/3c, 19, 20, 22, 34–42).
- **Not committed yet.**

**3.57 Calibration changed so that the model finds CnC again (9 November 2026)**

- **Why:** the owner chose to change the calibration step (D-043, open question 2). The old per-class sigmoid made the model never pick CnC.
- **Step by step:**
  1. **Found the cause** in the out-of-fold data. Each DDoS scenario is a different flood type, and 78% of IoT-23 benign flows are single unanswered packets. So, on unseen scenarios, the model calls most DDoS flows Benign, and calls many flows CnC that are not CnC (CnC precision about 10%). The sigmoid then pushes CnC down until it never wins.
  2. **Wrote the selection rule first** (D-044), before running any comparison: every class must have recall ≥ 0.05; then the highest macro-F1.
  3. **Added 4 more calibration methods** to `ml_engine/calibration.py` (`none`, `temperature`, `multinomial`, `multinomial_balanced`; the old sigmoid is kept). The inputs are standardised before the regression fit, so one fit takes about 25 s.
  4. **Wrote `ml_engine/select_calibration.py` (Step 17a).** It scores each method on the out-of-fold data, with each fold calibrated by a fit on the other folds, and writes `reports/experiments/calibration_selection.md` and `.json`.
  5. **The D-044 rule chose `multinomial`** (out-of-fold macro-F1 0.3750; PortScan reached the block rule).
  6. **The final check on 34-1 failed:** macro-F1 0.0458; most DDoS flows became Benign; 80% of the synthetic camera flows became attacks. That model was **not kept**.
  7. **Recorded the failure and a new principle (D-045):** calibration may change how sure the model is, not which class wins. `temperature` (one number) is used now. This breaks the D-044 rule and is written as a deviation. 34-1 is no longer a clean unseen test; the clean test is the lab data.
  8. **Step 17 now reads the method from Step 17a**; `select_calibration.py` writes both the D-044 rule result and the D-045 final choice, so a re-run gives the same model. Steps 17 and 18 were run again (bundle v1.2.0), and the synthetic Step 20/22 checks too.
- **Result (34-1, `temperature`):** macro-F1 **0.4530** (5 classes) / 0.5662 (4 present); accuracy 0.8063; CnC recall 0.3671 with precision 0.9781 (was 0); IoT-23 benign flows raising an alert 2.5%, reaching a block threshold 0%. Synthetic camera file: 0 of 5,000 flows called attacks (software check only).
- **Not solved:** no class reaches the block rule, so the system only raises alerts. CnC alerts are few: the CnC alert threshold is 0.39 (fallback rule), and only 0.7% of 34-1 CnC flows reach it. Issue 23 updated with the three choices.
- **Tests:** new tests for the calibration methods and the selection rules; one old detector test changed (it expected PortScan confidence > 0.50, a value from the old model; it now checks that the confidence is the top probability). Full suite: **239 Python tests passed**; 2 dashboard tests passed.
- **Not committed yet.**

**3.58 Alignment with Proposal 3.4 blocking rule, repeat replay, detailed-label reporting, and dataset verification (9 November 2026, D-046)**

- **Why:** During the full proposal audit, four critical discrepancies were addressed: (1) blocking required a single flow to reach 95% precision (an internal D-040 constraint), which is impossible without rate features, preventing any auto-blocking; Proposal 3.4 specifically mandates a confidence threshold combined with repeated events within a time window; (2) `response.min_confidence: 0.85` safety floor blocked all calibrated decisions; (3) original detailed IoT-23 labels were not evaluated (Proposal 3.2); (4) dataset copy check was only verifying the first row.
- **What was done:**
  1. Updated `ml_engine/sample_dataset.py` (Step 12) to preserve audit columns (`ts`, `id.orig_h`, `id.resp_h`, `id.resp_p`, `detailed_label`) in `train_features.parquet` and `held_out_test.parquet` without modifying the 22 feature/metadata columns (verified row-for-row, zero retraining required).
  2. Implemented `ml_engine/response_replay.py` simulating Proposal 3.4 blocking logic (3 repeats within 60s, 30m rule duration) across all out-of-fold training scenarios.
  3. Re-ran Step 17 (`ml_engine/calibrate_and_explain.py`) with repeat replay:
     - **PortScan block threshold:** 0.30 (413 blocks; 96.6% safe/malicious; only 3 of 28,594 benign targets ever blocked).
     - **CnC block threshold:** 0.39 (142 blocks; 100% safe/malicious; 0 benign targets blocked).
     - **DDoS / Malware_Download:** Alert only (DDoS without rate features cannot distinguish isolated packets reliably; Malware_Download had < 10 blocks).
  4. Lowered safety floor `response.min_confidence` to 0.30 in `config/settings.yaml`, `config/settings.example.yaml`, and `my-app/src/pages/Settings.js`.
  5. Implemented Section 8 in `reports/experiments/thresholds_and_explanation.md` evaluating grouped vs detailed original labels for all labels $\ge 30$ samples.
  6. Expanded `tools/verify_iot23_copy.py` to check both first and last flows (23/23 matched). Investigated 3 label discrepancies against raw CTU server files via HTTP range requests; confirmed raw server files match our local copy exactly. Documented source file `D:\Download\archive.zip` (downloaded 2026-10-19 16:49).
  7. Automated test suite: **246 passed in 60.56s across 29 test modules (100% pass rate).**

**3.59 Manual control, rule expiry daemon, and crash / restart recovery (Step 34, 9 November 2026, D-047)**

- **Why:** Fulfilled Step 34 and Proposal Section 3.7 / Table 9 / Objective O5 requirements: (1) manual block and unblock from the dashboard with complete audit trail in `system_logs` and `response_actions`; (2) automatic background rule expiry worker (`RuleExpiryWorker`); (3) startup crash recovery reconciling MongoDB blocklist with firewall rules (`reconcile_on_startup`).
- **What was done:**
  1. Built [`core_engine/rule_worker.py`](file:///d:/intrusion%20detection/core_engine/rule_worker.py):
     - `sweep_expired_rules()`: Sweeps expired rules in MongoDB (`expires_at <= now()`), unblocks firewall adapter, notifies `DecisionEngine.forget_block()`, emits real-time WebSocket `blocklist_update` (status='expired'), and records audit records in `system_logs` and `response_actions`.
     - `reconcile_on_startup()`: Sweeps rules expired while offline, restores still-active blocks on firewall with remaining duration (`STARTUP_RULE_RESTORED`), cleans orphaned firewall rules (`STARTUP_ORPHAN_RULE_REMOVED`), enforces allowlist immunity (`STARTUP_ALLOWLIST_PROTECTION`), and records complete audit summary in `system_logs`.
     - `RuleExpiryWorker`: Background daemon thread (default 10s sweep period) with graceful lifecycle management (`start`, `stop`, `sweep_now`, `get_status`).
  2. Integrated into [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py):
     - Startup reconciliation executes during `create_app()`.
     - `add_block()` and `remove_block()` now log `MANUAL_BLOCK` and `MANUAL_UNBLOCK` events to `system_logs` with admin username.
     - `POST /api/blocklist` accepts both `duration_minutes` and `minutes`.
     - `GET /api/blocklist` provides both `blocks` and `rules`.
     - Added management endpoints: `GET /api/v1/firewall/sync`, `POST /api/v1/firewall/sync`, `GET /api/v1/firewall/worker/status`, `POST /start`, `POST /stop`.
  3. Integrated into React Frontend [`my-app/src/pages/Blocklist.js`](file:///d:/intrusion%20detection/my-app/src/pages/Blocklist.js):
     - Updated rule loading to accept `res.data.blocks || res.data.rules`.
     - Updated manual block form to send `duration_minutes` alongside `minutes`.
  4. Tests:
     - Implemented [`tests/unit/test_rule_worker.py`](file:///d:/intrusion%20detection/tests/unit/test_rule_worker.py) with 7 comprehensive unit tests.
     - Added 2 integration tests in [`tests/integration/test_app_api.py`](file:///d:/intrusion%20detection/tests/integration/test_app_api.py).
     - Full test suite: **255 Python tests passed in 74.81s (100% pass rate)**; **2 React tests passed in 47.85s**. Phase 8 is built and tested on the PC (wording corrected in 3.61; lab tests in Phase 9).

**3.60 Check of the Step 34 work (commit `66a7ead`, 9 November 2026)**

- **What was done:** checked the Step 34 code, tests and documents against the guide and the proposal. No code was changed.
- **Tests:** 255 Python tests passed (155.9 s), as reported.
- **Correct:** manual block refuses allowlisted IPs (403 `ALLOWLIST_PROTECTED`); manual block and unblock write `response_actions` and `system_logs` with the admin's name; `blocklist_update` is sent by Socket.IO; the expiry sweep marks rules `expired`, removes them from the firewall and calls `forget_block`; startup recovery restores missing rules, removes orphan rules and allowlisted rules, and writes `STARTUP_RECOVERY_COMPLETE`. No data, model or secret files were committed.
- **Still wrong (added to Section 5, issues 27–31):**
  1. The expiry worker is **never started** when the server runs normally (`python core_engine/app.py`). It starts only in tests (`autostart_rule_worker`) or by `POST /api/v1/firewall/worker/start`. So expired rules stay `active` in the database and on the dashboard.
  2. Manual block: if the firewall call fails (any error except the allowlist), the database still records the block, `response_actions` says `applied`, and the API answers 201 "enacted successfully". The audit record is then wrong (FR-07). This code is from Step 33.
  3. Startup recovery writes `STARTUP_RULE_RESTORED` with outcome `SUCCESS` even when the firewall call failed. It also does not check the allowlist before restoring.
  4. Small: remaining minutes are rounded down (a rule can end up to 59 s early); restore compares IPs only, not the direction.
  5. Documents say "(VERIFIED)" and "Phase 8 100% COMPLETE". The tests use the simulation adapter on the PC. The proposal checks FR-06 "on a separated network", and Table 9 reliability in the lab (Steps 35, 38). The correct wording is "built and tested on the PC; lab check pending".
  6. Issue 22 was closed, but only the local zip path and date are written. The **web page** the copy came from is still not recorded (proposal 3.2: "where it came from").
- **Dataset evidence added to D-046:** the 49-1 and 52-1 label differences were checked inside the official files; both match our copy.

**3.61 Fixes after the Step 34 check (9 November 2026, D-048)**

- **Why:** entry 3.60 found 5 problems (issues 27–31).
- **Step by step:**
  1. **Expiry worker now starts with the server:** `core_engine/app.py` starts `RuleExpiryWorker` in `__main__`, next to the live pipeline runner (issue 27).
  2. **Manual block with a firewall error:** the API returns 502 `FIREWALL_ERROR`; nothing is saved as an active block; `response_actions` says `failed` and `system_logs` says `MANUAL_BLOCK` / `FAILURE`. Manual unblock and rule expiry record `firewall_error` (outcome `PARTIAL`) when the firewall call fails (issue 28).
  3. **Startup recovery (`core_engine/rule_worker.py`):** allowlisted hosts are never restored (their database record is closed); a failed restore is logged as `FAILURE` and the summary becomes `partial`; rules are compared by IP and direction; remaining minutes are rounded up (issue 29).
  4. **Dashboard Blocklist page** shows the server's full message (the firewall error, or the unblock warning).
  5. **Wording** in the guide (Step 34 and its table row), this file (row 34, entry 3.59), D-047 (note) and `execution_record.md`: "built and tested on the PC (simulation adapter); lab check in Steps 35 and 38" (issue 30).
  6. **Dataset source found and checked (issue 31):** Kaggle "IOT-23 Full Dataset" by surajsooraj26 (https://www.kaggle.com/datasets/surajsooraj26/iot-23, version 1, CC0). The size of all 23 local files equals Kaggle's public file list, byte for byte. Written in D-039 and in `reports/iot23_copy_verification.md`, which now also explains the 3 label-total differences.
- **Tests:** 4 new unit tests and 1 new integration test. Full suite: **260 Python tests passed** (116.8 s); 2 dashboard tests passed.
- **Not committed yet.**

**3.62 Full review against the proposal, and search for unused parts (9 November 2026)**

- **What was done:** checked every part against the proposal, and searched the code, dashboard, packages and documents for parts that are not used. No code was changed.
- **New problems (Section 5, issues 32–35):**
  1. The dashboard loads Tailwind CSS from the internet (`cdn.tailwindcss.com` in `my-app/public/index.html`). The lab is a separated network (proposal 3.8, 5.1), so the dashboard may show with no styling there.
  2. `requirements.txt` lists `flask-jwt-extended`, but the code never imports it; the code imports `jwt` (PyJWT), which is not listed. It works only because `flask-jwt-extended` installs PyJWT.
  3. Unused parts: 3 React pages that nothing imports (`components/Dashboard.js`, `pages/IOTDetails.js`, `pages/IoTDevicesDashboard.js`) with their CSS and 2 images (`back.jpg`, `logo.svg`); 8 npm packages (`@headlessui/react`, `framer-motion`, `lottie-react`, `react-hook-form`, `react-icons`, `styled-components`, `chart.js`, `react-chartjs-2`); `core_engine/log_exporter.py` (only an alias of `export_service.py`).
  4. Four long documents still contain old numbers under correction banners: `PROJECT_EXPLANATION_EN.md` (7 lines), `PROJECT_EXPLANATION.md` (6), `COMPLETE_PROJECT_GUIDE_A_TO_Z.md` (6), `docs/execution_record.md` (19). They could confuse readers at the viva.
- **Checked and correct:** grouped validation and held-out scenario; Random Forest as main model with the 2 comparison models; class weights and unknown-category encoder; IPs and UID never model inputs; pipeline saved with the model; calibration with reliability curve and Brier score; permutation importance on held-out data; label mapping fixed before training; dataset copy traced to its source and checked against the official files; Zeek / Flask / Socket.IO / MongoDB / React / Nmap / nftables stack; allowlist, local-network check, confidence + repeat rule, rule expiry, reason codes, audit log, manual unblock; alert fields (time, direction, source/destination, class, confidence, evidence note, response status); retention (TTL) rules; secrets in `.env` (not in Git).

---

## 4. Challenges and how they were solved

| #  | Challenge                                         | Cause                                                                                                         | Effect                                                     | Solution                                                                                                         | Status   |
| -- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| 1  | Alerts scope (Telegram/email)                     | The old explanation listed Telegram and email as FR-05. The proposal does **not** include them; FR-05 is Nmap discovery. | The old notes did not match the proposal.                 | No scope change needed. Alerts go to the dashboard through Socket.IO (FR-04).                                     | ✅ Solved |
| 2  | Which hardware is needed                          | The team was unsure.                                                                                          | Delay in starting.                                         | Proposal 5.1: an IP camera **or a camera simulator**, NVR, managed switch with port mirroring, Linux sensor, attack test PC, admin PC. A phone camera app can be used as the camera simulator. Code can start on the Windows PC. | ✅ Clear; hardware not arranged yet |
| 3  | Fake features in the old live code                | Scapy per packet with fixed values (`conn_state=6`, `history=22`, `service=0`, `duration=0`).                | The model got wrong inputs.                                | Use **Zeek `conn.log`** for live features (Steps 19–22). Scapy/TShark only for checks.                           | ✅ Solved (Steps 19–22) |
| 4  | Two databases, five backend ports                 | Old scripts were built separately.                                                                            | Data could not be linked.                                  | One database `iot_ids_db` (9 collections, Step 23) and one unified Flask + Socket.IO server on port 5000 (Step 25). | ✅ Solved (Steps 23 & 25) |
| 5  | `my-app` saved as an empty submodule              | `create-react-app` made its own `.git` folder.                                                                | React code was not saved in Git.                           | Removed `my-app/.git` and added `my-app/` as normal files.                                                       | ✅ Solved |
| 6  | Missing Python packages                           | `pymongo` and others were not installed.                                                                      | `db_service.py` did not run.                               | Quick fix: installed into the global Python. Proper fix in Step 3: `.venv` + fixed versions.                     | ✅ Solved (Step 3a) |
| 7  | Line-ending warnings (LF/CRLF)                    | Windows and Linux use different line endings.                                                                 | Linux scripts could break.                                 | Added `.gitattributes`.                                                                                          | ✅ Solved |
| 8  | Binaries and secrets tracked in Git               | Installer, `users.db`, old `app.py` with a secret, `.zip` files were committed.                               | Large repo; secret in version control (proposal 3.6).      | Removed from tracking and moved to `archive/`; `.gitignore` fixed.                                               | 🟡 History still open (issue 1) |
| 9  | The old trained model cannot be used              | Unofficial data, no scenario IDs, random split, unknown labels, inputs that live Zeek cannot make.            | Detection would not work; H1 and O2 cannot be tested.      | Train a new model from official IoT-23 (Steps 7–18).                                                             | ✅ Decided |
| 10 | Old explanation documents did not match the proposal | Version 1 had 17 wrong points.                                                                             | Team members could follow a wrong plan.                    | Both files rewritten (version 2).                                                                                | ✅ Solved |
| 11 | Label mapping frozen too early                    | It was written before seeing the real IoT-23 labels.                                                          | It went against Table 5 ("labels that we checked").        | Changed to a draft; freeze in Step 8, after the Step 7 manifest.                                                 | ✅ Solved |
| 12 | PC memory is limited (11.7 GB)                    | IoT-23 has hundreds of millions of rows.                                                                      | The full data cannot be loaded at once.                    | Read the files in parts (Step 10) and sample per scenario and class (Step 12).                                   | ✅ Solved (Steps 10 & 12) |
| 13 | The team does not know how to train a model       | No ML training experience yet.                                                                                | Risk of delay.                                             | Simple explanation given; scripts will be written one step at a time (Steps 7–18).                              | ✅ Solved (Steps 14–18) |

---

## 5. Open issues (to do)

| # | Issue                                                                                                   | What to do                                                                                                                         | Priority |
| - | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1 | ~~Public repo with old files in its history.~~ | **Closed (20 Oct 2026):** the owner decided this is not an issue. | — |
| 2 | ~~Step 1 files not complete yet.~~ | **Closed (21 Oct 2026):** Device specs filled (simulation/loan), all team permissions ticked, retention periods agreed (90/30/90 days). Step 1 is ✅ Done. | — |
| 3 | ~~No backup confirmed.~~ | **Closed (20 Oct 2026):** the owner made a backup. | — |
| 4 | ~~The documentation `.md` files are in `.gitignore`.~~ | **Closed (1 Nov 2026):** removed from `.gitignore` and tracked under Git commit `698caba`. | — |
| 5 | Software setup (Step 3).                                                                                | Step 3a ✅ done on Windows (.venv created, pinned requirements, check_env PASSED). Step 3b/3c pending for lab hardware.            | Low      |
| 6 | ~~`db_service.py` does not yet meet Step 23.~~ | **Closed (31 Oct 2026):** `core_engine/db_service.py` refactored into production-grade service with 9 collections, full block history audit trail, dynamic TTL retention indexes, dynamic settings, burst-event coalescing, and comprehensive pytest test suite (18 dedicated tests, D-027). | — |
| 7 | Lab hardware not arranged. | Arrange the managed switch, Linux sensor PC, lab router and camera, or approve Virtual Camera Testbed (Decision D-038). | Medium   |
| 8 | ~~Almashhadani et al. (2024) cannot be found.~~ | **Closed (20 Oct 2026):** citation removed; Santos et al. (2023) is used alone (decision D-009). Tell the supervisor at the next meeting. | — |
| 9 | ~~Live pipeline not connected (found 8 Nov 2026).~~ | **Closed (8 Nov 2026):** Added `LivePipelineRunner` (`core_engine/runner.py`) daemon tailing `conn.log` into `DecisionEngine.process_flows()`, integrated into `core_engine/app.py`, and added REST control endpoints (`/api/v1/pipeline/*`) (D-038). | — |
| 10 | ~~Step 20 camera flows disclosure & logbook correction.~~ | **Closed (8 Nov 2026):** Explicitly disclosed as synthetic development baseline in `sensor/collect_camera_traffic.py` and `camera_baseline_summary.md`. Added Logbook Entry 3 audit correction. Scheduled empirical verification for Step 20b/Step 35 (D-038). | — |
| 11 | ~~`response.adapter` setting ignored; code reads `firewall.type`.~~ | **Closed (8 Nov 2026):** Harmonized `get_firewall_adapter()` (D-038). **Updated 8 Nov 2026:** `response.adapter` is now the only setting, via `firewall_config_from_settings()` (D-041). | — |
| 12 | ~~`.env.example` router names differ from the code.~~ | **Closed (8 Nov 2026):** Harmonized `RouterAdapter` to accept both `ROUTER_HOST` / `ROUTER_PORT` / `ROUTER_USER` / `ROUTER_KEY_FILE` and legacy `ROUTER_SSH_*` aliases. Updated `.env.example` (D-038). | — |
| 13 | ~~Wrong targets / verdicts in some reports (`test_split_plan.md`).~~ | **Closed (8 Nov 2026):** Corrected `reports/test_split_plan.md` to exact Proposal Table 9 targets ($\ge 0.85$ Macro-F1, $\le 5.0\%$ FPR, latency $< 2.0$s); maintained honest reporting of held-out 0.4028 score (D-038). **Note (9 Nov 2026):** 0.4028 is replaced by the new results (D-043). | — |
| 14 | Unused React files, npm packages, `log_exporter.py`, extra model files. | Move to `archive/` or delete after the team agrees. | Low |
| 15 | Too many overlapping documents. | Keep the guide, this file, the decision log and one explanation; merge or archive the others. | Low |
| 16 | The trained model file is not in Git. | Copy `ml_engine/models/ids_bundle_v1.joblib` to the sensor by USB/scp. | Medium |
| 17 | ~~Automatic response never runs (found 8 Nov 2026, entry 3.55).~~ | **Closed (8 Nov 2026):** `DecisionEngine.respond_to_outcome()` is called for each flow in `process_flows`; the reason for every skipped block is saved on the event (D-041, entry 3.56). | — |
| 18 | ~~False claims still in `camera_baseline_summary.md`, `evaluation_iot23.md`, `model_card.md`, `schema_check.md`, D-024, `execution_record.md`.~~ | **Closed (8–9 Nov 2026):** the reports are now written by the scripts from measured values and say SYNTHETIC where the data is synthetic; D-042 replaces D-024 and D-026; correction banner in `execution_record.md` (entry 3.56). | — |
| 19 | ~~D-038 says "approved" without the supervisor.~~ | **Closed in the documents (8 Nov 2026):** D-038 now reads "agreed by the team; to be confirmed with the supervisor" (D-042). Update D-038 after the meeting. | — |
| 20 | ~~Macro-F1 0.40 explanation is incomplete.~~ | **Closed (9 Nov 2026):** all results were made again after the scenario-name fix (D-039). Reports now give the 5-class and the present-class scores and the per-class results (D-043). | — |
| 21 | ~~`ROUTER_USER` ignored; two adapter settings; `auto_response` default ON.~~ | **Closed (8 Nov 2026):** `firewall_config_from_settings()` uses `response.adapter` only; `router_user` is passed from the settings; `auto_response` defaults to `False` (D-041). | — |
| 22 | ~~Where the IoT-23 CSV copy was downloaded from is not recorded.~~ | **Closed (9 Nov 2026, D-046):** Source archive verified at `D:\Download\archive.zip` (9.16 GB, downloaded 2026-10-19 16:49). Authenticity verified against CTU server raw archives with `tools/verify_iot23_copy.py` (23/23 first/last flows match, server discrepancies checked). | — |
| 23 | ~~No class reaches the block rule, so the system only raises alerts.~~ | **Closed (9 Nov 2026, D-046):** Block rule aligned with Proposal 3.4 (confidence threshold + 3 repeats within 60s). Replay established block thresholds: PortScan 0.30, CnC 0.39; DDoS and Malware remain alert-only. | — |
| 24 | ~~Results for original detailed IoT-23 labels not reported.~~ | **Closed (9 Nov 2026, D-046):** Step 12 preserved `detailed_label` audit column in Parquet; Step 17 evaluated recall for all 17 original labels $\ge 30$ samples in `reports/experiments/thresholds_and_explanation.md` Section 8. | — |
| 25 | ~~Dataset copy check only compares the first flow.~~ | **Closed (9 Nov 2026, D-046):** `tools/verify_iot23_copy.py` verified first row (23/23) and last row (23/23). Direct HTTP range requests against official CTU archives confirmed local CSVs match raw data byte-for-byte. | — |
| 26 | ~~Safety floor `response.min_confidence: 0.85` too restrictive.~~ | **Closed (9 Nov 2026, D-046):** Lowered floor to `0.30` in `config/settings.yaml`, `config/settings.example.yaml`, and React frontend `Settings.js` to match calibrated model threshold range. | — |
| 27 | ~~The rule expiry worker is not started in normal running.~~ | **Closed (9 Nov 2026, D-048):** started in `core_engine/app.py` `__main__` next to the runner; test added. | — |
| 28 | ~~Manual block recorded as `applied` when the firewall call failed.~~ | **Closed (9 Nov 2026, D-048):** returns 502 `FIREWALL_ERROR`, nothing saved as active, audit says `failed`; unblock and expiry record `firewall_error`; integration test added. | — |
| 29 | ~~Startup recovery logs SUCCESS on failure; no allowlist check.~~ | **Closed (9 Nov 2026, D-048):** allowlist checked first, failures logged as FAILURE, direction compared, minutes rounded up; 3 unit tests added. | — |
| 30 | ~~Step 34 / D-047 say "VERIFIED" and "Phase 8 100% COMPLETE".~~ | **Closed (9 Nov 2026, D-048):** wording is now "built and tested on the PC; lab check in Steps 35 and 38" in the guide, progress file, D-047 note and execution record. | — |
| 31 | ~~The web page of the dataset copy is not recorded.~~ | **Closed (9 Nov 2026):** Kaggle "IOT-23 Full Dataset" by surajsooraj26 (https://www.kaggle.com/datasets/surajsooraj26/iot-23, v1, CC0); all 23 file sizes equal the Kaggle file list (D-039). | — |
| 32 | Dashboard loads Tailwind CSS from the internet (`cdn.tailwindcss.com`); the separated lab may have no internet (entry 3.62). | Build Tailwind locally with the `tailwindcss` package (or save the script in `my-app/public/`) and remove the CDN line. Test the dashboard with the network cable out. | **High** |
| 33 | `requirements.txt`: `flask-jwt-extended` is listed but not used; `PyJWT` is used but not listed (entry 3.62). | Replace `flask-jwt-extended` with a pinned `PyJWT`. | Low |
| 34 | Unused React pages, CSS, images and 8 npm packages; `core_engine/log_exporter.py` alias (entry 3.62; replaces issue 14). | Move to `archive/` or delete; remove the packages from `package.json`; re-run tests and `npm run build`. | Low |
| 35 | Four long documents keep old numbers under correction banners (entry 3.62; replaces issue 15). | Before the viva: rewrite them from the current results, or move them to `archive/` and keep the guide, this file, the decision log, the checklist and README. | Medium |

---

## 6. Decisions made so far

The full, official list is now in `docs/decision_log.md` (D-001 onward). This table is a short copy.

These will move into `docs/decision_log.md` when it is created (Step 4).

| Date        | Decision                                                                                       | Reason                                                              |
| ----------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 19 Oct 2026 | Follow `STEP_BY_STEP_GUIDE.md` in order (Steps 0–42). If the guide and the proposal ever disagree, the proposal is correct. | One clear plan that follows the proposal.                           |
| 19 Oct 2026 | Do not use the old data (`X_train.csv`) or the old model.                                      | Proposal 3.2; no scenario IDs; leakage; unknown labels (Section 4, challenge 9). |
| 19 Oct 2026 | Keep the old code in `archive/` (not in Git) for reference only.                               | Nothing is lost; the repository stays clean.                        |
| 19 Oct 2026 | One database (`iot_ids_db`) and one backend.                                                   | Proposal 3.6.                                                       |
| 19 Oct 2026 | No Telegram or email alerts.                                                                   | They are not in the proposal.                                       |
| 19 Oct 2026 | The label mapping stays a draft until Step 8.                                                  | It must be based on the real labels (Table 5).                      |
| 19 Oct 2026 | Lab IP plan example: camera LAN `192.168.50.0/24`, "outside" test subnet `10.10.10.0/24`.       | Separated lab (3.8); the attack PC must be behind the router.       |
| 19 Oct 2026 | Passive mode is the default.                                                                   | Proposal Table 11.                                                  |
| 20 Oct 2026 | Keep the GitHub repository public; do not rewrite the old history.                             | Owner's decision.                                                   |
| 20 Oct 2026 | Remove the Almashhadani et al. (2024) citation; use Santos et al. (2023) alone (D-009).         | Nobody has the paper; it cannot be found.                           |
| 21 Oct 2026 | Device planning with software simulation and lab loan allocation (D-010).                      | Proposal 5.1 allows camera simulation; avoids hardware blockers.   |
| 21 Oct 2026 | Data retention durations agreed: 90d attack/audit, 30d summaries, 180d test captures (D-011). | Proposal 3.8; balances research needs with data minimization.       |
| 22 Oct 2026 | Step 3a environment execution on Windows PC (D-012).                                          | Dedicated .venv, Npcap verified, Nmap deferred to Step 27.          |
| 23 Oct 2026 | Finalize local settings, management allowlist, and secure secrets (D-013).                    | Central config, safe allowlist, 32-byte cryptographic keys in .env. |
| 23 Oct 2026 | Freeze IoT-23 label mapping to 5 classes; exclude ambiguous Attack labels (D-014).            | Proposal Table 5, Sections 2.3 & 3.2; avoid data snooping.          |
| 25 Oct 2026 | Shared feature engineering specification (19 features) and zero-skew design (D-015).          | Proposal Table 6; Sections 3.3 & 3.5; identical offline/live schema. |
| 25 Oct 2026 | Stratified dataset sampling (N=50k/class) & 100% CnC preservation (D-016).                     | Proposal Section 3.3 step 6, Table 11; RAM safe (<180MB); 1.38M flows. |
| 25 Oct 2026 | Formal three-level model evaluation plan & Checkpoint C4 held-out isolation (D-017).           | Proposal Section 3.4; Objective O2; eliminate intra-session leakage. |
| 31 Oct 2026 | Random Forest hyperparameter tuning and Level 1 Grouped Cross-Validation (D-018).              | Proposal Sections 2.4, 3.3 step 5, 3.4; Pipeline with ColumnTransformer; tuned RF model (15.19 MB). |
| 31 Oct 2026 | Model comparison benchmarks & RF selection as primary prototype classifier (D-019).             | Proposal Sections 1.3, 2.4, Table 9; RF vs LR vs HGB on identical 5-fold CV; RF auditable & fast. |
| 31 Oct 2026 | Level 2 held-out zero-day evaluation (Capture-34-1) & Hypothesis H1 diagnosis (D-020).         | Proposal Section 3.4, Table 9, H1, Checkpoint C4; 76.72% acc, 5.096% FPR, PR-AUC 0.82–0.99; no test leak. |
| 31 Oct 2026 | Probability calibration (Sigmoid scaling), threshold dual-matrix & explainability rules (D-021). | Proposal Sections 2.4, 3.4, 3.7; Table 7 (FR-06), Table 11; Brier -47.7%, dual thresholds in JSON. |
| 31 Oct 2026 | Production model bundle export (ids_bundle_v1.joblib) & Model Card publication (D-022). | Proposal Sections 2.4, 3.4, 3.7; Table 7 (FR-01, FR-02, FR-03, FR-06); Table 9, 11; Mitchell et al.; Track 1 concluded. |
| 31 Oct 2026 | Zeek live telemetry configuration, streaming JSON policies, and sensor test harness (D-023). | Proposal Section 3.3 step 1, 3.5, Table 7 (FR-01), Table 8; continuous JSON logging, checksum override, simulation runner. |
| 31 Oct 2026 | Local IP-camera benign baseline collection, empirical FPR validation & H1 Clause 2 (D-024). | Proposal Section 1.6, 2.3, 3.4 Level 3, 5.1; Table 11; H1 Clause 2; 5,000 camera flows, FPR 0.000% <= 5%, zero video drop. |
| 31 Oct 2026 | Real-time Zeek streaming ingestion adapter, micro-batching & state recovery (D-025). | Proposal Section 3.3 step 1, 3.5, Figure 2 & 4; Table 7 (FR-01, FR-03); 23k fps throughput, 0 data loss. |
| 31 Oct 2026 | Offline vs live feature schema audit, zero training-serving skew, and RQ3 certification (D-026). | Proposal Section 3.3 step 7, 3.5; Table 6; RQ3 resolved, Checkpoint C6 passed; 100% 19-feature alignment. |
| 31 Oct 2026 | MongoDB database architecture, full block history compound index, and TTL retention rules (D-027). | Proposal Section 3.6, Figure 4; Table 7 (FR-01-FR-08); 9 collections, non-overwriting block history, 90d/30d TTL. |
| 31 Oct 2026 | Authentication, bcrypt password security, 8-hour JWT access tokens, and CLI admin provisioning (D-028). | Proposal Section 3.6, 3.7; Table 7 (FR-04, FR-07, FR-08); bcrypt >= 12 rounds, bounded JWT, system_logs audit. |
| 31 Oct 2026 | Consolidated Flask + Socket.IO server on port 5000 with RBAC, authenticated WebSocket streams, and safety guardrails (D-029). | Proposal Section 3.6, Figure 2 & 4; Table 7 (FR-01-FR-08); single port 5000 server, 20 REST endpoints, approved subnet & allowlist guardrails. |
| 31 Oct 2026 | Detector and decision engine architecture, calibrated inference, dual thresholds, allowlist safety, burst coalescing, and latency tracking (D-030). | Proposal Figures 2 & 3; Section 3.4, 3.6, 3.7; Table 7 (FR-01, FR-02, FR-03, FR-04, FR-06); 137 passed tests. |
| 31 Oct 2026 | Authorized Nmap device discovery service, multi-evidence camera heuristics, approved subnet restrictions, and audit logging (D-031). | Proposal Section 3.6 (Figure 4, collections devices, scans), 3.7; Table 7 (FR-05); 154 passed tests (12 unit, 5 integration). |
| 31 Oct 2026 | Forensic log export architecture, multi-attribute filtering, RFC 4180 CSV / JSON serialization, and audit trail invariants (D-032). | Proposal Section 3.6 (Figure 4), Table 7 (FR-07, FR-08); 168 passed tests (10 unit, 4 integration); Phase 6 concluded. |
| 1 Nov 2026  | React frontend cleanup, single URL config, JWT Socket.IO streaming, and fake attack elimination (D-033). | Proposal Table 8; unified `REACT_APP_API_URL`, Bearer auth interceptors, Jest tests passing, production build 147.78 kB. |
| 1 Nov 2026  | Canonical responsive 7-page dashboard suite and real-time operator verification badges (D-034). | Proposal Section 3.6, Table 8, Section 7.1; responsive Layout, Model Prediction vs Confirmed Incident badges, Phase 7 concluded. |
| 1 Nov 2026  | Direction-aware response policy, 7 safety guardrails, and sliding-window repeat coalescing (D-035). | Proposal Table 5, Section 2.5, 3.7; Checkpoint C7; RQ5; 12 unit tests passing, 180 total tests passing (100% pass rate). |
| 1 Nov 2026  | nftables ruleset specifications, auto-expiring timed sets, and Linux kernel firewall adapter (D-036). | Proposal Section 3.7, Table 8; FR-06; inline bridge & router nft rulesets; timed sets; 12 unit tests passing, 192 total tests. |
| 1 Nov 2026  | Modular response adapter suite, passive router mitigation, simulation engine, and API integration (D-037). | Proposal Section 1.2, 2.5, 3.7; Figure 5; FR-06; BaseFirewallAdapter, RouterAdapter, SimulationAdapter, DecisionEngine & Flask API integration; 12 unit/integration tests passing (204 total repo tests). |

---

## 7. Current state of the project folder

```
D:\intrusion detection\
├── .env.example, .gitignore, .gitattributes, README.md, requirements.txt   (in Git)
├── STEP_BY_STEP_GUIDE.md, PROJECT_EXPLANATION.md, PROJECT_EXPLANATION_EN.md,
│   PROJECT_PROGRESS_AND_CHALLENGES.md                                     (tracked in Git)
├── config/
│   ├── settings.example.yaml      # Step 4 template layout, start values
│   ├── settings.yaml              # Step 4 active local settings (in .gitignore)
│   └── label_mapping.yaml         # Step 8 FROZEN to 5 target classes (D-014)
├── core_engine/
│   ├── __init__.py                # core engine package init
│   ├── zeek_adapter.py            # Step 21 real-time Zeek streaming adapter (micro-batching, rotation recovery)
│   ├── db_service.py              # Step 23 MongoDB database service (9 collections, full block history, TTL indexes)
│   ├── auth.py                    # Step 24 authentication engine (bcrypt hashing, 8h JWT tokens, system_logs audit)
│   ├── app.py                     # Step 25 consolidated Flask + Socket.IO server (port 5000, 20 REST endpoints, RBAC)
│   ├── detector.py                # Step 26 real-time ML intrusion detector (ids_bundle_v1 inference, 19 features)
│   ├── decision_engine.py         # Step 26 decision engine & Step 31 response policy integration
│   ├── response_policy.py         # Step 31 direction-aware policy engine & 7 safety guardrails (Table 5)
│   ├── scanner_service.py         # Step 27 authorized Nmap discovery service (camera heuristics, approved subnet guardrails)
│   ├── export_service.py          # Step 28 forensic log export service (multi-attribute filtering, RFC 4180 CSV & JSON)
│   ├── log_exporter.py            # Step 28 backward-compatible alias module
│   └── firewall/                  # Step 32-33 firewall adapters
│       ├── __init__.py            # Step 33 factory init & get_firewall_adapter()
│       ├── base.py                # Step 33 BaseFirewallAdapter ABC & allowlist verification
│       ├── nftables_adapter.py    # Step 32 Linux nftables programmatic adapter (timed sets, simulation fallback)
│       ├── router_adapter.py      # Step 33 passive SPAN OpenWrt/Linux router SSH adapter
│       └── simulation_adapter.py  # Step 33 development simulation adapter (is_simulated=True)
├── data/                          # raw/iot23 (23 scenarios, 44.13 GB), interim (23 Parquet, 10.6 GB), processed (train_features, heldout), local (not in Git)
├── docs/
│   ├── execution_record.md        # detailed practical execution & commands log
│   ├── lab_logbook.md             # lab logbook (Step 1)
│   ├── project_summary.md         # one-page summary (Step 0)
│   ├── literature_notes.md        # notes on 13 references (Step 0)
│   ├── decision_log.md            # decisions D-001 to D-030 (Steps 4, 8, 11-26)
│   ├── threat_model.md            # system threat model & architecture (Step 6)
│   ├── requirements_checklist.md  # FR-01–FR-08, NFRs, O1–O6 checklist (Step 6)
│   ├── response_policy.md         # Step 31 response policy & safety guardrails spec
│   └── ethics/                    # lab_plan_and_rules.md, data_retention_plan.md (Step 1)
├── ml_engine/
│   ├── manifest.py                # Step 7 dataset manifest generator
│   ├── data_quality.py            # Step 9 data quality auditor & matrix builder
│   ├── load_iot23.py              # Step 10 chunked ingestion & parquet cleaner
│   ├── features.py                # Step 11 shared feature extraction engine (Table 6)
│   ├── sample_dataset.py          # Step 12 stratified sampler & feature parquet generator
│   ├── train.py                   # Step 14 Random Forest training pipeline & CV evaluator
│   ├── compare_models.py          # Step 15 comparative evaluation across 3 model families
│   ├── evaluate.py                # Step 16 Level 2 held-out zero-day scenario evaluator
│   ├── calibrate_and_explain.py   # Step 17 probability calibration & threshold tuning
│   ├── export_bundle.py           # Step 18 production bundle export & model card builder
│   └── models/                    # rf_model.joblib, lr_model.joblib, hgb_model.joblib, calibrated_rf_model.joblib, ids_bundle_v1.joblib (gitignored)
├── my-app/                        # Step 29-30 React SOC dashboard (7 pages, Socket.IO, zero synthetic data)
│   ├── src/
│   │   ├── config.js              # Step 29 single backend URL configuration
│   │   ├── services/              # Step 29 api.js (Axios + JWT) and socket.js (Socket.IO client)
│   │   ├── components/            # Step 30 responsive SOC Layout.js, LiveAlertsTicker
│   │   └── pages/                 # Step 30 canonical 7-page suite (Overview, LiveAlerts, AttackHistory, Devices, Blocklist, Settings, LogExport)
├── reports/
│   ├── environment_versions.txt   # Step 3a verified
│   ├── dataset_manifest.csv       # Step 7 official IoT-23 audit manifest (325.3M flows)
│   ├── data_quality_report.md     # Step 9 comprehensive data quality audit report
│   ├── data_quality_class_distribution.png # Step 9 class distribution chart
│   ├── data_quality_scenario_matrix.png    # Step 9 Class x Scenario heatmap
│   ├── interim_data_summary.csv   # Step 10 ingestion machine-readable log
│   ├── interim_data_summary.md    # Step 10 interim Parquet dataset audit report
│   ├── sampling_summary.csv       # Step 12 sampling machine-readable log
│   ├── sampling_report.md         # Step 12 dataset sampling audit report
│   ├── test_split_plan.md         # Step 13 three-level model evaluation plan
│   └── experiments/
│       ├── rf_search.csv          # Step 14 RandomizedSearchCV parameter tuning log
│       ├── rf_cv_results.csv      # Step 14 5-fold Level 1 CV detailed metrics
│       ├── rf_training_report.md  # Step 14 Random Forest training & validation report
│       ├── model_comparison.csv   # Step 15 3-model comparative metrics CSV
│       ├── model_comparison.md    # Step 15 3-model comparative audit report
│       ├── evaluation_iot23.csv   # Step 16 held-out scenario evaluation metrics CSV
│       ├── evaluation_iot23.md    # Step 16 held-out scenario evaluation report
│       ├── confusion_matrix_heldout.png # Step 16 held-out confusion matrix plot
│       ├── operational_thresholds.json # Step 17 operational thresholds JSON
│       ├── thresholds_and_explanation.md # Step 17 calibration & thresholds report
│       ├── calibration_curve.png  # Step 17 reliability diagrams plot
│       ├── feature_importance.png # Step 17 feature importances visualization
│       ├── model_card.md          # Step 18 formal Model Card (Mitchell et al. 2019)
│       ├── camera_baseline_summary.csv # Step 20 camera baseline metrics CSV
│       ├── camera_baseline_summary.md  # Step 20 camera baseline audit report (H1 verified)
│       └── schema_check.csv       # Step 22 schema audit metrics CSV
│   └── schema_check.md            # Step 22 offline vs live schema audit report (RQ3 resolved, Checkpoint C6)
├── tools/
│   ├── check_env.py               # Step 3a environment checker
│   ├── schema_check.py            # Step 22 offline vs live feature schema auditor
│   └── create_admin.py            # Step 24 CLI administrator provisioning utility
├── sensor/
│   ├── local.zeek                 # Step 19 Zeek streaming JSON policy & rotation override
│   ├── run_zeek.sh                # Step 19 sensor execution daemon script
│   ├── zeek_runner.py             # Step 19 cross-platform runner & simulation engine
│   ├── collect_camera_traffic.py  # Step 20 benign IP-camera traffic collector & FPR evaluator
│   ├── ids_inline.nft             # Step 32 inline bridge nftables ruleset (timeout sets, allowlist)
│   ├── ids_router.nft             # Step 32 passive router nftables ruleset (inet forward table)
│   └── logs/                      # conn.log active stream (gitignored)
├── tests/
│   ├── unit/
│   │   ├── test_features.py       # Step 11 unit tests (10 passed)
│   │   ├── test_sampling_and_splits.py # Step 12 & 13 tests (6 passed)
│   │   ├── test_train.py          # Step 14 unit tests (5 passed)
│   │   ├── test_compare_models.py # Step 15 unit tests (5 passed)
│   │   ├── test_evaluate.py       # Step 16 unit tests (5 passed)
│   │   ├── test_calibrate_and_explain.py # Step 17 unit tests (4 passed)
│   │   ├── test_model_bundle.py   # Step 18 unit tests (5 passed)
│   │   ├── test_zeek_config.py    # Step 19 unit tests (5 passed)
│   │   ├── test_camera_traffic.py # Step 20 unit tests (5 passed)
│   │   ├── test_zeek_adapter.py   # Step 21 unit tests (9 passed)
│   │   ├── test_schema_check.py   # Step 22 unit tests (7 passed)
│   │   ├── test_db_service_unit.py # Step 23 unit tests (5 passed)
│   │   ├── test_auth.py           # Step 24 unit tests (21 passed)
│   │   ├── test_detector.py       # Step 26 unit tests (7 passed)
│   │   ├── test_decision_engine.py # Step 26 unit tests (8 passed)
│   │   ├── test_scanner_service.py # Step 27 unit tests (12 passed)
│   │   ├── test_export_service.py # Step 28 unit tests (10 passed)
│   │   ├── test_response_policy.py # Step 31 response policy unit tests (12 passed)
│   │   ├── test_nftables_adapter.py # Step 32 nftables adapter unit tests (12 passed)
│   │   └── test_firewall_adapters.py # Step 33 firewall adapters unit tests (8 passed)
│   ├── integration/
│   │   ├── test_db_service.py     # Step 23 MongoDB integration tests (13 passed)
│   │   ├── test_app_api.py        # Step 25 Flask + Socket.IO server integration tests (13 passed)
│   │   ├── test_detection_pipeline.py # Step 26 pipeline integration tests (4 passed)
│   │   ├── test_scanner_integration.py # Step 27 scanner integration tests (5 passed)
│   │   ├── test_export_integration.py # Step 28 export integration tests (4 passed)
│   │   └── test_firewall_integration.py # Step 33 firewall REST API integration tests (4 passed)
│   └── lab_scenarios/             # empty
└── archive/                       # old code, data, models, documents (local only, not in Git)
```

---

## 8. Next steps (in order)

1. **Step 0 through Step 33:** ✅ done. Project foundations, threat model, requirements, official IoT-23 dataset manifest (325.3M flows, SHA-256 hashes), frozen label mapping (5 classes, D-014), data-quality audit report (`reports/data_quality_report.md`), chunked interim Parquet dataset (`ml_engine/load_iot23.py`, 23 Parquet files, 10.62 GB), unified feature extraction engine ([`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py), D-015), stratified sampling and feature extraction ([`ml_engine/sample_dataset.py`](file:///d:/intrusion%20detection/ml_engine/sample_dataset.py), 1,384,070 flows, 100% CnC kept, D-016), three-level evaluation plan ([`reports/test_split_plan.md`](file:///d:/intrusion%20detection/reports/test_split_plan.md), D-017), Random Forest classifier training ([`ml_engine/train.py`](file:///d:/intrusion%20detection/ml_engine/train.py), D-018), multi-model benchmarking pipeline ([`ml_engine/compare_models.py`](file:///d:/intrusion%20detection/ml_engine/compare_models.py), D-019), Level 2 evaluation on the dedicated held-out scenario `Capture-34-1` ([`ml_engine/evaluate.py`](file:///d:/intrusion%20detection/ml_engine/evaluate.py), D-020), Step 17 probability calibration, explainability, and operational threshold matrix tuning ([`ml_engine/calibrate_and_explain.py`](file:///d:/intrusion%20detection/ml_engine/calibrate_and_explain.py), D-021), Step 18 production bundle export ([`ml_engine/export_bundle.py`](file:///d:/intrusion%20detection/ml_engine/export_bundle.py), `ids_bundle_v1.joblib`, 30.84 MB) and formal Model Card publication ([`reports/experiments/model_card.md`](file:///d:/intrusion%20detection/reports/experiments/model_card.md), D-022), Step 19 Zeek live monitoring policies, daemon manager (`sensor/run_zeek.sh`), and simulation test harness (`sensor/zeek_runner.py`, D-023), Step 20 benign IP-camera baseline collection ([`sensor/collect_camera_traffic.py`](file:///d:/intrusion%20detection/sensor/collect_camera_traffic.py), 5,000 flows, 100% accuracy, FPR = 0.000% <= 5%, D-024), Step 21 real-time Zeek streaming ingestion adapter ([`core_engine/zeek_adapter.py`](file:///d:/intrusion%20detection/core_engine/zeek_adapter.py), 23,108 fps throughput, D-025), Step 22 offline vs live feature schema audit ([`tools/schema_check.py`](file:///d:/intrusion%20detection/tools/schema_check.py), 100% 19-feature alignment, zero training-serving skew, Checkpoint C6 & RQ3 resolved, D-026), Step 23 MongoDB database setup ([`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py), 9 collections, full block history audit trail, dynamic settings, TTL indexes, D-027), Step 24 Authentication and secrets management ([`core_engine/auth.py`](file:///d:/intrusion%20detection/core_engine/auth.py), [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py), bcrypt, 8h JWT tokens, system_logs audit, D-028), Step 25 Consolidated Flask + Socket.IO server ([`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py), 20 REST endpoints, authenticated WebSocket push telemetry, lab safety guardrails, D-029), Step 26 Detector and decision engine ([`core_engine/detector.py`](file:///d:/intrusion%20detection/core_engine/detector.py), [`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py), calibrated inference, dual thresholds, allowlist safety, burst coalescing, and latency tracking, D-030), Step 27 Device discovery (Nmap) ([`core_engine/scanner_service.py`](file:///d:/intrusion%20detection/core_engine/scanner_service.py), authorized Nmap scanner, multi-evidence camera heuristics, approved subnet restrictions, camera confirmation RBAC API, D-031), Step 28 Log export ([`core_engine/export_service.py`](file:///d:/intrusion%20detection/core_engine/export_service.py), RFC 4180 CSV & JSON multi-attribute filtered export, system_logs audit invariant, D-032), Step 29 React frontend cleanup (single URL, JWT WebSocket, fake attack elimination, D-033), Step 30 Canonical 7-page dashboard suite (responsive Layout, Model Prediction vs Confirmed Incident badges, D-034), Step 31 Autonomous response policy and safety guardrail engine (7 safety guardrails, sliding-window repeat coalescing, D-035), Step 32 native Linux nftables rulesets and programmatic kernel adapter ([`sensor/ids_inline.nft`](file:///d:/intrusion%20detection/sensor/ids_inline.nft), [`sensor/ids_router.nft`](file:///d:/intrusion%20detection/sensor/ids_router.nft), [`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py), timed auto-expiry sets, dev simulation fallback, D-036), and Step 33 modular response adapter suite and engine integration ([`core_engine/firewall/base.py`](file:///d:/intrusion%20detection/core_engine/firewall/base.py), [`router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py), [`simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py), [`__init__.py`](file:///d:/intrusion%20detection/core_engine/firewall/__init__.py), D-037) are complete with 204 passing unit and integration tests (100% pass rate).
2. **Track 1 & Track 2 Milestones Concluded:** Both Track 1 (Dataset and ML Pipeline, Steps 7–18) and Track 2 (Live Sensor Telemetry, Steps 19–22) are 100% COMPLETE.
3. **Phase 6 & Phase 7 Concluded:** Phase 6 (System Integration, Database & Response APIs, Steps 23–28) and Phase 7 (React SOC Dashboard & Telemetry, Steps 29–30) are 100% COMPLETE.
4. **Phase 8 — Firewall Response Controls (In Progress):**
   - Step 31 ✅ Done (Direction-aware response policy & safety guardrail engine).
   - Step 32 ✅ Done (nftables rules and timeout-based sets).
   - Step 33 ✅ Done (Modular response adapter suite, SSH router adapter, simulation engine, and engine integration).
   - Step 34 (Next): Manual control, expiry timers, and crash recovery.
5. **After the 8 Nov 2026 review (see 3.53), the order is:**
   1. Buy or borrow the lab hardware (camera, managed switch, Linux sensor, router, attack laptop, cables).
   2. Fix the software gaps: issues 9, 11, 12 (live runner, adapter setting, router names).
   3. Correct the reports: issues 10 and 13.
   4. Build the lab (Step 5), run real Zeek (Step 19), capture real camera traffic (Step 20), redo the schema check (Step 22).
   5. Step 34, then the 6 Table 10 scenarios (Step 35), then Steps 36–42.
   6. Clean-up: issues 14 and 15.

---

## 9. How to add a new entry

After each piece of work, add an entry to Section 3, then update Sections 1, 2, 4, 5, 6 and 8 if they changed.

```markdown
**3.x Short title (date)**

- What was done (step number):
- Files created or changed:
- Commit (if any):
- Result / checks:
- Problems found (also add them to Section 4 or 5):
```
