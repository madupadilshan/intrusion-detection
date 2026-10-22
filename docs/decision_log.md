# Decision Log

Every important project decision is written here: the date, the decision, the reason, the other options looked at, and who agreed. Once a decision is written, it is not deleted. If it changes later, add a **new** entry that points to the old one.

(Guide Step 4; template in guide Part F1. Started 20 October 2026. Decisions D-001 to D-009 were made on 19–20 October 2026 and are copied here from `PROJECT_PROGRESS_AND_CHALLENGES.md`.)

---

## D-001 — 2026-10-19 — Follow the step-by-step guide in order
- **Decision:** Build the project by following `STEP_BY_STEP_GUIDE.md` (Steps 0–42) in order. If the guide and the proposal ever disagree, the proposal is correct.
- **Why:** One clear plan that follows the proposal, so the work is repeatable (O1).
- **Who agreed:** project owner.
- **Proposal link:** whole proposal; Section 4 (keep the order of tasks that depend on each other).

## D-002 — 2026-10-19 — Do not use the old data or the old model
- **Decision:** Do not train on the old `X_train.csv` / `X_test.csv`, and do not use the old `random_forest_model.pkl`. Train a new model from the official IoT-23 v1.0.0 files (Steps 7–18).
- **Why:**
  - the data is an unofficial processed copy;
  - it has no scenario IDs;
  - it was split randomly by rows (the accuracy of 1.00 shows leakage);
  - the output labels 0–12 have no saved meaning;
  - the inputs cannot be made from live Zeek data.

  See guide Part B3.
- **Other options looked at:** reusing the old model to save time. Rejected, because it would not work with Zeek and cannot test O2 or H1.
- **Who agreed:** project owner.
- **Proposal link:** Section 3.2; Section 3.4; O2; H1.

## D-003 — 2026-10-19 — Keep old code only in `archive/`
- **Decision:** Move the old code, data, models and documents into `archive/`, which Git ignores. Keep them for reference only.
- **Why:** Nothing is lost, and the repository stays clean.
- **Who agreed:** project owner.
- **Proposal link:** O1 (code with versions); Section 3.6 (secrets not in version control).

## D-004 — 2026-10-19 — One database and one backend
- **Decision:** One MongoDB database (`iot_ids_db`) and one Flask + Flask-SocketIO backend, instead of the old 5 ports and 2 databases.
- **Why:** The proposal describes one backend and one MongoDB store.
- **Who agreed:** project owner.
- **Proposal link:** Section 3.6; Figure 4.

## D-005 — 2026-10-19 — No Telegram or email alerts
- **Decision:** Alerts go only to the logged-in dashboard through Socket.IO, with audit records in MongoDB.
- **Why:** Telegram and email are not in the proposal. FR-05 is Nmap discovery, not alerts.
- **Who agreed:** project owner.
- **Proposal link:** Table 7 (FR-04, FR-05).

## D-006 — 2026-10-19 — The label mapping stays a draft until Step 8
- **Decision:** `config/label_mapping.yaml` stays a draft (`mapping_status: draft`). Eight mixed labels are `TO_DECIDE`. It is frozen only in Step 8, after the Step 7 manifest shows the real labels.
- **Why:** The mapping must be checked against the official label descriptions and the real counts. A label that is unclear is not forced into a class.
- **Who agreed:** project owner.
- **Proposal link:** Table 5; Sections 2.3, 3.2.

## D-007 — 2026-10-19 — Example lab IP plan and passive mode as default
- **Decision:**
  - Example plan: camera LAN `192.168.50.0/24`; "outside" test subnet `10.10.10.0/24`, with the attack test computer behind the lab router.
  - **Passive mode is the default.**
  - The real IP addresses are set in Step 5.
- **Why:**
  - The lab must be separated (3.8).
  - A device can only block traffic that passes through it.
  - Passive mode is safer (Table 11).
- **Who agreed:** project owner. **To confirm** with the team and the supervisor in Steps 4–5.
- **Proposal link:** Sections 1.2, 3.8, 5.1; Figure 5; Table 11.

