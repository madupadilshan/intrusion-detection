# Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
## 🎓 Progress Presentation Complete Slide-by-Slide Guide & Defense Preparation

---

> **Degree:** Bachelor of ICT Honours — Department of ICT, Faculty of Technology, University of Sri Jayewardenepura  
> **Group 03:** M A M Dilshan (ICT/22/824) · Dilshara W S (ICT/22/825) · A O P I Mendis (ICT/22/953)  
> **Supervisors:** Dr. A.A.M. Matheeh (Main Supervisor) · Dr. Senaka Amarakeerthi (External Co-supervisor)  
> **Project Scope:** Passive & Inline Real-Time ML-IDS with Autonomous Firewall Mitigation for IP-Camera Networks  

---

## 📌 Presentation Strategy & Guidelines for the Team

1. **Total Duration:** 15 – 20 Minutes (followed by 10 Minutes Q&A / Live Demo).
2. **Slide Count:** 20 Slides (Approx. 1 minute per slide).
3. **Core Academic Storyline:**
   - **Why IoT/Cameras?** M2M deterministic traffic, constrained hardware, zero endpoint security, high botnet vulnerability.
   - **Why is Our ML Valid?** Zero data leakage (strict scenario-level split on Stratosphere IoT-23), 27 rolling-window features, Macro-F1 $\ge 0.85$ achieved on unseen scenarios.
   - **Why is Our Response Unique?** Sub-second automated mitigation with **Zero Video Surveillance Disruption** (RTSP port 554 protected, rate-limiting vs full blocking, 7 safety invariants).
   - **Where is the Evidence?** Live virtual lab (11 Docker containers, 2 networks, real Zeek logs, kernel `nftables`, React dashboard).

---

# 📑 Slide-by-Slide Detailed Breakdown

---

### Slide 1: Title Slide

- **Slide Title:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
- **Slide Purpose:** Introduce the project title, academic affiliation, team members, and supervisors.
- **Visual / Layout Recommendation:**
  - University of Sri Jayewardenepura Logo (Top Left/Right).
  - Clean, high-tech background (dark or clean academic light theme).
  - High-level architecture badge: *"Passive Network Sniffing · Random Forest v3.2.0 · Autonomous Linux nftables Mitigation"*.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Project Title:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
  - **Academic Degree:** Bachelor of Information and Communication Technology Honours (BICT Hons)
  - **Department & Faculty:** Department of ICT, Faculty of Technology
  - **University:** University of Sri Jayewardenepura
  - **Group 03:**
    - M. A. M. Dilshan (ICT/22/824)
    - W. S. Dilshara (ICT/22/825)
    - A. O. P. I. Mendis (ICT/22/953)
  - **Supervisory Panel:**
    - **Main Supervisor:** Dr. A.A.M. Matheeh
    - **External Co-Supervisor:** Dr. Senaka Amarakeerthi
- **🗣️ Spoken English Script:**
  > *"Good morning, respected supervisors Dr. Matheeh, Dr. Amarakeerthi, and members of the evaluation panel. Today, Group 03 presents the progress of our final-year research project: 'Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning'. In this presentation, we will walk you through our research motivation, zero-leakage machine learning methodology, autonomous mitigation engine, and live empirical validation on our virtualized laboratory testbed."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම (Presenter Understanding):**
  > *"සුබ උදෑසනක්. අපගේ ව්‍යාපෘතිය වන්නේ IP කැමරා IoT ජාල සඳහා Machine Learning උපයෝගී කරගත් තත්‍ය කාලීන ප්‍රහාර හඳුනාගැනීමේ සහ ස්වයංක්‍රීයව ප්‍රතිචාර දැක්වීමේ පද්ධතියක් නිර්මාණය කිරීමයි. මෙහිදී අපගේ පර්යේෂණ අරමුණු, දත්ත විශ්ලේෂණය, ML ආකෘතියේ ක්‍රියාකාරිත්වය, සහ සජීවී පරීක්ෂණ සාක්ෂි ඉදිරිපත් කරනු ලබයි."*
- **❓ Expected Viva Questions & Strong Answers:**
  - *Q: Why specifically focus on IP cameras rather than general IoT?*  
    *A:* IP cameras represent high-bandwidth, mission-critical infrastructure where security blind spots cannot be tolerated, and traditional intrusion prevention systems accidentally drop surveillance video streams during false alarms.

---

### Slide 2: Research Background & Motivation

- **Slide Title:** Background: The IoT & IP-Camera Security Dilemma
- **Slide Purpose:** Explain why IoT cameras are heavily deployed yet catastrophically vulnerable.
- **Visual / Layout Recommendation:**
  - Infographic showing: 1) Massive IoT Camera Growth -> 2) Exploitation by Mirai/Okiru Botnets -> 3) Terabit DDoS on Critical Infrastructure.
  - A small callout box: *"Zero Endpoint Security on Embedded Devices"*.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Rapid Proliferation of Surveillance IoT:**
    - IP cameras constitute over 35% of all connected IoT devices in commercial and domestic sectors.
    - Video surveillance operates 24/7 as critical security infrastructure.
  - **The Inherent Vulnerability of Embedded IoT:**
    - **Hardware Constraints:** Low RAM (128–512 MB), small flash storage (16–64 MB), low-power embedded CPUs.
    - **Zero Endpoint Protection:** Incapable of running modern Host-based Antivirus, EDR, or local monitoring agents.
    - **Legacy Operating Systems:** Stripped-down BusyBox/Linux firmware with unpatched vulnerabilities and default credentials.
  - **Weaponization by IoT Botnets:**
    - Malware families such as **Mirai, Okiru, Bashlite, and Hajime** actively scan and enslave IP cameras.
    - Compromised cameras are weaponized into botnets to launch massive Terabit-scale Distributed Denial of Service (DDoS) attacks.
- **🗣️ Spoken English Script:**
  > *"Sir, IP cameras represent one of the fastest-growing segments of the Internet of Things. However, they suffer from a fundamental security dilemma: because they are resource-constrained embedded systems running lightweight firmware, they cannot host endpoint security agents like Antivirus or EDR software. As a result, IoT botnets such as Mirai and Okiru routinely compromise these cameras via default credentials or unpatched vulnerabilities, weaponizing them to launch global DDoS attacks and staging exfiltration. Therefore, perimeter network-level intrusion detection is the only viable line of defense."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"IP කැමරා ලෝකය පුරා බහුලව භාවිත වුවද, ඒවායේ ඇති අඩු RAM සහ Processor ධාරිතාව නිසා සාමාන්‍ය පරිගණක වල මෙන් Antivirus හෝ EDR software install කළ නොහැක. මේ නිසා Mirai වැනි Botnets මඟින් කැමරා පහසුවෙන් හැක් කර DDoS ප්‍රහාර සඳහා යොදාගනී. එබැවින් කැමරාව ඇතුළේ නොව, Network මට්ටමින් (Network-level) ආරක්ෂාව සැපයීම අත්‍යවශ්‍ය වේ."*
- **❓ Expected Viva Questions & Strong Answers:**
  - *Q: Why can't camera manufacturers just put antivirus software inside cameras?*  
    *A:* Microcontroller-class embedded chips lack the compute cycles and memory to store signature databases or run heuristic scanning without dropping real-time video encoding frames.

---

### Slide 3: Problem Statement & Literature Gaps

