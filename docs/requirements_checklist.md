# Requirements and Objectives Checklist

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Team:** Group 03 — University of Sri Jayewardenepura
**Based on:** proposal Sections 1.5, 3.7, 5.1; Tables 3, 7, 9, 10
**Version:** 3.1 · **Date:** 11 November 2026 (full check against the proposal; corrections in D-056) · version 3.0: 8 November 2026

**Status words used here:**
- **Built** — the code exists and its unit/integration tests pass on the development PC.
- **Verified** — checked the way the proposal says (Table 7 "how we check", Table 9 target), with real data or in the lab.
- **Not started** — nothing yet.

Numbers are not copied into this file. They are in the result files named in each row, so this file cannot go out of date.

---

## 1. Functional requirements (proposal Table 7)

| ID | Requirement (proposal) | How the proposal checks it | What exists | Status |
| --- | --- | --- | --- | --- |
| FR-01 | Capture mirrored or inline traffic, and make connection flows from it. | Must / schema test | `sensor/local.zeek`, `sensor/run_zeek.sh`, `core_engine/zeek_adapter.py`, `core_engine/runner.py`, `tools/schema_check.py`, `lab_hardware/` | **Built.** Runs on real Zeek in the virtual lab (D-053). Schema test on real camera traffic pending (Steps 19, 22; `tools/fr_tests.py` FR-01). |
| FR-02 | Put each usable flow into a class; give back the class, the confidence and the model version. | Must / model API test | `core_engine/detector.py`, `ml_engine/models/ids_bundle_v3.joblib` | **Built and tested** (unit tests). |
| FR-03 | Save benign traffic summaries, attacks and response actions. | Must / database test | `core_engine/db_service.py` (TTL retention), `decision_engine.py` | **Built and tested** (integration tests with MongoDB). |
| FR-04 | Send new events and alerts to the dashboard, which needs a login, without pressing refresh. | Must / Socket.IO latency test | `core_engine/app.py` (Socket.IO with JWT; `summary_update`, `new_event`, `event_update`, `blocklist_update`, `device_update`, `scan_progress`, `settings_update`, `log_export`), `my-app/` pages | **Built and tested** (`tests/integration/test_live_dashboard.py`). Fixed 11 Nov 2026: the Overview never got live numbers (D-056). Latency test: `tools/measure_latency.py` (Step 37). |
| FR-05 | Find approved devices and services with controlled Nmap scans. | Should / inventory test | `core_engine/scanner_service.py` (approved subnet only, admin only) | **Built and tested** with a mocked Nmap; real inventory test in the lab pending. |
| FR-06 | Add, list, expire and remove blocking rules on the firewall or router. | Must / test on a separated network | `core_engine/firewall/` (router, nftables, simulation), `sensor/ids_router.nft`, `sensor/ids_inline.nft` | **Built.** Tested on a real nftables router in the virtual lab (D-053; blocks, rate-limits (D-055), expiry). Hardware-lab test: `tools/fr_tests.py` FR-06 and `hwlab.py reliability expiry`. |
| FR-07 | Keep the allowlists, the confidence thresholds and a full audit history. | Must / safety test | `core_engine/response_policy.py`, settings API with change history, audit log (`system_logs`) | **Built and tested.** Since 11 Nov 2026 confirming an incident and changing a setting are also audited (D-056). Lab safety test pending (Step 35). |
| FR-08 | Export filtered attack logs for testing and reporting. | Should / export test | `core_engine/export_service.py`, `GET /api/logs/export` | **Built and tested.** |

## 2. Targets of proposal Table 9

