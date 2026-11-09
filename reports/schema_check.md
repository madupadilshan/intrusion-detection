# Offline vs Live Feature Check (Step 22)

**Proposal:** Sections 2.5 and 3.5; Objective O3; Research Question RQ3; Table 11
**Date:** 2026-11-09 05:26:45 UTC
**Offline data:** `D:\intrusion detection\data\processed\train_features.parquet` (1,384,070 flows)
**Live data:** `data\local\synthetic\2026-10-31\conn.log` (5,000 flows)
**Model bundle:** `D:\intrusion detection\ml_engine\models\ids_bundle_v1.joblib`

> **Data source: SYNTHETIC.** SYNTHETIC test data (decision D-038). This only shows that the check runs. It is NOT evidence for O3 or RQ3. Note: the synthetic file uses service names such as `rtsp`, `ssdp` and `onvif`; Zeek's standard analyzers may not produce these, so real Zeek output can look different.

## Summary

| Check (proposal 3.5) | Result | Verdict |
| :--- | :--- | :--- |
| Column names and order (19 features) | live 19 / expected 19; order match = True | **PASS** |
| Data types | 19 / 19 compatible | **PASS** |
| Missing values | 19 / 19 features with no missing values | **PASS** |
| Normal ranges (no negative counts; ratios in 0–1) | 13 / 13 numeric features valid | **PASS** |
| Model runs on the live features | valid probabilities = True | **PASS** |
| Categories not seen in training | 1 feature(s): `service` | reported (encoded as unknown = -1) |
| Summary distributions (KS statistic >= 0.3) | 12 feature(s): `duration`, `orig_bytes`, `resp_bytes`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`, `orig_bytes_per_pkt`, `resp_bytes_per_pkt`, `byte_ratio`, `pkt_ratio`, `is_incomplete_flow` | reported (a large shift is a domain difference, see below) |

**Format check overall: PASS.** This means the live pipeline makes the same 19 columns, with the same types, without missing or impossible values, and the model accepts them. It does **not** mean the live traffic looks like IoT-23: the distribution and category rows show how different it is.

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

## 2. Numeric ranges and distributions

KS = two-sample Kolmogorov–Smirnov statistic on samples of up to 10,000 flows (0 = same distribution, 1 = no overlap).

| Feature | Offline min–max | Live min–max | Offline median (p95) | Live median (p95) | KS statistic | Range status |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `duration` | 0.0 – 93280.0312 | 0.01 – 119.9913 | 0.0 (17.3633) | 14.679 (108.5152) | 0.815 | PASS |
| `orig_bytes` | 0.0 – 66205577216.0 | 32.0 – 344727.0 | 0.0 (636.0) | 23385.5 (205258.7) | 0.913 | PASS |
| `resp_bytes` | 0.0 – 336516352.0 | 0.0 – 21188000.0 | 0.0 (0.0) | 1511780.5 (13159516.4) | 0.977 | PASS |
| `missed_bytes` | 0.0 – 1342177280.0 | 0.0 – 0.0 | 0.0 (0.0) | 0.0 (0.0) | 0.000 | PASS |
| `orig_pkts` | 0.0 – 14319118.0 | 1.0 – 4144.0 | 1.0 (6.0) | 334.5 (2838.0) | 0.673 | PASS |
| `orig_ip_bytes` | 0.0 – 1781371392.0 | 70.0 – 500607.0 | 60.0 (1080.0) | 36712.0 (316991.55) | 0.790 | PASS |
| `resp_pkts` | 0.0 – 239484.0 | 0.0 – 16592.0 | 0.0 (0.0) | 1330.5 (11596.2) | 0.963 | PASS |
| `resp_ip_bytes` | 0.0 – 349618688.0 | 0.0 – 21802560.0 | 0.0 (0.0) | 1570026.5 (13630037.5) | 0.969 | PASS |
| `orig_bytes_per_pkt` | 0.0 – 946322432.0 | 20.2 – 649.0 | 0.0 (30.0) | 73.6299 (283.0) | 0.949 | PASS |
| `resp_bytes_per_pkt` | 0.0 – 16394.0 | 0.0 – 1978.5 | 0.0 (0.0) | 959.1202 (1341.6293) | 0.979 | PASS |
| `byte_ratio` | 0.0 – 1.0 | 0.0043 – 1.0 | 0.0 (1.0) | 0.0253 (0.6732) | 0.912 | PASS |
| `pkt_ratio` | 0.0 – 1.0 | 0.0994 – 1.0 | 1.0 (1.0) | 0.2616 (0.6667) | 0.928 | PASS |
| `is_incomplete_flow` | 0.0 – 1.0 | 0.0 – 1.0 | 1.0 (1.0) | 0.0 (0.0) | 0.976 | PASS |

## 3. Categories

| Feature | Offline categories | Live categories | In both | Not seen in training |
| :--- | ---: | ---: | ---: | :--- |
| `proto` | 3 | 2 | 2 | `none` |
| `service` | 7 | 7 | 3 | `ntp, onvif, rtsp, ssdp` |
| `conn_state` | 13 | 2 | 2 | `none` |
| `history` | 238 | 4 | 4 | `none` |
| `orig_port_cat` | 4 | 1 | 1 | `none` |
| `resp_port_cat` | 4 | 2 | 2 | `none` |

Categories not seen in training are encoded as "unknown" (-1). The model still runs, but it has never learned what these values mean, so predictions for such flows are less reliable.

## 4. Model run on the live features

- Flows: 5,000
- Probabilities valid (each row sums to 1): True
- Predicted classes: `{"Benign": 5000}`

## 5. What to do with the result (proposal 3.5)

- If a feature fails the format checks, fix the live adapter, or drop the feature and train again.
- A large distribution shift or new categories are not format errors. They show the domain difference between IoT-23 and our camera traffic, which is part of the answer to RQ3. Report them.
- Run this check again on the **real** lab capture (`--source real`). Only that run answers RQ3.