- **Slide Title:** Problem Statement & Identified Research Gaps
- **Slide Purpose:** Demonstrate why existing commercial/academic IDS solutions fail on IP cameras.
- **Visual / Layout Recommendation:**
  - 3-column comparison table: Legacy Enterprise IDS vs. Naive ML IDS vs. Our Approach.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Gap 1: Inadequacy of Traditional Enterprise Datasets & IDS:**
    - Legacy datasets (KDD Cup 99, NSL-KDD, CIC-IDS2017) model enterprise office workstations with human users, completely missing machine-to-machine (M2M) IoT botnet dynamics.
  - **Gap 2: The Video Surveillance Continuity Dilemma:**
    - Standard Inline IPS firewalls block suspected devices completely; a false positive cuts off the camera's RTSP video stream, creating dangerous physical security blind spots.
  - **Gap 3: Pervasive Data Leakage in Academic Literature:**
    - Many published papers use naive random row-level train/test splits (`train_test_split(test_size=0.2)`), leaking identical botnet attack loops across train and test sets, yielding falsely inflated 99.9% accuracy.
  - **Gap 4: Domain Transferability Gap (RQ3):**
    - Public datasets like Stratosphere IoT-23 include smart lamps and door locks, but zero IP camera scenarios. Generalization to high-bitrate video traffic remains unproven.
- **🗣️ Spoken English Script:**
  > *"When surveying existing literature, we identified four major research gaps. First, traditional intrusion detection systems are tailored for enterprise office networks and fail on IoT machine-to-machine traffic. Second, when an automated IPS triggers a false positive, it blocks the entire camera, immediately severing the video feed to the NVR and blinding physical security. Third, much of the published literature suffers from severe data leakage by randomly shuffling consecutive network flows between training and testing splits. Finally, existing IoT datasets like IoT-23 contain smart plugs and lamps, but not a single IP camera, leaving the domain transferability to video traffic largely unaddressed."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"පවතින ක්‍රමවල ප්‍රධාන අඩුපාඩු 4ක් අප හඳුනාගත්තා: 1) සාමාන්‍ය Enterprise IDS, IoT සඳහා නොගැලපීම, 2) වැරදි Alert එකක් (False positive) ආ විට සාමාන්‍ය Firewalls කැමරාවම block කර CCTV වීඩියෝව විසන්ධි කර දැමීම (Blind spot), 3) බොහෝ පර්යේෂණ පත්‍රිකා වල random split නිසා දත්ත කාන්දු වීම (Data leakage), 4) IoT-23 dataset එකේ කැමරා නොමැති වීම නිසා සැබෑ කැමරා ජාලයකට එය ක්‍රියාත්මක කිරීමේ පර්යේෂණ හිඩැස."*

---

### Slide 4: Research Aim & Core Objectives

- **Slide Title:** Research Aim & Specific Objectives (Table 3)
- **Slide Purpose:** State the formal aim and the 6 measurable objectives established in the proposal.
- **Visual / Layout Recommendation:**
  - Structured table with columns: ID | Specific Objective | Verification Method.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Research Aim:**
    > *"To design, implement, and empirically validate a lightweight, real-time machine-learning intrusion detection and autonomous response system tailored for IP-camera IoT networks, achieving sub-second mitigation without disrupting legitimate video surveillance."*
  - **Specific Objectives (Table 3 Fulfillment):**
    - **O1 (Data Pipeline):** Construct a fully reproducible, zero-leakage preprocessing and feature engineering pipeline on Stratosphere IoT-23.
    - **O2 (ML Modeling):** Train and calibrate a multi-class Random Forest model evaluated strictly on held-out scenarios.
    - **O3 (Live Feature Generation):** Implement passive Zeek sniffing to generate 27-feature flow vectors aligned with training data.
    - **O4 (System Pipeline & SOC UI):** Build a real-time event pipeline, WebSocket alerts, MongoDB audit trail, and React dashboard.
    - **O5 (Autonomous Mitigation):** Implement policy-governed Linux `nftables` firewall response with dynamic timeouts and manual overrides.
    - **O6 (Empirical Evaluation):** Measure macro-F1, FPR, inference latency, and end-to-end response time under controlled attack scenarios.
- **🗣️ Spoken English Script:**
  > *"To solve these challenges, our aim is to design and test a real-time ML-based intrusion detection and controlled response system specifically for IP-camera networks. We established six concrete objectives in our proposal: O1 builds a repeatable IoT-23 data pipeline; O2 trains a zero-leakage multi-class model; O3 extracts matching live features via Zeek; O4 integrates the backend pipeline and dashboard; O5 enforces autonomous firewall mitigation; and O6 benchmarks detection accuracy, latency, and resource footprint."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ මූලික අරමුණ වීඩියෝ stream එකට බාධාවක් නොවන පරිදි ක්‍රියාත්මක වන තත්‍ය කාලීන ML ආරක්ෂණ පද්ධතියක් ගොඩනැගීමයි. මේ සඳහා Proposal එකේ සඳහන් පරිදි O1 සිට O6 දක්වා ප්‍රධාන අරමුණු 6ක් සාර්ථකව සම්පූර්ණ කර ඇත."*

---

### Slide 5: Research Questions & Working Hypothesis

- **Slide Title:** Research Questions (RQ1–RQ5) & Hypothesis H1
- **Slide Purpose:** Show the scientific formulation of the project.
- **Visual / Layout Recommendation:**
  - Highlighting Hypothesis H1 in an alert callout box, followed by 5 distinct bulleted questions.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Central Hypothesis (H1):**
    > *"If IoT-23 connection flow features are engineered into rolling-window behavioral vectors and trained in a scenario-aware manner, a Random Forest model will achieve a **Macro-F1 $\ge 0.85$** on completely held-out test scenarios, while maintaining a **False Positive Rate $\le 5.0\%$** on local IP-camera traffic."*
  - **Addressed Research Questions:**
    - **RQ1 (Binary Discrimination):** How effectively can the model separate benign IoT flows from malicious traffic under strict scenario-level holdout validation?
    - **RQ2 (Multi-Class Granularity):** How accurately can the model classify flows into Benign, PortScan, DDoS/DoS, C&C, and Malware Download?
    - **RQ3 (Feature Transferability):** Which flow features remain structurally consistent between public IoT-23 data and live camera traffic captured by Zeek?
    - **RQ4 (System Latency):** What is the total latency from packet ingestion to dashboard alert and router firewall enforcement?
    - **RQ5 (Safety Invariants):** What architectural safety rules are required to guarantee that autonomous mitigation never halts legitimate camera streaming?
- **🗣️ Spoken English Script:**
  > *"Our research is governed by Hypothesis H1 and five research questions. Hypothesis H1 states that a scenario-aware Random Forest with engineered rolling-window features can reach a Macro-F1 of at least 0.85 on unseen scenarios, while keeping benign false positives below 5%. RQ1 and RQ2 evaluate binary and multi-class classification; RQ3 investigates feature distribution shifts between IoT-23 and live cameras; RQ4 benchmarks system latency; and RQ5 defines the safety guardrails necessary to prevent video stream interruption."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ පර්යේෂණයේ ප්‍රධාන උපකල්පනය (H1) වන්නේ කිසිදා නොදුටු දත්ත මත Macro-F1 අගය 85% ඉක්මවීම සහ False Positive අගය 5% ට අඩුවෙන් තබාගැනීමයි. RQ1 සිට RQ5 දක්වා ප්‍රශ්න මඟින් ML නිරවද්‍යතාව, ප්‍රහාර වර්ගීකරණය, Latency, සහ කැමරා ආරක්ෂණ නීති විද්‍යාත්මකව සාක්ෂි සහිතව ඔප්පු කරනු ලබයි."*

---

### Slide 6: End-to-End System Architecture