## D-008 — 2026-10-20 — Keep the GitHub repository public
- **Decision:** Keep https://github.com/madupadilshan/intrusion-detection public, and do not rewrite the old Git history.
- **Why:** Owner's decision. The old files in the history (`users.db`, the old `app.py`, the installer) belong to the archived prototype and are not used by the new system.
- **Who agreed:** project owner.

## D-009 — 2026-10-20 — Remove the "Almashhadani et al. (2024)" citation
- **Decision:** Do **not** cite "Almashhadani et al., 2024" in any project document or in the final report. The sentence in proposal Section 1.4 is supported by **Santos et al. (2023)** alone. In the final report, the sentence will end:
  > "…and limiting false positives (Santos et al., 2023)."
- **Why:**
  - The citation is in the proposal text but not in its reference list.
  - A search of the web (3 name spellings) and of Crossref (94 publications by authors named Almashhadani, 2023–2025) found **no** matching paper.
  - **No team member has the paper or its source.**
  - A reference that nobody can show must not be cited.
- **Other options looked at:** replacing it with Mutambik, I. (2024) 'An Efficient Flow-Based Anomaly Detection System for Enhanced Security in IoT Networks', *Sensors*, 24(22), 7408. Not chosen, because Santos et al. (2023) already supports the sentence. It stays in the literature notes as an extra reading.
- **Also:** add the full Santos et al. (2023) reference to the final report's reference list (it is missing from the proposal's list):
  > Santos, L., Gonçalves, R., Rabadão, C. and Martins, J. (2023) 'A flow-based intrusion detection framework for internet of things networks', *Cluster Computing*, 26(1), pp. 37–57. doi:10.1007/s10586-021-03238-y.
- **Who agreed:** project owner and team (20 Oct 2026). **To tell the supervisor** at the next meeting.
- **Proposal link:** Section 1.4; References.

## D-010 — 2026-10-21 — Lab device planning with software simulation and lab loans
- **Decision:** In [`docs/ethics/lab_plan_and_rules.md`](file:///d:/intrusion%20detection/docs/ethics/lab_plan_and_rules.md), allocate device roles with software camera simulation (RTSP camera simulator / mobile camera stream) and software network bridges / lab loans, as physical IP cameras and dedicated hardware switches are not yet available.
- **Why:** The proposal (Section 5.1) explicitly permits an IP camera or camera simulator. Work on software, dataset, ML pipeline, and simulation testing can proceed without hardware delays.
- **Who agreed:** project owner and team (21 Oct 2026).
- **Proposal link:** Section 5.1; Table 10.

## D-011 — 2026-10-21 — Data retention durations agreed
- **Decision:** In [`docs/ethics/data_retention_plan.md`](file:///d:/intrusion%20detection/docs/ethics/data_retention_plan.md) and [`config/settings.example.yaml`](file:///d:/intrusion%20detection/config/settings.example.yaml), set:
  - `attack_events`: 90 days (automatic deletion via MongoDB TTL index);
  - `traffic_summaries`: 30 days (automatic deletion via MongoDB TTL index);
  - `system_logs`: 90 days (automatic deletion via MongoDB TTL index);
  - Local benign / test captures: until evaluation is completed (maximum 180 days).
- **Why:** Balances research data availability for analysis and reports with data minimization and storage management (proposal Section 3.8).
- **Who agreed:** project owner and team (21 Oct 2026).
- **Proposal link:** Section 3.8; FR-08.

## D-012 — 2026-10-22 — Windows laptop setup and package isolation for Step 3a
- **Decision:** Execute Step 3a on the Windows laptop with a dedicated Python virtual environment (`.venv`) and pinned versions in `requirements.txt`. Note that Npcap is already present (`C:\Program Files\Npcap`), and Nmap installation is deferred to Step 27 (Device Discovery) since Nmap is not required for the Machine Learning pipeline (Steps 7–18).
- **Why:** Keeps development agile, avoids version pollution across global Python packages, and maintains strict dependency reproducibility without blocking dataset processing and model training on hardware tools.
- **Who agreed:** project owner and team (22 Oct 2026).
- **Proposal link:** Table 8; Section 3.3.
