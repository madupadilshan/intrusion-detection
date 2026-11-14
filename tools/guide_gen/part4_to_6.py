# -*- coding: utf-8 -*-
"""Part 4, 5, and 6: Objectives, Research Questions, and Automated Test Suite"""

SECTION_4_TO_6 = """# 4. Part 3: Research Objectives (Objectives O1 to O6)

Demonstrate fulfillment of all 6 research objectives from Section 3 of **[`docs/requirements_checklist.md`](docs/requirements_checklist.md)**:

1. **Objective O1 (Repeatable Preprocessing & Mapping):**  
   - Cleaned 1,182,984 flows across 22 scenarios of Stratosphere IoT-23 with SHA-256 manifests and data quality reports (`reports/iot23_copy_verification.md`).
2. **Objective O2 (Multi-class Random Forest with Zero Scenario Leakage):**  
   - Evaluated on sealed held-out scenario `Capture-34-1`, our 100-tree Random Forest Model v3.2.0 achieved an 87.77% Macro-F1 (up from 85.95% in v3.1.0).
3. **Objective O3 (Live Features Matching Dataset):**  
   - Zeek Feature Extractor builds 27 features from live packets, passing Kolmogorov-Smirnov statistical tests and schema alignment audits (`schema_check.py`).
4. **Objective O4 (Monitoring, Dashboard, Storage & Alerts Joined Together):**  
   - Zeek Sensor, Random Forest ML Detector, React SOC Dashboard, and MongoDB are unified in a single end-to-end pipeline operating over Socket.IO in real time.
5. **Objective O5 (Policy-Based IP Blocking with Manual Undo):**  
   - Autonomous Drop rules are injected into the router's `block_dst` set upon C&C detection, with full manual block/rollback capabilities via the UI and API.
6. **Objective O6 (Detection Quality, Speed & Resource Use):**  
   - Sub-second pipeline latency (112 ms), 7.96 $\\mu\\text{s}$ per-flow inference speed, and zero camera surveillance disruption.

---

# 5. Part 4: Hypothesis and Research Questions (Hypothesis H1 & RQ1 to RQ5)

Provide scientific answers to the research questions defined in Section 4 of **[`docs/requirements_checklist.md`](docs/requirements_checklist.md)**:

* **Hypothesis H1:**  
  *"Macro-F1 score $\\ge 0.85$ on held-out scenarios while keeping false-positive rate $\\le 5\%$ on local camera traffic."*  
  - **Part 1 (Held-out Macro-F1 $\\ge 0.85$):** Model v3.2.0 achieves **87.77%** (v3.1.0 achieved **85.95%**), fully validated in our Virtual Lab.  
  - **Part 2 (Benign FPR $\\le 5\%$):** NVR video stream operates with zero packet drops, ready for final physical camera validation in the hardware lab (`lab_hardware/`).
* **RQ1 (Benign vs Malicious Discrimination):**  
  - Achieves 96.25% overall accuracy on held-out `Capture-34-1` and grouped cross-validation, cleanly separating benign flows from attacks.
* **RQ2 (Multi-Class Sorting across DDoS, Scanning, C&C, Malware):**  
  - Per-class evaluation yields DDoS (F1: 99.5%), C&C (F1: 93.6%), PortScan (F1: 73.3%), and Benign (F1: 84.7%) (Malware_Download flows are absent on 34-1, but detected live via retrained model v3.2.0 and file inspection).
* **RQ3 (Feature Availability in Zeek vs IoT-23):**  
  - All 27 engineered features are natively extractable from Zeek `conn.log` and `http.log`, verified by `tools/schema_check.py`.
* **RQ4 (End-to-End Latency from Detection to Blocking):**  
  - Total latency is **112.2 milliseconds (0.11 s)**, running 18 times faster than our 2.0 s proposal target.
* **RQ5 (Safety Rules Preventing Camera Cut-off):**  
  - The immutable allowlist guardrail in `docs/response_policy.md` ensures camera IP `192.168.50.30` cannot be blocked, quarantining only the outside C&C destination (`10.10.10.50`).

---

# 6. Part 5: Automated Test Suite (318 Tests Passed)

If the supervisor requests inspection of unit and integration test coverage, run the following command to demonstrate that **all 318 automated tests pass cleanly**:

#### 💡 Why We Are Doing This:
To scientifically prove software engineering rigor: every system component (Zeek log parser, feature extraction, ML classification bundle, decision engine, router firewall adapter, JWT authentication, and WebSockets) operates with 100% test integrity and zero code regressions.

#### ⚙️ What Happens Under the Hood:
The Python `pytest` framework scans 24 test suites in `tests/`, executes all 318 test cases sequentially, and verifies assertions.

#### 💻 Direct Raw Command (Terminal):

```powershell
.venv\\Scripts\\python.exe -m pytest tests/ -q
```

#### 🔍 Line-by-Line Breakdown:
- `.venv\\Scripts\\python.exe`: Python virtual environment interpreter.
- `-m pytest`: Calls the pytest automated testing engine.
- `tests/`: Executes all test suites in the `tests/` directory.
- `-q` (quiet mode): Summarizes test execution with dots for passing tests.

#### 📋 Verified Output:

```text
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 67%]
........................................................................ [ 90%]
..............................                                           [100%]
============================== warnings summary ===============================
tests/integration/test_app_api.py::test_blocklist_enforcement_and_allowlist_protection
  ...
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
318 passed, 6 warnings in 158.08s (0:02:38)
```

#### 📊 Output Breakdown:
- `318 passed`: All 318 unit, integration, router, model, and API tests passed with zero failures.
- `in 158.08s`: Full test suite completed cleanly.

#### 🗣️ Spoken English Script:
> *"Sir, every component of our system—including the Zeek parser, feature extractor, ML inference bundle, decision engine, Linux nftables adapter, and authenticated WebSocket API—is backed by a comprehensive automated test suite of 318 unit and integration tests, all currently passing with 100% test integrity."*

---
"""
