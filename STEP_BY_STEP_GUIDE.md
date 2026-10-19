# Step-by-Step Guide: Building the Project From the Very Beginning

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Based on:** Group 03 Research Proposal (July 2026)
**Guide version:** 2. This version was checked line by line against the proposal.

---

## How to Read This Guide

- **Read Part A first.** It explains the project in plain words, the key terms, what you need, and the rules. Do not skip it, even if you want to start coding.
- **Part B** explains what is already in the project folder and what is wrong with it.
- **Part C** is the work itself: **43 steps in order**, from Step 0 to Step 42.
- **Part D** is the final checklist. **Part E** lists common mistakes.

Each step in Part C has the same parts:

| Part | Meaning |
|---|---|
| **Why** | Why we do this step, in plain words. |
| **What you need** | Tools, files or earlier steps that must be ready. |
| **How to do it** | The actions, in order, with commands and code where helpful. |
| **Output** | The files or results the step must produce. |
| **Done when** | A simple check. **Do not move on until it passes.** |
| **Proposal** | Where the proposal asks for this step. |

**Two labels are used in this guide:**

- Everything **without a label** is written in the proposal. You must do it.
- **➕ Extra** marks a small helpful addition that is **not written in the proposal**. It does not change or replace anything in the proposal. You may skip it, but we recommend it.

**If this guide and the proposal ever disagree, the proposal wins.**

---

# Part A: Start Here

## A1. The project in plain words

IP cameras sit on the network all day. Attackers can scan them, flood them, take control of them, or use them to download malware. Most small camera networks have **nothing watching the traffic** and **no automatic way to react**. This is the "security gap" in proposal Figure 1.

We will build a system that:

1. **Watches** the camera network traffic (it does not look at the video, only at *who talks to whom, how much and how*).
2. **Turns** the traffic into connection records called *flows*, using a tool called **Zeek**.
3. **Classifies** each flow with a **Random Forest** machine-learning model into one of 5 classes: Benign, DDoS/DoS, Port scan, C&C, Malware/download.
4. **Saves** the evidence in **MongoDB**.
5. **Shows** live alerts on a **React** dashboard.
6. **Responds safely**: it blocks or rate-limits a bad IP address with **nftables** (or through the router), but **only** when strict safety rules are met. The admin can always undo it.
7. **Finds devices** on the lab network with **Nmap**.

The model learns from a public dataset called **IoT-23**. A big part of the research is to check **whether a model trained on IoT-23 still works on real camera traffic** (the IoT-23 normal traffic does not come from cameras).

## A2. Key words explained

| Word | Simple meaning |
|---|---|
| **IoT** | "Internet of Things": small network devices like cameras, smart lamps or door locks. |
| **NVR** | Network Video Recorder. It records the camera video. |
| **Packet** | One small piece of network data. |
| **Flow (connection)** | All packets of one conversation between two devices, for example one TCP connection. One flow = one row of data. |
| **Zeek** | A free tool that watches traffic and writes one line per flow into a file called **`conn.log`**. |
| **`conn.log` fields** | `duration` (how long), `orig_bytes`/`resp_bytes` (bytes each side sent), `orig_pkts`/`resp_pkts` (packets each side), `proto` (tcp/udp/icmp), `service` (http, dns…), `conn_state` (how the connection ended, e.g. `SF` normal, `S0` no answer), `history` (a short code of what happened, e.g. `ShADadFf`). |
| **IoT-23** | A public dataset of labelled IoT flows: 23 captures ("scenarios"), 20 with malware and 3 normal. |
| **Scenario** | One capture in IoT-23, for example `CTU-IoT-Malware-Capture-34-1`. |
| **Label** | The correct answer for a flow (e.g. "PartOfAHorizontalPortScan"). |
| **Class** | Our 5 groups of labels (Benign, DDoS/DoS, Port scan, C&C, Malware/download). |
| **Feature** | One input column the model uses (e.g. `duration`). |
| **Random Forest** | A model made of many decision trees that vote together. |
| **Training / testing** | The model learns from training data. We check it on testing data it has never seen. |
| **Leakage** | When test data is too similar to training data (e.g. flows from the same capture in both). The score then looks better than it really is. |
| **Grouped cross-validation** | We split the data into parts **by scenario**, so flows from one scenario are never in both training and testing. |
| **Held-out scenario** | A scenario we keep away completely and test on only at the very end. |
| **Macro-F1** | A score from 0 to 1 that treats every class equally. It is fairer than accuracy when some classes are tiny. |
| **Recall** | Of all real attacks of a class, how many did we catch. |
| **False-positive rate (FPR)** | Of all normal flows, how many did we wrongly call an attack. |
| **Confusion matrix** | A table showing which classes are mixed up with which. |
| **Calibration** | Checking whether "90% confidence" really means right about 90% of the time. |
| **Port scan (horizontal)** | One attacker tries the same port on many devices to find weak ones. |
| **DDoS / DoS** | Flooding a device with traffic so it stops working. |
| **C&C (Command and Control)** | A taken-over device talking to the attacker's server to get orders. |
| **SPAN / port mirroring** | The switch sends a **copy** of traffic to our sensor. The sensor can watch but **cannot block**. This is **passive mode**. |
| **Inline mode** | The sensor sits **in the path** of the traffic, so it can block directly. |
| **Sensor** | The Linux computer that runs Zeek, the model, the backend and the response adapter. |
| **nftables** | The Linux firewall. We use it to block or rate-limit IP addresses. |
| **Allowlist** | IP addresses that must **never** be blocked (admin PC, NVR, gateway, sensor). |
| **Flask / Flask-SocketIO** | Python tools to build the backend API and send live updates to the dashboard. |
| **MongoDB** | The database where we save devices, events, actions, users and logs. |
| **React** | The tool used to build the web dashboard. |
| **Nmap** | A tool to find devices and open ports on a network. |
| **JWT token** | A "pass" the backend gives after login. The dashboard sends it with every request. |

## A3. One example from start to end

This is how the finished system handles an **authorised port scan** in the lab:

1. The attack test computer scans port 23 on every device in the camera subnet.
2. The switch copies the traffic to the sensor (passive mode), or the traffic passes through the sensor (inline mode).
3. Zeek writes one line in `conn.log` for each scan attempt (state `S0`: no answer).
4. The **Zeek adapter** reads the new lines straight away.
5. The **feature code** turns each line into the same feature columns used in training.
6. The **Random Forest** says: "Port scan, confidence 0.97".
7. The **decision engine** saves an event in MongoDB and sends an alert to the dashboard. The alert shows: time, direction, source, destination, class, confidence, a short evidence note and the response status. It is marked **"model prediction"** until an admin confirms it.
8. The decision engine checks the **safety rules**: Is the scanner on the allowlist? No. Is confidence above the threshold? Yes. Has it happened again inside the time window? Yes.
9. Only then does the **response adapter** block the scanner's IP, **with an expiry time**. It writes a reason code and an audit record.
10. The dashboard shows the block. The admin can press **Unblock** at any time.

This is proposal Figure 2 (architecture) and Figure 3 (detection and response cycle).

## A4. What you need

### A4.1 Hardware (proposal Section 5.1)

| Item | Why | Notes |
|---|---|---|
| At least **one IP camera** *or* an approved **camera simulator** | The device we protect | A simulator can be a PC or Raspberry Pi that streams a test video. |
| **NVR** or a recording service | Records the video, like a real setup | Can be recording software on a PC. |
| **Managed switch with port mirroring** | Sends a copy of traffic to the sensor (passive mode) | "Port mirroring" or "SPAN" must be in its features. |
| **Linux sensor computer** | Runs Zeek, the model, the backend and the response adapter | Needs **two network ports** (a USB Ethernet adapter is fine). |
| **Attack test computer** | Makes the controlled test traffic | Linux. Used **only** inside the lab. |
| **Admin workstation** | Opens the dashboard | Any PC with a browser. Your Windows PC can be this. |
| **Lab router you control** | Connects the lab parts. Applies blocks in passive mode | A router you can log into by SSH or API (OpenWrt is a good choice). |
| Network cables | — | — |

### A4.2 Software (proposal Table 8)

| Area | Tool | Where it runs |
|---|---|---|
| Dataset | IoT-23 v1.0.0 | Download to the development PC |
| Machine learning | Python, pandas, scikit-learn | Development PC (training) and sensor (prediction) |
| Network analytics | Zeek; TShark/Scapy only for checking | Sensor |
| Backend | Flask, Flask-SocketIO | Sensor |
| Frontend | React and chart components | Built on the development PC; opened in the admin browser |
| Database | MongoDB | Sensor |
| Response | nftables; adapter for router/firewall API | Sensor (inline) or router (passive) |
| Discovery | Nmap | Sensor |

**Your Windows PC already has:** Python 3.10, scikit-learn 1.6, pandas 2.2, Node.js 22 and MongoDB 8. **Nmap is not installed yet.** Zeek and nftables **do not run on Windows**, so the sensor must be a Linux computer.

### A4.3 Skills the team will use

You do not need to be an expert at the start. You will learn these during the steps:

- Basic Linux terminal commands (`cd`, `ls`, `sudo apt install`, editing files).
- Python with pandas and scikit-learn.
- Basic networking (IP address, subnet, router, switch, TCP/UDP).
- Basic React and REST APIs.
- Git (save versions of your work).

### A4.4 Permissions

- Written approval from the supervisor before any scan or attack test.
- University ethics or technical clearance, **if university policy asks for it**.

