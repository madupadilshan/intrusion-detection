# Literature Notes

**Started:** 20 October 2026 (guide Step 0). Keep adding to this file until about week 8 (proposal Figure 6).

**How to use this file:** each paper has the same short parts:

- **Reference:** Harvard style, as in the proposal.
- **What they did**
- **Data**
- **Main result**
- **Limit / gap:** why our project is still needed.
- **How we use it:** which part of our work it supports.

**Rule:** write only what the paper really says. If you have not checked something in the paper itself, mark it **(to check)**.

**Status of each reference:**

| # | Reference | In proposal list? | Notes checked against |
| - | --------- | ----------------- | --------------------- |
| 1 | Antonakakis et al. (2017) | Yes | Proposal 2.1, Table 4 |
| 2 | Biondi, Bognanni and Bella (2022) | Yes | arXiv abstract (2202.06597) |
| 3 | Breiman (2001) | Yes | Proposal 1.3, 2.4 |
| 4 | Fagan et al. (2020), NISTIR 8259A | Yes | Proposal 2.1 |
| 5 | Garcia, Parmisano and Erquiaga (2020), IoT-23 | Yes | Proposal 2.3; dataset page |
| 6 | Gyamfi and Jurcut (2022) | Yes | Proposal 2.2, Table 4 |
| 7 | Moustafa and Slay (2015), UNSW-NB15 | Yes | Proposal 2.3, Table 4 |
| 8 | Sharafaldin, Habibi Lashkari and Ghorbani (2018), CICIDS2017 | Yes | Proposal 2.3, Table 4 |
| 9 | Vitorino et al. (2022) | Yes | arXiv abstract (2111.13149) |
| 10 | Yang et al. (2022) | Yes | Proposal 2.2 |
| 11 | Zeek Project (2026), conn.log | Yes | Proposal 2.5; Zeek docs |
| 12 | **Santos et al. (2023)** | **No — missing** | **Found and checked** (Crossref, abstract) |
| 13 | **Almashhadani et al. (2024)** | **No — missing** | **Not found → removed, not cited** (decision D-009) |

---

## A. References in the proposal's reference list

### 1. Antonakakis et al. (2017) — Mirai botnet

- **Reference:** Antonakakis, M., April, T., Bailey, M., Bernhard, M., Bursztein, E., Cochran, J., Durumeric, Z., Halderman, J.A., Invernizzi, L., Kallitsis, M., Kumar, D., Lever, C., Ma, Z., Mason, J., Menscher, D., Seaman, C., Sullivan, N., Thomas, K. and Zhou, Y. (2017) 'Understanding the Mirai Botnet', *26th USENIX Security Symposium*, pp. 1093–1110.
- **What they did:** a large measurement study of how the Mirai botnet grew, which devices it infected, and how it was used for DDoS attacks.
- **Data:** many network measurements collected over months (for example network-telescope traffic and DNS data) **(to check: the full list of data sources)**.
- **Main result:** Mirai reached a peak of about **600,000 infected devices**. It spread through IoT devices left open with weak or default credentials, and it was used for very large DDoS attacks.
- **Limit / gap:** it explains the threat, but it does **not** build an IDS for IP cameras (proposal Table 4).
- **How we use it:** the motivation (Sections 1.1, 2.1). It is the reason we watch both **incoming** scanning/flooding and **outgoing** traffic that could show a taken-over camera (C&C class).

### 2. Biondi, Bognanni and Bella (2022) — penetration test of an IP camera

- **Reference:** Biondi, P., Bognanni, S. and Bella, G. (2022) 'Vulnerability Assessment and Penetration Testing on IP Cameras', *arXiv preprint* arXiv:2202.06597.
- **What they did:** a vulnerability assessment and penetration test of one consumer IP camera, the **TP-Link Tapo C200**.
- **Data:** hands-on tests on the real device.
- **Main result:** three weaknesses — **denial of service**, **video eavesdropping**, and a new attack they call **"Motion Oracle"**. They propose countermeasures that use a **Raspberry Pi** as an extra device on the network.
- **Limit / gap:** only **one camera model**, so it cannot speak for every camera (proposal 2.1, Table 4).
- **How we use it:** it shows why a **separate network-level protection layer** is useful, instead of trusting only the camera firmware. It supports the DoS class and our "metadata only, no video" design.

### 3. Breiman (2001) — Random Forests

