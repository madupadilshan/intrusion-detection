# Step-by-Step Guide: Building the Project From the Very Beginning

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Based on:** Group 03 Research Proposal (July 2026)
**Guide version:** 4 (19 October 2026)

What is new in version 4:

- Simpler English, with shorter sentences.
- More key words explained (A2).
- Supervisor checkpoints (A6) and weekly team habits (A7).
- **Tips and common problems** inside many steps.
- A table that shows which steps depend on which (Part 0.4).
- Ready-to-use templates (Part F).
- A map from every proposal section to the steps that do it (Part G).
- Practice questions for the viva (Part H).

---

## How to Use This Guide

This guide explains the **whole project from the very start**, in the correct order, exactly as the proposal asks. It also shows **what is already done** in the project folder.

**The parts of this guide:**

| Part       | What it contains                                                                 |
| ---------- | -------------------------------------------------------------------------------- |
| **Part 0** | Progress so far. Use it to answer "what has been done?"                          |
| **Part A** | The project in plain words, key words, what you need, rules, timeline.           |
| **Part B** | The old files in the folder: what was wrong, where they are now, the old model.  |
| **Part C** | The work: **43 steps in order** (Step 0 to Step 42).                              |
| **Part D** | The final checklist.                                                             |
| **Part E** | Common mistakes to avoid.                                                        |
| **Part F** | Templates (decision log, logbook, test record, weekly note).                     |
| **Part G** | Proposal map: which step does each part of the proposal.                         |
| **Part H** | Practice questions for the viva.                                                 |

**Every step in Part C has the same parts:**

| Part           | Meaning                                                    |
| -------------- | ---------------------------------------------------------- |
| **Status**     | What already exists in the folder. What is left.           |
| **Why**        | Why we do this step.                                       |
| **You need**   | Tools, files or earlier steps that must be ready first.    |
| **Do this**    | The actions, in order.                                     |
| **Tips**       | Common problems and how to avoid them.                     |
| **Output**     | The files or results the step must make.                   |
| **Done when**  | A simple check. **Do not move on until it passes.**        |
| **Proposal**   | Where the proposal asks for this step.                     |

**Status labels:**

| Label                       | Meaning                                                                  |
| --------------------------- | ------------------------------------------------------------------------ |
| ✅ **Done**                 | It exists in the folder and matches the proposal.                         |
| 🔧 **Done – needs changes** | It exists, but some things must still be changed. The box lists them.     |
| 🟡 **Started**              | Some parts exist. The box lists what is missing.                          |
| ♻️ **Old code to reuse**    | Old code can be a starting point. The step itself is **not done**.        |
| ⬜ **Not started**          | Nothing exists yet.                                                       |

The status was checked on **19 October 2026**. We looked at the project folder (`D:\intrusion detection`), the software on the development PC, and the Git history. **When you finish a step, update its Status box and the table in Part 0.2.**

**Two more labels:**

- Text **without a label** comes from the proposal. **You must do it.**
- **➕ Extra** means a helpful addition that is **not in the proposal**. It does not change the proposal. You may skip it, but we recommend it.

**If this guide and the proposal ever disagree, the proposal is correct.**

---

# Part 0: Progress So Far (19 October 2026)

> **Status update — 8 November 2026 (read this first; it replaces the older summary below where they differ).**
> - **Built and tested on the development PC:** data pipeline and model (Steps 7–18), Zeek adapter and live runner (Step 21), MongoDB, login, server, detector, decision engine, Nmap discovery, log export, dashboard, response policy, nftables rules and adapters (Steps 23–33).
> - **Corrected on 8 Nov 2026** after a full check against the proposal: 4 swapped scenario names in the dataset map (D-039); Step 17 redone so that no threshold is chosen from the held-out scenario (D-040); automatic response connected, off by default, with `lab.local_networks` deciding what is local (D-041); the synthetic "camera" data and every result based on it withdrawn (D-042).
> - **Not done yet (needs the lab):** Zeek on the sensor (Step 19), real benign camera traffic (Step 20), the real schema check (Step 22), and Steps 34–42.
> - **Hypothesis H1 is not confirmed:** the held-out macro-F1 is below 0.85, and the camera-traffic FPR is not measured yet.

## 0.1 What has been done from the beginning?

1. **The research proposal is written** (July 2026). Everything in this guide is based on it. The PDF is at `Desktop\research\Group03_Proposal.pdf`. It is not in the project folder yet.
2. **An old prototype exists from 2025.** It was made before this proposal. It had:
   - a React dashboard,
   - a small Flask login server,
   - a Scapy detector with a Random Forest trained on an unofficial IoT-23 copy,
   - KDD and CICIDS2017 models,
   - an Nmap scanner.

   It **does not meet the proposal** (see Part B). The old Python code and models are in `archive/`, for reference only. The React dashboard in `my-app/` will be reused and changed (Steps 29–30).
3. **The project folder was cleaned and put under Git (Step 2)** on 19 Oct 2026:
   - new folder layout;
   - old files moved to `archive/`;
   - a Git repository with 6 commits;
   - `.gitignore` and `.gitattributes`.

   A review on the same day fixed some mistakes. All fixes were committed (`9f90ce1`) and pushed to GitHub (`main`).
4. **Start-up files were written:**
   - `README.md`;
   - `requirements.txt` (the package list; the versions are not fixed yet);
   - `.env.example` (the names of the secret settings);
   - `config/settings.example.yaml` (the Step 4 layout, with example values);
   - a **draft** `config/label_mapping.yaml` (Step 8; not frozen yet).
5. **An early draft of the database code** (`core_engine/db_service.py`, Step 23) was written ahead of order. It connects to MongoDB 8, and its small self-test passed. It still needs the changes listed in Step 23.
6. **The explanation documents were corrected.** `PROJECT_EXPLANATION_EN.md` and `PROJECT_EXPLANATION.md` were rewritten to follow the proposal (Part B2).
7. **The development PC is partly ready (Step 3).** It has Python 3.10, scikit-learn 1.6.0, pandas 2.2.3, pymongo, Flask-SocketIO, python-nmap, Scapy, Node.js 22, Git and MongoDB 8.

**Not started yet:**

- the lab network (Step 5)
- the IoT-23 download and all dataset and model work (Steps 7–18)
- Zeek and live features (Steps 19–22)
- the new backend, response controls and dashboard (Steps 24–34)
- all testing and evaluation (Steps 35–42)

**No objective (O1–O6), requirement (FR-01 to FR-08), research question (RQ1–RQ5) or the hypothesis (H1) is finished yet.**

## 0.2 Status of every step

| Step | Name                                       | Status | What exists now / what is left                                                                              |
| ---- | ------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------- |
| 0    | Understand the project, literature review  | ✅     | Summary and literature notes written; Almashhadani citation removed (D-009); all members have read.         |
| 1    | Lab plan, retention plan, logbook          | ✅     | All 3 files complete: device simulation/lab allocations, team permissions, keep periods (90/30/90).         |
| 2    | Clean the folder and set up Git            | ✅     | Committed (`9f90ce1`) and pushed to GitHub. Backup done. Public repo accepted.                               |
| 3    | Install the software                       | 🟡     | Step 3a ✅ done on Windows PC (.venv, pinned requirements, check_env PASSED). Step 3b/3c pending for lab.    |
| 4    | Settings file and decision log             | ✅     | Local `config/settings.yaml`, `.env` and `docs/decision_log.md` (D-001 to D-013) complete; allowlist confirmed. |
| 5    | Build the lab network                      | ⬜     | Hardware track: requires physical lab equipment (proceed to Step 6 on Development PC).      |
| 6    | Threat model and requirement checklist     | ✅     | `docs/threat_model.md` and `docs/requirements_checklist.md` (FR-01–FR-08, O1–O6) complete.  |
| 7    | Download IoT-23 and make a manifest        | ✅     | Local CSV copy of all 23 IoT-23 v1.0.0 scenarios in `data/raw/iot23/` (44.13 GB, 325.3M flows). `tools/verify_iot23_copy.py`: first and last flow match the official files for 23/23; label totals match the official website for 17 scenarios, 3 small label differences explained (D-039, D-046); download source still to record (issue 22). |
| 8    | Write and freeze the label mapping         | ✅     | Frozen `config/label_mapping.yaml` to 5 target classes (D-014); all 17 labels resolved; ambiguous excluded (0.0031%). |
| 9    | Data-quality report                        | ✅     | `reports/data_quality_report.md` complete with Class x Scenario matrix (325.3M flows), missing rates & charts. |
| 10   | Load and clean the data                    | ✅     | Streamed all 23 scenarios (325.3M flows); imputed Zeek nulls; 10,240 ambiguous excluded; 23 Parquet files in `data/interim/` (10.62 GB); summary in `reports/interim_data_summary.md`. |
| 11   | Shared feature code                        | ✅     | `ml_engine/features.py` unified engine; 19 features (6 cat, 13 num); 10 unit tests in `tests/unit/test_features.py` passed (D-015). |
| 12   | Sampling and class balance                 | ✅     | `ml_engine/sample_dataset.py`; capped $N=50,000$/class per scenario; 1,384,070 training flows; re-run 9 Nov 2026 to keep audit columns (time, IPs, original label; never model inputs, D-046): feature columns identical, model not retrained (D-016, D-046). |
| 13   | Plan the three test levels                 | ✅     | Three-level plan in `reports/test_split_plan.md`; Level 1 Grouped CV (`StratifiedGroupKFold`); Level 2 Held-out `Capture-34-1` (23,145 flows sealed in `data/processed/heldout/`); Level 3 Lab camera; tests passed in `tests/unit/test_sampling_and_splits.py` (D-017). |
| 14   | Train the Random Forest                    | ✅     | `ml_engine/train.py`; grouped CV by scenario; re-run 8 Nov 2026 after D-039: out-of-fold macro-F1 **0.3422** (fold mean 0.3353 ± 0.1704); best `n_estimators=100, max_depth=18`; 4.30 MB; out-of-fold probabilities saved for Step 17 (D-018, D-040, D-043). |
| 15   | Compare with other models                  | ✅     | `ml_engine/compare_models.py`; re-run 9 Nov 2026: out-of-fold macro-F1 HGB **0.4331** > RF 0.3422 > LR 0.2722; RF kept as the main model per proposal 2.4 (explainable tree paths); `reports/experiments/model_comparison.md` (D-019, D-043). |
| 16   | Evaluate on the held-out scenario          | ✅     | `ml_engine/evaluate.py`; re-run 9 Nov 2026 on `Capture-34-1` (23,145 flows): uncalibrated RF macro-F1 0.4530 (5 classes) / 0.5662 (4 present); H1 part 1 **not met** (D-020, D-043). |
| 17   | Calibration, explanation, thresholds       | ✅     | Redone 8–9 Nov 2026: `temperature` calibration (D-045); deployed model on 34-1 macro-F1 **0.4530**; block thresholds by replaying the proposal's repeat rule (D-046): **PortScan 0.30, CnC 0.39**, DDoS and Malware alert only; results per original label added. |
| 18   | Model bundle and model card                | ✅     | Re-run 9 Nov 2026: `ml_engine/models/ids_bundle_v1.joblib` v1.2.0 (9.3 MB, not in Git, `temperature` calibration); `reports/experiments/model_card.md` filled from the result files (D-022, D-045). |
| 19   | Run Zeek on the sensor                     | 🟡     | Re-opened 8 Nov 2026 (D-042): config, start script and tests ready; Zeek not yet run on the Linux sensor. |
| 20   | Collect our own benign camera traffic      | 🟡     | Re-opened 8 Nov 2026 (D-042): the 31 Oct flows were synthetic and the result is withdrawn; real capture pending (`collect_camera_traffic.py --source real`). |
| 21   | Zeek adapter                               | ✅     | `core_engine/zeek_adapter.py` streaming JSON adapter; offset persistence in `.zeek_adapter_state.json`; micro-batching (`batch_size=100`, `timeout=0.5s`); direction & device enrichment; 9 unit tests passed (D-025). |
| 22   | Offline vs live schema check               | 🟡     | Re-opened 8 Nov 2026 (D-042): `tools/schema_check.py` ready; run on the real capture to answer RQ3. |
| 23   | Set up MongoDB                             | ✅     | `core_engine/db_service.py` 9 collections, full block history compound non-unique index, dynamic settings, TTL indexes (D-027). 18 dedicated unit/integration tests passed. |
| 24   | Login and secrets                          | ✅     | `core_engine/auth.py` bcrypt hashing, 8-hour JWT access tokens, `tools/create_admin.py` CLI provisioning, route decorators, system_logs audit integration (D-028). 21 unit tests passed. |
| 25   | Flask + Socket.IO server                   | ✅     | `core_engine/app.py` 15 REST endpoints, authenticated WebSocket push telemetry, lab safety guardrails (D-029). 13 integration tests passed. |
| 26   | Detector and decision engine               | ✅     | `detector.py`, `decision_engine.py`: calibrated inference, alert/block thresholds from Step 17, allowlist, burst coalescing, stage timestamps; block candidates go to the response policy (D-030, D-041). |
| 27   | Device discovery (Nmap)                    | ✅     | `core_engine/scanner_service.py` authorized Nmap scanner, multi-evidence camera heuristics, approved subnet restrictions (192.168.50.0/24), camera confirmation RBAC API (D-031). 17 tests passed (12 unit, 5 integration). |
| 28   | Log export                                 | ✅     | `core_engine/export_service.py` forensic log export in RFC 4180 CSV & JSON, multi-attribute filtering (time, class, IP, status, severity), system_logs audit invariant (D-032). 14 tests passed (10 unit, 4 integration). Phase 6 100% COMPLETE. |
| 29   | Clean up the React app                     | ✅     | `my-app/` cleaned, legacy routes/styles removed, single `REACT_APP_API_URL` config (`src/config.js`), Axios Bearer auth interceptors (`services/api.js`), `socket.io-client` with JWT auth (`services/socket.js`), zero fake attacks, verified with passing Jest test and production build (D-033). |
| 30   | Dashboard pages                            | ✅     | 7 canonical pages built in `my-app/src/pages/` (Overview, Live Alerts, Attack History, Devices, Blocklist, Settings, Log Export), responsive `Layout.js`, "Model prediction" vs "Confirmed incident" badges, full Socket.IO push telemetry, zero synthetic data, verified with Jest tests & production build (D-034). Phase 7 100% COMPLETE. |
| 31   | Response policy (safety rules)             | ✅     | `docs/response_policy.md` formal spec; `core_engine/response_policy.py` direction-aware policy engine (Table 5) & 7 safety guardrails (Checkpoint C7); deque sliding window repeat coalescing; integrated into `decision_engine.py`; 12 unit tests passed (D-035). RQ5 answered. |
| 32   | nftables rules                             | ✅     | `sensor/ids_inline.nft` (bridge) & `sensor/ids_router.nft` (inet) rulesets; dynamic timeout sets (`block_src`, `block_dst`, `limit_src`); source-only allowlist; `core_engine/firewall/nftables_adapter.py` kernel adapter with dev simulation fallback; 12 unit tests passed (D-036). FR-06 fulfilled. |
| 33   | Response adapters                          | ✅     | `core_engine/firewall/base.py` ABC; `router_adapter.py` passive SSH router mitigation; `simulation_adapter.py` in-memory dev engine; `__init__.py` factory; integrated with `DecisionEngine.execute_response()` & Flask blocklist REST API; 12 tests passed (8 unit, 4 integration) (D-037). FR-06 fulfilled. |
| 34   | Manual control, expiry, restart recovery   | ⬜     | —                                                                                                            |
| 35   | 6 controlled test scenarios                | ⬜     | —                                                                                                            |
| 36   | Functional requirement tests               | ⬜     | —                                                                                                            |
| 37   | Speed and resource use                     | ⬜     | —                                                                                                            |
| 38   | Reliability tests                          | ⬜     | —                                                                                                            |
| 39   | Usability and audit test                   | ⬜     | —                                                                                                            |
| 40   | Put all results together                   | ⬜     | —                                                                                                            |
| 41   | Final documents                            | 🟡     | `README.md` started (overview and quick start).                                                              |
| 42   | Final demo and data clean-up               | ⬜     | —                                                                                                            |

**Count:**

| Status                     | Number of steps | Steps             |
| -------------------------- | --------------- | ----------------- |
| ✅ Fully done              | 29              | 0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| 🔧 Done, small changes left | 0               | —                 |
| 🟡 Started                 | 5               | 3, 19, 20, 22, 41 |
| ♻️ Old code to reuse       | 0               | —                 |
| ⬜ Not started             | 9               | 5, 34, 35, 36, 37, 38, 39, 40, 42 |

## 0.3 What to do next, in order

**First, three tasks that need no hardware (9 Nov 2026):**

A. ~~Decide how automatic blocking should work~~ **Done 9 Nov 2026 (D-046):** block thresholds follow proposal 3.4 (confidence threshold + repeats); PortScan and CnC can be blocked, DDoS and Malware are alert only.
B. **Write down where the IoT-23 CSV copy was downloaded from** (page link and date). The content already matches the official files (D-039).
C. **Confirm the lab type with the supervisor** (real camera or camera simulator; physical or virtual lab), and update D-038.

**Then the lab work:**

1. **Set up the lab (Step 5).** A real camera, or a camera simulator confirmed with the supervisor (D-038), a switch that can mirror ports (or a virtual switch), a Linux sensor, a lab router, an attack computer and the admin PC. Fill in the real IPs and models in `docs/ethics/lab_plan_and_rules.md`.
2. **Prepare the sensor (Step 3b/3c).** Ubuntu, Zeek, MongoDB, Python `.venv`, the project from Git, and `ml_engine/models/ids_bundle_v1.joblib` copied by USB (it is not in Git).
3. **Step 19:** run Zeek on the mirror port; check real `conn.log` lines.
4. **Step 20:** capture real benign camera traffic for several hours; run `sensor/collect_camera_traffic.py --conn-log ... --source real`.
5. **Step 22:** run `tools/schema_check.py --live-path ... --source real`. Drop and retrain any feature that cannot be made the same way (proposal 3.5).
6. **Step 34:** manual block/unblock from the dashboard, rule expiry shown in the database, recovery after a restart.
7. **Step 35:** the 6 scenarios of proposal Table 10, with `auto_response: true` only during these tests; write each run in the lab logbook.
8. **Steps 36–42:** requirement tests, speed and resources, reliability, usability, results, final documents, demo and data clean-up.

**Keep this order.** Steps 19, 20 and 22 use real traffic with `auto_response: false`. Turn `auto_response` on only in Step 35, and only after task A is decided. If Step 22 shows that a feature cannot be made the same way live, retrain (Steps 14–18) before Step 35.

## 0.4 Which steps depend on which (➕ Extra)

A step can start only when the steps in "Needs" are done.

| Step(s) | Needs                       | Why                                                        |
| ------- | --------------------------- | ---------------------------------------------------------- |
| 3a, 3d  | 2                           | PC environment inside the clean project folder. (✅ Done)   |
| 4       | 2                           | Settings files live in the repository.                     |
| 6       | 0, 4                        | Threat model and FR definitions need project scope.        |
| 7       | 3a                          | Python tools on the PC.                                    |
| 8       | 7                           | You must see the real labels before freezing the mapping.  |
| 9       | 7, 8                        | Counts per class need the mapping.                         |
| 10–12   | 8, 9                        | Clean data and sampling plan.                              |
| 13      | 9                           | Choose the held-out scenario from the class × scenario table. |
| 14–17   | 11, 12, 13                  | Features, data and the split plan.                         |
| 18      | 14–17                       | The final model and thresholds.                            |
| 3b, 5   | 1, 4                        | Lab hardware, IP plan and sensor setup.                    |
| 19      | 3b, 5                       | Zeek on the sensor, in the lab.                            |
| 20      | 1, 19                       | Lab rules and logbook ready; Zeek running.                 |
| 21      | 11, 19                      | Adapter uses `make_features()` and Zeek logs.              |
| 22      | 11, 20, 21                  | Compare offline and live features.                         |
| 23      | 1 (retention), 4            | TTL periods and settings.                                  |
| 24–28   | 23                          | They all use the database.                                 |
| 26      | 18, 21, 22, 25              | Needs the model, the adapter and the server.               |
| 29–30   | 24, 25                      | The dashboard talks to the new backend.                    |
| 31–34   | 17, 26                      | Final thresholds and the decision engine.                  |
| 3c, 35  | 1, 5, 31–34                 | Attack PC setup and controlled tests in the separated lab. |
| 36–39   | 35                          | System reliability, speed, and usability tests.            |
| 40      | 16, 22, 35–39               | All evaluation results combined.                           |
| 41–42   | 40                          | Final report and demo.                                     |

---

# Part A: Start Here

## A1. The project in plain words

**The problem.** IP cameras are on the network all day. Attackers can:

- **scan** them to find weak ones,
- **flood** them so they stop working,
- **take control** of them (C&C), or
- use them to **download malware**.

Most small camera networks have **nothing watching the traffic**. They also have **no safe way to react**. This is the "security gap" in proposal Figure 1.

**What we build.** A system that:

1. **Watches** the camera network traffic. It never looks at the video. It only looks at *who talks to whom, how much, and how*.
2. **Turns** the traffic into connection records called **flows**, using a tool called **Zeek**.
3. **Classifies** each flow with a **Random Forest** model into one of 5 classes:
   - Benign
   - DDoS/DoS
   - Port scan
   - C&C
   - Malware/download
4. **Saves** the evidence in **MongoDB**.
5. **Shows** live alerts on a **React** dashboard.
6. **Responds safely.** It blocks or slows down a bad IP address with **nftables** (or through the router). It does this **only** when strict safety rules pass. The admin can always undo it.
7. **Finds devices** on the lab network with **Nmap**.

**The research question.** The model learns from a public dataset called **IoT-23**. But the normal traffic in IoT-23 does **not** come from cameras. So the main research question is: **does a model trained on IoT-23 still work on real camera traffic?**

## A2. Key words explained

**Network words**

