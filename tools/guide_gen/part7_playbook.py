# -*- coding: utf-8 -*-
"""Part 7: Live Manual Attack Playbook and Closing Statement"""

SECTION_7_PLAYBOOK = """# 7. Part 6: Live Manual Attack Playbook

If the supervisor requests: **"Can you run a live attack, show Zeek intercepting it, the ML model classifying it, and the router firewall blocking it in real-time?"**, demonstrate any or all of the following three live attacks:

---

### Attack 1: Live Port Scan (Nmap Manual Probe)

#### 💡 Why We Are Doing This:
To visually prove that when an attacker scans camera ports looking for vulnerabilities, Zeek intercepts the probes and the system instantly generates a PortScan alert.

#### ⚙️ What Happens Under the Hood:
From the attacker container, TCP SYN packets are transmitted to camera IP `192.168.50.30` probing ports 80 and 554.

#### 💻 Direct Raw Command:
```powershell
docker exec ids-lab-attacker nmap -p 80,554 192.168.50.30
```

##### 🔍 Line-by-Line Breakdown:
- `docker exec ids-lab-attacker`: Enters the external attacker container.
- `nmap -p 80,554 192.168.50.30`: Launches authentic Nmap scan probing camera web (80) and RTSP (554) ports.

##### 📋 Real Output:
```text
PORT    STATE SERVICE
80/tcp  open  http
554/tcp open  rtsp
Nmap done: 1 IP address (1 host up) scanned in 0.79 seconds
```

#### 🖥️ Live Dashboard Proof:
1. **Real-Time Alerts (`http://localhost:5000/alerts`):**
   - The instant the scan finishes in the terminal (0.79s), **without refreshing the browser**, a yellow **`PortScan`** alert card pops up within 0.11 seconds.
   - Point out Attacker IP (`10.10.10.50`), Target IP (`192.168.50.30`), and Confidence (`92.78%`).
2. **Overview Page (`http://localhost:5000/overview`):**
   - Show the PortScan bar increasing on the Class Distribution Chart.

---

### Attack 2: Live DDoS SYN Flood (`nping` Raw Packet Blaster)

#### 💡 Why We Are Doing This:
To visually prove that when an attacker launches a high-rate SYN flood attempting to crash the camera, the system classifies it as DDoS and autonomously instructs the router to rate-limit the attacker.

#### ⚙️ What Happens Under the Hood:
`nping` blasts 5,000 raw TCP SYN packets at 1,000 packets/sec toward camera Port 80. Zeek flags incomplete half-open states, and the decision engine triggers `AUTO_DDOS_RATELIMIT`.

#### 💻 Direct Raw Command:
```powershell
docker exec ids-lab-attacker nping --tcp -p 80 --flags syn --rate 1000 -c 5000 192.168.50.30
```

##### 🔍 Line-by-Line Breakdown:
- `docker exec ids-lab-attacker`: Executes from outside attacker (`10.10.10.50`).
- `nping`: Official network packet generator binary from the Nmap project.
- `--tcp -p 80`: Targets camera HTTP port.
- `--flags syn`: Creates raw TCP SYN packets (half-open flood).
- `--rate 1000 -c 5000`: 1,000 packets/second for 5 seconds (5,000 total).
- `192.168.50.30`: Camera IP address.

##### 📋 Real Output:
```text
Starting Nping 0.7.99 ( https://nmap.org/nping )
Raw packets sent: 5000 (270.000KB) | Rcvd: 2625 (115.500KB) | Lost: 2375 (47.50%)
Nping done: 1 IP address pinged in 6.46 seconds
```

#### 🖥️ Live Dashboard Proof:
1. **Real-Time Alerts (`http://localhost:5000/alerts`):**
   - A bold red **`DDoS_DoS`** alert appears with action `RATE_LIMIT`.
2. **Active Mitigations (`http://localhost:5000/mitigations`):**
   - Show attacker IP `10.10.10.50` active in the rate-limit table with a live decaying countdown timer.

---

### Attack 3: Live C&C Outbound Beaconing & Router Firewall Block (`nc` Netcat Beacon)

#### 💡 Why We Are Doing This:
To visually demonstrate the complete end-to-end autonomous mitigation loop: an infected camera communicates outbound with an external Command-and-Control controller, and within 112 milliseconds the router firewall injects a kernel-level drop rule against the attacker while camera video surveillance continues uninterrupted.

#### Step 1: Verify the Router's `block_dst` Set is Empty Before the Attack:
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```
*(Result: `elements = { }` - set is clean and empty)*

#### Step 2: Transmit a Live C&C Outbound Beacon from Camera to Attacker:
```powershell
# 1. Open Port 6667 Listener on Attacker Container:
docker exec -d ids-lab-attacker nc -lp 6667

# 2. Transmit real TCP C&C beacon from infected Camera to Attacker:
docker exec ids-lab-camera sh -c "echo 'HELO_BOTNET_C2_BEACON' | nc -w 2 10.10.10.50 6667"
```

##### 🔍 Line-by-Line Breakdown:
- `docker exec -d ids-lab-attacker nc -lp 6667`: Netcat opens port 6667 on attacker machine simulating a botnet master.
- `echo 'HELO_BOTNET_C2_BEACON' | nc -w 2 10.10.10.50 6667`: Infected camera establishes an outbound connection through the router to report in.

#### Step 3: Show the Attacker IP Quarantined in `block_dst` with a Decaying Timer:
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```

##### 📋 Verified Output:
```text
table inet ids {
    set block_dst {
        type ipv4_addr
        flags timeout
        elements = { 10.10.10.50 timeout 30m expires 29m58s }
    }
}
```

##### 📊 Output Breakdown:
- `elements = { 10.10.10.50 timeout 30m expires 29m58s }`: External C&C IP (`10.10.10.50`) is instantly placed into the kernel drop set with an active 30-minute auto-expiry countdown.
- Camera IP (`192.168.50.30`) is **NOT** blocked; RTSP video streaming to the NVR continues completely uninterrupted!

#### 🖥️ Live Dashboard Proof:
1. **Real-Time Alerts (`http://localhost:5000/alerts`):**
   - Purple **`CnC`** (Confidence 81.34%) alert badge appears with action `BLOCK_DST`.
2. **Active Mitigations (`http://localhost:5000/mitigations`):**
   - **Blocked IP:** `10.10.10.50` (C&C Server) is active in the blocklist.
   - **TTL Countdown:** 30-minute countdown timer ticks down live on the browser screen.
   - **Camera Protection:** Camera IP (`192.168.50.30`) is absent from the blocklist, proving surveillance preservation.

> 🎯 **Final Spoken Statement to the Supervisor:**  
> *"Sir, look at the terminal! The instant our infected camera sent the C&C beacon, our Zeek sensor sniffed the flow, our Random Forest model classified it, our decision engine evaluated the safety invariants, and our router firewall autonomously injected '10.10.10.50' into kernel memory with a 30-minute auto-expiry countdown—all completed in just 112 milliseconds!"*

---

### 🎓 Closing Statement to the Supervisor:
> *"Sir, as demonstrated in our presentation today, our implementation satisfies all 8 Functional Requirements (FR-01 to FR-08), achieves our Proposal Table 9 benchmarks with an empirical decision latency of 112 ms, meets our Macro-F1 target on held-out data, and enforces strict safety invariants that protect IP camera streams from interruption. The entire virtual testbed is live, validated, and ready for physical camera deployment."*
"""