## A5. The golden rules (never break these)

All of these come straight from the proposal.

1. **Use the official IoT-23 v1.0.0 labelled flows.** Do not train on an unofficial copy that someone already processed, unless you can check where it came from and what was changed (3.2).
2. **Write the label mapping before training.** Never change it after seeing test results (2.3).
3. **Never split data by random rows.** Keep each scenario together. Keep at least one scenario (or one local capture) out for final testing (2.2, 3.4).
4. **Do not touch the test data** while choosing preprocessing steps or model settings (3.4).
5. **Never use UID, raw IP addresses or the capture file name as model inputs.** Use them only for grouping and audit (Table 6).
6. **Offline and live must use exactly the same preprocessing.** Save it together with the model (3.3 step 7).
7. **Accuracy is not the main result.** Use macro-F1, recall per class, false-positive rate and confusion matrices (3.4).
8. **One high prediction never blocks by itself.** A block needs: allowlist check, private-network check, minimum confidence, repeated events, maximum rule time, reason code and audit record (3.4, 3.7).
9. **Only the separated lab network.** No other person's camera, no public IP, no vendor cloud, no university production network (3.8).
10. **No live malware.** Only controlled scans, rate-limited flooding or replay, and simulations of C&C-like or file-transfer behaviour (5.1).
11. **No video or audio is kept.** Only the network metadata we need (3.8).
12. **Passive mode is the default.** Inline mode needs a bypass and recovery plan (Table 11).
13. **Report all results, even bad ones** (6, 7.1).

## A6. Timeline (32 weeks, from proposal Figure 6)

Week numbers are approximate. Fit the real dates to the academic calendar, but **keep the order of tasks that depend on each other**.

| Phase (Figure 6 task) | Steps | Weeks (about) |
|---|---|---|
| Problem refinement & ethics | Steps 0 – 4 | W1 – W3 |
| Literature review | Step 0 (keeps running) | W1 – W8 |
| Lab and network design | Steps 5 – 6 | W3 – W8 |
| Dataset audit & label mapping | Steps 7 – 9 | W5 – W10 |
| Preprocessing & feature pipeline | Steps 10 – 12 | W7 – W13 |
| Model training & validation | Steps 13 – 18 | W10 – W17 |
| Live Zeek integration | Steps 19 – 22 | W13 – W20 |
| Backend, database & APIs | Steps 23 – 28 | W15 – W23 |
| React dashboard & alerts | Steps 29 – 30 | W18 – W25 |
| Firewall response controls | Steps 31 – 34 | W21 – W27 |
| Controlled security testing | Steps 35 – 39 | W25 – W30 |
| Evaluation & analysis | Step 40 | W28 – W32 |
| Documentation & final demo | Steps 41 – 42 | W29 – W32 |

- Check progress as a team **every week**.
- Meet the supervisors **at least once every two weeks** (proposal Section 4).

---

# Part B: What Is Already in the Project Folder

Before starting, understand what you already have. This decides what to keep, fix or put away.

## B1. Current files and their problems

| File / folder | What is wrong | What we do |
|---|---|---|
| `iot23_attacks/iot23/X_train.csv`, `X_test.csv`, `y_*.csv` | An **already-processed copy**. Some numbers are already scaled (e.g. `orig_pkts = 3.03e-08`). There is **no scenario ID**, so grouped validation is impossible. It was split **randomly by rows** (`train_test_split` in `iot0331.ipynb`). Golden rule 1 and 3 say no. | Do not train on it. Start from the official IoT-23 files (Step 7). Move it to `archive/`. |
| Label numbers 0–12 | The two versions of `iot23_attacks.py` give **different names to the same number** (e.g. label 10). The code's label list has no port-scan name, so we cannot tell which number is port scan. | Make a new written label mapping (Step 8). |
| `iot23_attacks/random_forest_model.pkl` (820 MB) | Trained on the old scaled data with unclear labels. Too large. | Retire it. Train a new model (Phase 4). |
| `iot23_attacks.py` | Uses Scapy **per packet** with **fixed fake values** (`duration=0`, `conn_state=6`, `history=22`, `service=0`). `simulate_attack()` **makes up** a "DDoS" from request counts with invented features. The root copy imports `DatabaseManager`, which does not exist in `db_manager.py`, so it cannot start. | Replace with the Zeek adapter (Step 21) and the real detector (Step 26). |
| `network_scan.py` | Adds **random numbers** to the vulnerability count (fake data). Calls a device a "camera" from port 554 alone (proposal 3.7 says no). | Reuse the Nmap parts in the new scanner (Step 27) without these problems. |
| `my-app/app.py` | Users are in **SQLite**, not MongoDB. JWT secret and admin password are **written in the code**. Open register page. | Users in MongoDB; secrets in `.env` (Step 24). |
| `my-app/src/pages/IOTDetails.js` | Uses a plain `WebSocket` to talk to a **Socket.IO** server. They cannot connect to each other. | Use `socket.io-client`, which is already installed (Step 29). |
| Front end in general | Calls 5 different ports (5002, 5005, 5006, 5007, 5012). | One backend address (Step 29). |
| `KDD/`, `CICID2017/`, `CyberDetails.js`, `TraditionalDetails.js`, `AttackHistoryCICIDS.js`, `KDDAttackHistory.js` | The proposal does **not** train on KDD or CICIDS2017 (CICIDS2017 is only a reference in Section 2.3; KDD is not in the proposal). | Move to `archive/`; remove from the dashboard. |
| Premiere Pro files, `python-installer.exe`, `.zip` files, screenshots, presentation | Not part of the system. | Move out of the project folder. |
| No Git | The proposal needs "code with versions" (O1). | Set up Git (Step 2). |

## B2. Where `PROJECT_EXPLANATION_EN.md` does not match the proposal

`PROJECT_EXPLANATION_EN.md` is a useful start, but these parts go against the proposal. **This guide replaces it.**

| `PROJECT_EXPLANATION_EN.md` says | The proposal says | This guide |
|---|---|---|
| Train on the existing `X_train.csv` / `X_test.csv`. | Official IoT-23 v1.0.0; no unofficial processed copy (3.2). | Steps 7–12 |
| A normal train/test split. | Grouped CV + leave-one-scenario-out + local camera test (3.4). | Steps 13–16 |
| Random Forest only. | Also compare a linear model and one gradient-boosting model (1.3, 2.4). | Step 15 |
| No calibration or permutation importance. | Required before using confidence for automatic response (2.4, 3.4). | Step 17 |
| A fixed list of 10 features. | Table 6 also lists port categories, an incomplete-flow flag and optional time-window rates; keep only features the live pipeline can make the same way. | Steps 11, 22 |
| No offline vs live feature check. | Required (3.5). | Step 22 |
| No local camera traffic. | Collect our own benign camera flows (Table 11, H1). | Step 20 |
| Block with `iptables -A INPUT`. | nftables first; iptables/ipset or router API as adapters (3.7). Also, an `INPUT` rule only protects the sensor itself, **not the cameras**. | Steps 32–33 |
| No rule expiry and no direction logic. | Maximum rule time; outside scanner blocked by source; C&C by destination or device isolation (3.7). | Steps 31–34 |
| 5 collections, no `users`. | MongoDB also keeps users (3.6). | Step 23 |
| No log export. | FR-08. | Step 28 |
| 5 test scenarios. | 6 scenarios in Table 10. | Step 35 |
| Firewall = FR-07, allowlist = FR-08, FR-05 = Telegram/email. | FR-05 = Nmap discovery, FR-06 = blocking rules, FR-07 = allowlists/thresholds/audit, FR-08 = log export. No Telegram or email in the proposal. | Step 6 |
| No ethics step, no data retention. | Required (3.8). | Steps 1, 23, 42 |
| "Confidence > 0.85 and 3 flows in 10 s" as fixed rules. | The proposal asks for a minimum confidence and repeated events inside a set time window, but gives no numbers. | Start values only; final values chosen from validation data (Step 17). |

---

# Part C: The Steps

---

# Phase 0: Start-Up, Ethics and Project Setup (W1 – W3)

## Step 0. Understand the project and start the literature review

**Why:** Everyone must understand the goal, the questions and the limits before building anything.

**What you need:** The proposal PDF and this guide.

**How to do it:**
1. Every team member reads the whole proposal once, slowly.
2. Read Part A of this guide again. Make sure everyone can explain A3 (the example) in their own words.
3. Write the aim, objectives (O1–O6), hypothesis (H1) and research questions (RQ1–RQ5) on one page. Put it at the top of the shared folder.
4. Keep reading the papers in the reference list (Antonakakis 2017, Garcia 2020, Vitorino 2022, Yang 2022, Gyamfi & Jurcut 2022, Biondi 2022, NISTIR 8259A, Zeek conn.log docs). Keep short notes in `docs/literature_notes.md`. You will need them for the final report.

**Output:** `docs/project_summary.md`, `docs/literature_notes.md`.

**Done when:** Each member can explain what the system does and what H1 means.

**Proposal:** Sections 1, 2; Figure 6 (literature review W1–W8).

---

## Step 1. Get approvals and write the ethics plan

**Why:** Scanning and attack tests are only allowed on a network we own and have permission for.

**What you need:** The supervisor.

**How to do it:**
1. Write a one-page **lab permission note**: which devices we own, the lab IP ranges, who may use attack tools, credentials and firewall rights.
2. Ask the supervisor if university ethics or technical clearance is needed. If yes, apply now. Experiments wait until it is approved.
3. Write a **data retention plan**: what metadata we keep, who can open it, how long we keep it, and when we delete it. Agree the time periods with the supervisor.
4. Start a **lab logbook** (`docs/lab_logbook.md`). Every scan, attack test and firewall change gets one line: date, person, what, why.