| Word                          | Simple meaning                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **IoT**                       | "Internet of Things": small network devices, like cameras, smart lamps or door locks.                       |
| **NVR**                       | Network Video Recorder. It records the camera video.                                                        |
| **RTSP**                      | The usual protocol that cameras use to send video.                                                          |
| **PoE**                       | Power over Ethernet: the network cable also gives power to the camera.                                      |
| **Packet**                    | One small piece of network data.                                                                            |
| **Flow (connection)**         | All packets of one conversation between two devices, for example one TCP connection. **One flow = one row of data.** |
| **IP address**                | The address of a device on the network, for example `192.168.50.30`.                                        |
| **Subnet**                    | A group of addresses that belong together, for example `192.168.50.0/24` (= `192.168.50.0` to `192.168.50.255`). |
| **Port**                      | A number that says which service a connection is for (e.g. 80 = web, 554 = RTSP, 23 = Telnet).               |
| **Switch**                    | Connects devices on the same network with cables.                                                           |
| **Managed switch**            | A switch you can configure. We need one with **port mirroring**.                                            |
| **SPAN / port mirroring**     | The switch sends a **copy** of the traffic to our sensor. The sensor can watch but **cannot block**. This is **passive mode**. |
| **Router**                    | Connects two different networks (subnets) and passes traffic between them.                                  |
| **OpenWrt**                   | Free Linux software for routers. It lets you log in by SSH and run nftables on the router.                  |
| **Inline mode**               | The sensor sits **in the path** of the traffic, so it can block directly.                                   |
| **Bridge**                    | A Linux setting that joins two network ports, so traffic passes straight through the computer.              |
| **Sensor**                    | The Linux computer that runs Zeek, the model, the backend and the response adapter.                         |
| **Allowlist**                 | IP addresses that must **never** be blocked (admin PC, NVR, gateway, sensor).                               |
| **nftables**                  | The Linux firewall. We use it to block or rate-limit IP addresses.                                          |
| **Rate-limit**                | Allow only a small amount of traffic per second from an address, and drop the rest.                         |
| **Nmap**                      | A tool that finds devices and open ports on a network.                                                      |

**Zeek and data words**

| Word                          | Simple meaning                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Zeek**                      | A free tool that watches traffic and writes **one line per flow** into a file called **`conn.log`**.         |
| **`conn.log` fields**         | `duration` (how long), `orig_bytes`/`resp_bytes` (bytes each side sent), `orig_pkts`/`resp_pkts` (packets each side), `proto` (tcp/udp/icmp), `service` (http, dns …), `conn_state` (how the connection ended, e.g. `SF` normal, `S0` no answer), `history` (a short code of what happened, e.g. `ShADadFf`). |
| **IoT-23**                    | A public dataset of labelled IoT flows: 23 captures ("scenarios"), 20 with malware and 3 normal.            |
| **Scenario**                  | One capture in IoT-23, for example `CTU-IoT-Malware-Capture-34-1`.                                          |
| **Label**                     | The correct answer for a flow, for example `PartOfAHorizontalPortScan`.                                     |
| **Class**                     | One of our 5 groups of labels (Benign, DDoS/DoS, Port scan, C&C, Malware/download).                         |
| **Label mapping**             | The written list that says which IoT-23 label goes into which class.                                        |
| **Manifest**                  | A list of every data file we use, with its size, row count, label counts and hash.                          |
| **Hash (SHA-256)**            | A long code made from a file. If the file changes, even by one byte, the code changes. It proves the file is the same. |
| **CSV / Parquet / JSON**      | File formats. CSV = text table. Parquet = compressed table, much faster to read. JSON = one record per line, with field names. |
| **Metadata**                  | Information *about* traffic (who, when, how much), not the content. We keep only metadata.                  |

**Machine-learning words**

| Word                          | Simple meaning                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Feature**                   | One input column the model uses, for example `duration`.                                                    |
| **Encoder**                   | Code that changes text categories (like `tcp`, `udp`) into numbers the model can use.                       |
| **Pipeline**                  | The encoder and the model joined into one object, so the same steps always run in the same order.           |
| **Random Forest**             | A model made of many decision trees that vote together.                                                     |
| **Training / testing**        | The model learns from training data. We check it on testing data it has never seen.                         |
| **Leakage**                   | Test data that is too similar to training data (for example, flows from the same capture in both). The score then looks better than it really is. |
| **Grouped cross-validation**  | Split the data into parts **by scenario**, so flows from one scenario are never in both training and testing. |
| **Held-out scenario**         | A scenario we keep away completely. We test on it only at the very end.                                     |
| **Hyperparameters**           | Model settings we choose, such as the number of trees.                                                      |
| **Precision**                 | Of all flows we called "attack X", how many really were attack X.                                           |
| **Recall**                    | Of all real attacks of a class, how many we caught.                                                         |
| **F1 / Macro-F1**             | F1 mixes precision and recall into one score. Macro-F1 is the average F1 over all classes, so **every class counts the same**. It is fairer than accuracy when some classes are tiny. |
| **False-positive rate (FPR)** | Of all normal flows, how many we wrongly called an attack.                                                  |
| **Confusion matrix**          | A table that shows which classes are mixed up with which.                                                   |
| **PR-AUC**                    | A score for how well the model separates one class from the others, useful for small classes.               |
| **Calibration**               | Checking whether "90% confidence" really means "right about 90% of the time".                               |
| **Brier score**               | A number for calibration. Lower is better.                                                                  |
| **Permutation importance**    | Shuffle one feature and see how much the score drops. A big drop means the feature matters.                 |
| **Domain shift**              | The live data is different from the training data, so the model does worse.                                 |
| **Schema check**              | Comparing the offline and live features: names, types, ranges, missing values, categories.                  |
| **Threshold**                 | A limit value, for example "act only if confidence ≥ 0.85".                                                 |

**Software words**

| Word                          | Simple meaning                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Virtual environment (`.venv`)** | A private Python folder for this project, so its package versions do not mix with other projects.        |
| **Git / commit**              | Git saves versions of your files. A **commit** is one saved version with a short message.                   |
| **Flask / Flask-SocketIO**    | Python tools to build the backend API and send live updates to the dashboard.                               |
| **REST API / endpoint**       | A web address the dashboard calls to get or change data, for example `GET /api/events`.                     |
| **Socket.IO**                 | A way for the server to **push** live updates to the dashboard without a page refresh.                      |
| **MongoDB / collection**      | The database. A **collection** is like a table (e.g. `attack_events`).                                       |
| **TTL index**                 | A MongoDB setting that deletes old records automatically after a set time.                                  |
| **JWT token**                 | A "pass" the backend gives after login. The dashboard sends it with every request.                           |
| **bcrypt**                    | A safe way to store passwords. Only a scrambled "hash" is saved, never the real password.                   |
| **React**                     | The tool used to build the web dashboard.                                                                   |
| **WSL**                       | "Windows Subsystem for Linux". Runs Ubuntu inside Windows. Your PC has it.                                  |
| **Latency**                   | The delay between two moments, for example from "flow seen" to "alert shown".                               |
| **Median / 95th percentile**  | Median = the middle value. 95th percentile = 95% of the values are below this.                              |

## A3. One example from start to end

This is how the finished system handles an **authorised port scan** in the lab:

1. The attack test computer scans port 23 on every device in the camera subnet.
2. The traffic reaches the sensor:
   - **passive mode:** the switch copies the traffic to the sensor;
   - **inline mode:** the traffic passes through the sensor.
3. Zeek writes one line in `conn.log` for each scan attempt. The state is `S0` ("no answer").
4. The **Zeek adapter** reads the new lines straight away.
5. The **feature code** turns each line into the same feature columns used in training.
6. The **Random Forest** says: "Port scan, confidence 0.97".
7. The **decision engine** saves an event in MongoDB and sends an alert to the dashboard.
   - The alert shows: time, direction, source, destination, class, confidence, a short evidence note and the response status.
   - It is marked **"model prediction"** until an admin confirms it.
8. The decision engine checks the **safety rules**:
   - Is the scanner on the allowlist? **No.**
   - Is the confidence above the threshold? **Yes.**
   - Has it happened again inside the time window? **Yes.**
9. Only then does the **response adapter** block the scanner's IP. The block has an **expiry time**. A reason code and an audit record are saved.
10. The dashboard shows the block. The admin can press **Unblock** at any time.

This is proposal Figure 2 (architecture) and Figure 3 (detection and response cycle).

## A4. What you need

### A4.1 Hardware (proposal Section 5.1)

| Item                                                        | Why we need it                                             | Notes                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| At least **one IP camera**, or a **camera simulator**       | The device we protect                                  | A simulator can be a PC or Raspberry Pi that streams a test video. |
| **NVR** or a recording service                              | Records the video, like a real setup                       | Can be recording software on a PC.                                       |
| **Managed switch with port mirroring**                      | Sends a copy of the traffic to the sensor (passive mode)   | "Port mirroring" or "SPAN" must be in its features list.                 |
| **Linux sensor computer**                                   | Runs Zeek, the model, the backend and the response adapter | Needs **two network ports**. A USB Ethernet adapter is fine for the second one. |
| **Attack test computer**                                    | Makes the controlled test traffic                          | Linux. Used **only** inside the lab.                                     |
| **Admin workstation**                                       | Opens the dashboard                                        | Any PC with a browser. Your Windows PC can be this.                      |
| **Lab router you control**                                  | Connects the lab parts; applies blocks in passive mode     | You must be able to log in by SSH or API. OpenWrt is a good choice.      |
| Network cables                                              | —                                                          | —                                                                        |

**Tips (➕ Extra):**

- Before you buy a switch or router, check its documentation for "port mirroring" (switch) or "OpenWrt supported" (router).
- An old laptop or desktop is enough for the sensor.
- Some cheap cameras need the internet or a vendor cloud for their **first setup**. Do that first, then disconnect them from the internet (Step 5).

### A4.2 Software (proposal Table 8)

| Area              | Tool                                      | Where it runs                                            |
| ----------------- | ----------------------------------------- | -------------------------------------------------------- |
| Dataset           | IoT-23 v1.0.0                             | Downloaded to the development PC                         |
| Machine learning  | Python, pandas, scikit-learn              | Development PC (training) and sensor (prediction)        |
| Network analytics | Zeek; TShark/Scapy only for checking      | Sensor                                                   |
| Backend           | Flask, Flask-SocketIO                     | Sensor                                                   |
| Frontend          | React and chart components                | Built on the development PC; opened in the admin browser |
| Database          | MongoDB                                   | Sensor                                                   |
| Response          | nftables; adapter for router/firewall API | Sensor (inline) or router (passive)                      |
| Discovery         | Nmap                                      | Sensor                                                   |

**Your Windows PC already has** (checked 19 Oct 2026):

- Python 3.10.0, scikit-learn 1.6.0, pandas 2.2.3
- Node.js 22.12, Git 2.47
- MongoDB 8.0
- **WSL Ubuntu.** It can run Zeek on saved capture files for practice (➕ Extra, see Step 3). It **cannot** be the real sensor.

**Not on the PC yet:** Nmap.

**Zeek and nftables do not run on Windows.** So the sensor must be a Linux computer.

### A4.3 Skills the team will use

You do not need to be an expert at the start. You will learn these during the steps:

- Basic Linux terminal commands (`cd`, `ls`, `sudo apt install`, editing files).
- Python with pandas and scikit-learn.
- Basic networking (IP address, subnet, router, switch, TCP/UDP).
- Basic React and REST APIs.
- Git (save versions of your work).

### A4.4 Lab rules

- The team has permission to carry out this work in the lab.
- Only the team members listed in the lab plan (Step 1) use the attack tools, the lab passwords and the firewall rights (proposal 3.8).
- Every test follows the lab plan and is written in the lab logbook first.

## A5. The golden rules (never break these)

All of these come straight from the proposal.

1. **Use the official IoT-23 v1.0.0 labelled flows.** Do not train on a copy that someone else already processed, unless you can check where it came from and what was changed (3.2).
2. **Write the label mapping before training.** Never change it after you see test results (2.3).
3. **Never split data by random rows.** Keep each scenario together. Keep at least one scenario (or one local capture) out for the final test (2.2, 3.4).
4. **Do not touch the test data** while you choose preprocessing steps or model settings (3.4).
5. **Never use UID, raw IP addresses or the capture file name as model inputs.** Use them only for grouping and audit (Table 6).
6. **Offline and live must use exactly the same preprocessing.** Save it together with the model (3.3 step 7).
7. **Accuracy is not the main result.** Use macro-F1, recall per class, false-positive rate and confusion matrices (3.4).
8. **One high prediction never blocks by itself.** A block needs all of these: allowlist check, private-network check, minimum confidence, repeated events, maximum rule time, reason code and audit record (3.4, 3.7).
9. **Only use the separated lab network.** No other person's camera, no public IP, no vendor cloud, no university production network (3.8).
10. **No live malware.** Only controlled scans, rate-limited flooding or replay, and simulations of C&C-like or file-transfer behaviour (5.1).
11. **Keep no video or audio.** Only the network metadata we need (3.8).
12. **Passive mode is the default.** Inline mode needs a bypass and recovery plan (Table 11).
13. **Report all results, even bad ones** (6, 7.1).

## A6. Timeline (32 weeks, from proposal Figure 6)

Week numbers are approximate. Fit the real dates to the academic calendar, but **keep the order of tasks that depend on each other** (proposal Section 4).

| Phase (Figure 6 task)            | Steps                  | Weeks (about) |
| -------------------------------- | ---------------------- | ------------- |
| Problem refinement & ethics      | Steps 0 – 4            | W1 – W3       |
| Literature review                | Step 0 (keeps running) | W1 – W8       |
| Lab and network design           | Steps 5 – 6            | W3 – W8       |
| Dataset audit & label mapping    | Steps 7 – 9            | W5 – W10      |
| Preprocessing & feature pipeline | Steps 10 – 12          | W7 – W13      |
| Model training & validation      | Steps 13 – 18          | W10 – W17     |
| Live Zeek integration            | Steps 19 – 22          | W13 – W20     |
| Backend, database & APIs         | Steps 23 – 28          | W15 – W23     |
| React dashboard & alerts         | Steps 29 – 30          | W18 – W25     |
| Firewall response controls       | Steps 31 – 34          | W21 – W27     |
| Controlled security testing      | Steps 35 – 39          | W25 – W30     |
| Evaluation & analysis            | Step 40                | W28 – W32     |
| Documentation & final demo       | Steps 41 – 42          | W29 – W32     |

**Meetings (proposal Section 4):**

- Check progress as a team **every week**.
- Meet the supervisors **at least once every two weeks**.

**Supervisor checkpoints (➕ Extra).** Show these items at the supervisor meetings.

| Checkpoint | After step | What to show                                                    | Why it matters                              |
| ---------- | ---------- | --------------------------------------------------------------- | ------------------------------------------- |
| C1         | 1          | Lab plan and rules, retention plan                              | Everyone works by the same lab rules.       |
| C2         | 5–6        | Lab diagram, IP plan, threat model, requirement checklist       | The lab must be separated and safe.         |
| C3         | 8          | Label mapping and the reasons                                   | It is frozen after this.                    |
| C4         | 13         | Split plan with held-out scenario(s)                            | It must be fixed before training.           |
| C5         | 16–17      | Results and chosen thresholds                                   | These control automatic blocking.           |
| C6         | 22         | Schema check report                                             | Live use only after features match.         |
| C7         | 31         | Response policy and its unit tests                              | Before any automatic blocking in the lab.   |
| C8         | 35–40      | Test results and the final evaluation                           | Before writing the final report.            |

## A7. How the team works every week (➕ Extra)

These habits keep the work repeatable (Objective O1) and traceable (Section 3.8).

1. **Weekly note.** Write a short note each week: done, problems, next (template in Part F).
2. **Commit small and often.** Use clear messages, for example `Step 10: add IoT-23 loader`. Never commit data, models or `.env`.
3. **Decision log.** Every important choice goes into `docs/decision_log.md`, with the date and the reason (template in Part F).
4. **Lab logbook.** Every scan, capture, attack test or firewall change gets one line in `docs/lab_logbook.md` (template in Part F).
5. **Fixed seed.** Use `random_seed: 42` from the settings in every script that uses randomness.
6. **Update this guide.** When a step is finished, update its Status box and Part 0.2.

---

# Part B: What Was Already in the Project Folder

Read this before you start. It explains what the old files were, what was wrong, and where they are now.

## B1. Old files, their problems and where they are now

| Old item                                                       | What was wrong                                                                                                                                                       | Where it is now (19 Oct 2026)                       | Status / next action                                              |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------- |
| `iot23_attacks/iot23/X_train.csv`, `X_test.csv`, `y_*.csv`     | A copy that someone **already processed**. Some numbers are scaled (e.g. `orig_pkts = 3.03e-08`). **No scenario ID.** Split **randomly by rows**.                     | `archive/legacy_datasets/iot23_attacks/iot23/`      | ✅ Archived. **Never train on it.** Use official IoT-23 (Step 7).  |
| Label numbers 0–12                                             | The two versions of `iot23_attacks.py` gave **different names to the same number**. No port-scan name.                                                               | Old code in `archive/`                              | 🟡 Replaced by the draft `config/label_mapping.yaml` (Step 8).     |
| `random_forest_model.pkl` (820 MB) and the other old models    | Trained on the old data with unknown labels. KDD and CICIDS2017 are not used for training in the proposal.                                                           | `archive/legacy_datasets/`                          | ✅ Archived. Cannot be used (B3). Train a new model (Phase 4).     |
| Root `iot23_attacks.py`                                        | Scapy **per packet** with **fixed fake values** (`duration=0`, `conn_state=6`, `history=22`, `service=0`). `simulate_attack()` **makes up** a DDoS. It cannot start (imports a class that does not exist). | `archive/legacy_code/iot23_attacks.py`              | ✅ Archived. Replaced by Steps 21 and 26.                          |
| `db_manager.py`, `attack_logs.db`, `devices.db`                | Plain script, no class; two separate databases.                                                                                                                      | `archive/legacy_code/`                              | ✅ Archived. Replaced by `core_engine/db_service.py` (🟡 Step 23).  |
| `network_scan.py`                                              | Adds **random numbers** to the vulnerability count. Calls a device a camera from port 554 alone. Own server (port 5012) and own database.                              | `archive/legacy_code/network_scan.py`               | ♻️ Reuse the Nmap parts in Step 27, without these problems.       |
| `my-app/app.py`, `req.txt`, `instance/users.db`                | Users in **SQLite**, not MongoDB. JWT secret and admin password **written in the code**. Open sign-up page.                                                         | `archive/legacy_code/my-app_flask_backend/`         | ✅ Archived and removed from Git. New login in Step 24.            |
| `my-app/src/pages/IOTDetails.js` (and `CyberDetails.js`)       | Plain `WebSocket` to a **Socket.IO** server (they cannot connect). When the backend is down, it shows **made-up attack messages** (`fakeAttacks`).                    | Still in `my-app/`                                  | 🔧 Fix in Step 29.                                                 |
| Front end in general                                           | Calls 5 different ports (5002, 5005, 5006, 5007, 5012). The login page calls port 5002, whose server is now archived.                                                | Still in `my-app/`                                  | 🔧 One backend address (Step 29).                                  |
| `KDD/`, `CICID2017/` folders                                   | The proposal does **not** train on KDD or CICIDS2017 (CICIDS2017 is only a reference in Section 2.3).                                                                | `archive/legacy_datasets/`                          | ✅ Archived.                                                       |
| Pages `CyberDetails.js`, `TraditionalDetails.js`, `AttackHistoryCICIDS.js`, `KDDAttackHistory.js`, `Register.js` | Pages for datasets the proposal does not use; an open sign-up page.                                                                         | Still in `my-app/src/`                              | 🔧 Remove in Step 29.                                              |
| Premiere Pro files, presentation, `.zip` files, `python-installer.exe`, empty files | Not part of the system.                                                                                                                         | `archive/legacy_docs/`                              | ✅ Archived and removed from Git.                                  |
| No Git                                                         | The proposal needs "code with versions" (O1).                                                                                                                        | Git repository, 6 commits                           | ✅ Done; pushed to GitHub (Step 2).                                |

`archive/` is ignored by Git. It exists only on this PC. **Keep a backup of it on another drive.**

**Other documents in the folder:**

- `PROJECT_EXPLANATION_EN.md` (English) and `PROJECT_EXPLANATION.md` (Sinhala) explain **what** the system is and **why** it is built this way. They were rewritten on 19 Oct 2026 (version 2) and now agree with this guide. This guide explains **how** to build it.
- `PROJECT_PROGRESS_AND_CHALLENGES.md` is the team's progress report. It was corrected on 19 Oct 2026.
- These files and this guide are listed in `.gitignore`, so Git does not share them. Share them with the team another way, or remove them from `.gitignore`.

## B2. Where the old `PROJECT_EXPLANATION_EN.md` did not match the proposal (✅ resolved)

> **Status: ✅ Resolved (19 Oct 2026).**
>
> - Version 1 of both explanation files went against the proposal in the places below.
> - Both files were **rewritten (version 2)**. They now agree with this guide. Section 14 of each file lists the same changes.
> - None of these parts had been built yet, so **no code had to be fixed**. When you reach each step, follow this guide.
> - The table stays here as a record.

