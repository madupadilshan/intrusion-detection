# Data Retention Plan

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Team (Group 03):** M A M Dilshan · Dilshara W S · A O P I Mendis
**Version:** 1 · **Date:** 20 October 2026
**Based on:** proposal Sections 3.2, 3.6 and 3.8 · guide Step 1

> **Purpose:** to say clearly **what data we keep, where, who can open it, how long we keep it, and how we delete it.** The proposal says we will keep as little as possible, control who can open the dataset and the logs, and delete them following the agreed retention plan (Section 3.8).
>
> **The keep periods in Section 3 are left blank on purpose.** The team fills them in (Section 6). We do not guess them.

---

## 1. Main rules

1. **Metadata only.** We keep only connection metadata: who talked to whom, when, which protocol, how long, how many bytes and packets. **We never keep video, audio or packet contents.**
2. **Only our own lab devices.** Local data comes only from cameras and test computers that we are allowed to watch (proposal 3.2).
3. **Keep as little as possible** (proposal 3.8). Benign traffic is kept as **summaries** (counts per minute), not as every single flow.
4. **Data never goes into Git.** The `data/` folder, model files, logs and databases are listed in `.gitignore`. **The GitHub repository is public**, so this rule is important.
5. **Only the team and the supervisors** can open the data.
6. **Delete on time,** following Section 3, and write each deletion in the lab logbook.

## 2. What we will never collect

- ❌ Camera video or audio, or still images.
- ❌ Packet payloads (the contents of the traffic).
- ❌ Data from any device that is not in our lab, or that we are not allowed to watch.
- ❌ Passwords of real people. (Lab passwords are kept only in the private `.env` file, never in the data.)

## 3. Data we keep

| # | Data | What it contains | Where it is stored | Who can open it | Keep for | How it is deleted |
| - | ---- | ---------------- | ------------------ | --------------- | -------- | ----------------- |
| 1 | **IoT-23 dataset** (public, v1.0.0) | Labelled connection flows from the Stratosphere Laboratory captures | Development PC: `data/raw/iot23/` | Team, supervisors | Until the end of the project (it is public data) | Delete the folder at the end, or keep it |
| 2 | **Processed dataset files** | Cleaned tables and feature tables made from IoT-23 | `data/interim/`, `data/processed/` | Team, supervisors | Until the end of the project | Delete the folders at the end |
| 3 | **Local benign camera traffic** | Zeek connection logs from our own lab (metadata only) | `data/local/`; sensor | Team, supervisors | ________ (team decides) | Delete the files |
| 4 | **Lab test traffic** (scans, floods, simulations) | Zeek connection logs from the Table 10 tests | `data/local/`; sensor | Team, supervisors | ________ (team decides) | Delete the files |
| 5 | **Attack events** (MongoDB `attack_events`) | Time, direction, lab IP addresses and ports, protocol, predicted class, confidence, model version, short evidence note, status | MongoDB on the sensor | Logged-in admins (team) | ________ days → `retention_days.attack_events` | Automatic delete (MongoDB TTL index) |
| 6 | **Traffic summaries** (MongoDB `traffic_summaries`) | Counts of benign flows per minute | MongoDB on the sensor | Logged-in admins (team) | ________ days → `retention_days.traffic_summaries` | Automatic delete (TTL index) |
| 7 | **System and audit logs** (MongoDB `system_logs`) | Who did what and when (login, scan, block, unblock, settings change) | MongoDB on the sensor | Logged-in admins (team) | ________ days → `retention_days.system_logs` | Automatic delete (TTL index) |
| 8 | **Response actions and blocklist** | Each block, rate-limit or unblock, with reason code, actor and expiry time | MongoDB on the sensor | Logged-in admins (team) | Same as row 7 (audit history) — ________ | Automatic delete or at project end |
| 9 | **Device records and scans** | Lab device IP and MAC addresses, open ports, services, scan times | MongoDB on the sensor | Logged-in admins (team) | ________ | Delete at project end |
| 10 | **User accounts** (`users`) | Admin usernames and **bcrypt password hashes** only | MongoDB on the sensor | System only | Until the end of the project | Delete all accounts at project end |
| 11 | **Exported logs** (FR-08) | CSV or JSON files of filtered attack events | `reports/` (results only) or a private folder | Team, supervisors | ________ | Delete raw exports at the end; keep only the summary tables in the report |
| 12 | **Trained models** | Model bundle (`.joblib`), no traffic data inside | `ml_engine/models/` (not in Git) | Team, supervisors | Until the end of the project | Delete, or keep |
| 13 | **Reports and results** | Tables, figures and summaries (no raw traffic) | `reports/`, the final report | Team, supervisors, examiners | Kept (part of the final report) | — |
| 14 | **Lab logbook** | Date, person, activity, target, reason | `docs/lab_logbook.md` (in Git) | Public (no secrets in it) | Kept (part of the project record) | — |

> When the team decides the periods for rows 5, 6 and 7, also write them into `config/settings.example.yaml` under `retention_days`. The system will then delete old records automatically (guide Step 23).

## 4. Protecting the data

- The **development PC** and the **sensor** have user passwords. Only team members have accounts.
- **MongoDB** is reachable only from the lab (not from the internet), and the dashboard needs a login (proposal 3.6).
- Secrets (database address, JWT key, router login) are kept in the private `.env` file, which is **not in Git** (proposal 3.6).
- Lab IP and MAC addresses belong to **our own lab devices** only.
- If a laptop with project data is lost, tell the team and the supervisor, and write it in the logbook.

## 5. Deleting data at the end of the project (guide Step 42)

1. Delete the local captures and test logs (rows 3 and 4).
2. Empty the MongoDB database on the sensor (rows 5–10).
3. Delete the exported raw logs (row 11).
4. Delete or keep the IoT-23 files and the models (rows 1, 2, 12).
5. Remove the lab passwords, and the team's firewall and router rights.
6. Write each deletion in the lab logbook, with the date and the person.

## 6. Sign-off

| | |
| --- | --- |
| **Keep periods decided** (rows 3–9, 11) | ______________________ |
| **Decided by (team)** | ______________________ |
| **Date** | ______________________ |