**Output:** `docs/ethics/lab_permission.md`, `docs/ethics/data_retention_plan.md`, `docs/lab_logbook.md`, clearance letter (if needed).

**Done when:** The supervisor has approved the plan in writing.

**Proposal:** Section 3.8, Section 1.2 (limits).

---

## Step 2. Clean the project folder and set up Git

**Why:** A clean folder with saved versions makes the work repeatable (O1).

**What you need:** Git installed (from git-scm.com).

**How to do it:**
1. **Make a full backup** of the current folder (copy it to another drive).
2. Create this folder layout:

```
intrusion detection/
├── README.md
├── STEP_BY_STEP_GUIDE.md
├── requirements.txt
├── .env.example               <- names of secret settings, no real values
├── .gitignore
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
│   ├── features.py            <- feature steps, SHARED by training and live
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
└── archive/                   <- old code we no longer use (not in Git)
```

3. Move old things to `archive/`: `KDD/`, `CICID2017/`, the old `iot23_attacks/` folder, `db_manager.py`, the root `iot23_attacks.py`, `network_scan.py` (we copy useful parts later), and old CSV/PKL files.
4. Move non-project files (Premiere Pro files, `python-installer.exe`, presentations, screenshots, `.zip` files) out of the project folder.
5. In the project folder, run:

```bash
git init
```

6. Create `.gitignore`:

```
data/
archive/
*.pkl
*.joblib
*.pcap
*.log
.env
config/settings.yaml
node_modules/
__pycache__/
.venv/
```

7. Save the first version:

```bash
git add .
git commit -m "Clean project structure"
```

8. ➕ Extra: Put the repository on a **private** GitHub repo so the team can share it.

**Output:** A clean Git repository.

**Done when:** `git status` says "nothing to commit" and no data, model or secret file is tracked.

**Proposal:** Objective O1 ("code with versions"); Section 3.6 (secrets not in version control).

---

## Step 3. Install the software

**Why:** Every tool in proposal Table 8 must work before we use it.

**What you need:** The development PC (your Windows PC) and the Linux sensor computer.

**How to do it:**

**3a. Development PC (Windows)**
1. Install **Nmap** from nmap.org (it also installs Npcap).
2. Create a Python virtual environment in the project folder:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Create `requirements.txt`. **Write exact version numbers** (e.g. `scikit-learn==1.6.0`) so everyone has the same versions. Use the versions you install and test:

```txt
pandas
numpy
pyarrow
scikit-learn
joblib
pyyaml
matplotlib
flask
flask-socketio
flask-cors
flask-jwt-extended
bcrypt
pymongo
python-dotenv
python-nmap
psutil
scapy
pytest
```

4. Install: `pip install -r requirements.txt`. Then run `pip freeze` and copy the exact versions into `requirements.txt`.

**3b. Linux sensor (Ubuntu LTS)**
1. Install Ubuntu LTS.
2. Install Python, nftables, Nmap and tcpdump:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nftables nmap tcpdump ethtool git
```

3. Install **Zeek** from the official Zeek binary packages. Follow the install page in the Zeek documentation for your Ubuntu version. It installs Zeek in `/opt/zeek`. Then add it to your path:

```bash
echo 'export PATH=/opt/zeek/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
zeek --version
```

4. Install **MongoDB Community Server** following the official MongoDB install page for Ubuntu.
5. Copy the project (with Git) to the sensor, create the same virtual environment, and install the **same** `requirements.txt`. The model is trained on the PC and used on the sensor, so the **scikit-learn version must be the same** on both.

**3c. Attack test computer (Linux)**

```bash
sudo apt install -y nmap hping3 tcpdump python3
```

**3d. Version record**
Write a small script `tools/check_env.py` that imports every library and prints its version. Save the output as `reports/environment_versions.txt` (one for the PC, one for the sensor).

**Output:** Pinned `requirements.txt`, `reports/environment_versions.txt`.

**Done when:** `zeek --version`, `nft --version`, `nmap --version` and `mongod --version` work on the sensor, and `tools/check_env.py` runs with no errors on the PC and the sensor.

**Proposal:** Table 8, Section 5.1.

---

## Step 4. Write the settings file and the decision log

**Why:** All important settings and decisions must be in one place so anyone can repeat the work (fixed seed and configuration file).

**How to do it:**
1. Create `config/settings.example.yaml`. Copy it to `config/settings.yaml` for real use (this copy is not in Git). The IP addresses below are examples; use your lab plan from Step 5:

```yaml
lab:
  approved_scan_subnets: ["192.168.50.0/24"]  # Nmap may scan ONLY these
  local_networks: ["192.168.50.0/24"]         # used to decide traffic direction

allowlist:            # management IPs that are NEVER blocked
  - 192.168.50.1      # router / gateway
  - 192.168.50.5      # IDS sensor
  - 192.168.50.10     # admin workstation
  - 192.168.50.20     # NVR

response:
  deployment_mode: passive      # passive is the default (Table 11)
  adapter: router               # router (passive) | nftables (inline) | simulation
  auto_response: false          # ➕ Extra: master switch; turn on only in approved tests
  min_confidence: 0.85          # START value; final value chosen in Step 17
  min_repeats: 3                # START value; final value chosen in Step 17
  repeat_window_seconds: 60     # START value; final value chosen in Step 17
  max_rule_minutes: 30          # every rule expires (maximum rule time)
  allow_device_isolation: false # isolating a local device only if the policy allows

model:
  bundle_path: ml_engine/models/ids_bundle_v1.joblib
  random_seed: 42

retention_days:   # fill in from the agreed retention plan (Step 1)
  attack_events: null
  traffic_summaries: null
  system_logs: null