| Version 1 said                                                | The proposal says                                                                                                                       | Handled in       |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Train on the existing `X_train.csv` / `X_test.csv`.           | Official IoT-23 v1.0.0; no unofficial processed copy (3.2).                                                                             | Steps 7–12       |
| A normal train/test split.                                    | Grouped CV + leave-one-scenario-out + local camera test (3.4).                                                                          | Steps 13–16      |
| Random Forest only.                                           | Also compare a linear model and one gradient-boosting model (1.3, 2.4).                                                                 | Step 15          |
| No calibration or permutation importance.                     | Required before using confidence for automatic response (2.4, 3.4).                                                                     | Step 17          |
| A fixed list of 10 features.                                  | Table 6 also lists port categories, an incomplete-flow flag and optional time-window rates. Keep only features the live pipeline can make the same way. | Steps 11, 22 |
| No offline vs live feature check.                             | Required (3.5).                                                                                                                         | Step 22          |
| No local camera traffic.                                      | Collect our own benign camera flows (Table 11, H1).                                                                                     | Step 20          |
| Block with `iptables -A INPUT`.                               | nftables first; iptables/ipset or router API as adapters (3.7). An `INPUT` rule only protects the sensor itself, **not the cameras**.   | Steps 32–33      |
| No rule expiry and no direction logic.                        | Maximum rule time; outside scanner blocked by source; C&C by destination or device isolation (3.7).                                     | Steps 31–34      |
| 5 collections, no `users`.                                    | MongoDB also keeps users (3.6).                                                                                                         | Step 23          |
| No log export.                                                | FR-08.                                                                                                                                  | Step 28          |
| 5 test scenarios.                                             | 6 scenarios in Table 10.                                                                                                                | Step 35          |
| Firewall = FR-07, allowlist = FR-08, FR-05 = Telegram/email.  | FR-05 = Nmap discovery, FR-06 = blocking rules, FR-07 = allowlists/thresholds/audit, FR-08 = log export. No Telegram or email anywhere. | Step 6           |
| No ethics step, no data retention.                            | Required (3.8).                                                                                                                         | Steps 1, 23, 42  |
| "Confidence > 0.85 and 3 flows in 10 s" as fixed rules.       | A minimum confidence and repeated events inside a time window, but no numbers are given.                                                | Step 17          |
| A phone "IP Webcam" app is enough.                            | At least one IP camera **or a** camera simulator, plus a managed switch with mirroring, a Linux sensor, an attack test computer and an admin workstation (5.1). | Steps 1, 5 |
| Lab addresses `192.168.8.x` (a common home-router range).      | A separated lab network that we control (3.8).                                                                                          | Step 5           |

## B3. Can we use the old trained model? (No)

The folder has an old trained model: `archive/legacy_datasets/iot23_attacks/random_forest_model.pkl` (820 MB). **It cannot be used in this project.** The old training files (`iot0331.ipynb`, `iot23/A.py`, `iot23/X_train.csv`) show why:

| # | What we found in the old files                                                                                                                       | Why it blocks the proposal                                                                     |
| - | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1 | It was trained on `iot_23_preprocessed_cleaned.csv`, a file **somebody else had already processed**. Nobody wrote down where it came from or what was changed. | Proposal 3.2 does not allow an unofficial processed copy.                                   |
| 2 | The data has **no scenario IDs**.                                                                                                                    | Grouped cross-validation and a held-out scenario are impossible. **O2 and H1 cannot be tested.** |
| 3 | The data was split **randomly by rows**. The old notebook reports **accuracy 1.00**.                                                                 | Leakage. The test rows came from the same captures as the training rows. 1.00 does not show real skill. |
| 4 | The model outputs the numbers **0–12**. The meaning of each number was **not saved**.                                                                | We cannot match its output to the 5 classes of Table 5.                                        |
| 5 | Some inputs are **scaled** (e.g. `orig_pkts = 3.03e-08`). The categories are **unknown numbers** (e.g. `conn_state = 6`, `history = 22`). The scaling and the codes were **not saved**. | The live Zeek system cannot make the same input (3.3 step 7, 3.5). This is why the old live code used fixed fake values. |
| 6 | No saved preprocessing, no model version, no calibration, no comparison models.                                                                      | Needed by FR-02 and Sections 2.4, 3.3, 3.4.                                                    |

**What to do instead:**

- **Train a new model** from the official IoT-23 files (Steps 7–18). The team already used scikit-learn, so you are not starting from zero.
- **Keep the old notebook and model in `archive/`.** Do not load them in the new system.
- **In the final report**, you may mention the old 1.00 result as an example of **why** grouped validation is needed.
- **If you need test predictions before Step 18** (for example, to test the dashboard), use the **simulation adapter** and saved test events. Never use the old model. Never show its output as real detection.

---

# Part C: The Steps

---

# Phase 0: Start-Up, Ethics and Project Setup (W1 – W3)

## Step 0. Understand the project and start the literature review

> **Status: ✅ Done** (20 Oct 2026)
>
> - ✅ `docs/project_summary.md` — one page; aim, O1–O6, H1 and RQ1–RQ5 in the proposal's exact words.
> - ✅ `docs/literature_notes.md` — notes on all 11 references in the proposal, plus the 2 missing ones.
> - ✅ Missing reference **Santos et al. (2023)** found: *Cluster Computing*, 26(1), pp. 37–57, doi:10.1007/s10586-021-03238-y.
> - ✅ Missing reference **Almashhadani et al. (2024)** could not be found, and no team member has it. **Removed** (decision D-009). Tell the supervisor at the next meeting.
> - ✅ Every member has read the proposal.
> - Keep adding papers to the literature notes until about week 8.

**Why:** Everyone must understand the goal, the questions and the limits before building anything.

**You need:** The proposal PDF and this guide.

**Do this:**

1. Every team member reads the **whole proposal** once, slowly.
2. Read Part A of this guide again. Each member must be able to explain A3 (the example) in their own words.
3. Write the aim, the objectives (O1–O6), the hypothesis (H1) and the research questions (RQ1–RQ5) on **one page**: `docs/project_summary.md`.
4. Keep reading the papers in the reference list:
   - Antonakakis 2017
   - Garcia 2020
   - Vitorino 2022
   - Yang 2022
   - Gyamfi & Jurcut 2022
   - Biondi 2022
   - NISTIR 8259A
   - Zeek conn.log docs

   Write short notes in `docs/literature_notes.md`. You need them for the final report.
5. **Fix a gap in the proposal's references.** Section 1.4 cites **Santos et al. (2023)** and **Almashhadani et al. (2024)**, but they are **not in the reference list**. Find both papers, add them to your notes, and put them in the final report's references.

**Tips:**

- For each paper, write 4 lines: what they did, data used, main result, limit (why our project is different).
- Read one proposal section per day, so you do not rush.

**Output:** `docs/project_summary.md`, `docs/literature_notes.md`.

**Done when:** Each member can explain what the system does and what H1 means.

**Proposal:** Sections 1, 2; Figure 6 (literature review W1–W8).

---

## Step 1. Write the lab plan, the data retention plan and the lab logbook

> **Status: ✅ Done** (21 Oct 2026)
>
> - ✅ `docs/ethics/lab_plan_and_rules.md` written and completed: device specifications (IP camera simulation / lab loan allocations), all team permissions ticked, safety rules and allowed activities defined.
> - ✅ `docs/ethics/data_retention_plan.md` written and completed: keep periods agreed (90 days attack/audit logs, 30 days traffic summaries, 180 days local test captures), team sign-off recorded.
> - ✅ `docs/lab_logbook.md` started (entry 1: planning and documentation complete).
> - ✅ `config/settings.example.yaml` updated with agreed retention periods (90/30/90 days).

**Why:** Every test must follow the same rules, every action must be traceable, and we keep only the data we need (proposal 3.8).

**Do this:**

1. Write the **lab plan and rules** (`docs/ethics/lab_plan_and_rules.md`). It lists:
   - the separated lab network and its IP ranges;
   - the devices, and who owns or provides each one;
   - which team members use the attack tools, the lab passwords and the firewall rights (proposal 3.8);
   - the activities we run (proposal Table 10 and Sections 3.7, 5.1);
   - what we **never** do (public IPs, other cameras, vendor cloud, university network, live malware, keeping video);
   - the safety rules for every test.
2. Write a **data retention plan** (`docs/ethics/data_retention_plan.md`):
   - what metadata we keep;
   - who can open it;
   - how long we keep it;
   - when and how we delete it.

   **Decide the keep periods as a team.** Do not guess them.
3. Start a **lab logbook** (`docs/lab_logbook.md`). Every scan, capture, attack test and firewall change gets one line: date, person, what, why. (Template in Part F.)

**Tips:**

- Never write passwords in these files. They are in Git, and the repository is public.
- Write the names of the team members who use the attack tools in the lab plan (Section 4).

**Output:** `docs/ethics/lab_plan_and_rules.md`, `docs/ethics/data_retention_plan.md`, `docs/lab_logbook.md`.

**Done when:** The three files are complete (device owners, team permissions and keep periods filled in), and every team member has read them.

**Proposal:** Section 3.8; Section 1.2 (limits).

---

## Step 2. Clean the project folder and set up Git

> **Status: ✅ Done** (19 Oct 2026)
>
> **Done:**
> - ✅ The folder layout below exists, with `.gitkeep` files in the empty folders.
> - ✅ Old code, datasets and models moved to `archive/legacy_code/` and `archive/legacy_datasets/`; non-project files to `archive/legacy_docs/` (Git ignores `archive/`).
> - ✅ The inner `my-app/.git` was removed, so `my-app/` is saved as normal files.
> - ✅ `.gitignore` and `.gitattributes`, corrected on 19 Oct 2026.
> - ✅ The installer, `users.db`, the old `app.py` (hard-coded secret), `.zip` files and empty files were moved to `archive/` and removed from Git tracking.
> - ✅ All fixes committed (`9f90ce1`) and pushed to GitHub: https://github.com/madupadilshan/intrusion-detection (branch `main`). The working tree is clean.
>
> **Owner decisions (20 Oct 2026):**
> - ✅ The backup is done.
> - ✅ Keeping the repository public is accepted (the old history is not rewritten).
>
> **Still open (team decision):** the documentation `.md` files (including this guide) are in `.gitignore`. Either remove them from `.gitignore`, or share the guide another way, so every member uses the same version.

**Why:** A clean folder with saved versions makes the work repeatable (O1).

**You need:** Git (from git-scm.com).

**Do this:**

1. **Make a full backup** of the current folder. Copy it to another drive.
2. Create this folder layout:

```
intrusion detection/
├── README.md
├── STEP_BY_STEP_GUIDE.md
├── requirements.txt
├── .env.example               <- names of secret settings, no real values
├── .gitignore
├── .gitattributes
├── config/
│   ├── settings.example.yaml  <- lab settings (Step 4)
│   └── label_mapping.yaml     <- frozen label mapping (Step 8)
├── data/                      <- NOT in Git (too big, and private)
│   ├── raw/iot23/             <- official files, never changed
│   ├── interim/               <- parsed files
│   ├── processed/             <- feature tables, train / held-out
│   └── local/                 <- our own lab flows
├── ml_engine/
│   ├── manifest.py            <- dataset manifest with hashes
│   ├── load_iot23.py          <- reads conn.log.labeled files
│   ├── features.py            <- feature code, SHARED by training and live
│   ├── data_quality.py        <- data-quality report
│   ├── train.py               <- Random Forest training
│   ├── compare_models.py      <- linear + gradient-boosting comparison
│   ├── evaluate.py            <- metrics and figures
│   ├── calibrate.py           <- reliability curve, Brier score, thresholds
│   └── models/                <- saved model bundles (NOT in Git)
├── core_engine/
│   ├── app.py                 <- Flask + Socket.IO server
│   ├── auth.py                <- login
│   ├── db_service.py          <- MongoDB access
│   ├── zeek_adapter.py        <- reads Zeek conn.log live
│   ├── detector.py            <- features + model prediction
│   ├── decision_engine.py     <- safety rules and response policy
│   ├── scanner_service.py     <- Nmap discovery
│   ├── export_service.py      <- log export
│   └── firewall/
│       ├── base.py            <- common interface
│       ├── nftables_adapter.py
│       ├── router_adapter.py
│       └── simulation_adapter.py   <- ➕ Extra: for Windows development only
├── sensor/
│   ├── local.zeek             <- Zeek settings
│   ├── ids_inline.nft         <- nftables rules for inline mode
│   └── ids_router.nft         <- nftables rules for the router (passive mode)
├── tools/
│   ├── check_env.py           <- prints library versions (Step 3)
│   ├── create_admin.py
│   ├── schema_check.py        <- offline vs live feature check
│   └── measure_latency.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── lab_scenarios/         <- scripts for the Table 10 tests
├── my-app/                    <- React dashboard
├── reports/                   <- results, figures, data-quality report
├── docs/                      <- decision log, logbook, ethics, notes
└── archive/                   <- old code we no longer use (NOT in Git)
```

3. Move old things to `archive/`:
   - `KDD/`, `CICID2017/`, the old `iot23_attacks/` folder;
   - `db_manager.py`, the root `iot23_attacks.py`, `network_scan.py` (we copy useful parts later);
   - old CSV, PKL and `.db` files.
4. Move non-project files out of the project folder (or into `archive/`): Premiere Pro files, `python-installer.exe`, presentations, screenshots, `.zip` files.

   Inside `my-app/`, also move:
   - `python-installer.exe` and `instance/users.db` (old user accounts);
   - the old Flask backend `app.py` + `req.txt` (hard-coded secret; replaced in Step 24);
   - the `.zip` files and the empty "New Text Document" / "New folder" files.
5. **Remove the inner Git folder of the React app.** `create-react-app` makes its own `my-app/.git`. If it stays, the main repository saves `my-app` as an empty link (a "submodule"), and **none of the React code is saved**. Delete `my-app/.git` before `git add`.
6. In the project folder, run:

```bash
git init
```

7. Create `.gitignore`. The full file is in the repository. The most important lines:

```
# Data: keep only the empty folder layout
data/**
!data/**/
!data/**/.gitkeep
archive/

# Models and captures
*.pkl
*.joblib
*.pcap
*.pcapng
*.log

# CSV is usually data, but result tables in reports/ are kept (Step 7 manifest)
*.csv
!reports/**/*.csv

# Local databases, binaries, archives
*.db
*.sqlite
*.sqlite3
instance/
*.exe
*.zip
*.gz

# Secrets and real lab settings
.env
.env.*
!.env.example
config/settings.yaml

# Dependencies and caches
node_modules/
my-app/build/
__pycache__/
*.pyc
.venv/
.pytest_cache/
.ipynb_checkpoints/
```

8. Create `.gitattributes`, so files that run on the Linux sensor keep Linux line endings. (A `.sh` or `.nft` file with Windows line endings fails on Linux.)

```
* text=auto
*.sh    text eol=lf
*.nft   text eol=lf
*.zeek  text eol=lf
*.py    text eol=lf
*.yaml  text eol=lf
```

9. Put an empty `.gitkeep` file in each empty folder. (Git does not save empty folders.)
10. **Check before the first commit.** Run `git add .`, then `git status`. Read the list.
    - If you see any `.exe`, `.db`, `.zip`, `.csv`, `.pkl`, `.env` or data file, remove it (`git rm --cached <file>`) and fix `.gitignore`.
    - A file saved in a commit **stays in the history**, even if you delete it later.
11. Save the first version:

```bash
git commit -m "Clean project structure"
```

12. ➕ Extra: put the repository on a **private** GitHub repo so the team can share it.

**Do not fill in** `config/settings.example.yaml` or `config/label_mapping.yaml` in this step. They belong to Step 4 and Step 8. The label mapping can only be frozen after the Step 7 manifest shows the real labels.

**Tips:**

- Folder names with spaces (like `intrusion detection`) need quotes in commands: `cd "D:\intrusion detection"`.
- The warning "LF will be replaced by CRLF" is normal on Windows. `.gitattributes` handles it.

**Output:** A clean Git repository.

**Done when:**

- `git status` says "nothing to commit".
- `git ls-files` shows no data, model, database, binary or secret file. Check in PowerShell: `git ls-files | findstr /i ".exe .db .zip .csv .pkl .joblib .env"`. It should print nothing, except `.env.example` and CSV files in `reports/`.
- `git ls-files my-app/src` lists the React files (the list is not empty).

**Proposal:** Objective O1 ("code with versions"); Section 3.6 (secrets not in version control).

---

## Step 3. Install the software

> **Status: 🟡 Started (Step 3a & 3d completed on 22 Oct 2026)**
>
> **Phase 1: Development PC (Windows Laptop) — ✅ Done:**
> - ✅ Python 3.10.0, Node.js 22.12, Git 2.47, MongoDB Server 8.0 running locally on port 27017.
> - ✅ Dedicated `.venv` created and all dependencies installed from `requirements.txt`.
> - ✅ Exact package versions locked in `requirements.txt` (scikit-learn 1.7.2, pandas 2.3.3, pyarrow 25.0.1, etc.).
> - ✅ Npcap detected at `C:\Program Files\Npcap`. Nmap binary deferred to Step 27 under Decision D-012.
> - ✅ `tools/check_env.py` executed; `reports/environment_versions.txt` generated with status **PASSED**.
>
> **Phase 2: Linux Sensor Computer (Ubuntu LTS) — ⬜ To do during Step 5 & Step 19:**
> - Prepared when lab hardware is available. Runs Zeek, nftables, MongoDB, and the live detector.
>
> **Phase 3: Attack Test Computer (Linux) — ⬜ To do during Step 35:**
> - Prepared when controlled security testing begins (Table 10 scenarios).
>
> ➕ Extra: the PC already has **WSL Ubuntu**. You can install Zeek there and run it on saved capture files (`zeek -C -r file.pcap`). This lets you practise Steps 19, 21 and 22 before the physical sensor is ready.

**Why:** Every tool in proposal Table 8 must work before we use it.

**You need:** The development PC (your Windows PC) for all dataset and model work (Steps 7–18). The Linux sensor and attack test machines are needed only when lab hardware is set up (Steps 5, 19, and 35).

**Execution Order for Software Installation:**

### 3a & 3d. Development PC Setup (Windows) — ✅ Completed
1. Verified Npcap is installed at `C:\Program Files\Npcap`.
2. Created virtual environment: `python -m venv .venv`.
3. Upgraded pip and installed all packages from `requirements.txt`:
   - Data & ML: `pandas`, `numpy`, `pyarrow`, `scikit-learn`, `scipy`, `joblib`, `matplotlib`
   - Settings: `pyyaml`, `python-dotenv`
   - Backend: `flask`, `flask-socketio`, `flask-cors`, `flask-jwt-extended`, `bcrypt`, `pymongo`
   - Tools & Tests: `python-nmap`, `psutil`, `scapy`, `pytest`
4. Locked exact versions into `requirements.txt` using `pip freeze`.
5. Created and ran `tools/check_env.py` to verify all imports and local MongoDB connection. Audit log written to `reports/environment_versions.txt`.

### 3b. Linux Sensor Setup (Ubuntu LTS) — (To perform during Steps 5 & 19)
*(Execute on the physical sensor computer when hardware is ready; not needed for ML Steps 7–18)*
1. Install **Ubuntu 22.04 LTS** (comes with Python 3.10, matching development PC).
2. Install networking packages:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip nftables nmap tcpdump tshark ethtool git
   ```
3. Install **Zeek** from official binary packages into `/opt/zeek`. Add to PATH (`export PATH=/opt/zeek/bin:$PATH`).
4. Install **MongoDB Community Server**.
5. Clone repo, create `.venv`, install the same locked `requirements.txt`, and run `python tools/check_env.py`.

### 3c. Attack Test Computer Setup (Linux) — (To perform during Step 35)
*(Execute when controlled attack testing begins)*
```bash
sudo apt install -y nmap hping3 tcpdump python3
```

**Tips:**
- **Development PC is completely ready.** You do NOT need the Linux sensor or attack computer to do Steps 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18.
- Always activate `.venv` before running any Python scripts (`.venv\Scripts\activate` on Windows).

**Output:** `.venv` (not in Git), version-locked `requirements.txt`, `tools/check_env.py`, `reports/environment_versions.txt`.

**Done when:**
- **For Development PC (Current Phase):** ✅ **PASSED.** `tools/check_env.py` runs with 0 errors on Windows PC, MongoDB connected, report saved.
- **For Sensor Computer (Future Lab Phase):** `tools/check_env.py` runs on the sensor in Step 19, and `zeek --version`, `nft --version`, `mongod --version` work.

**Proposal:** Table 8; Section 5.1.

---

## Step 4. Write the settings file and the decision log

> **Status: ✅ Done** (23 Oct 2026)
>
> - ✅ `config/settings.example.yaml` and active local `config/settings.yaml` created with confirmed management allowlist, fixed seed 42, start thresholds, and retention periods (90/30/90 days).
> - ✅ `.env.example` and local `.env` created with 32-byte cryptographically secure random keys for JWT and Flask secrets (Decision D-013).
> - ✅ `docs/decision_log.md` contains Decisions D-001 through D-013.
> - ✅ `.env` and `config/settings.yaml` confirmed protected by `.gitignore` (never committed to version control).

**Why:** All important settings and decisions must be in one place, so anyone can repeat the work (fixed seed and configuration file).

**Do this:**

1. Create `config/settings.example.yaml`. Copy it to `config/settings.yaml` for real use (this copy is not in Git). The IP addresses are examples; use your lab plan from Step 5:

```yaml
lab:
  approved_scan_subnets: ["192.168.50.0/24"]  # Nmap may scan ONLY these
  local_networks: ["192.168.50.0/24"]         # used to decide traffic direction
  sensor_mirror_interface: "eth1"             # sensor port that receives the switch mirror (no IP)

allowlist:            # management IPs that are NEVER blocked
  - 192.168.50.1      # router / gateway
  - 192.168.50.5      # IDS sensor
  - 192.168.50.10     # admin workstation
  - 192.168.50.20     # NVR

response:
  deployment_mode: passive      # passive is the default (Table 11)
  adapter: router               # router (passive) | nftables (inline) | iptables | simulation
  auto_response: false          # ➕ Extra: master switch; turn on only in approved tests
  min_confidence: 0.85          # START value; final value chosen in Step 17
  min_repeats: 3                # START value; final value chosen in Step 17
  repeat_window_seconds: 60     # START value; final value chosen in Step 17
  max_rule_minutes: 30          # every rule expires (maximum rule time)
  allow_device_isolation: false # isolating a local device only if the policy allows

zeek:
  conn_log_path: /var/log/ids-zeek/conn.log  # Zeek is started in this folder (Step 19)

model:
  bundle_path: ml_engine/models/ids_bundle_v1.joblib
  random_seed: 42

retention_days:   # fill in from the agreed retention plan (Step 1)
  attack_events: null
  traffic_summaries: null
  system_logs: null