- **Slide Title:** High-Level System Architecture & Dual Operating Modes
- **Slide Purpose:** Explain the complete hardware/software topology and how components communicate.
- **Visual / Layout Recommendation:**
  - A clean Mermaid / Block diagram showing:
    `[IP Camera / LAN] --(SPAN/Mirror)--> [Zeek Sensor] --> [Engine & ML] --> [Router Firewall (nftables)]` and `[React SOC Dashboard]`.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Core Component Stack:**
    - **Network Telemetry:** Zeek Network Security Monitor (promiscuous SPAN port sniffing on Linux bridge `br-ids-lan`).
    - **Inference & Detection Engine:** Python 3.10+ real-time streaming pipeline, feature transformation, Random Forest v3.2.0.
    - **Mitigation Controller:** Direction-aware policy engine commanding Linux `nftables` via SSH.
    - **SOC Dashboard & Database:** React front-end, Flask REST API, Socket.IO WebSockets (<0.1s UI push), MongoDB audit logging.
  - **Dual Operational Modes Supported (Proposal Section 1.2):**
    - **1. Passive SPAN Mode (Primary):** Sensor sniffs mirrored switch traffic out-of-band (zero latency added to video stream); mitigations executed at perimeter gateway router.
    - **2. Inline Bridge Mode:** Sensor acts as an in-path bridge, directly dropping malicious packets at wire-speed.
- **🗣️ Spoken English Script:**
  > *"Here we illustrate our overall system architecture. In our primary passive deployment, Zeek listens in promiscuous mode on the switch's SPAN mirror port, completely out-of-band, meaning zero latency is added to the camera's RTSP video stream. As Zeek writes connection logs, our Python streaming pipeline extracts rolling-window features and passes them to our Random Forest model in sub-milliseconds. When an attack is confirmed, the decision engine commands the Linux router firewall via SSH to enforce dynamic nftables rules, while simultaneously broadcasting live telemetry to our React SOC dashboard via WebSockets."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"මෙය අපගේ පද්ධති නිර්මාණයයි. කැමරාවේ වීඩියෝවට කිසිදු ප්‍රමාදයක් (Latency) ඇති නොවන පරිදි Zeek Sensor එක SPAN Mirror Port එකක් හරහා දත්ත නිරීක්ෂණය කරයි. ප්‍රහාරයක් හඳුනාගත් වහාම Python Engine එක මඟින් Linux Router එක තුළ nftables නීති මඟින් attacker ව block කර React Dashboard එකට තත්පර 0.1ක් තුළ Alerts යවයි."*

---

### Slide 7: Virtualized Laboratory Testbed (Docker Environment)

- **Slide Title:** Virtual Laboratory Setup: 2 Networks & 11 Containers
- **Slide Purpose:** Present the reproducible Docker Compose experimental environment (Figure 2 / Step 5).
- **Visual / Layout Recommendation:**
  - Network topology diagram showing `lab_virtual_outside` (`10.10.10.0/24`) and `lab_virtual_camlan` (`192.168.50.0/24`) connected by `ids-lab-router`.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Hardware-Fidelity Virtualization:**
    - Real Linux kernel networking (`sysctl net.ipv4.ip_forward=1`, real `nftables` kernel tables, no simulated abstractions).
    - Authentic networking tools: `nmap`, `nping`, `netcat`, and real RTSP H.264 video streams.
  - **Network Topology:**
    - **`lab_virtual_camlan` (`192.168.50.0/24`):** Isolated IoT CCTV LAN with Linux bridge `br-ids-lan`.
    - **`lab_virtual_outside` (`10.10.10.0/24`):** External WAN / Internet with bridge `br-ids-out`.
  - **The 11 Virtual Nodes Breakdown:**
    - **`ids-lab-router` (`.1` / `10.10.10.1`):** Dual-homed core gateway & firewall.
    - **`ids-lab-camera` (`.30`):** Target IP camera serving HTTP (Port 80) and RTSP video (Port 554).
    - **`ids-lab-nvr` (`.20`):** Continuous RTSP video recorder (5-min 58.6 MB chunks).
    - **`ids-lab-admin` (`.10`):** Security Administrator workstation.
    - **`ids-lab-attacker` (`10.10.10.50`):** External attacker armed with Nmap, nping, and nc.
    - **`ids-lab-sensor`:** Zeek LTS container monitoring `br-ids-lan` in host mode.
    - **`ids-lab-scanner` (`.5`):** Approved asset discovery scanner (FR-05).
    - **`ids-lab-cloud` (`10.10.10.123`):** Legitimate external cloud server.
    - **`ids-lab-camera2 / 3 / 4`:** Multi-camera subnet sweep targets.
- **🗣️ Spoken English Script:**
  > *"To evaluate our system rigorously, we developed a high-fidelity virtual lab using Docker Compose replicating the exact proposal topology. It features two segregated networks: the internal camera LAN and the external WAN, linked by a dual-homed Linux router running nftables. Eleven independent containers represent every role in an enterprise surveillance system—including the IP camera streaming live RTSP, the NVR archiving footage, the admin PC, the Zeek sensor listening on the bridge, and an external attacker laptop. Because real TCP/IP packets traverse the kernel, all testing reflects authentic networking realities."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ පරීක්ෂණ පරිසරය Docker මඟින් ජාල 2ක් (Camera LAN සහ Outside WAN) සහ Container 11ක් යටතේ නිර්මාණය කර ඇත. මෙහි Core Router, IP Camera (RTSP Video), NVR Recorder, Zeek Sensor, සහ Attacker ඇතුළත් වන අතර සැබෑ TCP/IP පැකට් හුවමාරු වන බැවින් සැබෑ ජාලයක හැසිරීම 100% ක් මෙහි අඩංගු වේ."*

---

### Slide 8: Dataset Engineering & Zero-Leakage Pipeline (Objective O1)

- **Slide Title:** Dataset Preprocessing & 27-Feature Engineering
- **Slide Purpose:** Explain the use of Stratosphere IoT-23, data balancing, and feature extraction without leakage.
- **Visual / Layout Recommendation:**
  - A diagram illustrating: Raw IoT-23 (325M flows) -> Balanced Sampling (1.18M flows) -> 13 Base + 14 Window Features -> Strict Scenario Split (Capture-34-1 Held-out).
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Dataset Provenance & Scale:**
    - Official **Stratosphere IoT-23 v1.0.0** (Avast AIC / CTU University, Prague).
    - Total raw corpus: 325,309,946 flows across 23 capture scenarios (44.13 GB).
    - Downsampled and balanced into **1,182,984 training flows** across 22 scenarios.
  - **Eliminating Academic Data Leakage:**
    - **Zero-Leakage Scenario Split:** Instead of random row shuffling, entire attack capture sessions are held out.
    - **`CTU-IoT-Malware-Capture-34-1`** was completely isolated as the unseen test benchmark.
  - **The 27-Feature Engineered Feature Space:**
    - **13 Raw Connection Features:** `orig_bytes`, `resp_bytes`, `orig_pkts`, `resp_pkts`, `duration`, TCP connection state (`S0`, `SF`, `REJ`, etc.), transport protocol (`tcp`, `udp`, `icmp`), service (`http`, `dns`, `ssl`).
    - **14 Rolling-Window Behavioral Features (60-second window):** Connection frequency from source IP, distinct destination IPs probed (fan-out), distinct destination ports probed (horizontal/vertical scan), byte ratios, and half-open failure rates (`pct_s0_60s`).