```

2. Create `.env.example` with **names only**, no real values:

```
MONGO_URI=
JWT_SECRET_KEY=
ROUTER_SSH_HOST=
ROUTER_SSH_USER=
```

3. Create `docs/decision_log.md`. Every important choice is written here with the date, the choice and the reason. For example: label mapping, sampling caps, chosen features, held-out scenarios, final thresholds, dropped features.

**Output:** `config/settings.example.yaml`, `.env.example`, `docs/decision_log.md`.

**Done when:** The team has agreed the allowlist and the starting values.

**Proposal:** Sections 3.4 (fixed seed, configuration file), 3.6 (secrets), 3.7 (allowlists, thresholds, maximum rule time).

---

# Phase 1: Lab and Network Design (W3 – W8)

## Step 5. Build the lab network

**Why:** All tests must happen on a separated network we control and can set up again.

**What you need:** The hardware from A4.1.

**Important idea first:** a device can only block traffic that **passes through it**. If the attacker and the camera are on the same switch, their traffic never reaches the router or the sensor's bridge, so nothing can block it. That is why the attack computer goes on a **separate "outside" subnet** behind the lab router. This lets us test outside attacks **without using any public IP address**.

**How to do it:**

1. **Plan the IP addresses** (example):

| Network | Device | Example IP |
|---|---|---|
| Camera LAN `192.168.50.0/24` | Lab router (LAN side) | 192.168.50.1 |
| | Sensor (management) | 192.168.50.5 |
| | Admin workstation | 192.168.50.10 |
| | NVR | 192.168.50.20 |
| | IP camera | 192.168.50.30 |
| | Camera simulator (if used) | 192.168.50.31 |
| "Outside" lab network `10.10.10.0/24` | Lab router (outside side) | 10.10.10.1 |
| | Attack test computer (also the lab "C&C test server" in Step 35) | 10.10.10.50 |

2. **Set up the lab router** to route between the two subnets **without NAT**, and allow forwarding, so the attack computer can reach the cameras like an outside attacker. The lab must **not** connect to the university or public network. (If the camera needs the internet for its first setup, do that first, then disconnect.)
3. **Passive mode (the default)** — proposal Figure 5 left side:
   - Connect the camera, NVR, admin PC and router to the managed switch.
   - Connect the sensor's **second** network port to a free switch port. This is the **mirror port**. Give it no IP address.
   - In the switch settings, mirror traffic to that port. If your switch allows it, mirror **ingress (incoming) traffic of all used ports**. Each packet enters the switch once, so the sensor sees each packet once (no duplicates).
   - Turn off NIC offloading on the mirror port so Zeek sees real packets:

```bash
sudo ip link set <mirror_port> up
sudo ethtool -K <mirror_port> gro off lro off
```

   - In this mode the sensor **cannot block**. Blocking is done by the **router** (Step 33).
4. **Inline mode** — proposal Figure 5 right side:
   - Put the sensor **between the camera switch and the router** as a **transparent bridge** (both network ports joined in a bridge `br0`). Traffic between the cameras and the router now passes through the sensor, so nftables on the sensor can block it.
   - Note: in inline mode the sensor only sees traffic **that crosses it**. Camera-to-NVR traffic on the same switch does not cross it. Use passive mode to measure normal camera traffic.
5. **Bypass plan for inline mode:** if the sensor fails, connect the switch cable straight to the router. Write this in `docs/lab_network.md` and test it once.
6. Draw the lab diagram with all IP addresses.

**Output:** Working lab, `docs/lab_network.md` (diagram, IP table, mirror settings, bypass plan).

**Done when:**
- The camera streams video to the NVR.
- On the sensor, `sudo tcpdump -i <mirror_port> -c 20` shows camera traffic.
- The attack computer can reach the camera through the router.
- No lab device can reach the university or public network.

**Proposal:** Sections 1.2, 3.8, 5.1; Figure 5; Table 11 (inline risk).

---

## Step 6. Threat model and requirement checklist

**Why:** Be clear about what we defend against and what "finished" means.

**How to do it:**
1. Write a short **threat model**:
   - What we protect: camera, NVR, video privacy, admin access, the rest of the network.
   - Who attacks: an outside scanner, a flooder, a botnet controlling a camera (C&C), a malware download.
   - Paths: inbound scans and floods; outbound C&C or downloads from a taken-over device.
2. Copy the functional requirements into `docs/requirements_checklist.md`:

| ID | Requirement | Priority / how we check |
|---|---|---|
| FR-01 | Capture mirrored or inline traffic and make connection flows from it. | Must / schema test |
| FR-02 | Put each usable flow into a class; give back the class, the confidence and the model version. | Must / model API test |
| FR-03 | Save benign traffic summaries, attacks and response actions. | Must / database test |
| FR-04 | Send new events and alerts to the dashboard (which needs a login) without the user pressing refresh. | Must / Socket.IO latency test |
| FR-05 | Find approved devices and services with controlled Nmap scans. | Should / inventory test |
| FR-06 | Add, list, expire and remove blocking rules on the firewall or router. | Must / test on a separated network |
| FR-07 | Keep the allowlists, the confidence thresholds and a full audit history. | Must / safety test |
| FR-08 | Export filtered attack logs for testing and reporting. | Should / export test |

3. Add O1–O6 and RQ1–RQ5 to the same file. Tick them as you finish.

**Output:** `docs/threat_model.md`, `docs/requirements_checklist.md`.

**Done when:** The supervisor has seen both.

**Proposal:** Sections 1.5, 3.1 (requirements and threat modelling); Tables 3 and 7.

---

# Phase 2: Dataset Audit and Label Mapping (W5 – W10)

## Step 7. Download IoT-23 and make a manifest

**Why:** We must use the official data and be able to prove exactly which files we used.

**What you need:** About 10 GB+ of free disk space for the compressed file and more for the extracted files.

**How to do it:**
1. Download **IoT-23 version 1.0.0** from the official source: Zenodo (DOI `10.5281/zenodo.4743746`) or the Stratosphere Laboratory IoT-23 page. Take the **smaller release that has only the labelled flows** (`conn.log.labeled` files). The full release with packet captures is much bigger and not needed for training.
2. Extract it into `data/raw/iot23/`. On Windows you can use 7-Zip, or `tar -xzf <file>.tar.gz` in PowerShell. Each scenario has its own folder with a `conn.log.labeled` file.
3. **Never change these files.**
4. Write `ml_engine/manifest.py`. For every `conn.log.labeled` file it records the scenario ID, file name, **SHA-256 hash**, number of rows, and the count of each `label` and `detailed-label`. Example for the hash:

```python
import hashlib

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()
```

5. Save it as `reports/dataset_manifest.csv` and commit it to Git.

**Note:** IoT-23 has **20 malicious and 3 benign scenarios**. The benign ones come from a smart lamp, a voice assistant and a smart door lock. **None are IP cameras.** This is why Step 20 is required.

**Output:** `data/raw/iot23/`, `reports/dataset_manifest.csv`.

**Done when:** All 23 scenarios are listed with hashes, row counts and label counts.

**Proposal:** Sections 2.3, 3.2; Objective O1.

---

## Step 8. Write and freeze the label mapping

**Why:** If we choose the mapping after seeing results, we could (even by accident) make the results look better. So we fix it first.

**What you need:** The manifest from Step 7 and the official IoT-23 label descriptions.

**How to do it:**
1. From the manifest, make a table of **every detailed label × every scenario** with counts.
2. Read the official description of each label.
3. Start from proposal Table 5:

| Our class | IoT-23 labels in this group (Table 5) |
|---|---|
| Benign | Benign |
| DDoS / DoS | DDoS, and "attack" labels **that we checked are flooding** |
| Port scan | PartOfAHorizontalPortScan |
| C&C | C&C, C&C-HeartBeat, C&C-Torii |
| Malware / download | Okiru, Mirai, FileDownload, and **mixed labels we checked** |

4. Some IoT-23 labels are **mixed** and need a team decision. Check each one against the official descriptions and the counts:

| Mixed or unclear label | Possible class | Decide by |
|---|---|---|
| C&C-FileDownload, C&C-HeartBeat-FileDownload | Malware / download or C&C | Main behaviour in the description |
| C&C-Mirai | C&C or Malware / download (Table 5 lists "Mirai" under malware) | Main behaviour in the description |
| C&C-PartOfAHorizontalPortScan | C&C or Port scan | Main behaviour in the description |
| Attack, Okiru-Attack, C&C-HeartBeat-Attack, PartOfAHorizontalPortScan-Attack | DDoS / DoS **only if** you checked they are flooding | Description + flow patterns |
| Malicious with no detailed label | — | Count them; suggest exclude |

5. Rules for these decisions (proposal 2.3 and 3.2):
   - A mixed label with **very few examples** goes under its **main behaviour**, or is reported on its own when there is enough data.
   - If a label is **too general or not clear**, do **not** force it into a class. Exclude it and write down how many rows were excluded.
6. Write the final mapping in `config/label_mapping.yaml`, for example:

```yaml
Benign: Benign
DDoS: DDoS_DoS
PartOfAHorizontalPortScan: PortScan
C&C: CnC
C&C-HeartBeat: CnC
C&C-Torii: CnC
Okiru: Malware_Download
FileDownload: Malware_Download
# ... every other label, each one decided and explained in docs/decision_log.md
# labels set to EXCLUDE are removed and counted
```

7. Write the reasons in `docs/decision_log.md`. Show the supervisor. Commit to Git. **From now on, the mapping does not change.**

**Output:** `config/label_mapping.yaml` (frozen), decision log entry.

**Done when:** The mapping is committed and the supervisor has seen it.

**Proposal:** Table 5; Sections 2.3, 3.2.

---

## Step 9. Data-quality report

**Why:** Find problems in the data before modelling.

**How to do it:** Write `ml_engine/data_quality.py`. It produces `reports/data_quality/report.md` with:
1. Rows per scenario and per class (after the mapping).
2. A **class × scenario table**. This is very important: a class that appears in **only one scenario** cannot be tested on an unseen scenario. Write this down as a known limit.
3. Missing values per column (IoT-23 uses `-` for missing).
4. Data types and value ranges (min, max, median) for duration, bytes and packets.
5. Category counts for `proto`, `service`, `conn_state`, `history`.
6. Duplicate rows.
7. Very large scenarios (some have many millions of rows) and the sampling plan (Step 12).

**Output:** `reports/data_quality/report.md` with charts.

**Done when:** The team has reviewed it, and it is clear from the class × scenario table which scenario(s) can be held out (Step 13).

**Proposal:** Objective O1 (data-quality report); Section 3.2.

---

# Phase 3: Preprocessing and Feature Pipeline (W7 – W13)

## Step 10. Load and clean the data

**Why:** Turn the raw files into a clean table that **keeps the scenario ID**.

**How to do it:** Write `ml_engine/load_iot23.py`, following proposal Section 3.3 steps 1–4:

1. Read each `conn.log.labeled` file. Lines that start with `#` are headers.
   - **Watch out:** in IoT-23 files the last three columns (`tunnel_parents`, `label`, `detailed-label`) are often separated by **spaces**, not tabs. No field contains a space, so reading with "any whitespace" as the separator handles both:

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

   Check the `#fields` line in your files matches `COLS`. Count any bad lines.
2. Add a `scenario_id` column to every row.
3. Change `-` and `(empty)` into missing values.
4. Convert `duration`, byte, packet and port columns to numbers. Convert `ts` to a time.
5. Apply `config/label_mapping.yaml` to make a `class` column. Remove `EXCLUDE` rows and **count them**.
6. Keep `uid`, `id.orig_h`, `id.resp_h` and `scenario_id` in the table **only for grouping and audit**. They are removed before the model sees the data (golden rule 5).
7. Save as Parquet files in `data/interim/` (much faster than CSV).

**Output:** `data/interim/*.parquet`, and a log of rows read and dropped per file.

**Done when:** Row counts match the manifest (minus the excluded rows you counted).

**Proposal:** Section 3.3 steps 1–4.

---

## Step 11. Write the shared feature code

**Why:** Live traffic must be turned into features **exactly** the same way as the training data. The easiest way is **one function used by both**.

**How to do it:**
1. Write `ml_engine/features.py` with one main function `make_features(df)`. `train.py` and the live `detector.py` both import it.
2. Use the candidate features from proposal Table 6:

| Group | Features | What we do |
|---|---|---|
| Transport | `proto`, source port category, destination port category | Encode the categories. **Group the ports** (e.g. well-known 0–1023, registered 1024–49151, dynamic 49152–65535) so the model does not memorise port numbers. For ICMP, Zeek puts the ICMP type/code in the port fields, so use a separate `icmp` category. |
| Service / state | `service`, `conn_state`, `history` | A clear `unknown` category; join rare categories together. |
| Time | `duration`; rate over a time window **only if we use it** | Check the numbers. Use a log transform if values are very skewed (this mainly matters for the linear comparison model; trees do not need it). |
| Volume | Bytes and packet counts from each side (`orig_bytes`, `resp_bytes`, `orig_pkts`, `resp_pkts`; optionally `orig_ip_bytes`, `resp_ip_bytes`) and ratios such as bytes per packet | Check the numbers; **stop divide-by-zero** in ratios. |
| Quality | `missed_bytes`, a flag for a flow that is not complete | Keep **only if the live pipeline always makes it** (checked in Step 22). |
| Left out | UID, raw IP addresses, capture file name (and `ts`) | Used only for grouping and audit. **Never model inputs.** |

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

