# IoT-23 Copy Verification (proposal Section 3.2)

**Date:** 2026-11-09 13:49  
**Official files:** `https://mcfp.felk.cvut.cz/publicDatasets/IoT-23-Dataset/IndividualScenarios/<scenario>/bro/conn.log.labeled` (IoT-23 v1.0.0)  
**Official label totals:** https://www.stratosphereips.org/datasets-iot23 (per-scenario label tables, read 2026-11-09)
  
**Local copy source:** Kaggle "IOT-23 Full Dataset" by surajsooraj26, https://www.kaggle.com/datasets/surajsooraj26/iot-23 (version 1, CC0; all 23 file sizes equal the Kaggle file list; D-039).

Proposal 3.2: *"We will not train the model from an unofficial copy that somebody has already processed, unless we can check where it came from and what was changed in it."* Three checks are made for every local file:

1. **First row:** the first flow (`ts`, `uid`) equals the first flow of the official file (first 8 KB downloaded).
2. **Last row:** the last flow equals the last flow of the official file (last 64 KB downloaded). Together with 1, this shows the file is complete at both ends.
3. **Label totals:** the number of flows for every label (counted over every row in Step 7) equals the official table on the IoT-23 website.

**Result:** first row 23/23 match; last row 23/23 match; label totals 17 match, 3 different, 3 not listed on the website.

| Local file | Scenario | First row | Last row | Label totals | Differences |
| --- | --- | --- | --- | --- | --- |
| `dataset1.csv` | `CTU-Honeypot-Capture-4-1` | MATCH | MATCH | NOT_LISTED | — |
| `dataset2.csv` | `CTU-Honeypot-Capture-5-1` | MATCH | MATCH | NOT_LISTED | — |
| `dataset3.csv` | `CTU-Honeypot-Capture-7-1` | MATCH | MATCH | NOT_LISTED | — |
| `dataset4.csv` | `CTU-IoT-Malware-Capture-9-1` | MATCH | MATCH | MATCH | — |
| `dataset5.csv` | `CTU-IoT-Malware-Capture-8-1` | MATCH | MATCH | MATCH | — |
| `dataset6.csv` | `CTU-IoT-Malware-Capture-7-1` | MATCH | MATCH | MATCH | — |
| `dataset7.csv` | `CTU-IoT-Malware-Capture-60-1` | MATCH | MATCH | MATCH | — |
| `dataset8.csv` | `CTU-IoT-Malware-Capture-52-1` | MATCH | MATCH | DIFFERENT | C&C-Mirai: local 2 vs official 0 |
| `dataset9.csv` | `CTU-IoT-Malware-Capture-49-1` | MATCH | MATCH | DIFFERENT | FileDownload: local 14 vs official 0 |
| `dataset10.csv` | `CTU-IoT-Malware-Capture-48-1` | MATCH | MATCH | MATCH | — |
| `dataset11.csv` | `CTU-IoT-Malware-Capture-44-1` | MATCH | MATCH | MATCH | — |
| `dataset12.csv` | `CTU-IoT-Malware-Capture-43-1` | MATCH | MATCH | MATCH | — |
| `dataset13.csv` | `CTU-IoT-Malware-Capture-42-1` | MATCH | MATCH | MATCH | — |
| `dataset14.csv` | `CTU-IoT-Malware-Capture-39-1` | MATCH | MATCH | MATCH | — |
| `dataset15.csv` | `CTU-IoT-Malware-Capture-36-1` | MATCH | MATCH | MATCH | — |
| `dataset16.csv` | `CTU-IoT-Malware-Capture-35-1` | MATCH | MATCH | MATCH | — |
| `dataset17.csv` | `CTU-IoT-Malware-Capture-34-1` | MATCH | MATCH | MATCH | — |
| `dataset18.csv` | `CTU-IoT-Malware-Capture-33-1` | MATCH | MATCH | DIFFERENT | Okiru: local 13,609,467 vs official 0; Okiru-Attack: local 0 vs official 13,609,467 |
| `dataset19.csv` | `CTU-IoT-Malware-Capture-3-1` | MATCH | MATCH | MATCH | — |
| `dataset20.csv` | `CTU-IoT-Malware-Capture-21-1` | MATCH | MATCH | MATCH | — |
| `dataset21.csv` | `CTU-IoT-Malware-Capture-20-1` | MATCH | MATCH | MATCH | — |
| `dataset22.csv` | `CTU-IoT-Malware-Capture-17-1` | MATCH | MATCH | MATCH | — |
| `dataset23.csv` | `CTU-IoT-Malware-Capture-1-1` | MATCH | MATCH | MATCH | — |

**The 3 label-total differences were checked inside the official files (D-046):** 33-1 — the official file says `Okiru` (the website says `Okiru-Attack`; same count); 49-1 — the official file has the same 14 `FileDownload` flows; 52-1 — both `C&C-Mirai` flows are in the official file (one of them, a connection that never closed, is written at the end of the file). So the differences come from the website's summary tables, not from our copy.

**What was changed in the copy:** the format only. The official files are tab-separated Zeek logs with `#` header lines; the local copy is comma-separated with one header row. The last three columns stay joined by spaces (`tunnel_parents   label   detailed-label`), as in the official file. The values are the same.
