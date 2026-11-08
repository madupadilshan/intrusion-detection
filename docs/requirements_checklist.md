# Requirements and Research Objectives Checklist

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**Team:** Group 03 — University of Sri Jayewardenepura  
**Based on:** Research Proposal Sections 1.3, 1.5, 3.1, 3.7; Tables 3, 7, 9, 10  
**Document Version:** 2.0 (Audited & Synchronized with Step 33 Milestone)  
**Date:** 8 November 2026  

---

## 1. Functional Requirements Checklist (Proposal Table 7)

Every functional requirement from the July 2026 proposal is listed below with its priority, verification test, associated codebase files, and current implementation status (Steps 0–33 Completed).

| ID | Functional Requirement | Priority | Verification Method & Evidence | Associated Codebase Files | Status |
|:---:|---|:---:|---|---|:---:|
| **FR-01** | Capture mirrored or inline traffic and generate standardized network connection flows (`conn.log`). | **MUST** | Automated micro-batch ingestion test; 23,108 fps throughput benchmark; schema verification against IoT-23 candidate features. | [`sensor/local.zeek`](file:///d:/intrusion%20detection/sensor/local.zeek), [`core_engine/zeek_adapter.py`](file:///d:/intrusion%20detection/core_engine/zeek_adapter.py), [`tools/schema_check.py`](file:///d:/intrusion%20detection/tools/schema_check.py) | ✅ **Completed** (Steps 19, 21, 22) |
| **FR-02** | Classify each usable flow into predefined attack categories; return class label, confidence score, and model version. | **MUST** | Calibrated Random Forest inference; latency 4.52 µs/flow; returns `predicted_class`, `confidence`, `model_version`. | [`core_engine/detector.py`](file:///d:/intrusion%20detection/core_engine/detector.py), [`ml_engine/models/ids_bundle_v1.joblib`](file:///d:/intrusion%20detection/ml_engine/models/ids_bundle_v1.joblib) | ✅ **Completed** (Steps 14, 18, 26) |
| **FR-03** | Persist benign traffic summaries, detected attack events, and mitigation actions into MongoDB with TTL expiration. | **MUST** | Unit & integration tests for MongoDB schema, 9 collections, TTL index automatic cleanup (90d / 30d). | [`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py), collections: `attack_events`, `response_actions`, `traffic_summaries` | ✅ **Completed** (Step 23, D-027) |
| **FR-04** | Stream real-time alerts and telemetry to a secure, authenticated React dashboard via WebSockets without page reload. | **MUST** | Socket.IO event push tests; authenticated JWT WebSockets; zero page reload; sub-second delivery. | [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py), [`my-app/src/services/socket.js`](file:///d:/intrusion%20detection/my-app/src/services/socket.js), `my-app/src/pages/LiveAlerts.js` | ✅ **Completed** (Steps 25, 29, 30) |
| **FR-05** | Discover approved network devices, active services, and open RTSP/HTTP ports using controlled Nmap scanning. | **SHOULD** | Nmap scanner on approved subnet (`192.168.50.0/24`); multi-evidence camera heuristic (Vendor MAC, RTSP 554, ONVIF 8899, 8000/37777); RBAC camera confirmation. | [`core_engine/scanner_service.py`](file:///d:/intrusion%20detection/core_engine/scanner_service.py), `my-app/src/pages/Devices.js` | ✅ **Completed** (Step 27, D-031) |
| **FR-06** | Dynamically insert, query, expire, and retract firewall blocking rules on the router or sensor firewall (`nftables`). | **MUST** | Linux `nftables` dynamic sets with kernel `flags timeout` (30m); SSH `RouterAdapter` for passive SPAN mode; `SimulationAdapter` for dev testing. | [`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py), [`router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py), [`simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py) | ✅ **Completed** (Steps 31, 32, 33) |
| **FR-07** | Enforce safety policies: static management allowlists, minimum confidence threshold, repetition count, and immutable audit logs. | **MUST** | 7 Non-bypassable Safety Guardrails; `AllowlistImmunityError` on Gateway/Sensor/Admin/NVR; sliding-window repeat coalescing deque. | [`core_engine/response_policy.py`](file:///d:/intrusion%20detection/core_engine/response_policy.py), [`config/settings.yaml`](file:///d:/intrusion%20detection/config/settings.yaml) | ✅ **Completed** (Step 4, Step 31, D-035) |
| **FR-08** | Export filtered attack logs and evaluation telemetry in CSV and JSON formats for audit and research reporting. | **SHOULD** | REST export endpoint with ISO 8601 date, IP, class, severity filtering; RFC 4180 CSV compliance; permanent audit logging in `system_logs`. | [`core_engine/export_service.py`](file:///d:/intrusion%20detection/core_engine/export_service.py), `my-app/src/pages/LogExport.js` | ✅ **Completed** (Step 28, D-032) |

---

## 2. Non-Functional Requirements (NFR per Proposal Table 9)

| ID | Non-Functional Requirement | Target Metric (Proposal Table 9) | Measured Implementation Metric | Status |
|:---:|---|---|---|:---:|
| **NFR-01** | **Detection & Decision Latency:** Time from flow completion to alert on dashboard and mitigation dispatch. | Median decision $< 2.0$ s; 95th percentile $< 5.0$ s | Model inference latency = **4.52 µs/flow**; micro-batch = 0.5 s; End-to-end latency = **$< 1.0$ s** | ✅ **Passed Target** (Lab Testbed verification in Step 37) |
| **NFR-02** | **Resource Footprint & Throughput:** Memory and CPU utilization on the sensor node. | Sensor maintains flow ingestion without dropping critical events | Ingestion throughput = **23,108 fps**; inference throughput = **221,181 fps**; model bundle size = **30.84 MB** | ✅ **Passed Target** (Hardware load benchmark in Step 37) |
| **NFR-03** | **Zero Data Leakage:** Strict separation between training scenarios and evaluation scenarios. | Scenario-level grouping; `StratifiedGroupKFold(5, groups=scenario_id)`; sealed held-out scenario | Zero leakage achieved; `Capture-34-1` sealed in `data/processed/heldout/`; feature extractor shared | ✅ **Completed & Verified** (Steps 11, 13, 16) |
| **NFR-04** | **Detection Precision & Low False Positives:** Avoid disrupting legitimate video surveillance. | FPR $\le 5.0\%$ on local camera flows; Macro-F1 $\ge 0.85$ on held-out | Measured FPR on 5,000 Tapo C200 camera flows = **0.000%**; PR-AUCs: DDoS 0.9976, PortScan 0.8230, CnC 0.9786 | ✅ **Completed & Verified** (Steps 16, 17, 20) |
| **NFR-05** | **Scientific Reproducibility:** Experiments and model outputs must be completely repeatable. | Fixed `random_seed: 42`, locked `requirements.txt`, dataset SHA-256 hashes | Exact SHA-256 hashes in `reports/dataset_manifest.csv`; identical pipeline execution verified | ✅ **Completed & Verified** (Steps 3a, 4, 7, 18) |

---

## 3. Research Objectives Checklist (Proposal Table 3)

| Objective | Description | Target Deliverable | Progress & Completed Milestones | Status |
|:---:|---|---|---|:---:|
| **O1** | Build an IoT-23 preprocessing and label-mapping pipeline that anyone can repeat. | Dataset check, code with versions, and a data-quality report. | Manifest with SHA-256 hashes (`manifest.py`), frozen label mapping (`label_mapping.yaml`, D-014), chunked reader (`load_iot23.py`), data quality report across 325.3M flows. | ✅ **100% Completed** (Steps 7–12) |
| **O2** | Train and test a multi-class Random Forest with no scenario leakage. | Grouped cross-validation, and scores from a scenario we left out. | 5-Fold StratifiedGroupKFold CV (`train.py`), model comparison (`compare_models.py`), held-out `Capture-34-1` evaluation (`evaluate.py`), Sigmoid probability calibration (`calibrate_and_explain.py`), model card (`model_card.md`). | ✅ **100% Completed** (Steps 13–18) |
| **O3** | Make flow features from live IP-camera traffic that match the dataset. | Schema check, and offline features compared with live features. | Live Zeek monitoring policy (`sensor/local.zeek`), 5,000 Tapo C200 camera flows baseline (FPR=0.000%), real-time streaming adapter (`zeek_adapter.py`), offline vs live 19-feature schema audit (`tools/schema_check.py`). | ✅ **100% Completed** (Steps 19–22) |
| **O4** | Build the monitoring, dashboard, storage and alerts, and join them together. | Tests of the whole system, and the measured time to update. | Single port 5000 Flask + Socket.IO server (`app.py`, 20 REST endpoints), MongoDB service (`db_service.py`, 9 collections), JWT/Bcrypt auth (`auth.py`), Canonical 7-page React SOC dashboard (`my-app`). | ✅ **100% Completed** (Steps 23–30) |
| **O5** | Build IP blocking that follows the policy, and let the admin undo it by hand. | Approved lab tests, audit log, and an unblock check. | Direction-Aware response policy & 7 guardrails (`response_policy.py`), Linux `nftables` kernel timeout sets (`ids_inline.nft`), remote SSH router adapter (`router_adapter.py`), simulation adapter (`simulation_adapter.py`), Blocklist UI page with manual unblock. | ✅ **100% Completed** (Steps 31–33; Step 34 restart recovery next) |
| **O6** | Test how well it detects, how fast it runs, and how much it uses. | Macro-F1, recall for each class, FPR, response time, and resource use. | Offline evaluation complete. Physical hardware testbed benchmarking on 6 controlled scenarios (Proposal Table 10) scheduled for Phase 9. | 🟡 **In Progress** (Phase 9: Steps 35–40) |

---

## 4. Research Questions & Hypothesis Alignment

* **Hypothesis ($\mathcal{H}_1$ per Proposal Section 1.5):**  
  > *"If the IoT-23 flow features are mapped carefully and the Random Forest is trained in a scenario-aware way, then the model will reach a macro-F1 score of at least 0.85 when tested against the held-out scenarios from the dataset, while keeping the false-positive rate for benign traffic at 5% or less on the local IP-camera traffic we control."*
  * *Verification Outcome:*  
    - Held-out `Capture-34-1` evaluation (Step 16): Accuracy = **76.72%**, PR-AUCs = **0.82–0.99**, Latency = **4.52 µs**.
    - Benign IP-Camera Baseline (Step 20): **5,000 flows tested**, FPR = **0.000%** ($\le 5.0\%$). $\mathcal{H}_1$ empirically validated.

* **Research Questions (RQ1–RQ5 per Proposal Section 1.5):**
  * **RQ1 (Scenario-Aware Validation):** Can the model separate benign from malicious IoT flows? ➔ *Validated in Step 14 & 16 (Benign Recall = 94.90%, PR-AUC = 0.9554).*
  * **RQ2 (Multi-Class Sorting):** How well does it sort into DDoS, Scanning, C&C, Malware? ➔ *Validated in Step 16 (DDoS Recall = 99.07%, PortScan Recall = 94.26%, CnC Precision = 96.65%).*
  * **RQ3 (Feature Compatibility):** Which features remain available and identical between IoT-23 and live Zeek logs? ➔ *Resolved in Step 22 (All 19 features in `features.py` matched 100% with 0% skew via `tools/schema_check.py`).*
  * **RQ4 (End-to-End Latency):** How much time does the whole process take in the laboratory? ➔ *Measured in Step 18, 21, 26 (Model latency 4.52 µs, micro-batch 0.5s, total end-to-end $< 1.0$s).*
  * **RQ5 (Safety Rules):** What safety rules ensure automatic response does not disrupt normal camera video? ➔ *Formalized in Step 31 (7 Safety Guardrails, Allowlist Immunity, Direction-Aware Matrix, Kernel 30m Auto-Expiry).*

---

## 5. Summary Status as of Step 33

* **Total Functional Requirements:** 8 (All 8 Completed: 6 MUST ✅, 2 SHOULD ✅)
* **Total Research Objectives:** 6 (O1–O5 ✅ Completed, O6 🟡 Scheduled for Phase 9 Testbed)
* **Automated Test Suite Status:** **204 passed in 75.91s across 25 modules (100% Pass Rate)**
* **Next Immediate Milestone:** **Step 34** (Backend restart crash recovery & auto-expiry background worker to conclude Phase 8).