| What we test | Target | Current state | Where |
| --- | --- | --- | --- |
| Classification | Macro-F1 ≥ 0.85 on the scenario we left out; report all results either way | `CTU-IoT-Malware-Capture-34-1`, v3.1.0: **0.8595** over the classes present (the H1 number, D-054), 0.6876 over 5 classes. 34-1 was seen before: **not a clean test** | `reports/experiments/model_card.md`, `evaluation_iot23.md`, `thresholds_and_explanation.md` |
| Benign safety | FPR ≤ 5% on local camera traffic; no blocks on the management computer or the NVR | **Not measured.** Only synthetic test data exists (D-042) | Step 20 (real capture), Step 35 |
| Latency | Median decision < 2 s; 95th percentile < 5 s under target load | **Not measured.** Only the model step was timed on the PC (microseconds) | Step 37 |
| Throughput / resources | Keeps up with the measured lab traffic; no important event lost | **Not measured** | Step 37 |
| Reliability | All important recovery tests pass | **Not started** | Steps 34, 38 |
| Usability / audit | Admin can finish the set tasks; every action can be traced | **Not started** | Step 39 |

## 3. Objectives (proposal Table 3)

| ID | Objective | How we show it | Status |
| --- | --- | --- | --- |
| O1 | Repeatable IoT-23 preprocessing and label-mapping pipeline | Dataset check, code with versions, data-quality report | **Done.** Copy checked against the official files (`reports/iot23_copy_verification.md`, D-039); manifest with SHA-256; frozen mapping; data-quality report. |
| O2 | Multi-class Random Forest with no scenario leakage | Grouped CV, scores from a left-out scenario | **Done** (method). Scores are reported as measured and are below the H1 target. |
| O3 | Live features that match the dataset | Schema check, offline vs live features | **Not done.** The tool is ready; it must run on real Zeek output (Steps 19, 20, 22). |
| O4 | Monitoring, dashboard, storage and alerts joined together | Whole-system tests, measured time to update | **Built.** Whole-system test and update time in the lab pending (Steps 35–37). |
| O5 | Policy-based IP blocking with manual undo | Approved lab tests, audit log, unblock check | **Built.** Lab tests pending (Steps 34–35). |
| O6 | Detection quality, speed and resource use | Macro-F1, per-class recall, FPR, response time, resource use | **Partly.** Offline detection results exist; FPR, response time and resources need the lab (Steps 35–40). |

## 4. Hypothesis and research questions

**H1 (proposal 1.5):** "If the IoT-23 flow features are mapped carefully and the Random Forest is trained in a scenario-aware way, then the model will reach a macro-F1 score of at least 0.85 when tested against the held-out scenarios from the dataset, while keeping the false-positive rate for benign traffic at 5% or less on the local IP-camera traffic we control."

- Part 1 (macro-F1 ≥ 0.85 on the held-out scenario): 0.8595 over the classes present on 34-1 (D-054). 34-1 is not a clean test, because it was seen and studied before; the lab results must confirm it. See the model card.
- Part 2 (FPR ≤ 5% on local camera traffic): **not tested yet.**
- So H1 is **not confirmed**. The proposal (1.5) asks us to use the per-class metrics, the schema check and the scenario-aware validation to find which reason applies (domain shift, feature mismatch, or too few examples).

| RQ | Question (proposal 1.5) | State |
| --- | --- | --- |
| RQ1 | How well can the chosen model tell benign traffic apart from malicious IoT flows under scenario-aware validation? | Offline answer available (grouped CV and 34-1, per-class results). |
| RQ2 | How well can it sort traffic into the DDoS, scanning, C&C and malware/download classes? | Offline answer available (per-class precision/recall/F1, confusion matrix). |
| RQ3 | Which flow features stay available and stay the same in both IoT-23 and live camera traffic made by Zeek? | **Open** — needs real Zeek output (Step 22). |
| RQ4 | How much time does the whole process take in the laboratory, from detection to dashboard, alert and blocking? | **Open** — Step 37. The code records the timestamps of every stage. |
| RQ5 | What safety rules do we need so that automatic response does not stop normal camera access? | Rules designed and built (`docs/response_policy.md`); lab evidence pending (Step 35). |

## 5. Automated tests

Run `python -m pytest -q` in the project folder. The suite tests each part on the development PC. Passing tests do **not** replace the lab tests above.
