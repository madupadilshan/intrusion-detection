# System Threat Model and Security Architecture

**Project:** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**Team:** Group 03 — University of Sri Jayewardenepura  
**Based on:** Research Proposal Sections 1.2, 1.5, 3.1, 3.7, 3.8, 5.1; Tables 10 and 11  
**Document Version:** 1.0  
**Date:** 23 October 2026  

---

## 1. System Overview & Context

This threat model defines the security boundaries, assets, threat actors, and attack vectors for an Internet of Things (IoT) surveillance network centered around IP cameras. 

IP cameras represent high-risk IoT nodes because:
1. They maintain continuous, high-volume real-time network streams (RTSP/RTP).
2. They have limited on-board computational and memory resources, preventing them from running heavy endpoint security agents.
3. They are frequently targeted by botnet families (such as Mirai, Gafgyt, and Hajime) for automated recruitment into Distributed Denial of Service (DDoS) networks or unauthorized video surveillance exfiltration.

The intrusion detection and response system operates at the network level (in passive mirror mode by default, or inline transparent bridge mode during controlled tests) to detect malicious traffic flows and initiate policy-compliant response actions without disrupting critical operations.

```
                  Outside Test Network (10.10.10.0/24)
                        [ Attacker / C&C Server ]
                                   │
                                   ▼
                         [ Lab Linux Router ]
                            192.168.50.1
                                   │
    ┌──────────────────────────────┴──────────────────────────────┐
    │                                                             │
    │  Camera LAN Subnet (192.168.50.0/24)                        │
    │                                                             │
    │   [ Admin PC ]                [ NVR Recorder ]              │
    │   192.168.50.10               192.168.50.20                 │
    │                                                             │
    │   [ IDS Sensor ]              [ Protected IP Camera ]       │
    │   192.168.50.5                192.168.50.30                 │
    │   (Zeek + ML + Backend)       (or RTSP Simulator)           │
    └─────────────────────────────────────────────────────────────┘
```

---

## 2. Assets to Protect

| Asset | Description | Security Objective | Criticality |
|---|---|---|:---:|
| **IP Camera** | Real-time RTSP/ONVIF video streaming device (`192.168.50.30`). | **Availability & Integrity:** Prevent resource exhaustion, unauthorized credential compromise, and tampering. | High |
| **NVR Recorder** | Central video stream receiver and storage node (`192.168.50.20`). | **Availability:** Ensure uninterrupted recording of legitimate camera streams. | High |
| **Network Gateway / Router** | Subnet router connecting camera LAN and outside test network (`192.168.50.1`). | **Availability & Control:** Maintain legitimate forwarding; enforce dynamic firewall drop rules. | Critical |
| **IDS Sensor & Engine** | Network monitoring appliance running Zeek, ML classifier, and DB (`192.168.50.5`). | **Integrity & Availability:** Continuous flow inspection; prevent sensor overload or self-lockout. | Critical |
| **Admin Workstation & Dashboard** | Management workstation accessing the React UI (`192.168.50.10`). | **Confidentiality & Access Control:** Restrict IDS management and manual unblock controls to authorized admins. | High |
| **Video Stream Privacy** | Transmitted RTSP/RTP packets. | **Confidentiality:** Prevent unauthorized interception and metadata profiling. | High |

---

## 3. Threat Actors & Capabilities

1. **External Network Attacker:**
   * **Location:** Positioned in the outside subnet (`10.10.10.0/24`) attempting to reach the camera LAN through the gateway.
   * **Capabilities:** High-rate scanning (Nmap horizontal and vertical scans), volume-based SYN/UDP flooding, brute-force credential stuffing against RTSP/HTTP ports, and automated exploit attempts.
   * **Constraints:** Cannot bypass network-level firewall filtering; cannot forge internal MAC addresses through the routed gateway.

2. **Infected IoT Node / Compromised Camera (Internal Attacker):**
   * **Location:** Inside the camera LAN (`192.168.50.0/24`), having been infected via simulated credential exploitation or firmware vulnerability.
   * **Capabilities:** Periodic outbound Command & Control (C&C) beaconing, outbound malicious payload downloads, lateral network scanning toward other LAN devices.

---

## 4. Attack Vectors & Flow Trajectories