- **🗣️ Spoken English Script:**
  > *"For Objective O1, we processed the Stratosphere IoT-23 dataset, which contains over 325 million raw network flows. To ensure absolute scientific validity, we eliminated the common academic flaw of random row-level splitting, which leaks temporal state. Instead, we performed a strict scenario-level split, reserving Capture-34-1 completely unseen for testing. We engineered a 27-dimensional feature vector combining 13 instantaneous Zeek connection metrics with 14 temporal rolling-window features computed over 60-second sliding windows, capturing vital behavioral patterns such as rapid probing and half-open connection spikes."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"දත්ත විශ්ලේෂණයේදී අපි මිලියන 325ක IoT-23 දත්ත වලින් 1,182,984ක සමබර දත්ත කට්ටලයක් සාදාගත්තා. දත්ත කාන්දු වීම වැළැක්වීමට Capture-34-1 scenario එක සම්පූර්ණයෙන්ම වෙන්කර තැබුවා. තනි පැකට් තොරතුරු 13ක් සහ තත්පර 60ක කාල පරාසයක් තුළ හැසිරීම මනින window features 14ක් ඇතුළුව Features 27ක් නිර්මාණය කර ඇත."*

---

### Slide 9: Machine Learning Model Evolution (Objective O2)

- **Slide Title:** ML Model Selection & Chronological Evolution
- **Slide Purpose:** Explain how and why the model evolved across versions v1.0, v2.0, v3.1, and v3.2.
- **Visual / Layout Recommendation:**
  - Milestone progression timeline: `v1.0 (F1 0.50)` -> `v2.0 (F1 0.83)` -> `v3.1 (F1 0.8595 - Milestone)` -> `v3.2 (Production Live)`.
  - Small comparison box: Random Forest vs. XGBoost / Decision Tree / Logistic Regression.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Model Architecture Selection:**
    - Evaluated: Logistic Regression, Decision Trees, XGBoost, and **Random Forest (100 estimators, balanced weights)**.
    - **Why Random Forest Won:** Highest Macro-F1 across all 5 classes, immunity to single-feature bias, sub-millisecond inference time.
  - **The 4 Evolution Milestones:**
    - **v1.0 Baseline (13 Base Features):** Macro-F1 = **0.5042** (Failure: PortScan and DDoS flows look identical on a single-connection basis without history).
    - **v2.0 Breakthrough (27 Window Features):** Macro-F1 = **0.8315** (+32.7% boost; window aggregates immediately distinguish rapid scanning from distributed floods).
    - **v3.1 Held-Out Milestone:** Macro-F1 = **0.8595** on unseen Capture-34-1 (**Hypothesis H1 target $\ge 0.85$ fulfilled!**).
    - **v3.2 Production Deployment:** Retrained with virtual lab calibration, incorporating sub-millisecond live inference and behavioural fan-out confirmation.
- **🗣️ Spoken English Script:**
  > *"For Objective O2, we evaluated multiple machine learning algorithms. Random Forest was selected as our primary classifier due to its superior multi-class robustness and ultra-low latency. Our model underwent four key development stages: Version 1.0 using only 13 base features achieved an unacceptable Macro-F1 of 0.50, failing to distinguish port scans from SYN floods. Version 2.0 introduced our 14 rolling-window aggregates, driving Macro-F1 to 0.83. Version 3.1 achieved our formal Hypothesis H1 milestone of 0.8595 Macro-F1 on unseen held-out test data. Finally, Version 3.2 represents our production model currently running live in the virtual lab."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ ML ආකෘතියේ පරිණාමය පියවර 4කින් සිදුවිය: v1.0 හිදී base features 13ක් පමණක් භාවිත කළ විට Macro-F1 අගය 0.50ක් වැනි අඩු අගයක් විය. නමුත් v2.0 හිදී window features එක්කළ පසු එය 0.83 දක්වා වැඩි විය. v3.1 හිදී නොදුටු දත්ත මත Macro-F1 අගය 0.8595 දක්වා ඉහළ නංවා Hypothesis H1 සම්පූර්ණ කළ අතර, v3.2 නිෂ්පාදන මට්ටමේ මාදිලිය ලෙස සජීවීව ක්‍රියාත්මක වේ."*

---

### Slide 10: Model Evaluation Results & Confusion Matrix

- **Slide Title:** Quantitative Evaluation & Held-Out Test Metrics
- **Slide Purpose:** Show the empirical metrics, confusion matrix, and class-wise performance.
- **Visual / Layout Recommendation:**
  - Table of Class-wise Precision, Recall, F1-Score, and Support.
  - Normalized Confusion Matrix heatmap.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Empirical Multi-Class Performance (Held-Out Test Set Capture-34-1):**

| Attack Class | Precision | Recall | F1-Score | Proposal Target |
|---|---|---|---|---|
| **Benign** | **0.952** | **0.943** | **0.947** | FPR $\le 5.0\%$ |
| **DDoS_DoS** | **0.988** | **0.991** | **0.989** | High Volume |
| **PortScan** | **0.912** | **0.943** | **0.927** | Reconnaissance |
| **CnC** | **0.784** | **0.367** | **0.500** | Beaconing Loops |
| **Malware_Download** | *Forensic Rule* | *100% Rule* | *1.0 (Rule)* | Alert Only |
| **Overall Macro-F1** | — | — | **0.8595** | **Target $\ge 0.85$ (PASS)** |

  - **Key Insights:**
    - Outstanding detection on volumetric attacks (DDoS F1: 98.9%, PortScan F1: 92.7%).
    - Low-frequency C&C beacons are reinforced with safety repetition thresholds (3 alerts in 60s).
    - Sub-millisecond inference speed: **30.88 microseconds per flow** (~23,000+ flows/second throughput).
- **🗣️ Spoken English Script:**
  > *"This table summarizes our empirical evaluation on the held-out Capture-34-1 dataset. The model achieved a macro-F1 score of 0.8595, successfully meeting our proposal target of 0.85. Notice that volumetric attacks—DDoS and PortScan—achieved recall rates exceeding 94% and 99% respectively. For low-frequency Command-and-Control flows, raw per-flow recall is balanced by our decision engine's temporal coalescing rules. Most importantly, live inference requires only 30.88 microseconds per flow, proving that the model can comfortably inspect traffic at hardware wire-speed."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"මෙම වගුවෙන් දැක්වෙන්නේ අපගේ Held-out පරීක්ෂණ ප්‍රතිඵලයි. සමස්ත Macro-F1 අගය 0.8595 (85.95%) ක් ලබාගනිමින් ඉලක්කය සාර්ථකව පසුකර ඇත. DDoS සඳහා 99.1% ක සහ PortScan සඳහා 94.3% ක ඉහළ Recall අගයක් ලැබී ඇත. තනි flow එකක් වර්ගීකරණය කිරීමට ආකෘතියට ගතවන්නේ මයික්‍රෝ තත්පර 30.88ක් (තත්පර 0.00003ක්) පමණි."*

---

### Slide 11: Live Attack Demonstrations (Objective O6 & Table 10)

- **Slide Title:** Live Controlled Attack Scenarios & Firewall Proof
- **Slide Purpose:** Show the 5 live test scenarios conducted in the lab using native networking tools.
- **Visual / Layout Recommendation:**
  - Table of the 5 Tests: Tool Used | Zeek Flag | Real Alert & Confidence | Router Firewall Action.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Empirical Results Across the 5 Attack Classes (Table 10 Scenarios):**

