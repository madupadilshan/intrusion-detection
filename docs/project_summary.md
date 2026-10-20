# Project Summary (one page)

**Title:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Degree:** Bachelor of ICT Honours — Department of ICT, Faculty of Technology, University of Sri Jayewardenepura
**Team (Group 03):** M A M Dilshan (ICT/22/824) · Dilshara W S (ICT/22/825) · A O P I Mendis (ICT/22/953)
**Supervisors:** Dr A.A.M. Matheeh (main) · Dr Senaka Amarakeerthi (co-supervisor, external)
**Source:** Research Proposal, July 2026 (Section 1.5, Table 3). The aim, objectives, hypothesis and research questions below use the proposal's own words.

---

**Aim:** To design and test a real-time machine-learning system for intrusion detection and controlled response in small IP-camera IoT networks.

**Objectives (Table 3)**

| ID | What we will do | How we will show it |
| -- | --------------- | ------------------- |
| O1 | Build an IoT-23 preprocessing and label-mapping pipeline that anyone can repeat. | Dataset check, code with versions, and a data-quality report |
| O2 | Train and test a multi-class Random Forest with no scenario leakage. | Grouped cross-validation, and scores from a scenario we left out |
| O3 | Make flow features from live IP-camera traffic that match the dataset. | Schema check, and offline features compared with live features |
| O4 | Build the monitoring, dashboard, storage and alerts, and join them together. | Tests of the whole system, and the measured time to update |
| O5 | Build IP blocking that follows the policy, and let the admin undo it by hand. | Approved lab tests, audit log, and an unblock check |
| O6 | Test how well it detects, how fast it runs, and how much it uses. | Macro-F1, recall for each class, FPR, response time and resource use |

**Hypothesis H1:** If the IoT-23 flow features are mapped carefully and the Random Forest is trained in a scenario-aware way, then the model will reach a macro-F1 score of at least 0.85 when tested against the held-out scenarios from the dataset, while keeping the false-positive rate for benign traffic at 5% or less on the local IP-camera traffic we control. *(These are targets, not promised results.)*

**Research questions**

- **RQ1:** How well can the chosen model tell benign traffic apart from malicious IoT flows under scenario-aware validation?
- **RQ2:** How well can it sort traffic into the DDoS, scanning, C&C and malware/download classes?
- **RQ3:** Which flow features stay available and stay the same in both IoT-23 and live camera traffic made by Zeek?
- **RQ4:** How much time does the whole process take in the laboratory, from detection to dashboard, alert and blocking?
- **RQ5:** What safety rules do we need so that automatic response does not stop normal camera access?

---

**What we build (scope, Section 1.2):** Zeek turns camera-network traffic into connection flows. A Random Forest puts each flow into one of **5 classes**: Benign, DDoS/DoS, Port scan, C&C, Malware/download. A Flask + Flask-SocketIO backend stores evidence in MongoDB and pushes alerts to a React dashboard that needs a login. Nmap finds devices on the approved lab subnet. Response uses nftables (or a router/firewall adapter), only when the safety rules pass, and the admin can always unblock. It works in **passive mode** (switch mirror/SPAN; the router blocks) and in **inline mode** (the sensor blocks itself).

**Data:** official **IoT-23 v1.0.0** labelled flows (20 malicious + 3 benign scenarios; no benign device is an IP camera), plus **our own benign camera traffic** (metadata only).

**Main targets (Table 9):** macro-F1 ≥ 0.85 on the held-out scenario · FPR ≤ 5% on local camera traffic, with no blocks on the management computer or the NVR · median decision < 2 s, 95th percentile < 5 s · all important recovery tests pass · every admin action can be traced.

**Limits (Sections 1.2, 3.8):** we will not put malware on devices that are not ours; no live malware in tests; no public IP addresses, other people's cameras, vendor clouds or the university production network; no video or audio is kept; this is not a certified firewall product; we do not claim to catch every new or zero-day attack.

**Timeline:** 32 weeks (Figure 6). The team checks progress every week and meets the supervisors at least once every two weeks.