4. **Do not scale numbers** for Random Forest. Scaling is only added inside the comparison models that need it (Step 15).
5. If you decide to use a **time-window rate** feature (e.g. "flows from this source in the last 10 seconds"), it must be computed the **same way** on IoT-23 (sorted by time inside each scenario) and live. If you are not sure you can do that, leave it out.
6. Write unit tests in `tests/unit/test_features.py`: missing values, zero packets, unknown categories, ICMP.

**Output:** `ml_engine/features.py`, tests, the feature list in `docs/decision_log.md`.

**Done when:** Tests pass, and the function works on an IoT-23 row **and** on a Zeek JSON row.

**Proposal:** Table 6; Section 3.3 steps 2–5; Section 3.5.

---

## Step 12. Sampling and class balance

**Why:** Some scenarios are huge and some classes are tiny. We must handle this fairly, without changing the test data in a way that makes results look better.

**How to do it:**
1. **Cap very large scenarios** so the data fits in memory: for each (scenario, class), keep at most N rows, chosen at random with the fixed seed. Use the manifest counts to compute the fraction to keep, then sample each chunk with that fraction. Write N in the decision log.
2. For the **held-out test scenario(s)**, sample (if needed for memory) **without balancing**, so the real class proportions stay the same.
3. Inside the **training data only**:
   - Use **class weights** (`class_weight="balanced"`) — first choice.
   - If needed, **under-sample** very large classes.
   - Use synthetic oversampling (e.g. SMOTE) **only after grouping and only inside the training folds**. Never before the split.
4. Save the feature tables in `data/processed/`: one for the training scenarios, one for the held-out scenario(s).

**Output:** `data/processed/` tables; sampling notes in the decision log.

**Done when:** You can say exactly how many rows of each class from each scenario are in training and in the held-out set.

**Proposal:** Section 3.3 step 6; Table 11 (class imbalance).

---

# Phase 4: Model Training and Validation (W10 – W17)

## Step 13. Plan the three test levels

**Why:** To test honestly with no leakage, the plan must be fixed **before** training.

**How to do it:** Write in the decision log:

1. **Level 1 — Grouped cross-validation:** flows from the same scenario always stay together. Use `StratifiedGroupKFold` with `groups = scenario_id`.
2. **Level 2 — Held-out scenario(s):** keep at least one malicious scenario out completely. Choose it from the class × scenario table (Step 9) so that **every class still has training data**. It is opened **only at the end** (Step 16).
3. **Level 3 — Local lab traffic:** our own benign camera traffic (Step 20) and the controlled test traffic (Phase 9).

**Output:** Written split plan with the held-out scenario IDs.

**Done when:** The plan is committed, and the held-out data is in its own folder that nobody uses for tuning.

**Proposal:** Sections 2.2, 3.4; Objective O2.

---

## Step 14. Train the Random Forest

**Why:** This is the main model of the prototype.

**What you need:** Steps 11–13 done.

**How to do it:** Write `ml_engine/train.py`.
1. Build **one scikit-learn `Pipeline`** with the categorical encoder and the model. The encoder must handle categories it has not seen before (proposal 3.3 step 5):

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

2. Tune the settings the proposal lists (number of trees, max depth, min samples in a split / leaf, max features, class weights) with a **random search inside grouped cross-validation**, scored by **macro-F1**:

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

   (If some classes appear in too few scenarios for 5 folds, use fewer folds and write why.)
3. Save every setting tried and its score to `reports/experiments/rf_search.csv`.
4. Record the model file size and the prediction time per flow.

**Output:** Best RF pipeline, search results.

**Done when:** Grouped-CV macro-F1 and recall per class are recorded for the best settings.

**Proposal:** Sections 2.4, 3.4.

---

## Step 15. Compare with other models

**Why:** We must **check**, not assume, that Random Forest gives a good balance of accuracy and speed.

**How to do it:** Write `ml_engine/compare_models.py`. Use the **same features, the same grouped folds and the same held-out scenario** for all models:
1. **Linear classifier:** `LogisticRegression(class_weight="balanced", max_iter=1000)` with one-hot encoding and scaling (scaling only here).
2. **One gradient-boosting model:** `HistGradientBoostingClassifier` (built into scikit-learn) or LightGBM. Choose one and write it in the decision log.
3. Compare macro-F1, recall per class, benign FPR, training time, **prediction time per flow** and model size in one table.
4. Random Forest stays the **main model in the prototype** because it is easier to look inside its decisions. Report the comparison honestly, even if another model scores higher.

**Output:** `reports/experiments/model_comparison.md`.

**Done when:** The table is complete for all three models.

**Proposal:** Sections 1.3, 2.4.

---

## Step 16. Evaluate on the held-out scenario

**Why:** This is the real test of the model on unseen data.

**How to do it:** Write `ml_engine/evaluate.py`. For Level 1 (grouped CV) and Level 2 (held-out scenario), report:
1. Macro, micro and weighted precision, recall and F1.
2. **Recall for each class.**
3. **Confusion matrix** for the grouped classes, and for the original detailed labels when there are enough samples.
4. **Benign false-positive rate** = benign flows predicted as any attack ÷ all benign flows.
5. PR-AUC per class where it helps.
6. Accuracy (reported, but **not** the main result).
7. The **generalisation gap**: the score difference between Level 1 and Level 2.

Then check **H1** (macro-F1 ≥ 0.85 on the held-out scenarios). If it is lower, write the likely reason: domain shift, feature mismatch or too few examples. **Do not change the label mapping or the test set to fix it.**

**Output:** `reports/experiments/evaluation_iot23.md` with figures.

**Done when:** All metrics are saved and H1 (first half) is answered.

**Proposal:** Section 3.4; Table 9; H1; RQ1, RQ2.

---

## Step 17. Calibration, explanation and final thresholds

**Why:** Confidence values will start automatic responses, so we must check they can be trusted.

**How to do it:** Write `ml_engine/calibrate.py`, using **validation folds, not the held-out test set**:
1. Draw a **reliability curve** for each class (one class vs the rest) with `sklearn.calibration.calibration_curve`, and compute the **Brier score** with `sklearn.metrics.brier_score_loss`.
2. If the probabilities are poorly calibrated, you may use `CalibratedClassifierCV` with separate scenario groups, then check again.
3. Compute **permutation importance on held-out data** (`sklearn.inspection.permutation_importance`). The built-in feature importance can give too much weight to features with many values.
4. Save a few example **decision paths** to help explain predictions. Do **not** treat one importance value as proof of what caused an attack.
5. **Choose the final values** of `min_confidence`, `min_repeats` and `repeat_window_seconds`. Pick values that keep wrong blocks on benign traffic low. Write them in `config/settings.example.yaml` and in the decision log with the reason.

**Output:** `reports/experiments/calibration.md`, permutation-importance chart, final threshold values.

**Done when:** The thresholds are chosen with a written reason.

**Proposal:** Sections 2.4, 3.4.

---

## Step 18. Save the model bundle and model card

**Why:** One file holds everything the live system needs, so offline and live use exactly the same steps.

**How to do it:**
1. Train the final pipeline on all training scenarios with the best settings, and save:

```python
import joblib, sklearn

bundle = {
    "pipeline": final_pipeline,          # encoder + model, fitted together
    "feature_columns": FEATURE_COLUMNS,  # exact order
    "classes": list(final_pipeline.classes_),
    "model_version": "rf-v1.0",
    "trained_on": "IoT-23 v1.0.0, scenarios: ...",
    "label_mapping_sha256": "...",
    "sklearn_version": sklearn.__version__,
}
joblib.dump(bundle, "ml_engine/models/ids_bundle_v1.joblib", compress=3)
```

2. Write `reports/model_card.md`: the data used, features, scores, chosen thresholds, and **known limits** (e.g. the benign training data is not from cameras).

**Output:** `ml_engine/models/ids_bundle_v1.joblib`, `reports/model_card.md`.

**Done when:** A fresh Python session loads the bundle and gives the same prediction for a test row as during training.

**Proposal:** Section 3.3 step 7; FR-02 (model version); Section 1.6 (written list of limits).

---

# Phase 5: Live Zeek Integration (W13 – W20)

## Step 19. Run Zeek on the sensor

**Why:** Zeek makes the live connection records (flows) from the traffic.

**How to do it:**
1. Create `sensor/local.zeek`:

```zeek
@load policy/tuning/json-logs.zeek   # one JSON record per line, easy for Python
```

2. Run Zeek on the mirror port (passive) or on `br0` (inline), from a fixed log folder:

```bash
sudo mkdir -p /var/log/ids-zeek && cd /var/log/ids-zeek
sudo zeek -C -i <interface> /path/to/project/sensor/local.zeek
```

   `-C` tells Zeek to ignore checksum errors, which are common on mirrored traffic.
3. **How Zeek writes flows:** Zeek keeps open connections in memory and writes a line to `conn.log` **when the connection ends or times out**. So a long video stream appears late, and a scan attempt with no answer appears after a short timeout.
   - Start with Zeek's **default timeouts**.
   - If you change any timeout later, write it in the decision log and re-run Step 22, because timeouts change `duration` and byte counts and can make live features differ from IoT-23.