- **Reference:** Breiman, L. (2001) 'Random Forests', *Machine Learning*, 45(1), pp. 5–32. doi:10.1023/A:1010933404324.
- **What they did:** introduced the Random Forest. Many decision trees are each trained on a **bootstrap sample** and a **random subset of features**, and they **vote** together.
- **Data:** benchmark datasets **(to check: which ones)**.
- **Main result:** the voting lowers the variance of a single tree. The method gives good accuracy and can estimate how important each feature is.
- **Limit / gap:** the class probabilities **may not be well calibrated**, and the built-in feature importance can give too much weight to features with many values (proposal 2.4).
- **How we use it:** the reason for our main model (proposal 1.3). It is also why we check **calibration** (reliability curve, Brier score) and use **permutation importance** (guide Step 17).

### 4. Fagan et al. (2020) — NISTIR 8259A

- **Reference:** Fagan, M., Megas, K.N., Scarfone, K. and Smith, M. (2020) *IoT Device Cybersecurity Capability Core Baseline*. NISTIR 8259A. Gaithersburg, MD: National Institute of Standards and Technology. doi:10.6028/NIST.IR.8259A.
- **What they did:** defined a basic set of cybersecurity abilities that IoT devices should have.
- **Data:** a standards document (no dataset).
- **Main result:** six abilities — device **identification**, device **configuration**, **data protection**, **logical access** to interfaces, **software update**, and **cybersecurity state awareness**.
- **Limit / gap:** a network IDS cannot add these abilities **inside** the camera (proposal 2.1).
- **How we use it:** our IDS is **one layer of defence-in-depth**. It gives extra evidence about the network when device management is weak. It supports, but does not replace, segmentation, passwords and patching.

### 5. Garcia, Parmisano and Erquiaga (2020) — IoT-23 dataset

- **Reference:** Garcia, S., Parmisano, A. and Erquiaga, M.J. (2020) *IoT-23: A labeled dataset with malicious and benign IoT network traffic*, Version 1.0.0 [Dataset]. Zenodo. doi:10.5281/zenodo.4743746.
- **What they did:** recorded and labelled real IoT network traffic at the **Stratosphere Laboratory** (2018–2019).
- **Data:** **23 captures**: **20 malicious** (malware run in a controlled IoT setup) and **3 benign**. The benign devices are a **smart lamp**, a **voice assistant** and a **smart door lock**. The flows come as Zeek `conn.log.labeled` files, with a `label` and a `detailed-label` column.
- **Main result:** a public dataset of real labelled flows with detailed behaviour labels (for example `PartOfAHorizontalPortScan`, `C&C-HeartBeat`, `DDoS`, `Okiru`).
- **Limit / gap:** **none of the benign devices is an IP camera** (proposal 2.3, Table 4).
- **How we use it:** our training data (guide Steps 7–18). Because there is no camera in it, we must also collect **our own benign camera traffic** (Step 20) and measure the FPR there (H1).

### 6. Gyamfi and Jurcut (2022) — review of IoT IDS

- **Reference:** Gyamfi, E. and Jurcut, A. (2022) 'Intrusion Detection in Internet of Things Systems: A Review on Design Approaches Leveraging Multi-Access Edge Computing, Machine Learning, and Datasets', *Sensors*, 22(10), 3744. doi:10.3390/s22103744.
- **What they did:** reviewed machine-learning NIDS designs for IoT: **where** the IDS is placed, **which datasets** are used, and **how performance is measured**.
- **Data:** a literature review (no new dataset).
- **Main result:** supports monitoring **at the edge or at network level**, because many IoT devices are too small to run heavy security software themselves.
- **Limit / gap:** a wide review, but it does **not** build a joined-up response prototype like ours (proposal Table 4).
- **How we use it:** supports our design choice: a **separate Linux sensor** watches the network, instead of software on the camera.

### 7. Moustafa and Slay (2015) — UNSW-NB15

- **Reference:** Moustafa, N. and Slay, J. (2015) 'UNSW-NB15: A Comprehensive Data Set for Network Intrusion Detection Systems (UNSW-NB15 Network Data Set)', *2015 Military Communications and Information Systems Conference (MilCIS)*, Canberra, Australia, pp. 1–6. doi:10.1109/MilCIS.2015.7348942.
- **What they did:** built a general network intrusion benchmark in a controlled testbed.
- **Data:** about **2.5 million records**, **nine attack families**, and **49 features** made with the **Argus** and **Bro/Zeek** tools.
- **Main result:** a widely used, carefully made NIDS benchmark.
- **Limit / gap:** **not IoT traffic**. Its benign side is office traffic, not camera traffic (proposal 2.3, Table 4).
- **How we use it:** **reference only**, for feature design. Part of its features come from **Bro (the old name of Zeek)**, the tool we use. **No model is trained on it.**

