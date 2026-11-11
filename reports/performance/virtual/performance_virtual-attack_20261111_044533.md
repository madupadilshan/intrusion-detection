# Speed and resource use: virtual-attack (2026-11-11 04:45 UTC, 540 s)

Guide Step 37; proposal Table 9 (latency, throughput/resources), RQ4. Measured on the sensor's own clock; the dashboard times are when a logged-in Socket.IO client (this tool) received the message.

| Time (seconds) | Alerts | Median | 95th percentile | Max |
| --- | ---: | ---: | ---: | ---: |
| A. Zeek wait (flow end -> line read) | 6 | 5.780 | 300.520 | 300.520 |
| B. Read -> decision | 6 | 0.125 | 0.629 | 0.629 |
| C. Decision -> dashboard | 6 | 0.004 | 0.025 | 0.025 |
| D. Read -> dashboard (system part) | 6 | 0.141 | 0.636 | 0.636 |
| E. Flow end -> dashboard | 6 | 5.921 | 301.156 | 301.156 |
| F. First alert -> rule active | 2 | 0.159 | 0.273 | 0.273 |

- Proposal target (median decision < 2 s, 95th percentile < 5 s) on D: **met** (median 0.141 s, 95th 0.636 s)
- Flows per second: median 0.000, max 500.000; flows processed in total: 19024
- Dashboard summary messages received: 62 (FR-04: the Overview updates without refresh)
- Zeek capture loss (max % in the run): 98.35526315789474; packets dropped (stats.log): 0; Zeek logs found: capture_loss.log, stats.log

| Process | CPU % median | CPU % max | Memory MB max |
| --- | ---: | ---: | ---: |
| zeek | 0.000 | 0.000 | 0.000 |
| ids_backend | 1.500 | 78.500 | 128.400 |

Raw samples (every second): `reports/performance/virtual/samples_virtual-attack_20261111_044533.csv`.
Note: A depends on Zeek's timeouts (a long video stream is written only when it ends); it is reported, not hidden (guide Step 37 item 3).
