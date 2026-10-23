# Requirements and Research Objectives Checklist

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**Team:** Group 03 — University of Sri Jayewardenepura  
**Based on:** Research Proposal Sections 1.3, 1.5, 3.1, 3.7; Tables 3, 7, 9, 10  
**Document Version:** 1.0  
**Date:** 23 October 2026  

---

## 1. Functional Requirements Checklist (Proposal Table 7)

Every functional requirement from the July 2026 proposal is listed below with its priority, verification test, and implementation status.

| ID | Functional Requirement | Priority | Verification Method | Associated Step | Status |
|:---:|---|:---:|---|:---:|:---:|
| **FR-01** | Capture mirrored or inline traffic and generate standardized network connection flows (`conn.log`). | **MUST** | Feed PCAP or live mirror stream into Zeek; verify flow field completeness. | Step 19, 21 | ⬜ In Progress |
| **FR-02** | Classify each usable flow into predefined attack categories; return class label, confidence score, and model version. | **MUST** | Automated inference test using pipeline bundle (`ids_bundle_v1.joblib`). | Step 14, 18, 26 | ⬜ In Progress |
| **FR-03** | Persist benign traffic summaries, detected attack events, and mitigation actions into MongoDB with TTL expiration. | **MUST** | Database unit tests verifying collection schema, document writes, and TTL index expiration. | Step 23 | 🟡 Implemented (`db_service.py`) |
| **FR-04** | Stream real-time alerts and telemetry to a secure, authenticated React dashboard via WebSockets without page reload. | **MUST** | Socket.IO event latency test; JWT login and token expiration verification. | Step 25, 29, 30 | ⬜ In Progress |
| **FR-05** | Discover approved network devices, active services, and open RTSP/HTTP ports using controlled Nmap scanning. | **SHOULD** | Run Nmap discovery on approved subnet (`192.168.50.0/24`); verify devices collection output. | Step 27 | ⬜ In Progress |
| **FR-06** | Dynamically insert, query, expire, and retract firewall blocking rules on the router or sensor firewall (`nftables`). | **MUST** | Automated rule insertion, drop verification, and TTL auto-expiry test in separated lab. | Step 31, 32, 33 | ⬜ In Progress |
| **FR-07** | Enforce safety policies: static management allowlists, minimum confidence threshold ($\ge 0.85$), repetition count, and immutable audit logs. | **MUST** | Unit test simulating attack from allowlisted IP; verify rejection of blocking command. | Step 4, 31 | 🟡 In Progress (`settings.yaml` ready) |
| **FR-08** | Export filtered attack logs and evaluation telemetry in CSV and JSON formats for audit and research reporting. | **SHOULD** | API export endpoint test; verify CSV format compliance against saved MongoDB events. | Step 28 | ⬜ In Progress |

*Priority Definitions:*
- **MUST:** Mandatory core requirement. The research prototype is not complete without it.
- **SHOULD:** Highly important feature providing significant operational value.

---

## 2. Non-Functional Requirements (NFR)

| ID | Non-Functional Requirement | Target Metric (Proposal Table 9) | Verification Method | Status |
|:---:|---|---|---|:---:|
| **NFR-01** | **Detection Latency:** Time from flow completion to alert on dashboard. | $< 2.0$ seconds | Automated timestamp delta measurement (`measure_latency.py`). | ⬜ Pending Step 37 |
| **NFR-02** | **Resource Footprint:** Memory and CPU utilization on the sensor node. | $< 1.0$ GB RAM usage; $< 50\%$ CPU under normal flow rates | `psutil` resource monitor logging during streaming and attack tests. | ⬜ Pending Step 37 |
| **NFR-03** | **Zero Data Leakage:** Strict separation between training scenarios and evaluation scenarios. | Scenario-level grouping; StratifiedGroupKFold; held-out scenario test | Automated split validator checking scenario ID isolation. | ⬜ Pending Step 13 |
| **NFR-04** | **Detection Precision & Low False Positives:** Avoid blocking legitimate surveillance traffic. | Macro-F1 $> 0.90$; False Positive Rate (FPR) on benign camera flows $< 1.0\%$ | Confusion matrix and ROC-AUC evaluation on held-out and local flows. | ⬜ Pending Step 16 |
| **NFR-05** | **Reproducibility:** Experiments and model outputs must be scientifically reproducible. | Fixed `random_seed: 42`, locked `requirements.txt`, dataset SHA-256 hashes | Re-running training pipeline produces identical weights and metrics. | ✅ Verified (Steps 3a, 4) |

