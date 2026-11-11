# Training variant choice (Step 14, decision D-052)

**Created:** 2026-11-10 23:00:03  
**Data:** grouped out-of-fold predictions of the 22 training scenarios only. The held-out scenario 34-1 is not used.  
**Rule (written before the results):** compare on the rows both variants keep; WCD only if its macro-F1 is at least 0.01 higher, else WC.

| Model | Rows | Macro-F1 | Benign | DDoS_DoS | PortScan | CnC | Malware_Download |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **WC, compared rows** | 1,182,984 | 0.7085 | 0.759 | 0.796 | 0.595 | 0.778 | 0.614 |
| **WCD, compared rows** | 1,182,984 | 0.7097 | 0.740 | 0.764 | 0.631 | 0.769 | 0.644 |
| WC, all its own rows | 1,184,004 | 0.7084 | 0.760 | 0.796 | 0.595 | 0.777 | 0.614 |
| v2.0.0 (26 features, WC), compared rows | 1,182,984 | 0.7010 | 0.747 | 0.786 | 0.600 | 0.752 | 0.620 |
| v1 (19 features, W), compared rows | 1,182,984 | 0.3726 | 0.472 | 0.003 | 0.495 | 0.206 | 0.687 |

- Compared rows (kept by both WC and WCD): 1,182,984.
- Rows left out by the trusted-label rule (D-051): 200,066; rows listed as disputed (D-052, `config/disputed_labels.yaml`): 1,948.
- WCD minus WC on the compared rows: +0.0012. **Chosen: WC.**
- Each variant has its own grouped folds (the fold split depends on the rows), so part of a difference can come from the fold split.
- These are training-data (out-of-fold) results. The held-out result is in `evaluation_iot23.md`.
