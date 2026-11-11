# Training variant choice (Step 14, decision D-051)

**Created:** 2026-11-10 18:00:46  
**Data:** grouped out-of-fold predictions of the 22 training scenarios only. The held-out scenario 34-1 is not used.  
**Rule (written before the results):** compare on trusted rows; WC only if its macro-F1 is at least 0.01 higher, else W.

| Model | Rows | Macro-F1 | Benign | DDoS_DoS | PortScan | CnC | Malware_Download |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1: 19 features, all rows | 1,384,070 | 0.3422 | 0.447 | 0.003 | 0.464 | 0.167 | 0.629 |
| v1: 19 features, trusted rows | 1,184,004 | 0.3730 | 0.474 | 0.003 | 0.495 | 0.206 | 0.687 |
| W: 26 features, all rows | 1,384,070 | 0.6041 | 0.518 | 0.773 | 0.502 | 0.509 | 0.719 |
| **W: 26 features, trusted rows** | 1,184,004 | 0.6465 | 0.588 | 0.773 | 0.561 | 0.515 | 0.795 |
| **WC: 26 features, trained without untrusted rows, trusted rows** | 1,184,004 | 0.7009 | 0.747 | 0.786 | 0.600 | 0.751 | 0.620 |

- Rows left out in WC (`label_trusted = False`): 200,066.
- WC minus W on the trusted rows: +0.0544. **Chosen: WC.**
- The two variants have their own grouped folds (the fold split depends on the rows), so part of the difference can come from the fold split.
- These are training-data (out-of-fold) results. The held-out result is in `evaluation_iot23.md`.