4. In JSON logs, **unset fields are left out** (IoT-23 files use `-` instead). `make_features()` already handles this with `reindex`.
5. You can also run Zeek on a saved capture file to test without a live network: `zeek -C -r sample.pcap /path/to/sensor/local.zeek`.

**Output:** `sensor/local.zeek`; Zeek writing `conn.log`.

**Done when:** Opening the camera stream or a web page creates new lines in `conn.log`.

**Proposal:** Sections 2.5, 3.5; FR-01.

---

## Step 20. Collect our own benign camera traffic

**Why:** IoT-23 has no camera in its normal data. To test H1 (FPR ≤ 5% on local camera traffic), we need real normal camera traffic.

**How to do it:**
1. Use **passive mode** so you see all camera traffic.
2. With Zeek running, do the **normal activities** from proposal 5.1, for several hours on different days:
   - non-stop streaming to the NVR,
   - administrator login to the camera,
   - live view and video playback,
   - device discovery.
3. Save the logs as `data/local/benign/<date>/conn.log`. **Metadata only — no video.**
4. Write in the lab logbook what was running and when.
5. Keep this data **as test data**. If you also try adding part of it to training, report that as a **separate extra experiment** and never test on the same part.

**Output:** `data/local/benign/`; logbook notes.

**Done when:** You have enough local benign flows covering all the normal activities to measure the false-positive rate.

**Proposal:** Sections 1.6, 2.3, 3.4 (third level); Table 11; H1.

---

## Step 21. Build the Zeek adapter

**Why:** The adapter is the bridge between Zeek and the model.

**How to do it:** Write `core_engine/zeek_adapter.py`:
1. **Follow** `conn.log` and read each new JSON line as soon as it is written. Example idea:

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
3. **Keep flows that are not complete** (e.g. no answer, missing values). Do not drop them; `make_features()` marks them with the `incomplete` flag.
4. Add the **observation time**, the **traffic direction** (inbound / outbound / internal, using `local_networks` from settings) and the **device details** (if known) for the dashboard and audit history.
5. Send flows to the detector in **small batches** (e.g. every 0.5 s or every 200 flows). Batches keep up with floods much better than one at a time.
6. Count flows read, flows dropped and the queue size (needed for Step 37).
7. TShark or Scapy may be used **only to check packet details**, never to make a second feature format.

**Output:** `core_engine/zeek_adapter.py`; tests with a sample `conn.log`.

**Done when:** The adapter gives correct rows both from `zeek -r sample.pcap` and from live traffic.

**Proposal:** Section 3.5; FR-01; Figure 3.

---

## Step 22. Offline vs live feature check (schema check)

**Why:** If live features are made differently from training features, the model gets "wrong" input and the predictions are wrong, **without any error message**. This step stops that.

**How to do it:** Write `tools/schema_check.py`. Compare the IoT-23 features with the live features from Step 20 on:
1. Column names and order.
2. Data types.
3. Normal ranges (min, max, percentiles).
4. Missing values.
5. Categories: values of `proto`, `service`, `conn_state`, `history` that appear live but never in training.
6. Summary distributions (e.g. side-by-side histograms).

**Rule:** if a feature **cannot be made the same way** in both places, **drop it and train again** (go back to Step 14 with the smaller feature list). Write every drop in the decision log.

**Output:** `reports/schema_check.md`.

**Done when:** Every kept feature passes. This report answers **RQ3**.

**Proposal:** Sections 2.5, 3.5; Objective O3; RQ3; Table 11.

---

# Phase 6: Backend, Database and APIs (W15 – W23)

## Step 23. Set up MongoDB

**Why:** All evidence, actions and settings must be stored and traceable.

**How to do it:** Write `core_engine/db_service.py` (database name e.g. `iot_ids_db`).

**Collections required by the proposal** (Section 3.6 and Figure 4):

| Collection | Main fields |
|---|---|
| `devices` | IP, MAC, vendor, open ports, possible services, last scan time, `possible_camera` with evidence |
| `attack_events` | time, direction, source IP/port, destination IP/port, protocol, predicted class, confidence, model version, flow features, short evidence note, **status** (`prediction` or `confirmed`), response status |
| `response_actions` | event link, action (block / rate-limit / isolate / unblock), rule, target, **reason code**, actor, status, time |
| `blocklist` | IP, direction (source or destination), reason, linked event, created time, **expiry time**, status (`active` / `expired` / `removed`) |
| `system_logs` | actor, event, outcome, time |
| `users` | username, password hash, created time |

**Supporting collections needed by the requirements:**

| Collection | Needed by |
|---|---|
| `traffic_summaries` (benign flows counted per minute, by class) | FR-03 ("save benign traffic summaries"); Table 5 ("Benign: log it and update the traffic summary") |
| `settings` (allowlist and thresholds, with change history) | FR-07 |
| `scans` (who started a scan, subnet, start/end time) | FR-05; 3.7 (record scan time) |

Also:
1. Add indexes on IP, time and status fields.
2. Add **retention rules** with TTL indexes, using the periods from the agreed retention plan (Step 1). Example:

```python
db.traffic_summaries.create_index("minute", expireAfterSeconds=DAYS * 86400)  # "minute" must be a date
```

3. ➕ Extra: **group repeated flows into one event** (same source, destination and class within the time window updates one event: flow count + last seen). During a flood this avoids thousands of separate alerts.

**Output:** `core_engine/db_service.py`; index setup; tests.

**Done when:** A test writes and reads back one record in each collection; TTL indexes exist.

**Proposal:** Section 3.6; Figure 4; FR-03, FR-07.

---

## Step 24. Login and secrets

**Why:** The proposal says the REST endpoints and the dashboard need a login, and only a logged-in administrator can start scans and change blocks.

**How to do it:**
1. Write `core_engine/auth.py`: login with username and password (stored as a **bcrypt hash** in `users`). On success, return a JWT token.
2. **No open sign-up page.** Create administrator accounts with a script, `tools/create_admin.py`.
3. Read `JWT_SECRET_KEY` and `MONGO_URI` from the `.env` file (`python-dotenv`). **Remove the hard-coded secret and admin password** that were in the old `my-app/app.py`.
4. Write every login, failed login and admin action to `system_logs`.

**Output:** `core_engine/auth.py`, `tools/create_admin.py`, `.env` (not in Git).

**Done when:** A request without a valid token gets `401 Unauthorized`.

**Proposal:** Section 3.6 (login, secrets); Section 3.7 (logged-in administrator); FR-04.

---

## Step 25. Build the Flask + Socket.IO server

**Why:** One backend replaces the five old ones.

**How to do it:** Write `core_engine/app.py` (one port, e.g. 5000). All endpoints need a login.

**REST endpoints:**

| Method and path | Purpose |
|---|---|
| `POST /api/auth/login` | Log in, get a token |
| `GET /api/summary` | Event totals, class distribution, traffic summary |
| `GET /api/events` | Attack history, with filters (time, class, IP, status) |
| `GET /api/events/<id>` | One event with its evidence and actions |
| `PATCH /api/events/<id>` | Admin marks the event as a **confirmed incident** |
| `GET /api/devices` | Device records |
| `POST /api/scans` | Start a scan (approved subnet only) |
| `GET /api/scans/<id>` | Scan progress and result |
| `GET /api/blocklist` | Active and past rules |
| `POST /api/blocklist` | Manual block |
| `DELETE /api/blocklist/<id>` | Manual unblock |
| `GET /api/settings`, `PUT /api/settings` | Allowlist and thresholds |
| `GET /api/logs/export` | Export filtered logs (FR-08) |
| `GET /api/health` | Status of Zeek, model, database and response adapter |

**Socket.IO events** (live updates; the proposal lists summaries, attack history, device records, blocklist controls, scans, settings and log export):
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

**Output:** `core_engine/app.py`; API tests in `tests/integration/`.

**Done when:** All endpoints work in the tests, and a logged-in Socket.IO test client receives a test event.

**Proposal:** Section 3.6; FR-03, FR-04, FR-08.

---

## Step 26. Build the detector and decision engine

**Why:** This connects everything: flow → features → prediction → decision → record → dashboard → response (proposal Figure 3).

**How to do it:**
1. `core_engine/detector.py`:
   - Load the model bundle **once** at start-up.
   - For each batch from the adapter: `make_features()` → `pipeline.predict_proba()`.
   - Return the **class, confidence and model version** for each flow (FR-02).
2. `core_engine/decision_engine.py`:
   - **Benign** → update the traffic summary only. No blocking.
   - **Attack below the confidence threshold** → save the event and **alert only**.
   - **Attack at or above the threshold** → save the event, alert, and pass it to the response policy (Step 31). A response happens only if **all** safety checks pass.
   - Every new event has status `prediction` until an admin confirms it.
3. Every alert contains: **time, traffic direction, source and destination, predicted class, confidence, a short evidence note** (e.g. "40 unanswered connections to port 23 on 30 hosts in 20 s") **and response status**.
4. Save a timestamp at each stage: flow written by Zeek, read by adapter, predicted, saved, sent to dashboard, firewall rule applied. These are needed in Step 37.

**Output:** `core_engine/detector.py`, `core_engine/decision_engine.py`, tests.

**Done when:** Running a saved capture through Zeek creates events in MongoDB and on a Socket.IO test client.

**Proposal:** Figures 2, 3; Sections 3.4, 3.6; FR-02, FR-03, FR-04.

