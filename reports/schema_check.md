# Offline vs Live Feature Check (Step 22)

**Proposal:** Sections 2.5 and 3.5; Objective O3; Research Question RQ3; Table 11
**Date:** 2026-11-14 05:21:13 UTC
**Offline data:** `D:\intrusion detection\data\processed\train_features.parquet` (1,384,070 flows)
**Live data:** `lab_virtual\zeek_logs\conn.log` (36 flows)
**Model bundle:** `D:\intrusion detection\ml_engine\models\ids_bundle_v3.joblib`

> **Data source: REAL.** REAL capture: Zeek `conn.log` from the lab mirror port. This report is the Step 22 evidence for Objective O3 and Research Question RQ3.

## Summary

| Check (proposal 3.5) | Result | Verdict |
| :--- | :--- | :--- |
| Column names and order (27 features) | live 27 / expected 27; order match = True | **PASS** |
| Data types | 27 / 27 compatible | **PASS** |
| Missing values | 27 / 27 features with no missing values | **PASS** |
| Normal ranges (no negative counts; ratios in 0–1) | 21 / 21 numeric features valid | **PASS** |
| Model runs on the live features | valid probabilities = True | **PASS** |
| Categories not seen in training | 2 feature(s): `service`, `history` | reported (encoded as unknown = -1) |
| Summary distributions (KS statistic >= 0.3) | 19 feature(s): `duration`, `orig_bytes`, `resp_bytes`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`, `orig_bytes_per_pkt`, `resp_bytes_per_pkt`, `byte_ratio`, `pkt_ratio`, `is_incomplete_flow`, `src_conn_60s`, `src_udst_60s`, `src_uport_60s`, `src_udst_ratio`, `pair_conn_60s`, `pair_gap`, `pair_gap_change` | reported (a large shift is a domain difference, see below) |

**Format check overall: PASS.** This means the live pipeline makes the same 27 columns, with the same types, without missing or impossible values, and the model accepts them. It does **not** mean the live traffic looks like IoT-23: the distribution and category rows show how different it is.

## 1. Data types and missing values

| Feature | Kind | Offline dtype | Live dtype | Offline missing % | Live missing % | Status |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| `proto` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `service` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `conn_state` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `history` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `orig_port_cat` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `resp_port_cat` | categorical | `object` | `object` | 0.00 | 0.00 | PASS |
| `duration` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `orig_bytes` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `resp_bytes` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `missed_bytes` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `orig_pkts` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `orig_ip_bytes` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `resp_pkts` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `resp_ip_bytes` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `orig_bytes_per_pkt` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `resp_bytes_per_pkt` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `byte_ratio` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `pkt_ratio` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `is_incomplete_flow` | numerical | `int8` | `int8` | 0.00 | 0.00 | PASS |
| `src_conn_60s` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `src_udst_60s` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `src_uport_60s` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `src_udst_ratio` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `pair_conn_60s` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `pair_gap` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `pair_gap_change` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |
| `pair_fail_1h` | numerical | `float32` | `float32` | 0.00 | 0.00 | PASS |

## 2. Numeric ranges and distributions

KS = two-sample Kolmogorov–Smirnov statistic on samples of up to 10,000 flows (0 = same distribution, 1 = no overlap).

| Feature | Offline min–max | Live min–max | Offline median (p95) | Live median (p95) | KS statistic | Range status |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `duration` | 0.0 – 93280.0312 | 0.0003 – 286.4468 | 0.0 (17.3633) | 0.0009 (0.1675) | 0.798 | PASS |
| `orig_bytes` | 0.0 – 66205577216.0 | 27.0 – 55977600.0 | 0.0 (636.0) | 57.0 (2368.0) | 0.913 | PASS |
| `resp_bytes` | 0.0 – 336516352.0 | 0.0 – 5618.0 | 0.0 (0.0) | 48.0 (5618.0) | 0.951 | PASS |
| `missed_bytes` | 0.0 – 1342177280.0 | 0.0 – 0.0 | 0.0 (0.0) | 0.0 (0.0) | 0.000 | PASS |
| `orig_pkts` | 0.0 – 14319118.0 | 1.0 – 2857.0 | 1.0 (6.0) | 5.5 (21.0) | 0.677 | PASS |
| `orig_ip_bytes` | 0.0 – 1781371392.0 | 55.0 – 56126164.0 | 60.0 (1080.0) | 351.0 (3465.0) | 0.629 | PASS |
| `resp_pkts` | 0.0 – 239484.0 | 1.0 – 2857.0 | 0.0 (0.0) | 5.0 (20.0) | 0.963 | PASS |
| `resp_ip_bytes` | 0.0 – 349618688.0 | 71.0 – 148552.0 | 0.0 (0.0) | 280.0 (5938.0) | 0.973 | PASS |
| `orig_bytes_per_pkt` | 0.0 – 946322432.0 | 9.5 – 19593.1406 | 0.0 (30.0) | 21.1667 (119.9638) | 0.915 | PASS |
| `resp_bytes_per_pkt` | 0.0 – 16394.0 | 0.0 – 1123.6 | 0.0 (0.0) | 43.0 (936.3333) | 0.951 | PASS |
| `byte_ratio` | 0.0 – 1.0 | 0.0204 – 1.0 | 0.0 (1.0) | 0.4536 (0.8261) | 0.912 | PASS |
| `pkt_ratio` | 0.0 – 1.0 | 0.5 – 0.5455 | 1.0 (1.0) | 0.5 (0.5322) | 0.932 | PASS |
| `is_incomplete_flow` | 0.0 – 1.0 | 0.0 – 1.0 | 1.0 (1.0) | 0.0 (0.0) | 0.948 | PASS |
| `src_conn_60s` | 1.0 – 1176902.0 | 1.0 – 4.0 | 9292.0 (638456.65) | 2.0 (4.0) | 0.962 | PASS |
| `src_udst_60s` | 1.0 – 1176785.0 | 1.0 – 1.0 | 5212.0 (610887.1) | 1.0 (1.0) | 0.895 | PASS |
| `src_uport_60s` | 1.0 – 73.0 | 1.0 – 3.0 | 2.0 (7.0) | 1.0 (3.0) | 0.496 | PASS |
| `src_udst_ratio` | 0.0 – 1.0 | 0.25 – 1.0 | 0.9998 (1.0) | 0.5 (1.0) | 0.474 | PASS |
| `pair_conn_60s` | 1.0 – 729517.0 | 1.0 – 4.0 | 1.0 (148124.2) | 2.0 (4.0) | 0.395 | PASS |
| `pair_gap` | -1.0 – 599.9959 | -1.0 – 60.042 | -1.0 (8.5833) | 28.941 (60.0401) | 0.658 | PASS |
| `pair_gap_change` | -1.0 – 599.9834 | -1.0 – 60.0013 | -1.0 (4.4299) | 29.9999 (60.0011) | 0.663 | PASS |
| `pair_fail_1h` | 0.0 – 3578269.0 | 0.0 – 0.0 | 0.0 (411457.85) | 0.0 (0.0) | 0.197 | PASS |

## 3. Categories

| Feature | Offline categories | Live categories | In both | Not seen in training |
| :--- | ---: | ---: | ---: | :--- |
| `proto` | 3 | 2 | 2 | `none` |
| `service` | 7 | 5 | 4 | `ntp` |
| `conn_state` | 13 | 3 | 3 | `none` |
| `history` | 238 | 5 | 4 | `DafAr` |
| `orig_port_cat` | 4 | 3 | 3 | `none` |
| `resp_port_cat` | 4 | 2 | 2 | `none` |

Categories not seen in training are encoded as "unknown" (-1). The model still runs, but it has never learned what these values mean, so predictions for such flows are less reliable.

## 4. Model run on the live features

- Flows: 36
- Probabilities valid (each row sums to 1): True
- Predicted classes: `{"Benign": 36}`

## 5. What to do with the result (proposal 3.5)

- If a feature fails the format checks, fix the live adapter, or drop the feature and train again.
- A large distribution shift or new categories are not format errors. They show the domain difference between IoT-23 and our camera traffic, which is part of the answer to RQ3. Report them.
- Run this check again on the **real** lab capture (`--source real`). Only that run answers RQ3.
