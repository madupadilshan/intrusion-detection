# IoT-23 Interim Cleaned Parquet Dataset Summary (Step 10)

**Generated Date:** 25 October 2026  
**Proposal Alignment:** Section 3.3 (Steps 1–4: Ingestion & Data Cleaning); Objective O1  
**Label Mapping Policy:** Frozen under Decision `D-014` (`config/label_mapping.yaml`)  
**Storage Location:** `data/interim/*.parquet`  

---

## 1. Executive Summary

- **Total Scenarios Processed:** 1  
- **Total Raw Input Flows:** 1,008,748  
- **Total Clean Flows Retained:** 1,008,748  
- **Total Excluded Ambiguous Flows:** 0 (0.0000%)  
- **Total Compressed Parquet Disk Footprint:** 40.16 MB (0.04 GB)  
- **Total Ingestion Execution Time:** 13.4 seconds (0.22 minutes)  

---

## 2. Overall Clean Class Distributions

| Target Class | Class ID | Clean Flow Count | Percentage |
| :--- | :---: | :---: | :---: |
| `Benign` | 0 | 469,275 | 46.52% |
| `DDoS_DoS` | 1 | 0 | 0.00% |
| `PortScan` | 2 | 539,465 | 53.48% |
| `CnC` | 3 | 8 | 0.00% |
| `Malware_Download` | 4 | 0 | 0.00% |

---

## 3. Scenario-by-Scenario Ingestion Matrix

| # | Scenario ID | Raw File | Raw Rows | Clean Rows | Excluded | Parquet Size (MB) | Runtime (s) |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `CTU-IoT-Malware-Capture-1-1` | `dataset23.csv` | 1,008,748 | 1,008,748 | 0 | 40.16 | 13.4 |

---

## 4. Verification and Data Integrity Checks

1. **Zero Data Corruption:** All fields conform strictly to `INTERIM_SCHEMA` with float32/int64/int32/string typing.
2. **Zeek Null Handling:** All `-` and `(empty)` indicators were successfully imputed (duration -> 0.0, bytes -> 0, service -> 'unknown').
3. **Zero Scenario Contamination:** `scenario_id` is preserved in every row, guaranteeing strict separation for Step 13 Grouped Cross-Validation.
4. **No Identity Leakage to Features:** IP addresses and UIDs are retained for audit and scenario-level grouping only, ready to be stripped during feature extraction.

