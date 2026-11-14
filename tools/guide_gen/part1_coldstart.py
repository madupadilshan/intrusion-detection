# -*- coding: utf-8 -*-
"""Part 1: Pre-Meeting Lab Initialization (Cold Start)"""

SECTION_1 = """# 1. Pre-Meeting Lab Initialization (Cold Start)

Two minutes before sharing your screen with the supervisor, run the following commands in your terminal to prepare the system:

---

#### 1. Start All 11 Docker Containers in the Background:

##### 💡 Why We Are Doing This:
To bring the virtual lab network topology (11 virtual devices and 2 isolated subnets) into a fully active, running state as formally specified in Section 5.1 of our Research Proposal.

> [!IMPORTANT]
> **Prerequisite:** Docker Desktop must be running on your system! Open `Docker Desktop` from the Windows Start Menu, and wait until the whale icon in the System Tray turns green and indicates "Docker Desktop is running" (if Docker Desktop is not running, commands will fail with `failed to connect to the docker API at npipe:...`).

##### ⚙️ What Happens Under the Hood:
The Docker daemon reads `lab_virtual/docker-compose.yml`, creates two Linux bridge networks (`camlan` 192.168.50.0/24 and `outside` 10.10.10.0/24), and spins up all 11 containers (Router, IP Camera, NVR, Admin PC, Attacker, Zeek Sensor, etc.) as isolated memory processes.

```powershell
# Option 1: Using the project's official Lab CLI (Recommended)
.venv\\Scripts\\python.exe lab_virtual\\lab.py up

# Option 2: Directly via docker compose
docker compose -f lab_virtual\\docker-compose.yml up -d
```

##### 🔍 Line-by-Line Breakdown:
- `.venv\\Scripts\\python.exe lab_virtual\\lab.py up`: Launches our custom lab controller to start and verify all 11 Docker containers.
- `docker compose -f lab_virtual\\docker-compose.yml up -d`: Starts the containers defined in the Compose configuration file in detached (`-d`) background mode.

##### 📋 Verified Output:
```text
[+] Running 11/11
 ✔ Network lab_virtual_camlan       Created
 ✔ Network lab_virtual_outside      Created
 ✔ Container ids-lab-router         Started
 ✔ Container ids-lab-camera         Started
 ✔ Container ids-lab-nvr            Started
 ✔ Container ids-lab-admin          Started
 ✔ Container ids-lab-attacker       Started
 ✔ Container ids-lab-sensor         Started
 ✔ Container ids-lab-scanner        Started
 ✔ Container ids-lab-cloud          Started
 ✔ Container ids-lab-camera2        Started
 ✔ Container ids-lab-camera3        Started
 ✔ Container ids-lab-camera4        Started
```

##### 📊 Output Breakdown:
- `Network Created`: Two virtual Linux bridge switches (`camlan` for internal IoT LAN and `outside` for WAN/Attacker) have been created.
- `Started (11/11)`: All 11 virtual nodes (IP camera, NVR recorder, Zeek sensor, Linux router, attacker, etc.) started cleanly without any errors.

---

#### 2. Start the Python IDS Backend & Dashboard on Port 5000 in the Background:

##### 💡 Why We Are Doing This:
To launch the real-time streaming pipeline that tails Zeek logs, the Random Forest classifier, the router firewall controller, and the Flask REST API with Socket.IO WebSockets that serves the React SOC dashboard.

> [!NOTE]
> In Windows PowerShell 5.1 (standard PowerShell), the `Start-Process` cmdlet does not support the `-Environment` parameter. Therefore, use **Option 1 (Recommended)** below, which handles background logging, environment variables, health checks, and starts the streaming pipeline automatically.

##### ⚙️ What Happens Under the Hood:
The Python interpreter runs `core_engine/app.py`. Upon startup, it loads the trained AI model bundle `ml_engine/models/ids_bundle_v3_2.joblib` (v3.2.0) into RAM, connects to MongoDB, starts the background Zeek log tailer thread, and begins listening on Port 5000 for HTTP and WebSocket requests.

```powershell
# Method 1: Using the official Lab CLI in background (Recommended - All PowerShell versions supported)
.venv\\Scripts\\python.exe lab_virtual\\lab.py ids-start

# Method 2: Running directly in background via Windows PowerShell 5.1
$env:IDS_SETTINGS_FILE="lab_virtual/settings.lab.yaml"; $env:DB_NAME="iot_ids_lab"; $env:PORT="5000"; $env:HOST="127.0.0.1"
Start-Process .venv\\Scripts\\python.exe -ArgumentList "-m core_engine.app"
```

##### 🔍 Line-by-Line Breakdown:
- `lab_virtual\\lab.py ids-start`: Sets environment variables (`IDS_SETTINGS_FILE`, `DB_NAME`, `PORT`), redirects output to `lab_virtual/logs/ids_backend.log`, launches the process in the background, waits for Port 5000 to become ready, and issues `/api/v1/pipeline/start` to start the streaming pipeline.
- `$env:...`: Configures PowerShell environment variables.
- `Start-Process ... -ArgumentList "-m core_engine.app"`: Spawns `core_engine/app.py` as a detached background process.

##### 📋 Verified Output:
```text
IDS backend running (pid 14328), database iot_ids_lab; pipeline start: 200 running
Dashboard: http://localhost:5000 (served by the backend)  login in lab_virtual\\keys\\dashboard_login.txt
```

---

#### 3. Clean the Lab Before the Demo (Very Important):

##### 💡 Why We Are Doing This:
Residual firewall blocks or lingering C&C test servers from earlier test runs can distort demonstration results:
- An active block remaining on the router drops packets at the firewall before they ever reach the Zeek sensor, preventing the new attack from being analyzed.
- A lingering C&C server on Port 6667 (`lab_server.py --role cnc`) allows outbound connections to succeed; our model does not alert on clean, established connections (in tests on 13 Nov, 18 clean connections produced 0 alerts), and it prevents `nc -lp 6667` from binding to the port.

```powershell
# 1. Stop any C&C test servers left from an earlier run (it is fine if this prints nothing):
docker exec ids-lab-attack-server pkill -f "lab_server.py --role cnc"

# 2. Remove all blocks and rate-limits (from both Database and Router):
.venv\\Scripts\\python.exe lab_virtual\\lab.py reset
```

##### 📋 Verified Output:
```text
removed 0 block(s) through the IDS
router sets now: {'block_src': [], 'block_dst': [], 'limit_src': []}
```

> ⚠️ Remember to run `lab.py reset` between the individual attack tests in FR-02 as well.

---

#### 3b. Fresh Backend Start After Any Rehearsal (Very Important for FR-02):

##### 💡 Why We Are Doing This:
The model utilizes time-window features that track per-source behavior over the past **60 minutes** (e.g., `pair_fail_1h` = count of failed connection attempts to the same destination). Every rehearsal run from attacker `10.10.10.50` accumulates inside this memory. If multiple floods and scans were executed within an hour, a subsequent port scan might be classified as **C&C** rather than PortScan. (Thanks to the Issue 43 fix, this does not cause a false block, but restarting ensures the alert card displays a clean PortScan classification: on 13 Nov, after an hour of heavy testing, the sweep showed CnC 0.52, whereas after a fresh restart, it immediately showed **PortScan 0.84**). Running `lab.py reset` clears the router firewall, but **does not clear the ML window memory**.

##### ⚙️ What Happens Under the Hood:
The rolling window memory (`WindowState`) and repeat counters reside solely in backend RAM. Restarting the backend completely re-initializes them to a clean state.

```powershell
.venv\\Scripts\\python.exe lab_virtual\\lab.py ids-stop
.venv\\Scripts\\python.exe lab_virtual\\lab.py ids-start
.venv\\Scripts\\python.exe lab_virtual\\lab.py reset
```

##### 📋 Verified Output:
```text
IDS backend stopped
IDS backend running (pid 20864), database iot_ids_lab; pipeline start: 200 running
router sets now: {'block_src': [], 'block_dst': [], 'limit_src': []}
```

> **Rules for the Live Demo:**
> - After your final rehearsal, run this fresh start right before presenting to the supervisor.
> - After FR-02 Test 2.3 (SYN Flood), running this fresh restart ensures that Test 2.4 (C&C) and Test 2.5 (Malware Download) produce crystal-clear, textbook alert cards.

---

#### 4. Verify the Router Firewall (`nftables`) is Ready:

##### 💡 Why We Are Doing This:
To verify that the Linux kernel firewall on the router is loaded with its dynamic drop sets (`block_dst`, `block_src`, `limit_src`) and that forwarding rules are active.

##### ⚙️ What Happens Under the Hood:
Queries the `nftables` kernel subsystem inside the router container to list the complete firewall ruleset.

```powershell
docker exec ids-lab-router nft list table inet ids
```

##### 🔍 Line-by-Line Breakdown:
- `docker exec ids-lab-router`: Executes a command inside the router container.
- `nft list table inet ids`: Displays the complete packet-filtering table and rules in the Linux kernel `nftables` firewall.

##### 📋 Verified Output:
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

##### 📊 Output Breakdown:
- `set block_dst { flags timeout }`: Dynamic destination drop set with automatic expiry timers (blocks infected camera C&C outbound beacons).
- `set block_src { flags timeout }`: Dynamic source drop set with timeout timers (blocks inbound external attackers).
- `set limit_src { flags timeout }`: Dynamic rate-limit set (mitigates DDoS SYN floods).
- `chain forward`: Linux kernel packet-filtering chain on the bridge, configured to evaluate every forwarded IP packet against these sets before routing.

---

#### 5. Open the Web Dashboard & Introduce the 7 Pages:

##### 💡 Why We Use the Web Dashboard:
Provides a real-time SOC (Security Operations Center) visual interface for monitoring network traffic, alerts, active mitigations, and device inventory with zero manual browser refreshes (powered by Socket.IO WebSockets).

##### 🌐 Accessing the Dashboard:
- URL: **`http://localhost:5000`**
- Login Credentials: Found in `lab_virtual/keys/dashboard_login.txt` (default username: `admin`, password generated cryptographically).

##### 📑 The 7 Main Navigation Tabs:
1. **🖥️ Overview (`/overview`):** Displays real-time System Status, pipeline health, active model version (**v3.2.0**), processed flow counts, throughput, and 24-hour benign vs. attack metric cards.
2. **🚨 Real-Time Alerts (`/alerts`):** Displays live incoming security alerts pushed instantly via WebSockets with calibrated confidence scores, flow telemetry, and response status.
3. **🌐 Live Visualizer (`/visualizer`):** Interactive topological graph of the network showing camera nodes, router, attacker, and live packet/attack flows with color-coded risk indicators.
4. **📋 Device Inventory (`/inventory`):** Comprehensive asset inventory table displaying IP addresses, MAC addresses, device roles (Camera, NVR, Admin), operating status, and open services discovered by Nmap.
5. **📜 System Logs (`/logs`):** Live streaming administrative and engine log viewer for real-time auditability.
6. **📁 Attack History (`/history`):** Persistent forensic incident archive stored in MongoDB, searchable and filterable by attack class, IP, and time range.
7. **🛡️ Active Mitigations (`/mitigations`):** Live control center showing active firewall blocks and rate-limits with real-time countdown timers, manual block controls, and one-click rollback capabilities.

---

### 💡 Key Concept to Clarify Upfront: Why We Built This Virtual Testbed

If the supervisor asks: **"Are you running this virtually? What is this lab environment?"**, or when introducing the setup at the start of the meeting, present the following points and spoken script:

#### 1. Core Rationale per Proposal Section 5.1:
* As formally approved in Section 5.1 of our Research Proposal, **prior to deploying onto physical hardware in the hardware lab**, we constructed this **realistic Docker virtual testbed** to safely and rigorously verify our end-to-end architecture (Zeek Sniffer, Random Forest AI Model, Linux nftables Router Firewall, and React Dashboard).
* This controlled virtual environment allows us to safely test aggressive cyberattacks—such as 1,000 packets/sec DDoS SYN floods, outbound C&C beacons, and full port scans—without risking physical hardware damage, device bricking, or campus network disruption.

#### 2. What is 100% Real and What is Simulated:
* **100% Real Components:**
  - **Real Network Packets:** Authentic raw Ethernet frames traversing Linux bridge networks (`br-ids-lan`, `br-ids-out`).
  - **Real Zeek Security Sensor:** Authentic Zeek binary sniffer attached to the switch interface in promiscuous mode, generating live `conn.log` and `http.log` from binary packet captures.
  - **Real Machine Learning Model (v3.2.0):** Authentic 100-tree Random Forest classifier trained on Stratosphere IoT-23 and lab download flows (extracting 27 flow features and performing live mathematical inference).
  - **Real Linux nftables Router Firewall:** Authentic Linux kernel `nftables` firewall inside the router running dynamic drop sets (`block_dst`, `block_src`) and auto-expiry timeout timers.
  - **Real React SOC Dashboard & WebSockets:** Authentic responsive web UI updating in real time over Port 5000 via Socket.IO events.
  - **Real Nmap Scanner:** Authentic Nmap binary executing real network scanning probes.
* **Simulated Network Entities:**
  - **Network Endpoint Devices:**
    - **IP Camera (`ids-lab-camera` / `192.168.50.30`):** Dockerized camera service providing Port 80 (HTTP Web GUI) and Port 554 (RTSP Video Streaming at ~200 KB/s).
    - **NVR Recorder (`ids-lab-nvr` / `192.168.50.20`):** Video recorder continuously pulling camera RTSP streams and saving 58.6 MB chunks every 5 minutes.
    - **Admin Workstation (`ids-lab-admin` / `192.168.50.10`):** Authorized client workstation managing camera settings.
    - **Attacker Machine (`ids-lab-attacker` / `10.10.10.50`):** Outside workstation launching Nmap scans, DDoS floods, and hosting malicious binaries.

#### 3. Opening Statement to the Supervisor (Spoken English Script):
> *"Good morning Sir. Before demonstrating our live intrusion detection and autonomous response, I would like to clarify our testbed setup."*  
> *"As formally approved in our research proposal Section 5.1, we have implemented the complete end-to-end architecture inside a realistic Docker virtual testbed."*  
> *"Sir, in this testbed: the network packets, Zeek sensor, Random Forest ML classifier (v3.2.0), Linux nftables router firewall, and the React dashboard are all 100% REAL. The network endpoints—our IP camera, NVR recorder, and outside attacker—are containerized simulations so we can safely evaluate high-rate attacks without risking physical hardware damage. Final physical camera validation will be conducted in the hardware lab as per our proposal timeline."*

---
"""