---

## 3. Research Objectives Checklist (Proposal Table 3)

| Objective | Description | Target Deliverable | Progress / Status |
|:---:|---|---|:---:|
| **O1** | Design and prepare a standardized, reproducible flow-based dataset pipeline using official IoT-23 captures. | Manifest script with SHA-256 hashes; cleaning and feature engineering modules (`features.py`). | 🟡 In Progress (Steps 7–12) |
| **O2** | Train, optimize, and cross-validate multi-class machine learning classifiers (Random Forest, Gradient Boosting, Logistic Regression) with zero scenario leakage. | Validated model bundle (`ids_bundle_v1.joblib`), performance comparison tables, calibration curves. | ⬜ Pending Steps 13–18 |
| **O3** | Develop a live Zeek ingestion adapter matching offline feature schema without artificial packet padding. | `zeek_adapter.py` and offline-vs-live schema checker (`schema_check.py`). | ⬜ Pending Steps 19–22 |
| **O4** | Construct an authenticated backend API and real-time React dashboard for visual monitoring and alert dispatch. | Flask + Socket.IO server (`app.py`), MongoDB service (`db_service.py`), React UI (`my-app`). | 🟡 Started (Step 23 draft complete) |
| **O5** | Implement an automated, safety-constrained mitigation mechanism with allowlists, thresholds, and auto-expiry. | Firewall adapters (`nftables_adapter.py`, `router_adapter.py`, `simulation_adapter.py`), policy tests. | 🟡 Started (`settings.yaml` allowlist defined) |
| **O6** | Empirically evaluate detection accuracy, mitigation latency ($<2$s), and sensor resource consumption in a controlled lab testbed. | Comprehensive evaluation report with Table 10 scenario benchmarks and final thesis analysis. | ⬜ Pending Steps 35–40 |

---

## 4. Research Questions & Hypothesis Alignment

* **Hypothesis (H1):**  
  > *"A flow-based machine learning intrusion detection and dynamic response architecture can classify malicious IoT IP-camera traffic with macro-F1 $\ge 0.90$, maintain false positive rates below $1.0\%$ on camera flows, and trigger automated mitigations in under $2.0$ seconds without disrupting legitimate video operations."*
  * *Verification Status:* Tested through Objectives O2, O5, and O6 in Steps 16, 35, and 37.

* **Research Questions:**
  * **RQ1 (Feature Discriminability):** Which flow features extracted by Zeek best distinguish IoT attacks from normal video streaming? ➔ *Addressed in Steps 11, 14, and 17.*
  * **RQ2 (Model Generalizability):** Does a Random Forest classifier trained on IoT-23 generalize to held-out scenarios and distinct camera hardware without scenario leakage? ➔ *Addressed in Steps 13, 16, and 20.*
  * **RQ3 (Real-Time Ingestion):** Can live Zeek connection flows be parsed and classified in under 2 seconds on edge hardware? ➔ *Addressed in Steps 21, 26, and 37.*
  * **RQ4 (Response Safety):** Do static allowlists, confidence thresholds ($\ge 0.85$), and repetition checks prevent unintended disruption of legitimate camera streaming? ➔ *Addressed in Steps 4, 31, and 35.*
  * **RQ5 (Resource Overhead):** Can the complete IDS sensor stack operate within 1.0 GB RAM on resource-constrained hardware? ➔ *Addressed in Steps 3b and 37.*

---

## 5. Summary Status

* **Total Functional Requirements:** 8 (6 MUST, 2 SHOULD)
* **Total Research Objectives:** 6 (O1 to O6)
* **Foundational Steps Complete:** Steps 0, 1, 2, 3a/3d, 4, 6 (100% Foundation Complete)
* **Next Immediate Milestone:** Step 7 (Download official IoT-23 dataset and generate SHA-256 manifest)