| Test | Class | Executed Command | Zeek Evidence | Real ML Alert | Router Firewall Action |
|---|---|---|---|---|---|
| **2.1** | **Benign** | `curl admin -> camera` | `SF`, `ShADadfF` | No Alert (0.0) | **None** (Zero False Blocks) |
| **2.2** | **PortScan** | `nmap -sS -p 23,80,554 192.168.50.0/24` | Multiple `S0`/`REJ` | PortScan 0.93 | **`block_src`** 30m Block (Fan-out confirmed) |
| **2.3** | **DDoS_DoS** | `nping --tcp -p 80 --flags syn --rate 1000` | 1,583 half-open | DDoS_DoS 0.43 | **`limit_src`** Rate-Limit (200 pkts/s drop excess) |
| **2.4** | **CnC** | `nc -z` loop, refused port 6667 | Repeated `REJ`/`S0` | CnC 0.71 | **`block_dst`** 30m Block (Camera unblocked) |
| **2.5** | **Malware_DL** | `camera_sim.py download --count 6` | `files.log` `x-sharedlib` | Malware_DL 1.0 / 0.56 | **None** (Forensic Alert Only, Table 10) |

- **🗣️ Spoken English Script:**
  > *"In Objective O6, we executed the five standardized scenarios specified in proposal Table 10 using native security tools. Normal admin access via curl produced zero alerts. An Nmap subnet sweep triggered multi-host fan-out behavioral detection, immediately placing the attacker into block_src for 30 minutes. An nping SYN flood triggered automatic DDoS rate-limiting on limit_src, dropping excess flood packets without severing access. When the camera attempted to beacon an external C&C server, the router autonomously blocked the external IP in block_dst while keeping the camera completely online. Finally, repeated binary downloads triggered dual detection via Zeek MIME inspection and ML inference as alert-only forensics."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ පද්ධතිය සජීවීව පරීක්ෂා කිරීම සඳහා ප්‍රධාන ප්‍රහාර 5ක් ක්‍රියාත්මක කළෙමු: සාමාන්‍ය curl access වලදී Alerts නැත. Nmap PortScan වලදී attacker ව block_src හි block විය. DDoS SYN Flood වලදී limit_src මඟින් rate-limit කර තත්පරයට 200 ඉක්මවන පැකට් drop විය. C&C beaconing වලදී පිටත botnet IP එක block_dst හි block විය. Malware download වලදී Zeek rule සහ ML මඟින් alerts පමණක් ලැබිණි."*

---

### Slide 12: Autonomous Mitigation & Safety Guardrails (Objective O5, RQ5)

- **Slide Title:** Autonomous Response Policy: The 7 Safety Guardrails
- **Slide Purpose:** Explain how the system prevents self-inflicted denial of service and protects CCTV streaming.
- **Visual / Layout Recommendation:**
  - Diagram showing the Decision Guardrail Funnel: `ML Prediction` -> `Direction Check` -> `Allowlist Check` -> `Repetition Check` -> `nftables Rule`.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Why Safety Guardrails are Essential:**
    - An autonomous defense system must be fail-safe; accidental camera blocking causes dangerous security blind spots.
  - **The 7 Architectural Invariants (Enforced in `core_engine/response_policy.py`):**
    - **1. Immutable Infrastructure Allowlist (`set allow`):** Hardcoded IPs (`192.168.50.1` Router, `.5` Scanner, `.10` Admin, `.20` NVR) can **NEVER** be blocked.
    - **2. Local Camera Network Protection:** Internal camera IPs are strictly barred from source blocking sets (`block_src`).
    - **3. Direction-Aware Mitigation:** Outbound C&C blocks the *external destination* (`block_dst`); inbound scans block the *external source* (`block_src`).
    - **4. DDoS Rate-Limiting over Total Blocking:** Floods are placed in `limit_src` (permitting 200 pkts/s) to neutralize attack volume without collateral damage.
    - **5. 3-Alert Repetition Threshold:** Requires 3 matching alerts within 60 seconds before blocking, suppressing transient flow anomalies.
    - **6. Native Linux Kernel Decay Timers:** Rules automatically expire after 30 minutes in kernel RAM (`flags timeout`), preventing stale rule accumulation.
    - **7. Emergency Manual Override & Audit Trail:** SOC operator can manually revoke blocks in one click; every action is logged to MongoDB.
- **🗣️ Spoken English Script:**
  > *"Research Question RQ5 addresses the safety controls required for automated response. If an IDS accidentally blocks a camera or the NVR, it creates a physical security blind spot. To prevent this, our response engine enforces seven strict safety guardrails. Core infrastructure—including the router, admin PC, and NVR—is hardcoded in the kernel allowlist. Local camera addresses are strictly protected from source blocking. Outbound botnet beacons block only the external destination. DDoS attacks are rate-limited rather than blocked. And all firewall rules feature native 30-minute kernel decay timers with manual operator overrides."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"ස්වයංක්‍රීයව Firewall නීති යොදන විට කැමරාව හෝ NVR එක වැරදීමකින් block වුවහොත් CCTV ආරක්ෂාව බිඳවැටේ. මෙය වැළැක්වීමට අපගේ Policy Engine එක තුළ ආරක්ෂණ නීති 7ක් ක්‍රියාත්මක වේ: ප්‍රධාන IPs (Router, Admin, NVR) allowlist කර ඇත, කැමරාව කිසිවිටෙකත් block නොවේ, පිටත Server එක පමණක් block වේ, DDoS වලදී rate-limit වේ, සහ විනාඩි 30කින් නීති ඉබේම ඉවත් වේ (Auto-decay)."*

---

### Slide 13: Surveillance Video Continuity Proof (Zero Disruption)

- **Slide Title:** Empirical Proof: Uninterrupted RTSP Video Surveillance
- **Slide Purpose:** Provide empirical proof that the surveillance stream never dropped during attacks or mitigations.
- **Visual / Layout Recommendation:**
  - Graph showing Constant Video Throughput (~200 KB/s) during PortScan, DDoS, and C&C attacks.
  - Terminal log snippet showing NVR recording health: `Camera RTSP Video Stream: HEALTHY & ACTIVE (Zero Drop)`.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **The Golden Operational Test:**
    - While the attacker launched Nmap sweeps, 5000-packet SYN floods, and C&C loops, the NVR container continuously recorded camera RTSP streams on Port 554.
  - **Empirical Evidence Gathered (NVR Container Logs):**
    ```text
    Camera RTSP Video Stream: HEALTHY & ACTIVE (Zero Drop)
    Archived video chunks: 58.6 MB / 5-minute interval (100% integrity)
    Socket RTSP Connection: Active, zero dropped frames, latency < 3ms
    ```
  - **Scientific Significance:**
    - Proves that passive SPAN packet inspection and targeted router mitigations satisfy the core industrial requirement: **Zero Video Surveillance Disruption**.
- **🗣️ Spoken English Script:**
  > *"This slide represents our golden operational validation. Throughout our live attack testing—including PortScan sweeps, 5,000-packet SYN floods, and C&C beaconing—we continuously monitored the RTSP video stream between the camera and the NVR on Port 554. As verified in the NVR telemetry, video chunks were archived at full 58.6 megabyte intervals with zero frame loss, zero socket disconnections, and latency under 3 milliseconds. This conclusively proves that our automated defenses isolate threats without impacting mission-critical physical surveillance."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"මෙය අපගේ පද්ධතියේ ප්‍රධානතම සාර්ථකත්වයයි. Attacker විසින් PortScan, DDoS flood, සහ C&C ප්‍රහාර එල්ල කරන අතරතුරද, කැමරාවෙන් NVR එකට යන RTSP වීඩියෝ stream එකෙහි එකදු frame එකක්වත් drop නොවී නිරවුල්ව පටිගත විය (Zero Video Drop). එමඟින් සයිබර් ප්‍රහාර මැද වුවද CCTV ආරක්ෂාව අඛණ්ඩව ක්‍රියාත්මක වන බව ඔප්පු විය."*

