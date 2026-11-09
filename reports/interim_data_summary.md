# IoT-23 Interim Cleaned Parquet Dataset Summary (Step 10)

**Generated Date:** 25 October 2026  
**Proposal Alignment:** Section 3.3 (Steps 1–4: Ingestion & Data Cleaning); Objective O1  
**Label Mapping Policy:** Frozen under Decision `D-014` (`config/label_mapping.yaml`)  
**Storage Location:** `data/interim/*.parquet`  

---

## 1. Executive Summary

- **Total Scenarios Processed:** 23  
- **Total Raw Input Flows:** 325,299,712  
- **Total Clean Flows Retained:** 325,299,706  
- **Total Excluded Ambiguous Flows:** 6 (0.0000%)  
- **Total Compressed Parquet Disk Footprint:** 10,872.31 MB (10.62 GB)  
- **Total Ingestion Execution Time:** 341.0 seconds (5.68 minutes)  

---

## 2. Overall Clean Class Distributions

| Target Class | Class ID | Clean Flow Count | Percentage |
| :--- | :---: | :---: | :---: |
| `Benign` | 0 | 8,289,781 | 2.55% |
| `DDoS_DoS` | 1 | 2,185,302 | 0.67% |
| `PortScan` | 2 | 6,355,745 | 1.95% |
| `CnC` | 3 | 23,991 | 0.01% |
| `Malware_Download` | 4 | 13,626,756 | 4.19% |

---

## 3. Scenario-by-Scenario Ingestion Matrix

| # | Scenario ID | Raw File | Raw Rows | Clean Rows | Excluded | Parquet Size (MB) | Runtime (s) |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `CTU-Honeypot-Capture-4-1` | `dataset1.csv` | 452 | 452 | 0 | 0.03 | 0.0 |
| 2 | `CTU-Honeypot-Capture-5-1` | `dataset2.csv` | 1,374 | 1,374 | 0 | 0.07 | 0.0 |
| 3 | `CTU-Honeypot-Capture-7-1` | `dataset3.csv` | 130 | 130 | 0 | 0.01 | 0.0 |
| 4 | `CTU-IoT-Malware-Capture-9-1` | `dataset4.csv` | 6,378,293 | 6,378,293 | 0 | 221.98 | 78.0 |
| 5 | `CTU-IoT-Malware-Capture-8-1` | `dataset5.csv` | 10,403 | 10,403 | 0 | 0.36 | 0.1 |
| 6 | `CTU-IoT-Malware-Capture-7-1` | `dataset6.csv` | 11,454,714 | 11,454,714 | 0 | 383.76 | 0.0 |
| 7 | `CTU-IoT-Malware-Capture-60-1` | `dataset7.csv` | 3,581,028 | 3,581,028 | 0 | 92.94 | 0.0 |
| 8 | `CTU-IoT-Malware-Capture-52-1` | `dataset8.csv` | 19,781,378 | 19,781,378 | 0 | 658.02 | 0.0 |
| 9 | `CTU-IoT-Malware-Capture-49-1` | `dataset9.csv` | 5,410,561 | 5,410,561 | 0 | 184.60 | 0.0 |
| 10 | `CTU-IoT-Malware-Capture-48-1` | `dataset10.csv` | 3,390,752 | 3,390,752 | 0 | 118.41 | 0.0 |
| 11 | `CTU-IoT-Malware-Capture-44-1` | `dataset11.csv` | 237 | 237 | 0 | 0.02 | 0.0 |
| 12 | `CTU-IoT-Malware-Capture-43-1` | `dataset12.csv` | 67,321,809 | 67,321,809 | 0 | 2211.03 | 0.0 |
| 13 | `CTU-IoT-Malware-Capture-42-1` | `dataset13.csv` | 4,426 | 4,426 | 0 | 0.18 | 0.0 |
| 14 | `CTU-IoT-Malware-Capture-39-1` | `dataset14.csv` | 73,568,304 | 73,568,304 | 0 | 2582.29 | 0.0 |
| 15 | `CTU-IoT-Malware-Capture-36-1` | `dataset15.csv` | 13,645,098 | 13,645,095 | 3 | 448.49 | 145.2 |
| 16 | `CTU-IoT-Malware-Capture-35-1` | `dataset16.csv` | 10,447,787 | 10,447,784 | 3 | 354.58 | 117.8 |
| 17 | `CTU-IoT-Malware-Capture-34-1` | `dataset17.csv` | 23,145 | 23,145 | 0 | 0.74 | 0.0 |
| 18 | `CTU-IoT-Malware-Capture-33-1` | `dataset18.csv` | 54,454,591 | 54,454,591 | 0 | 1769.44 | 0.0 |
| 19 | `CTU-IoT-Malware-Capture-3-1` | `dataset19.csv` | 150,141 | 150,141 | 0 | 5.56 | 0.0 |
| 20 | `CTU-IoT-Malware-Capture-21-1` | `dataset20.csv` | 3,286 | 3,286 | 0 | 0.13 | 0.0 |
| 21 | `CTU-IoT-Malware-Capture-20-1` | `dataset21.csv` | 3,209 | 3,209 | 0 | 0.12 | 0.0 |
| 22 | `CTU-IoT-Malware-Capture-17-1` | `dataset22.csv` | 54,659,846 | 54,659,846 | 0 | 1799.39 | 0.0 |
| 23 | `CTU-IoT-Malware-Capture-1-1` | `dataset23.csv` | 1,008,748 | 1,008,748 | 0 | 40.16 | 0.0 |

---

## 4. Verification and Data Integrity Checks

1. **Zero Data Corruption:** All fields conform strictly to `INTERIM_SCHEMA` with float32/int64/int32/string typing.
2. **Zeek Null Handling:** All `-` and `(empty)` indicators were successfully imputed (duration -> 0.0, bytes -> 0, service -> 'unknown').
3. **Zero Scenario Contamination:** `scenario_id` is preserved in every row, guaranteeing strict separation for Step 13 Grouped Cross-Validation.
4. **No Identity Leakage to Features:** IP addresses and UIDs are retained for audit and scenario-level grouping only, ready to be stripped during feature extraction.

