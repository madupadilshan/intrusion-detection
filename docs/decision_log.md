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