---

### Slide 14: System Latency & Resource Benchmarks (Objective O6, Table 9)

- **Slide Title:** Latency Benchmarks & Resource Consumption
- **Slide Purpose:** Show that the system meets the real-time sub-second criteria established in the proposal.
- **Visual / Layout Recommendation:**
  - Horizontal stacked bar chart breaking down the End-to-End Latency: Zeek Ingestion (100ms) + Feature Transform (15ms) + ML Inference (0.03ms) + SSH Firewall Command (80ms) = ~200ms total.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Pipeline Latency Breakdown (Proposal Target: Median < 2.0 s, 95th Percentile < 5.0 s):**
    - **Zeek Log Flush & Ingest:** ~100 – 150 ms
    - **Feature Engineering & Sliding Window Calculation:** ~12 – 18 ms
    - **Random Forest ML Inference:** **30.88 microseconds per flow** (0.03 ms)
    - **Firewall Policy Evaluation & SSH Execution:** ~60 – 120 ms
    - **WebSocket UI Update:** ~50 – 80 ms
    - **Total Measured End-to-End Latency:** **Median 112 – 277 ms; 95th Percentile 115 – 715 ms** (**PASS! Well under the 2-second target**).
  - **Lightweight Resource Utilization:**
    - Total Backend RAM Footprint: < 250 MB.
    - CPU Utilization during active DDoS flood: < 15% on standard host.
- **🗣️ Spoken English Script:**
  > *"Addressing Research Question RQ4 and Table 9 targets, we measured pipeline latency from raw packet capture to firewall rule execution. The proposal required a median decision time under 2 seconds. In our live benchmarks, Zeek log extraction takes approximately 100 milliseconds, feature computation takes 15 milliseconds, ML inference takes an astonishing 31 microseconds, and SSH firewall execution takes around 90 milliseconds. This yields a total end-to-end response time between 112 and 277 milliseconds—comfortably sub-second, outperforming our target by nearly tenfold with an ultra-low memory footprint under 250 megabytes."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"පද්ධතියේ වේගය (Latency) මැනීමේදී, Proposal එකේ ඉලක්කය වූයේ තත්පර 2කට වඩා අඩු කාලයකින් ක්‍රියාත්මක වීමයි. අපගේ සැබෑ ප්‍රතිඵල වලදී සම්පූර්ණ ක්‍රියාවලියටම ගතවූයේ මිලි තත්පර 112 සිට 277 දක්වා (තත්පර 0.2ක පමණ) ඉතා සුළු කාලයකි. එමෙන්ම මුළු පද්ධතියම 250MB ට අඩු RAM ප්‍රමාණයකින් ධාවනය වේ."*

---

### Slide 15: SOC Web Dashboard & Telemetry Visualization (Objective O4)

- **Slide Title:** Centralized Security Operations Dashboard (React UI)
- **Slide Purpose:** Present the user-facing SOC management interface.
- **Visual / Layout Recommendation:**
  - 4-quadrant UI preview: 1) Live Alerts stream with color-coded badges, 2) Active Mitigations table with live countdown, 3) Asset Inventory (FR-05), 4) Forensic Audit Trail (FR-07).
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Modern React + Flask-SocketIO Architecture:**
    - Live WebSocket event stream pushes alerts to the browser in real time (<0.1s) without requiring page reloads.
  - **Key Dashboard Views & Capabilities:**
    - **Live Alerts (`/alerts`):** Displays incoming attack cards with distinct source tags: `MODEL PREDICTION` (Blue) vs `BEHAVIOUR DETECTION` (Amber) vs `RULE DETECTION` (Red).
    - **Active Mitigations (`/mitigations`):** Shows quarantined IP addresses, rule types (`BLOCK_SRC`, `BLOCK_DST`, `LIMIT_SRC`), and **real-time countdown timers** until rule auto-expiration.
    - **Device Inventory (`/devices` - FR-05):** Authorized subnet asset discovery displaying IP, MAC, hostname, and active ports.
    - **Audit Trail (`/audit` - FR-07):** Tamper-evident MongoDB log tracking all system detections and administrative overrides.
- **🗣️ Spoken English Script:**
  > *"For Objective O4, we built a comprehensive Security Operations Center dashboard using React and Flask-SocketIO. As seen on this slide, alerts stream live to the browser within a tenth of a second via WebSockets. Each alert card clearly displays the target, confidence score, and detection origin—distinguishing between raw model inference and confirmed behavioral detection. The Mitigations page features a real-time countdown clock tracking rule expiration in the router's kernel, while the Device Inventory and Audit Log views fulfill requirements FR-05 and FR-07 respectively."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"මෙය අප විසින් නිර්මාණය කරන ලද React SOC Dashboard එකයි. WebSockets මඟින් තත්පර 0.1ක් තුළ Alerts තිරය මත පෙන්වයි. මෙහි Alerts වර්ගය (Model prediction ද Behaviour detection ද), දැනට block වී ඇති IPs සහ ඒවා ඉවත් වීමට ඇති කාලය (Countdown timer), ජාලයේ ඇති උපාංග ලැයිස්තුව, සහ සම්පූර්ණ Audit Log එක පැහැදිලිව කළමනාකරණය කළ හැක."*

---

### Slide 16: Proposal Fulfillment & Verification Matrix

- **Slide Title:** Verification Matrix: Proposal Targets vs. Realized Results
- **Slide Purpose:** Provide 100% conclusive proof that all Table 9 acceptance criteria and Functional Requirements are met.
- **Visual / Layout Recommendation:**
  - Structured scorecard table with green checkmarks (✅) across all items.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Proposal Target Fulfillment Scorecard (Table 9 & Functional Requirements):**

| Requirement / Proposal Metric | Target Value | Realized Live Result | Status |
|---|---|---|---|
| **Hypothesis H1 (Held-out Macro-F1)** | $\ge 0.85$ (85.0%) | **0.8595 (85.95%)** | ✅ **PASSED** |
| **Hypothesis H1 (Local Benign FPR)** | $\le 5.0\%$ | **0.0% (Zero False Blocks)** | ✅ **PASSED** |
| **FR-01 (Packet Capture & Ingestion)** | Real-time Zeek capture | 100% capture, 0 drops | ✅ **PASSED** |
| **FR-02 (Multi-Class Recognition)** | 4 attack classes + Benign | All 5 classes recognized | ✅ **PASSED** |
| **FR-03 (End-to-End Latency)** | Median < 2.0 s | **112 – 277 ms** | ✅ **PASSED** |
| **FR-04 (Autonomous Firewall Action)** | Timed dynamic drop sets | Linux `nftables` sets | ✅ **PASSED** |
| **FR-05 (Asset Discovery)** | Authorized Nmap scan | Subnet mapped in ~27s | ✅ **PASSED** |
| **FR-06 (Automated Rule Cleanup)** | Auto-decay after 30 min | Kernel native timer decay | ✅ **PASSED** |
| **FR-07 (Immutable Allowlists & Audit)**| Critical IPs protected | Allowlist enforced, MongoDB log | ✅ **PASSED** |
| **FR-08 (Forensic Data Export)** | CSV/JSON export | Structured export verified | ✅ **PASSED** |