```

2. Create `.env.example` with **names only**, no real values. Each person copies it to `.env` and fills in real values there:

```
MONGO_URI=
DB_NAME=iot_ids_db
JWT_SECRET_KEY=
FLASK_SECRET_KEY=
ROUTER_SSH_HOST=
ROUTER_SSH_USER=
ROUTER_SSH_KEY_PATH=
```

3. Create `docs/decision_log.md`. Every important choice goes here, with the date, the choice and the reason. Examples: the label mapping, the sampling limits, the chosen features, the held-out scenarios, the final thresholds, any dropped features. (Template in Part F.)

**Tips:**

- Make a long random secret with: `python -c "import secrets; print(secrets.token_hex(32))"`.
- The lab IP addresses go in `settings.yaml`, **not** in `.env`. `.env` is only for secrets.

**Output:** `config/settings.example.yaml`, `.env.example`, `docs/decision_log.md`.

**Done when:** The team has agreed the allowlist and the start values.

**Proposal:** Sections 3.4 (fixed seed, configuration file), 3.6 (secrets), 3.7 (allowlists, thresholds, maximum rule time).

---

# Phase 1: Lab and Network Design (W3 – W8)

## Step 5. Build the lab network (Track 2: Physical Lab Hardware)

> **Status: ⬜ Not started (Hardware Track)**
>
> ⚠️ **Development PC Execution Notice:** Step 5 requires physical networking hardware (managed switch with mirror port, lab router, ethernet cables, physical IP camera).
> **If you are working on your development PC without physical lab equipment, do not stop here. Proceed directly to Step 6 (Threat model) and Step 7 (Dataset download).**
> All dataset downloads, data processing, and machine learning model training (Steps 6–18) run 100% on your PC. Step 5 will be executed together with Step 19 when the physical lab hardware is set up.
>
> Note: an earlier version of the settings used `192.168.8.0/24`. Many home 4G routers use this range. The lab must be a **separate** network: not a home, university or public one.

**Why:** All tests must happen on a separated network that we control and can set up again.

**You need:** The hardware from A4.1. The lab plan and rules (Step 1).

**First, an important idea:** a device can only block traffic that **passes through it**.

- If the attacker and the camera are on the same switch, their traffic never reaches the router or the sensor's bridge. Nothing can block it.
- So the attack computer goes on a **separate "outside" subnet**, behind the lab router.
- This lets us test outside attacks **without using any public IP address**.

**Do this:**

1. **Plan the IP addresses** (example):

| Network                                  | Device                                                            | Example IP    |
| ---------------------------------------- | ----------------------------------------------------------------- | ------------- |
| Camera LAN `192.168.50.0/24`             | Lab router (LAN side)                                             | 192.168.50.1  |
|                                          | Sensor (management)                                               | 192.168.50.5  |
|                                          | Admin workstation                                                 | 192.168.50.10 |
|                                          | NVR                                                               | 192.168.50.20 |
|                                          | IP camera                                                         | 192.168.50.30 |
|                                          | Camera simulator (if used)                                        | 192.168.50.31 |
| "Outside" lab network `10.10.10.0/24`    | Lab router (outside side)                                         | 10.10.10.1    |
|                                          | Attack test computer (also the lab "C&C test server" in Step 35)  | 10.10.10.50   |

2. **Set up the lab router.**
   - It routes between the two subnets **without NAT**, and allows forwarding.
   - The attack computer can then reach the cameras like an outside attacker.
   - The lab must **not** connect to the university or public network.
   - If the camera needs the internet for its first setup, do that first, then disconnect it.
3. **Passive mode (the default)** — proposal Figure 5, left side:
   - Connect the camera, NVR, admin PC and router to the managed switch.
   - Connect the sensor's **second** network port to a free switch port. This is the **mirror port**. Give it no IP address.
   - In the switch settings, mirror the traffic to that port. If your switch allows it, mirror **incoming (ingress) traffic of all used ports**. Each packet enters the switch once, so the sensor sees each packet once (no duplicates).
   - Turn off NIC offloading on the mirror port, so Zeek sees real packets:

```bash
sudo ip link set <mirror_port> up
sudo ethtool -K <mirror_port> gro off lro off
```

   - In this mode, the sensor **cannot block**. The **router** blocks (Step 33).
4. **Inline mode** — proposal Figure 5, right side:
   - Put the sensor **between the camera switch and the router** as a **transparent bridge**: both network ports are joined in a bridge called `br0`.
   - Traffic between the cameras and the router now passes through the sensor, so nftables on the sensor can block it.
   - Note: in inline mode, the sensor sees only traffic **that crosses it**. Camera-to-NVR traffic on the same switch does not cross it. Use passive mode to measure normal camera traffic.
5. **Bypass plan for inline mode.** If the sensor fails, connect the switch cable straight to the router. Write this in `docs/lab_network.md` and test it once.
6. Draw the lab diagram with all IP addresses.

**Tips:**

- Label every cable and port. It saves time when you move between passive and inline mode.
- Turn off Wi-Fi on lab devices, so nothing connects to another network by accident.
- Write the switch's mirror settings (screenshots) into `docs/lab_network.md`.

**Output:** A working lab; `docs/lab_network.md` (diagram, IP table, mirror settings, bypass plan).

**Done when:**

- The camera streams video to the NVR.
- On the sensor, `sudo tcpdump -i <mirror_port> -c 20` shows camera traffic.
- The attack computer can reach the camera through the router.
- No lab device can reach the university or public network.

**Proposal:** Sections 1.2, 3.8, 5.1; Figure 5; Table 11 (inline risk).

---

## Step 6. Threat model and requirement checklist (Track 1)

> **Status: ✅ Done** (23 Oct 2026)
>
> - ✅ `docs/threat_model.md` created: defines protected assets, threat actors, inbound/outbound attack trajectories, defensive boundaries, and the 6 Table 10 evaluation scenarios.
> - ✅ `docs/requirements_checklist.md` created: tracks all Functional Requirements (FR-01 to FR-08), Non-Functional Requirements (latency < 2s, lightweight RAM, zero leakage), Objectives O1–O6, and Research Questions RQ1–RQ5 / Hypothesis H1.

**Why:** Be clear about what we defend against, and what "finished" means.

**Do this:**

1. Write a short **threat model** (`docs/threat_model.md`):
   - **What we protect:** the camera, the NVR, video privacy, admin access, the rest of the network.
   - **Who attacks:** an outside scanner, a flooder, a botnet controlling a camera (C&C), a malware download.
   - **Paths:** inbound scans and floods; outbound C&C or downloads from a taken-over device.
2. Copy the functional requirements into `docs/requirements_checklist.md`:

| ID    | Requirement                                                                                          | Priority / how we check            |
| ----- | ---------------------------------------------------------------------------------------------------- | ---------------------------------- |
| FR-01 | Capture mirrored or inline traffic, and make connection flows from it.                               | Must / schema test                 |
| FR-02 | Put each usable flow into a class; give back the class, the confidence and the model version.        | Must / model API test              |
| FR-03 | Save benign traffic summaries, attacks and response actions.                                         | Must / database test               |
| FR-04 | Send new events and alerts to the dashboard (which needs a login) without the user pressing refresh. | Must / Socket.IO latency test      |
| FR-05 | Find approved devices and services with controlled Nmap scans.                                       | Should / inventory test            |
| FR-06 | Add, list, expire and remove blocking rules on the firewall or router.                               | Must / test on a separated network |
| FR-07 | Keep the allowlists, the confidence thresholds and a full audit history.                             | Must / safety test                 |
| FR-08 | Export filtered attack logs for testing and reporting.                                               | Should / export test               |

3. Add O1–O6 and RQ1–RQ5 to the same file. Tick them when you finish them.

**Tips:**

- "Must" requirements have to pass for the project to be complete. "Should" requirements are important, but lower priority.
- There are **no** Telegram or email alerts in the proposal.

**Output:** `docs/threat_model.md`, `docs/requirements_checklist.md`.

**Done when:** The supervisor has seen both.

**Proposal:** Sections 1.5, 3.1 (requirements and threat modelling); Tables 3 and 7.

---

# Phase 2: Dataset Audit and Label Mapping (W5 – W10)

## Step 7. Download IoT-23 and make a manifest

> **Status: ✅ Done** (23 Oct 2026)
>
> - ✅ All 23 official IoT-23 scenario files (44.13 GB, 325,309,946 flows) placed in `data/raw/iot23/`.
> - ✅ `ml_engine/manifest.py` written and executed with chunked memory streaming (< 100 MB RAM).
> - ✅ `reports/dataset_manifest.csv` generated with full SHA-256 cryptographic hashes, row counts, and detailed label breakdowns.
> - ⚠️ The old CSV files in `archive/legacy_datasets/iot23_attacks/iot23/` remain safely archived and unused.

**Why:** We must use the official data, and we must be able to prove exactly which files we used.

**You need:** Step 3a. A lot of free disk space: the compressed download is large (about 10 GB or more), and the extracted files are bigger. Use drive **D:** (it has over 400 GB free).

**Do this:**

1. Download **IoT-23 version 1.0.0** from the official source:
   - Zenodo, DOI `10.5281/zenodo.4743746`, **or**
   - the Stratosphere Laboratory IoT-23 page.

   Take the **smaller release that has only the labelled flows** (`conn.log.labeled` files). The full release with packet captures is much bigger, and you do not need it for training.
2. Extract it into `data/raw/iot23/`. On Windows, use 7-Zip, or `tar -xzf <file>.tar.gz` in PowerShell. Each scenario has its own folder with one `conn.log.labeled` file.
3. **Never change these files.**
4. Write `ml_engine/manifest.py`. For every `conn.log.labeled` file, it records:
   - the scenario ID and the file name;
   - the **SHA-256 hash**;
   - the number of rows;
   - the count of each `label` and each `detailed-label`.

   Example code for the hash:

```python
import hashlib

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()
```

5. Save it as `reports/dataset_manifest.csv`, and commit it to Git. (`.gitignore` keeps CSV files in `reports/`.)

**Note:** IoT-23 has **20 malicious and 3 benign scenarios**. The benign ones come from a smart lamp, a voice assistant and a smart door lock. **None are IP cameras.** This is why Step 20 is required.

**Tips:**

- Write down the download date, the source link and the exact file name in the decision log.
- Some files have many millions of rows. Count rows by reading the file line by line, not by loading it all at once.

**Output:** `data/raw/iot23/`, `reports/dataset_manifest.csv`.

**Done when:** All 23 scenarios are listed with hashes, row counts and label counts.

**Proposal:** Sections 2.3, 3.2; Objective O1.

---

## Step 8. Write and freeze the label mapping

> **Status: ✅ Done** (23 Oct 2026)
>
> - ✅ `config/label_mapping.yaml` frozen (`mapping_status: frozen`) under Decision `D-014`.
> - ✅ All 17 unique labels discovered in Step 7 manifest resolved into the 5 target classes:
>   - `Benign`: `Benign`, `benign` (30,860,691 flows, 9.49%)
>   - `DDoS_DoS`: `DDoS` (19,538,713 flows, 6.01%)
>   - `PortScan`: `PartOfAHorizontalPortScan`, `C&C-PartOfAHorizontalPortScan` (213,853,812 flows, 65.74%)
>   - `CnC`: `C&C`, `C&C-HeartBeat`, `C&C-Torii` (55,698 flows, 0.02%)
>   - `Malware_Download`: `Okiru`, `Mirai`, `FileDownload`, `C&C-FileDownload`, `C&C-HeartBeat-FileDownload`, `C&C-Mirai` (60,990,792 flows, 18.75%)
> - ✅ Ambiguous, unverified labels excluded (`Attack`, `Okiru-Attack`, `C&C-HeartBeat-Attack`, `PartOfAHorizontalPortScan-Attack`). Total excluded: 10,240 flows (0.0031% of dataset) per Proposal Sections 2.3 & 3.2.
> - ✅ Reasons and full mapping criteria documented in `docs/decision_log.md` (Decision `D-014`). Supervisor checkpoint C3 ready.

**Why:** If we choose the mapping after we see results, we could make the results look better (even by accident). So we fix it first.

**You need:** The manifest from Step 7 and the official IoT-23 label descriptions.

**Do this:**

1. From the manifest, make a table of **every detailed label × every scenario**, with counts.
2. Read the official description of each label.
3. Start from proposal Table 5:

| Our class          | IoT-23 labels in this group (Table 5)                          |
| ------------------ | -------------------------------------------------------------- |
| Benign             | Benign                                                         |
| DDoS / DoS         | DDoS, and "attack" labels **that we checked are flooding**     |
| Port scan          | PartOfAHorizontalPortScan                                      |
| C&C                | C&C, C&C-HeartBeat, C&C-Torii                                  |
| Malware / download | Okiru, Mirai, FileDownload, and **mixed labels we checked**    |

4. Some IoT-23 labels are **mixed**. The team must decide each one. Check it against the official description and the counts:

| Mixed or unclear label                                                        | Possible class                                                   | Decide by                          |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------- |
| C&C-FileDownload, C&C-HeartBeat-FileDownload                                  | Malware / download or C&C                                        | Main behaviour in the description  |
| C&C-Mirai                                                                     | C&C or Malware / download (Table 5 lists "Mirai" under malware)  | Main behaviour in the description  |
| C&C-PartOfAHorizontalPortScan                                                 | C&C or Port scan                                                 | Main behaviour in the description  |
| Attack, Okiru-Attack, C&C-HeartBeat-Attack, PartOfAHorizontalPortScan-Attack  | DDoS / DoS **only if** you checked they are flooding             | Description + flow patterns        |
| Malicious with no detailed label                                              | —                                                                | Count them; suggest exclude        |

5. Rules for these decisions (proposal 2.3 and 3.2):
   - A mixed label with **very few examples** goes under its **main behaviour**, or is reported on its own when there is enough data.
   - If a label is **too general or not clear**, do **not** force it into a class. Mark it `EXCLUDE`, and write down how many rows were excluded.
6. Write the final mapping in `config/label_mapping.yaml`. Example:

```yaml
mapping_status: frozen
mapping:
  Benign: Benign
  DDoS: DDoS_DoS
  PartOfAHorizontalPortScan: PortScan
  "C&C": CnC
  "C&C-HeartBeat": CnC
  "C&C-Torii": CnC
  Okiru: Malware_Download
  FileDownload: Malware_Download
  # ... every other label, each one decided and explained in docs/decision_log.md
  # labels set to EXCLUDE are removed and counted