### 4.1 Inbound Attack Vectors (Outside ➔ Camera LAN)
* **Reconnaissance & Port Scanning:**
  * Attacker transmits TCP SYN / Connect probes across IP ranges to identify active IP cameras (e.g. testing ports 23, 80, 554, 8080).
  * *IDS Detection Target:* Multi-flow connection anomalies with `REJ`, `S0`, or short durations across multiple destination ports.
* **Denial of Service (DoS / DDoS Flooding):**
  * High-rate SYN/UDP flooding directed at the IP camera RTSP streaming port (554) to degrade video transmission to the NVR.
  * *IDS Detection Target:* Bursts of incomplete TCP connections (`S0` state), high packet count, and zero responder bytes.

### 4.2 Outbound Attack Vectors (Camera LAN ➔ Outside)
* **Command & Control (C&C) Heartbeats:**
  * Infected camera periodically contacts external server over non-standard ports to receive botnet commands (e.g. Mirai heartbeats).
  * *IDS Detection Target:* Regular, periodic short-duration flows with low byte counts and predictable inter-arrival times.
* **Malicious File Download / Staging:**
  * Infected device initiates outbound HTTP/FTP request to retrieve executable binaries (e.g. secondary malware stages).
  * *IDS Detection Target:* Asymmetric flow profiles featuring high responder bytes (`resp_bytes >> orig_bytes`) originating from camera IPs.

### 4.3 Lateral & Internal Traffic
* Normal video streaming from IP Camera (`192.168.50.30`) to NVR (`192.168.50.20`) consists of long-lived, high-volume UDP/TCP connections (`SF` state, high `orig_bytes` or `resp_bytes`).
* *IDS Requirement:* Must classify legitimate video streams as `Benign` with $>99\%$ precision to prevent false alarms.

---

## 5. Controlled Security Testing Scenarios (Proposal Table 10)

The system is evaluated against the 6 standardized scenarios specified in the proposal:

| Scenario | Name | Traffic Vector | Tool / Protocol | Target Class | Expected Action |
|:---:|---|---|---|---|---|
| **1** | Normal Streaming | Camera ➔ NVR | RTSP / RTP / HTTP | `Benign` | Pass through; update traffic summaries. |
| **2** | Horizontal Port Scan | Outside ➔ Camera LAN | Nmap TCP SYN scan | `PortScan` | Alert dashboard; block attacker IP if threshold met. |
| **3** | Rate-limited DDoS Flood | Outside ➔ Camera | `hping3` SYN flood | `DDoS` / `Flood` | Alert dashboard; trigger firewall drop rule on attacker IP. |
| **4** | C&C Outbound Beacon | Camera ➔ Outside | Periodic TCP connections | `C&C` | Alert dashboard; isolate or flag outbound session. |
| **5** | Controlled File Download | Camera ➔ Outside | HTTP/FTP binary transfer | `FileTransfer` | Alert dashboard; record evidence log in MongoDB. |
| **6** | Manual Block / Unblock | Admin ➔ Dashboard | REST API / Firewall rule | Management | Immediate rule insertion / removal via UI. |

---

## 6. Defensive Architecture & Safety Boundaries

To prevent automated security systems from causing accidental network failures, the architecture enforces strict defensive boundaries (Proposal Sections 1.2 and 3.7):

1. **Static Management Allowlist (Never Block):**
   * Source IPs matching Gateway (`192.168.50.1`), Sensor (`192.168.50.5`), Admin Workstation (`192.168.50.10`), and NVR (`192.168.50.20`) are explicitly bypassed by the decision engine before any mitigation evaluation.
2. **Confidence & Repetition Multi-Check:**
   * A single flow prediction never blocks traffic. Automatic mitigation requires:
     * Classification confidence $\ge 0.85$ (85%).
     * Repetition count $\ge 3$ malicious events within a 60-second sliding window.
3. **Automatic Rule Expiry (No Permanent Lockout):**
   * Every firewall block rule is inserted with a mandatory time-to-live (`max_rule_minutes: 30`). Expired rules are purged automatically.
4. **Metadata-Only Policy (Privacy by Design):**
   * The system never records video frames, audio payloads, or raw packet payloads. Only Zeek flow metadata (timestamps, IP tuples, ports, protocols, byte and packet counters) is processed and stored.
5. **Separated Lab Subnets:**
   * All security experiments run exclusively within isolated private subnets (`192.168.50.0/24` and `10.10.10.0/24`) with zero connection to the university production network or public internet.
