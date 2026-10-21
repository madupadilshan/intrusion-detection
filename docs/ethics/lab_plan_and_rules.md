# Lab Plan and Rules

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning
**Team (Group 03):** M A M Dilshan (ICT/22/824) · Dilshara W S (ICT/22/825) · A O P I Mendis (ICT/22/953)
**Supervisors:** Dr A.A.M. Matheeh (main) · Dr Senaka Amarakeerthi (co-supervisor, external)
**Version:** 1 · **Date:** 20 October 2026
**Based on:** proposal Sections 1.2, 3.8 and 5.1, and Tables 10 and 11 · guide Step 1

> **Purpose:** this document describes the separated lab network, the devices, who may use which tools, the tests we run, what we never do, and the safety rules for every test. Every team member follows these rules.

---

## 1. What we do in the lab

We build and test a prototype that:

- watches the traffic of a small IP-camera network;
- finds attack behaviour with a machine-learning model;
- blocks bad traffic only when strict safety rules are met;
- lets the administrator undo every block.

Only network **metadata** is recorded (who talks to whom, when, how much). **No video or audio is kept.**

## 2. The lab network

- The lab is a **separate network**. It is **not connected** to the university network, any home network, or the internet during tests.
- If a camera needs the internet for its first setup, we do that first, then disconnect it before any test.
- The lab has two small networks:

| Network                          | Use                                    | Address range (example — final plan in guide Step 5) |
| -------------------------------- | -------------------------------------- | ----------------------------------------------------- |
| Camera LAN                       | Camera, NVR, admin PC, sensor          | `192.168.50.0/24`                                     |
| "Outside" test network           | Attack test computer only              | `10.10.10.0/24`                                       |

- Both ranges are **private** addresses. **No public IP address is used.**
- **Passive mode is the default.** The sensor only receives a copy of the traffic from the switch mirror port. Inline mode is used only for short, planned tests, with a bypass plan.

## 3. Devices

| Device                                   | Purpose                                         | Example IP     | Owner / provided by | Model / serial |
| ---------------------------------------- | ----------------------------------------------- | -------------- | ------------------- | -------------- |
| IP camera **or** camera simulator        | The device we protect                           | 192.168.50.30  | Lab / Team          | RTSP IP Camera Simulator / Generic ONVIF Camera (Software emulation or Lab loan) |
| NVR or recording software                | Records the camera video (normal use)           | 192.168.50.20  | Lab / Team          | Software NVR / VLC media stream recorder |
| Managed switch with port mirroring       | Connects the lab; copies traffic to the sensor  | —              | University Lab / Virtual bridge | Managed switch with SPAN/mirror port (Lab loan / Software bridge) |
| Lab router (we can log in to it)         | Joins the two lab networks; applies blocks      | 192.168.50.1 / 10.10.10.1 | Lab / Team | Linux router / OpenWrt VM (dual-interface) |
| Linux sensor computer (2 network ports)  | Runs Zeek, the model, the backend, the firewall | 192.168.50.5   | Team workstation    | Ubuntu Linux 22.04 LTS (Zeek + IDS Engine) |
| Admin workstation                        | Opens the dashboard                             | 192.168.50.10  | M A M Dilshan       | Windows 11 PC (Dashboard & Admin Client) |
| Attack test computer (Linux)             | Makes the controlled test traffic               | 10.10.10.50    | Team workstation    | Linux test environment (Kali / Ubuntu testbed) |

## 4. People and permissions

Only the people ticked below use the attack tools, the lab passwords and the firewall rights (proposal 3.8).

| Team member     | Attack tools (Nmap, hping3, test scripts) | Lab passwords (router, camera, sensor) | Firewall / router rule changes |
| --------------- | :---------------------------------------: | :------------------------------------: | :----------------------------: |
| M A M Dilshan   |                     ☑                     |                   ☑                    |               ☑                |
| Dilshara W S    |                     ☑                     |                   ☑                    |               ☑                |
| A O P I Mendis  |                     ☑                     |                   ☑                    |               ☑                |

- Lab passwords are kept in the private `.env` file or a password manager. They are **never** written in Git, in this document or in the logbook.
- Every use of these permissions is written in the **lab logbook** (`docs/lab_logbook.md`) **before** it starts.

## 5. What we do (activities)

| # | Activity                                         | Tool / method                                                         | Where                     | Proposal |
| - | ------------------------------------------------ | --------------------------------------------------------------------- | ------------------------- | -------- |
| 1 | Record normal camera traffic (metadata only)     | Zeek on the sensor's mirror port                                      | Camera LAN                | 5.1; Table 11 |
| 2 | Device discovery                                 | Nmap, started only by a logged-in admin, **only** on the lab subnet listed in `approved_scan_subnets` | Camera LAN | 3.7 |
| 3 | Normal live streaming and playback               | Camera → NVR; admin login; video playback                             | Camera LAN                | Table 10 (1) |
| 4 | Nmap horizontal scan test                        | For example `nmap -p 23,80,554 192.168.50.0/24` from the attack computer | Outside → camera LAN   | Table 10 (2) |
| 5 | Rate-limited DDoS-like traffic, or replay of saved traffic | For example `hping3` at a limited rate, for a short time      | Outside → camera LAN      | Table 10 (3); 5.1 |
| 6 | C&C-like periodic outbound simulation            | A lab simulator device makes small, regular connections to the lab test server | Camera LAN → outside | Table 10 (4) |
| 7 | Controlled file-transfer pattern                 | A lab device downloads a **harmless** file from a lab web server       | Camera LAN → outside      | Table 10 (5) |
| 8 | Manual block and unblock                         | Admin blocks / unblocks the attack computer from the dashboard        | Lab router or sensor      | Table 10 (6) |
| 9 | Firewall tests                                   | nftables rules with an expiry time, on the sensor or the lab router   | Lab only                  | 3.7; FR-06 |

## 6. What we never do

- ❌ **No live malware**, and no malware on devices that are not ours (1.2, 5.1).
- ❌ **No public IP addresses** (1.2, 3.8).
- ❌ **No other person's camera** or device (3.8).
- ❌ **No vendor cloud service** (3.8).
- ❌ **No university production network** (3.8).
- ❌ **No video or audio is kept.** Only the network metadata we need (3.8).
- ❌ **No tests outside the separated lab** (3.8).
- ❌ We do not claim the system is a certified firewall product, or that it catches every new attack (1.2).

## 7. Safety rules for every test

1. Write the test in the lab logbook **before** it starts.
2. Check that the lab is **not connected** to any other network.
3. Check that the **allowlist** (router, sensor, admin PC, NVR) is loaded, so these devices can never be blocked.
4. Floods are **rate-limited** and **short**.
5. Every firewall rule has an **expiry time**, and the admin can **unblock by hand** at any time.
6. In inline mode, the **bypass plan** is ready (connect the switch straight to the router).
7. **Stop the test at once** if anything affects a device outside the lab, or behaves in a way we did not expect. Write it in the logbook and tell the team.

## 8. Data

Only network metadata is recorded. What we keep, who can open it, how long we keep it, and how we delete it are described in the **data retention plan** (`docs/ethics/data_retention_plan.md`).

---

## Appendix: points for the next supervisor meeting

1. **Lab hardware:** can the department provide a managed switch with port mirroring, a Linux PC for the sensor, a router we can control, or an IP camera?
2. **For information:** proposal Section 1.4 cites "Almashhadani et al., 2024", but we could not find this paper, and nobody has it. We removed it, and Santos et al. (2023) supports the sentence alone (decision D-009).
3. **Meetings:** when can we meet every two weeks (proposal Section 4)?
