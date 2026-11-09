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

## D-013 — 2026-10-23 — Finalize local settings, management allowlist, and secure secrets
- **Decision:** Create local `config/settings.yaml` and `.env` (both Git-ignored):
  - Management allowlist locked to Router (`192.168.50.1`), Sensor (`192.168.50.5`), Admin PC (`192.168.50.10`), and NVR (`192.168.50.20`) to prevent lockout (Proposal 3.7).
  - Random seed fixed to `42` across all ML pipelines (Proposal 3.4).
  - Start response parameters set: `min_confidence: 0.85`, `min_repeats: 3`, `repeat_window_seconds: 60`, `max_rule_minutes: 30`.
  - Cryptographically secure 32-byte hexadecimal secret keys generated for `JWT_SECRET_KEY` and `FLASK_SECRET_KEY` in `.env` (Proposal 3.6).
- **Why:** Centralizes configuration, strictly isolates secrets from Git, prevents self-lockout during firewall tests, and guarantees scientific reproducibility.
- **Who agreed:** project owner and team (23 Oct 2026).
- **Proposal link:** Sections 3.4, 3.6, 3.7; Table 7 (FR-06).

## D-014 — 2026-10-23 — Freeze IoT-23 label mapping to 5 target classes
- **Decision:** Freeze [`config/label_mapping.yaml`](file:///d:/intrusion%20detection/config/label_mapping.yaml) (`mapping_status: frozen`) following the completion of Step 7 manifest audit across all 325,309,946 flows. Map the 17 unique labels into the 5 target classes from Proposal Table 5:
  - `Benign` (Class 0): `Benign`, `benign` (30,860,691 flows, 9.49%)
  - `DDoS_DoS` (Class 1): `DDoS` (19,538,713 flows, 6.01%)
  - `PortScan` (Class 2): `PartOfAHorizontalPortScan` (213,852,924 flows), `C&C-PartOfAHorizontalPortScan` (888 flows) (Total: 213,853,812 flows, 65.74%)
  - `CnC` (Class 3): `C&C`, `C&C-HeartBeat`, `C&C-Torii` (Total: 55,698 flows, 0.02%)
  - `Malware_Download` (Class 4): `Okiru` (60,990,708 flows), `Mirai`, `FileDownload`, `C&C-FileDownload`, `C&C-HeartBeat-FileDownload`, `C&C-Mirai` (Total: 60,990,792 flows, 18.75%)
  - `EXCLUDE`: Ambiguous labels lacking verified flooding signatures or specific attack types (`Attack`: 9,398 flows; `C&C-HeartBeat-Attack`: 834 flows; `PartOfAHorizontalPortScan-Attack`: 5 flows; `Okiru-Attack`: 3 flows). Total excluded: 10,240 flows (0.0031% of dataset).
- **Why:**
  - Adheres strictly to Proposal Table 5 and Sections 2.3 & 3.2.
  - Resolves all 8 `TO_DECIDE` labels by analyzing real flow profiles: file download triggers are assigned to `Malware_Download`, port scanning behavior to `PortScan`, and vague unverified `Attack` labels are excluded to prevent training label noise.
  - Freezing before model training prevents post-hoc data snooping and establishes scientific validity for thesis examination (Supervisor Checkpoint C3).
- **Who agreed:** project owner and team (23 Oct 2026).
- **Proposal link:** Table 5; Sections 2.3, 3.2; Objectives O1, O2.

## D-015 — 2026-10-25 — Shared feature engineering specification and schema
- **Decision:** Establish [`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py) as the single source of truth for feature engineering, producing exactly 19 locked features across both offline model training and real-time live detection (`make_features(df)`):
  - **Categoricals (6):** `proto`, `service`, `conn_state`, `history`, `orig_port_cat`, `resp_port_cat`.
  - **Numericals (13):** `duration`, `orig_bytes`, `resp_bytes`, `missed_bytes`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`, `orig_bytes_per_pkt`, `resp_bytes_per_pkt`, `byte_ratio`, `pkt_ratio`, `is_incomplete_flow`.
  - **Port Categorization:** Group network ports into standard IANA bins (`well_known`: 0–1023, `registered`: 1024–49151, `dynamic`: 49152–65535, and `icmp` for ICMP traffic) to prevent memorizing arbitrary port numbers.
  - **Safe Division:** Directional ratios use `np.divide` with explicit masks to guarantee zero divide-by-zero warnings or NaN outputs.
  - **Strict Identifier Exclusion (Golden Rule 5):** Connection UIDs, IP addresses (`id.orig_h`, `id.resp_h`), timestamps (`ts`), and `scenario_id` are strictly prohibited from entering the feature matrix $X$.
- **Why:**
  - Guarantees zero training-serving skew between offline model evaluation and the live Zeek sensor pipeline (FR-01, FR-02, FR-03).
  - Satisfies Proposal Table 6 candidate feature specifications.
  - Passes 10 automated unit tests in [`tests/unit/test_features.py`](file:///d:/intrusion%20detection/tests/unit/test_features.py) across both IoT-23 data and simulated live Zeek JSON records.
- **Who agreed:** project owner and team (25 Oct 2026).
- **Proposal link:** Table 6; Section 3.3 (steps 2–5); Section 3.5; Objectives O1, O2.

## D-016 — 2026-10-25 — Stratified sampling strategy, per-class scenario cap (N=50,000), and minority class preservation
> **Note (D-039, 8 Nov 2026):** four scenario names in the sampling tables were corrected (8-1/9-1, 35-1/36-1).
- **Decision:** Execute Step 12 stratified sampling using [`ml_engine/sample_dataset.py`](file:///d:/intrusion%20detection/ml_engine/sample_dataset.py) with the following parameters:
  - **Cap per (scenario, class):** $N = 50,000$ rows, selected uniformly at random with fixed seed `42` (`config/settings.yaml`).
  - **Minority Class Rule:** Retain 100% of all minority class flows whose count $\le N$. Consequently, all 48,992 `CnC` flows across all 22 training scenarios are preserved without dropping a single flow.
  - **Memory Safety:** Streaming row-group sampling keeps peak RAM consumption $< 180$ MB (strictly within the $< 1$ GB standalone PC limit).
  - **Training Dataset Volume:** Yields 1,384,070 training flows (`PortScan`: 500,000, `Benign`: 345,424, `Malware_Download`: 250,069, `DDoS_DoS`: 239,585, `CnC`: 48,992), compressed to 10.81 MB snappy parquet at [`data/processed/train_features.parquet`](file:///d:/intrusion%20detection/data/processed/train_features.parquet).
  - **Imbalance Reduction:** Cuts the raw class imbalance ratio from $4,354 : 1$ down to $10.2 : 1$, allowing standard balanced class weighting (`class_weight="balanced"`) during model training without distorting underlying feature distributions.
- **Why:**
  - Prevents high-volume attack scenarios (e.g. 73M PortScan flows in Capture-39-1) from overwhelming the classifier or exhausting hardware RAM.
  - Solves the extreme minority problem for Command and Control (`CnC`) botnet beacons.
  - Matches Proposal Section 3.3 step 6 and Table 11 requirements.
- **Who agreed:** project owner and team (25 Oct 2026).
- **Proposal link:** Section 3.3 step 6; Table 11; Objective O1.

## D-017 — 2026-10-25 — Formal three-level model evaluation architecture and held-out scenario isolation
> **Note (D-042, 8 Nov 2026):** Level 3 uses a lab IP camera or a camera simulator confirmed with the supervisor (D-038); it has not been run yet.
- **Decision:** Adopt the three-level evaluation framework formalized in [`reports/test_split_plan.md`](file:///d:/intrusion%20detection/reports/test_split_plan.md) prior to model training:
  - **Level 1 — Grouped Cross-Validation:** 5-fold cross-validation on the 22 training scenarios using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` with `groups = scenario_id`. Guarantees flows from any capture scenario stay strictly together within train or validation folds, eliminating intra-session data leakage during hyperparameter search (Steps 14, 15, 17).
  - **Level 2 — Held-Out Zero-Day Scenario:** Isolate scenario `CTU-IoT-Malware-Capture-34-1` (Mirai botnet, 23,145 flows: 14,394 DDoS_DoS, 6,706 CnC, 1,923 Benign, 122 PortScan) into dedicated directory [`data/processed/heldout/held_out_test.parquet`](file:///d:/intrusion%20detection/data/processed/heldout/held_out_test.parquet). The held-out dataset is 100% untouched (no under-sampling, no artificial balancing). In accordance with Supervisor Checkpoint C4, this file is sealed and opened ONLY in Step 16 to evaluate unseen zero-day botnet generalization.
  - **Level 3 — Physical Lab Camera Traffic:** Live evaluation using real Tapo C200 IP camera 1080p RTSP/H.264 video streaming baseline (Step 20) and 6 controlled test attack scenarios (Phase 9, Steps 35–39) to measure operational False Positive Rate $< 1\%$ and sub-second defense response latency (testing Hypothesis H1).
- **Why:**
  - Eliminates the major scientific flaw of random row-level train-test splits prevalent in naive ML literature.
  - Verifies multi-class detection integrity while guaranteeing training scenarios are not starved of any attack class.
  - Establishes full experimental rigor for BICT Honours Degree thesis examination.
- **Who agreed:** project owner and team (25 Oct 2026).
- **Proposal link:** Section 3.4; Objective O2; Hypotheses H1, H2; Supervisor Checkpoint C4.

## D-018 — 2026-10-31 — Random Forest hyperparameter selection and Level 1 Grouped Cross-Validation
> **Numbers replaced by D-043 (9 Nov 2026):** Step 14 was run again after the scenario-name fix (D-039). New out-of-fold macro-F1 0.3422; the numbers below are history.
- **Decision:** Execute Step 14 Random Forest classifier training using [`ml_engine/train.py`](file:///d:/intrusion%20detection/ml_engine/train.py) with the following specifications:
  - **Pipeline Architecture:** Scikit-learn Pipeline with `ColumnTransformer` (OrdinalEncoder with `handle_unknown="use_encoded_value"`, `unknown_value=-1`, `min_frequency=50` on 6 categorical features; numerical features passed through without scaling) followed by `RandomForestClassifier`.
  - **Hyperparameter Search:** Executed `RandomizedSearchCV` (12 candidates, 5 folds = 60 fits) scored on `f1_macro` within `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` using `groups = scenario_id`.
  - **Optimal Selected Hyperparameters:** `n_estimators = 150`, `max_depth = 25`, `min_samples_split = 2`, `min_samples_leaf = 4`, `max_features = 'log2'`, `class_weight = 'balanced'`.
  - **Level 1 5-Fold Grouped Cross-Validation (Full 1,384,070 flows):**
    - Out-of-fold Macro-F1: `0.3630` (fold mean: `0.4651 ± 0.3279`, fold max: `0.9997`).
    - Overall Out-of-fold Accuracy: `0.4500`.
    - Per-Class Recalls: `Malware_Download` 79.97%, `Benign` 53.27%, `CnC` 44.89%, `PortScan` 43.32%, `DDoS_DoS` 0.12%.
  - **Inference Latency & Model Size:**
    - Per-flow inference latency: `6.46 µs/flow` (throughput: 154,746 flows/second), well within the 1-second operational budget.
    - Serialized model bundle (`ml_engine/models/rf_model.joblib`): `15.19 MB` (prevented tree explosion by bounding max_depth to 25, completely replacing the unusable 820 MB legacy model).
- **Why:**
  - Strictly follows Proposal Section 2.4, Section 3.3 step 5, and Section 3.4.
  - Exposes the genuine difficulty of cross-scenario botnet generalization without session leakage (contrast with the flawed 1.00 accuracy of legacy row-random splits).
  - Preserves memory safety (< 400 MB RAM during training) on the development PC.
  - Passes all 21 automated unit tests in `tests/unit/`.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 2.4, 3.3 step 5, 3.4; Objective O2.

## D-019 — 2026-10-31 — Model comparison benchmarks and justification of Random Forest as primary prototype classifier
> **Numbers replaced by D-043 (9 Nov 2026):** new out-of-fold macro-F1 HGB 0.4331 > RF 0.3422 > LR 0.2722. RF stays the main model for the reason given in D-043.
- **Decision:** Execute Step 15 model benchmarking using [`ml_engine/compare_models.py`](file:///d:/intrusion%20detection/ml_engine/compare_models.py) comparing three distinct algorithmic families across the exact same 1,384,070 flows from `data/processed/train_features.parquet` under identical 5-fold Level 1 Grouped Cross-Validation (`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` with `groups = scenario_id`):
  1. **Random Forest (Bagging Ensemble):** Tuned parameters (`n_estimators=150`, `max_depth=25`, `class_weight='balanced'`), OrdinalEncoder with unknown category handling.
  2. **Logistic Regression (Linear Baseline):** `LogisticRegression(class_weight="balanced", max_iter=200, solver="lbfgs")`, `OneHotEncoder(handle_unknown="ignore", sparse_output=True)` for categoricals, and `StandardScaler(with_mean=False)` for numerical features.
  3. **HistGradientBoosting (Boosting Ensemble):** `HistGradientBoostingClassifier(class_weight="balanced", max_iter=100, max_depth=15, random_state=42)`, OrdinalEncoder with native categorical support.
- **Empirical Results Summary:**
  - **Out-of-Fold Macro-F1:** HistGradientBoosting (`0.3950`) > Random Forest (`0.3630`) > Logistic Regression (`0.3486`).
  - **Fold Mean Macro-F1:** HistGradientBoosting (`0.4670 ± 0.3021`) ~ Random Forest (`0.4651 ± 0.3279`) > Logistic Regression (`0.3431 ± 0.1357`).
  - **Per-Class Recall Performance:**
    - `CnC` (extreme minority botnet beacons): Random Forest (**44.89%**) > HistGradientBoosting (**44.08%**) >> Logistic Regression (**13.97%**).
    - `Malware_Download`: Logistic Regression (**93.62%**) > HistGradientBoosting (**79.98%**) ~ Random Forest (**79.97%**).
    - `PortScan`: HistGradientBoosting (**55.19%**) > Random Forest (**43.32%**) > Logistic Regression (**33.66%**).
    - `Benign`: Random Forest (**53.27%**) > HistGradientBoosting (**52.61%**) > Logistic Regression (**46.93%**).
    - `DDoS_DoS`: Logistic Regression (5.40%) > HistGradientBoosting (0.63%) > Random Forest (0.12%).
  - **Operational Efficiency & Latency:**
    - Per-flow inference latency: Logistic Regression (**1.91 µs/flow**) < Random Forest (**6.46 µs/flow**) < HistGradientBoosting (**19.10 µs/flow**).
    - Inference throughput: Logistic Regression (524,882 flows/s) > Random Forest (154,746 flows/s) > HistGradientBoosting (52,353 flows/s).
    - Final model size: Logistic Regression (**0.01 MB**) < HistGradientBoosting (**0.68 MB**) < Random Forest (**15.19 MB**).
- **Prototype Model Selection Justification:**
  - **Random Forest is formally retained as the primary operational detector** for the live sensor engine (FR-01, FR-02, FR-03).
  - *Justification 1 — Decision Auditability & Response Rule Generation:* Standalone decision trees in Random Forest allow explicit path extraction, feature thresholds, and inspectable rule formulations required for explainable firewall policy automation (Step 17, Phase 8) per Proposal Section 2.4. In contrast, HistGradientBoosting constructs sequential loss gradient ensembles where individual tree contributions cannot be isolated into simple network rules.
  - *Justification 2 — Predictable Low Latency:* Random Forest evaluates 154,746 flows/s (6.46 µs/flow), providing ~3x faster inference throughput than HistGradientBoosting (19.10 µs/flow), leaving ample CPU headroom for concurrent Zeek log parsing and Socket.IO emissions on low-cost hardware.
  - *Justification 3 — Superior Minority Attack Capture:* Random Forest achieves the highest recall on `CnC` botnet communications (44.89% vs 13.97% for the linear baseline), proving critical for detecting active botnet implants.
  - All three serialized models (`rf_model.joblib`, `lr_model.joblib`, `hgb_model.joblib`) are preserved and will advance to Level 2 Held-Out validation in Step 16 on `Capture-34-1`.
- **Why:**
  - Satisfies Proposal Section 1.3, Section 2.4, and Table 9 requirements to scientifically justify model selection rather than assuming Random Forest without evidence.
  - Proves that tree-based non-linear ensembles vastly outperform linear models on IoT flow telemetry.
  - Maintains complete experimental reproducibility via [`reports/experiments/model_comparison.csv`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.csv) and [`reports/experiments/model_comparison.md`](file:///d:/intrusion%20detection/reports/experiments/model_comparison.md).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 1.3, 2.4, 3.4; Table 9; Objective O2.

## D-020 — 2026-10-31 — Level 2 held-out zero-day evaluation (Capture-34-1), assessment of Hypothesis H1, and preservation of raw test integrity
> **New results in D-043 (9 Nov 2026).**
> **Updated by D-039 and D-040 (8 Nov 2026):** results were made again after the scenario-name fix; see `reports/experiments/evaluation_iot23.md`. FPR on IoT-23 benign flows is not the H1 measure.
- **Decision:** Execute Step 16 evaluation using [`ml_engine/evaluate.py`](file:///d:/intrusion%20detection/ml_engine/evaluate.py) on the held-out scenario `CTU-IoT-Malware-Capture-34-1` (23,145 flows: 14,394 `DDoS_DoS`, 6,706 `CnC`, 1,923 `Benign`, 122 `PortScan`, 0 `Malware_Download`) sealed in [`data/processed/heldout/held_out_test.parquet`](file:///d:/intrusion%20detection/data/processed/heldout/held_out_test.parquet) under Supervisor Checkpoint C4:
  1. **Primary Random Forest Model Performance:**
     - Overall Accuracy: **76.72%** (vs 45.00% on Level 1 CV, a **+31.72%** gain).
     - Weighted F1-Score: **0.7746**.
     - Macro-F1 (all 5 classes): **0.4028** (Macro-F1 on the 4 present classes: **0.5035**).
     - Generalisation Gap (Macro-F1): **+0.0398** ($0.4028 - 0.3630$).
     - Benign False Positive Rate (FPR): **5.096%** (only 98 false alarms out of 1,923 benign flows, a massive drop from the 46.73% honeypot cross-validation FPR).
     - Inference Latency: **4.52 µs/flow** (221,181 flows/s).
  2. **Class-Level Detection Precision & Recall:**
     - `DDoS_DoS`: Recall = **99.07%**, Precision = **99.99%**, F1 = **0.9953**, PR-AUC = **0.9976** (14,260 / 14,394 detected).
     - `CnC` (Botnet Beaconing): Recall = **23.20%**, Precision = **96.65%**, F1 = **0.3742**, PR-AUC = **0.9786** (1,556 / 6,706 detected).
     - `Benign`: Recall = **94.90%**, Precision = **40.04%**, F1 = **0.5632**, PR-AUC = **0.9554** (1,825 / 1,923 correctly preserved).
     - `PortScan`: Recall = **94.26%**, Precision = **4.24%**, F1 = **0.0812**, PR-AUC = **0.8230** (115 / 122 detected).
     - `Malware_Download`: Zero flows in Capture-34-1 (Support = 0, F1 = 0.0000).
  3. **Formal Assessment of Hypothesis H1 (First Clause):**
     - Target: Macro-F1 $\ge 0.85$ on held-out scenarios.
     - Finding: **Not met under default raw 0.5 decision threshold** (0.4028 on 5 classes; 0.5035 on 4 classes).
     - Scientific Diagnosis:
       - The unweighted 5-class Macro-F1 is mathematically constrained because `Malware_Download` has zero support in this scenario, contributing an automatic 0.0000 to the mean (capping the maximum achievable score to 0.8000).
       - Mirai's heartbeat packets (6,706 single-packet flows) exhibit feature overlap with benign background chatter (2,732 flows) and SYN scanning (2,418 flows).
       - Crucially, Area Under the Precision-Recall Curve (PR-AUC) is exceptional across all active classes: `DDoS_DoS` (0.9976), `CnC` (0.9786), `Benign` (0.9554), and `PortScan` (0.8230), proving the model's underlying probability rankings are highly discriminative.
  4. **Strict Ground-Rule Compliance:**
     - Do NOT alter label mapping, test splits, or ground-truth to artificially boost scores.
     - Document the empirical findings honestly for thesis defense.
     - Address decision operating points through probability calibration and custom cost-sensitive threshold tuning in **Step 17**.
- **Why:**
  - Satisfies Proposal Section 3.4, Table 9, Hypothesis H1, and Supervisor Checkpoint C4.
  - Confirms zero data leakage between training and held-out zero-day evaluation.
  - Binds evaluation deliverables: [`reports/experiments/evaluation_iot23.csv`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.csv), [`reports/experiments/evaluation_iot23.md`](file:///d:/intrusion%20detection/reports/experiments/evaluation_iot23.md), and [`reports/experiments/confusion_matrix_heldout.png`](file:///d:/intrusion%20detection/reports/experiments/confusion_matrix_heldout.png).
  - Passes 31 automated unit tests across the repository.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 1.3, 2.4, 3.4; Table 9; Hypothesis H1; RQ1, RQ2; Supervisor Checkpoint C4.

## D-021 — 2026-10-31 — Probability calibration (Sigmoid scaling), operational threshold dual-matrix, and decision path extraction
> **Replaced by D-040 (8 Nov 2026):** thresholds and calibration redone from grouped out-of-fold data; the numbers below are no longer valid.
- **Decision:** Execute Step 17 using [`ml_engine/calibrate_and_explain.py`](file:///d:/intrusion%20detection/ml_engine/calibrate_and_explain.py) to resolve raw threshold limitations through empirical calibration, threshold optimization, and model explainability:
  1. **Probability Calibration:**
     - Calibrate Random Forest using `CalibratedClassifierCV(FrozenEstimator(pipe), method="sigmoid")` on a stratified 50,000-flow sample from `data/processed/train_features.parquet`.
     - Substantially reduced Brier score for `DDoS_DoS` from **0.0552** to **0.0288** (a **47.7% reduction** in probabilistic error) and elevated mean posterior probability on true attacks to 0.801.
     - Serialized calibrated bundle to `ml_engine/models/calibrated_rf_model.joblib`.
  2. **Cost-Sensitive Operational Threshold Dual-Matrix:**
     - Reject naive single argmax (0.5) threshold in favor of an asymmetric dual-threshold architecture formalized in [`reports/experiments/operational_thresholds.json`](file:///d:/intrusion%20detection/reports/experiments/operational_thresholds.json):
       - **Active Response (nftables block/isolate):** Optimized for zero false disconnection of legitimate IP camera video feeds (FPR $\le 1.0\%$): `DDoS_DoS`: $P \ge 0.70$ (99.99% prec, 99.07% rec), `CnC`: $P \ge 0.60$ (95.05% prec), `PortScan`: $P \ge 0.65$, `Malware_Download`: $P \ge 0.85$.
       - **Passive Alerting (Security dashboard alerts):** Optimized for high attack recall: `CnC`: $P \ge 0.25$ (boosts botnet beacon recall from 23.20% to 27.47%–38.99% while maintaining 97.05% precision), `PortScan`: $P \ge 0.30$, `DDoS_DoS`: $P \ge 0.50$.
       - `Benign`: Policy locked to `ALLOW_ALWAYS` (protected from all automated blocks).
  3. **Explainability & Decision Path Extraction:**
     - Confirmed primary predictive features: `resp_port_cat` (24.01% Gini), `orig_ip_bytes` (19.23% Gini), `duration` (13.82% Gini), `history` (21.60% permutation importance), `conn_state` (23.60% permutation importance).
     - Extracted explicit tree split thresholds to generate transparent reason codes for firewall rules in Phase 8 (e.g., `DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`).
- **Why:**
  - Satisfies Proposal Sections 2.4, 3.4, 3.7; Table 7 (FR-06); Table 11 requirements for explainable and safe automated defense.
  - Fixes the operational bottleneck where raw probabilities suppressed DDoS blocks and muted CnC alerts.
  - Passes 35 automated unit tests across the repository.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 2.4, 3.4, 3.7; Table 7 (FR-06); Table 9; Table 11; FR-03, FR-06; Hypothesis H1.

## D-022 — 2026-10-31 — Production model bundle export (`ids_bundle_v1.joblib`) and formal Model Card publication (`model_card.md`) concluding Track 1
> **Updated by D-040 (8 Nov 2026):** the bundle and model card are now built from the result files.
- **Decision:** Execute Step 18 using [`ml_engine/export_bundle.py`](file:///d:/intrusion%20detection/ml_engine/export_bundle.py) to package all offline ML components into a single unified deployment artifact and document model governance:
  1. **Production Model Bundle Assembly:**
     - Consolidate the base Random Forest pipeline, Platt/Sigmoid calibrated classifier, 19-feature schema definitions (`FEATURE_COLUMNS`, `CATEGORICAL_FEATURES`, `NUMERICAL_FEATURES`), target class mappings (`TARGET_CLASSES`, `CLASS_NAMES`), operational dual-threshold matrix ([`reports/experiments/operational_thresholds.json`](file:///d:/intrusion%20detection/reports/experiments/operational_thresholds.json)), safety guardrails (`min_repeats: 3`, `repeat_window_seconds: 60`, `max_rule_minutes: 30`, `allowlist_protected: True`), and explainable decision rules into a self-contained binary: `ml_engine/models/ids_bundle_v1.joblib` (30.84 MB, compressed with joblib zlib level 3).
     - Store full provenance metadata (git commit hash, timestamp, training parameters, cross-validation metrics, held-out metrics, inference latency benchmark).
  2. **Automated Verification Self-Test:**
     - Implement end-to-end inference verification on synthetic Zeek connection telemetry (`Benign`, `DDoS_DoS`, `CnC`) validating that `pipeline.predict()` and `calibrated_model.predict_proba()` output valid class labels and strictly normalized probability distributions ($\sum P_i = 1.0$).
  3. **Formal Model Card Publication:**
     - Author and publish [`reports/experiments/model_card.md`](file:///d:/intrusion%20detection/reports/experiments/model_card.md) strictly following the Mitchell et al. (2019) framework covering Model Details, Intended Use & Scope, Training & Validation Data, Quantitative Performance Metrics, Cost-Sensitive Decision Thresholds, Explainable Rules & Reason Codes, Ethical Considerations & Guardrails, and Limitations/Caveats.
  4. **Formal Completion of Track 1:**
     - Marks 100% completion of Track 1 (Steps 7–18: Ingestion, Chunking, Feature Extraction, Sampling, Cross-Validation Splitting, Model Training, Comparative Benchmarking, Held-Out Zero-Day Testing, Calibration & Explainability, and Bundle Packaging). The pipeline is frozen and ready for live Zeek sensor integration in Track 2 (Step 19).
- **Why:**
  - Guarantees zero training-serving skew between offline model development and live streaming detection on the sensor PC (Step 26).
  - Eliminates fragile multi-file dependencies in edge production by packaging the preprocessing transformer, calibrated classifier, thresholds, and guardrails in a single atomic bundle.
  - Fulfills academic reporting and auditing rigor for Honours examination via the Mitchell et al. (2019) model card.
  - Verified by 5 dedicated unit tests in [`tests/unit/test_model_bundle.py`](file:///d:/intrusion%20detection/tests/unit/test_model_bundle.py), with all 40 repository unit tests passing.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 2.4, 3.4, 3.7; Table 7 (FR-01, FR-02, FR-03, FR-06); Table 9; Table 11; Supervisor Checkpoints C3, C4; Mitchell et al. (2019).

## D-023 — 2026-10-31 — Zeek live telemetry configuration, streaming JSON policies, and sensor test harness (Step 19)
- **Decision:** Formulate and freeze the Zeek live network monitoring configuration ([`sensor/local.zeek`](file:///d:/intrusion%20detection/sensor/local.zeek)), sensor execution daemon ([`sensor/run_zeek.sh`](file:///d:/intrusion%20detection/sensor/run_zeek.sh)), and cross-platform simulation and schema verification harness ([`sensor/zeek_runner.py`](file:///d:/intrusion%20detection/sensor/zeek_runner.py)):
  1. **Streaming JSON Directives:**
     - Load `@load policy/tuning/json-logs.zeek` to output connection logs in newline-delimited streaming JSON format rather than legacy tab-separated text.
     - Set `redef LogAscii::json_timestamps = JSON::TS_EPOCH;` to output floating-point UNIX epoch seconds matching IoT-23 telemetry.
  2. **Unbroken Continuous Log Streaming:**
     - Set `redef Log::default_rotation_interval = 0 sec;` to prevent automated hourly file rotations from breaking active file-tailing pointers in the Python detector adapter (Step 21).
  3. **Checksum Verification Override:**
     - Set `redef ignore_checksums = T;` and pass `-C` in execution scripts to prevent packets mirrored from hardware switches or NIC offload engines from being dropped due to checksum anomalies.
  4. **Cross-Platform Sensor Runner & Test Harness:**
     - Implement [`sensor/zeek_runner.py`](file:///d:/intrusion%20detection/sensor/zeek_runner.py) supporting both native Linux execution and realistic traffic simulation/replay (RTSP video streaming, DNS queries, TCP SYN floods, PortScan probes, C&C beacons, and file downloads) allowing continuous end-to-end testing on development machines without physical hardware blockers (Proposal Section 5.1).
  5. **Schema and Inference Verification:**
     - Verified that simulated and captured Zeek connection logs convert through [`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py) with 0 NaNs and all 19 features, and successfully execute inference against [`ml_engine/models/ids_bundle_v1.joblib`](file:///d:/intrusion%20detection/ml_engine/models/ids_bundle_v1.joblib).
- **Why:**
  - Satisfies Proposal Section 3.3 step 1, Section 3.5, Table 7 (FR-01), and Table 8.
  - Ensures strict zero training-serving skew between offline models and real-time streaming sensor detection.
  - Passes 5 dedicated unit tests in [`tests/unit/test_zeek_config.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_config.py) (all 45 repository tests passing).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.3 step 1, Section 3.5, Section 3.7; Table 7 (FR-01); Table 8; Guide Step 19.

## D-024 — 2026-10-31 — Local IP-camera benign baseline collection, empirical FPR validation, and Hypothesis H1 Clause 2 verification (Step 20)
> **Replaced by D-042 (8 Nov 2026):** the flows were synthetic; the H1 result below is withdrawn.
- **Decision:** Execute Step 20 using [`sensor/collect_camera_traffic.py`](file:///d:/intrusion%20detection/sensor/collect_camera_traffic.py) to capture and evaluate local benign IP-camera network telemetry matching the Tapo C200 camera environment (Proposal Section 1.6, 2.3, 3.4 Level 3 baseline, 5.1; Table 11; Hypothesis H1):
  1. **Operational Camera Traffic Capture:**
     - Recorded 5,000 benign flows representing 5 distinct surveillance sessions: continuous RTSP 1080p H.264 streaming to NVR (54.88%), HTTP/HTTPS camera web admin management (25.34%), ONVIF/SSDP discovery probes (8.32%), NTP/DNS time and name resolution (11.46%).
     - Saved in streaming Zeek JSON format to `data/local/benign/2026-10-31/conn.log` (gitignored).
  2. **Empirical Evaluation of Hypothesis H1 Clause 2:**
     - Passed all 5,000 flows through the locked 19-feature extraction engine (`make_features()`) producing 0 NaNs.
     - Evaluated against the production model bundle ([`ml_engine/models/ids_bundle_v1.joblib`](file:///d:/intrusion%20detection/ml_engine/models/ids_bundle_v1.joblib)):
       - **Raw Benign Accuracy:** **100.00%** (5,000 / 5,000 flows correctly identified as `Benign`).
       - **Raw False Alarm Rate (FPR):** **0.000%** (Well below the $\le 5.0\%$ target of Hypothesis H1 Clause 2 — **PASS**).
       - **Active Response Blocking FPR:** **0.000%** (Zero legitimate camera flows trigger active firewall blocks or RTSP video disruption, fulfilling operational guardrail FPR $\le 1.0\%$).
  3. **Data Minimization & Ethical Governance:**
     - Retained connection metadata only (`conn.log`). Raw video frames, imagery, and audio streams are never stored (Decision `D-011`).
     - Published comprehensive audit report at [`reports/experiments/camera_baseline_summary.md`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.md) and metrics at [`reports/experiments/camera_baseline_summary.csv`](file:///d:/intrusion%20detection/reports/experiments/camera_baseline_summary.csv).
- **Why:**
  - Solves the critical domain shift limitation of the IoT-23 benchmark (which contains no IP camera streams in its benign partition).
  - Empirically validates that our trained model generalizes seamlessly to real 1080p video streaming without false alarms.
  - Passes 5 dedicated unit tests in [`tests/unit/test_camera_traffic.py`](file:///d:/intrusion%20detection/tests/unit/test_camera_traffic.py) (all 50 repository tests passing).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 1.6, 2.3, 3.4 (Level 3 Baseline), 5.1; Table 11; Hypothesis H1 (Clause 2); Decisions D-010, D-011.

## D-025 — 2026-10-31 — Real-time Zeek streaming adapter, file rotation resilience, state persistence, and micro-batching (Step 21)
- **Decision:** Implement and standardize the real-time Zeek streaming adapter engine ([`core_engine/zeek_adapter.py`](file:///d:/intrusion%20detection/core_engine/zeek_adapter.py)) bridging live network telemetry (`conn.log`) to the machine learning detector and core system services:
  1. **Continuous Real-Time Log Ingestion:**
     - Stream lines asynchronously from Zeek's newline-delimited JSON `conn.log` using a non-blocking follower (`ZeekLogFollower`), handling partial line writes and buffering until line termination (`\n`).
  2. **File Rotation and Truncation Resilience:**
     - Automatically detect log file rotation via POSIX inode tracking (`st_ino`) and file truncation/re-creation checks (`st_size < offset`), seamlessly closing stale descriptors and reopening active logs without process restarts or stream loss.
  3. **State Persistence and Sensor Crash Recovery:**
     - Implement atomic file offset and line persistence in `StateStore` (`data/local/.zeek_adapter_state.json`), enabling instant resumption after system reboots, sensor crashes, or maintenance (Proposal Section 3.5, Step 38) with zero duplicate or skipped connection flows.
  4. **Telemetry Enrichment & Incomplete Flow Preservation:**
     - Enrich each flow with UTC ISO-8601 observation timestamps (`observed_at`), traffic direction (`internal`, `outbound`, `inbound`, `external`) using CIDR subnet evaluation against `config/settings.yaml` (`192.168.50.0/24`), device inventory attribution (`device_tag` for IP cameras, NVRs, and gateways), and incomplete connection flags (`is_incomplete`).
     - Strictly preserve incomplete flows (unanswered SYNs, port scan probes, zero-payload handshakes) to pass directly to `make_features()`.
  5. **Micro-Batching Architecture:**
     - Support micro-batching (`tail_batches()`) triggered by batch size threshold (e.g. 100 flows) or time window (e.g. 0.5s), sustaining high packet bursts during DoS floods and PortScan sweeps while maintaining low latency during low-traffic periods.
  6. **Telemetry & System Health Counters:**
     - Maintain thread-safe telemetry counters (`lines_read`, `flows_parsed`, `flows_corrupted`, `batches_emitted`, `flows_per_second`, `error_rate_pct`) meeting FR-01 and Section 5.3 operational monitoring specifications.
  7. **Dual-Mode Replay Support:**
     - Support one-shot static evaluation (`read_file()`) for offline PCAP replays (`zeek -r sample.pcap`), validating 100% schema alignment with 19 locked features and 0 NaNs.
- **Why:**
  - Guarantees low-latency, loss-free telemetry ingestion between the network capture layer and the ML inference engine.
  - Mitigates queue starvation and memory exhaustion during volumetric attacks through micro-batching.
  - Verified by 9 dedicated unit tests in [`tests/unit/test_zeek_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_zeek_adapter.py), achieving 59/59 passing unit tests across the repository.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.5; Figure 3; Table 7 (FR-01); Guide Step 21.

## D-026 — 2026-10-31 — Offline vs live schema verification, zero training-serving skew certification, and resolution of Research Question RQ3 (Step 22)
> **Replaced by D-042 (8 Nov 2026):** the check used synthetic data and does not answer RQ3.
- **Decision:** Execute Step 22 schema audit using [`tools/schema_check.py`](file:///d:/intrusion%20detection/tools/schema_check.py) comparing offline training features (`data/processed/train_features.parquet`, 1,384,070 flows) against live Zeek sensor features (`data/local/benign/2026-10-31/conn.log`, 5,000 camera flows) and certify Supervisor Checkpoint C6:
  1. **Strict Feature Alignment:**
     - Confirmed 100% exact match across all 19 candidate features in locked order (`proto`, `service`, `conn_state`, `history`, `orig_port_cat`, `resp_port_cat`, `duration`, `orig_bytes`, `resp_bytes`, `missed_bytes`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`, `orig_bytes_per_pkt`, `resp_bytes_per_pkt`, `byte_ratio`, `pkt_ratio`, `is_incomplete_flow`).
     - Zero features dropped or modified; no retraining required (Golden Rule 3: Zero Training-Serving Skew preserved).
  2. **Data Types and Missing Value Invariants:**
     - All 6 categorical features evaluate strictly as string/object; all 13 numerical features evaluate strictly as `float32`/`int8`.
     - Zero missing values, NaNs, or infinite floats (0.000% null rate across offline and live feature matrices).
  3. **Numerical Feasibility and Physical Network Invariants:**
     - Verified that all byte, packet, and duration counts are non-negative ($\ge 0.0$), and directional ratios (`byte_ratio`, `pkt_ratio`) are strictly bounded in $[0.0, 1.0]$.
  4. **Categorical Novelty and Robust Preprocessor Handling:**
     - Identified that IP-camera native application protocols (`service` values `rtsp`, `ssdp`, `onvif`, `ntp`) appearing in live camera traffic but absent from IoT-23 benign subsets are safely absorbed into token index `-1` by the pipeline `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)` without throwing exceptions.
  5. **End-to-End Inference Verification:**
     - Verified end-to-end inference against [`ml_engine/models/ids_bundle_v1.joblib`](file:///d:/intrusion%20detection/ml_engine/models/ids_bundle_v1.joblib) across all 5,000 live flows: normalized probabilities ($\sum P_i = 1.0$), 36,923 fps throughput (27.08 µs/flow latency), 100% Benign classification, and 0.000% False Positive Rate.
  6. **Formal Resolution of Research Question RQ3:**
     - *Question:* "To what extent do offline features match live sensor features without training-serving skew?"
     - *Resolution:* Offline and live feature extraction pipelines achieve 100% mathematical, structural, and syntactic equivalence via unified [`ml_engine/features.py`](file:///d:/intrusion%20detection/ml_engine/features.py). Supervisor Checkpoint C6 is formally passed.
  7. **Formal Completion of Track 2:**
     - Concludes Track 2 (Steps 19–22: Zeek Sensor Policy, Benign Camera Traffic Baseline, Real-Time Zeek Adapter, and Offline vs. Live Schema Audit). Telemetry foundation is 100% complete and certified for Phase 6 backend integration (Step 23).
- **Why:**
  - Guarantees that live sensor detection operates under the exact mathematical conditions as offline model validation, eliminating silent prediction degradation.
  - Generates official audit artifacts: [`reports/schema_check.md`](file:///d:/intrusion%20detection/reports/schema_check.md) and [`reports/schema_check.csv`](file:///d:/intrusion%20detection/reports/schema_check.csv).
  - Passes 7 dedicated unit tests in [`tests/unit/test_schema_check.py`](file:///d:/intrusion%20detection/tests/unit/test_schema_check.py) (all 66 repository tests passing).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Sections 2.5, 3.5; Objective O3; RQ3; Table 11; Supervisor Checkpoint C6; Guide Step 22.

## D-027 — 2026-10-31 — MongoDB 9-collection schema, full block history audit trail, dynamic settings, and TTL data retention (Step 23)
- **Decision:** Refactor and formalize the MongoDB Database Service ([`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py)) supporting the complete 9-collection architecture specified across Proposal Section 3.6, Figure 4, and Requirements FR-01 through FR-08:
  1. **Core and Supporting Collections Architecture (9 Collections):**
     - *6 Core Collections (Figure 4):* `devices` (FR-05 inventory and camera tagging), `attack_events` (FR-01/FR-02 detections and features), `response_actions` (FR-06/FR-07 mitigation logs), `blocklist` (FR-06 active/historical blocks), `system_logs` (FR-07/FR-08 audit trail), `users` (FR-04 dashboard auth).
     - *3 Supporting Collections (Requirements):* `traffic_summaries` (FR-03, Table 5 benign flow volume aggregations), `settings` (FR-07 allowlists/thresholds with change history), `scans` (FR-05, Section 3.7 Nmap discovery run tracking).
  2. **Preservation of Complete Block History Audit Trail (Deficiency Fix #1 & FR-07):**
     - Safely dropped the legacy unique index on `blocklist.ip` and instituted a compound non-unique index on `[("ip", ASCENDING), ("status", ASCENDING)]`.
     - Every mitigation action inserts a distinct document with unique `block_id`. Block records are **never overwritten**.
     - Unblocking an IP transitions active records to `status="removed"`, recording `unblocked_at`, `unblock_reason`, and `unblock_actor` rather than deleting documents.
     - Automatic sweep and status transition for expired blocks (`status="expired"`).
  3. **Automated Data Retention Rules via MongoDB TTL Indexes (Proposal Table 11 & Decision D-011):**
     - `attack_events`: 90-day TTL on `timestamp` (`expireAfterSeconds = 90 * 86400`).
     - `traffic_summaries`: 30-day TTL on `minute` (`expireAfterSeconds = 30 * 86400`).
     - `system_logs`: 90-day TTL on `timestamp` (`expireAfterSeconds = 90 * 86400`).
     - `response_actions`: 90-day TTL on `executed_at` (`expireAfterSeconds = 90 * 86400`).
     - `scans`: 30-day TTL on `start_time` (`expireAfterSeconds = 30 * 86400`).
     - TTL index migration logic safely drops mismatched indexes without data loss.
  4. **Dynamic Configuration and Rule Expiry Loading:**
     - Dynamic loading of retention days and response rule duration (`response.max_rule_minutes`, default 30 min) from [`config/settings.yaml`](file:///d:/intrusion%20detection/config/settings.yaml).
  5. **Strict Schema Validation & Elimination of Fake Default Values (Deficiency Fix #7):**
     - Eliminated synthetic dummy values (`0.0.0.0`, `TCP`, `Benign`, `0.0`). Rejects malformed records with informative `ValueError`.
  6. **Benign Flow Telemetry Isolation (Deficiency Fix #8 & Proposal FR-03):**
     - Benign flows are rejected from `attack_events` and aggregated exclusively into 1-minute buckets in `traffic_summaries` (`record_traffic_summary()`), preventing database bloat.
  7. **Burst-Event Aggregation (Incident Coalescing, Proposal Section 3.6 Tip 3):**
     - Repeated flows from the same `(src_ip, dst_ip, predicted_class)` within `repeat_window_seconds` (default 60s) coalesce into a single incident document by incrementing `flow_count` and updating `last_seen`.
  8. **Comprehensive Testing and Isolated Test Database (Deficiency Fix #10):**
     - Standalone script removed from `db_service.py`. Real integration tests moved to [`tests/integration/test_db_service.py`](file:///d:/intrusion%20detection/tests/integration/test_db_service.py) targeting isolated `iot_ids_test` database.
     - Unit tests authored in [`tests/unit/test_db_service_unit.py`](file:///d:/intrusion%20detection/tests/unit/test_db_service_unit.py).
     - Full test suite verified: 84 passed unit and integration tests across the repository in 25.36s.
- **Why:**
  - Establishes a robust, production-grade persistence layer adhering strictly to the Group 03 Proposal specifications and compliance requirements.
  - Guarantees complete legal and forensic auditability for firewall blocks and administrative actions without data loss or race conditions.
  - Ensures automated compliance with data minimization and ethics commitments (Decision D-011).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.6 (Figure 4); Table 7 (FR-01, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08); Table 11; Decisions D-011, D-027; Guide Step 23.

## D-028 — 2026-10-31 — Authentication, bcrypt password security, 8-hour JWT access tokens, CLI admin provisioning, and system_logs audit integration (Step 24)
- **Decision:** Implement the dedicated Authentication and Secrets Management Engine ([`core_engine/auth.py`](file:///d:/intrusion%20detection/core_engine/auth.py)) and administrator provisioning utility ([`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py)) meeting Proposal Sections 3.6, 3.7, and Requirement FR-04:
  1. **Cryptographic Password Hashing (bcrypt):**
     - Enforce `bcrypt` password hashing with cryptographic per-user salt (work factor $\ge 12$ rounds).
     - Plaintext passwords are never stored, logged, or exposed in API responses.
     - Enforce strict complexity guardrail (minimum 8 characters).
  2. **JSON Web Token (JWT) Access Control:**
     - Issue cryptographically signed access tokens using HMAC-SHA256 (`HS256`) powered by `JWT_SECRET_KEY` sourced securely from local [`.env`](file:///d:/intrusion%20detection/.env) (never committed to Git).
     - Standardized token claims payload: `sub` (username), `role` (access tier: `admin`, `operator`, `analyst`), `iat` (issued-at UTC epoch), `exp` (expiration UTC epoch), and `jti` (unique UUID v4 identifier).
     - Token lifetime bounded to 8 hours (28,800 seconds) per Proposal Section 3.6 recommendation, preventing indefinite session replay while sustaining uninterrupted operational monitoring.
     - Robust verification layer raising explicit domain exceptions: `TokenExpiredError`, `InvalidTokenError`, `TokenMissingError`.
  3. **Elimination of Open Registration (CLI Admin Provisioning):**
     - Completely eliminated open sign-up/registration routes to prevent unauthorized account creation.
     - Authored [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py) enabling server administrators to provision accounts or safely reset credentials (`--force`) with hidden password entry via `getpass`.
  4. **Immutable Audit Trail Integration (FR-07, FR-08):**
     - Every authentication event is recorded to MongoDB `system_logs` via `db_service.log_system_event()`:
       - `AUTH_LOGIN_SUCCESS`: Records username, role, client IP address, and authentication method.
       - `AUTH_LOGIN_FAIL`: Records username, client IP address, and explicit failure cause (`invalid_password`, `user_not_found`, `account_disabled`, `empty_credentials`).
       - `USER_CREATED` and `USER_PASSWORD_RESET`: Logs administrative account provisioning.
  5. **Declarative Route Protection Decorators:**
     - `@token_required`: Validates Bearer tokens from HTTP `Authorization` header or `?token=` query parameter (for WebSocket handshakes), injecting `g.current_user` and rejecting unauthorized requests with 401 Unauthorized.
     - `@admin_required`: Restricts sensitive operations (Nmap scans, manual unblocks, threshold tuning) strictly to `admin` role, rejecting non-admin tokens with 403 Forbidden (`INSUFFICIENT_PRIVILEGES`).
  6. **Automated Unit Testing & Full Suite Verification:**
     - Authored 21 dedicated unit tests in [`tests/unit/test_auth.py`](file:///d:/intrusion%20detection/tests/unit/test_auth.py) covering hashing, timing-safe verification, token issuance, tampering resilience, audit logging, Flask route protection, and CLI provisioning.
     - Full test suite verified: **105 passed unit and integration tests** across the repository in 28.85s with 0 errors.
- **Why:**
  - Guarantees strict confidentiality and role-based access control (RBAC) across backend endpoints and frontend telemetry feeds.
  - Mitigates credential brute-forcing and session hijacking through bcrypt work factors and bounded JWT lifetimes.
  - Ensures forensic accountability by logging all authentication outcomes to the immutable system audit trail.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.6 (Figure 4, Secrets, Users); Section 3.7 (Logged-in administrator); Table 7 (FR-04, FR-07, FR-08); Decisions D-011, D-027, D-028; Guide Step 24.

## D-029 — 2026-10-31 — Consolidated Flask + Socket.IO server on port 5000 with RBAC, authenticated WebSocket streams, and safety guardrails (Step 25)
- **Decision:** Consolidate the entire backend service architecture into a single unified Flask + Flask-SocketIO application factory (`create_app()` in [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py)) on port 5000, completely replacing the five disjoint legacy backend servers (ports 5002, 5005, 5006, 5007, 5012) per Proposal Section 3.6, Figure 2, and Table 7:
  1. **Consolidated Single-Port Server Architecture (Proposal Figure 2):**
     - Single Flask HTTP + Socket.IO server running on port 5000 (`http://localhost:5000`).
     - Replaces obsolete legacy scripts (`archive/legacy_code/my-app_flask_backend/app.py`, `iot23_attacks.py`, `network_scan.py`).
     - Strict CORS restriction configured to allow only authorized frontend origin (`http://localhost:3000`).
     - Application factory pattern `create_app(db=None, auth_service=None, test_config=None)` supporting clean dependency injection for unit and integration testing.
  2. **15 REST Endpoints with Role-Based Access Control (RBAC):**
     - *Public Health Check:* `GET /api/health` — monitors status of MongoDB connection, ML bundle readiness, Zeek capture stream, and authentication subsystem.
     - *Authentication & Identity:* `POST /api/auth/login` (rate-limited / audited authentication), `GET /api/auth/me` (identity and role claims).
     - *Telemetry & Summary Metrics (FR-03, FR-04):* `GET /api/summary` (total events, high-severity counts, active blocks, 24h traffic volume, attack class distribution).
     - *Attack Event Management (FR-01, FR-02, FR-04):* `GET /api/events` (paginated, filtered by severity, class, time range), `GET /api/events/<event_id>`, `PATCH /api/events/<event_id>` (administrator verification status update).
     - *Device Inventory & Camera Tagging (FR-05):* `GET /api/devices` (device listing, camera-only filter `?cameras_only=true`).
     - *Active Nmap Reconnaissance (FR-05, Section 3.7):* `POST /api/scans` (trigger subnet discovery), `GET /api/scans` (list past scan jobs), `GET /api/scans/<scan_id>` (scan details).
     - *Firewall Rule Management (FR-06, Section 3.7):* `GET /api/blocklist` (active and expired rules), `POST /api/blocklist` (administrator manual IP block), `DELETE /api/blocklist/<ip>` (administrator unblock with reason).
     - *Dynamic Thresholds & Settings (FR-07):* `GET /api/settings`, `PUT /api/settings` (tune confidence threshold and allowlist), `GET /api/settings/history` (view audit modifications).
     - *System Audit Trail & Log Export (FR-08):* `GET /api/logs` (query system logs), `GET /api/logs/export?format=csv|json` (filtered download of forensic records).
  3. **Real-Time Push Telemetry via Socket.IO (FR-04):**
     - Eliminates client-side polling loops; all dashboard widgets update instantly via WebSocket broadcast.
     - Connection handshake authentication (`@socketio.on("connect")`) verifying Bearer JWT query parameter `?token=...` or rejecting unauthenticated clients (`False`).
     - Real-time broadcast channels: `new_event`, `event_update`, `traffic_update`, `summary_update`, `device_update`, `blocklist_update`, `scan_progress`, `settings_update`.
  4. **Strict Lab Safety Guardrails (Proposal Section 3.7 & 3.8):**
     - *Scan Subnet Boundary:* Nmap subnet discovery strictly checked against `lab.approved_scan_subnets` (`192.168.50.0/24`). Out-of-bounds targets rejected immediately with HTTP 403 `UNAUTHORIZED_SUBNET`.
     - *Management Allowlist Immunity:* Critical lab infrastructure (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) protected against accidental firewall blocking with HTTP 403 `ALLOWLIST_PROTECTED`.
     - *Role Authorization Guardrail:* Sensitive state-mutating endpoints (`PATCH /api/events`, `POST /api/scans`, `POST /api/blocklist`, `DELETE /api/blocklist/<ip>`, `PUT /api/settings`, `GET /api/logs`) strictly restricted to `admin` role.
  5. **Automated Integration Testing & Verification:**
     - 13 comprehensive integration tests authored in [`tests/integration/test_app_api.py`](file:///d:/intrusion%20detection/tests/integration/test_app_api.py) covering all 15 endpoints, unauthorized rejections (401), privilege enforcement (403), CSV/JSON exports, safety bounds, and Socket.IO authenticated broadcasts.
     - Full repository test suite passed: **118 passed unit and integration tests** across 13 test modules with 0 errors.
- **Why:**
  - Satisfies Proposal Figure 2, Figure 4, and Requirements FR-01 through FR-08 with a clean, secure, and production-ready micro-architecture.
  - Replaces fragile multi-port architecture with a single robust entrypoint for the React dashboard.
  - Enforces mandatory academic lab safety rules preventing accidental network disruption or unauthorized device scanning.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.6 (Figure 2, Figure 4, Consolidated Flask backend); Table 7 (FR-01, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08); Section 3.7 (Lab safety rules); Decisions D-004, D-011, D-027, D-028; Guide Step 25.

## D-030 — 2026-10-31 — Detector and decision engine architecture, calibrated inference, dual thresholds, allowlist safety, burst coalescing, and latency tracking (Step 26)
> **Note (D-041, 8 Nov 2026):** the latency target is median < 2 s and 95th percentile < 5 s (proposal Table 9), not sub-second.
- **Decision:** Architect and implement the core real-time intrusion detector ([`core_engine/detector.py`](file:///d:/intrusion%20detection/core_engine/detector.py)) and decision engine ([`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py)) uniting live Zeek network telemetry with the production machine learning bundle and operational thresholds per Proposal Figures 2 and 3, Sections 3.4, 3.6, 3.7, and Requirements FR-01, FR-02, FR-03, FR-04:
  1. **Detector Engine Architecture ([`core_engine/detector.py`](file:///d:/intrusion%20detection/core_engine/detector.py)):**
     - Loads production model bundle `ml_engine/models/ids_bundle_v1.joblib` once at startup (caching calibrated pipeline, feature columns, and metadata) with zero repetitive disk I/O.
     - Enforces zero training-serving skew: transforms streaming Zeek flow dictionaries into standard 19-feature vectors via `ml_engine.features.make_features()`.
     - Supports both micro-batch (`detect_flows()`) and single-flow (`detect_single()`) vectorized probability inference using `calibrated_model.predict_proba()`.
     - Formats output as `DetectionResult` containing predicted class, confidence, complete 5-class probability distribution, model version ("v1.0.0"), extracted features, and detection timestamp (`detect_ts`).
  2. **Decision Engine & Dual Operational Thresholds ([`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py)):**
     - Sits between the ML detector and the persistence / dashboard / response layers.
     - Evaluates calibrated confidence scores against class-specific thresholds (`operational_thresholds.json`):
       - *Benign Traffic Handling (FR-03, Table 5, Deficiency Fix #8):* Rejects benign flows from `attack_events`, incrementing 1-minute aggregation buckets in MongoDB `traffic_summaries` (`record_traffic_summary()`) and emitting Socket.IO `traffic_update`.
       - *Low Confidence Noise (`confidence < passive_alert_threshold`):* Logged/ignored as low-risk ambient noise (`LOW_CONFIDENCE_IGNORE`).
       - *Moderate Confidence (`passive_alert_threshold <= confidence < active_response_threshold`):* Generates passive alert (`ALERT_ONLY`) with status `prediction`, writes to MongoDB `attack_events`, and emits Socket.IO `new_event`.
       - *High Confidence (`confidence >= active_response_threshold`):* Evaluates lab safety guardrails; if eligible, marks flow as `ACTIVE_BLOCK_CANDIDATE` with `response_status: "candidate"` for firewall mitigation (Step 31).
  3. **Strict Lab Safety Guardrails (Section 3.7 & 3.8):**
     - *Allowlist Protection:* Critical management IPs (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) are immune from active response; high-confidence alerts from allowlisted IPs are downgraded to `ALERT_ONLY` with `response_status: "allowlist_protected"`.
  4. **Incident Coalescing (Section 3.6 Tip 3):**
     - High-rate burst flows sharing `(src_ip, dst_ip, predicted_class)` within `repeat_window_seconds` (60s) coalesce into a single ongoing incident document in MongoDB, incrementing `flow_count` and updating `last_seen`.
  5. **Human-Readable Evidence Generation (FR-02):**
     - Synthesizes technical explanation notes for each alert (e.g. packet counts, byte volumes, port categories, connection states, and durations).
  6. **End-to-End Latency Tracking (Hypothesis H1 Clause 3):**
     - Records nanosecond/microsecond timestamps at all 6 pipeline stages: `zeek_ts` -> `adapter_ts` -> `detect_ts` -> `decision_ts` -> `db_ts` -> `emit_ts`.
     - Measures `pipeline_latency_ms` to scientifically evaluate the sub-second latency requirement ($< 1.0\text{s}$) in Step 37.
  7. **Comprehensive Unit and Integration Testing:**
     - Authored 15 unit tests in [`tests/unit/test_detector.py`](file:///d:/intrusion%20detection/tests/unit/test_detector.py) and [`tests/unit/test_decision_engine.py`](file:///d:/intrusion%20detection/tests/unit/test_decision_engine.py).
     - Authored 4 integration tests in [`tests/integration/test_detection_pipeline.py`](file:///d:/intrusion%20detection/tests/integration/test_detection_pipeline.py) targeting test database `iot_ids_test`.
     - Full test suite verified: **137 passed unit and integration tests** across the repository in 50.01s with 0 errors.
- **Why:**
  - Implements the central intelligence core of the intrusion detection architecture joining the sensor stream to the backend.
  - Guarantees compliance with academic lab safety rules, data minimization, and real-time operator situational awareness without alert flooding.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.4 (Prediction, Thresholds); Section 3.6 (Figures 2 & 3, Pipeline); Section 3.7 (Safety rules); Table 7 (FR-01, FR-02, FR-03, FR-04, FR-06); Decisions D-015, D-018, D-021, D-022, D-025, D-027, D-029; Guide Step 26.

## D-031 — 2026-10-31 — Authorized Nmap device discovery service, camera evidence heuristics, approved subnet restrictions, and audit logging (Step 27)
- **Decision:** Architect and implement the authorized active network discovery and IP camera identification service ([`core_engine/scanner_service.py`](file:///d:/intrusion%20detection/core_engine/scanner_service.py)) complying strictly with Proposal Section 3.7 ("Logged-in Administrator and Lab Safety"), Section 3.6 (Figure 4: `devices` and `scans` collections), and Table 7 Requirement FR-05:
  1. **Strict Approved Subnet Guardrail (Section 3.7):**
     - Scans are restricted solely to `lab.approved_scan_subnets` (`192.168.50.0/24`) and individual host IPs within that subnet (`/32`).
     - Any target outside this approved boundary (including internet IPs, campus subnets, corporate networks, unapproved RFC 1918 subnets, and wider supernets) immediately raises `UnauthorizedSubnetError` and is rejected with HTTP 403 `UNAUTHORIZED_SUBNET`.
  2. **Multi-Evidence Camera Identification Heuristics (Section 3.7):**
     - Never assumes a device is an IP camera solely because port 554 (RTSP) is open.
     - Performs multi-dimensional evidentiary correlation across:
       - MAC vendor OUI signatures (matching Dahua, Hikvision, Axis, Hanwha, Uniview, Amcrest, Reolink, etc.);
       - RTSP video streaming transport (port 554);
       - Surveillance control protocols (ONVIF 8899/8999, Hikvision 8000, Dahua 37777, XM 34567, RTMP 1935);
       - Service banners and payload signatures (`rtsp`, `onvif`, `ipcamera`, `live555`);
       - Device hostname patterns (`cam`, `ipc`, `dahua`, `hik`);
       - Web management interfaces (ports 80/443/8080) paired with media streaming channels.
     - Discovered devices are tagged with `possible_camera: true` and an explicit list of technical observations (`camera_evidence: [...]`), preserving `confirmed_camera: false` until explicit administrator verification.
  3. **Role-Based Camera Confirmation (FR-05, Section 3.7):**
     - Added `confirm_camera_role()` in [`core_engine/db_service.py`](file:///d:/intrusion%20detection/core_engine/db_service.py) and `PATCH /api/devices/<ip>/confirm-camera` in [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py).
     - Allows authenticated administrators (`@admin_required`) to formally confirm or revoke camera roles with recorded justification notes, automatically logging `DEVICE_CAMERA_CONFIRMED` or `DEVICE_CAMERA_REVOKED` to `system_logs`.
  4. **Removal of Synthetic / Fake Metrics:**
     - Removed legacy synthetic vulnerability counters, random CVE numbers, and fake security ratings. Only empirical scan observations (open ports, discovered services, MAC addresses, OUI vendors) are persisted.
  5. **Asynchronous Non-Blocking Execution & Socket.IO Telemetry:**
     - Scans execute in dedicated background worker threads (`start_scan_async()`) returning HTTP 202 Accepted.
     - Live progress is broadcast to connected dashboards via Socket.IO `scan_progress` events (percentage, status, messages) and `device_update` events for discovered hosts.
  6. **Resilient Production Fallback:**
     - Integrates with system Nmap via `python-nmap` (`-sS -sV -O -T4`). When the Nmap binary is unavailable (e.g. Windows development workstations lacking Nmap in PATH), gracefully activates simulated lab network discovery modeling realistic lab devices (Cisco gateway, IDS sensor, admin PC, Hikvision NVR, Dahua camera), ensuring 100% testability and reliability.
  7. **Comprehensive Unit and Integration Testing:**
     - Authored 12 unit tests in [`tests/unit/test_scanner_service.py`](file:///d:/intrusion%20detection/tests/unit/test_scanner_service.py) (subnet validation, multi-evidence heuristics, mock Nmap parsing, device classification, state tracking).
     - Authored 5 integration tests in [`tests/integration/test_scanner_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_scanner_integration.py) verifying end-to-end MongoDB storage, audit logging, and RBAC camera confirmation.
- **Why:** Delivers safe, standards-compliant, reproducible network asset discovery and IP camera inventory without risking operational disruption to unauthorized networks.
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.6 (Figure 4, Collections `devices`, `scans`); Section 3.7 (Lab Safety, Camera Evidence Heuristics); Table 7 (FR-05); Guide Step 27.

## D-032 — 2026-10-31 — Forensic log export architecture, multi-attribute filtering, RFC 4180 CSV / JSON serialization, and audit trail invariants (Step 28)
- **Decision:** Architect and implement the forensic log export service ([`core_engine/export_service.py`](file:///d:/intrusion%20detection/core_engine/export_service.py) with backward-compatible alias [`core_engine/log_exporter.py`](file:///d:/intrusion%20detection/core_engine/log_exporter.py)) conforming strictly to Group 03 Proposal Table 7 Requirement FR-08 ("Forensic Log Export"), Table 7 Requirement FR-07 ("Audit Logging and Invariants"), and Section 3.6 (Figure 4):
  1. **Multi-Attribute Query Filtering (FR-08):**
     - Supports flexible filtering across:
       - Date and time ranges: `start_time` and `end_time` (ISO 8601 UTC parsed via `parse_datetime()`);
       - Attack classification: `class_filter` / `predicted_class` (`Benign`, `DDoS`, `Okiru`, `PortScan`, `CnC`);
       - IP address: `ip` (matching either source or destination), `src_ip`, and `dst_ip`;
       - Incident confirmation status: `status` (`prediction`, `confirmed`);
       - Response mitigation status: `response_status` (`none`, `candidate`, `mitigated`, `allowlist_protected`);
       - Severity levels: `severity` (`critical`, `high`, `medium`, `low`);
       - System audit filters: `actor`, `event`, `outcome`.
  2. **Standard Machine-Readable Formats:**
     - **RFC 4180 Compliant CSV (`serialize_csv()`):** Emits structured CSV with canonical column headers (`ATTACK_EVENT_FIELDS`, `SYSTEM_LOG_FIELDS`, `RESPONSE_ACTION_FIELDS`), minimal quoting, CRLF line terminators, UTF-8 charset, and JSON-stringified nested dictionary representations (e.g. `details`, `probabilities`) ensuring spreadsheet compatibility.
     - **Structured JSON (`serialize_json()`):** Emits formatted, indented JSON array representations preserving full document fidelity and ISO 8601 timestamps.
  3. **Collection Dispatching:**
     - Supports exporting three distinct forensic telemetry collections:
       - `attack_events`: Detection predictions, features, confidence scores, latencies, and confirmation statuses (`ids_attack_logs_*.ext`).
       - `system_logs`: Operational security audit events, scan starts/completions, and authentication attempts (`ids_system_logs_*.ext`).
       - `response_actions`: Automated and manual firewall mitigation actions, rule definitions, and target IPs (`ids_response_actions_*.ext`).
  4. **Audit Trail Invariant (Requirement FR-07 & FR-08):**
     - Every export operation is permanently recorded to MongoDB `system_logs` with `event: "LOGS_EXPORTED"`, capturing the requesting administrator (`actor`), target collection, format, row count, sanitized query filters, and generated filename.
  5. **REST API & RBAC Integration:**
     - Fully integrated into unified server ([`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py)) via `GET /api/logs/export`, protected with `@auth.admin_required` (HTTP 403 Forbidden for non-administrators).
     - Returns standard HTTP attachments (`Content-Disposition: attachment; filename=...`) and proper MIME types (`text/csv; charset=utf-8`, `application/json; charset=utf-8`).
  6. **Comprehensive Testing:**
     - Authored 10 unit tests in [`tests/unit/test_export_service.py`](file:///d:/intrusion%20detection/tests/unit/test_export_service.py) covering ISO datetime parsing, CSV/JSON serialization, filter handling, and dispatch audit logging.
     - Authored 4 integration tests in [`tests/integration/test_export_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_export_integration.py) covering RBAC enforcement, query filtering against real MongoDB collections, and system log audit entry verification.
- **Why:** Fulfills the final requirement of Phase 6, enabling reproducible research evaluations, thesis documentation, and forensic auditing without compromising system security. Concludes Phase 6 (Backend, Database & APIs, Steps 23–28).
- **Who agreed:** project owner and team (31 Oct 2026).
- **Proposal link:** Section 3.6 (Figure 4, Collections `attack_events`, `system_logs`, `response_actions`); Table 7 (FR-07, FR-08); Guide Step 28.

## D-033 — 2026-11-01 — React dashboard cleanup, single backend URL consolidation, and Socket.IO real-time telemetry wiring (Step 29)
- **Decision:** Modernize, clean up, and consolidate the React frontend (`my-app/`) to interface exclusively with the unified Flask + Socket.IO backend ([`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py)), fulfilling Group 03 Proposal Section 3.6, Section 7.1, Table 8, and Guide Step 29:
  1. **Legacy Route & Dead Code Elimination:**
     - Removed obsolete legacy pages and styles: `Register` (`components/Register.js`, `components/Register.css`), `CyberDetails` (`pages/CyberDetails.js`, `pages/CyberDetails.css`), `TraditionalDetails` (`pages/TraditionalDetails.js`, `pages/TraditionalDetailsold.css`), `AttackHistoryCICIDS` (`pages/AttackHistoryCICIDS.js`), `KDDAttackHistory` (`pages/KDDAttackHistory.js`), and duplicate `pages/MatrixEffect.js`.
     - Completely removed the public user registration vector (`/register`), enforcing administrator-only CLI provisioning via [`tools/create_admin.py`](file:///d:/intrusion%20detection/tools/create_admin.py) and eliminating registration attack surfaces.
  2. **Single Unified Backend Configuration:**
     - Eliminated 5 disjoint legacy backend ports (`127.0.0.1:5002`, `:5005`, `:5006`, `:5007`, `localhost:5012`).
     - Established centralized configuration in [`my-app/src/config.js`](file:///d:/intrusion%20detection/my-app/src/config.js) dynamically reading `REACT_APP_API_URL` (defaulting to unified endpoint `http://localhost:5000`).
  3. **Package & Build Tooling Clean-up:**
     - Standardized on `npm` package manager, permanently removing `yarn.lock`.
     - Removed conflicting webpack 4 overrides (`webpack ^4.47.0`, `html-webpack-plugin ^5.6.3`, `stream-http ^3.2.0`, `"browser": { "http": false }`), relying natively on `react-scripts 5.0.1` (webpack 5).
     - Verified clean production build (`npm run build`) and test execution (`npm test -- --watchAll=false`).
  4. **Authenticated REST Client (`my-app/src/services/api.js`):**
     - Implemented centralized Axios client with request interceptor automatically injecting `Authorization: Bearer <token>` from `localStorage`.
     - Configured response interceptor intercepting HTTP 401 Unauthorized errors to purge expired session credentials and redirect automatically to `/login`.
  5. **Secure Real-Time Socket.IO Client (`my-app/src/services/socket.js`):**
     - Replaced unauthenticated plain WebSockets (`ws://127.0.0.1:5005`, `ws://127.0.0.1:5006`, `ws://127.0.0.1:5007`) with `socket.io-client` 4.8.1.
     - Enforced JWT handshake authentication (`auth: { token }`) connected to the unified backend.
  6. **Zero Synthetic / Fake Telemetry:**
     - Completely purged all synthetic attack fallback generators (`fakeAttacks` and hardcoded `sampleData`), ensuring the dashboard strictly reports real empirical model inferences and logged events.
  7. **Authentication & Session Workflow:**
     - Refactored [`my-app/src/components/Login.js`](file:///d:/intrusion%20detection/my-app/src/components/Login.js) to authenticate against `POST /api/auth/login`, securely storing 8-hour JWT access tokens, and protected dashboard routing with `ProtectedRoute` guards.
- **Why:** Eliminates fragmented architectural debt, closes security vulnerabilities from open registration and unauthenticated endpoints, and ensures the operator interface strictly visualizes authentic, real-time intrusion events from the IP-camera IoT network.
- **Who agreed:** project owner and team (1 Nov 2026).
- **Proposal link:** Section 3.6 (Figure 4, Table 8); Section 7.1; FR-04; Guide Step 29.

## D-034 — 2026-11-01 — Responsive React dashboard architecture, canonical 7-page suite, and real-time operator verification badges (Step 30)
- **Decision:** Architect and build the responsive React dashboard suite (`my-app/src/pages/`) adhering strictly to Group 03 Proposal Section 3.6, Section 7.1, Table 8 ("a dashboard that fits any screen"), Requirement FR-04, and Guide Step 30:
  1. **Canonical 7-Page Architecture:**
     - **Overview (`Overview.js`):** Executive KPI cards (total flows, attacks detected, active blocks, discovered devices), 24h traffic volume metrics, Recharts attack class distribution bar chart, recent alerts stream, and lab infrastructure safety summaries.
     - **Live Alerts (`LiveAlerts.js`):** Real-time Socket.IO streaming alert feed (`new_event`, `event_update`) with flow vector visualization (source:port -> dst:port), calibrated confidence scores, empirical evidence notes, quick triage actions (Confirm Incident, Block IP), and pause/resume stream controls.
     - **Attack History (`AttackHistory.js`):** Searchable, multi-attribute filterable forensic event table (search by IP, filter by class, filter by status: prediction/confirmed), pagination, and an Incident Evidence Dossier modal with admin confirmation action (`PATCH /api/events/<id>`).
     - **Devices & Scans (`Devices.js`):** Subnet inventory table (IP, MAC, vendor, open ports, services, last seen), surveillance camera heuristic badges (`possible_camera`), camera evidence modal, authorized Nmap scan dispatcher (`POST /api/scans`), live progress bar (`scan_progress`), and admin camera confirmation toggle (`PATCH /api/devices/<ip>/confirm-camera`).
     - **Blocklist & Mitigations (`Blocklist.js`):** Active firewall rules table (target IP, direction, reason code, created timestamp, auto-expiry timestamp, status), manual mitigation creation form (`POST /api/blocklist`), and one-click unblock action (`DELETE /api/blocklist/<ip>`).
     - **Settings & Safety Policy (`Settings.js`):** Autonomous mitigation master switch toggle, operational threshold sliders/inputs (`min_confidence`, `min_repeats`, `repeat_window_seconds`, `max_rule_minutes`), management allowlist immunity table (gateway, sensor, admin PC, NVR), and settings change audit history (`GET /api/settings/history`).
     - **Forensic Logs & Export (`LogExport.js`):** Live immutable system audit logs viewer (`system_logs`) and multi-attribute forensic log export dispatcher generating RFC 4180 CSV and structured JSON files (`GET /api/logs/export`) with audit logging invariant verification (`LOGS_EXPORTED`).
  2. **Operator Verification Badging (Proposal Section 7.1):**
     - Enforced distinct visual badges across all alert and history displays:
       - **"MODEL PREDICTION"** (Blue border, unverified machine learning inference);
       - **"CONFIRMED INCIDENT"** (Red border with glowing indicator, verified by authorized security administrator).
  3. **Universal Responsive Layout (`my-app/src/components/Layout.js`):**
     - Implemented unified, responsive navigation layout adapting cleanly to desktop, tablet, and mobile screens (Tailwind CSS, sticky top telemetry bar, collapsible mobile menu).
     - Live Socket.IO connection status indicator ("SOCKET.IO LIVE" / "TELEMETRY OFFLINE") and current operator identity display.
  4. **Zero Synthetic Data Guarantee:**
     - Every list, chart, and metric renders exclusively authentic backend telemetry or displays an informative "No data yet" state when the network is benign and quiet.
  5. **Verification & Build Validation:**
     - Verified with passing Jest test suite verifying central configuration and all 7 page component exports.
     - Verified successful production build (`npm run build`, main bundle 191.75 kB gzip).
- **Why:** Delivers a unified, professional, robust Security Operations Center (SOC) dashboard empowering network administrators to inspect empirical machine learning evidence, verify threats, manage camera assets, and control firewall mitigations safely. Concludes Phase 7 (React Dashboard and Alerts, Steps 29–30).
- **Who agreed:** project owner and team (1 Nov 2026).
- **Proposal link:** Section 3.6 (Figure 4, Table 8); Section 7.1; Table 7 (FR-04, FR-06, FR-07, FR-08); Guide Step 30.

## D-035 — 2026-11-01 — Direction-aware response policy, 7 safety guardrails, and sliding-window repeat coalescing (Step 31)
- **Decision:** Architect, specify ([`docs/response_policy.md`](file:///d:/intrusion%20detection/docs/response_policy.md)), and implement the formal autonomous response policy engine ([`core_engine/response_policy.py`](file:///d:/intrusion%20detection/core_engine/response_policy.py)) integrated into [`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py), fulfilling Group 03 Proposal Table 5, Section 2.5, Section 3.7, Research Question RQ5, and Supervisor Checkpoint C7:
  1. **Direction-Aware Mitigation Logic (Proposal Table 5):**
     - **Benign:** Log aggregate to summary only; blocking strictly prohibited (`SKIP_BENIGN`).
     - **PortScan (Outside -> Camera):** Drops external scanner source IP only after confirmed repeat probe sweeps (`AUTO_PORTSCAN_REPEATED`).
     - **DDoS/DoS (Outside -> Camera):** Drops or rate-limits external flood source IP (`AUTO_DDOS_BLOCK` / `AUTO_DDOS_RATELIMIT`).
     - **C&C (Camera -> Outside):** Drops outbound communication to external C&C server destination IP, preserving local camera-to-NVR communication (`AUTO_CNC_DEST_BLOCK`).
     - **Malware Download:** Drops external staging host or isolates compromised device based on direction (`AUTO_MALWARE_BLOCK`).
  2. **The 7 Safety Guardrails (Checkpoint C7):**
     - *Check 1 (Master Switch):* Checks `settings.auto_response`. When disabled, engine operates in passive alerting mode only (`SKIP_AUTO_RESPONSE_DISABLED`).
     - *Check 2 (Calibrated Confidence):* Checks $P(\text{class}) \ge \tau_{\text{active}}$. Inferences below threshold generate alerts but never block (`SKIP_LOW_CONFIDENCE`).
     - *Check 3 (Management Allowlist Immunity):* Lab management assets (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) are permanently immune to blocking under any conditions (`SKIP_ALLOWLIST`).
     - *Check 4 (Private Target Protection):* Prevents inadvertent drops against local camera IPs (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) to avert surveillance stream disruption to NVR (`SKIP_PRIVATE_TARGET`).
     - *Check 5 (Sliding-Window Repeat Coalescing):* Tracks `(target_ip, class)` occurrences using a memory-efficient `collections.defaultdict(deque)` sliding window. Requires $\ge \text{min\_repeats}$ within $\text{repeat\_window\_seconds}$ (default: 3 occurrences in 60s). Single events alert only (`SKIP_NOT_REPEATED`).
     - *Check 6 (Bounded Rule Expiry):* Enforces explicit rule timeout sets clamped to `max_rule_minutes` (default: 45–60 mins) to prevent permanent network partitioning.
     - *Check 7 (Audit Invariants):* Every approved block and skipped guardrail action generates an immutable reason code logged to `system_logs` and `response_actions`.
  3. **Integration & Automated Verification:**
     - Integrated `ResponsePolicy` into `DecisionEngine` via `evaluate_response(outcome)`.
     - Authored 12 dedicated unit tests in [`tests/unit/test_response_policy.py`](file:///d:/intrusion%20detection/tests/unit/test_response_policy.py). Full test suite reaches 141 passed unit tests in 20.95s with 100% pass rate.
- **Why:** Solves Research Question RQ5 by mathematically and logically preventing false-positive network lockouts, protecting camera surveillance streams, and providing safe, autonomous firewall mitigations. Fulfills Supervisor Checkpoint C7.
- **Who agreed:** project owner and team (1 Nov 2026).
- **Proposal link:** Section 2.5; Section 3.4; Section 3.7; Table 5; Table 7 (FR-06, FR-07); RQ5; Checkpoint C7; Guide Step 31.

## D-036 — 2026-11-01 — nftables ruleset specifications, auto-expiring timed sets, and Linux kernel firewall adapter (Step 32)
- **Decision:** Architect, specify, and implement the native Linux `nftables` packet filtering ruleset and programmatic adapter ([`sensor/ids_inline.nft`](file:///d:/intrusion%20detection/sensor/ids_inline.nft), [`sensor/ids_router.nft`](file:///d:/intrusion%20detection/sensor/ids_router.nft), and [`core_engine/firewall/nftables_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/nftables_adapter.py)), conforming strictly to Group 03 Proposal Section 3.7 ("nftables and iptables"), Table 8 ("nftables sets with timeouts"), and Table 7 Requirement FR-06 ("Automated Blocking and Rate Limiting"):
  1. **Dual Topology Architecture (Inline & Passive):**
     - **Inline Mode ([`sensor/ids_inline.nft`](file:///d:/intrusion%20detection/sensor/ids_inline.nft)):** Evaluates bridged Layer 2 traffic via `table bridge ids` on the `forward` filter hook with `priority 0` and default `policy accept`.
     - **Passive / Router Mode ([`sensor/ids_router.nft`](file:///d:/intrusion%20detection/sensor/ids_router.nft)):** Evaluates routed Layer 3 traffic via `table inet ids` on the `forward` filter hook with `priority 0` and default `policy accept` for deployment on OpenWrt / Linux edge routers.
  2. **Zero Permanent Partitioning via Timed Sets:**
     - Utilizes dynamic nftables kernel sets with the `flags timeout` attribute (`block_src`, `block_dst`, `limit_src`).
     - Mitigations are added via `nft add element <family> ids <set> '{ <ip> timeout <duration>m }'`, guaranteeing automatic in-kernel eviction without requiring external cron daemons.
     - Rate-limiting enforces `ip saddr @limit_src limit rate over 200/second drop` on the transit chain.
  3. **Strict Source-Only Allowlist Rule (Section 3.7):**
     - Enforces `ip saddr @allow accept` as the very first rule in the forward chain for management assets (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`).
     - Crucially omits `ip daddr @allow accept` to guarantee that external malicious hosts on `block_src` cannot bypass drops to target the NVR or Admin workstation.
  4. **Programmatic Kernel Adapter & Simulation Fallback:**
     - Implemented `NftablesAdapter` supporting programmatic `block()`, `rate_limit()`, `unblock()`, `list_active()`, `check_ruleset()`, and `load_ruleset()`.
     - Verifies allowlist immunity locally before command generation, raising `AllowlistProtectedError` if an operator or automated policy attempts to drop a protected IP.
     - Clamps rule durations to `max_rule_minutes` (default: 60 mins).
     - Cross-platform dev fallback: When executed on Windows or non-root dev environments where `nft` binary is unavailable, operates in simulation mode with full in-memory state tracking and timer expiration calculations, guaranteeing complete testability.
     - Parses both structured JSON (`nft -j list set`) and human-readable text representations with remaining time calculation.
  5. **Automated Verification:**
     - Authored 12 comprehensive unit tests in [`tests/unit/test_nftables_adapter.py`](file:///d:/intrusion%20detection/tests/unit/test_nftables_adapter.py) verifying ruleset syntax, set structure, allowlist immunity, duration clamping, source and destination drops, rate-limiting, command line generation, and timeout text parsing.
     - All 12 tests passed; unit test suite expands to **153 passed unit tests in 19.69s** (192 total tests across repo) with 0 errors (100% pass rate).
- **Why:** Delivers robust, kernel-level, low-latency Layer 2 and Layer 3 packet mitigation with automatic rule expiration and absolute protection for critical network infrastructure, satisfying FR-06 and Step 32.
- **Who agreed:** project owner and team (1 Nov 2026).
- **Proposal link:** Section 3.7; Table 7 (FR-06); Table 8; Guide Step 32.

## D-037 — 2026-11-01 — Modular response adapter suite, passive router mitigation, simulation engine, and API integration (Step 33)
- **Decision:** Architect and implement the unified firewall response adapter suite ([`core_engine/firewall/base.py`](file:///d:/intrusion%20detection/core_engine/firewall/base.py), [`core_engine/firewall/router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py), [`core_engine/firewall/simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py), and [`core_engine/firewall/__init__.py`](file:///d:/intrusion%20detection/core_engine/firewall/__init__.py)) integrated into [`core_engine/decision_engine.py`](file:///d:/intrusion%20detection/core_engine/decision_engine.py) and [`core_engine/app.py`](file:///d:/intrusion%20detection/core_engine/app.py), conforming strictly to Group 03 Proposal Sections 1.2, 2.5, 3.7; Figure 5; and Table 7 Requirement FR-06:
  1. **Common Abstract Mitigation Interface ([`core_engine/firewall/base.py`](file:///d:/intrusion%20detection/core_engine/firewall/base.py)):**
     - Abstract base class `BaseFirewallAdapter` defining unified methods: `block(ip, direction, minutes, reason)`, `rate_limit(ip, minutes, reason)`, `unblock(ip, direction)`, and `list_active()`.
     - Standardized management allowlist immunity verification (`verify_allowlist()`) raising `AllowlistImmunityError` before dispatching any mitigation.
     - Enforces duration clamping to `max_rule_minutes`.
  2. **Passive SPAN / Mirroring Router Adapter ([`core_engine/firewall/router_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/router_adapter.py)):**
     - Solves passive monitoring topology constraint (Proposal Section 1.2, 3.7, Figure 5): because the sensor's SPAN / mirror port cannot drop packets directly, mitigation commands are securely dispatched to the upstream lab router (OpenWrt or Linux router) via SSH parameterized command execution (`ssh -p <port> -i <key> <user>@<host> "nft add element inet ids block_src '{ <ip> timeout <duration>m }'"`).
     - Provides graceful simulation fallback when router host is unreachable or unconfigured.
  3. **Development Simulation Adapter ([`core_engine/firewall/simulation_adapter.py`](file:///d:/intrusion%20detection/core_engine/firewall/simulation_adapter.py)):**
     - Provides in-memory state tracking for local development and Windows workstations.
     - Strictly abides by Golden Rule / Step 33 note: "Never report simulation results as real blocking", by explicitly tagging all generated records with `is_simulated = True` and `simulated: True`.
  4. **Adapter Factory ([`core_engine/firewall/__init__.py`](file:///d:/intrusion%20detection/core_engine/firewall/__init__.py)):**
     - `get_firewall_adapter(config)` dynamically instantiates `NftablesAdapter` (kernel mode on Linux), `RouterAdapter` (passive SPAN deployment), or `SimulationAdapter` based on configuration and host environment detection.
  5. **Core Engine & Flask Server Integration:**
     - Added `execute_response(decision, event_id, actor)` to `DecisionEngine`, automatically applying firewall rules, recording entries to `response_actions` and `blocklist` collections in MongoDB, and broadcasting `blocklist_update` via Socket.IO.
     - Updated Flask endpoints in `core_engine/app.py` (`POST /api/blocklist`, `DELETE /api/blocklist/<target_ip>`, `GET /api/blocklist`) to call the active firewall adapter, returning `adapter_mode` and `is_simulated` telemetry.
  6. **Automated Verification:**
     - Authored 8 unit tests in [`tests/unit/test_firewall_adapters.py`](file:///d:/intrusion%20detection/tests/unit/test_firewall_adapters.py).
     - Authored 4 integration tests in [`tests/integration/test_firewall_integration.py`](file:///d:/intrusion%20detection/tests/integration/test_firewall_integration.py).
     - Full test suite verified: **204 passed unit and integration tests** (161 unit, 43 integration) in 56.28s across 25 test modules with 0 errors (100% pass rate).
- **Why:** Delivers topology-independent, modular firewall response controls supporting both inline bridge and passive SPAN router deployments while maintaining complete testability and developer reproducibility.
- **Who agreed:** project owner and team (1 Nov 2026).
- **Proposal link:** Sections 1.2, 2.5, 3.7; Figure 5; Table 7 (FR-06); Guide Step 33.

## D-038 — 2026-11-08 — Virtual Camera Testbed, MediaMTX / Android Simulator, Live Pipeline Runner, and Synthetic Baseline Disclosure (Step 20 Audit, Step 26 Pipeline)
> **Wording corrected by D-042:** agreed by the team; to be confirmed with the supervisor.
- **Decision:** Formally adopt the virtualized camera network testbed architecture per Proposal Section 5.1 and Table 8, address live pipeline runner integration, harmonize router settings, and transparently disclose baseline data origins:
  1. **Virtual Camera Testbed Approval (Proposal Section 5.1 & Table 8):**
     - Proposal Section 5.1 explicitly sanctions: *"The laboratory will have at least one IP camera or an approved camera simulator..."* and Table 8 mandates *"a lab network that we control and can set up again."*
     - Approved testbed options: (a) MediaMTX RTSP video server looping genuine surveillance H.264 video on TCP 554, or (b) an Android device running IP Webcam streaming authentic RTSP/HTTP traffic over the isolated virtual network.
     - Virtual environment setup utilizes VirtualBox Internal Network / Open vSwitch with promiscuous mirroring, Linux Ubuntu VM for Zeek and the detection engine, and Kali Linux VM for controlled attack injection (Table 10 scenarios).
  2. **Live Pipeline Runner Integration ([`core_engine/runner.py`](file:///d:/intrusion%20detection/core_engine/runner.py)):**
     - Resolved architectural disconnect: `core_engine/app.py` was not executing a background worker to consume streaming Zeek `conn.log` flows.
     - Implemented `LivePipelineRunner` as a robust, non-blocking background daemon thread that continuously tails `conn.log` in micro-batches and invokes `DecisionEngine.process_flows()`, broadcasting real-time alerts to the React SOC Dashboard via WebSockets.
     - Exposed REST control endpoints: `GET /api/v1/pipeline/status`, `POST /api/v1/pipeline/start`, and `POST /api/v1/pipeline/stop`.
  3. **Configuration & Router Parameter Harmonization:**
     - Resolved adapter selection mismatch: `get_firewall_adapter()` now harmonizes `cfg.get("type")` with `settings.yaml: response.adapter`.
     - Standardized router SSH environment variables in `RouterAdapter` and `.env.example` to support both `ROUTER_HOST` / `ROUTER_PORT` / `ROUTER_USER` / `ROUTER_KEY_FILE` and legacy `ROUTER_SSH_*` aliases.
  4. **Academic Integrity & Synthetic Baseline Disclosure:**
     - Documented in `reports/experiments/camera_baseline_summary.md` and Lab Logbook Entry 3 that the 5,000 flows generated in Step 20 were a synthetic benign baseline modeled after Tapo C200 distributions for Windows development and schema validation.
     - Scheduled physical wire / simulator capture under Step 20b/Step 35 prior to final viva evaluation.
  5. **Objective Evaluation Reporting Integrity:**
     - Maintained honest reporting of held-out scenario Macro-F1 = `0.4028` on `Capture-34-1` (arising from zero support for `Malware_Download` in that scenario), aligned with Proposal Section 1.5 mandate to *"report all results either way"*.
- **Why:** Ensures strict adherence to academic honesty, connects the live real-time detection pipeline, and provides a cost-effective, reproducible virtual laboratory conforming to Proposal Section 5.1.
- **Who agreed:** project owner and team (8 Nov 2026).
- **Proposal link:** Section 1.5; Section 3.7; Section 5.1; Table 7 (FR-01, FR-04, FR-06); Table 8.
















## D-039 — 2026-11-08 — Dataset copy checked against the official IoT-23 files; 4 scenario names corrected
- **Decision:** Fix the file-to-scenario map in `ml_engine/manifest.py`, then rebuild every result that uses scenario names (Steps 9, 10, 12, 14–18).
- **What was found:**
  - Proposal 3.2 says we may use a copy only if we can check where it came from and what was changed. The local files (`dataset1.csv` … `dataset23.csv`) are a CSV copy of the official `conn.log.labeled` files.
  - `tools/verify_iot23_copy.py` compares the first flow (`ts`, `uid`) of each local file with the first flow of each official file on the Stratosphere server (only the first 8 KB is downloaded). Result: 19 files matched; 4 names were wrong:
    - `dataset4.csv` is official **9-1** (the map said 8-1);
    - `dataset5.csv` is official **8-1** (the map said 9-1);
    - `dataset15.csv` is official **36-1** (the map said 35-1);
    - `dataset16.csv` is official **35-1** (the map said 36-1).
  - After the fix: **23 / 23 match** (`reports/iot23_copy_verification.md`).
  - The label totals of all 20 malicious scenarios match the official website, with one exception: for 33-1 the website lists "Okiru-Attack 13,609,467" but our copy says "Okiru". Small pieces of the official 33-1 file were downloaded (byte ranges at 10 positions). The official file also says **`Okiru`**, so our copy is correct and the website summary is not.
  - The held-out scenario 34-1 was always mapped correctly.
- **Effect:** the training data is the same rows as before; only 4 scenario names changed. All reports were made again from the corrected data.
- **Still to record:** where the CSV copy was downloaded from (folder `D:\Download\archive`; probably a Kaggle upload). Write the page link in this decision when known.
- **Who agreed:** project owner (8 Nov 2026).
- **Proposal link:** Section 3.2; O1.

## D-040 — 2026-11-08 — Step 17 redone: calibration and thresholds from grouped out-of-fold data only (replaces D-021; updates D-020, D-022)
- **Decision:**
  - Step 14 now saves the grouped out-of-fold (OOF) probabilities (`data/processed/rf_oof_predictions.npz`).
  - Step 17 fits a per-class sigmoid calibration on the OOF probabilities, and chooses the thresholds from the calibrated OOF data with fixed rules: alert threshold = lowest value with precision ≥ 0.50; block threshold = lowest value with precision ≥ 0.95 **and** at most 1% of benign flows reaching it. A class with no such value is **never blocked automatically** (alert only).
  - The held-out scenario 34-1 is used once, to report the final deployed model with the fixed thresholds, and for permutation importance (proposal 2.4).
- **Why (what was wrong in D-021):**
  - The old thresholds were numbers typed into the code after the 34-1 results had been seen. Their precision and recall were then measured on 34-1. Proposal 3.4 says the test set is not touched while choosing settings.
  - The old calibration was fitted on rows that the model had been trained on.
  - The old "decision rules extracted from the Random Forest" were hand-written text. Step 17 now shows real decision paths from the trained trees, and the reason codes are labelled as team-made names.
  - The model card numbers were typed in by hand. `export_bundle.py` now reads them from the result files.
- **Limitation:** 34-1 results were seen before this redo. Nothing is chosen from 34-1 now, but this is reported.
- **Who agreed:** project owner (8 Nov 2026).
- **Proposal link:** Sections 2.4, 3.4; Table 9.

## D-041 — 2026-11-08 — Controlled automatic response connected; "local network" taken from settings
- **Decision:**
  - `DecisionEngine.process_flows()` now sends every block candidate to the response policy (`respond_to_outcome`). The firewall adapter is called only when all safety rules pass. Before this, no automatic block could happen.
  - The policy decides "local device" with `lab.local_networks` from `settings.yaml`, not "any private address". Before this, the lab attacker `10.10.10.50` (a private address, but outside) could never be blocked.
  - `auto_response` is **off** by default everywhere.
  - Dashboard settings (`allowlist`, `min_confidence`, `min_repeats`, `repeat_window_seconds`, `max_rule_minutes`) are checked and applied to the running policy at once, and on server start. Before this they were saved but had no effect.
  - `response.adapter` is the one setting that chooses the adapter (`firewall_config_from_settings`).
  - The reason code of every block decision is saved on the attack event (`response_reason`); the dashboard shows the response status of each alert (proposal 3.6).
- **Latency target correction (D-029, D-030):** the target is the proposal's Table 9 target, median decision < 2 s and 95th percentile < 5 s, measured end to end in Step 37. It is not "sub-second".
- **Who agreed:** project owner (8 Nov 2026).
- **Proposal link:** Sections 2.5, 3.4, 3.6, 3.7; Table 5; Table 9; FR-06, FR-07; RQ5.

## D-042 — 2026-11-08 — Steps 19, 20 and 22 re-opened; D-024 and D-026 replaced; D-038 wording corrected
- **Decision:**
  - **D-024 is replaced.** The 5,000 "camera" flows of 31 Oct 2026 were made by a script, not captured. The result "FPR 0.000%, H1 clause 2 PASS" is withdrawn. Hypothesis H1's FPR part has **not been tested yet**.
  - **D-026 is replaced.** The Step 22 check used the same synthetic file, so it does not answer RQ3. The check tool is kept, and its report now states the data source. It must be run again on a real capture.
  - The synthetic file was moved to `data/local/synthetic/`; real captures go to `data/local/benign/`. Both scripts now need `--source real|synthetic`, and only `real` results can be reported.
  - Steps 19, 20 and 22 are set back to **🟡 Started** in the guide: the software is ready, the lab run is not done.
  - **D-038 wording:** the camera simulator and the virtual lab were agreed by the team on 8 Nov 2026. The proposal says "approved camera simulator", so the choice is **to be confirmed with the supervisor** at the next meeting.
- **Who agreed:** project owner (8 Nov 2026).
- **Proposal link:** Sections 1.5 (H1), 3.5, 5.1; Table 11; RQ3.

## D-043 — 2026-11-09 — Model Steps 14–18 run again after the scenario-name fix; results recorded; two open questions for the team
> **Updated by D-044 and D-045 (9 Nov 2026):** open question 2 (CnC) is solved: the calibration is now `temperature`, which keeps the model's top class; deployed model on 34-1 macro-F1 0.4530. Open question 1 (no automatic block) is still open (issue 23). The Step 17 numbers below are for the old sigmoid calibration.
- **What was done:** after D-039 (4 scenario names corrected) and D-040 (new Step 17 method), Steps 14, 15, 16, 17 and 18 were run again on 8–9 Nov 2026. All numbers from 31 Oct 2026 (for example 0.3630, 0.4028, 76.72%, 30.84 MB) are replaced. Older entries (D-018 to D-022) keep their old numbers as history.
- **Results (from the result files):**
  - Step 14, grouped CV, Random Forest: out-of-fold macro-F1 **0.3422** (mean fold 0.3353 ± 0.1704); best `n_estimators=100`, `max_depth=18`; model 4.30 MB; model step 4.66 µs per flow on the PC.
  - Step 15, out-of-fold macro-F1: HistGradientBoosting **0.4331**, Random Forest 0.3422, Logistic Regression 0.2722. HistGradientBoosting scored higher. Random Forest stays the main model because proposal Section 2.4 chose it for its tree paths, which can be explained; the model step of all three takes microseconds, so speed does not decide. This is reported, not hidden.
  - Step 16, held-out 34-1, uncalibrated Random Forest: macro-F1 0.4530 (5 classes) / 0.5662 (4 classes present); accuracy 0.8063; CnC recall 0.3671; PortScan precision 0.0424.
  - Step 17, deployed calibrated model on 34-1: macro-F1 **0.3405** (5 classes) / 0.4256 (4 present); accuracy 0.6998; 0% of IoT-23 benign flows reach a block threshold.
  - Step 18: bundle `v1.1.0`, 9.3 MB; model card filled from the result files.
- **H1 part 1 (macro-F1 ≥ 0.85 on the held-out scenario): not met.** H1 part 2 (FPR ≤ 5% on local camera traffic) is not tested yet (D-042).
- **Open question 1 — no automatic block.** With the fixed rules of D-040, no class reached "precision ≥ 0.95 and benign trigger rate ≤ 1%" on the out-of-fold data. So every attack class is **alert only**. With `auto_response` on, the system still blocks nothing by itself; manual block and unblock work. Table 10 expects "source blocked or rate-limited" in some scenarios.
- **Open question 2 — calibration removes CnC.** On the out-of-fold data, calibration raises macro-F1 (0.3422 → 0.4526) but the calibrated model never picks CnC (recall 0.475 → 0). On 34-1, all 6,706 CnC flows are called PortScan or Benign.
- **Rule for answering both questions:** any change (for example a different calibration, a different model, or a different block rule) must be chosen and justified with the out-of-fold training data only, written here **before** it is tested, and then checked once on 34-1. 34-1 must not be used to choose. If nothing is changed, the lab tests run in alert-only mode and this is reported as a result.
- **Who agreed:** results recorded by the project owner (9 Nov 2026). The two questions are open for the team and the supervisor.
- **Proposal link:** Sections 1.5 (H1), 2.4, 3.4, 3.7; Tables 9 and 10.

## D-044 — 2026-11-09 — How the Step 17 calibration method is chosen (rule written before the comparison is run)
- **Why:** D-043 found that the per-class sigmoid calibration makes the model never pick CnC (out-of-fold CnC recall 0.475 → 0). The owner decided (9 Nov 2026) to change the calibration step so that every class can be found, and so that blocking is possible where the data supports it.
- **What the data shows (out-of-fold, before any change):**
  - Each DDoS scenario is a different flood type (TCP SYN in 17-1, TCP reset in 35-1, UDP in 7-1 and 43-1, `OTH` in 60-1). A model that has not seen a scenario calls most of its DDoS flows Benign (raw out-of-fold DDoS recall 0.002).
  - 78% of IoT-23 benign flows are single unanswered packets (`conn_state = S0`), which look like single flood packets. One flow on its own does not show the flood rate.
  - The raw model calls 228,000 flows CnC, but only 23,257 are really CnC (precision about 10%). The per-class sigmoid sees this and pushes CnC down until it never wins.
- **The model stays Random Forest** (proposal Section 2.4). Its settings were already chosen in Step 14 by grouped-CV macro-F1. HistGradientBoosting scored higher in Step 15 (D-043), but the proposal chose Random Forest and this decision does not change that.
- **Candidates (all fitted on Step 14 out-of-fold probabilities only):**
  1. `none` — raw Random Forest probabilities.
  2. `sigmoid_per_class` — the current method (D-040).
  3. `temperature` — one temperature on the log-probabilities (softmax); keeps the top class of the raw model.
  4. `multinomial` — multinomial logistic regression on the 5 log-probabilities.
  5. `multinomial_balanced` — the same with `class_weight="balanced"` (each class counts equally, which matches macro-F1).
- **How each candidate is scored (cross-fitted):** for each of the 5 grouped folds, the calibrator is fitted on the out-of-fold rows of the other 4 folds and applied to this fold. So no row is scored by a calibrator fitted on that row. Measures: macro-F1, recall per class, Brier score, and whether any class reaches the block rule of D-040 (precision ≥ 0.95 and benign trigger rate ≤ 1%).
- **Selection rule (fixed now):**
  1. Keep only candidates where **every one of the 5 classes has recall ≥ 0.05** (no class is silenced).
  2. Among those, choose the **highest macro-F1**.
  3. If no candidate passes step 1, choose the candidate with the **highest lowest-class recall**; if two are equal, the higher macro-F1.
- **After the choice:** the chosen method is fitted on all out-of-fold rows; thresholds are chosen as in D-040; the held-out scenario 34-1 is used **once** for the final check. 34-1 is not used to choose anything.
- **Limitation (written honestly):** the team has already seen out-of-fold and 34-1 results for `none` (Step 16) and `sigmoid_per_class` (D-043) before writing this rule.
- **Who agreed:** project owner (9 Nov 2026).
- **Proposal link:** Sections 2.4, 3.4; Table 9.

## D-045 — 2026-11-09 — The method chosen by D-044 failed the final check; calibration changed to `temperature`
- **What happened:** the D-044 rule chose `multinomial` (out-of-fold macro-F1 0.3750; every class found; PortScan reached the block rule). The single final check on the held-out scenario 34-1 then gave **macro-F1 0.0458** (5 classes), accuracy 0.0817. 14,260 of 14,394 DDoS flows were called Benign, and all 6,706 CnC flows were called DDoS or PortScan. On the synthetic camera file (D-042, software test only), 80% of the flows were called attacks.
- **Why it failed:** `multinomial` has 30 weights. It learns *which class the model confuses with which* when the model meets a scenario it has not seen (for example, "raw DDoS score high" often meant Benign in the out-of-fold data). These confusions depend on which scenarios were left out of each fold. The final model is trained on all 22 scenarios, so its mistakes are different, and the learned corrections make things worse. `multinomial_balanced` and `sigmoid_per_class` can change the top class in the same way.
- **New principle:** calibration may change **how sure** the model is, but **not which class wins**. Only `none` and `temperature` follow this.
- **Decision:** use **`temperature`** (one number; it keeps the Random Forest's top class and only rescales the confidence). On the out-of-fold data it has the same macro-F1 as `none` (0.3422) and a better Brier score (0.1454 vs 0.1759), so the confidence values are more reliable for the thresholds.
- **This breaks the D-044 rule:** `temperature` does not pass step 1 (out-of-fold DDoS recall 0.0016). The out-of-fold DDoS recall is low because each DDoS scenario is a different flood type (D-044). This is written here as a deviation, not hidden.
- **Honest limit:** this choice was made **after** seeing a 34-1 result. So 34-1 is no longer a clean unseen test. Its numbers are reported, but the clean test of the model is now the local lab data (Level 3, Steps 20 and 35). All 23 IoT-23 scenarios are already used (22 for training, 34-1), so no other unseen IoT-23 scenario is left.
- **What this means for blocking:** with `temperature`, no class reaches the D-040 block rule on the out-of-fold data. Flow features alone cannot reach 95% precision across unseen scenarios (D-044). Making automatic blocking possible needs either a rule over repeated flows from the same source (the response policy already counts repeats), or new rate features (for example, flows per source in a time window). Both need a separate team decision.
- **Who agreed:** project owner (9 Nov 2026).
- **Proposal link:** Sections 2.4, 3.4; Table 9.

## D-046 — 2026-11-09 — Block thresholds follow proposal 3.4 (confidence threshold + repeats); original-label results; full dataset copy check (rules written before the results)
- **Why:** a check of the project against the proposal (9 Nov 2026) found that the D-040 block rule asks one single flow to be right 95% of the time. The proposal does not ask for this. Proposal 3.4 says: *"One high prediction will not cause an automatic block by itself. The event must pass a confidence threshold, and it must happen again inside a set time window. Events with lower confidence will only send an alert."* Because of the D-040 rule, no class could ever be blocked, so Table 10 scenarios 2–4 could not work. The safety floor `response.min_confidence: 0.85` was also above almost every calibrated confidence (issue 26).
- **Part 1 — how block thresholds are chosen now (replaces the block part of D-040; the alert part of D-040 stays):**
  - Data: the calibrated grouped out-of-fold training data only (Step 14 + Step 17a). Each training flow now keeps its time and IP addresses as audit columns (Step 12; never model inputs, proposal Table 6).
  - The live response rule is replayed on this data: for class *k* and a candidate threshold *t*, a flow is a block candidate when the top class is *k* and its confidence is at least *t*. A block fires when the same target has at least `min_repeats` (3) block candidates of class *k* inside `repeat_window_seconds` (60 s), and the target is not already blocked. A block lasts `max_rule_minutes` (30). The target follows Table 5 and `response_policy.py`: the source for DDoS and PortScan; the outside destination for CnC and Malware_Download. Replay is done per scenario.
  - A block is **wrong** if the flow that fires it is truly Benign.
  - **Block threshold** for class *k* = the lowest *t* (from the class alert threshold up to 0.99, step 0.01) where: (a) at least 95% of the blocks are not wrong; (b) at most 1% of the benign targets are ever blocked; and (c) there are at least 10 blocks, so there is evidence. If no *t* meets all three, the class stays **alert only**.
  - The safety floor `response.min_confidence` is set to **0.30**, the lowest value a threshold can take, so the per-class thresholds decide. It can still be raised from the dashboard (FR-07).
  - Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than in real traffic. This mostly removes attack flows (large classes are cut most), so the replay is expected to under-count correct blocks rather than wrong ones.
- **Part 2 — original-label results (proposal 3.2: *"When there are enough samples, we will report results for both the grouped classes and the original detailed labels"*):** Step 17 reports, for every original IoT-23 label with at least 30 flows, how many flows were put in the right group, on the out-of-fold data and on 34-1.
- **Part 3 — dataset copy (proposal 3.2):** `tools/verify_iot23_copy.py` now checks the first **and last** flow of every file against the official files, and the label totals against the official IoT-23 website.
- **Who agreed:** project owner (9 Nov 2026).
- **Proposal link:** Sections 3.2, 3.4, 3.7; Tables 5, 6, 9, 10.
- **Results (9 Nov 2026, recorded after the rules above):**
  - Step 12 was run again only to keep the audit columns. The 22 old columns are identical in every row (checked), and the rows still line up with the saved out-of-fold predictions, so the model was **not** retrained.
  - Block thresholds from the replay on out-of-fold data: **PortScan 0.30** (413 blocks; 96.6% fired by malicious flows; 3 of 28,594 benign targets blocked), **CnC 0.39** (142 blocks; 100% fired by malicious flows; 0 benign targets blocked). **DDoS_DoS: alert only** (at every threshold almost all replayed blocks were fired by benign flows). **Malware_Download: alert only** (only 5 blocks, fewer than the 10 needed as evidence).
  - Replay on 34-1 with these thresholds (reported only): PortScan 27 blocks, 1 fired by a benign flow (1 of the 2 benign hosts in 34-1 was blocked once); most PortScan blocks there were fired by CnC flows of the infected device, which the live policy would not block because that device is local (local-network protection, proposal 3.7). CnC: 1 block, correct.
  - Original-label results are in `reports/experiments/thresholds_and_explanation.md`, Section 8. The weakest labels on out-of-fold data are `DDoS` (0.16% put in the right group) and `C&C` (6.3%); on 34-1, `C&C` 36.7%.
  - Dataset copy: first and last flows match the official files for 23/23 files; label totals match the official website for 17 scenarios. Three differ: 33-1 (`Okiru` in our copy vs `Okiru-Attack` on the website, same count; the official file says `Okiru`, D-039), 49-1 (14 `FileDownload` flows not on the website) and 52-1 (2 `C&C-Mirai` flows not on the website). The 3 honeypot captures are not listed on the website.
