# Benign Camera Traffic Check (Step 20)

**Data source:** SYNTHETIC — made by `generate_camera_flow()` for software testing (decision D-038)  
**File:** `data\local\synthetic\2026-10-31\conn.log`  
**Model bundle:** `ml_engine\models\ids_bundle_v1.joblib`  
**Generated:** 2026-11-09 10:56:37

> **This is not a measurement.** The flows were made by a script, not captured from a camera. They only show that the pipeline runs end to end. They are not evidence for Hypothesis H1, and they must not be reported as results.

## Results

| Measure | Value | Proposal target |
| --- | ---: | --- |
| Flows checked | 5,000 | — |
| Benign flows predicted as an attack (FPR) | 0.000% (0 / 5,000) | <= 5% (H1) → **not tested (synthetic data)** |
| Flows that would raise an alert | 0.000% (0) | reported |
| Flows that reach a block threshold | 0.000% (0) | reported (a block also needs the policy checks) |
| Missing values after feature making | 0 | 0 |

Predicted classes: Benign 5,000

Protocols: tcp 4,011, udp 989

Services: rtsp 2,744, http 943, dns 376, ssl 324, ssdp 216, onvif 200, ntp 197

Only connection metadata is used; no video or audio is stored (proposal 3.8). Keep periods follow `docs/ethics/data_retention_plan.md`.
