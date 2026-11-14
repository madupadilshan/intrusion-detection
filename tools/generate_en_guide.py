# -*- coding: utf-8 -*-
"""
Generator script to produce PROGRESS_MEETING_PRESENTATION_GUIDE_EN.md
as an exact 1:1 English mirror of PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md.
"""

def get_header_and_toc():
    return '''# Progress Meeting Presentation Guide & Requirements Verification Manual

**Project:** Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks Using Machine Learning  
**Group:** Group 03 — University of Sri Jayewardenepura  
**Reference Document:** [`docs/requirements_checklist.md`](file:///d:/intrusion%20detection/docs/requirements_checklist.md)  
**Supporting Architecture:** [`A_TO_Z_SYSTEM_FLOW.md`](file:///d:/intrusion%20detection/A_TO_Z_SYSTEM_FLOW.md)  
**Date:** November 2026  

---

> 🌐 **Language:** English | [**Sinhala Presentation Guide Available Here (සිංහල පිටපත)**](PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md)

> 🎯 **Purpose of this Guide:**  
> This manual is prepared for the live progress meeting with our supervisors (Dr. Matheeh & Dr. Amarakeerthi). It provides an authoritative, step-by-step verification protocol to prove that our project 100% practically satisfies all **Functional Requirements (FR-01 to FR-08)**, **Acceptance Targets (Proposal Table 9)**, **Research Objectives (O1 to O6)**, and **Research Questions (RQ1 to RQ5 & Hypothesis H1)** exactly in the order defined in **[`docs/requirements_checklist.md`](docs/requirements_checklist.md)** using direct terminal commands.
>
> ⚠️ **Presentation Principles:**  
> No wrapper scripts or obfuscated shortcuts are used. Every single proof follows an identical, transparent 8-point structure:
> 1. **💡 Why We Are Doing This (Requirement and Objective)**
> 2. **⚙️ What Happens Under the Hood When Run**
> 3. **💻 Direct Raw Command**
> 4. **🔍 Line-by-Line Breakdown**
> 5. **📋 Verified Output**
> 6. **📊 Output Breakdown (Explaining Every Key Value)**
> 7. **🔬 Scientific Meaning / Proof**
> 8. **🗣️ Spoken English Script (What to Say to the Supervisor)**

---

# Table of Contents

1. [Pre-Meeting Lab Initialization (Cold Start)](#1-pre-meeting-lab-initialization-cold-start)
2. [Part 1: Functional Requirements Verification (FR-01 to FR-08)](#2-part-1-functional-requirements-verification-fr-01-to-fr-08)
   - [FR-01: Live Packet Capture & Flow Extraction (Schema Test)](#fr-01-live-packet-capture--flow-extraction-must--schema-test)
   - [FR-02: Multi-Class AI Detection & Live 5-Attack Suite (Live Attack Suite)](#fr-02-multi-class-ai-detection--live-5-attack-suite-must--live-attack-suite)
   - [FR-03: Benign, Attack & Mitigation Database Storage (DB Retention Test)](#fr-03-database-storage-for-benign-attacks--mitigations-must--db-test)
   - [FR-04: Authenticated Dashboard & WebSocket Push (Zero Refresh Test)](#fr-04-authenticated-dashboard--real-time-websocket-push-must--socketio-test)
   - [FR-05: Controlled Subnet Nmap Asset Discovery (Inventory Test)](#fr-05-controlled-nmap-asset-discovery-should--inventory-test)
   - [FR-06: Router Firewall Ruleset, Auto-Expiry & Timers (Firewall Test)](#fr-06-router-firewall-ruleset-auto-expiry--timers-must--firewall-test)
   - [FR-07: Immutable Allowlists & System Audit Trail (Safety & Audit Test)](#fr-07-immutable-allowlists-thresholds--audit-trail-must--safety-test)
   - [FR-08: Filtered Forensic Incident Log Export (RFC 4180 CSV Test)](#fr-08-filtered-forensic-log-export-should--export-test)
3. [Part 2: Acceptance Targets Verification (Proposal Table 9 Targets)](#3-part-2-acceptance-targets-verification-proposal-table-9-targets)
   - [Target 1: Classification Quality (Macro-F1 ≥ 0.85 on Unseen Data)](#target-1-classification-quality-macro-f1--085-on-held-out-scenario)
   - [Target 2: Benign Safety (Zero Video Disruption & FPR ≤ 5%)](#target-2-benign-safety-zero-video-disruption--benign-safety)
   - [Target 3: Decision Latency (Median < 2.0 s Target)](#target-3-decision-latency-median--20-s-target)
   - [Target 4: Throughput & Resource Efficiency](#target-4-throughput--resource-efficiency)
   - [Target 5: Reliability & Clean State Recovery](#target-5-reliability--clean-state-recovery)
   - [Target 6: Usability & Administrative Audit Compliance](#target-6-usability--administrative-audit-compliance)
4. [Part 3: Research Objectives (Objectives O1 to O6 - Table 3)](#4-part-3-research-objectives-objectives-o1-to-o6)
5. [Part 4: Hypothesis and Research Questions (Hypothesis H1 & RQ1 to RQ5)](#5-part-4-hypothesis-and-research-questions-hypothesis-h1--rq1-to-rq5)
6. [Part 5: Automated Test Suite (315 Tests Passed)](#6-part-5-automated-test-suite)
7. [Part 6: Live Manual Attack Playbook](#7-part-6-live-manual-attack-playbook)

---
'''