---

## Step 27. Device discovery (Nmap)

**Why:** The admin needs to know which devices and services are on the network.

**How to do it:** Write `core_engine/scanner_service.py` (reuse the Nmap parts of the old `network_scan.py` with `python-nmap`):
1. **Refuse any subnet that is not in `approved_scan_subnets`.**
2. Only a **logged-in administrator** can start a scan. Write who started it in `system_logs`.
3. Record: whether the host is up, the MAC address (when visible), open ports, possible service names and the scan time.
4. **Remove the random vulnerability numbers** from the old code.
5. **Never decide a device is a camera from one port number.** HTTP, HTTPS and RTSP are common, but vendors use different ports. Mark it `possible_camera` with the evidence and let the admin confirm.
6. Save to `devices` and `scans`; send progress with `scan_progress`.

**Output:** `core_engine/scanner_service.py`; tests.

**Done when:** A scan of the lab subnet lists the lab devices, and a request for any other subnet is refused.

**Proposal:** Section 3.7; FR-05.

---

## Step 28. Log export

**Why:** We need attack logs for testing and for the final report.

**How to do it:** Write `core_engine/export_service.py`: filter by time range, class, IP and status; export as CSV or JSON. Write each export in `system_logs`.

**Output:** `core_engine/export_service.py`; test.

**Done when:** Exporting one test day gives a file with the right rows.

**Proposal:** FR-08.

---

# Phase 7: React Dashboard and Alerts (W18 – W25)

## Step 29. Clean up the React app

**Why:** One clean dashboard that talks to one backend.

**How to do it:**
1. Remove the KDD and CICIDS pages and menu items, and the register page.
2. Make one config file, `src/config.js`, with the backend address (read from an environment variable such as `REACT_APP_API_URL`).
3. Use **`socket.io-client`** (already in `package.json`) instead of plain `WebSocket`:

```javascript
import { io } from "socket.io-client";
const socket = io(API_URL, { auth: { token } });
socket.on("new_event", (event) => { /* add to the alert list */ });
```

4. Add a login page. Store the token and send it with every request (`Authorization: Bearer <token>`) and on the Socket.IO connection. Go back to the login page when the token is missing or expired.

**Output:** Cleaned `my-app/`.

**Done when:** `npm start` works, login works, and no code calls the old ports.

**Proposal:** Section 3.6; FR-04.

---

## Step 30. Build the dashboard pages

**Why:** The operator needs one place to see devices, predictions, evidence, alerts and actions that can be undone (proposal 7.1).

**How to do it:**

| Page | What it shows (proposal 3.6) |
|---|---|
| **Overview** | Event totals, recent alerts, class distribution, live traffic, device status, response history. |
| **Live alerts** | New alerts appear without refresh. Each one: time, direction, source, destination, class, confidence, evidence note, response status. A clear badge **"Model prediction"** or **"Confirmed incident"**. |
| **Attack history** | Search and filter events; open one event to see its evidence and actions; admin can confirm it. |
| **Devices** | Discovered devices with MAC, vendor, ports and services; admin can start a scan; scan progress. |
| **Blocklist / response** | Active rules (IP, direction, reason, class, confidence, created, **expires**), past rules, **Unblock** button, manual block form. |
| **Settings** | Allowlist and thresholds. Every change is logged. |
| **Logs and export** | System log; export with filters. |

The layout must work on any screen size (proposal Table 8: "a dashboard that fits any screen").

**Output:** Dashboard pages.

**Done when:** A replayed attack appears live without refresh, and a manual block/unblock from the dashboard changes the rule and the database.

**Proposal:** Sections 3.6, 7.1; Table 8; FR-04, FR-06, FR-07, FR-08.

---

# Phase 8: Firewall Response Controls (W21 – W27)

## Step 31. Write the response policy (the safety rules)

**Why:** A wrong block could cut off the administrator or the NVR. The policy makes sure the system only acts when it is safe.

**How to do it:** Write `docs/response_policy.md` and implement it in `decision_engine.py`.

**A. What to do, by class and direction** (proposal Table 5 and Section 3.7):

| Class | Direction | Action (only if all safety checks pass) |
|---|---|---|
| Benign | any | Log and update the summary. **Never block.** |
| Port scan | from outside | Alert. **Block the scanner (source IP) after it keeps trying.** |
| DDoS / DoS | from outside | Alert. **Rate-limit or block the outside source**, if the policy allows. |
| C&C | local device → outside | Treat as suspicious. **Block the destination**, or **isolate the device** if the policy allows. |
| Malware / download | any | Alert with the subtype. **Quarantine (isolate) or block, based on direction and confidence.** |
| Any attack class | — | Below the confidence threshold → **alert only**. |

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
- an allowlisted IP is **never** blocked,
- **one** high-confidence event does **not** block,
- a low-confidence event only alerts,
- every rule has an expiry.

**Output:** `docs/response_policy.md`; code; unit tests.

**Done when:** All the tests in D pass. This step answers **RQ5**.

**Proposal:** Sections 2.5, 3.4, 3.7; Table 5; FR-07; RQ5.

---

## Step 32. Write the nftables rules

**Why:** nftables is the proposal's first choice for blocking. Sets with timeouts give rules that expire on their own and are easy to undo.

**How to do it:**

**32a. Inline mode (sensor is a transparent bridge).** Bridged traffic is filtered in the **`bridge`** family on the **forward** hook. Create `sensor/ids_inline.nft`:

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

Load it with `sudo nft -f sensor/ids_inline.nft`. Note: the rate limit above is shared by all IPs in `limit_src`, which is fine for lab tests.

**32b. Passive mode (blocking on the lab router).** If the router runs nftables (OpenWrt does), use the same sets in an **`inet`** table on its **forward** hook (`sensor/ids_router.nft`), because the router *routes* traffic instead of bridging it.

**32c. The commands the adapter uses:**

```bash
sudo nft add element bridge ids block_src '{ 10.10.10.50 timeout 30m }'   # block for 30 minutes
sudo nft delete element bridge ids block_src '{ 10.10.10.50 }'            # unblock
sudo nft list set bridge ids block_src                                    # list active blocks
```

(On the router, use `inet` instead of `bridge`.)

**Important:** the allowlist rule only checks the **source** (`ip saddr @allow`). Do not add `ip daddr @allow accept`, or a blocked attacker could still reach the NVR or the admin PC.

➕ Extra: run the backend as a normal user and allow it to run **only** `/usr/sbin/nft` with `sudo` (a sudoers rule), not full root.

**Output:** `sensor/ids_inline.nft`, `sensor/ids_router.nft`.

**Done when:** Adding the attack computer to `block_src` stops its traffic to the camera, and deleting it brings the traffic back.

**Proposal:** Section 3.7; Table 8; FR-06.

---

## Step 33. Build the response adapters

**Why:** The same decision must work in both deployment modes.