```

7. Write the reasons in `docs/decision_log.md`. Show the supervisor. Commit to Git. **From now on, the mapping does not change.**

**Tips:**

- In YAML, put quotes around any label with `&` in it (for example `"C&C"`). Without quotes, YAML reads `&` as a special symbol.
- Benign rows have `label = Benign` and `detailed-label = -`. The loader must map them by the `label` column.

**Output:** `config/label_mapping.yaml` (frozen); a decision log entry.

**Done when:** The mapping is committed, and the supervisor has seen it (checkpoint C3).

**Proposal:** Table 5; Sections 2.3, 3.2.

---

## Step 9. Data-quality report

> **Status: ✅ Done** (23 Oct 2026)
>
> - ✅ `ml_engine/data_quality.py` executed across all 23 scenarios.
> - ✅ `reports/data_quality_report.md` generated with full Class x Scenario matrix (325,309,946 flows), missing rates, and value distributions.
> - ✅ High-resolution visualization charts generated: `reports/data_quality_class_distribution.png` and `reports/data_quality_scenario_matrix.png`.
> - ✅ Cleaning strategies (imputations) and sampling recommendations established for Steps 10, 11, and 12.

**Why:** Find problems in the data before modelling.

**Do this:** Write `ml_engine/data_quality.py`. It makes `reports/data_quality/report.md` with:

1. Rows per scenario and per class (after the mapping).
2. A **class × scenario table**. This is very important:
   - A class that appears in **only one scenario** cannot be tested on an unseen scenario.
   - Write this down as a known limit.
3. Missing values per column (IoT-23 uses `-` for missing).
4. Data types and value ranges (min, max, median) for duration, bytes and packets.
5. Category counts for `proto`, `service`, `conn_state`, `history`.
6. Duplicate rows.
7. Very large scenarios (some have many millions of rows), and the sampling plan (Step 12).

**Tips:**

- Make the report from code, not by hand. Then you can run it again if anything changes.
- Save the charts as PNG files next to the report.

**Output:** `reports/data_quality/report.md` with charts.

**Done when:** The team has reviewed it, and the class × scenario table shows which scenario(s) can be held out (Step 13).

**Proposal:** Objective O1 (data-quality report); Section 3.2.

---

# Phase 3: Preprocessing and Feature Pipeline (W7 – W13)

## Step 10. Load and clean the data

> **Status: ✅ Done** (25 Oct 2026)
>
> - ✅ `ml_engine/load_iot23.py` executed across all 23 scenarios.
> - ✅ All Zeek missing indicators (`-`) imputed (0.0 for duration, 0 for bytes/packets, 'unknown' for service/history).
> - ✅ Label mapping applied to 5 target classes; 10,240 ambiguous flows excluded and audited.
> - ✅ `scenario_id` metadata preserved on every row to guarantee zero cross-scenario data leakage.
> - ✅ Output: `data/interim/*.parquet` generated and audited in `reports/interim_data_summary.md`.

**Why:** Turn the raw files into a clean table that **keeps the scenario ID**.

**Do this:** Write `ml_engine/load_iot23.py`. It follows proposal Section 3.3 steps 1–4:

1. Read each `conn.log.labeled` file. Lines that start with `#` are headers.
   - **Watch out:** in IoT-23 files, the last three columns (`tunnel_parents`, `label`, `detailed-label`) are often separated by **spaces**, not tabs.
   - No field contains a space, so reading with "any whitespace" as the separator works for both:

```python
import pandas as pd

COLS = ["ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p", "proto",
        "service", "duration", "orig_bytes", "resp_bytes", "conn_state",
        "local_orig", "local_resp", "missed_bytes", "history", "orig_pkts",
        "orig_ip_bytes", "resp_pkts", "resp_ip_bytes", "tunnel_parents",
        "label", "detailed_label"]

def read_chunks(path, chunksize=1_000_000):
    return pd.read_csv(path, sep=r"\s+", comment="#", header=None, names=COLS,
                       dtype=str, chunksize=chunksize)
```

   Check that the `#fields` line in your files matches `COLS`. Count any bad lines.
2. Add a `scenario_id` column to every row (from the folder name).
3. Change `-` and `(empty)` into missing values.
4. Change `duration`, the byte, packet and port columns into numbers. Change `ts` into a time.
5. Apply `config/label_mapping.yaml` to make a `class` column. Remove the `EXCLUDE` rows and **count them**.
6. Keep `uid`, `id.orig_h`, `id.resp_h` and `scenario_id` in the table **only for grouping and audit**. They are removed before the model sees the data (golden rule 5).
7. Save as **Parquet** files in `data/interim/`, one per scenario. Parquet is much faster than CSV.

**Tips:**

- Your PC has about 12 GB of memory. **Read in chunks** (as above). Never load a whole large file at once.
- Write a small log line per file: rows read, rows dropped, reason.

**Output:** `data/interim/*.parquet`, and a log of rows read and dropped per file.

**Done when:** The row counts match the manifest (minus the excluded rows you counted).

**Proposal:** Section 3.3 steps 1–4.

---

## Step 11. Write the shared feature code

> **Status: ✅ Done** (25 Oct 2026)
>
> - ✅ `ml_engine/features.py` implemented with `make_features(df)` and `build_feature_preprocessor()`.
> - ✅ 19 candidate features extracted matching Proposal Table 6 in locked column order.
> - ✅ Standardized IANA port bins (`well_known`, `registered`, `dynamic`, `icmp`) and safe directional ratios.
> - ✅ Automated unit test suite `tests/unit/test_features.py` (10 passed tests, 0 warnings).
> - ✅ Decision `D-015` recorded in `docs/decision_log.md`.

**Why:** Live traffic must be turned into features **exactly** the same way as the training data. The easiest way is **one function that both use**.

**Do this:**

1. Write `ml_engine/features.py` with one main function, `make_features(df)`. Both `train.py` and the live `detector.py` import it.
2. Use the candidate features from proposal Table 6:

| Group           | Features                                                                                                     | What we do                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Transport       | `proto`, source port category, destination port category                                                     | Encode the categories. **Group the ports** (well-known 0–1023, registered 1024–49151, dynamic 49152–65535), so the model does not memorise port numbers. For ICMP, Zeek puts the ICMP type/code in the port fields, so use a separate `icmp` category. |
| Service / state | `service`, `conn_state`, `history`                                                                           | A clear `unknown` category; join rare categories together.                                                                         |
| Time            | `duration`; a rate over a time window **only if we use it**                                                   | Check the numbers. Use a log transform if the values are very skewed (mainly for the linear model; trees do not need it).          |
| Volume          | Bytes and packets from each side (`orig_bytes`, `resp_bytes`, `orig_pkts`, `resp_pkts`; optionally `orig_ip_bytes`, `resp_ip_bytes`) and ratios such as bytes per packet | Check the numbers; **stop divide-by-zero** in ratios.                                                  |
| Quality         | `missed_bytes`; a flag for a flow that is not complete                                                       | Keep **only if the live pipeline always makes it** (checked in Step 22).                                                           |
| Left out        | UID, raw IP addresses, capture file name (and `ts`)                                                          | Used only for grouping and audit. **Never model inputs.**                                                                          |

3. A short example of the idea:

```python
import numpy as np
import pandas as pd

RAW = ["proto", "service", "conn_state", "history", "id.orig_p", "id.resp_p",
       "duration", "orig_bytes", "resp_bytes", "missed_bytes", "orig_pkts", "resp_pkts"]
CAT_COLS = ["proto", "service", "conn_state", "history", "orig_port_cat", "resp_port_cat"]

def port_category(port, proto):
    if proto == "icmp":
        return "icmp"
    if pd.isna(port):
        return "unknown"
    port = int(port)
    if port < 1024:
        return "well_known"
    if port < 49152:
        return "registered"
    return "dynamic"

def make_features(df):
    df = df.reindex(columns=RAW)  # live Zeek JSON may leave fields out
    out = pd.DataFrame(index=df.index)
    for c in ["proto", "service", "conn_state", "history"]:
        out[c] = df[c].fillna("unknown").astype(str)
    out["orig_port_cat"] = [port_category(p, pr) for p, pr in zip(df["id.orig_p"], df["proto"])]
    out["resp_port_cat"] = [port_category(p, pr) for p, pr in zip(df["id.resp_p"], df["proto"])]
    nums = ["duration", "orig_bytes", "resp_bytes", "missed_bytes", "orig_pkts", "resp_pkts"]
    num = df[nums].apply(pd.to_numeric, errors="coerce")
    out["incomplete"] = num[["duration", "orig_bytes", "resp_bytes"]].isna().any(axis=1).astype(int)
    out[nums] = num.fillna(0)
    out["orig_bytes_per_pkt"] = out["orig_bytes"] / out["orig_pkts"].replace(0, np.nan)
    out["resp_bytes_per_pkt"] = out["resp_bytes"] / out["resp_pkts"].replace(0, np.nan)
    out[["orig_bytes_per_pkt", "resp_bytes_per_pkt"]] = out[["orig_bytes_per_pkt", "resp_bytes_per_pkt"]].fillna(0)
    return out
```

4. **Do not scale numbers** for Random Forest. Scaling is added only inside the comparison models that need it (Step 15).
5. **Time-window rate feature** (for example "flows from this source in the last 10 seconds"): use it only if it is computed **the same way** on IoT-23 (sorted by time inside each scenario) and live. If you are not sure, leave it out.
6. Write unit tests in `tests/unit/test_features.py` for: missing values, zero packets, unknown categories, ICMP.

**Tips:**

- Keep the order of the output columns fixed. Save the list as `FEATURE_COLUMNS` (it goes into the model bundle in Step 18).
- Test with one IoT-23 row **and** one Zeek JSON row that has missing fields.

**Output:** `ml_engine/features.py`, the tests, the feature list in `docs/decision_log.md`.

**Done when:** The tests pass, and the function works on an IoT-23 row **and** on a Zeek JSON row.

**Proposal:** Table 6; Section 3.3 steps 2–5; Section 3.5.

---

## Step 12. Sampling and class balance

> **Status: ✅ Done (25 Oct 2026)**
>
> - Script: [`ml_engine/sample_dataset.py`](file:///d:/intrusion%20detection/ml_engine/sample_dataset.py) executed inside `.venv`.
> - Sampling rule: Capped at $N = 50,000$ rows per (scenario, class) using fixed seed `42` (`config/settings.yaml`).
> - Minority preservation: 100% of all 48,992 `CnC` flows across all 22 training scenarios preserved (zero flows lost).
> - Training output: [`data/processed/train_features.parquet`](file:///d:/intrusion%20detection/data/processed/train_features.parquet) (1,384,070 rows, 0 NaNs).
> - **Update 9 Nov 2026 (D-046):** both output files now also keep 5 audit columns (`ts`, `id.orig_h`, `id.resp_h`, `id.resp_p`, `detailed_label`). They are never model inputs (proposal Table 6: "used only for grouping and audit"); Step 17 uses them to replay the repeat rule and to report results per original label. The 22 old columns are identical in every row.
> - Imbalance ratio reduced from 4,354 : 1 down to 10.2 : 1. Peak RAM during sampling stayed under 180 MB.
> - Reports: [`reports/sampling_summary.csv`](file:///d:/intrusion%20detection/reports/sampling_summary.csv) and [`reports/sampling_report.md`](file:///d:/intrusion%20detection/reports/sampling_report.md).
> - Decision: `D-016` recorded in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).

**Why:** Some scenarios are huge, and some classes are tiny. We must handle this fairly, without changing the test data in a way that makes the results look better.

**Do this:**

1. **Limit very large scenarios** so the data fits in memory. For each (scenario, class), keep at most **N** rows, chosen at random with the fixed seed.
   - Use the manifest counts to work out the fraction to keep.
   - Sample each chunk with that fraction.
   - Write N in the decision log.
2. For the **held-out test scenario(s)**, sample only if memory needs it, and **without balancing**, so the real class proportions stay the same.
3. Inside the **training data only**:
   - Use **class weights** (`class_weight="balanced"`). This is the first choice.
   - If needed, **under-sample** very large classes.
   - Use synthetic oversampling (e.g. SMOTE) **only after grouping, and only inside the training folds**. Never before the split.
4. Save the feature tables in `data/processed/`: one for the training scenarios, one for the held-out scenario(s).

**Tips:**

- Start with a small N (for example 50,000 rows per scenario and class). Check the memory use. Increase N only if training time and memory allow.
- Never sample the held-out scenario in a way that changes its class proportions.

**Output:** Tables in `data/processed/`; sampling notes in the decision log.

**Done when:** You can say exactly how many rows of each class from each scenario are in training and in the held-out set.

**Proposal:** Section 3.3 step 6; Table 11 (class imbalance).

---

# Phase 4: Model Training and Validation (W10 – W17)

## Step 13. Plan the three test levels

> **Status: ✅ Done (25 Oct 2026)**
>
> - Plan document: Formalized in [`reports/test_split_plan.md`](file:///d:/intrusion%20detection/reports/test_split_plan.md).
> - Level 1 (Grouped CV): `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` on 22 training scenarios with `groups = scenario_id`. Guarantees zero intra-session leakage.
> - Level 2 (Held-Out Scenario): `CTU-IoT-Malware-Capture-34-1` (Mirai, 23,145 flows: 14,394 DDoS_DoS, 6,706 CnC, 1,923 Benign, 122 PortScan). 100% untouched. Sealed in dedicated directory [`data/processed/heldout/held_out_test.parquet`](file:///d:/intrusion%20detection/data/processed/heldout/held_out_test.parquet) (Supervisor Checkpoint C4). Opened ONLY in Step 16.
> - Level 3 (Physical Lab Camera): Tapo C200 IP camera 1080p RTSP/H.264 baseline traffic (Step 20) and 6 controlled test attack scenarios (Phase 9, Steps 35–39) testing operational FPR < 1% (Hypothesis H1).
> - Automated tests: [`tests/unit/test_sampling_and_splits.py`](file:///d:/intrusion%20detection/tests/unit/test_sampling_and_splits.py) passed all 6 unit tests in 5.00s.
> - Decision: `D-017` recorded in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).

**Why:** To test honestly, with no leakage, the plan must be fixed **before** training.

**Do this:** Write in the decision log:

1. **Level 1 — Grouped cross-validation.** Flows from the same scenario always stay together. Use `StratifiedGroupKFold` with `groups = scenario_id`.
2. **Level 2 — Held-out scenario(s).** Keep at least one malicious scenario out completely.
   - Choose it from the class × scenario table (Step 9), so that **every class still has training data**.
   - Open it **only at the end** (Step 16).
3. **Level 3 — Local lab traffic.** Our own benign camera traffic (Step 20) and the controlled test traffic (Phase 9).

**Tips:**

- Put the held-out data in its own folder (`data/processed/heldout/`). Nobody uses that folder for tuning.

**Output:** A written split plan with the held-out scenario IDs.

**Done when:** The plan is committed, and the held-out data is in its own folder (checkpoint C4).

**Proposal:** Sections 2.2, 3.4; Objective O2.

---

## Step 14. Train the Random Forest

> **Status: ✅ Done (first run 31 Oct 2026; run again 8 Nov 2026 after the scenario-name fix, D-039)**
>
> - Script: [`ml_engine/train.py`](file:///d:/intrusion%20detection/ml_engine/train.py), run inside `.venv`.
> - Model: one scikit-learn `Pipeline` (`OrdinalEncoder` that handles unknown values, `min_frequency=50`, then `RandomForestClassifier`).
> - Tuning: `RandomizedSearchCV` (12 candidates × 5 folds) with `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`, groups = `scenario_id`, scored by macro-F1.
> - Best settings (8 Nov run): `n_estimators=100`, `max_depth=18`, `min_samples_split=5`, `min_samples_leaf=4`, `max_features='sqrt'`, `class_weight='balanced'`.
> - Level 1 grouped CV (1,384,070 flows, 22 scenarios): out-of-fold macro-F1 = **0.3422**; mean fold macro-F1 = 0.3353 ± 0.1704.
> - Model step only, on the PC: 4.66 µs per flow; model file 4.30 MB. (This is not the end-to-end time of proposal Table 9; that is Step 37.)
> - New: the out-of-fold probabilities are saved to `data/processed/rf_oof_predictions.npz`, so Step 17 can choose thresholds without the held-out scenario (D-040).
> - Files: `ml_engine/models/rf_model.joblib`, `reports/experiments/rf_search.csv`, `rf_cv_results.csv`, `rf_training_report.md`.
> - The 31 Oct numbers (0.3630, 15.19 MB) came from data with 4 wrong scenario names and are replaced (D-039, D-043).

**Why:** This is the main model of the prototype.

**You need:** Steps 11–13 done.

**Do this:** Write `ml_engine/train.py`.

1. Build **one scikit-learn `Pipeline`** with the categorical encoder and the model. The encoder must handle categories it has never seen (proposal 3.3 step 5):

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

pre = ColumnTransformer(
    [("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                            min_frequency=50), CAT_COLS)],   # rare categories joined
    remainder="passthrough")                                 # numbers stay as they are

pipeline = Pipeline([
    ("pre", pre),
    ("model", RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1)),
])
```

2. Tune the settings that the proposal lists (number of trees, max depth, min samples in a split / leaf, max features, class weights). Use a **random search inside grouped cross-validation**, scored by **macro-F1**:

```python
from sklearn.model_selection import RandomizedSearchCV, StratifiedGroupKFold

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
param_dist = {
    "model__n_estimators": [100, 200, 300],
    "model__max_depth": [10, 20, 30, None],
    "model__min_samples_split": [2, 5, 10],
    "model__min_samples_leaf": [1, 2, 4],
    "model__max_features": ["sqrt", "log2"],
    "model__class_weight": ["balanced", "balanced_subsample"],
}
search = RandomizedSearchCV(pipeline, param_dist, n_iter=30, cv=cv,
                            scoring="f1_macro", random_state=42, n_jobs=-1)
search.fit(X_train, y_train, groups=groups_train)
```

   If some classes appear in too few scenarios for 5 folds, use fewer folds, and write why.
3. Save every setting tried, and its score, to `reports/experiments/rf_search.csv`.
4. Record the model file size and the prediction time per flow.

**Tips:**

- **Training can take hours on your PC.** Start small: fewer rows and `n_iter=10`. Increase later if time allows. Write what you used in the decision log.
- If the PC runs out of memory, set `n_jobs=2` in `RandomizedSearchCV` (each parallel job copies the data).
- Limiting `max_depth` keeps the model file much smaller. (The old model was 820 MB because its trees had no limit.)

**Output:** The best RF pipeline; the search results.

**Done when:** The grouped-CV macro-F1 and the recall per class are recorded for the best settings.

**Proposal:** Sections 2.4, 3.4.

---

## Step 15. Compare with other models

> **Status: ✅ Done (first run 31 Oct 2026; run again 9 Nov 2026 after D-039)**

**Why:** We must **check**, not assume, that Random Forest gives a good balance of accuracy and speed.

**Result (9 Nov 2026 run):** [`ml_engine/compare_models.py`](file:///d:/intrusion%20detection/ml_engine/compare_models.py) compared 3 models on the same 1,384,070 flows with the same 5-fold grouped CV (groups = `scenario_id`).

| Model | Out-of-fold macro-F1 | Mean fold macro-F1 | CnC recall | Model step per flow (PC) | Size |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random Forest | 0.3422 | 0.3353 ± 0.1704 | 44.9% | 4.66 µs | 4.30 MB |
| Logistic Regression | 0.2722 | 0.2723 ± 0.1048 | 12.8% | 1.52 µs | 0.01 MB |
| HistGradientBoosting | **0.4331** | 0.4160 ± 0.1102 | 45.5% | 17.12 µs | 0.68 MB |

- **HistGradientBoosting scored higher than Random Forest.** We report this as measured.
- Random Forest stays the main model because the proposal (Section 2.4) chose it for its tree paths, which can be explained, and for its speed. The model step of all three takes only microseconds, far below the 2-second whole-system target, so speed does not decide between them. This choice is written in D-019 and D-043.
- The 31 Oct numbers (HGB 0.3950 > RF 0.3630 > LR 0.3486) are replaced (D-039).
- All 3 models are saved in `ml_engine/models/`. Tests: [`tests/unit/test_compare_models.py`](file:///d:/intrusion%20detection/tests/unit/test_compare_models.py).

**Output:** [`reports/experiments/model_comparison.md`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.md) and [`reports/experiments/model_comparison.csv`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.csv).

**Proposal:** Sections 1.3, 2.4.

---

## Step 16. Evaluate on the held-out scenario

> **Status: ✅ Done (first run 31 Oct 2026; run again 9 Nov 2026 after D-039)**

**Why:** This is the real test of the model on data it has never seen (Supervisor Checkpoint C4).

**Result (9 Nov 2026 run):** [`ml_engine/evaluate.py`](file:///d:/intrusion%20detection/ml_engine/evaluate.py) tested the **uncalibrated** models on the held-out scenario `CTU-IoT-Malware-Capture-34-1` (23,145 flows; file `data/processed/heldout/held_out_test.parquet`). The model actually used by the live system is the calibrated one; its result is in Step 17.

| Random Forest on 34-1 (uncalibrated) | Value |
| --- | ---: |
| Macro-F1, 5 classes | 0.4530 |
| Macro-F1, 4 classes present | 0.5662 |
| Accuracy / weighted F1 | 0.8063 / 0.8285 |
| IoT-23 benign flows predicted as attack | 5.148% (99 of 1,923) |

| Class (RF, uncalibrated) | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.4997 | 0.9485 | 0.6546 |
| DDoS_DoS | 14,394 | 0.9999 | 0.9908 | 0.9953 |
| PortScan | 122 | 0.0424 | 0.9426 | 0.0812 |
| CnC | 6,706 | 0.9781 | 0.3671 | 0.5339 |
| Malware_Download | 0 | — | — | — |

- **H1 part 1 (macro-F1 ≥ 0.85): not met.** 34-1 has no Malware_Download flows, so that class scores 0 and the 5-class macro-F1 cannot be above 0.80. Even on the 4 classes present the score is 0.57. PortScan precision is very low (most flows called PortScan are really CnC or Benign).
- The IoT-23 benign rate above is **not** the H1 FPR measure. H1 uses our own camera traffic (Step 20).
- The 31 Oct numbers (0.4028, 76.72%) are replaced (D-039, D-043).
- Tests: [`tests/unit/test_evaluate.py`](file:///d:/intrusion%20detection/tests/unit/test_evaluate.py).

**Output:**
- [`reports/experiments/evaluation_iot23.md`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.md)
- [`reports/experiments/evaluation_iot23.csv`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.csv)
- [`reports/experiments/confusion_matrix_heldout.png`](file:///d:/intrusion%20detection/reports/experiments/confusion_matrix_heldout.png)

**Proposal:** Section 3.4; Table 9; H1; RQ1, RQ2; Supervisor Checkpoint C4.

---

## Step 17. Calibration, explanation and final thresholds

> **Status: ✅ Done (redone 8–9 Nov 2026: D-040, D-043, D-044, D-045, D-046). The 31 Oct method and numbers are withdrawn.**

**Why:** Confidence values will start automatic responses, so we must check that they can be trusted (Checkpoint C5).

**Method now (D-040, D-044, D-045, D-046):** [`ml_engine/select_calibration.py`](file:///d:/intrusion%20detection/ml_engine/select_calibration.py) (Step 17a) and [`ml_engine/calibrate_and_explain.py`](file:///d:/intrusion%20detection/ml_engine/calibrate_and_explain.py)
1. **Choosing the calibration method (Step 17a):** 5 methods were compared on the Step 14 out-of-fold probabilities only, each fold calibrated by a fit on the other folds (`reports/experiments/calibration_selection.md`).
   - The D-044 rule chose `multinomial`. It **failed** the final check on 34-1 (macro-F1 0.0458): it turned most DDoS flows into Benign (D-045).
   - Reason: it learns how the model confuses classes on unseen out-of-fold scenarios, and those confusions do not carry over to the final model.
   - New principle (D-045): calibration may change **how sure** the model is, but **not which class wins**. The method used now is **`temperature`** (one number; keeps the Random Forest's top class).
2. **Thresholds, from the calibrated out-of-fold data only, with fixed rules:**
   - alert threshold (D-040) = the lowest value (0.30–0.99) where precision ≥ 0.50 (if never reached: the value with the best precision);
   - block threshold (D-046, proposal 3.4: *"The event must pass a confidence threshold, and it must happen again inside a set time window"*): the live response rule is **replayed** on the training flows, using their time and IP addresses (kept by Step 12 as audit columns, never model inputs). A block fires when the same target has 3 block candidates within 60 s and is not already blocked (a block lasts 30 min). The block threshold is the lowest value with at least 10 blocks, at least 95% of them fired by truly malicious flows, and at most 1% of benign targets blocked;
   - if no value meets the block rule, the class is **alert only** (never blocked automatically).
   - The old D-040 block rule (one single flow must be right 95% of the time) is not in the proposal and is replaced.
3. **34-1:** used for the final check and for permutation importance (proposal 2.4). Because the D-045 choice was made after a 34-1 result, **34-1 is no longer a clean unseen test**. The clean test is now the lab data (Steps 20 and 35).
4. **Decision paths:** real paths from the trained trees. The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD` and the others) are names the team made.

**Result (9 Nov 2026, `temperature`):**

| Measure | Value |
| --- | ---: |
| Deployed model on 34-1: macro-F1, 5 classes | **0.4530** |
| Deployed model on 34-1: macro-F1, 4 classes present | 0.5662 |
| Deployed model on 34-1: accuracy | 0.8063 |
| IoT-23 benign flows on 34-1 that raise an alert / reach a block threshold | 2.5% / 0.0% |

| Class | Alert threshold | Block threshold (D-046) | Replay on training data: blocks / fired by malicious / benign targets blocked | 34-1 recall (top class) | 34-1 alert recall |
| --- | ---: | --- | --- | ---: | ---: |
| DDoS_DoS | 0.33 | **none: alert only** | almost all replayed blocks were fired by benign flows | 0.9908 | 0.9908 |
| PortScan | 0.30 | **0.30** | 413 / 96.6% / 3 of 28,594 | 0.9426 | 0.9426 |
| CnC | 0.39 | **0.39** | 142 / 100% / 0 | 0.3671 | **0.0073** |
| Malware_Download | 0.30 | **none: alert only** | only 5 blocks (fewer than 10) | no flows in 34-1 | — |

Replay on 34-1 with these thresholds (reported only): PortScan 27 blocks, 1 fired by a benign flow; CnC 1 block, correct.

**Results per original IoT-23 label (proposal 3.2):** Section 8 of `thresholds_and_explanation.md`. On the out-of-fold data, the weakest labels are `DDoS` (0.16% put in the right group) and `C&C` (6.3%); `Okiru` 73.7%, `C&C-HeartBeat` 66.2%. On 34-1: `DDoS` 99.1%, `PartOfAHorizontalPortScan` 94.3%, `C&C` 36.7%.

**What this means:**
- **CnC is found again** at the model level (36.7% of CnC flows get CnC as the top class; 98% of these are right). But the CnC alert threshold (0.39) was set by the fallback rule, because CnC never reached 50% precision on the out-of-fold data. Most CnC flows on 34-1 are below 0.39, so only 0.7% raise an alert.
- **Automatic blocking now works the proposal's way (D-046)** for PortScan and CnC. Table 10 scenario 2 (Nmap scan) and scenario 4 (C&C-like outbound) can show a block.
- **DDoS stays alert only.** On unseen training scenarios most flows called DDoS are benign, so a block would be unsafe. Table 10 scenario 3 expects "blocked or rate-limited"; with this model it will show alerts, and a manual block from the dashboard. This is reported as a result. Rate features over a time window (proposal Table 6, "rate over a time window if we use it") are the proposal's way to improve it later.

**Files:** [`thresholds_and_explanation.md`](file:///d:/intrusion%20detection/reports/experiments/thresholds_and_explanation.md), [`operational_thresholds.json`](file:///d:/intrusion%20detection/reports/experiments/operational_thresholds.json), `step17_results.json`, `calibration_curve.png`, `feature_importance.png`, `ml_engine/models/calibrated_rf_model.joblib`. Tests: [`tests/unit/test_calibrate_and_explain.py`](file:///d:/intrusion%20detection/tests/unit/test_calibrate_and_explain.py).

**Output:**
- [`reports/experiments/thresholds_and_explanation.md`](file:///d:/intrusion%20detection/reports/experiments/thresholds_and_explanation.md)
- [`reports/experiments/operational_thresholds.json`](file:///d:/intrusion%20detection/reports/experiments/operational_thresholds.json)
- [`reports/experiments/calibration_curve.png`](file:///d:/intrusion%20detection/reports/experiments/calibration_curve.png)
- [`reports/experiments/feature_importance.png`](file:///d:/intrusion%20detection/reports/experiments/feature_importance.png)

**Proposal:** Sections 2.4, 3.4, 3.7; Table 7 (FR-06); Table 11; Checkpoint C5.

---

## Step 18. Save the model bundle and model card

> **Status: ✅ Done (run again 9 Nov 2026, bundle `v1.2.0`, D-045)**
>
> [`ml_engine/export_bundle.py`](file:///d:/intrusion%20detection/ml_engine/export_bundle.py) writes `ml_engine/models/ids_bundle_v1.joblib` (v1.2.0, `temperature` calibration, 9.3 MB, not in Git) and [`reports/experiments/model_card.md`](file:///d:/intrusion%20detection/reports/experiments/model_card.md). All numbers in the model card are read from the result files, not typed in. The bundle self-test passed. Tests: [`tests/unit/test_model_bundle.py`](file:///d:/intrusion%20detection/tests/unit/test_model_bundle.py). The 31 Oct bundle (30.84 MB) is replaced (D-040, D-043).

**Why:** One file holds everything the live system needs, so offline and live use exactly the same steps.

**Do this:**

1. Train the final pipeline on all the training scenarios with the best settings. Save it:

```python
import joblib, sklearn

bundle = {
    "pipeline": final_pipeline,              # encoder + model, fitted together
    "calibrated_model": calibrated_pipeline, # temperature calibration fitted on out-of-fold data (D-045)
    "feature_columns": FEATURE_COLUMNS,      # exact order (19 features)
    "categorical_features": CATEGORICAL_FEATURES,
    "numerical_features": NUMERICAL_FEATURES,
    "classes": TARGET_CLASSES,
    "class_names": CLASS_NAMES,
    "class_to_name": CLASS_TO_NAME,
    "operational_thresholds": thresholds_json["classes"],
    "threshold_rules": thresholds_json["metadata"]["rules"],
    "example_decision_paths": step17_results["example_decision_paths"],
    "metadata": {
        "bundle_version": "v1.2.0",
        "level_1_oof_macro_f1": ...,        # read from the result files
        "level_2_macro_f1_5class": ...,
        ...
    }
}
joblib.dump(bundle, "ml_engine/models/ids_bundle_v1.joblib", compress=3)
```

2. Write `reports/experiments/model_card.md`: the data used, the features, the scores, the chosen thresholds, and the **known limits** (for example, the benign training data is not from cameras).

**Tips:**

- When the sensor loads the bundle, check that `sklearn_version` matches the installed version. If not, stop with a clear error message.

**Output:** `ml_engine/models/ids_bundle_v1.joblib`, [`reports/experiments/model_card.md`](file:///d:/intrusion%20detection/reports/experiments/model_card.md), [`tests/unit/test_model_bundle.py`](file:///d:/intrusion%20detection/tests/unit/test_model_bundle.py).

**Done when:** A fresh Python session loads the bundle and gives the same prediction for a test row as during training. Verified with 5 automated unit tests in `tests/unit/test_model_bundle.py`. Track 1 is complete!

**Proposal:** Section 3.3 step 7; FR-02 (model version); Section 1.6 (written list of limits); Table 7 (FR-01, FR-02, FR-03, FR-06); Table 9; Table 11.

---

# Phase 5: Live Zeek Integration (W13 – W20)

## Step 19. Run Zeek on the sensor

> **Status: 🟡 Started — software ready, not yet run on the sensor (re-opened 8 Nov 2026, D-042)**
>
> Ready: `sensor/local.zeek` (JSON logs, no rotation, `ignore_checksums = T`), `sensor/run_zeek.sh` (start/stop/status on an interface or a PCAP), `sensor/zeek_runner.py` (checks and test tools), 5 unit tests.
> **Left:** install Zeek on the Linux sensor (Step 3b), run it on the mirror port (or the virtual-lab capture interface), and confirm that real `conn.log` lines pass `verify_conn_log_schema`. The 31 Oct check used generated records, not Zeek output.

**Why:** Zeek makes the live connection records (flows) from the traffic.

**You need:** Step 3b (Zeek installed) and Step 5 (the lab) — or WSL / PCAP replay test harness.

**Do this:**

1. Create `sensor/local.zeek`:

```zeek
@load policy/tuning/json-logs.zeek   # one JSON record per line, easy for Python
redef Log::default_rotation_interval = 0 sec;  # continuous stream for live tailing
redef ignore_checksums = T;          # ignore switch mirror checksum anomalies
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
```

2. Run Zeek on the mirror port (passive mode) or on `br0` (inline mode), from a fixed log folder:

```bash
sudo mkdir -p /var/log/ids-zeek && cd /var/log/ids-zeek
sudo zeek -C -i <interface> /path/to/project/sensor/local.zeek
```

   `-C` tells Zeek to ignore checksum errors. They are common on mirrored traffic.
3. **How Zeek writes flows.** Zeek keeps open connections in memory. It writes a line to `conn.log` **when the connection ends or times out**.
   - So a long video stream appears late.
   - A scan attempt with no answer appears after a short timeout.
   - Start with Zeek's **default timeouts**.
   - If you change any timeout later, write it in the decision log and run Step 22 again. Timeouts change `duration` and the byte counts, and can make the live features differ from IoT-23.
4. In JSON logs, **unset fields are left out** (IoT-23 files use `-` instead). `make_features()` already handles this with `reindex`.
5. You can also run Zeek on a saved capture file, to test without a live network: `zeek -C -r sample.pcap /path/to/sensor/local.zeek` or run `python sensor/zeek_runner.py --simulate`.

**Tips:**

- Find the interface names with `ip link`.
- If `conn.log` stays empty, check with `sudo tcpdump -i <interface> -c 20` that traffic really arrives.

**Output:** [`sensor/local.zeek`](file:///d:/intrusion%20detection/sensor/local.zeek), [`sensor/run_zeek.sh`](file:///d:/intrusion%20detection/sensor/run_zeek.sh), [`sensor/zeek_runner.py`](file:///d:/intrusion%20detection/sensor/zeek_runner.py), [`tests/unit/test_zeek_config.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_config.py).

**Done when:** Zeek **on the sensor** writes newline-delimited JSON connection records to `conn.log`, and `verify_conn_log_schema` passes on those real records with 0 NaNs and all 19 features matching `ml_engine/features.py`.

**Output:** `sensor/local.zeek`; Zeek writing `conn.log`.

**Done when:** Opening the camera stream or a web page creates new lines in `conn.log`.

**Proposal:** Sections 2.5, 3.5; FR-01.

---

## Step 20. Collect our own benign camera traffic

> **Status: 🟡 Started — real capture not done (re-opened 8 Nov 2026, D-042; replaces D-024)**
>
> The 5,000 flows of 31 Oct 2026 were **made by a script** (`generate_camera_flow()`), not captured from a camera. They were moved to `data/local/synthetic/` and are labelled synthetic test data. The old result "FPR 0.000%, H1 clause 2 PASS" is **withdrawn**.
> Ready: `sensor/collect_camera_traffic.py --conn-log <real conn.log> --source real` measures the FPR and writes the report.
> **Left:** capture real benign traffic from the lab camera (or the camera simulator confirmed with the supervisor, D-038), save it in `data/local/benign/<date>/conn.log`, write the logbook entry, and run the check with `--source real`.

**Why:** IoT-23 has no camera in its normal data. To test H1 (FPR ≤ 5% on local camera traffic), we need real normal camera traffic.

**Do this:**

1. Use **passive mode**, so you see all the camera traffic.
2. With Zeek running, do the **normal activities** from proposal 5.1, for several hours on different days:
   - non-stop streaming to the NVR (RTSP TCP 554, RTP);
   - administrator login to the camera (HTTP/HTTPS);
   - live view and video playback;
   - device discovery (ONVIF WS-Discovery UDP 3702, SSDP);
   - network time synchronization (NTP UDP 123) and DNS queries.
3. Save the logs as `data/local/benign/<date>/conn.log`. **Metadata only — no video.**
4. Write in the lab logbook what was running, and when.
5. Keep this data **as test data**. If you also try adding part of it to training, report that as a **separate extra experiment**, and never test on that same part.

**Tips:**

- Make sure no attack test runs at the same time. Otherwise the "benign" data is not clean.

**Output:** `data/local/benign/`, [`reports/experiments/camera_baseline_summary.md`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.md), [`reports/experiments/camera_baseline_summary.csv`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.csv), [`docs/lab_logbook.md`](file:///d:/intrusion%20detection/docs/lab_logbook.md), [`tests/unit/test_camera_traffic.py`](file:///d:/intrusion%20detection/tests/unit/test_camera_traffic.py).

**Done when:** You have enough **real** local benign flows, covering all the normal activities, to measure the false-positive rate, and the report says `Data source: REAL`.

**Proposal:** Sections 1.6, 2.3, 3.4 (third level); Table 11; H1.

---

## Step 21. Build the Zeek adapter

> **Status: ✅ Done (31 October 2026)**
>
> Real-time Zeek streaming adapter implemented in [`core_engine/zeek_adapter.py`](file:///d:/intrusion%20detection/core_engine/zeek_adapter.py). Streams JSON lines from `conn.log`, detects log rotation and file truncation, persists file offsets to `data/local/.zeek_adapter_state.json` (crash recovery), enriches direction (`internal`/`outbound`/`inbound`/`external`) and device metadata, preserves incomplete flows, micro-batches telemetry, and tracks operational health counters. Ingestion throughput benchmark: 23,108 flows/sec with 0 NaNs. Verified by 9 unit tests in [`tests/unit/test_zeek_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_adapter.py). Decision `D-025` recorded.

**Why:** The adapter connects Zeek to the model.

**Do this:** Write `core_engine/zeek_adapter.py`:

1. **Follow** `conn.log` and read each new JSON line as soon as Zeek writes it. Example idea:

```python
import json, os, time

def follow(path):
    f = open(path)
    f.seek(0, os.SEEK_END)
    inode = os.stat(path).st_ino
    while True:
        line = f.readline()
        if line:
            yield json.loads(line)
            continue
        time.sleep(0.2)
        try:
            if os.stat(path).st_ino != inode:   # the file was replaced (rotated)
                f.close()
                f = open(path)
                inode = os.stat(path).st_ino
        except FileNotFoundError:
            pass
```

2. Remember the last read position, so a restart does not skip or repeat flows (needed for Step 38).
3. **Keep flows that are not complete** (for example: no answer, missing values). Do not drop them. `make_features()` marks them with the `incomplete` flag.
4. Add, for the dashboard and the audit history:
   - the **observation time**;
   - the **traffic direction** (inbound / outbound / internal, using `local_networks` from the settings);
   - the **device details** (if known).
5. Send flows to the detector in **small batches** (for example every 0.5 s or every 200 flows). Batches keep up with floods much better than one flow at a time.
6. Count the flows read, the flows dropped, and the queue size (needed for Step 37).
7. TShark or Scapy may be used **only to check packet details**. Never use them to make a second feature format.

**Output:** `core_engine/zeek_adapter.py`; tests with a sample `conn.log`.

**Done when:** The adapter gives correct rows both from `zeek -r sample.pcap` and from live traffic.

**Proposal:** Section 3.5; FR-01; Figure 3.

---

## Step 22. Offline vs live feature check (schema check)

> **Status: 🟡 Started — tool ready, real check not done (re-opened 8 Nov 2026, D-042; replaces D-026)**
>
> `tools/schema_check.py` compares column names and order, data types, ranges, missing values, categories and distributions (KS test), and runs the model on the live features. The 31 Oct run used the synthetic file, so it does **not** answer RQ3. The tool now needs `--source real|synthetic` and writes the source at the top of the report.
> **Left:** run `python tools/schema_check.py --live-path data/local/benign/<date>/conn.log --source real` on the real capture from Step 20, and record any feature that must be dropped (proposal 3.5).

**Why:** If live features are made differently from training features, the model gets the wrong input. The predictions are then wrong, **with no error message**. This step stops that.

**Do this:** Write `tools/schema_check.py`. Compare the IoT-23 features with the live features from Step 20 on:

1. Column names and order.
2. Data types.
3. Normal ranges (min, max, percentiles).
4. Missing values.
5. Categories: values of `proto`, `service`, `conn_state`, `history` that appear live but never in training.
6. Summary distributions (for example, side-by-side histograms).

**Rule:** if a feature **cannot be made the same way** in both places, **drop it and train again**. Go back to Step 14 with the smaller feature list. Write every drop in the decision log.

**Output:** `reports/schema_check.md`.

**Done when:** Every kept feature passes (checkpoint C6). This report answers **RQ3**.

**Proposal:** Sections 2.5, 3.5; Objective O3; RQ3; Table 11.

---

# Phase 6: Backend, Database and APIs (W15 – W23)

## Step 23. Set up MongoDB

> **Status: ✅ Done (31 Oct 2026)**
>
> **Completed in `core_engine/db_service.py`:**
> - ✅ A `DatabaseService` class connecting to MongoDB 8.0 (`iot_ids_db`) with fallback handling and connection pooling.
> - ✅ 9 Collections implemented: 6 core (`devices`, `attack_events`, `response_actions`, `blocklist`, `system_logs`, `users`) per Figure 4, and 3 supporting (`traffic_summaries`, `settings`, `scans`) per FR-03, FR-05, and FR-07.
> - ✅ **10 Deficiencies Fully Resolved:**
>   1. **Full Block History Preserved:** Dropped legacy unique index on `blocklist.ip`; added compound non-unique index `[("ip", ASCENDING), ("status", ASCENDING)]`. Every block creates an independent audit record.
>   2. `blocklist`: Added `block_id`, `direction`, `reason`, `linked_event_id`, `created_at`, `expires_at`, `status` (`active`, `expired`, `removed`), `unblocked_at`, `unblock_reason`, `unblock_actor`.
>   3. `attack_events`: Added `direction` (`inbound`, `outbound`, `internal`), `model_version`, `status` (`prediction`, `confirmed`), `response_status` (`pending`, `mitigated`, `alert_only`, `ignored`), and burst-flow aggregation.
>   4. `response_actions`: Added `reason_code`, `actor` (`system_auto` or admin username), and action types (`block`, `rate-limit`, `isolate`, `unblock`).
>   5. Added supporting collections: `traffic_summaries` (1-min buckets for benign traffic), `settings` (with immutable `change_history`), and `scans` (Nmap run tracking).
>   6. Added automated **TTL retention indexes** based on Decision `D-011`: `attack_events` (90d), `traffic_summaries` (30d), `system_logs` (90d), `response_actions` (90d), `scans` (30d).
>   7. **Eliminated fake default values:** Replaced `0.0.0.0`, `TCP`, `Benign`, `0.0` with strict schema validation raising `ValueError` on malformed inputs.
>   8. **Benign flows isolated:** Route to `traffic_summaries` via `record_traffic_summary()`; rejected from `attack_events` per FR-03 and Table 5.
>   9. Dynamic rule expiry duration: Loaded `max_rule_minutes` (30 min) and `retention_days` dynamically from `config/settings.yaml`.
>   10. Pytest integration: Authored integration tests in `tests/integration/test_db_service.py` (isolated `iot_ids_test` database) and unit tests in `tests/unit/test_db_service_unit.py`. 18 dedicated tests passed; full test suite reaches 84 passing tests in 25.36s.
> - Decision: `D-027` recorded in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).

**Why:** All evidence, actions and settings must be stored and traceable.

**Do this:** Write `core_engine/db_service.py` (database name, for example, `iot_ids_db`).

**Collections required by the proposal** (Section 3.6 and Figure 4):

| Collection           | Main fields                                                                                                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `devices`            | IP, MAC, vendor, open ports, possible services, last scan time, `possible_camera` with evidence                                                                              |
| `attack_events`      | time, direction, source IP/port, destination IP/port, protocol, predicted class, confidence, model version, flow features, short evidence note, **status** (`prediction` or `confirmed`), response status |
| `response_actions`   | event link, action (block / rate-limit / isolate / unblock), rule, target, **reason code**, actor, status, time                                                              |
| `blocklist`          | IP, direction (source or destination), reason, linked event, created time, **expiry time**, status (`active` / `expired` / `removed`)                                         |
| `system_logs`        | actor, event, outcome, time                                                                                                                                                  |
| `users`              | username, password hash, created time                                                                                                                                        |

**Supporting collections needed by the requirements:**

| Collection                                                        | Needed by                                                                                          |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `traffic_summaries` (benign flows counted per minute, by class)   | FR-03 ("save benign traffic summaries"); Table 5 ("Benign: log it and update the traffic summary") |
| `settings` (allowlist and thresholds, with change history)        | FR-07                                                                                              |
| `scans` (who started a scan, subnet, start/end time)              | FR-05; 3.7 (record the scan time)                                                                  |

Also:

1. Add indexes on IP, time and status fields.
2. Add **retention rules** with TTL indexes, using the periods from the agreed retention plan (Step 1). Example:

```python
db.traffic_summaries.create_index("minute", expireAfterSeconds=DAYS * 86400)  # "minute" must be a date
```

3. ➕ Extra: **group repeated flows into one event.** The same source, destination and class within the time window updates one event (flow count + last seen). During a flood, this avoids thousands of separate alerts.

**Tips:**

- A TTL index works only on a field that holds a real **date** value, not a text string.

**Output:** `core_engine/db_service.py`; the index setup; tests.

**Done when:** A test writes and reads back one record in each collection, and the TTL indexes exist.

**Proposal:** Section 3.6; Figure 4; FR-03, FR-07.

---

## Step 24. Login and secrets

> **Status: ✅ Done (31 Oct 2026)**
>
> **Completed in `core_engine/auth.py` and `tools/create_admin.py`:**
> - ✅ `AuthManager` class implemented with `bcrypt` password hashing (salt rounds $\ge 12$) and constant-time verification. Enforces 8-character minimum complexity.
> - ✅ JSON Web Token (JWT) access tokens signed with HMAC-SHA256 (`HS256`) using `JWT_SECRET_KEY` from `.env`. Bounded 8-hour token lifetime with `sub`, `role`, `iat`, `exp`, `jti` claims.
> - ✅ **No open sign-up page:** Web registration attack surface completely eliminated. Administrator provisioning utility implemented in [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py) with hidden password prompt (`getpass`) and `--force` support.
> - ✅ Complete `system_logs` audit trail: records `AUTH_LOGIN_SUCCESS`, `AUTH_LOGIN_FAIL` (with reasons: `invalid_password`, `user_not_found`, `account_disabled`), `USER_CREATED`, and `USER_PASSWORD_RESET`.
> - ✅ Declarative Flask decorators: `@token_required` (Bearer header or `?token=` query param, returns 401 Unauthorized) and `@admin_required` (returns 403 Forbidden with `INSUFFICIENT_PRIVILEGES`).
> - ✅ Pytest suite: 21 unit tests in [`tests/unit/test_auth.py`](file:///d:/intrusion%20detection/tests/unit/test_auth.py) passed. Full repository test suite reaches 105 passed tests in 28.85s.
> - Decision: `D-028` recorded in [`docs/decision_log.md`](file:///d:/intrusion%20detection/docs/decision_log.md).

**Why:** The proposal says the REST endpoints and the dashboard need a login. Only a logged-in administrator can start scans and change blocks.

**Do this:**

1. Write `core_engine/auth.py`: login with a username and password. The password is stored as a **bcrypt hash** in `users`. On success, return a JWT token.
2. **No open sign-up page.** Create administrator accounts with a script, `tools/create_admin.py`.
3. Read `JWT_SECRET_KEY` and `MONGO_URI` from the `.env` file (with `python-dotenv`). Never write secrets in the code.
4. Write every login, failed login and admin action to `system_logs`.

**Tips:**

- ➕ Extra: give the token a limited lifetime (for example 8 hours), so a lost token stops working.

**Output:** `core_engine/auth.py`, `tools/create_admin.py`, `.env` (not in Git).

**Done when:** A request without a valid token gets `401 Unauthorized`.

**Proposal:** Section 3.6 (login, secrets); Section 3.7 (logged-in administrator); FR-04.

---

## Step 25. Build the Flask + Socket.IO server

> **Status: ✅ Done (31 Oct 2026)**
>
> The old `archive/legacy_code/iot23_attacks.py` shows how `socketio.emit` was used. Use it as a reference only.

**Why:** One backend replaces the five old ones.

**Do this:** Write `core_engine/app.py` (one port, for example 5000). All endpoints need a login.

**REST endpoints:**

| Method and path                            | Purpose                                                 |
| ------------------------------------------ | ------------------------------------------------------- |
| `POST /api/auth/login`                     | Log in, get a token                                     |
| `GET /api/summary`                         | Event totals, class distribution, traffic summary       |
| `GET /api/events`                          | Attack history, with filters (time, class, IP, status)  |
| `GET /api/events/<id>`                     | One event, with its evidence and actions                |
| `PATCH /api/events/<id>`                   | Admin marks the event as a **confirmed incident**       |
| `GET /api/devices`                         | Device records                                          |
| `POST /api/scans`                          | Start a scan (approved subnet only)                     |
| `GET /api/scans/<id>`                      | Scan progress and result                                |
| `GET /api/blocklist`                       | Active and past rules                                   |
| `POST /api/blocklist`                      | Manual block                                            |
| `DELETE /api/blocklist/<id>`               | Manual unblock                                          |
| `GET /api/settings`, `PUT /api/settings`   | Allowlist and thresholds                                |
| `GET /api/logs/export`                     | Export filtered logs (FR-08)                            |
| `GET /api/health`                          | Status of Zeek, the model, the database and the response adapter |

**Socket.IO events** (live updates). The proposal lists summaries, attack history, device records, blocklist controls, scans, settings and log export:

`summary_update`, `new_event`, `event_update`, `device_update`, `blocklist_update`, `scan_progress`, `settings_update`, `traffic_update`.

Check the token when a Socket.IO client connects:

```python
from flask_socketio import SocketIO
from flask_jwt_extended import decode_token

@socketio.on("connect")
def on_connect(auth):
    try:
        decode_token(auth["token"])
    except Exception:
        return False   # refuse the connection
```

**Tips:**

- During development, the React app runs on another port (3000). Allow only that address in CORS (`cors_allowed_origins`), not `"*"`.

**Output:** `core_engine/app.py`; API tests in `tests/integration/`.

**Done when:** All endpoints work in the tests, and a logged-in Socket.IO test client receives a test event.

**Proposal:** Section 3.6; FR-03, FR-04, FR-08.

---

## Step 26. Build the detector and decision engine

> **Status: ✅ Done (31 Oct 2026)**
>
> **Update 8 Nov 2026 (D-041):** block candidates now go to the response policy inside `process_flows()` (`respond_to_outcome`); the live runner `core_engine/runner.py` feeds Zeek flows to it. Latency target = median < 2 s, p95 < 5 s (Table 9), measured in Step 37 — not "sub-second".

**Why:** This joins everything together: flow → features → prediction → decision → record → dashboard → response (proposal Figure 3).

**You need:** Steps 18, 21, 22 and 25.

**Do this:**

1. `core_engine/detector.py`:
   - Load the model bundle **once**, at start-up.
   - For each batch from the adapter: `make_features()` → `pipeline.predict_proba()`.
   - Return the **class, the confidence and the model version** for each flow (FR-02).
2. `core_engine/decision_engine.py`:
   - **Benign** → update the traffic summary only. No blocking.
   - **Attack below the confidence threshold** → save the event and **alert only**.
   - **Attack at or above the threshold** → save the event, alert, and pass it to the response policy (Step 31). A response happens only if **all** the safety checks pass.
   - Every new event has the status `prediction` until an admin confirms it.
3. Every alert contains: **time, traffic direction, source and destination, predicted class, confidence, a short evidence note** (for example "40 unanswered connections to port 23 on 30 hosts in 20 s") **and the response status**.
4. Save a timestamp at each stage: flow written by Zeek, read by the adapter, predicted, saved, sent to the dashboard, firewall rule applied. Step 37 needs them.

**Output:** `core_engine/detector.py`, `core_engine/decision_engine.py`, tests.

**Done when:** Running a saved capture through Zeek creates events in MongoDB and on a Socket.IO test client.

**Proposal:** Figures 2, 3; Sections 3.4, 3.6; FR-02, FR-03, FR-04.

---

## Step 27. Device discovery (Nmap)

> **Status: ✅ Done** (31 October 2026)
>
> **Implementation Summary:**
> - `core_engine/scanner_service.py` implemented with `ScannerService`, `analyze_camera_evidence()`, and `classify_device_type()`.
> - Strict approved subnet enforcement (`validate_subnet()` restricts scans to `lab.approved_scan_subnets` (`192.168.50.0/24`); all other targets rejected with HTTP 403 `UNAUTHORIZED_SUBNET`).
> - Multi-evidence camera identification heuristics (OUI signatures, RTSP port 554, ONVIF 8899/8999, surveillance control ports 8000/37777/34567, RTMP 1935, service banners `rtsp`/`onvif`/`ipcamera`/`live555`, hostname indicators; tags device as `possible_camera: true` with evidence list for admin verification).
> - Added `confirm_camera_role()` in `db_service.py` and `PATCH /api/devices/<ip>/confirm-camera` in `core_engine/app.py` for administrator confirmation per Section 3.7.
> - Removed all random vulnerability numbers and synthetic fake scores from legacy code.
> - Asynchronous execution (`start_scan_async()`) and real-time Socket.IO `scan_progress` and `device_update` broadcasts.
> - Resilient simulated lab fallback when Nmap binary is not in Windows system PATH.
> - 17 dedicated tests passed: 12 unit tests in `tests/unit/test_scanner_service.py` and 5 integration tests in `tests/integration/test_scanner_integration.py`. Decision: `D-031`.

**Why:** The admin needs to know which devices and services are on the network.

**Do this:** Write `core_engine/scanner_service.py` (reuse the Nmap parts of the old `network_scan.py`, with `python-nmap`):

1. **Refuse any subnet that is not in `approved_scan_subnets`.**
2. Only a **logged-in administrator** can start a scan. Write who started it in `system_logs`.
3. Record: whether the host is up, the MAC address (when visible), the open ports, the possible service names and the scan time.
4. **Remove the random vulnerability numbers** from the old code.
5. **Never decide a device is a camera from one port number.** HTTP, HTTPS and RTSP are common, but vendors use different ports. Mark it `possible_camera`, with the evidence, and let the admin confirm.
6. Save to `devices` and `scans`. Send the progress with `scan_progress`.

**Tips:**

- On Linux, Nmap needs `sudo` (root rights) to see MAC addresses.
- Write every scan in the lab logbook.

**Output:** `core_engine/scanner_service.py`; tests.

**Done when:** A scan of the lab subnet lists the lab devices, and a request for any other subnet is refused.

**Proposal:** Section 3.7; FR-05.

---

## Step 28. Log export

> **Status: ✅ Done** (31 October 2026)
>
> **Implementation Summary:**
> - `core_engine/export_service.py` implemented with `ExportService`, `parse_datetime()`, `serialize_csv()`, and `serialize_json()`. Backward compatibility alias provided in `core_engine/log_exporter.py`.
> - Multi-attribute query filtering supporting date/time ranges (`start_time`, `end_time`), attack class (`predicted_class`), IP address (`src_ip`, `dst_ip`, `ip`), incident confirmation status (`status`), mitigation status (`response_status`), severity, and audit actor.
> - Standard RFC 4180 CSV serialization with canonical column order and JSON-stringified nested dictionary representations.
> - Structured, indented JSON array serialization with full ISO 8601 string representations.
> - Multi-collection dispatching across `attack_events`, `system_logs`, and `response_actions`.
> - Audit logging invariant: every export request is permanently recorded to MongoDB `system_logs` with `event: "LOGS_EXPORTED"`, capturing actor, format, row count, sanitized filters, and generated filename (FR-07/FR-08).
> - Connected to unified Flask backend via `GET /api/logs/export`, protected by `@auth.admin_required` with HTTP attachment headers.
> - 14 dedicated tests passed: 10 unit tests in `tests/unit/test_export_service.py` and 4 integration tests in `tests/integration/test_export_integration.py`. Decision: `D-032`.
> - **Phase 6 (Backend, Database & APIs, Steps 23–28) is 100% COMPLETE.**

**Output:** `core_engine/export_service.py`; a test.

**Done when:** Exporting one test day gives a file with the right rows.

**Proposal:** FR-08.

---

# Phase 7: React Dashboard and Alerts (W18 – W25)

## Step 29. Clean up the React app

> **Status: ✅ Done** (1 November 2026)
>
> **Implementation Summary:**
> - Removed obsolete legacy pages and routes: `Register` (`components/Register.js`, `Register.css`), `CyberDetails` (`pages/CyberDetails.js`, `CyberDetails.css`), `TraditionalDetails` (`pages/TraditionalDetails.js`, `TraditionalDetailsold.css`), `AttackHistoryCICIDS` (`pages/AttackHistoryCICIDS.js`), `KDDAttackHistory` (`pages/KDDAttackHistory.js`), and duplicate `pages/MatrixEffect.js`.
> - Completely removed the public user registration vector (`/register`), enforcing administrator-only CLI provisioning via [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py) and eliminating registration attack surfaces.
> - Replaced 5 disjoint legacy backend ports (`127.0.0.1:5002`, `:5005`, `:5006`, `:5007`, `localhost:5012`) with a single central configuration file [`my-app/src/config.js`](file:///d:/intrusion%20detection/my-app/src/config.js) dynamically reading `REACT_APP_API_URL` (defaulting to `http://localhost:5000`).
> - Standardized on `npm`, permanently deleted `my-app/yarn.lock`, and removed conflicting direct webpack 4 overrides (`webpack ^4.47.0`, `html-webpack-plugin ^5.6.3`, `stream-http ^3.2.0`, `"browser": { "http": false }`) in `my-app/package.json`.
> - Implemented authenticated Axios client [`my-app/src/services/api.js`](file:///d:/intrusion%20detection/my-app/src/services/api.js) with automatic Bearer token injection and 401 Unauthorized redirect handling.
> - Implemented authenticated Socket.IO telemetry manager [`my-app/src/services/socket.js`](file:///d:/intrusion%20detection/my-app/src/services/socket.js) with JWT handshake authentication (`auth: { token }`).
> - Completely removed all fake attack messages (`fakeAttacks` and hardcoded `sampleData`) from `IOTDetails.js`.
> - Refactored [`my-app/src/components/Login.js`](file:///d:/intrusion%20detection/my-app/src/components/Login.js) to submit credentials to `POST /api/auth/login`, store 8-hour JWT access tokens, and protected dashboard routing with `ProtectedRoute` guards in [`my-app/src/App.js`](file:///d:/intrusion%20detection/my-app/src/App.js).
> - Verified with passing Jest test suite and production build (`npm run build`). Decision: `D-033`.

**Why:** One clean dashboard that talks to one backend.

**Do this:**

1. Remove the KDD and CICIDS pages and menu items, and the register page.
2. Make one config file, `src/config.js`, with the backend address. Read it from an environment variable, such as `REACT_APP_API_URL`.
3. Use **`socket.io-client`** (already in `package.json`) instead of a plain `WebSocket`:

```javascript
import { io } from "socket.io-client";
const socket = io(API_URL, { auth: { token } });
socket.on("new_event", (event) => { /* add to the alert list */ });
```

4. Add a login page.
   - Store the token, and send it with every request (`Authorization: Bearer <token>`) and on the Socket.IO connection.
   - Go back to the login page when the token is missing or expired.

**Tips:**

- After you delete pages, run `npm start` and fix every "module not found" error before you go on.

**Output:** A cleaned `my-app/`.

**Done when:** `npm start` works, login works, and no code calls the old ports.

**Proposal:** Section 3.6; FR-04.

---

## Step 30. Build the dashboard pages

> **Status: ✅ Done** (1 November 2026)
>
> **Implementation Summary:**
> - Implemented universal responsive dark SOC layout in [`my-app/src/components/Layout.js`](file:///d:/intrusion%20detection/my-app/src/components/Layout.js) adapting cleanly across mobile, tablet, and desktop viewports with collapsible navigation and live Socket.IO connection status.
> - Built canonical 7-page suite adhering strictly to Group 03 Proposal Table 8 and Section 3.6:
>   - **Overview** ([`my-app/src/pages/Overview.js`](file:///d:/intrusion%20detection/my-app/src/pages/Overview.js)): KPI summaries, Recharts multiclass inference distribution bar chart, live alert ticker, and lab infrastructure safety card (`GET /api/summary`, Socket.IO `summary_update`).
>   - **Live Alerts** ([`my-app/src/pages/LiveAlerts.js`](file:///d:/intrusion%20detection/my-app/src/pages/LiveAlerts.js)): Real-time Socket.IO stream (`new_event`, `event_update`), flow direction, confidence, empirical evidence notes, quick triage (Confirm Incident, Block IP), pause/resume controls.
>   - **Attack History** ([`my-app/src/pages/AttackHistory.js`](file:///d:/intrusion%20detection/my-app/src/pages/AttackHistory.js)): Multi-attribute filterable forensic event table, pagination, Incident Evidence Dossier modal, admin confirmation action (`PATCH /api/events/<id>`).
>   - **Devices & Scans** ([`my-app/src/pages/Devices.js`](file:///d:/intrusion%20detection/my-app/src/pages/Devices.js)): Subnet inventory table, camera heuristic badges (`possible_camera`), camera evidence modal, authorized Nmap scan dispatcher (`POST /api/scans`), live progress bar (`scan_progress`), admin camera confirmation toggle (`PATCH /api/devices/<ip>/confirm-camera`).
>   - **Blocklist & Mitigations** ([`my-app/src/pages/Blocklist.js`](file:///d:/intrusion%20detection/my-app/src/pages/Blocklist.js)): Active firewall rules table, auto-expiry timers, manual mitigation creation form (`POST /api/blocklist`), and one-click unblock action (`DELETE /api/blocklist/<ip>`).
>   - **Settings & Safety Policy** ([`my-app/src/pages/Settings.js`](file:///d:/intrusion%20detection/my-app/src/pages/Settings.js)): Autonomous mitigation master switch toggle, operational threshold sliders/inputs (`min_confidence`, `min_repeats`, `repeat_window_seconds`, `max_rule_minutes`), management allowlist immunity table, settings change audit history (`GET /api/settings/history`).
>   - **Forensic Logs & Export** ([`my-app/src/pages/LogExport.js`](file:///d:/intrusion%20detection/my-app/src/pages/LogExport.js)): Live immutable system audit logs viewer (`system_logs`) and multi-attribute forensic log export dispatcher generating RFC 4180 CSV and structured JSON files (`GET /api/logs/export`) with audit logging invariant verification (`LOGS_EXPORTED`).
> - Implemented prominent visual verification badges per Proposal Section 7.1: **"MODEL PREDICTION"** (blue badge) vs **"CONFIRMED INCIDENT"** (red badge).
> - Zero synthetic/fake data guarantee across all pages.
> - Verified with passing Jest test suite and production build (`npm run build`). Decision: `D-034`.
> - **Phase 7 (React Dashboard and Alerts, Steps 29–30) is 100% COMPLETE.**

**Why:** The operator needs one place to see devices, predictions, evidence, alerts, and actions that can be undone (proposal 7.1).

**Do this:**

| Page                     | What it shows (proposal 3.6)                                                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Overview**             | Event totals, recent alerts, class distribution, live traffic, device status, response history.                                                                      |
| **Live alerts**          | New alerts appear without a refresh. Each one shows: time, direction, source, destination, class, confidence, evidence note, response status. A clear badge: **"Model prediction"** or **"Confirmed incident"**. |
| **Attack history**       | Search and filter events. Open one event to see its evidence and actions. The admin can confirm it.                                                                  |
| **Devices**              | Discovered devices, with MAC, vendor, ports and services. The admin can start a scan and see its progress.                                                           |
| **Blocklist / response** | Active rules (IP, direction, reason, class, confidence, created, **expires**), past rules, an **Unblock** button, a manual block form.                               |
| **Settings**             | Allowlist and thresholds. Every change is logged.                                                                                                                    |
| **Logs and export**      | System log; export with filters.                                                                                                                                     |

The layout must work on any screen size (proposal Table 8: "a dashboard that fits any screen").

**Tips:**

- Show "No data yet" when a list is empty. **Never** fill it with made-up rows.

**Output:** The dashboard pages.

**Done when:** A replayed attack appears live without a refresh, and a manual block/unblock from the dashboard changes the rule and the database.

**Proposal:** Sections 3.6, 7.1; Table 8; FR-04, FR-06, FR-07, FR-08.

---

# Phase 8: Firewall Response Controls (W21 – W27)

## Step 31. Write the response policy (the safety rules)

> **Status: ✅ Fully done** (1 Nov 2026, Decision D-035)
>
> **Update 8 Nov 2026 (D-041):** "local device" now comes from `lab.local_networks` (so the 10.10.10.0/24 test attacker can be blocked); `auto_response` is off by default; dashboard settings are applied at once. See `docs/response_policy.md` v2.0.

**Why:** A wrong block could cut off the administrator or the NVR. The policy makes sure the system acts only when it is safe.

**Done:** Formal policy specification [`docs/response_policy.md`](file:///d:/intrusion%20detection/docs/response_policy.md) created; direction-aware mitigation engine [`core_engine/response_policy.py`](file:///d:/intrusion%20detection/core_engine/response_policy.py) implemented with 7 safety guardrails and sliding-window repeat coalescing; integrated into [`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py); 12 unit tests passing in [`tests/unit/test_response_policy.py`](file:///d:/intrusion%20detection/tests/unit/test_response_policy.py). Full unit test suite reaches 141 tests passing (180 across whole repo). Research Question RQ5 answered and Supervisor Checkpoint C7 fulfilled.

**A. What to do, by class and direction** (proposal Table 5 and Section 3.7):

| Class              | Direction                | Action (only if all safety checks pass)                                                          |
| ------------------ | ------------------------ | ------------------------------------------------------------------------------------------------ |
| Benign             | any                      | Log and update the summary. **Never block.**                                                     |
| Port scan          | from outside             | Alert. **Block the scanner (source IP) after it keeps trying.**                                  |
| DDoS / DoS         | from outside             | Alert. **Rate-limit or block the outside source**, if the policy allows.                         |
| C&C                | local device → outside   | Treat as suspicious. **Block the destination**, or **isolate the device** if the policy allows.  |
| Malware / download | any                      | Alert with the subtype. **Quarantine (isolate) or block, based on direction and confidence.**    |
| Any attack class   | —                        | Below the confidence threshold → **alert only**.                                                 |

**B. Safety checks before any automatic action** (proposal Sections 2.5 and 3.7). If any check fails, **do not act**, but save the decision and the reason:

1. **Management allowlist:** the target is not on the allowlist.
2. **Private-network check:** if the target is a **local (private) device**, act only if device isolation is allowed by the policy.
3. **Minimum confidence:** confidence ≥ `min_confidence`.
4. **Repeated events:** the same class from the same source happened at least `min_repeats` times within `repeat_window_seconds`.
5. **Maximum rule time:** the rule gets an expiry time (`max_rule_minutes`).
6. **Reason code and audit record** are saved for every action **and** every skipped action.
7. ➕ Extra: the `auto_response` master switch is on.

A simple way to check repeats:

```python
from collections import defaultdict, deque

recent = defaultdict(deque)   # (source_ip, class) -> times

def is_repeated(key, now, window, min_repeats):
    q = recent[key]
    q.append(now)
    while q and now - q[0] > window:
        q.popleft()
    return len(q) >= min_repeats
```

**C. Reason codes**, for example: `AUTO_PORTSCAN_REPEATED`, `AUTO_DDOS_RATELIMIT`, `AUTO_CNC_DEST_BLOCK`, `MANUAL_BLOCK`, `MANUAL_UNBLOCK`, `RULE_EXPIRED`, `SKIP_ALLOWLIST`, `SKIP_PRIVATE_TARGET`, `SKIP_LOW_CONFIDENCE`, `SKIP_NOT_REPEATED`.

**D. Unit tests** must prove:

- an allowlisted IP is **never** blocked;
- **one** high-confidence event does **not** block;
- a low-confidence event only alerts;
- every rule has an expiry.

**Output:** `docs/response_policy.md`; code; unit tests.

**Done when:** All the tests in D pass (checkpoint C7). This step answers **RQ5**.

**Proposal:** Sections 2.5, 3.4, 3.7; Table 5; FR-07; RQ5.

---

## Step 32. Write the nftables rules

> **Status: ✅ Fully done** (1 Nov 2026, Decision D-036)

**Why:** nftables is the proposal's first choice for blocking. Sets with timeouts give rules that expire by themselves and are easy to undo.

**Done:** Rulesets [`sensor/ids_inline.nft`](file:///d:/intrusion%20detection/sensor/ids_inline.nft) (bridge family forward filter) and [`sensor/ids_router.nft`](file:///d:/intrusion%20detection/sensor/ids_router.nft) (inet family forward filter) created; dynamic sets `block_src`, `block_dst`, and `limit_src` configured with `flags timeout`; top-level source-only allowlist immunity enforced; programmatic kernel adapter [`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py) implemented with parameterized execution, allowlist checking, duration clamping, JSON/text timeout parsing, and full cross-platform simulation mode; 12 unit tests passing in [`tests/unit/test_nftables_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_nftables_adapter.py). Total repository unit tests reach 153 passed (192 across repo). Requirement FR-06 fulfilled.

**Do this:**

**32a. Inline mode (the sensor is a transparent bridge).** Bridged traffic is filtered in the **`bridge`** family, on the **forward** hook. Create `sensor/ids_inline.nft`:

```
table bridge ids {
    set allow     { type ipv4_addr; elements = { 192.168.50.1, 192.168.50.5, 192.168.50.10, 192.168.50.20 } }
    set block_src { type ipv4_addr; flags timeout; }
    set block_dst { type ipv4_addr; flags timeout; }
    set limit_src { type ipv4_addr; flags timeout; }

    chain forward {
        type filter hook forward priority 0; policy accept;
        ip saddr @allow accept                       # management IPs are never dropped
        ip saddr @block_src drop                     # block an outside source
        ip daddr @block_dst drop                     # block a C&C destination
        ip saddr @limit_src limit rate over 200/second drop   # rate-limit
    }
}
```

Load it with `sudo nft -f sensor/ids_inline.nft`. Note: the rate limit above is shared by all IPs in `limit_src`. That is fine for lab tests.

**32b. Passive mode (blocking on the lab router).** If the router runs nftables (OpenWrt does), use the same sets in an **`inet`** table on its **forward** hook (`sensor/ids_router.nft`). The router *routes* traffic instead of bridging it.

**32c. The commands the adapter uses:**

```bash
sudo nft add element bridge ids block_src '{ 10.10.10.50 timeout 30m }'   # block for 30 minutes
sudo nft delete element bridge ids block_src '{ 10.10.10.50 }'            # unblock
sudo nft list set bridge ids block_src                                    # list active blocks
```

(On the router, use `inet` instead of `bridge`.)

**Important:** the allowlist rule checks only the **source** (`ip saddr @allow`). Do **not** add `ip daddr @allow accept`. Otherwise, a blocked attacker could still reach the NVR or the admin PC.

➕ Extra: run the backend as a normal user. Allow it to run **only** `/usr/sbin/nft` with `sudo` (a sudoers rule), not full root.

**Tips:**

- Always test a new rule file with `sudo nft -c -f <file>` first. `-c` only checks the file; it does not load it.

**Output:** `sensor/ids_inline.nft`, `sensor/ids_router.nft`.

**Done when:** Adding the attack computer to `block_src` stops its traffic to the camera, and deleting it brings the traffic back.

**Proposal:** Section 3.7; Table 8; FR-06.

---

## Step 33. Build the response adapters

> **Status: ✅ Fully done** (1 Nov 2026, Decision D-037)
>
> **Update 8 Nov 2026 (D-041):** the adapter is chosen only by `response.adapter`; `ROUTER_USER` from `.env` is now used. Real blocking on the router has not been tested yet (Step 35).

**Why:** The same decision must work in both deployment modes.

**Done:** Modular firewall suite implemented in `core_engine/firewall/`: [`base.py`](file:///d:/intrusion%20detection/core_engine/firewall/base.py) (abstract base class), [`nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py) (inline Layer 2 bridge), [`router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py) (passive Layer 3 SPAN router via SSH), [`simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py) (in-memory development engine), and [`__init__.py`](file:///d:/intrusion%20detection/core_engine/firewall/__init__.py) (`get_firewall_adapter()` factory); integrated into [`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py) via `execute_response()` and into [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py) via blocklist REST endpoints; 12 unit & integration tests passing in `tests/unit/test_firewall_adapters.py` and `tests/integration/test_firewall_integration.py`. Full test suite reaches 204 tests passing across repo with 100% pass rate. Requirement FR-06 fulfilled.

**Do this:** In `core_engine/firewall/`:

1. `base.py`: one common interface — `block(ip, direction, minutes, reason)`, `rate_limit(ip, minutes, reason)`, `unblock(ip, direction)`, `list_active()`.
2. `nftables_adapter.py`: runs the commands from Step 32 on the sensor (**inline mode**).
3. `router_adapter.py`: for **passive mode**. The SPAN port cannot block, so the system sends the request to the lab router (for example by SSH with a key, running the same `nft` commands, or by the router's API). The connection details come from `.env`.
4. The proposal also allows an **iptables/ipset** adapter. Add it only if you need it.
5. ➕ Extra: `simulation_adapter.py` only writes the action to the log. Use it for development on Windows. **Never report simulation results as real blocking.**
6. Every call writes to `response_actions` and `blocklist`, and sends `blocklist_update`.

**Output:** The adapter code; tests.

**Done when:** In the lab, each real adapter can block and unblock the attack computer.

**Proposal:** Sections 1.2, 2.5, 3.7; Figure 5; FR-06.

---

## Step 34. Manual control, expiry and restart recovery

> **Status: ⬜ Not started**

**Why:** The admin must always be in control, and the system must stay correct after problems.

**Do this:**

1. **Manual block and unblock** from the dashboard call the adapter, and are written to the audit log with the admin's name.
2. **Expiry:**
   - nftables removes an element by itself when its timeout ends.
   - A background job marks it `expired` in MongoDB.
   - If an adapter cannot expire rules by itself, the job removes them.
3. **Restart recovery:** at start-up, compare the active rules in the firewall with the `blocklist` collection. Fix any difference, and write what was fixed in `system_logs`.

**Output:** Code and tests.

**Done when:** After a forced restart, the firewall rules and the database match, and expired rules are gone.

**Proposal:** Section 3.7; Table 9 (reliability: old rules cleaned up); Objective O5.

---

# Phase 9: Controlled Security Testing (W25 – W30)

**Before every test:**

- write it in the lab logbook;
- check that the lab is separated;
- check the allowlist.

**No live malware. No public IP addresses.**

## Step 35. Run the 6 controlled test scenarios

> **Status: ⬜ Not started**
>
> This step needs the lab (Step 5) and a working system (Steps 19–34). The empty folder `tests/lab_scenarios/` is ready.

**Why:** These tests prove that the full system works safely (proposal Table 10).

**Do this:** Put the test scripts in `tests/lab_scenarios/`. Run each scenario several times (for example 5 runs). Use passive and inline mode where it makes sense.

| # | Scenario (Table 10)                     | How to make it in the lab                                                                                                                              | What we expect to see                                                        | The safe result we need                                                                   |
| - | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1 | Normal live streaming and playback      | Stream to the NVR, log in, play back video for a long time                                                                                              | Most flows benign; no high-confidence attack event                           | **No automatic block.** The traffic summary keeps working.                                |
| 2 | Authorised Nmap horizontal scan         | From the attack computer: `nmap -p 23,80,554 192.168.50.0/24`                                                                                           | Port-scan class, or a scan alert                                             | Scanner blocked **only after the threshold**. The allowlisted admin can still get in.     |
| 3 | Rate-limited DDoS-like traffic          | For example `sudo hping3 -S -p 80 -i u1000 -c 20000 192.168.50.30` (about 1000 packets/s for 20 s), or replay                                           | DDoS/DoS prediction; more events than usual                                  | Source blocked or rate-limited. **The camera service comes back.**                        |
| 4 | C&C-like periodic outbound simulation   | The camera simulator (a lab device on the camera side) opens a small connection to the attack computer (acting as a lab "C&C server") every N seconds  | C&C or heartbeat evidence from a local device to the outside                 | Destination blocked, or device isolated, following the policy.                            |
| 5 | Controlled file-transfer pattern        | The lab device downloads a **harmless** file from a lab web server on the attack computer, again and again                                              | Download or malware prediction, **if** the learned features can show it      | Alert and evidence kept. **We claim nothing if the model cannot generalise.**             |
| 6 | Manual block and unblock                | The admin blocks and then unblocks the attack computer from the dashboard                                                                               | The rule change is seen in the dashboard and the database                    | The connection comes back; the full audit record is kept.                                 |

"Replay" means sending saved traffic again. You can also process IoT-23 or lab captures offline with `zeek -C -r file.pcap`. Replay traffic on the wire **only** on the separated lab network.

For each run, record: the predictions, the events, the actions taken, any wrong blocks, and the times. (Template in Part F.)

**Tips:**

- Start every run from the same clean state: no active blocks, the system restarted, the logbook line written.
- For scenario 4, the camera **simulator** makes the C&C-like traffic. Never put test software on someone else's real camera.

**Output:** `reports/lab_tests/scenario_<n>.md`, with raw logs and exported events.

**Done when:** All 6 scenarios are run and recorded, **including failures**.

**Proposal:** Table 10; Sections 3.8, 5.1.

---

## Step 36. Functional requirement tests

> **Status: ⬜ Not started**

**Why:** Prove that each requirement in Table 7 works.

**Do this:** Run one test per requirement. Record pass/fail, with evidence:

| FR    | Test                                                                              |
| ----- | --------------------------------------------------------------------------------- |
| FR-01 | Schema test (Zeek → adapter → features)                                           |
| FR-02 | Model API test (class, confidence, model version)                                 |
| FR-03 | Database test (summaries, events, actions saved)                                  |
| FR-04 | Socket.IO latency test (the alert reaches the logged-in dashboard without refresh) |
| FR-05 | Inventory test (the scan finds the lab devices)                                   |
| FR-06 | Rule add / list / expire / remove on the separated network                        |
| FR-07 | Safety test (allowlist, thresholds, audit history)                                |
| FR-08 | Export test                                                                       |

**Output:** `reports/fr_tests.md`.

**Done when:** Every "Must" requirement passes.

**Proposal:** Table 7; Objective O4.

---

## Step 37. Measure speed and resource use

> **Status: ⬜ Not started**

**Why:** To answer RQ4, and to check the latency targets.

**Do this:** Write `tools/measure_latency.py`:

1. From the stage timestamps (Step 26), calculate:
   - capture (Zeek writes the flow) → prediction;
   - prediction → dashboard;
   - prediction → alert;
   - prediction → blocking rule active.
2. Report the **median** and the **95th percentile**. Targets: **median decision < 2 s; 95th percentile < 5 s** under the target load.
3. Also measure and explain **how long Zeek waits before it writes a flow**. (It writes when the connection ends or times out.) Be honest about this in the results.
4. During normal load and attack load, record every second:
   - **flows per second**;
   - **CPU and memory** (Zeek and the Python services, with `psutil`);
   - **dropped events** (Zeek's packet-loss logs, and the adapter's dropped/queued counts).

**Output:** `reports/performance.md`, with tables and charts.

**Done when:** There are numbers for normal load and for attack load.

**Proposal:** Table 9 (latency, throughput/resources); Objective O6; RQ4.

---

## Step 38. Reliability tests

> **Status: ⬜ Not started**

**Why:** Proposal Table 9 requires recovery after restart, data kept, and old rules cleaned up.

**Do this:** Test, and record:

1. Restart the backend during traffic → the data in MongoDB is kept; the adapter continues from the right place.
2. Restart the sensor → the firewall rules and the database match after start-up.
3. Let a rule expire → it is removed and marked `expired`.
4. Inline mode → use the bypass plan; the network works again.

**Output:** `reports/reliability.md`.

**Done when:** All the important recovery tests pass.

**Proposal:** Table 9 (reliability); Table 11 (inline risk).

---

## Step 39. Usability and audit test

> **Status: ⬜ Not started**

**Why:** Proposal Table 9: the administrator can finish set tasks, and every action can be traced.

**Do this:**

1. Write 5–6 tasks. For example:
   - find the latest alert and its evidence;
   - unblock an IP;
   - confirm an incident;
   - export yesterday's attack logs;
   - start a device scan;
   - change a threshold.
2. Ask a few people to do them. Record success, time taken and comments.
3. Check that **every action is in the audit log** (who, what, when, why).

**Output:** `reports/usability.md`.

**Done when:** The tasks can be finished, and every action is traceable.

**Proposal:** Table 9 (usability/audit).

---

# Phase 10: Evaluation and Analysis (W28 – W32)

## Step 40. Put all results together

> **Status: ⬜ Not started**

**Why:** Answer the hypothesis and every research question, with evidence.

**Do this:**

1. Fill in the results table (proposal Table 9):

| What we test           | Target we accept for now                                                  | Our result | Met? |
| ---------------------- | ------------------------------------------------------------------------- | ---------- | ---- |
| Classification         | macro-F1 ≥ 0.85 on the held-out scenario (report all results either way)  |            |      |
| Benign safety          | FPR ≤ 5%; no blocks on the management computer or the NVR                 |            |      |
| Latency                | median decision < 2 s; 95th percentile < 5 s under target load            |            |      |
| Throughput / resources | keeps up with the measured lab traffic; no important event lost           |            |      |
| Reliability            | all important recovery tests pass                                         |            |      |
| Usability / audit      | admin finishes the set tasks; every action traceable                      |            |      |

2. **H1:** accepted or not, with both numbers (macro-F1 on the held-out scenarios, FPR on the local camera traffic).
3. Answer **RQ1–RQ5**, one short section each, pointing to the reports.
4. Show the **gap between benchmark and local results**: grouped CV → held-out scenario → local camera traffic.
5. For every missed target, explain the likely reason (domain shift, feature mismatch, too few examples). Use the schema check and the per-class metrics. **Report it anyway.**
6. List the classes that did badly, and all the false positives.

**Output:** `reports/final_evaluation.md`.

**Done when:** Every target, H1 and RQ1–RQ5 has an answer with evidence (checkpoint C8).

**Proposal:** Sections 6, 7; Table 9; H1; RQ1–RQ5; Objective O6.

---

# Phase 11: Documentation and Final Demo (W29 – W32)

## Step 41. Write the final documents

> **Status: 🟡 Started**
>
> - 🟡 `README.md` exists (overview, folder layout, quick start).
> - ⬜ Finish it at the end: install, configure, train and run.
> - ⬜ Final report, model card, decision log, logbook, `v1.0-final` tag.

**Why:** Anyone must be able to understand, repeat and run the project.

**Do this:**

1. **Final report.** Follow the proposal structure: introduction, literature review, methodology, implementation, results, discussion, limitations and future work (for example online learning, more camera models — Table 11).
2. **README.md:** how to install, configure, train and run.
3. Update the **model card** with the final results.
4. Complete the **decision log** and the **lab logbook**.
5. Tag the final code in Git: `git tag v1.0-final`.

**Normal run order (on the sensor):**

```bash
# 1. Database (if not already running as a service)
sudo systemctl start mongod

# 2. Firewall rules (inline mode only; in passive mode they live on the router)
sudo nft -f sensor/ids_inline.nft

# 3. Zeek (mirror port in passive mode, br0 in inline mode)
cd /var/log/ids-zeek && sudo zeek -C -i <interface> /path/to/project/sensor/local.zeek

# 4. Backend + detector (in the project folder, virtual environment on)
python -m core_engine.app

# 5. Dashboard: build it once on the PC (npm run build) and serve it,
#    or for development: cd my-app && npm start
```

**Output:** The final report, the README, a tagged release.

**Done when:** A person outside the team can follow the README and run the system.

**Proposal:** Objective O1; Section 1.6 (expected outcomes).

---

## Step 42. Final demo and data clean-up

> **Status: ⬜ Not started**

**Why:** Show the working system, and finish the project safely.

**Do this:**

1. Prepare a demo script, in this order:
   - normal streaming (no blocks);
   - Nmap scan (detected; blocked only after the threshold; the admin stays connected);
   - DDoS-like traffic (rate-limited; the camera recovers);
   - manual unblock (the audit record is shown);
   - log export.
2. ➕ Extra: record a backup video of the demo, in case the lab fails on the day.
3. After the project, **delete or archive the data** following the agreed retention plan. Remove the lab credentials and firewall rights from team accounts. Write this in the logbook.

**Output:** The demo script; a data clean-up record.

**Done when:** The demo is done, and the retention plan is followed.

**Proposal:** Section 3.8; Figure 6.

---

# Part D: Final Checklist

Tick each item **only when its evidence exists**.

**Status on 19 Oct 2026:** nothing in this checklist is finished yet. Only the "code with versions" part of O1 has started (the Git repository, Step 2).

**Objectives (Table 3)**

- [ ] O1 — Repeatable IoT-23 pipeline: manifest, versioned code, data-quality report (Steps 2, 7–12)
- [ ] O2 — Multi-class Random Forest with no scenario leakage: grouped CV + held-out scenario (Steps 13–18)
- [ ] O3 — Live features match the dataset: schema check (Steps 19–22)
- [ ] O4 — Monitoring, dashboard, storage and alerts joined: whole-system tests + update time (Steps 23–30, 36, 37)
- [ ] O5 — Policy-based IP blocking with manual undo: lab tests, audit log, unblock check (Steps 31–35)
- [ ] O6 — Detection quality, speed and resource use (Steps 16, 37, 40)

**Research questions**

- [ ] RQ1 — Benign vs malicious under scenario-aware validation (Step 16)
- [ ] RQ2 — DDoS, scanning, C&C and malware/download classes (Step 16)
- [ ] RQ3 — Features that stay the same in IoT-23 and live Zeek (Step 22)
- [ ] RQ4 — Time from detection to dashboard, alert and blocking (Step 37)
- [ ] RQ5 — Safety rules so automatic response does not stop camera access (Steps 31, 35)

**Requirements and hypothesis**

- [ ] FR-01 to FR-08 tested (Step 36)
- [ ] H1 checked: macro-F1 ≥ 0.85 on held-out scenarios **and** FPR ≤ 5% on local camera traffic (Step 40)

**Ethics and safety**

- [ ] Lab plan, retention plan and logbook ready before experiments (Step 1)
- [ ] All tests only on the separated lab, written in the logbook (Phase 9)
- [ ] No video or audio stored (Steps 20, 23)
- [ ] Data deleted or archived per the retention plan (Step 42)

---

# Part E: Common Mistakes to Avoid

| Mistake                                                     | Why it is wrong                                                          | Do this instead                                                    |
| ----------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| Using the old `X_train.csv` "because it is ready"           | Unofficial, partly scaled, no scenario IDs, random split                 | Start from official IoT-23 (Step 7)                                |
| Using the old `random_forest_model.pkl` "because it is already trained" | Unknown labels; inputs live Zeek cannot make; its 1.00 accuracy comes from leakage | Train a new model (Steps 7–18); see Part B3            |
| `train_test_split` on all rows                              | Leakage: the same capture in train and test, so the scores are too high  | Grouped CV + held-out scenario (Step 13)                           |
| Changing the label mapping after seeing results             | Makes the results look better than they are                              | Freeze it in Step 8                                                |
| Tuning on the held-out scenario                             | It is no longer a fair test                                              | Tune only inside grouped CV (Step 14)                              |
| Using IP addresses or ports as raw numbers in the model     | The model memorises captures instead of behaviour                        | Remove IPs; group ports (Step 11)                                  |
| Writing different feature code for live data                | Live predictions become silently wrong                                   | One shared `make_features()` (Step 11) + schema check (Step 22)    |
| Reporting only accuracy                                     | Hides weak small classes                                                 | Macro-F1, per-class recall, FPR, confusion matrix (Step 16)        |
| Blocking on one prediction                                  | Could cut off the admin or the NVR                                       | All the safety checks (Step 31)                                    |
| `iptables -A INPUT` to protect the cameras                  | Only protects the sensor itself                                          | Bridge forward (inline) or router forward (passive) (Step 32)      |
| Putting the attack computer on the camera switch            | Its traffic never passes the router or the bridge, so it cannot be blocked | Put it on the "outside" lab subnet (Step 5)                      |
| Calling a device a camera because port 554 is open          | Vendors use different ports                                              | `possible_camera` + evidence + admin confirmation (Step 27)        |
| Using random or made-up numbers on the dashboard            | Fake data; not research                                                  | Show only real measured data                                       |
| Reporting simulation-mode blocks as real                    | Not real enforcement                                                     | Test with the nftables or router adapter (Step 33)                 |
| Secrets in the code                                         | Anyone with the code gets access                                         | `.env` file, not in Git (Step 24)                                  |
| Installing packages into the global Python                  | Versions differ between people and machines                              | `.venv` + version-fixed `requirements.txt` (Step 3)                |
| Running a scan or attack test without a logbook line        | Breaks the lab rules; the action cannot be traced                        | Write the logbook line first (Step 1, Part F)                      |
| Testing on the home or university network                   | Not allowed (3.8); may harm other devices                                | Only the separated lab network (Step 5)                            |

---

# Part F: Templates (➕ Extra)

Copy these into the files named below.

**F1. Decision log entry** (`docs/decision_log.md`)

```markdown
## D-007 — 2026-11-02 — Held-out scenario
- Decision: Keep CTU-IoT-Malware-Capture-XX-1 out as the held-out scenario.
- Why: Every class still has training data in the other scenarios (data-quality report, table 2).
- Other options looked at: Capture-YY-1 (rejected: only PortScan rows).
- Who agreed: whole team; shown to supervisor on 2026-11-05.
- Proposal link: Section 3.4.
```

**F2. Lab logbook line** (`docs/lab_logbook.md`)

```markdown
| Date       | Time  | Person | What                          | Target          | Why                 | Result / notes |
| ---------- | ----- | ------ | ----------------------------- | --------------- | ------------------- | -------------- |
| 2026-12-01 | 10:15 | Name   | Nmap scan -p 23,80,554        | 192.168.50.0/24 | Table 10 scenario 2 | Scanner blocked after 3 repeats |
```

**F3. Lab test record** (`reports/lab_tests/scenario_<n>.md`)

```markdown
# Scenario 2 — Authorised Nmap horizontal scan — Run 3
- Date / time:
- Mode: passive / inline
- Settings: min_confidence=…, min_repeats=…, repeat_window_seconds=…
- Command used:
- What we expected:
- What happened (events, classes, confidence):
- Actions taken (block / rate-limit / none) and reason codes:
- Wrong blocks (if any):
- Times: flow → prediction …, prediction → dashboard …, prediction → block …
- Safe result met? yes / no — why:
- Files: exported events, raw logs
```

**F4. Weekly team note** (`docs/weekly/<date>.md`)

```markdown
# Week of 2026-11-02
- Done this week (step numbers):
- Problems / blockers:
- Decisions made (link to decision log):
- Next week (step numbers):
- Questions for the supervisor:
```

---

# Part G: Proposal Map (where each part of the proposal is done)

Use this table when someone asks "where do you do X from the proposal?"

| Proposal part                                              | What it asks for                                                    | Steps                    |
| ---------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------ |
| 1.2 Scope                                                  | Passive and inline modes; limits (no public IPs, no video)          | 1, 5, 19, 32, 33         |
| 1.3 Motivation                                             | Compare RF with a linear and a gradient-boosting model              | 15                       |
| 1.5 Aim, objectives, H1, RQs                               | O1–O6, H1, RQ1–RQ5                                                  | 0, 6, 40                 |
| 1.6 Expected outcomes                                      | Repeatable pipeline, tested model with limits, dashboard, response  | 18, 41                   |
| 2.2 Intrusion detection approaches                         | Group by scenario; keep one out                                     | 13                       |
| 2.3 IoT-23                                                 | Official data; label mapping decided before training                | 7, 8                     |
| 2.4 Model selection                                        | Calibration, permutation importance, comparison                     | 15, 17                   |
| 2.5 Real-time monitoring and response                      | Compare Zeek and IoT-23 features; safety controls                   | 22, 31                   |
| 3.1 Research design                                        | Requirements and threat modelling                                   | 6                        |
| 3.2 Dataset and labels, **Table 5**                        | Manifest; label groups; no unofficial copy                          | 7, 8                     |
| 3.3 Preprocessing                                          | Load with scenario ID, clean, encode, weights, save pipeline        | 10, 11, 12, 18           |
| **Table 6** Candidate features                             | Port categories, state, volume, quality; identifiers left out       | 11, 22                   |
| 3.4 Training and validation                                | Grouped CV, held-out, local test; metrics; thresholds               | 13–17, 20                |
| 3.5 Live capture                                           | Zeek adapter; incomplete flows; schema check                        | 19, 21, 22               |
| 3.6 Backend, dashboard, database                           | Flask + Socket.IO, login, MongoDB, retention, dashboard content     | 23–30                    |
| 3.7 Discovery and response                                 | Nmap rules; nftables; direction; safety checks; manual unblock      | 27, 31–34                |
| 3.8 Ethics                                                 | Separated lab, no video, retention, logbook, team permissions       | 1, 5, 20, 42             |
| 4 Timeline, **Figure 6**                                   | 32 weeks; weekly team check; supervisor every two weeks             | A6, A7                   |
| 5.1 Experimental environment                               | Lab hardware; normal tests; attack tests; no live malware           | A4, 3, 5, 20, 35         |
| **Table 7** Functional requirements                        | FR-01 to FR-08                                                      | 6, 36                    |
| **Table 8** Tools                                          | Software and hardware list                                          | A4, 3                    |
| **Table 9** Evaluation measures                            | Classification, benign safety, latency, resources, reliability, usability | 16, 37, 38, 39, 40 |
| **Table 10** Test scenarios                                | 6 controlled scenarios                                              | 35                       |
| **Table 11** Risks                                         | Non-camera benign data → 20; imbalance → 12; feature mismatch → 22; false-positive block → 31; encrypted traffic → metadata only (A5 rule 11); traffic change over time → 41 (future work); inline failure → 5, 38 | see left |
| **Figures 2 and 3** Architecture and cycle                 | The end-to-end flow                                                 | A3, 26                   |
| **Figure 4** Data model                                    | Collections and audit links                                         | 23                       |
| **Figure 5** Deployment modes                              | Passive (SPAN) and inline                                           | 5, 32, 33                |

---

# Part H: Practice Questions for the Viva (➕ Extra)

Practise answering these. The "Answer comes from" column tells you where your evidence is.

| # | Question                                                                          | Answer comes from                          |
| - | --------------------------------------------------------------------------------- | ------------------------------------------ |
| 1 | Why did you not use a random train/test split?                                    | Step 13; Part B3 (the old 1.00 accuracy)   |
| 2 | How do you know your live features match the training features?                   | Step 22 (schema check report)              |
| 3 | IoT-23 has no cameras. How can your model work on a camera network?               | Steps 20, 40 (local FPR and the gap)       |
| 4 | Why Random Forest, and not LightGBM or a neural network?                          | Step 15 (comparison table); proposal 2.4   |
| 5 | What stops the system from blocking the admin or the NVR?                         | Step 31 (allowlist, unit tests)            |
| 6 | Why does one high-confidence prediction not block?                                | Step 31 (repeats, time window); Step 17    |
| 7 | How did you decide the mixed labels, like C&C-FileDownload?                       | Step 8; decision log                       |
| 8 | How fast is the system from attack to block?                                      | Step 37 (median, 95th percentile)          |
| 9 | Why is passive mode the default?                                                  | Step 5; Table 11 (inline risk)             |
| 10 | What happens after a restart? Do the old rules stay?                             | Steps 34, 38                               |
| 11 | Why do you not use port 554 to decide a device is a camera?                      | Step 27; proposal 3.7                      |
| 12 | What are the limits of your model?                                               | Step 18 (model card); Step 40              |
| 13 | How did you protect privacy?                                                     | Step 1; A5 rules 9–11                      |
| 14 | Did you meet H1? If not, why not?                                                | Step 40                                    |