### 8. Sharafaldin, Habibi Lashkari and Ghorbani (2018) — CICIDS2017

- **Reference:** Sharafaldin, I., Habibi Lashkari, A. and Ghorbani, A.A. (2018) 'Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization', *Proceedings of the 4th International Conference on Information Systems Security and Privacy (ICISSP)*, pp. 108–116. doi:10.5220/0006639801080116.
- **What they did:** made a labelled intrusion dataset with many attack types.
- **Data:** **five days** of labelled traffic, covering brute force, DoS, DDoS, web attacks, infiltration, port scanning and botnet activity. More than **80 flow features** made by **CICFlowMeter**.
- **Main result:** a widely used, carefully made benchmark.
- **Limit / gap:** **not IoT traffic**. CICFlowMeter features are **not the same as Zeek `conn.log`**, which would add a second feature-matching problem (proposal 2.3, Table 4).
- **How we use it:** **reference only**, for evaluation practice. **No model is trained on it.** (The old prototype's CICIDS2017 model is archived for this reason.)

### 9. Vitorino et al. (2022) — comparing ML methods on IoT-23

- **Reference:** Vitorino, J., Andrade, R., Praça, I., Sousa, O. and Maia, E. (2022) 'A Comparative Analysis of Machine Learning Techniques for IoT Intrusion Detection', in *Foundations and Practice of Security*, Lecture Notes in Computer Science, vol. 13291, pp. 191–207. Springer. doi:10.1007/978-3-031-08147-7_13.
- **What they did:** compared **supervised, unsupervised and reinforcement-learning** methods on **nine malware captures of IoT-23**, for binary and multi-class classification.
- **Data:** nine IoT-23 malware captures.
- **Main result:** they tested SVM, XGBoost, **LightGBM**, Isolation Forest, Local Outlier Factor and a Double Deep Q-Network model. **LightGBM was the most reliable.** Isolation Forest did well at anomaly detection.
- **Limit / gap:** it looks at the **algorithms**, not at live response and safe blocking (proposal Table 4).
- **How we use it:** we must **not assume** that Random Forest is the best. This is why we compare it with a **linear model** and **one gradient-boosting model** (guide Step 15).

### 10. Yang et al. (2022) — review of anomaly-based NIDS

- **Reference:** Yang, Z., Liu, X., Li, T., Wu, D., Wang, J., Zhao, Y. and Han, H. (2022) 'A systematic literature review of methods and datasets for anomaly-based network intrusion detection', *Computers & Security*, 116, 102675. doi:10.1016/j.cose.2022.102675.
- **What they did:** reviewed **119 well-known** anomaly-detection studies.
- **Data:** a systematic literature review.
- **Main result:** the same problems appear again and again in **preprocessing, datasets, evaluation**, and moving between different **domains**.
- **Limit / gap:** a review; it does not build a system.
- **How we use it:** the main reason for **grouping flows by scenario** and keeping **one scenario out** for testing (proposal 2.2). A random row split puts very similar flows from one capture in both training and test data, so the score looks better than it really is (guide Step 13; the old prototype's accuracy of 1.00 is an example).

### 11. Zeek Project (2026) — conn.log documentation

- **Reference:** Zeek Project (2026) 'conn.log', *Book of Zeek*. Available at: https://docs.zeek.org/en/v8.1.2/logs/conn.html (Accessed: 13 July 2026).
- **What it is:** the official documentation of Zeek's connection log.
- **Main points:** Zeek makes connection records for **TCP, UDP and ICMP**, with fields such as the endpoints, protocol, service, duration, byte and packet counts, `conn_state` and `history`. A record is written when a connection **ends or times out**.
- **Limit / gap:** Zeek and IoT-23 may not compute every field in the same way (timeouts, state values, byte totals). **We must measure this; we cannot assume it** (proposal 2.5, Table 4).
- **How we use it:** our live feature tool (guide Steps 19–22) and the **schema check** (Step 22, RQ3).

---

## B. The two references missing from the proposal's reference list

Proposal Section 1.4 says: *"This research problem is motivated by previous work showing the need for flow-based IoT intrusion detection systems that can operate in real time while remaining practical for real-world IoT environments and limiting false positives (Santos et al., 2023; Almashhadani et al., 2024)."*

Neither reference is in the proposal's reference list. We searched for both on 19–20 October 2026.

### 12. Santos et al. (2023) — ✅ FOUND AND CHECKED

- **Reference (Harvard):** Santos, L., Gonçalves, R., Rabadão, C. and Martins, J. (2023) 'A flow-based intrusion detection framework for internet of things networks', *Cluster Computing*, 26(1), pp. 37–57. doi:10.1007/s10586-021-03238-y.
- **Year note:** it was **published online on 10 February 2021**. It was printed in **volume 26, issue 1 (February 2023)**. The proposal's "2023" follows the issue year. Some databases list it as 2021. Use one year **consistently** in the final report.
- **Free copy:** http://hdl.handle.net/10198/25293 (open-access repository, CC BY-NC).
- **What they did:** proposed an **IP flow-based IDS framework** to monitor and protect IoT networks from external and internal threats **in real time**. It uses **flow features** instead of packet headers and payload. The architecture is **hybrid**: distributed data collection and centralised analysis.
- **Detection method:** **specification-based**, built from specifications of **normal traffic**. **It is not a machine-learning model.**
- **Main result:** about **100% detection success and 0% false positives** in their experiments. Compared with **Snort, Suricata and Zeek**, it used **less CPU, RAM and storage**.
- **Limit / gap:** it does not use machine learning, and it is not about IP cameras **(to check in the full text: which devices and attacks were tested)**.
- **How we use it:** it supports proposal 1.4 well: a flow-based IoT IDS can work **in real time** with **few false positives**. It also mentions **Zeek** as a comparison point.
- **Why we are sure this is the right paper:** Leonel Santos is the **first author**, the year (2023 issue) and the topic match the proposal's sentence exactly, and its abstract says "real-time", "flow-based" and "0% of false positives".
- **Another 2023 paper with Santos as co-author (not first author):** Prazeres, N., Costa, R.L.de C., Santos, L. and Rabadão, C. (2023) 'Engineering the application of machine learning in an IDS based on IoT traffic flow', *Intelligent Systems with Applications*, 17, 200189. doi:10.1016/j.iswa.2023.200189. It uses deep neural networks on IoT flows. It would be cited as "Prazeres et al., 2023", **not** "Santos et al., 2023". It may still be useful as an extra ML-based reference.

### 13. Almashhadani et al. (2024) — ❌ NOT FOUND — REMOVED (decision D-009)

**We could not find any 2024 paper by Almashhadani (or Al-Mashhadani) about IoT intrusion detection.**

What we searched:

- web searches with the name spellings "Almashhadani", "Al-Mashhadani", "AlMashhadani", plus IoT, intrusion detection and flow;
- the **Crossref** database: **94** publications by authors named Almashhadani from 2023–2025. **None** is about intrusion detection. They are about business, medicine, chemistry, solar cells and other topics.

The closest real matches, which are **not** this reference:

- Ahmad O. Almashhadani works on **network-based malware detection**, for example: Almashhadani, A.O., Kaiiali, M., Sezer, S. and O'Kane, P. (2019) 'A Multi-Classifier Network-Based Crypto Ransomware Detection System: A Case Study of Locky Ransomware', *IEEE Access*, 7, pp. 47053–47067. doi:10.1109/ACCESS.2019.2907485. It is from **2019**, and it is about **ransomware**, not IoT.
- An Almashhadani paper on **edge computing scheduling for IoT** (2023, *Materials Today: Proceedings*). It is **not** about intrusion detection.

**Decision (20 Oct 2026) — see `docs/decision_log.md`, D-009:**

- **No team member has this paper or knows its source.** So we do **not** cite "Almashhadani et al., 2024" anywhere.
- The sentence in Section 1.4 is supported by **Santos et al. (2023)** alone. In the final report it will end: "…and limiting false positives (Santos et al., 2023)."
- The full Santos et al. (2023) reference must be **added to the final report's reference list**, because it is missing from the proposal's list.
- The supervisor will be told at the next meeting.
- **Extra reading (not cited in Section 1.4):** Mutambik, I. (2024) 'An Efficient Flow-Based Anomaly Detection System for Enhanced Security in IoT Networks', *Sensors*, 24(22), 7408. doi:10.3390/s24227408. It proposes **IoT-FIDS**, a lightweight flow-based anomaly detector that builds profiles of normal device traffic. It is not a machine-learning model, and it was tested on UNSW-NB15 and BoT-IoT. It may be useful in the related-work section of the final report.

**Never cite a paper that nobody on the team has seen.** Examiners may check the references.

---

## C. Papers to add later (empty)

Add new papers here in the same format, for example papers on Zeek and IoT-23 feature matching, calibration of tree models, or IP-camera traffic.
