# IoT-23 Interim Cleaned Parquet Dataset Summary (Step 10)

**Generated Date:** 25 October 2026  
**Proposal Alignment:** Section 3.3 (Steps 1–4: Ingestion & Data Cleaning); Objective O1  
**Label Mapping Policy:** Frozen under Decision `D-014` (`config/label_mapping.yaml`)  
**Storage Location:** `data/interim/*.parquet`  

---

## 1. Executive Summary

- **Total Scenarios Processed:** 23  
- **Total Raw Input Flows:** 325,309,946  
- **Total Clean Flows Retained:** 325,299,706  
- **Total Excluded Ambiguous Flows:** 10,240 (0.0031%)  
- **Total Compressed Parquet Disk Footprint:** 10,872.31 MB (10.62 GB)  
- **Total Ingestion Execution Time:** 4443.2 seconds (74.05 minutes)  

---

## 2. Overall Clean Class Distributions

| Target Class | Class ID | Clean Flow Count | Percentage |
| :--- | :---: | :---: | :---: |
| `Benign` | 0 | 30,389,041 | 9.34% |
| `DDoS_DoS` | 1 | 19,524,319 | 6.00% |
| `PortScan` | 2 | 213,314,225 | 65.57% |
| `CnC` | 3 | 48,984 | 0.02% |
| `Malware_Download` | 4 | 60,990,792 | 18.75% |

---

## 3. Scenario-by-Scenario Ingestion Matrix

| # | Scenario ID | Raw File | Raw Rows | Clean Rows | Excluded | Parquet Size (MB) | Runtime (s) |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `CTU-Honeypot-Capture-4-1` | `dataset1.csv` | 452 | 452 | 0 | 0.03 | 0.0 |
| 2 | `CTU-Honeypot-Capture-5-1` | `dataset2.csv` | 1,374 | 1,374 | 0 | 0.07 | 0.1 |
| 3 | `CTU-Honeypot-Capture-7-1` | `dataset3.csv` | 130 | 130 | 0 | 0.01 | 0.0 |
| 4 | `CTU-IoT-Malware-Capture-8-1` | `dataset4.csv` | 6,378,293 | 6,378,293 | 0 | 221.98 | 104.2 |
| 5 | `CTU-IoT-Malware-Capture-9-1` | `dataset5.csv` | 10,403 | 10,403 | 0 | 0.36 | 0.2 |
| 6 | `CTU-IoT-Malware-Capture-7-1` | `dataset6.csv` | 11,454,714 | 11,454,714 | 0 | 383.76 | 200.7 |
| 7 | `CTU-IoT-Malware-Capture-60-1` | `dataset7.csv` | 3,581,028 | 3,581,028 | 0 | 92.94 | 45.3 |
| 8 | `CTU-IoT-Malware-Capture-52-1` | `dataset8.csv` | 19,781,378 | 19,781,378 | 0 | 658.02 | 235.8 |
| 9 | `CTU-IoT-Malware-Capture-49-1` | `dataset9.csv` | 5,410,561 | 5,410,561 | 0 | 184.60 | 61.6 |
| 10 | `CTU-IoT-Malware-Capture-48-1` | `dataset10.csv` | 3,394,338 | 3,390,752 | 3,586 | 118.41 | 37.5 |
| 11 | `CTU-IoT-Malware-Capture-44-1` | `dataset11.csv` | 237 | 237 | 0 | 0.02 | 0.1 |
| 12 | `CTU-IoT-Malware-Capture-43-1` | `dataset12.csv` | 67,321,809 | 67,321,809 | 0 | 2211.03 | 885.7 |
| 13 | `CTU-IoT-Malware-Capture-42-1` | `dataset13.csv` | 4,426 | 4,426 | 0 | 0.18 | 0.2 |
| 14 | `CTU-IoT-Malware-Capture-39-1` | `dataset14.csv` | 73,568,981 | 73,568,304 | 677 | 2582.29 | 979.0 |
| 15 | `CTU-IoT-Malware-Capture-35-1` | `dataset15.csv` | 13,645,098 | 13,645,095 | 3 | 448.49 | 197.5 |
| 16 | `CTU-IoT-Malware-Capture-36-1` | `dataset16.csv` | 10,447,787 | 10,447,784 | 3 | 354.58 | 139.3 |
| 17 | `CTU-IoT-Malware-Capture-34-1` | `dataset17.csv` | 23,145 | 23,145 | 0 | 0.74 | 0.0 |
| 18 | `CTU-IoT-Malware-Capture-33-1` | `dataset18.csv` | 54,454,591 | 54,454,591 | 0 | 1769.44 | 789.9 |
| 19 | `CTU-IoT-Malware-Capture-3-1` | `dataset19.csv` | 156,103 | 150,141 | 5,962 | 5.56 | 2.2 |
| 20 | `CTU-IoT-Malware-Capture-21-1` | `dataset20.csv` | 3,286 | 3,286 | 0 | 0.13 | 0.1 |
| 21 | `CTU-IoT-Malware-Capture-20-1` | `dataset21.csv` | 3,209 | 3,209 | 0 | 0.12 | 0.1 |
| 22 | `CTU-IoT-Malware-Capture-17-1` | `dataset22.csv` | 54,659,855 | 54,659,846 | 9 | 1799.39 | 763.6 |
| 23 | `CTU-IoT-Malware-Capture-1-1` | `dataset23.csv` | 1,008,748 | 1,008,748 | 0 | 40.16 | 0.0 |

---

## 4. Verification and Data Integrity Checks

1. **Zero Data Corruption:** All fields conform strictly to `INTERIM_SCHEMA` with float32/int64/int32/string typing.
2. **Zeek Null Handling:** All `-` and `(empty)` indicators were successfully imputed (duration -> 0.0, bytes -> 0, service -> 'unknown').
3. **Zero Scenario Contamination:** `scenario_id` is preserved in every row, guaranteeing strict separation for Step 13 Grouped Cross-Validation.
4. **No Identity Leakage to Features:** IP addresses and UIDs are retained for audit and scenario-level grouping only, ready to be stripped during feature extraction.

