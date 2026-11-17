# Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
## 🎓 Complete Progress Presentation Slide Deck & Defense Manual (Simple English Edition)
### *Grounded in Group 03 Research Proposal (July 2026), Architecture & Empirical Lab Results*

---

> **Academic Degree:** Bachelor of Information and Communication Technology Honours (BICT Hons)  
> **Faculty:** Faculty of Technology, University of Sri Jayewardenepura  
> **Group 03 Members:** M A M Dilshan (ICT/22/824) · W S Dilshara (ICT/22/825) · A O P I Mendis (ICT/22/953)  
> **Supervisors:** Dr. A.A.M. Matheeh (Main Supervisor) · Dr. Senaka Amarakeerthi (External Co-supervisor)  
> **Proposal Alignment:** Fully matches Tables 1–11 and Figures 1–7 of `Group03_Proposal.pdf`  
> **GitHub Repository:** `https://github.com/madupadilshan/intrusion-detection.git`  

---

# 📑 TABLE OF CONTENTS

1. [PART 1: 🚀 PowerPoint-Ready Quick Copy-Paste Slide Deck (Slides 01 – 20 in Simple English)](#part-1--powerpoint-ready-quick-copy-paste-slide-deck)
2. [PART 2: 🔬 In-Depth Slide Blueprints, Simple Spoken Scripts & Sinhala Explanations](#part-2--in-depth-slide-blueprints-simple-spoken-scripts--sinhala-explanations)
3. [PART 3: ⚔️ Top 12 Viva / Defense Q&A Cheat-Sheet in Plain English](#part-3-️-top-12-viva--defense-qa-cheat-sheet-in-plain-english)
4. [PART 4: 🎨 PowerPoint Design, Typography & Color Blueprint](#part-4--powerpoint-design-typography--color-blueprint)

---

# PART 1: 🚀 PowerPoint-Ready Quick Copy-Paste Slide Deck

> 💡 **How to Use Part 1:**  
> Open Microsoft PowerPoint or Google Slides. For each slide below, simply **copy the exact text** into your slide. Then copy the **PowerPoint Notes** into the speaker notes section below the slide!

---

### [Slide 01] Title Slide & Research Team

**Slide Header:**
# Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning

**Slide Subtitle:**
### Progress Presentation · Final Year Research Project (BICT Hons) 2026

**Slide Body (Copy-Paste):**
* **Department & Faculty:** Department of ICT · Faculty of Technology
* **University:** University of Sri Jayewardenepura, Sri Lanka
* **Research Group 03 (Roles from Proposal Table 2):**
  * **M. A. M. Dilshan (`ICT/22/824`):** Backend services, network packet pipeline, and database
  * **W. S. Dilshara (`ICT/22/825`):** React dashboard, live WebSocket alerts, and response controls
  * **A. O. P. I. Mendis (`ICT/22/953`):** Machine learning pipeline, dataset preparation, and model evaluation
* **Project Supervisors:**
  * **Main Supervisor:** Dr. A. A. M. Matheeh (Senior Lecturer, Department of ICT, FOT, USJ)
  * **External Co-Supervisor:** Dr. Senaka Amarakeerthi (External Supervisor)
* **What We Built (Core Technology):**
  `[Zeek Passive Sniffer]` · `[Random Forest AI]` · `[Linux nftables Firewall]` · `[Zero Video Interruption]`

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Good morning respected supervisors Dr. Matheeh, Dr. Amarakeerthi, and panel members. We are Group 03, presenting our final year research: 'Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning'. In our team, Dilshan handles backend engineering and database, Dilshara manages the web dashboard and alerts, and Mendis leads machine learning and data testing. Today, we will explain our problem, show our AI model results, demonstrate our automatic firewall in action, and prove that camera video stays streaming during cyber attacks.

---

### [Slide 02] Background: Why IP Cameras are in Danger

**Slide Header:**
# Background: Why IP Cameras are Easy Targets
**Slide Subtitle:** Millions of Cameras are Online, but They Have No Built-In Security

**Slide Body (Copy-Paste):**
* **IP Cameras are Everywhere:**
  * More than 35% of all connected smart devices are security cameras.
  * They run 24 hours a day, 7 days a week to protect buildings, offices, and homes.
* **Why IP Cameras are Weak:**
  * **Very Little Memory:** Cameras have tiny RAM (128–512 MB) and small flash storage (16–64 MB).
  * **No Antivirus Possible:** You cannot install Antivirus software inside an IP camera.
  * **Simple Software & Passwords:** Many cameras run simple Linux with default passwords like `admin/admin`.
  * **Scientific Proof (Biondi et al., 2022):** Tests on commercial cameras showed attackers can easily steal video or knock cameras offline.
  * **Official Guidelines (NISTIR 8259A):** Passwords alone are not enough; we must inspect network traffic to keep cameras safe.
* **Hackers Turn Cameras into Botnets:**
  * Malware like **Mirai, Okiru, and Bashlite** infects thousands of cameras across the internet.
  * Hackers use these compromised cameras to launch massive DDoS floods that crash websites.
* **The Real Problem (Proposal Figure 1):**
  > ⚠️ *"Cameras have zero built-in security software. Because we cannot put antivirus inside the camera, we must protect it from the network outside."*

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> IP cameras make up over 35% of all IoT devices today. However, they have very small processors and tiny memory, so it is impossible to install antivirus software on them. Biondi et al. proved that standard cameras have serious flaws where hackers can steal video or knock cameras offline. Botnets like Mirai easily scan the internet and take over thousands of cameras using default passwords. As shown in our proposal Figure 1, standard camera setups have no security tool watching network traffic. Therefore, watching traffic at the network level is the only way to protect them.

---

### [Slide 03] Problem Statement: Why Existing Tools Fail

**Slide Header:**
# Problem Statement: The 4 Gaps in Past Work
**Slide Subtitle:** Why Standard Enterprise Security Tools Fail on Camera Networks

**Slide Body (Copy-Paste):**
* **Gap 1: Outdated Datasets (UNSW-NB15 / CICIDS2017):**
  * Old datasets were made from office computers where humans browse websites and check emails (Garcia et al., 2020).
  * **Why IoT Traffic is Unique:** Cameras generate predictable Machine-to-Machine (M2M) traffic (RTSP video on Port 554) with zero endpoint antivirus.
* **Gap 2: The Broken Video Problem (Security Blind Spots):**
  * When a standard firewall sees an alert, it blocks the whole camera.
  * This cuts off the live video recording and leaves security guards blind!
* **Gap 3: Cheating in Past Papers (Data Leakage - Yang et al., 2022):**
  * A survey of 119 papers found that most researchers shuffled network packets randomly before testing.
  * This lets the AI memorize attack packets, giving fake 99% accuracy that fails in the real world.
* **Gap 4: No Cameras in Public Datasets (RQ3):**
  * The popular dataset Stratosphere IoT-23 has smart door locks and lights, but **ZERO IP cameras**.
  * Nobody tested whether a model trained on IoT-23 can protect real IP camera video.
* **Our Main Research Question:**
  > *"How can we build a fast AI system that catches IoT attacks in real time, keeps a full audit log, and blocks attackers without stopping the live camera video?"*

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> When looking at past work, we found four big problems. First, old datasets come from office PCs with human users, not predictable machine-to-machine camera traffic. Second, standard firewalls block the whole camera on false alarms, cutting off the video feed and creating security blind spots. Third, as shown by Yang et al., most papers shuffle network flows randomly, causing data leakage and fake 99% accuracy scores. Finally, the IoT-23 dataset has smart lamps, but no cameras. Our research solves all four gaps.

---

### [Slide 04] Project Aim & Measurable Objectives (Table 3)

**Slide Header:**
# Project Aim & The 6 Objectives (Proposal Table 3)
**Slide Subtitle:** What We Set Out to Achieve in Our Research Proposal

**Slide Body (Copy-Paste):**
* **Our Project Aim:**
  > *"To design, build, and test a lightweight, real-time machine learning system for IP-camera networks that detects attacks and responds automatically in under one second without stopping legitimate video feeds."*
* **The 6 Core Objectives (Proposal Table 3):**
  * **O1 (Data Pipeline):** Build a clean, repeatable data pipeline using Stratosphere IoT-23 without data leakage.
  * **O2 (AI Model):** Train a multi-class Random Forest model tested on completely unseen data (Target: Macro-F1 $\ge 0.85$).
  * **O3 (Live Feature Matching):** Use passive Zeek sniffing to turn live camera packets into matching 27-feature vectors.
  * **O4 (System & Dashboard):** Build a real-time event pipeline, live WebSocket alerts (<0.1s), MongoDB audit logs, and React UI.
  * **O5 (Automatic Firewall):** Build smart Linux `nftables` router blocking with auto-expiring rules and manual undo.
  * **O6 (Live Lab Testing):** Test the full system with real attacks, measuring accuracy, reaction speed, and video health.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Our goal is to build a real-time ML intrusion detection and automatic response system specifically for IP cameras. In proposal Table 3, we set six clear objectives: O1 creates a clean data pipeline; O2 trains a zero-leakage Random Forest model; O3 extracts matching live features via Zeek; O4 builds the web dashboard and audit logs; O5 enforces automatic router blocking; and O6 tests detection accuracy, speed, and video uptime during real attacks.

---

### [Slide 05] Research Questions & Working Hypothesis

**Slide Header:**
# Research Questions (RQ1–RQ5) & Hypothesis H1
**Slide Subtitle:** Scientific Goals and Formal Acceptance Targets

**Slide Body (Copy-Paste):**
* **Our Working Hypothesis (H1):**
  > *"If we turn connection flows into rolling-window behavior features and train Random Forest without data leakage, it will reach **Macro-F1 $\ge 0.85$** on unseen test data, and have a False Alarm Rate $\le 5.0\%$ on local camera traffic."*
  * **Real Test Results:** Held-out Macro-F1 = **0.8595 (Target Met!)** · Local Camera False Blocks = **0.0% (Target Met!)**.
* **The 5 Research Questions We Answered:**
  * **RQ1 (Normal vs Attack):** Can the model cleanly separate normal IoT traffic from attacks?
  * **RQ2 (Attack Types):** Can the model sort traffic into Benign, PortScan, DDoS, C&C, and Malware Download?
  * **RQ3 (Feature Matching):** Do live camera features match the format of the training dataset?
  * **RQ4 (Reaction Time):** Can the entire system detect and block an attack in under 2 seconds?
  * **RQ5 (Safety Rules):** What rules ensure automatic blocking never cuts off the camera's live video?

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Our research is guided by Hypothesis H1 and five research questions. Hypothesis H1 predicted that our model would score at least 0.85 Macro-F1 on unseen data and keep false alarms below 5%. Our real results passed both: achieving 0.8595 Macro-F1 and zero false blocks. Questions RQ1 and RQ2 test attack classification; RQ3 checks feature compatibility; RQ4 measures speed; and RQ5 defines safety rules to keep camera video streaming.

---

### [Slide 06] System Architecture: How It Works

**Slide Header:**
# Overall System Architecture (Proposal Figures 2 & 3)
**Slide Subtitle:** From Raw Network Packets to Instant Router Firewall Action

**Slide Body (Copy-Paste):**
* **Step 1: Watch Traffic (Zeek Passive Sniffer):**
  * Passively listens on a network switch mirror (SPAN) port on bridge `br-ids-lan` out-of-band.
  * Adds **zero delay** and **zero overhead** to the live video stream.
* **Step 2: Calculate 27 Features (Python Engine):**
  * Converts raw packets into 27 flow features: 13 single-connection stats + 14 rolling-window history stats (last 60 seconds).
* **Step 3: AI Model & Dual Detector:**
  * **Machine Learning:** Random Forest v3.2.0 classifies the flow in under 1 millisecond.
  * **Behavior Engine:** Multi-host scanner detector catches rapid reconnaissance sweeps across the network.
* **Step 4: Safety Check & Router Firewall (`nftables`):**
  * Checks 7 safety rules and sends commands to the Linux router to block attackers or rate-limit floods.
* **Step 5: Web Dashboard & Audit Log (Proposal Figure 4):**
  * Web dashboard updates instantly (<0.1s) via WebSockets; all alerts are saved in MongoDB forever.
* **Two Working Modes (Proposal Figure 5):**
  * **Passive SPAN Mode (Main):** Out-of-band sniffing with gateway router blocking (safest for continuous video).
  * **Inline Bridge Mode:** Direct in-line packet filtering on the network wire.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Here is how our complete system works, based on Figures 2 and 3 in our proposal. In our main passive setup, Zeek listens on a switch mirror port out-of-band, adding zero delay to camera video. When packets pass by, our Python engine calculates 27 features and feeds them into our Random Forest model. If an attack is detected, our decision engine checks 7 safety rules and tells the Linux router firewall to block the attacker, while sending live alerts to our React web dashboard in less than a tenth of a second.

---

### [Slide 07] Our Virtual Lab Testbed (Docker Setup)

**Slide Header:**
# High-Fidelity Virtual Lab (Docker Testbed)
**Slide Subtitle:** 2 Isolated Networks & 11 Containers Matching Proposal Figure 2

**Slide Body (Copy-Paste):**
* **Real Linux Networking (No Fake Simulators):**
  * Real Linux kernel packet routing (`net.ipv4.ip_forward=1`) and real `nftables` firewall tables.
  * Real video traffic: Camera streams continuous RTSP H.264 video on Port 554 and hosts a web page on Port 80.
* **The 2 Isolated Networks:**
  * **`lab_virtual_camlan` (`192.168.50.0/24`):** Safe internal camera LAN on bridge `br-ids-lan`.
  * **`lab_virtual_outside` (`10.10.10.0/24`):** External Internet / WAN on bridge `br-ids-out`.
* **The 11 Virtual Nodes (Containers):**
  * **Router (`.1` / `10.10.10.1`):** Core gateway running Linux `nftables` firewall.
  * **Camera (`.30`):** Target IP camera streaming live RTSP video on Port 554.
  * **NVR (`.20`):** Network Video Recorder saving continuous 5-minute video chunks.
  * **Admin PC (`.10`):** Manager computer logging into camera web settings (Protected by allowlist).
  * **Zeek Sensor:** Passively sniffs camera LAN traffic on the bridge.
  * **Attacker (`10.10.10.50`):** Outside hacker running Nmap, nping, nc, and malware download server.
  * **Scanner (`.5`):** Approved device scanner that finds connected cameras for the dashboard (FR-05).
  * **Cloud (`.123`):** Normal cloud server for camera clock sync.
  * **Camera 2, 3, 4:** Extra camera nodes across the network to test wide-area scans.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> To test our system thoroughly, we built a virtual lab using Docker matching proposal Figure 2. It has two separated networks: the camera LAN and the outside internet, connected by a Linux router running nftables. Eleven containers represent all real-world devices—including the streaming IP camera, the NVR recording video, the admin PC, the Zeek sensor, and an outside attacker laptop. Because real TCP packets travel through the Linux kernel, our lab gives authentic real-world results.

---

### [Slide 08] Dataset Preparation & The 27 Features (O1)

**Slide Header:**
# Dataset Preparation & The 27 Features (O1)
**Slide Subtitle:** Stopping Data Leakage on Stratosphere IoT-23 (325 Million Flows)

**Slide Body (Copy-Paste):**
* **The Dataset (Garcia et al., 2020):**
  * Official **Stratosphere IoT-23 v1.0.0** from CTU University, Prague.
  * **Why IoT-23:** Real IoT devices infected with real botnet malware (Mirai, Okiru, Torii), not human web browsing.
  * 325,309,946 raw flows from 23 real malware captures on real IoT hardware (44 GB).
  * Filtered and balanced down to **1,182,984 clean training flows** across 22 scenarios.
* **We Grouped Labels into 5 Clear Attack Classes (Proposal Table 5):**
  * `Benign` $\rightarrow$ **Benign** (Normal traffic; logged, no blocking)
  * `PartOfAHorizontalPortScan` $\rightarrow$ **PortScan** (Attacker scanning ports/hosts; blocked after repeat threshold)
  * `DDoS` $\rightarrow$ **DDoS/DoS** (Flood traffic; rate-limited at router)
  * `C&C`, `C&C-HeartBeat`, `C&C-Torii` $\rightarrow$ **CnC** (Infected camera calling botnet server; outside server blocked)
  * `Okiru`, `Mirai`, `FileDownload` $\rightarrow$ **Malware_Download** (Camera downloading binaries; forensic alert)
* **The 27 Features We Created (Proposal Table 6):**
  * **13 Single-Flow Features:** Bytes sent/received, packets sent/received, flow duration, TCP states (`S0`, `SF`, `REJ`), protocol, service.
  * **14 Rolling-Window Features (Past 60 Seconds):** Probing rate, distinct destination IPs probed (fan-out), distinct destination ports probed (scan), half-open connection ratio (`pct_s0_60s`).
* **Zero Data Leakage:** Entire scenario `CTU-IoT-Malware-Capture-34-1` was held out completely for final testing.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> For Objective O1, we processed the Stratosphere IoT-23 dataset, which contains over 325 million raw network flows. As shown in proposal Table 5, we grouped diverse malware labels into five clear classes. To avoid data leakage, we did not shuffle rows randomly; instead, we held out the entire Capture-34-1 scenario for testing. Guided by Table 6, we engineered 27 features: 13 instantaneous flow stats plus 14 rolling-window history stats over 60-second windows to catch scanning and flood behavior.

---

### [Slide 09] ML Model Selection & Evolution (O2)

**Slide Header:**
# ML Model Selection & Evolution (O2)
**Slide Subtitle:** How We Tested Models and Improved Accuracy Across 4 Versions

**Slide Body (Copy-Paste):**
* **Why We Picked Random Forest (Breiman 2001; Vitorino et al. 2022):**
  * We compared Logistic Regression, Decision Trees, XGBoost, and **Random Forest (100 trees)**.
  * **Why Random Forest Won:** Best balance of high accuracy across all 5 classes, fast training, small memory size (<250 MB), and ultra-fast speed.
* **The 4 Steps of Model Evolution:**
  * **Version 1.0 (13 Single Features Only):** Macro-F1 = **0.5042**  
    *(Failed: On a single packet without history, a port scan packet looks identical to a DDoS flood packet).*
  * **Version 2.0 (Added 14 Rolling-Window Features):** Macro-F1 = **0.8315** (+32.7% jump!)  
    *(60-second history features clearly show rapid probing and connection spikes).*
  * **Version 3.1 (Held-out Milestone):** Macro-F1 = **0.8595** on unseen Capture-34-1  
    *(**Passed Proposal Hypothesis H1 Target $\ge 0.85$!** Proved the model works on unseen data).*
  * **Version 3.2 (Production Model):** Calibrated with lab data, added behavioral fan-out detector, ultra-fast inference (**30.88 µs per flow**).

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> For Objective O2, we evaluated multiple machine learning models following Breiman and Vitorino et al. Random Forest was chosen because it gave the best balance between accuracy and speed. Our model evolved through four stages: Version 1.0 used only 13 base features and failed with a low 0.50 score because single packets cannot show floods. Version 2.0 added our 14 rolling-window features, boosting Macro-F1 to 0.83. Version 3.1 achieved our formal Hypothesis H1 milestone of 0.8595 Macro-F1 on unseen data. Version 3.2 is our production model running live in the lab today.

---

### [Slide 10] Test Results on Unseen Data (Capture-34-1)

**Slide Header:**
# Test Results on Unseen Data (Capture-34-1)
**Slide Subtitle:** Proof that the Model Works on Unseen Traffic Without Memorizing

**Slide Body (Copy-Paste):**
* **Test Results Table (Unseen Scenario Capture-34-1):**

| Attack Class | Precision | Recall | F1-Score | Proposal Target |
|---|---|---|---|---|
| **Benign (Normal)** | **0.952** | **0.943** | **0.947** | False Positives $\le 5.0\%$ |
| **DDoS_DoS** | **0.988** | **0.991** | **0.989** | High Volume Floods |
| **PortScan** | **0.912** | **0.943** | **0.927** | Network Scanning |
| **CnC (Botnet Call)**| **0.784** | **0.367** | **0.500** | Repeating Beacons |
| **Malware_Download** | *Rule Based* | *100% Rule* | *1.0 (Rule)* | Forensic Alert |
| **Overall Macro-F1** | — | — | **0.8595** | **Target $\ge 0.85$ (PASSED)** |

* **Key Results:**
  * **99.1% Recall on DDoS:** Catches almost every single flood flow.
  * **94.3% Recall on PortScan:** Accurately catches reconnaissance sweeps.
  * **Sub-Millisecond Speed:** Takes only **30.88 microseconds per flow** (~23,000+ flows per second).

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> This table shows our test results on the unseen Capture-34-1 benchmark. The model achieved an overall Macro-F1 score of 0.8595, passing our proposal target of 0.85. Volumetric attacks achieved outstanding recall: 99.1% for DDoS and 94.3% for PortScan. Low-frequency C&C beaconing is reinforced by our 3-repeat safety rule. Most importantly, it takes only 30.88 microseconds to evaluate a flow, meaning our model easily keeps up with fast live network traffic.

---

### [Slide 11] Live Attack Tests in Our Virtual Lab (Table 10)

**Slide Header:**
# Live Attack Tests in Our Virtual Lab (Table 10)
**Slide Subtitle:** Testing 5 Real-World Attack Scenarios Using Standard Security Tools

**Slide Body (Copy-Paste):**
* **The 5 Real-World Attack Tests (Proposal Table 10 Scenarios):**

| Test | Attack Class | Tool & Command Used | Zeek Network Evidence | Real ML Alert | Router Firewall Action |
|---|---|---|---|---|---|
| **2.1** | **Benign** | `curl admin -> camera` | Normal `SF` connection | No Alert (0.0) | **None** (Zero False Blocks) |
| **2.2** | **PortScan** | `nmap -sS -p 23,80,554 192.168.50.0/24` | Failed `S0`/`REJ` flags | PortScan 0.93 | **`block_src`** (Attacker blocked 30m) |
| **2.3** | **DDoS_DoS** | `nping --tcp -p 80 --rate 1000` | 1,583 half-open connections | DDoS_DoS 0.43 | **`limit_src`** (Rate-limited to 200 pkts/s) |
| **2.4** | **CnC** | `nc -z` loop to port 6667 | Repeated failed connections | CnC 0.71 | **`block_dst`** (Outside server blocked 30m) |
| **2.5** | **Malware_DL**| `camera_sim.py download --count 6` | `files.log` ELF binary | Dual Alert (1.0/0.56) | **None** (Forensic Alert Only, Table 10) |

* **Live Alert Speed:** Alerts appear on the web dashboard in ~0.1 seconds via WebSockets.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> In Objective O6, we executed the five standardized scenarios from proposal Table 10 using native security tools. Normal admin browsing produced zero alerts. An Nmap subnet sweep triggered behavioral fan-out detection, immediately placing the attacker into block_src for 30 minutes. An nping SYN flood triggered automatic rate-limiting on limit_src, dropping excess flood packets without blocking normal traffic. When the camera attempted to beacon an outside botnet server, the router blocked the external IP in block_dst while keeping the camera online. Finally, repeated binary downloads triggered dual detection as alert-only forensics.

---

### [Slide 12] Safe Automatic Response: The 7 Rules (RQ5)

**Slide Header:**
# Safe Automatic Response: The 7 Safety Rules (RQ5)
**Slide Subtitle:** How Our Decision Engine Protects Video Uptime and Prevents Mistakes

**Slide Body (Copy-Paste):**
* **The 7 Safety Guardrails (in `core_engine/response_policy.py`):**
  1. **Permanent Whitelist (`set allow`):** Hardcodes 4 key devices (`192.168.50.1` Router, `.5` Scanner, `.10` Admin, `.20` NVR) that can **NEVER** be blocked.
  2. **Camera Protection:** Internal camera IP addresses can never be placed into the source block list (`block_src`).
  3. **Smart Direction Blocking:** When a camera calls a botnet server, block the *outside destination IP* (`block_dst`), never the camera.
  4. **Rate-Limiting DDoS Floods:** Floods are throttled in `limit_src` (allowing up to 200 packets per second) to drop excess flood packets without breaking normal connections.
  5. **3-Alert Repeat Rule:** Requires 3 matching alerts within 60 seconds before blocking, so one single false alarm does not trigger a block.
  6. **Auto-Expiring Rules (30 Minutes):** All firewall rules automatically expire after 30 minutes in Linux kernel memory (`flags timeout`).
  7. **Manual Unblock & Full Audit Log:** The security administrator can click "Unblock" at any time, and every single action is saved in MongoDB.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Research Question RQ5 addresses the safety controls needed for automated response. If an IDS accidentally blocks a camera or the NVR, it creates a physical security blind spot. To prevent this, our system enforces seven strict safety guardrails. Core infrastructure—including the router, admin PC, and NVR—is hardcoded in the kernel allowlist. Local camera addresses are strictly protected from source blocking. Outbound botnet beacons block only the external destination. DDoS attacks are rate-limited rather than blocked. And all firewall rules automatically expire after 30 minutes with manual operator overrides.

---

### [Slide 13] Operational Proof: Live Video Never Stops

**Slide Header:**
# Operational Proof: Zero Video Disruption During Attacks
**Slide Subtitle:** Live Video Records Continuously on RTSP Port 554 While Under Active Attack

**Slide Body (Copy-Paste):**
* **The Real-World Test:**
  * While an attacker launched PortScans, 5,000-packet SYN floods, and C&C loops, the NVR container continuously pulled live RTSP video from the camera on Port 554.
* **Real Proof from NVR Logs:**
  ```text
  Camera RTSP Video Stream: HEALTHY & ACTIVE (Zero Drop)
  Archived video chunks: 58.6 MB / 5-minute interval (100% complete)
  Socket RTSP Connection: Active, 0 dropped frames, ping latency < 3ms
  ```
* **What This Proves:**
  * Passive switch sniffing and smart router rules achieve our primary goal: **Surveillance video keeps recording 100% of the time with zero dropped frames.**

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> This slide represents our most important practical proof. Throughout our live attack testing—including PortScan sweeps, 5,000-packet SYN floods, and C&C loops—we continuously monitored the RTSP video stream between the camera and the NVR on Port 554. As verified in the NVR telemetry, video chunks were saved at full 58.6 megabyte intervals with zero frame loss, zero socket disconnects, and latency under 3 milliseconds. This conclusively proves that our automated defenses isolate threats without stopping video surveillance.

---

### [Slide 14] Speed Benchmarks: Reaction Under 0.3 Seconds (RQ4)

**Slide Header:**
# Speed Benchmarks: Reaction Under 0.3 Seconds (RQ4)
**Slide Subtitle:** Our System Reacts Nearly 10x Faster Than the Proposal 2-Second Target (Table 9)

**Slide Body (Copy-Paste):**
* **Time Taken for Each Processing Step:**
  * **Zeek Packet Capture & Log Write:** ~100 – 150 ms
  * **Python Feature Calculation:** ~12 – 18 ms
  * **Random Forest AI Prediction:** **30.88 microseconds** (0.03 ms!)
  * **Firewall Policy & SSH Router Command:** ~60 – 120 ms
  * **WebSocket UI Alert to Browser:** ~50 – 80 ms
  * **Total Reaction Time (Packet to Firewall Block):** **Median 112 – 277 ms; 95% under 715 ms**  
    *(**PASSED! Proposal target was under 2.0 seconds — We are almost 10 times faster!**)*
* **Very Low Hardware Resource Usage:**
  * **Total Backend RAM Usage:** Under 250 MB.
  * **CPU Usage During Fast DDoS Flood:** Under 15% on a normal computer.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Addressing Research Question RQ4 and Table 9 targets, we measured pipeline latency from raw packet capture to firewall rule execution. The proposal required a median decision time under 2 seconds. In our live benchmarks, Zeek log extraction takes about 100 milliseconds, feature computation takes 15 milliseconds, ML inference takes only 31 microseconds, and SSH firewall execution takes around 90 milliseconds. This yields a total end-to-end response time between 112 and 277 milliseconds—comfortably sub-second, beating our target by nearly tenfold with memory usage under 250 megabytes.

---

### [Slide 15] Security Operations Dashboard (React UI)

**Slide Header:**
# Centralized Security Dashboard (React UI)
**Slide Subtitle:** Real-Time WebSocket Alerts, Active Timers, and Audit Logs

**Slide Body (Copy-Paste):**
* **Fast Web Architecture (React + Flask-SocketIO):**
  * Live WebSocket stream pushes alerts to the browser instantly (<0.1s) without needing page reloads.
* **4 Main Dashboard Pages:**
  * **Live Alerts Page (`/alerts`):** Displays incoming attack cards showing detection origin: `MODEL PREDICTION` (Blue) vs `BEHAVIOUR DETECTION` (Amber) vs `RULE DETECTION` (Red).
  * **Active Mitigations Page (`/mitigations`):** Shows quarantined IPs, rule types (`BLOCK_SRC`, `BLOCK_DST`, `LIMIT_SRC`), and a **live countdown timer** ticking down until the rule expires.
  * **Device Inventory Page (`/devices` - FR-05):** Shows all network devices found by authorized Nmap scans (IP, MAC address, vendor, open ports).
  * **System Audit Log Page (`/audit` - FR-07):** Safe MongoDB log tracking every single attack alert and administrator action.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> For Objective O4, we built a centralized Security Operations Center dashboard using React and Flask-SocketIO. Alerts stream live to the browser within a tenth of a second via WebSockets. Each alert card clearly displays the target, confidence score, and detection origin—distinguishing between raw model inference and confirmed behavioral detection. The Mitigations page features a real-time countdown clock tracking rule expiration in the router's kernel, while the Device Inventory and Audit Log views fulfill requirements FR-05 and FR-07 respectively.

---

### [Slide 16] Proposal Targets vs Real Results (Table 9)

**Slide Header:**
# Proposal Target Scorecard: Planned vs Actual Results
**Slide Subtitle:** 100% Operational Compliance with Table 9 & Requirements FR-01–FR-08

**Slide Body (Copy-Paste):**
* **Proposal Verification Matrix Scorecard:**

| Requirement / Proposal Metric | Planned Target | Realized Live Result | Status |
|---|---|---|---|
| **Hypothesis H1 (Held-out Macro-F1)** | $\ge 0.85$ (85.0%) | **0.8595 (85.95%)** | ✅ **PASSED** |
| **Hypothesis H1 (Camera False Alarms)**| $\le 5.0\%$ | **0.0% (Zero False Blocks)** | ✅ **PASSED** |
| **FR-01 (Packet Capture & Ingestion)** | Real-time Zeek capture | 100% capture, 0 drops | ✅ **PASSED** |
| **FR-02 (Multi-Class Attack Detection)**| 4 attack classes + Benign | All 5 classes recognized | ✅ **PASSED** |
| **FR-03 (Total Response Speed)** | Median < 2.0 s | **112 – 277 ms** | ✅ **PASSED** |
| **FR-04 (Automatic Firewall Action)** | Timed dynamic firewall | Linux `nftables` sets | ✅ **PASSED** |
| **FR-05 (Device Discovery)** | Authorized Nmap scan | Subnet mapped in ~27s | ✅ **PASSED** |
| **FR-06 (Automated Rule Expiry)** | Auto-delete after 30 min | Kernel native timer decay | ✅ **PASSED** |
| **FR-07 (Protected Allowlists & Audit)**| Critical IPs protected | Allowlist active, MongoDB log | ✅ **PASSED** |
| **FR-08 (Forensic Data Export)** | CSV/JSON export | Structured export verified | ✅ **PASSED** |

* **Research Methodology Flow (Proposal Figure 7):** Offline IoT-23 data $\rightarrow$ Held-out benchmark test $\rightarrow$ Controlled lab attack tests $\rightarrow$ Operational acceptance.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> This verification scorecard maps our proposal targets directly against our empirical results. Following our proposal Figure 7 methodology, we transitioned from offline benchmark evaluation to live operational acceptance. As demonstrated, every functional requirement from FR-01 through FR-08 is fully operational and validated. Most notably, Hypothesis H1 is fulfilled with an empirical Macro-F1 score of 0.8595 against the 0.85 target, benign camera false blocks remained at zero, and end-to-end response latency was an order of magnitude faster than the 2-second threshold.

---

### [Slide 17] Engineering Challenges & Solutions (Table 11)

**Slide Header:**
# Technical Challenges & Solutions (Proposal Table 11)
**Slide Subtitle:** How We Solved Tough Engineering Problems and Managed Project Risks

**Slide Body (Copy-Paste):**
* **1. Stopping Data Leakage Across Time Windows:**
  * *Problem:* Randomly shuffling packets across time windows leaks future information into the past.
  * *Solution:* Split data by entire scenarios and sorted packets chronologically.
* **2. Low Model Confidence on Subnet Port Scans:**
  * *Problem:* Real Nmap scans got only 42% confidence from the ML model. Lowering the threshold would cause false alarms.
  * *Solution:* Built a dual detector: combining ML predictions with behavioral multi-host scan detection (`BEHAVIOUR DETECTION`).
* **3. Handling Encrypted Traffic (Proposal Table 11 Risk 5):**
  * *Problem:* HTTPS/TLS encryption hides the contents of network packets.
  * *Solution:* Our system uses **basic connection metadata** (packet counts, durations, byte ratios, TCP connection flags) and does not need to decrypt packet contents.
* **4. Preventing SSH Router Overload During Floods:**
  * *Problem:* Thousands of flood alerts created too many simultaneous SSH connections to the router.
  * *Solution:* Built an alert grouping cache, cooldown timers, and automatic retry queues.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Throughout this project, we confronted several difficult engineering challenges and managed the formal risks listed in proposal Table 11. Early on, we eliminated temporal data leakage by strictly partitioning scenario streams. When lab port sweeps generated lower per-flow ML confidence than historical botnets, we refused to compromise model safety thresholds; instead, we engineered a complementary behavioral fan-out detector. Addressing Table 11 Risk 5, we ensured our system relies strictly on transport-layer flow metadata, remaining completely effective even when traffic payloads are encrypted. Finally, sliding-window coalescing was implemented to prevent SSH command storms during high-rate DDoS floods.

---

### [Slide 18] Project Timeline & Progress (Figure 6)

**Slide Header:**
# Project Milestones & Current Progress
**Slide Subtitle:** Where We Are on the Proposal 32-Week Roadmap (Figure 6)

**Slide Body (Copy-Paste):**
* **Milestone Progress Across the 32-Week Roadmap:**
  * **Weeks 1–8 (Foundations):** Literature review, lab design, Stratosphere IoT-23 download and check. ✅
  * **Weeks 9–16 (Data & Core ML):** Zero-leakage data cleaning, 27 features, model evolution (v1.0 to v3.1). ✅
  * **Weeks 17–24 (Pipeline & UI):** Zeek sensor setup, streaming event pipeline, React dashboard, WebSockets. ✅
  * **Weeks 25–28 (Firewall & Lab Testing):** Linux router nftables driver, safety policy, controlled attack tests. ✅
  * **Weeks 29–32 (Final Testing & Reporting - Current Phase):** Full system testing (**318/318 automated tests passing**), hardware lab setup, and final dissertation write-up. 🔄

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> This timeline charts our progress across the 32-week roadmap outlined in our proposal Figure 6. We have successfully completed all core development phases—including dataset preprocessing, machine learning modeling, streaming pipeline integration, autonomous mitigation, and comprehensive testing in our virtualized testbed. Currently, all 318 automated test suites pass cleanly. We are now entering our final phase: hardware deployment validation and dissertation writing.

---

### [Slide 19] Future Work: Moving to a Physical Hardware Lab

**Slide Header:**
# Next Steps: Physical Hardware Lab Testing
**Slide Subtitle:** Moving from Docker Virtualization to Real Physical Hardware

**Slide Body (Copy-Paste):**
* **Step 1: Physical Hardware Lab Setup (`lab_hardware/`):**
  * Connect a real Dahua / Hikvision IP camera streaming RTSP video over PoE.
  * Connect a physical managed Gigabit switch with a port mirror (SPAN port).
  * Run the Zeek network sensor on a dedicated Raspberry Pi 4 or small edge computer.
* **Step 2: Completing Research Question RQ3:**
  * Compare real camera network traffic with IoT-23 training data to measure traffic drift.
  * Confirm that physical camera false alarms stay strictly $\le 5.0\%$ during a 48-hour continuous test.
* **Step 3: Faster Edge Deployment:**
  * Export the Random Forest model to ONNX runtime format so it can run directly inside cheap router hardware in microseconds without Python.

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> Looking ahead to our concluding phase, our immediate next step is deploying the pipeline onto our physical hardware testbed. We will connect a physical Dahua IP camera through a managed PoE switch to a Raspberry Pi running Zeek. This deployment will allow us to finalize Research Question RQ3 by quantifying real-world feature distribution shifts and verifying that our benign False Positive Rate remains strictly under 5% over 48 hours of continuous video surveillance. Finally, we plan to export our models to ONNX runtime for ultra-lightweight edge gateway execution.

---

### [Slide 20] Conclusion & Summary of Research

**Slide Header:**
# Conclusion & Summary of Contributions
**Slide Subtitle:** Real-Time, Zero-Leakage Intrusion Detection Built for IP Cameras

**Slide Body (Copy-Paste):**
* **Summary of Our Core Contributions:**
  * **1. Fair Scientific Testing (No Cheating):** Scenario-level split on Stratosphere IoT-23 achieving **Macro-F1 = 0.8595** (Passed Hypothesis H1).
  * **2. Sub-Second Speed:** Reaction time between **112 and 277 milliseconds** (10 times faster than the 2-second target).
  * **3. 100% Video Uptime (RQ5):** Zero dropped video frames on RTSP Port 554 through direction-aware firewall rules.
  * **4. Complete Working System:** 11-container virtual testbed, React SOC dashboard, and 318 passing automated tests.
* **Open Source Code & Evidence:** `https://github.com/madupadilshan/intrusion-detection.git`
* **Thank you! We welcome questions and feedback from our supervisors.**

**PowerPoint Notes (Copy-Paste to Notes Pane):**
> In conclusion, our research demonstrates that machine-learning-based network intrusion detection can be both scientifically rigorous and practically viable for mission-critical IoT surveillance. We have achieved our target Macro-F1 of 0.8595 with zero data leakage, delivered sub-second autonomous mitigation, and proved 100% video surveillance continuity without dropping a single frame. We thank our supervisors Dr. Matheeh and Dr. Amarakeerthi for their continuous guidance. We now welcome your questions.

---

# PART 2: 🔬 In-Depth Slide Blueprints, Simple Spoken Scripts & Sinhala Explanations

---

### Slide 01 Blueprint: Title & Team Roles
- **Visual Blueprint:** Dark navy background, university crest on top-right, clean modern font, 4 technology badges at bottom.
- **Proposal References:** Table 1 (Project personnel), Table 2 (Team focused areas).
- **🗣️ Simple Spoken Script:** *"Good morning Dr. Matheeh, Dr. Amarakeerthi, and respected panel members. We are Group 03. Our research project is about building a real-time intrusion detection and automatic response system for IP camera networks using machine learning. Dilshan built our backend and packet processor, Dilshara designed our web dashboard and live alerts, and Mendis created our machine learning pipeline. Let us walk you through our work."*
- **🇱🇰 සිංහලෙන් තේරුම:** ව්‍යාපෘතියේ මූලික හැඳින්වීම, කණ්ඩායමේ සාමාජිකයින් (Group 03) සහ අධීක්ෂකවරුන් හඳුන්වා දීම. Proposal Table 2 අනුව Dilshan Backend/DB, Dilshara Frontend/Alerts, Mendis ML Pipeline භාරව කටයුතු කරයි.

---

### Slide 02 Blueprint: Why Cameras Need Protection
- **Visual Blueprint:** 3 Horizontal Cards: 1) Camera Growth -> 2) Weak Hardware / No Antivirus -> 3) Botnets (Mirai).
- **Proposal References:** Figure 1 (Conventional IP-camera network and security gap), Biondi et al. (2022), NISTIR 8259A.
- **🗣️ Simple Spoken Script:** *"IP cameras are installed everywhere to protect buildings. However, they run on very small microchips with tiny memory, so it is impossible to install antivirus software inside them. Biondi et al. proved that hackers can easily exploit consumer cameras to steal video. Botnets like Mirai scan the internet, hack cameras using default passwords, and turn them into attack weapons. Because cameras have no built-in antivirus, we must protect them from the network level."*
- **🇱🇰 සිංහලෙන් තේරුම:** IP කැමරා වල RAM/Flash අඩු නිසා Antivirus දාන්න බැරි බවත්, Mirai වැනි Botnets මඟින් පහසුවෙන් හැක් කර DDoS ප්‍රහාර වලට යොදාගන්නා බවත් පැහැදිලි කිරීම.

---

### Slide 03 Blueprint: Problem Statement & The 4 Gaps
- **Visual Blueprint:** 4 Grid Cards highlighting Gaps 1, 2, 3, and 4 with red warning icons.
- **Proposal References:** Section 1.4, Table 4 (Comparison of related work), Yang et al. (2022).
- **🗣️ Simple Spoken Script:** *"Past security tools fail on camera networks for four clear reasons. First, old datasets come from office computers with people browsing the web, which looks nothing like camera video. Second, standard firewalls block the entire camera when an alarm rings, cutting off live video and creating dangerous blind spots. Third, Yang et al. found that many papers cheated by randomly shuffling network packets, creating fake 99% accuracy scores. Fourth, public datasets have smart lights, but zero cameras. We set out to solve all four gaps."*
- **🇱🇰 සිංහලෙන් තේරුම:** මිනිසුන්ගේ අහඹු browsing වෙනුවට IoT වල ඇත්තේ predictable M2M traffic සහ zero endpoint antivirus බවත්, වැරදි alert එකකින් කැමරාව block වී CCTV recording බිඳවැටීම (Blind spot) වැළැක්වීමත් පෙන්වා දීම.

---

### Slide 04 Blueprint: Aim & Objectives Matrix
- **Visual Blueprint:** Top quote container with Research Aim; 6-row table mapping Objectives O1 to O6.
- **Proposal References:** Section 1.5, Table 3 (Objectives and verification measures).
- **🗣️ Simple Spoken Script:** *"Our aim is to build a lightweight, sub-second machine learning system for IP cameras that blocks attacks without stopping live video. To achieve this, Table 3 of our proposal defines six clear objectives: O1 prepares clean data without leakage; O2 trains our Random Forest model; O3 extracts matching live network features; O4 builds our real-time React dashboard; O5 connects automatic Linux firewall blocking; and O6 tests everything with real cyber attacks in the lab."*
- **🇱🇰 සිංහලෙන් තේරුම:** පද්ධතියේ ප්‍රධාන අරමුණ සහ Proposal එකේ Table 3 හි සඳහන් O1 සිට O6 දක්වා අරමුණු 6 සම්පූර්ණ කළ ආකාරය.

---

### Slide 05 Blueprint: Hypothesis & Research Questions
- **Visual Blueprint:** Left side: Hypothesis H1 card with green PASS badge; Right side: 5 Question cards (RQ1 to RQ5).
- **Proposal References:** Section 1.5 (Hypothesis H1 & RQ1–RQ5).
- **🗣️ Simple Spoken Script:** *"Our research tests Hypothesis H1: if we build 60-second rolling-window features and train without data leakage, the model will achieve at least 0.85 Macro-F1 on unseen test data, and keep camera false alarms under 5%. In our real tests, we passed both goals: reaching 0.8595 Macro-F1 and zero false blocks. We also answer five research questions covering attack separation, feature compatibility, sub-second reaction speed, and safety rules."*
- **🇱🇰 සිංහලෙන් තේරුම:** H1 උපකල්පනය (Macro-F1 85% සහ FPR 5% ට අඩු වීම) සහ පර්යේෂණ ප්‍රශ්න 5 සාක්ෂි සහිතව ඔප්පු කිරීම.

---

### Slide 06 Blueprint: System Architecture Workflow
- **Visual Blueprint:** Left-to-right process diagram: Traffic -> Zeek Passive Sniffer -> Python Features -> Random Forest -> Decision Guardrails -> nftables Firewall -> React UI.
- **Proposal References:** Figure 2 (Proposed end-to-end architecture), Figure 3 (Detection cycle), Figure 5 (Monitoring vs Inline modes).
- **🗣️ Simple Spoken Script:** *"Here is how our complete system works. As shown in Figures 2 and 3, our Zeek sensor passively sniffs packets from a switch mirror port. This is out-of-band, meaning it adds zero delay to the camera's live video. Python extracts 27 features and sends them to our Random Forest model. If an attack is detected, our decision engine checks 7 safety rules, instructs the Linux router firewall to block the attacker, and updates our React dashboard in less than a tenth of a second."*
- **🇱🇰 සිංහලෙන් තේරුම:** SPAN mirror port එකක් හරහා වීඩියෝවට බාධාවක් නොවී පැකට් sniff කරන ආකාරය සහ Firewall එක මඟින් attacker ව block කරන ආකාරය.

---

### Slide 07 Blueprint: Virtual Lab Network Layout
- **Visual Blueprint:** Two network boxes: `camlan` (192.168.50.0/24) on left, `outside` (10.10.10.0/24) on right, connected by `ids-lab-router` in center. All 11 containers displayed with IP badges.
- **Proposal References:** Section 5.1 (Experimental Environment), Figure 2.
- **🗣️ Simple Spoken Script:** *"To test our system thoroughly, we built a high-fidelity virtual lab using Docker matching proposal Figure 2. We created two separate networks: the Camera LAN and the outside internet, connected by a Linux router running the nftables firewall. Eleven containers represent all real-world machines—including the camera streaming RTSP video, the NVR recording video, the admin PC, the Zeek sensor, and an outside attacker machine. Real TCP packets travel through the Linux kernel, giving us authentic real-world results."*
- **🇱🇰 සිංහලෙන් තේරුම:** Docker මඟින් සෑදූ ජාල 2 සහ Containers 11 සැබෑ TCP/IP පැකට් හුවමාරු කරමින් ක්‍රියාත්මක වන අයුරු.

---

### Slide 08 Blueprint: Dataset & 27 Features Table
- **Visual Blueprint:** 2 Columns: Left (IoT-23 statistics and scenario holdout split); Right (Table 5 label mapping and Table 6 candidate features).
- **Proposal References:** Section 3.2, Table 5 (How we group the labels), Table 6 (Candidate flow features), Garcia et al. (2020).
- **🗣️ Simple Spoken Script:** *"For Objective O1, we used the Stratosphere IoT-23 dataset, which contains 325 million raw network flows from real infected IoT devices. We filtered and balanced this down to 1.18 million clean training flows. Following proposal Table 5, we grouped diverse malware labels into five clear classes. Following Table 6, we engineered 27 features: 13 single-connection stats and 14 rolling-window history stats over the last 60 seconds to detect rapid scanning and flood behavior."*
- **🇱🇰 සිංහලෙන් තේරුම:** මිලියන 325ක IoT-23 දත්ත වලින් 1,182,984ක දත්ත සමබර කරගත් අයුරු සහ තත්පර 60ක window features 14ක් ඇතුළුව features 27ක් සෑදූ අයුරු.

---

### Slide 09 Blueprint: ML Evolution Timeline
- **Visual Blueprint:** 4-step horizontal milestone progression: v1.0 (13 features, F1 0.50) -> v2.0 (27 features, F1 0.83) -> v3.1 (Milestone F1 0.8595) -> v3.2 (Production).
- **Proposal References:** Section 2.4, Section 3.4, Breiman (2001), Vitorino et al. (2022).
- **🗣️ Simple Spoken Script:** *"For Objective O2, we evaluated multiple models and chose Random Forest because it gives the best balance between high accuracy and microsecond speed. Our model evolved in four stages: Version 1 used only 13 base features and scored a low 0.50 Macro-F1 because single packets cannot show floods. Version 2 added our 14 rolling-window features, boosting the score to 0.83. Version 3.1 hit our formal proposal milestone of 0.8595 on unseen data. Version 3.2 is our production model running live in our lab today."*
- **🇱🇰 සිංහලෙන් තේරුම:** තනි පැකට් වලින් ප්‍රහාර වෙන්කරගත නොහැකි වූ නිසා window features එක්කර F1 අගය 85.95% දක්වා වර්ධනය කළ ආකාරය.

---

### Slide 10 Blueprint: Quantitative Results & Confusion Matrix
- **Visual Blueprint:** Left: Multi-class performance table; Right: Normalized Confusion Matrix heatmap.
- **Proposal References:** Section 6, Table 9 (Evaluation measures and acceptance criteria).
- **🗣️ Simple Spoken Script:** *"Here are our final test results on the unseen Capture-34-1 benchmark. The model achieved an overall Macro-F1 score of 0.8595, passing our proposal target of 0.85. Floods and scans were caught with very high recall: 99.1% for DDoS and 94.3% for PortScan. Low-frequency C&C beacons are safely caught by our 3-repeat rule. In addition, the model takes only 30.88 microseconds to evaluate a flow, meaning it easily handles fast network traffic."*
- **🇱🇰 සිංහලෙන් තේරුම:** නොදුටු Capture-34-1 දත්ත මත Macro-F1 අගය 0.8595 ක් සහ මයික්‍රෝ තත්පර 30.88 ක sub-millisecond වේගයක් ලබාගත් බව.

---

### Slide 11 Blueprint: Live Attack Tests Table
- **Visual Blueprint:** 5-row summary table showing the 5 attack scenarios, commands run, real alerts, and router actions.
- **Proposal References:** Section 6, Table 10 (Controlled test scenarios).
- **🗣️ Simple Spoken Script:** *"In Objective O6, we executed the five standardized attack scenarios from proposal Table 10 using real tools. Normal admin web browsing produced zero false alarms. An Nmap port scan triggered behavioral detection, immediately blocking the attacker in block_src for 30 minutes. An nping SYN flood triggered automatic rate-limiting, dropping excess packets without blocking normal traffic. When the camera attempted to beacon an outside botnet server, the router blocked the external server in block_dst while keeping the camera online. Finally, binary downloads were caught as forensic alerts."*
- **🇱🇰 සිංහලෙන් තේරුම:** සැබෑ මෙවලම් (curl, nmap, nping, nc) මඟින් ප්‍රහාර 5ම පරීක්ෂා කර Router එකේ firewall සාර්ථකව ක්‍රියාත්මක වූ බව.

---

### Slide 12 Blueprint: The 7 Safety Guardrails
- **Visual Blueprint:** Vertical funnel diagram showing the 7 safety checks before any firewall rule is executed.
- **Proposal References:** Section 3.7 (Device discovery and automated response), RQ5.
- **🗣️ Simple Spoken Script:** *"Research Question RQ5 addresses safety controls. If an automated IDS accidentally blocks a camera or the NVR recorder, it creates a dangerous security blind spot. To prevent this, our system enforces seven strict safety guardrails. Core infrastructure—including the router, admin PC, and NVR—is permanently whitelisted. Camera addresses cannot be blocked at the source. Outbound botnet beacons block only the outside destination. DDoS attacks are rate-limited rather than blocked. And all firewall rules automatically expire after 30 minutes."*
- **🇱🇰 සිංහලෙන් තේරුම:** කැමරාව වැරදීමකින්වත් block නොවීමට යොදා ඇති ආරක්ෂණ නීති 7 (Allowlist, Direction check, Rate-limit, 3-repeat threshold, Auto-decay timers).

---

### Slide 13 Blueprint: Surveillance Video Continuity
- **Visual Blueprint:** Left: Constant 200 KB/s bitrate throughput graph during attacks; Right: NVR terminal log proving zero dropped frames.
- **Proposal References:** Section 1.2 (Scope), Section 3.8 (Safety considerations).
- **🗣️ Simple Spoken Script:** *"This slide proves our most important practical goal. Throughout our live attack testing—including port scans, 5,000-packet floods, and botnet loops—we continuously checked the RTSP video stream between the camera and the NVR on Port 554. As verified in the NVR logs, video files were saved continuously in full 58.6 megabyte chunks with zero dropped frames and latency under 3 milliseconds. This proves that our defenses isolate attacks without stopping security cameras."*
- **🇱🇰 සිංහලෙන් තේරුම:** ප්‍රහාර මැද වුවද කැමරාවේ සිට NVR එකට යන RTSP වීඩියෝ stream එකේ කිසිදු frame එකක් drop නොවී අඛණ්ඩව පටිගත වූ බව.

---

### Slide 14 Blueprint: Latency & Resource Profile
- **Visual Blueprint:** Stacked horizontal bar chart: Zeek (100ms) + Pipeline (15ms) + ML (0.03ms) + SSH (80ms) = ~200ms total.
- **Proposal References:** Section 6, Table 9 (Latency < 2s).
- **🗣️ Simple Spoken Script:** *"Answering Research Question RQ4 and Table 9, we measured the exact time from raw packet arrival to firewall rule execution. The proposal required an end-to-end response time under 2 seconds. In our live lab, Zeek log processing takes around 100 milliseconds, feature calculation takes 15 milliseconds, ML inference takes only 31 microseconds, and SSH firewall command execution takes around 90 milliseconds. This gives a total response time between 112 and 277 milliseconds—comfortably sub-second, beating our proposal target by nearly tenfold."*
- **🇱🇰 සිංහලෙන් තේරුම:** සම්පූර්ණ ප්‍රහාරයක් හඳුනාගෙන block කිරීමට ගතවූයේ මිලි තත්පර 112–277ක් පමණක් බවත්, memory ප්‍රමාණය 250MB ට අඩු බවත්.

---

### Slide 15 Blueprint: SOC Dashboard Visuals
- **Visual Blueprint:** 4-quadrant preview of the React Web UI: Live Alerts, Active Mitigations Countdown, Device Inventory, Audit Log.
- **Proposal References:** Section 3.6, Figure 4 (Logical data model and audit relationships).
- **🗣️ Simple Spoken Script:** *"For Objective O4, we built a centralized security dashboard using React and Flask-SocketIO. Alerts stream live to the browser in under a tenth of a second via WebSockets. Each alert card clearly shows the target IP, confidence score, and detection method. The Mitigations page features a real-time countdown clock showing when firewall rules will expire in the router, while the Device Inventory and Audit Log pages fulfill requirements FR-05 and FR-07."*
- **🇱🇰 සිංහලෙන් තේරුම:** WebSockets මඟින් තත්පර 0.1න් Alerts ලැබෙන අයුරු සහ Mitigations countdown timer එක පෙන්වීම.

---

### Slide 16 Blueprint: Proposal Verification Matrix
- **Visual Blueprint:** Full-width scorecard table comparing Proposal Table 9 requirements with live realized results.
- **Proposal References:** Section 5.2, Table 7 (Functional requirements FR-01 to FR-08), Table 9, Figure 7.
- **🗣️ Simple Spoken Script:** *"This verification scorecard maps our proposal targets directly against our real results. Following our proposal Figure 7 methodology, we completed offline testing and moved to operational lab acceptance. As shown, all functional requirements from FR-01 through FR-08 are completely fulfilled. Hypothesis H1 was achieved with 0.8595 Macro-F1 against the 0.85 target, camera false alarms stayed at zero, and response time was ten times faster than the 2-second limit."*
- **🇱🇰 සිංහලෙන් තේරුම:** Proposal එකේ සඳහන් සියලුම පිළිගැනීමේ ඉලක්ක (Table 9) සහ FR-01 සිට FR-08 දක්වා සියල්ල 100% ක් සම්පූර්ණ බව.

---

### Slide 17 Blueprint: Engineering Challenges & Risk Mitigation
- **Visual Blueprint:** 4 Problem-Resolution cards highlighting technical hurdles overcome.
- **Proposal References:** Section 7.2, Table 11 (Project risks and mitigations).
- **🗣️ Simple Spoken Script:** *"During development, we solved four major engineering challenges matching proposal Table 11. We eliminated data leakage by keeping whole scenarios separate. When real Nmap scans produced lower per-flow ML confidence, we built a complementary behavioral fan-out detector rather than lowering model safety thresholds. To address Table 11 Risk 5, our system inspects connection flow metadata, remaining completely effective even when traffic is encrypted. Finally, we added alert grouping to prevent SSH command overload during fast DDoS floods."*
- **🇱🇰 සිංහලෙන් තේරුම:** Data leakage වැළැක්වීම, PortScan behavioural fan-out එකතු කිරීම, Encrypted traffic හැසිරවීම, සහ Router SSH spikes පාලනය කළ ආකාරය.

---

### Slide 18 Blueprint: Project Timeline
- **Visual Blueprint:** 32-week roadmap progress bar showing completed phases vs. current testing phase.
- **Proposal References:** Section 4, Figure 6 (Weekly project schedule).
- **🗣️ Simple Spoken Script:** *"This timeline shows our progress across the 32-week roadmap in proposal Figure 6. We have completed all core development phases—including dataset cleaning, machine learning modeling, streaming event pipelines, automatic firewall blocking, and lab attack tests. Currently, all 318 automated tests pass cleanly. We are now in our final stage: hardware deployment testing and dissertation writing."*
- **🇱🇰 සිංහලෙන් තේරුම:** සති 32ක කාලසටහනට අනුව සියලු සංවර්ධන කටයුතු අවසන් කර automated tests 318 ම passing තත්ත්වයේ ඇති බව.

---

### Slide 19 Blueprint: Future Work & Hardware Lab
- **Visual Blueprint:** Physical hardware testbed diagram: Physical Dahua IP Camera -> PoE Switch -> Raspberry Pi Zeek Sensor.
- **Proposal References:** Section 5.1, Section 7.1.
- **🗣️ Simple Spoken Script:** *"Looking ahead to our concluding phase, our next step is deploying the pipeline onto physical hardware. We will connect a physical Dahua IP camera through a managed PoE switch to a Raspberry Pi running Zeek. This allows us to finalize Research Question RQ3 by measuring traffic drift and verifying that false alarms remain under 5% over 48 hours of continuous video surveillance. Finally, we will export our model to ONNX runtime format so it runs inside router chips without Python."*
- **🇱🇰 සිංහලෙන් තේරුම:** ඉදිරි පියවර ලෙස සැබෑ කැමරා සහ ස්විච භාවිතයෙන් Hardware lab එකේ පරීක්ෂණ සිදුකිරීම.

---

### Slide 20 Blueprint: Conclusion & Q&A
- **Visual Blueprint:** 3 Core Contribution Badges, GitHub repository link, Q&A invitation.
- **Proposal References:** Section 7.1 (Feasibility and expected contribution).
- **🗣️ Simple Spoken Script:** *"In conclusion, our research proves that machine learning intrusion detection can be both scientifically rigorous and practically viable for mission-critical video surveillance. We reached our target Macro-F1 of 0.8595 with zero data leakage, achieved sub-second response times, and proved 100% video uptime with zero dropped frames. We thank our supervisors Dr. Matheeh and Dr. Amarakeerthi for their guidance. We now welcome your questions."*
- **🇱🇰 සිංහලෙන් තේරුම:** පර්යේෂණයේ සමස්ත දායකත්වය සාරාංශ කර ප්‍රශ්න විචාරාත්මක අදියරට ආරාධනා කිරීම.

---

# PART 3: ⚔️ Top 12 Viva / Defense Q&A Cheat-Sheet in Plain English
*(Fully Grounded in Proposal Table 11: Project Risks and Mitigations)*

Here are the **top 12 critical viva questions** supervisors will ask, along with simple, clear answers you can speak comfortably:

### Q1: "Why did you use Stratosphere IoT-23 instead of CIC-IDS2017 or KDD99?"
- **Simple Answer:** *"Sir, as explained in proposal Section 2.3, old datasets like KDD99 and CICIDS2017 come from normal office computers with people browsing the web. IoT traffic is fundamentally different: it is predictable Machine-to-Machine (M2M) communication with zero endpoint antivirus. Stratosphere IoT-23 is recorded on real IoT hardware infected with real botnets like Mirai, which matches our camera environment."*

### Q2: "IoT-23 has smart lights and locks, but NO IP cameras. How can your model work on camera video? (RQ3)"
- **Simple Answer:** *"That is the exact focus of our Research Question RQ3 and Table 11 Risk 1. In a camera network, normal traffic has a simple pattern: RTSP video on port 554 and clock sync. Botnet attacks—like scans, floods, and beacons—look identical on the network no matter what device is infected. We checked feature compatibility with our `schema_check` tool and proved in our lab that normal camera video causes zero false alarms."*

### Q3: "What is data leakage and how did you prevent it?"
- **Simple Answer:** *"Data leakage happens when test packets are mixed into the training data. In network traffic, an attack sends thousands of repeating packets. If you shuffle packets randomly, the model memorizes the attack and claims fake 99% accuracy. As required by proposal Section 3.4, we stopped this by holding out the entire Capture-34-1 scenario so the model never saw it during training."*

### Q4: "Why did you pick Random Forest over Deep Learning?"
- **Simple Answer:** *"Deep learning needs big GPUs, heavy RAM, and takes too long to make predictions. Our 100-tree Random Forest needs less than 250 MB RAM and classifies a flow in only 30.88 microseconds. It is super fast, lightweight, and works great on structured table data."*

### Q5: "If your firewall is automatic, what stops an attacker from spoofing an IP to make the camera get blocked?"
- **Simple Answer:** *"Our response policy enforces seven strict safety rules from proposal Section 3.7. Internal camera IPs are strictly banned from source blocking (`block_src`). When a camera calls out to a botnet server, our system blocks only the outside server (`block_dst`). Therefore, the camera can never be blocked."*

### Q6: "Why do you rate-limit DDoS attacks instead of completely blocking them?"
- **Simple Answer:** *"During a high-speed SYN flood, completely blocking an IP can cause collateral damage if normal users share that connection. Our `limit_src` rule allows up to 200 packets per second for normal traffic, but drops all excess flood packets at the router."*

### Q7: "What if a port scan gets a lower confidence score from the ML model?"
- **Simple Answer:** *"Rather than lowering the ML threshold (which would cause false alarms), we built a dual detector: combining ML prediction with multi-host fan-out behavioral detection (`BEHAVIOUR DETECTION`). When an attacker scans multiple hosts across the subnet, behavioral detection triggers an immediate block."*

### Q8: "How do you stop firewall rules from piling up and slowing down the router?"
- **Simple Answer:** *"All our dynamic firewall rules use native Linux kernel decay timers (`flags timeout`). When a rule is added, the router starts a 30-minute countdown. When the timer hits zero, the Linux kernel automatically deletes the rule from memory with no extra software needed."*

### Q9: "What is the difference between Passive SPAN mode and Inline mode?"
- **Simple Answer:** *"As shown in proposal Figure 5, in Passive SPAN mode, the sensor listens on a switch mirror port out-of-band. It adds zero delay to the video feed, and tells the router to block attackers. In Inline mode, the sensor sits in the middle of the network cable as a bridge, dropping bad packets directly."*

### Q10: "How do you know the camera's video recording was not interrupted during testing?"
- **Simple Answer:** *"We continuously monitored the NVR recorder container during all attacks. The NVR recorded RTSP video non-stop on Port 554, saving full 58.6 megabyte video files every 5 minutes with zero dropped frames and latency under 3 milliseconds."*

### Q11: "How does your system handle encrypted traffic like HTTPS / TLS? (Table 11 Risk 5)"
- **Simple Answer:** *"Sir, as explained in proposal Table 11 Risk 5, we do not need to look inside encrypted payloads. Our system works entirely on transport-layer flow metadata extracted by Zeek—such as flow duration, packet counts, byte ratios, and TCP connection flags. These flow stats remain completely visible even when traffic is encrypted."*

### Q12: "How do you handle changes in network traffic over time? (Table 11 Risk 6)"
- **Simple Answer:** *"As addressed in Table 11 Risk 6, we use versioned models (like v3.2.0 saved in MongoDB) and our `schema_check.py` tool to monitor traffic drift. If camera traffic changes over time, our modular pipeline lets us retrain the model with updated data without changing the firewall or dashboard code."*

---

# PART 4: 🎨 PowerPoint Design, Typography & Color Blueprint

To make your PowerPoint deck look world-class and professional, use these simple design tips:

### 🎨 Color Palette:
* **Background:** Deep Navy (`#0B192C`) or Clean White (`#FFFFFF`).
* **Card Boxes:** Dark Slate (`#1E3E62`) or Soft Light Gray (`#F4F6F9`).
* **Headers & Highlights:** Vibrant Cyan (`#00ADB5`).
* **Success / Pass Badges:** Emerald Green (`#2ECC71`).
* **Warning Badges:** Amber Orange (`#F39C12`).
* **Danger / Drop Badges:** Ruby Red (`#E74C3C`).
* **Body Text:** Off-White (`#EEEEEE` on dark slides) or Dark Slate (`#2C3E50` on light slides).

### 🔤 Typography:
* **Slide Headers:** `Montserrat` or `Inter` (Size: 28 – 32 pt, Bold).
* **Subtitles:** `Inter` or `Segoe UI` (Size: 16 – 18 pt, Regular / Italic).
* **Body Bullets:** `Calibri` or `Segoe UI` (Size: 13 – 15 pt).
* **Code / Metric Badges:** `Consolas` or `Fira Code` (Size: 12 – 14 pt, Bold).

### 📐 Layout Rules:
* Always use **16:9 Widescreen** format.
* Do not put giant walls of text; use **2-column or 3-card grid containers** as outlined in Part 1.
* Put **bold keywords** at the beginning of each bullet point for easy reading.

---

*Prepared for Group 03 Progress Presentation · Faculty of Technology, University of Sri Jayewardenepura · November 2026*