**How to do it:** In `core_engine/firewall/`:
1. `base.py`: one common interface — `block(ip, direction, minutes, reason)`, `rate_limit(ip, minutes, reason)`, `unblock(ip, direction)`, `list_active()`.
2. `nftables_adapter.py`: runs the commands from Step 32 on the sensor (**inline mode**).
3. `router_adapter.py`: for **passive mode**. The SPAN port cannot block, so the system sends the request to the lab router (e.g. by SSH with a key, running the same `nft` commands, or by the router's API). Connection details come from `.env`.
4. The proposal also allows an **iptables/ipset** adapter. Add it only if you need it.
5. ➕ Extra: `simulation_adapter.py` only writes the action to the log. Use it for development on Windows. **Never report simulation results as real blocking.**
6. Every call writes to `response_actions` and `blocklist` and sends `blocklist_update`.

**Output:** Adapter code; tests.

**Done when:** In the lab, each real adapter can block and unblock the attack computer.

**Proposal:** Sections 1.2, 2.5, 3.7; Figure 5; FR-06.

---

## Step 34. Manual control, expiry and restart recovery

**Why:** The admin must always be in control, and the system must stay correct after problems.

**How to do it:**
1. **Manual block and unblock** from the dashboard call the adapter and are written to the audit log with the admin's name.
2. **Expiry:** nftables removes an element by itself when its timeout ends. A background job marks it `expired` in MongoDB. If an adapter cannot expire rules by itself, the job removes them.
3. **Restart recovery:** at start-up, compare the active rules in the firewall with the `blocklist` collection, fix any difference, and write what was fixed in `system_logs`.

**Output:** Code and tests.

**Done when:** After a forced restart, the firewall rules and the database match, and expired rules are gone.

**Proposal:** Section 3.7; Table 9 (reliability: old rules cleaned up); Objective O5.

---

# Phase 9: Controlled Security Testing (W25 – W30)

**Before every test:** write it in the lab logbook, check the lab is separated, and check the allowlist. **No live malware. No public IP addresses.**

## Step 35. Run the 6 controlled test scenarios

**Why:** These prove the full system works safely (proposal Table 10).

**How to do it:** Put the test scripts in `tests/lab_scenarios/`. Run each scenario several times (e.g. 5 runs). Use passive and inline mode where it makes sense.

| # | Scenario (Table 10) | How to make it in the lab | What we expect to see | The safe result we need |
|---|---|---|---|---|
| 1 | Normal live streaming and playback | Stream to the NVR, log in, play back video for a long time | Most flows benign; no high-confidence attack event | **No automatic block.** Traffic summary keeps working. |
| 2 | Authorised Nmap horizontal scan | From the attack computer: `nmap -p 23,80,554 192.168.50.0/24` | Port-scan class or a scan alert | Scanner blocked **only after the threshold**. The allowlisted admin can still get in. |
| 3 | Rate-limited DDoS-like traffic | e.g. `sudo hping3 -S -p 80 -i u1000 -c 20000 192.168.50.30` (about 1000 packets/s for 20 s), or replay | DDoS/DoS prediction; more events than usual | Source blocked or rate-limited. **Camera service comes back.** |
| 4 | C&C-like periodic outbound simulation | The camera simulator (a lab device on the camera side) opens a small connection to the attack computer (acting as a lab "C&C server") every N seconds | C&C or heartbeat evidence from a local device to the outside | Destination blocked, or device isolated, following the policy. |
| 5 | Controlled file-transfer pattern | The lab device downloads a **harmless** file from a lab web server on the attack computer, repeatedly | Download or malware prediction, **if** the learned features can show it | Alert and evidence kept. **We claim nothing if the model cannot generalise.** |
| 6 | Manual block and unblock | The admin blocks and then unblocks the attack computer from the dashboard | Rule change seen in the dashboard and the database | Connection comes back; full audit record kept. |

"Replay" means sending saved traffic again. You can also process IoT-23 or lab captures offline with `zeek -C -r file.pcap`. Replay on the wire **only** on the separated lab network.

For each run, record: predictions, events, actions taken, any wrong blocks, and the times.

**Output:** `reports/lab_tests/scenario_<n>.md` with raw logs and exported events.

**Done when:** All 6 scenarios are run and recorded, **including failures**.

**Proposal:** Table 10; Sections 3.8, 5.1.

---

## Step 36. Functional requirement tests

**Why:** Prove each requirement from Table 7 works.

**How to do it:** Run one test per requirement and record pass/fail with evidence:

| FR | Test |
|---|---|
| FR-01 | Schema test (Zeek → adapter → features) |
| FR-02 | Model API test (class, confidence, model version) |
| FR-03 | Database test (summaries, events, actions saved) |
| FR-04 | Socket.IO latency test (alert reaches the logged-in dashboard without refresh) |
| FR-05 | Inventory test (scan finds the lab devices) |
| FR-06 | Rule add / list / expire / remove on the separated network |
| FR-07 | Safety test (allowlist, thresholds, audit history) |
| FR-08 | Export test |

**Output:** `reports/fr_tests.md`.

**Done when:** Every "Must" requirement passes.

**Proposal:** Table 7; Objective O4.

---

## Step 37. Measure speed and resource use

**Why:** To answer RQ4 and check the latency targets.

**How to do it:** Write `tools/measure_latency.py`:
1. From the stage timestamps (Step 26), calculate:
   - capture (Zeek writes the flow) → prediction,
   - prediction → dashboard,
   - prediction → alert,
   - prediction → blocking rule active.
2. Report the **median** and the **95th percentile**. Targets: **median decision < 2 s; 95th percentile < 5 s** under the target load.
3. Also measure and explain **how long Zeek waits before it writes a flow** (it writes when the connection ends or times out). Be honest about this in the results.
4. During normal load and attack load, record every second: **flows per second, CPU and memory** (Zeek and the Python services, with `psutil`), and **dropped events** (Zeek's packet-loss logs and the adapter's dropped/queued counts).

**Output:** `reports/performance.md` with tables and charts.

**Done when:** Numbers exist for normal and attack load.

**Proposal:** Table 9 (latency, throughput/resources); Objective O6; RQ4.

---

## Step 38. Reliability tests

**Why:** Proposal Table 9 requires recovery after restart, data kept, and old rules cleaned up.

**How to do it:** Test and record:
1. Restart the backend during traffic → data in MongoDB is kept; the adapter continues from the right place.
2. Restart the sensor → firewall rules and the database match after start-up.
3. Let a rule expire → it is removed and marked `expired`.
4. Inline mode → use the bypass plan; the network works again.

**Output:** `reports/reliability.md`.

**Done when:** All important recovery tests pass.

**Proposal:** Table 9 (reliability); Table 11 (inline risk).

---

## Step 39. Usability and audit test

**Why:** Proposal Table 9: the administrator can finish set tasks, and every action can be traced.

**How to do it:**
1. Write 5–6 tasks, e.g.: find the latest alert and its evidence; unblock an IP; confirm an incident; export yesterday's attack logs; start a device scan; change a threshold.
2. Ask a few people to do them. Record success, time taken and comments.
3. Check that **every action is in the audit log** (who, what, when, why).

**Output:** `reports/usability.md`.

**Done when:** The tasks can be finished and every action is traceable.

**Proposal:** Table 9 (usability/audit).

---

# Phase 10: Evaluation and Analysis (W28 – W32)

## Step 40. Put all results together

**Why:** Answer the hypothesis and every research question with evidence.

**How to do it:**
1. Fill in the results table (proposal Table 9):

| What we test | Target we accept for now | Our result | Met? |
|---|---|---|---|
| Classification | macro-F1 ≥ 0.85 on the held-out scenario (report all results either way) | | |
| Benign safety | FPR ≤ 5%; no blocks on the management computer or the NVR | | |
| Latency | median decision < 2 s; 95th percentile < 5 s under target load | | |
| Throughput / resources | keeps up with the measured lab traffic; no important event lost | | |
| Reliability | all important recovery tests pass | | |
| Usability / audit | admin finishes the set tasks; every action traceable | | |

2. **H1:** accepted or not, with both numbers (macro-F1 on held-out scenarios, FPR on local camera traffic).
3. Answer **RQ1–RQ5**, one short section each, pointing to the reports.
4. Show the **gap between benchmark and local results**: grouped CV → held-out scenario → local camera traffic.
5. For every missed target, explain the likely reason (domain shift, feature mismatch, too few examples) using the schema check and per-class metrics. **Report it anyway.**
6. List the classes that did badly and all false positives.

**Output:** `reports/final_evaluation.md`.

**Done when:** Every target, H1 and RQ1–RQ5 has an answer with evidence.

**Proposal:** Sections 6, 7; Table 9; H1; RQ1–RQ5; Objective O6.

---

# Phase 11: Documentation and Final Demo (W29 – W32)

## Step 41. Write the final documents

**Why:** Anyone must be able to understand, repeat and run the project.

**How to do it:**
1. **Final report** following the proposal structure: introduction, literature review, methodology, implementation, results, discussion, limitations and future work (e.g. online learning, more camera models — Table 11).
2. **README.md**: install, configure, train and run.
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

**Output:** Final report, README, tagged release.

**Done when:** A person outside the team can follow the README and run the system.

**Proposal:** Objective O1; Section 1.6 (expected outcomes).

---

## Step 42. Final demo and data clean-up

**Why:** Show the working system and finish the project safely.

**How to do it:**
1. Prepare a demo script: normal streaming (no blocks) → Nmap scan (detected; blocked only after the threshold; admin still connected) → DDoS-like traffic (rate-limited; camera recovers) → manual unblock (audit record shown) → log export.
2. ➕ Extra: record a backup video of the demo in case the lab fails on the day.
3. After the project, **delete or archive the data** following the agreed retention plan. Remove lab credentials and firewall rights from team accounts. Write this in the logbook.

**Output:** Demo script, data clean-up record.

**Done when:** The demo is done and the retention plan is followed.

**Proposal:** Section 3.8; Figure 6.

---

# Part D: Final Checklist

Tick each item only when its evidence exists.

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
- [ ] Approval before experiments (Step 1)
- [ ] All tests only on the separated lab, written in the logbook (Phase 9)
- [ ] No video or audio stored (Steps 20, 23)
- [ ] Data deleted or archived per the retention plan (Step 42)

---

# Part E: Common Mistakes to Avoid

| Mistake | Why it is wrong | Do this instead |
|---|---|---|
| Using the old `X_train.csv` "because it is ready" | Unofficial, partly scaled, no scenario IDs, random split | Start from official IoT-23 (Step 7) |
| `train_test_split` on all rows | Leakage: same capture in train and test, scores too high | Grouped CV + held-out scenario (Step 13) |
| Changing the label mapping after seeing results | Makes results look better than they are | Freeze it in Step 8 |
| Tuning on the held-out scenario | It is no longer a fair test | Tune only inside grouped CV (Step 14) |
| Using IP addresses or ports as raw numbers in the model | The model memorises captures instead of behaviour | Remove IPs; group ports (Step 11) |
| Writing different feature code for live data | Live predictions become silently wrong | One shared `make_features()` (Step 11) + schema check (Step 22) |
| Reporting only accuracy | Hides weak small classes | Macro-F1, per-class recall, FPR, confusion matrix (Step 16) |
| Blocking on one prediction | Could cut off the admin or the NVR | All safety checks (Step 31) |
| `iptables -A INPUT` to protect cameras | Only protects the sensor itself | Bridge forward (inline) or router forward (passive) (Step 32) |
| Putting the attack computer on the camera switch | Its traffic never passes the router or bridge, so it cannot be blocked | Put it on the "outside" lab subnet (Step 5) |
| Calling a device a camera because port 554 is open | Vendors use different ports | `possible_camera` + evidence + admin confirm (Step 27) |
| Using random or made-up numbers on the dashboard | Fake data; not research | Show only real measured data |
| Reporting simulation-mode blocks as real | Not real enforcement | Test with the nftables or router adapter (Step 33) |
| Secrets in the code | Anyone with the code gets access | `.env` file, not in Git (Step 24) |