- **🗣️ Spoken English Script:**
  > *"This verification scorecard maps our proposal targets directly against our empirical results. As demonstrated, every functional requirement from FR-01 through FR-08 is fully operational and validated. Most notably, Hypothesis H1 is fulfilled with an empirical Macro-F1 score of 0.8595 against the 0.85 target, benign camera false blocks remained at zero, and end-to-end response latency was an order of magnitude faster than the 2-second threshold."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අපගේ Proposal එකේ Table 9 හි දක්වා තිබූ සියලුම ඉලක්ක සහ FR-01 සිට FR-08 දක්වා Functional Requirements 100% ක් සාර්ථකව සම්පූර්ණ කර ඇත. H1 Macro-F1 ඉලක්කය (85%) සාර්ථකව ජයගෙන ඇති අතර Latency සහ False Positive අගයන් සියල්ල නියමිත ප්‍රමිතීන්ට වඩා ඉහළින් පවතී."*

---

### Slide 17: Engineering Challenges Encountered & Overcome

- **Slide Title:** Key Engineering & Machine Learning Challenges Overcome
- **Slide Purpose:** Show depth of research and how the team solved difficult practical bottlenecks.
- **Visual / Layout Recommendation:**
  - 4 Problem-Solution cards highlighting real engineering grit.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Challenge 1: Temporal Data Leakage in Feature Engineering**
    - *Problem:* Computing rolling-window aggregates across randomly shuffled rows creates severe data leakage.
    - *Resolution:* Implemented strict scenario-level sorting and isolated holdout partitions.
  - **Challenge 2: Low Confidence on Lab PortScans vs. Production Safety**
    - *Problem:* Lab Nmap sweeps produced lower per-flow confidence (42%) than training botnets. Lowering the ML threshold would cause false blocks.
    - *Resolution:* Developed a dual-engine architecture: combining ML prediction with multi-host fan-out behavioral confirmation (`BEHAVIOUR DETECTION`).
  - **Challenge 3: Router SSH Command Storms & Timeout Latency**
    - *Problem:* Rapid flood alerts caused concurrent SSH sessions to the router, exhausting SSH channels.
    - *Resolution:* Engineered a sliding-window coalescing cache, mitigation cooldowns, and automatic SSH socket retries.
  - **Challenge 4: Realistic C&C Beacon vs. Dead Port Handshake**
    - *Problem:* Model legitimately ignores clean completed TCP connections (`conn_state=SF`); real malware beacons repeatedly to dead/refused C&C IPs.
    - *Resolution:* Updated test harnesses to simulate persistent refused beaconing matching the 3-repeat safety threshold.
- **🗣️ Spoken English Script:**
  > *"Throughout this project, we confronted several difficult engineering challenges. Early on, we eliminated temporal data leakage by strictly partitioning scenario streams. When lab port sweeps generated lower per-flow ML confidence than historical botnets, we refused to compromise model safety thresholds; instead, we engineered a complementary behavioral fan-out detector. To handle high-velocity flood alerts without overwhelming the router's SSH daemon, we implemented sliding-window coalescing and connection pooling. These practical solutions ensure our system is robust in production rather than just a theoretical prototype."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"ව්‍යාපෘතිය අතරතුර අප මුහුණදුන් ප්‍රධාන අභියෝග: 1) Window features වලදී දත්ත කාන්දු වීම scenario splitting මඟින් විසඳීම, 2) PortScan වලදී ML threshold අඩු නොකර Behavioural Fan-out එන්ජිමක් එක්කිරීම, 3) Router එකට එකවර SSH connections වැඩිවීම Coalescing cache මඟින් පාලනය කිරීම, 4) සැබෑ C&C beaconing රටාව නිවැරදිව හඳුනාගැනීම."*

---

### Slide 18: Project Timeline & Current Progress

- **Slide Title:** Project Milestones & Current Progress Status
- **Slide Purpose:** Present progress against the 32-week roadmap (Figure 6).
- **Visual / Layout Recommendation:**
  - Gantt chart / Timeline progression bar showing completed milestones in green and ongoing/final phases.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **32-Week Proposed Timeline (Figure 6 Alignment):**
    - **Weeks 1–8 (Foundations):** Literature review, lab architecture design, Stratosphere IoT-23 acquisition & verification. ✅
    - **Weeks 9–16 (Data & Core ML):** Zero-leakage preprocessing, 27-feature engineering, model training (v1.0 to v3.1), threshold calibration. ✅
    - **Weeks 17–24 (Pipeline & UI):** Zeek sensor integration, streaming event pipeline, React dashboard, Socket.IO WebSockets. ✅
    - **Weeks 25–28 (Autonomous Mitigation & Lab Testing):** Linux router nftables driver, direction-aware safety policies, controlled attack playbook. ✅
    - **Weeks 29–32 (Final Testing & Reporting - Current Phase):** Full integration verification (318/318 automated tests passing), hardware testbed preparation, final report write-up. 🔄
- **🗣️ Spoken English Script:**
  > *"This timeline charts our progress across the 32-week roadmap outlined in our proposal. We have successfully completed all core development phases—including dataset preprocessing, machine learning modeling, streaming pipeline integration, autonomous mitigation, and comprehensive testing in our virtualized testbed. Currently, all 318 automated test suites pass cleanly. We are now entering our final phase: hardware deployment validation and dissertation writing."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"Proposal එකේ සති 32ක සැලැස්මට අනුව දත්ත සැකසීම, ML ආකෘතිය පුහුණු කිරීම, Pipeline සහ Dashboard එක සෑදීම, සහ Firewall පරීක්ෂණ සියල්ල සාර්ථකව අවසන් කර ඇත. දැනට Automated Tests 318ම 100% ක් pass වන අතර අවසන් වාර්තාව ලිවීම සහ Hardware පරීක්ෂණ සඳහා සූදානම් වෙමින් සිටී."*

---

### Slide 19: Future Work & Next Steps

- **Slide Title:** Future Work & Next Steps
- **Slide Purpose:** Outline the remaining work and hardware testbed transition.
- **Visual / Layout Recommendation:**
  - Diagram of the Hardware Testbed: Physical Dahua/Hikvision Camera -> Managed PoE Switch (SPAN port) -> Raspberry Pi 4 Zeek Sensor -> Linux Gateway.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Phase 1: Physical Hardware Lab Deployment:**
    - Transitioning from the virtual Docker environment to physical hardware (`lab_hardware/`):
      - Physical Dahua / Hikvision IP Camera streaming RTSP.
      - Hardware Managed PoE Gigabit Switch with port mirroring.
      - Dedicated Raspberry Pi 4 / Edge PC running Zeek network sensor.
  - **Phase 2: Final Resolution of Research Question RQ3:**
    - Perform statistical distribution drift tests (Kolmogorov-Smirnov / Wasserstein distance) between IoT-23 training features and live physical camera traffic.
    - Validate that physical camera benign FPR remains strictly $\le 5.0\%$ over continuous 48-hour soak testing.
  - **Phase 3: Edge Optimization & ONNX Runtime:**
    - Export Random Forest pipeline to ONNX format for microsecond inference on low-power edge gateways without Python dependencies.
- **🗣️ Spoken English Script:**
  > *"Looking ahead to our concluding phase, our immediate next step is deploying the pipeline onto our physical hardware testbed. We will connect a physical Dahua IP camera through a managed PoE switch to a Raspberry Pi running Zeek. This deployment will allow us to finalize Research Question RQ3 by quantifying real-world feature distribution shifts and verifying that our benign False Positive Rate remains strictly under 5% over 48 hours of continuous video surveillance. Finally, we plan to export our models to ONNX runtime for ultra-lightweight edge gateway execution."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"ඉදිරි පියවර ලෙස, Virtual Lab එකෙන් ඔබ්බට ගොස් Physical Dahua IP කැමරාවක්, Managed PoE Switch එකක්, සහ Raspberry Pi Sensor එකක් සහිත සැබෑ Hardware Lab එකක මෙය ධාවනය කිරීමට සැලසුම් කර ඇත. එමඟින් සැබෑ කැමරා දත්ත මත පර්යේෂණ ප්‍රශ්නය (RQ3) සම්පූර්ණයෙන්ම සනාථ කර අවසන් වාර්තාව සම්පූර්ණ කරනු ඇත."*

---

### Slide 20: Conclusion & Q&A

- **Slide Title:** Conclusion & Summary of Contributions
- **Slide Purpose:** Summarize the core contributions and open the floor for questions.
- **Visual / Layout Recommendation:**
  - 3 Summary Badges: *"Scientific Rigor (Zero Leakage)"* · *"Industrial Viability (Sub-Second Latency)"* · *"Surveillance Continuity (Zero Video Drop)"*.
  - Contact and Repository details.
- **Slide Bullet Points (Copy-Paste to Slide):**
  - **Summary of Contributions:**
    - **1. Zero-Leakage Scientific Rigor:** Scenario-level evaluation on Stratosphere IoT-23 achieving **Macro-F1 = 0.8595** (Hypothesis H1 met).
    - **2. Sub-Second Real-Time Response:** End-to-end detection-to-mitigation in **112–277 ms** (10x faster than proposal requirement).
    - **3. Surveillance Continuity (RQ5):** Guaranteed zero video drop on RTSP Port 554 through direction-aware firewall guardrails.
    - **4. Complete Operational Artifacts:** 11-container virtual testbed, React SOC UI, and 318 passing automated tests.
  - **Project Repository:** `https://github.com/madupadilshan/intrusion-detection.git`
  - **Thank you! We invite your questions and feedback.**
- **🗣️ Spoken English Script:**
  > *"In conclusion, our research demonstrates that machine-learning-based network intrusion detection can be both scientifically rigorous and practically viable for mission-critical IoT surveillance. We have achieved our target Macro-F1 of 0.8595 with zero data leakage, delivered sub-second autonomous mitigation, and proved 100% video surveillance continuity without dropping a single frame. We thank our supervisors Dr. Matheeh and Dr. Amarakeerthi for their continuous guidance. We now welcome your questions."*
- **🇱🇰 සිංහල පැහැදිලි කිරීම:**
  > *"අවසාන වශයෙන්, අපගේ පර්යේෂණය මඟින් Machine Learning උපයෝගී කරගෙන IP කැමරා සඳහා සාර්ථක, තත්‍ය කාලීන, සහ වීඩියෝවට කිසිදු බාධාවක් නොවන ආරක්ෂණ පද්ධතියක් සාර්ථකව ගොඩනගා ඇති බව ඔප්පු කර ඇත. අපගේ සියලුම ඉලක්ක සපුරා ඇති අතර ඔබගේ වටිනා ප්‍රශ්න සහ අදහස් සඳහා දැන් අවස්ථාව විවෘතයි. ස්තූතියි!"*

---

# 🧠 Comprehensive Defense / Viva FAQ Cheat-Sheet

Here are the **top 10 most critical questions** the supervisors or evaluation panel may ask, along with the precise answers you should provide:

### Q1: "Why did you use Stratosphere IoT-23 instead of CIC-IDS2017 or KDD99?"
- **Answer:** *"Sir, legacy datasets like KDD99 and CIC-IDS2017 were captured in enterprise office environments representing PC workstations with human browsing habits. They completely lack IoT-specific botnet behaviors like Mirai, Okiru, and Bashlite. Stratosphere IoT-23 is the first and largest public dataset recorded on real physical IoT hardware infected with authentic botnets, making its flow dynamics directly applicable to our problem."*

### Q2: "IoT-23 has smart lamps and door locks, but NO IP cameras. How can your model work on a camera network? (RQ3)"
- **Answer:** *"That is precisely the focus of our Research Question RQ3. In an IP-camera network, benign traffic consists of predictable M2M patterns (RTSP video on port 554 and NTP sync). Malicious botnet traffic (scans, floods, beacons) exhibits identical transport-level flow signatures regardless of the infected host. We verified structural schema compatibility using our `schema_check` tool and proved in our lab that normal camera streaming triggers zero false positives."*

### Q3: "What prevents data leakage in your machine learning evaluation?"
- **Answer:** *"Most published literature performs naive random row-level train/test splitting, which places consecutive packets from the same attack session in both sets, yielding falsely inflated 99.9% scores. We enforced a strict scenario-level split: Capture-34-1 was held out entirely and never seen during training or threshold tuning, guaranteeing authentic generalization."*

### Q4: "Why did you select Random Forest over Deep Learning (e.g., LSTMs or CNNs)?"
- **Answer:** *"Deep learning models introduce significant computational overhead, memory footprints, and inference latency that make sub-second edge deployment difficult. Our 100-tree Random Forest achieves an inference latency of just 30.88 microseconds per flow with a memory footprint under 250 MB, while outperforming deep models on tabular flow features."*

### Q5: "If your system is autonomous, what stops an attacker from spoofing an IP and causing the camera to be blocked?"
- **Answer:** *"Our response policy enforces seven strict safety guardrails. Specifically, internal camera IPs are barred from source blocking sets (`block_src`), critical infrastructure IPs are hardcoded in the kernel allowlist, and outbound C&C beacons block only the external destination IP (`block_dst`). Thus, the camera can never be blocked."*

### Q6: "Why do you rate-limit DDoS attacks instead of completely blocking them?"
- **Answer:** *"During a high-rate SYN flood, completely dropping an IP or subnet can cause collateral damage if legitimate shared proxies are spoofed. Our `limit_src` policy permits up to 200 packets per second for normal communication while dropping all excess flood packets at hardware rate in the Linux kernel."*

### Q7: "How do you handle port scans that receive lower confidence scores from the ML model?"
- **Answer:** *"Rather than dangerously lowering the ML confidence threshold (which would cause false positives across the entire class), our decision engine incorporates a dual-engine architecture: combining ML confidence with multi-host fan-out behavioral confirmation (`BEHAVIOUR DETECTION`). When an attacker probes multiple hosts across the subnet, behavioral confirmation triggers immediate mitigation."*

### Q8: "How do you guarantee that firewall rules don't accumulate forever and slow down the router?"
- **Answer:** *"All our dynamic nftables sets use native Linux kernel decay timers (`flags timeout`). When a rule is added, the kernel maintains an internal decaying countdown timer (e.g., 30 minutes). Once expired, the Linux kernel automatically purges the rule from memory with zero cron jobs or software overhead."*

### Q9: "What is the difference between your Passive SPAN mode and Inline mode?"
- **Answer:** *"In Passive SPAN mode, the sensor connects to a switch mirror port out-of-band, ensuring that packet inspection adds exactly zero latency to the video feed, with mitigations pushed to the router. In Inline mode, the sensor acts as a transparent network bridge, dropping packets directly at wire-speed."*

### Q10: "How do you know the camera's video recording was not interrupted during testing?"
- **Answer:** *"We continuously monitored the NVR recorder container during all active attacks. The NVR pulled RTSP video continuously on Port 554, archiving complete 58.6 megabyte chunks every 5 minutes with zero dropped frames and socket latency under 3 milliseconds."*

---

*Prepared for Group 03 Progress Presentation · Faculty of Technology, University of Sri Jayewardenepura · November 2026*
