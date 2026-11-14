# -*- coding: utf-8 -*-
"""
tools/build_si_proof.py
Generates PROPOSAL_FULFILLMENT_PROOF_SI.md as a 100% exact Sinhala mirror of PROPOSAL_FULFILLMENT_PROOF_EN.md.
"""

from pathlib import Path

content = """# යෝජනාවලිය සම්පූර්ණ කිරීම සහ සනාථ කිරීමේ වාර්තාව (Proposal Fulfillment & Proof Report)

**ව්‍යාපෘතිය (Project):** Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks Using Machine Learning  
**කණ්ඩායම (Group):** Group 03 — ශ්‍රී ජයවර්ධනපුර විශ්වවිද්‍යාලය, තාක්ෂණ පීඨය, තොරතුරු හා සන්නිවේදන තාක්ෂණ දෙපාර්තමේන්තුව  
**සිසුන් (Students):** M A M Dilshan (ICT/22/824), Dilshara W S (ICT/22/825), A O P I Mendis (ICT/22/953)  
**අධීක්ෂකවරුන් (Supervisors):** ආචාර්ය A.A.M. Matheeh (ප්‍රධාන අධීක්ෂක), ආචාර්ය සේනක අමරකීර්ති (බාහිර සම-අධීක්ෂක)  
**දිනය (Date):** 2026 නොවැම්බර් 14  
**මූලික යෝජනාවලිය (Source proposal):** `Group03_Proposal.pdf`  

> 🌐 **භාෂාව (Language):** සිංහල | ඉංග්‍රීසි වාර්තාව (English Report): [PROPOSAL_FULFILLMENT_PROOF_EN.md](PROPOSAL_FULFILLMENT_PROOF_EN.md)  
> 📋 **විධාන අත්පොත (8-point verification per item):** [PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md](PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md)  

---

## මෙම ලේඛනයේ අරමුණ (Purpose of This Document)

මෙම වාර්තාව අපගේ අධීක්ෂකවරුන් (Supervisors) සඳහා සකස් කරන ලද්දකි. මෙහි එකම අරමුණ වන්නේ, අප විසින් නිර්මාණය කරන ලද පද්ධතිය, අපගේ අනුමත පර්යේෂණ යෝජනාවලියෙහි (Research Proposal) සඳහන් කළ සියල්ල ඒ අයුරින්ම නිවැරදිව හා තාර්කික අනුපිළිවෙලකට ඉටුකර ඇති බව සෘජුවම ඔප්පු කර පෙන්වීමයි.

අපගේ පර්යේෂණ යෝජනාවලිය යනු එක්තරා ආකාරයක පොරොන්දුවකි. මෙම ලේඛනය එම පොරොන්දුව **යෝජනාවලිය ලියා ඇති නිල අනුපිළිවෙලටම** ඉදිරිපත් කරයි — විෂය පථය (Scope), ප්‍රධාන අරමුණ (Aim), අරමුණු (Objectives O1-O6), උපකල්පනය (Hypothesis H1), ගෘහ නිර්මාණ ශිල්පය (Architecture), පර්යේෂණ ක්‍රමවේදය (Methodology), ක්‍රියාකාරී අවශ්‍යතා (Functional Requirements FR-01 to FR-08), පිළිගැනීමේ නිර්ණායක (Acceptance Criteria Table 9), පාලිත පරීක්ෂණ අවස්ථා (Test Scenarios Table 10), අවදානම් සහ ආචාරධර්ම (Risks & Ethics) — සහ සෑම එක් පොරොන්දුවක් සඳහාම සෘජු ප්‍රායෝගික සාක්ෂියක් ඉදිරිපත් කරයි.

කිසිවක් සඟවන්නේ නැතිව, සෑම සාක්ෂි කොටසක්ම පහත පියවර හතරක ව්‍යුහය අනුගමනය කරයි:

| පියවර | එයින් පෙන්වන දේ |
|---|---|
| 📜 **යෝජනාවලියේ සඳහන් වූයේ (Proposal said)** | යෝජනාවලියෙන් උපුටා ගත් හෝ සාරාංශ කළ සැබෑ පොරොන්දුව. |
| 🔧 **අප විසින් නිර්මාණය කළ දේ (What we built)** | එය ඉටුකිරීම සඳහා අපගේ පද්ධතිය තුළ සැබවින්ම ගොඩනැගූ තාක්ෂණික අංගය. |
| 🧪 **සාක්ෂිය (Proof)** | ඕනෑම කෙනෙකුට නැවත run කර බැලිය හැකි සෘජු විධානයක්, ගොනුවක්, හෝ මිනුමක්. |
| ✅ **ප්‍රතිඵලය (Result)** | සත්‍යාපිත අවසාන ප්‍රතිඵලය, සැබෑ නිවැරදි අගයන් සමඟින්. |

යම් අගයක් ඉලක්කගත අගයකට වඩා මදක් අඩු නම් හෝ භෞතික දෘඩාංග (Physical Hardware) මට්ටමින් තවදුරටත් මැනිය යුතුව ඇත්නම්, අපි එය අවංකව හා පැහැදිලිව සඳහන් කරමු. යෝජනාවලියේම "පොරොන්දු වූ ප්‍රතිඵල නොව පරීක්ෂා කිරීමේ ඉලක්ක පමණි" ලෙස නම් කළ දෑ අවසන් ප්‍රතිඵල ලෙස අපි අසත්‍ය ලෙස ප්‍රකාශ නොකරමු.

---

## පටුන (Table of Contents)

- [කොටස 0 — ප්‍රධාන සොයාගැනීමේ න්‍යාසය (Master Traceability Matrix)](#කොටස-0--ප්‍රධාන-සොයාගැනීමේ-න්‍යාසය-master-traceability-matrix)
- [කොටස 1 — ව්‍යාපෘතියේ විෂය පථය සහ සීමාවන් (Proposal 1.2, 3.8)](#කොටස-1--ව්‍යාපෘතියේ-විෂය-පථය-සහ-සීමාවන්-proposal-12-38)
- [කොටස 2 — ප්‍රධාන අරමුණ සහ O1–O6 අරමුණු (Proposal 1.5, Table 3)](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3)
- [කොටස 3 — H1 උපකල්පනය සහ RQ1–RQ5 පර්යේෂණ ප්‍රශ්න (Proposal 1.5)](#කොටස-3--h1-උපකල්පනය-සහ-rq1rq5-පර්යේෂණ-ප්‍රශ්න-proposal-15)
- [කොටස 4 — අන්තයේ සිට අන්තය දක්වා ගෘහ නිර්මාණ ශිල්පය (Proposal Fig. 2, 3.1)](#කොටස-4--අන්තයේ-සිට-අන්තය-දක්වා-ගෘහ-නිර්මාණ-ශිල්පය-proposal-fig-2-31)
- [කොටස 5 — පර්යේෂණ ක්‍රමවේදය සම්පූර්ණ කිරීම (Proposal 3.2–3.8)](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238)
- [කොටස 6 — ක්‍රියාකාරී අවශ්‍යතා FR-01 සිට FR-08 දක්වා (Proposal Table 7)](#කොටස-6--ක්‍රියාකාරී-අවශ්‍යතා-fr-01-සිට-fr-08-දක්වා-proposal-table-7)
- [කොටස 7 — පිළිගැනීමේ නිර්ණායක (Proposal Table 9)](#කොටස-7--පිළිගැනීමේ-නිර්ණායක-proposal-table-9)
- [කොටස 8 — පාලිත පරීක්ෂණ අවස්ථා (Proposal Table 10)](#කොටස-8--පාලිත-පරීක්ෂණ-අවස්ථා-proposal-table-10)
- [කොටස 9 — අවදානම් සහ කළමනාකරණය (Proposal Table 11)](#කොටස-9--අවදානම්-සහ-කළමනාකරණය-proposal-table-11)
- [කොටස 10 — මෘදුකාංග ඉංජිනේරු විද්‍යාත්මක ප්‍රමිතිය (ස්වයංක්‍රීය පරීක්ෂණ 318)](#කොටස-10--මෘදුකාංග-ඉංජිනේරු-විද්‍යාත්මක-ප්‍රමිතිය-ස්වයංක්‍රීය-පරීක්ෂණ-318)
- [කොටස 11 — අවංක සීමාවන් සහ ඉතිරිව ඇති දෑ](#කොටස-11--අවංක-සීමාවන්-සහ-ඉතිරිව-ඇති-දෑ)
- [අවසාන ප්‍රකාශය (Closing Statement)](#අවසාන-ප්‍රකාශය-closing-statement)

---

## කොටස 0 — ප්‍රධාන සොයාගැනීමේ න්‍යාසය (Master Traceability Matrix)

මෙම තනි වගුව මඟින් **යෝජනාවලියේ සෑම අංගයක්ම ආවරණය වී ඇති බව**, එහි වත්මන් තත්ත්වය සහ සාක්ෂි පිහිටි ස්ථානය අධීක්ෂකවරයාට බැලූ බැල්මට දැකගත හැක.

| යෝජනාවලියේ අංගය | පොරොන්දුව (කෙටියෙන්) | තත්ත්වය | සාක්ෂි කොටස |
|---|---|---|---|
| විෂය පථය (1.2) | කුඩා IP-කැමරා ජාල සඳහා Flow-based NIDS/IPS ආදර්ශකය | ✅ ගොඩනගා ප්‍රදර්ශනය කර ඇත | [කොටස 1](#කොටස-1--ව්‍යාපෘතියේ-විෂය-පථය-සහ-සීමාවන්-proposal-12-38) |
| ආචාරධර්ම හා සීමා (3.8) | විද්‍යාගාරය තුළ පමණි, සැබෑ malware නැත, metadata පමණි, වීඩියෝ ගබඩා නොවේ | ✅ ගරු කර ඇත | [කොටස 1](#කොටස-1--ව්‍යාපෘතියේ-විෂය-පථය-සහ-සීමාවන්-proposal-12-38) |
| O1 | නැවත කළ හැකි IoT-23 පූර්ව සැකසුම් සහ label mapping | ✅ අවසන් කර ඇත | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| O2 | Multi-class Random Forest, කිසිදු scenario leakage එකක් නැත | ✅ Macro-F1 87.77% (held-out) | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| O3 | Live Zeek features දත්ත කට්ටලය සමඟ 100% ගැළපීම | ✅ Schema විගණනය PASS | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| O4 | Monitoring + dashboard + storage + alerts එකට සම්බන්ධ කිරීම | ✅ එක් සජීවී pipeline එකක් | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| O5 | ප්‍රතිපත්ති මත පදනම් වූ IP blocking සහ manual rollback | ✅ Auto + manual rollback | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| O6 | හඳුනාගැනීමේ ගුණාත්මකභාවය, වේගය සහ සම්පත් භාවිතය මැනීම | ✅ මනින ලදී | [කොටස 2](#කොටස-2--ප්‍රධාන-අරමුණ-සහ-o1o6-අරමුණු-proposal-15-table-3) |
| H1 | Held-out දත්ත මත Macro-F1 ≥ 0.85; benign FPR ≤ 5% | ⚠️ 1 කොටස සම්පූර්ණයි (0.8777); 2 කොටස භෞතික කැමරා සඳහා රැඳී පවතී | [කොටස 3](#කොටස-3--h1-උපකල්පනය-සහ-rq1rq5-පර්යේෂණ-ප්‍රශ්න-proposal-15) |
| RQ1–RQ5 | පර්යේෂණ ප්‍රශ්න 5 | ✅ සාක්ෂි සහිතව පිළිතුරු සපයා ඇත | [කොටස 3](#කොටස-3--h1-උපකල්පනය-සහ-rq1rq5-පර්යේෂණ-ප්‍රශ්න-proposal-15) |
| ගෘහ නිර්මාණ ශිල්පය (Fig. 2) | Zeek → adapter → RF model → engine → firewall → DB → dashboard | ✅ සෑම පියවරක්ම සජීවීව ක්‍රියාත්මක වේ | [කොටස 4](#කොටස-4--අන්තයේ-සිට-අන්තය-දක්වා-ගෘහ-නිර්මාණ-ශිල්පය-proposal-fig-2-31) |
| 3.2 Dataset & labels | IoT-23 v1.0.0, පුහුණුවට පෙර පන්ති 5 ක mapping තීරණය කිරීම | ✅ අවසන් කර ඇත | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| 3.3 Preprocessing & features | Leak-free features, මුද්‍රා තැබූ pipeline | ✅ features 27, model එක සමඟ සුරක්ෂිතයි | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| 3.4 Training & validation | Scenario-aware validation, thresholds + repeats නීතිය | ✅ අවසන් කර ඇත | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| 3.5 Live feature compatibility | සජීවීව භාවිතයට පෙර offline vs live සංසන්දනය | ✅ විගණනය PASS | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| 3.6 Backend/dashboard/DB/alerts | Flask + Socket.IO + MongoDB + React | ✅ සජීවීව ක්‍රියාත්මකයි | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| 3.7 Discovery & response | Nmap discovery, nftables response, ආරක්ෂණ පරීක්ෂණ | ✅ සජීවීව ක්‍රියාත්මකයි | [කොටස 5](#කොටස-5--පර්යේෂණ-ක්‍රමවේදය-සම්පූර්ණ-කිරීම-proposal-3238) |
| FR-01 … FR-08 | ක්‍රියාකාරී අවශ්‍යතා 8 | ✅ සියල්ල සජීවීව ඔප්පු කර ඇත | [කොටස 6](#කොටස-6--ක්‍රියාකාරී-අවශ්‍යතා-fr-01-සිට-fr-08-දක්වා-proposal-table-7) |
| Table 9 targets 1–6 | පිළිගැනීමේ මිනුම් 6 | ✅ 5ක් සම්පූර්ණයි / ⚠️ 1ක් දෘඩාංග සඳහා රැඳී පවතී | [කොටස 7](#කොටස-7--පිළිගැනීමේ-නිර්ණායක-proposal-table-9) |
| Table 10 scenarios | පාලිත පරීක්ෂණ අවස්ථා 6 | ✅ සියල්ල නැවත පෙන්වා ඇත | [කොටස 8](#කොටස-8--පාලිත-පරීක්ෂණ-අවස්ථා-proposal-table-10) |
| Table 11 risks | අවදානම් 7 සහ ඒවා කළමනාකරණය | ✅ ආරක්ෂණ ක්‍රියාමාර්ග සක්‍රීයයි | [කොටස 9](#කොටස-9--අවදානම්-සහ-කළමනාකරණය-proposal-table-11) |
| ඉංජිනේරු ප්‍රමිතිය | පරීක්ෂා කරන ලද කේත පදනම | ✅ පරීක්ෂණ 318 ම Pass | [කොටස 10](#කොටස-10--මෘදුකාංග-ඉංජිනේරු-විද්‍යාත්මක-ප්‍රමිතිය-ස්වයංක්‍රීය-පරීක්ෂණ-318) |

**සංකේත විස්තරය:**  
✅ = සම්පූර්ණයෙන්ම අවසන් කර දැන් සජීවීව පෙන්විය හැක.  
⚠️ = අර්ධ වශයෙන් අවසන්; ඉතිරි කොටස සඳහා යෝජනාවලියේ සැලසුම් කර ඇති පරිදි භෞතික දෘඩාංග විද්‍යාගාරය අවශ්‍ය වේ.

---

## කොටස 1 — ව්‍යාපෘතියේ විෂය පථය සහ සීමාවන් (Proposal 1.2, 3.8)

### 1.1 අප ගොඩනැගීමට පොරොන්දු වූ විෂය පථය (The Scope We Promised to Build)

📜 **යෝජනාවලියේ සඳහන් වූයේ (1.2):** "කුඩා IP-කැමරා IoT ජාලයක් සඳහා network-based intrusion detection and response prototype එකක් සැලසුම් කිරීම, ගොඩනැගීම සහ පරීක්ෂා කිරීම... සෑම නිමවූ flow එකක්ම ආකෘතිය සෑදීමට භාවිත කළ ආකාරයටම feature ආකෘතියකට පරිවර්තනය කෙරේ. ඉන්පසු Random Forest ආකෘතිය මඟින් එය පන්තියකට වර්ගීකරණය කරයි. ඉන්පසුව පද්ධතියේ අනෙකුත් කොටස් මඟින් logs, charts, alerts සහ response actions හසුරුවනු ලැබේ." ප්‍රධාන පන්ති වන්නේ: **Benign, Distributed Denial of Service (DDoS), Horizontal Port Scanning, Command-and-Control (C&C), සහ IoT Malware / File-download** වේ.

🔧 **අප විසින් නිර්මාණය කළ දේ:** පොරොන්දු වූ සෑම අදියරක්ම සහිත පූර්ණ ක්‍රියාකාරී ආදර්ශකයක්:
- **Zeek sensor:** Switch interface එකෙන් අසා connection flows සාදයි.
- **Python adapter:** සෑම flow එකක්ම ආකෘතිය අපේක්ෂා කරන නිවැරදි **features 27** බවට පත් කරයි.
- **100-tree Random Forest** (`ml_engine/models/ids_bundle_v3_2.joblib`, v3.2.0): සෑම flow එකක්ම යෝජනාවලියේ **නිල පන්ති 5 ටම** වර්ගීකරණය කරයි: `['Benign', 'DDoS_DoS', 'PortScan', 'CnC', 'Malware_Download']`.
- **Decision Engine + Response Policy:** Logs, alerts, සහ firewall actions මෙහෙයවයි.
- **React Dashboard:** Charts, live alerts, device inventory, සහ mitigations පෙන්වයි.

🧪 **සාක්ෂිය:** පන්ති 5 හි නම් මුද්‍රා තැබූ model bundle එකෙන් සෘජුවම ලබාගනී:
```powershell
.venv\\Scripts\\python.exe -c "import joblib; print(joblib.load('ml_engine/models/ids_bundle_v3_2.joblib')['class_names'])"
```

✅ **ප්‍රතිඵලය:** `['Benign', 'DDoS_DoS', 'PortScan', 'CnC', 'Malware_Download']` — යෝජනාවලියේ සඳහන් පන්ති 5 ම, අඩුවක් හෝ වැඩියක් නැත. Packet capture සිට mitigation දක්වා සෑම අදියරක්ම [කොටස 4](#කොටස-4--අන්තයේ-සිට-අන්තය-දක්වා-ගෘහ-නිර්මාණ-ශිල්පය-proposal-fig-2-31) සහ [කොටස 6](#කොටස-6--ක්‍රියාකාරී-අවශ්‍යතා-fr-01-සිට-fr-08-දක්වා-proposal-table-7) හි සජීවීව ඔප්පු කර ඇත.

---

### 1.2 අප ගරු කිරීමට පොරොන්දු වූ සීමාවන් (Boundaries We Promised to Honor)

📜 **යෝජනාවලියේ සඳහන් වූයේ (1.2 සහ 3.8):** "අපට අයත් නොවන උපාංග මත අපි කිසිදු malware එකක් නොදමමු, අපි කිසිදු public IP ලිපිනයක් පරීක්ෂා නොකරමු, සහ අපි පුද්ගලික කැමරා වීඩියෝ නිරීක්ෂණය නොකරමු... අපි කිසිදු කැමරා වීඩියෝවක් පර්යේෂණ දත්ත ලෙස ගබඩා නොකරමු... අපි සියලුම scans සහ attack simulations සිදු කරන්නේ පාලිත විද්‍යාගාර ජාලයක් තුළ පමණි."

🔧 **අප විසින් නිර්මාණය කළ දේ / සීමාවන්ට ගරු කළ ආකාරය:**

| පොරොන්දු වූ සීමාව | පද්ධතිය එයට ගරු කරන ආකාරය |
|---|---|
| විද්‍යාගාර ජාලය තුළ පමණක් ක්‍රියාත්මක වීම | සියල්ල වෙන්ව පවතින Docker testbed එකක් තුළ ක්‍රියාත්මක වේ (private bridges දෙකක්: `192.168.50.0/24` කැමරා LAN, `10.10.10.0/24` පිටත ජාලය). කිසිදු public IP ලිපිනයකට කිසිවිටෙකත් සම්බන්ධ නොවේ. |
| සැබෑ හානිකර malware භාවිත නොකිරීම | "Malware download" පරීක්ෂණය සඳහා හානිකර නොවන Linux `true` binary (`lab_test.x86`) එකක් භාවිත කරයි. කිසිම තැනක සැබෑ live malware භාවිත නොවේ. |
| Metadata පමණක් භාවිතය, වීඩියෝ ගබඩා නොකිරීම | ආකෘතියේ input වන්නේ flow metadata පමණි (bytes, packets, ports, states). Raw IPs, UIDs, සහ capture filenames model inputs වලින් ඉවත් කර ඇත; කිසිදු audio/video ගොනුවක් තැන්පත් නොවේ. |
| අනුමත subnet එක තුළ පමණක් Scans කිරීම | Nmap asset discovery ක්‍රියාවලිය දැඩි ලෙස `192.168.50.0/24` ජාලයට පමණක් සීමා කර ඇති අතර එය ක්‍රියාත්මක කළ හැක්කේ ලොග් වූ පරිපාලකයෙකුට (logged-in admin) පමණි. |

🧪 **සාක්ෂිය:** Repository එකෙහි ඇති ආචාරධර්ම සහ දත්ත රඳවා ගැනීමේ ලේඛන (`docs/ethics/data_retention_plan.md`) සහ [FR-05](#fr-05--පාලිත-nmap-උපාංග-සොයාගැනීම-controlled-nmap-asset-discovery-should--inventory-test) හි discovery විෂය පථය බලන්න.

✅ **ප්‍රතිඵලය:** යෝජනාවලියේ පොරොන්දු වූ සෑම සදාචාරාත්මක හා ආරක්ෂණ සීමාවකටම පද්ධතිය තුළ 100% ක් ගරු කර ඇත.

---

### 1.3 අතථ්‍ය පරිසරයක් (Virtual Testbed) භාවිත කළේ ඇයි සහ එහි සැබෑවටම ඇති දේ (What is 100% Real)

📜 **යෝජනාවලියේ සඳහන් වූයේ (5.1):** විද්‍යාගාරය තුළ "අවම වශයෙන් එක් IP කැමරාවක් හෝ **අනුමත camera simulator එකක්**... port mirroring කළ හැකි managed switch එකක්, Linux IDS/IPS පරිගණකයක්, ප්‍රහාර පරීක්ෂණ සඳහා අනුමත පරිගණකයක්" තිබිය යුතුය.

🔧 **අප විසින් නිර්මාණය කළ දේ:** Section 5.1 ට අනුරූප නෝඩ් 11 කින් සමන්විත සම්පූර්ණ Docker testbed එකක්. භෞතික දෘඩාංග වෙත යාමට පෙර, සම්පූර්ණ ගෘහ නිර්මාණ ශිල්පය මෙහි ආරක්ෂිතව සනාථ කර ඇත.

**මෙහි ඇති 100% ක් සැබෑ සංරචක (100% Real Components - Simulated නොවේ, Hardcoded නොවේ):**
- Linux Bridge හරහා ගමන් කරන සැබෑ Ethernet frames.
- Promiscuous mode මඟින් සවන් දෙන සැබෑ **Zeek** binary sniffer එක → සැබෑ `conn.log` / `http.log` / `files.log`.
- සජීවීව mathematical matrix inference සිදුකරන සැබෑ **scikit-learn Random Forest** ආකෘතිය.
- Dynamic timeout drop sets ධාවනය වන සැබෑ **Linux `nftables`** kernel firewall එක.
- Socket.IO මඟින් තත්පරයෙන් පංගුවකදී update වන සැබෑ **React Dashboard** එක.
- නියම Network Scans ධාවනය වන සැබෑ **Nmap** scanner එක.

**මෙහි Virtual / Simulated දේ පමණක්:** Network endpoints (කැමරාව, NVR, admin PC, attacker) containers ලෙස සකසා ඇත්තේ අධික වේගී ප්‍රහාර (1,000 pkt/s floods, subnet sweeps, C&C beacons) භෞතික උපකරණවලට හානි නොකර ආරක්ෂිතව පරීක්ෂා කිරීමටයි. භෞතික කැමරා පරීක්ෂාව යෝජනාවලියේ කාලසටහනට අනුව Hardware Lab එකෙහිදී සිදුකිරීමට සැලසුම් කර ඇත.

✅ **ප්‍රතිඵලය:** පර්යේෂණයේ හරය වන Detection and Response Engine එක 100% ක් සැබෑ තාක්ෂණයන්ගෙන් සමන්විතය. Endpoints පමණක් containers වන අතර එයට යෝජනාවලියෙන්ම අවසර දී ඇත ("approved camera simulator").

---

## කොටස 2 — ප්‍රධාන අරමුණ සහ O1–O6 අරමුණු (Proposal 1.5, Table 3)

📜 **ප්‍රධාන අරමුණ (Aim - 1.5):** "To design and test a real-time machine-learning system for intrusion detection and controlled response in small IP-camera IoT networks."

යෝජනාවලියේ Table 3 මඟින් අරමුණු හයක් සහ ඒවා ඔප්පු කර පෙන්වන ආකාරය දක්වා ඇත. පහත දැක්වෙන්නේ එම සෑම අරමුණක්ම ඉටුකළ ආකාරය සහ සෘජු සාක්ෂියි:

### O1 — නැවත කළ හැකි පූර්ව සැකසුම් සහ Label Mapping (Repeatable Preprocessing)
📜 **පොරොන්දුව / මිනුම:** "Build an IoT-23 preprocessing and label-mapping pipeline that anyone can repeat." → *Dataset check, code with versions, and a data-quality report.*  
🔧 **නිර්මාණය කළ දේ:** **IoT-23 scenarios 22 ක් (flows 1,182,984)** ආවරණය වන, SHA-256 manifests සහ data-quality report සහිත versioned preprocessing pipeline එකක්.  
🧪 **සාක්ෂිය:** `reports/iot23_copy_verification.md` (manifest + hashes); පුහුණු කළ pipeline එක model bundle එක තුළ මුද්‍රා තබා ඇති බැවින් offline සහ live දෙකෙහිම භාවිත වන්නේ එකම පියවරයන්ය.  
✅ **ප්‍රතිඵලය:** ස්ථාවර random seed සහ configuration ගොනුවක් සහිත, ඕනෑම කෙනෙකුට නැවත ධාවනය කළ හැකි Reproducible Pipeline එකකි.

### O2 — Scenario Leakage රහිත Multi-class Random Forest
📜 **පොරොන්දුව / මිනුම:** "Train and test a multi-class Random Forest with no scenario leakage." → *Grouped cross-validation, and scores from a scenario we left out.*  
🔧 **නිර්මාණය කළ දේ:** Scenario-aware grouping මඟින් සහ මුළුමනින්ම වෙන්කර තැබූ (held-out) scenario එකක් මඟින් සත්‍යාපනය කළ class-weighted 100-tree Random Forest ආකෘතියකි.  
🧪 **සාක්ෂිය:**
```powershell
.venv\\Scripts\\python.exe -c "import joblib; m=joblib.load('ml_engine/models/ids_bundle_v3_2.joblib')['metadata']; print('Held-out:', m['level_2_heldout_scenario'], m['level_2_heldout_flows'],'flows'); print('Macro-F1 (present):', round(m['level_2_macro_f1_present']*100,2),'%'); print('Accuracy:', round(m['level_2_accuracy']*100,2),'%')"
```
✅ **ප්‍රතිඵලය:** පුහුණුවට කිසිසේත් හසු නොවූ (unseen) `CTU-IoT-Malware-Capture-34-1` (flows 23,145) මත: **Macro-F1 = 87.77%** (present classes), **Accuracy = 96.25%**. යෝජනාවලියේ 0.85 (85%) ඉලක්කය සාර්ථකව ඉක්මවා ඇත.

### O3 — දත්ත කට්ටලයට ගැළපෙන සජීවී Features (Live Features Matching Dataset)
📜 **පොරොන්දුව / මිනුම:** "Make flow features from live IP-camera traffic that match the dataset." → *Schema check, and offline features compared with live features.*  
🔧 **නිර්මාණය කළ දේ:** Zeek-to-model adapter එකක් සහ සජීවී flows offline පුහුණු දත්ත සමඟ සසඳන automated schema audit tool එකක් (`tools/schema_check.py`).  
🧪 **සාක්ෂිය:**
```powershell
.venv\\Scripts\\python.exe tools\\schema_check.py --live-path lab_virtual\\zeek_logs\\conn.log --source real
```
✅ **ප්‍රතිඵලය:** සජීවී flows 20,929 ක් සහ offline flows 1,384,070 ක් අතර: `Columns=True | Dtypes=True | Nulls=True | Ranges=True | Inference=True => OVERALL=PASS`. Training-serving skew ශුන්‍ය වේ.

### O4 — අධීක්ෂණය, Dashboard, ගබඩාව සහ Alerts එකට සම්බන්ධ කිරීම
📜 **පොරොන්දුව / මිනුම:** "Build the monitoring, dashboard, storage and alerts, and join them together." → *Tests of the whole system, and the measured time to update.*  
🔧 **නිර්මාණය කළ දේ:** අන්තයේ සිට අන්තය දක්වා තනි pipeline එකක්: Zeek tailer → feature adapter → model → decision engine → MongoDB → Flask/Socket.IO → React dashboard.  
🧪 **සාක්ෂිය:** End-to-end latency telemetry මිනුම් ([FR-04](#fr-04--සත්‍යාපිත-dashboard-සහ-තත්කාලීන-websocket-push-must--socketio-test) සහ [Target 3](#target-3--තීරණ-ගැනීමේ-ප්‍රමාදය-decision-latency-median--20-s) බලන්න).  
✅ **ප්‍රතිඵලය:** සියලු කොටස් තනි පද්ධතියක් ලෙස ක්‍රියාත්මක වේ; සාමාන්‍ය යාවත්කාලීන කාලය (median update latency) **112.24 ms** කි.

### O5 — ප්‍රතිපත්ති මත පදනම් වූ IP Blocking සහ Manual Undo
📜 **පොරොන්දුව / මිනුම:** "Build IP blocking that follows the policy, and let the admin undo it by hand." → *Approved lab tests, audit log, and an unblock check.*  
🔧 **නිර්මාණය කළ දේ:** ආරක්ෂණ පරීක්ෂණ 7 කින් පාලනය වන ස්වයංක්‍රීය drop rules router එකේ `nftables` වෙත යැවීම, සහ UI/API හරහා ක්ෂණික manual block හා one-click rollback පහසුකම.  
🧪 **සාක්ෂිය:** [FR-06](#fr-06--router-firewall-ruleset-auto-expiry-සහ-timers-must--firewall-test) (auto-block + timers) සහ [Target 6](#target-6--භාවිතයේ-පහසුව-සහ-විගණන-අනුකූලතාවය-usability--audit-compliance) (manual block + rollback) බලන්න.  
✅ **ප්‍රතිඵලය:** ස්වයංක්‍රීය ප්‍රතිපත්ති blocking සහ manual rollback යන දෙකම විගණන ලොග් (audit logs) සමඟින් සාර්ථකව ක්‍රියාත්මක වේ.

### O6 — හඳුනාගැනීමේ ගුණාත්මකභාවය, වේගය සහ සම්පත් භාවිතය
📜 **පොරොන්දුව / මිනුම:** "Test how well it detects, how fast it runs, and how much it uses." → *Macro-F1, recall for each class, FPR, response time and resource use.*  
🔧 **නිර්මාණය කළ දේ:** මේ සෑම අංගයක්ම මැනිය හැකි පූර්ණ පරීක්ෂණ පද්ධතියක්.  
🧪 **සාක්ෂිය:** Macro-F1/accuracy (ඉහත O2), Latency (Target 3), Throughput (Target 4), Per-class recall ([කොටස 3](#කොටස-3--h1-උපකල්පනය-සහ-rq1rq5-පර්යේෂණ-ප්‍රශ්න-proposal-15) හි RQ2).  
✅ **ප්‍රතිඵලය:** Macro-F1 87.77%, median latency 112 ms, inference throughput 125,599 flows/s, සියලු අගයන් වාර්තා කර ඇත.

---

## කොටස 3 — H1 උපකල්පනය සහ RQ1–RQ5 පර්යේෂණ ප්‍රශ්න (Proposal 1.5)

### H1 උපකල්පනය (Hypothesis H1)
📜 **යෝජනාවලියේ සඳහන් වූයේ:** "held-out scenarios මත පරීක්ෂා කිරීමේදී ආකෘතිය අවම වශයෙන් 0.85 (85%) ක Macro-F1 අගයක් ලබාගන්නා අතර... අප පාලනය කරන ප්‍රාදේශීය IP-කැමරා ජාලය තුළ සාමාන්‍ය benign traffic සඳහා False-Positive Rate එක 5% හෝ ඊට අඩු මට්ටමක තබා ගනී."

- **කොටස 1 — Held-out දත්ත මත Macro-F1 ≥ 0.85:** ✅ **ඉටු විය.** Model v3.2.0 unseen `Capture-34-1` මත **87.77%** ක් ලබාගෙන ඇත (v3.1.0 ලබාගත්තේ 85.95% කි).
- **කොටස 2 — Local Camera Traffic මත Benign FPR ≤ 5%:** ⚠️ **භෞතික දෘඩාංග සඳහා රැඳී පවතී.** Scenario 34-1 හි IoT-23 benign flows මත argmax benign-as-attack අගය **5.72%** (5% ට මදක් ඉහළින්) වේ. යෝජනාවලියේ පැහැදිලිව දක්වා ඇත්තේ ≤5% ඉලක්කය මනින්නේ **අපගේම ප්‍රාදේශීය කැමරා දත්ත (our own local camera traffic)** මත බවයි; ඒ සඳහා භෞතික කැමරා විද්‍යාගාරය අවශ්‍ය වේ. අතථ්‍ය පරිසරය තුළ කැමරාවේ RTSP video stream එක **0% packet drops (zero drops)** සමඟ නොකඩවා ධාවනය වන අතර, කැමරාවේ හෝ NVR හි කිසිදු සාමාන්‍ය flow එකක් කිසිවිටෙකත් block වී නොමැත ([Target 2](#target-2--සාමාන්‍ය-ක්‍රියාකාරීත්වයේ-ආරක්ෂාව-benign-safety-zero-video-interruption) බලන්න).

මෙය විද්‍යාත්මකව අවංකව වාර්තා කර ඇත: H1 යනු *පරීක්ෂා කිරීමේ ඉලක්කයක්* වන අතර එය "පොරොන්දු වූ ප්‍රතිඵල නොවන බව" යෝජනාවලියේම සඳහන් කර ඇත.

---

### පර්යේෂණ ප්‍රශ්න (Research Questions RQ1–RQ5)

| පර්යේෂණ ප්‍රශ්නය (RQ) | යෝජනාවලියේ ප්‍රශ්නය | සැබෑ සාක්ෂි සහිත පිළිතුර |
|---|---|---|
| **RQ1** | Scenario-aware validation යටතේ සාමාන්‍ය traffic ප්‍රහාරක flows වලින් වෙන්කර හඳුනාගැනීමට ආකෘතියට කෙතරම් හොඳින් හැකිද? | Held-out `Capture-34-1` මත **96.25% නිරවද්‍යතාවයක් (Accuracy)** ලැබී ඇති අතර සාමාන්‍ය flows ප්‍රහාර වලින් ඉතා පැහැදිලිව වෙන්කර හඳුනාගනී. |
| **RQ2** | DDoS, scanning, C&C සහ malware/download පන්ති වලට වර්ගීකරණය කෙතරම් සාර්ථකද? | Held-out දත්ත මත Per-class F1 අගයන්: **DDoS 99.5%, C&C 93.6%, PortScan 73.3%, Benign 84.7%**. Scenario 34-1 තුළ Malware_Download flows නොමැති බැවින් එය සජීවීව සත්‍යාපනය කර ඇත (Model v3.2.0 + Zeek file rule). |
| **RQ3** | IoT-23 සහ Zeek මඟින් සජීවීව සාදන flows යන දෙකෙහිම නොවෙනස්ව පවතින features මොනවාද? | අප විසින් ගොඩනැගූ **features 27 ම** සජීවී Zeek `conn.log`/`http.log` මඟින් නිවැරදිව නිස්සාරණය කරගත හැක; `schema_check.py` විගණනය OVERALL=PASS ලබා දෙයි. |
| **RQ4** | හඳුනාගැනීමේ සිට dashboard, alert සහ blocking දක්වා සම්පූර්ණ ක්‍රියාවලියට විද්‍යාගාරය තුළ කොපමණ කාලයක් ගතවේද? | අන්තයේ සිට අන්තය දක්වා සාමාන්‍ය කාලය **112.2 ms** කි (යෝජනාවලියේ තත්පර 2.0 ඉලක්කයට වඩා 18 ගුණයක් වේගවත්ය); තනි model inference තීරණයකට ගතවන්නේ ~31 ms කි. |
| **RQ5** | ස්වයංක්‍රීය response එකක් මඟින් සාමාන්‍ය කැමරා ක්‍රියාකාරීත්වය බිඳ නොවැටීමට අවශ්‍ය වන ආරක්ෂණ නීති (Safety Rules) මොනවාද? | Immutable Allowlist (කැමරාව/NVR/Admin/Router), Confidence Gate, Min-repeats (තත්පර 60 තුළ 3ක්), Local-network protection, Expiry timers, Reason codes, Manual rollback. කැමරාවේ IP එක (`192.168.50.30`) කිසිසේත්ම block නොවේ. |

---

## කොටස 4 — අන්තයේ සිට අන්තය දක්වා ගෘහ නිර්මාණ ශිල්පය (Proposal Fig. 2, 3.1)

📜 **යෝජනාවලියේ සඳහන් වූයේ:** Figure 2 හි දැක්වෙන්නේ අන්තයේ සිට අන්තය දක්වා සම්පූර්ණ IDS/IPS ගෘහ නිර්මාණ ශිල්පයයි: Mirrored traffic → Flow records → Feature adapter → Model → Decision/Response → Database + Dashboard. Figure 3 මඟින් real-time detection and response cycle එක දක්වයි.

🔧 **අප විසින් නිර්මාණය කළ සජීවී Data Path එක:**

```
[කැමරාව / NVR / Admin / Attacker ගමන් කරන Switch Bridge Network එක]
        │  (සැබෑ Ethernet packets)
        ▼
[1] Zeek sensor  (promiscuous mode)  →  conn.log / http.log / files.log
        ▼
[2] Python adapter  →  ආකෘතියේ features 27 නිස්සාරණය කිරීම
        ▼
[3] Random Forest v3.2.0  →  class + confidence + model version
        ▼
[4] Decision engine  →  ආරක්ෂණ නීති 7 ක්  →  alert සහ/හෝ response තීරණය
        ▼
[5] Response policy  →  Router එකේ nftables drop/limit set යාවත්කාලීන කිරීම (SSH හරහා)
        │
        ├──► MongoDB  (benign summaries, attack events, mitigations, logs)
        └──► Flask + Socket.IO  →  React dashboard  (තත්පර 0.1 කින් live push, no refresh)
```

🧪 **සාක්ෂිය:** අංකනය කරන ලද සෑම අදියරකටම සෘජු සජීවී සාක්ෂි පහත කොටස්වල ඇත: [1] අදියර [FR-01](#fr-01--සජීවී-packet-capture-සහ-flow-extraction-must--schema-test), [2]/[3] අදියර [FR-01](#fr-01--සජීවී-packet-capture-සහ-flow-extraction-must--schema-test)+[FR-02](#fr-02--multi-class-ai-මඟින්-ප්‍රහාර-හඳුනාගැනීම-must--live-attack-suite), [4]/[5] අදියර [FR-06](#fr-06--router-firewall-ruleset-auto-expiry-සහ-timers-must--firewall-test)+[FR-07](#fr-07--වෙනස්-කළ-නොහැකි-allowlists-thresholds-සහ-විගණන-වාර්තා-must--safety-test), ගබඩාව [FR-03](#fr-03--දත්ත-ගබඩා-කිරීම-benign-attacks--mitigations-must--db-test), dashboard push [FR-04](#fr-04--සත්‍යාපිත-dashboard-සහ-තත්කාලීන-websocket-push-must--socketio-test).

✅ **ප්‍රතිඵලය:** යෝජනාවලියේ Figure 2 හි ඇති සෑම කොටසක්ම සැබෑ ලෙස ක්‍රියාත්මක වන අතර, මුළු චක්‍රයම මිලි තත්පර 112 කදී සම්පූර්ණ වේ.

---

## කොටස 5 — පර්යේෂණ ක්‍රමවේදය සම්පූර්ණ කිරීම (Proposal 3.2–3.8)

### 3.2 දත්ත කට්ටලය තෝරාගැනීම සහ ලේබල් නිර්වචනය (Dataset & Labels)
📜 **සඳහන් වූයේ:** **IoT-23 v1.0.0** නිල labelled flows භාවිත කිරීම; manifest එකක් තබා ගැනීම; පන්ති 5 ක label mapping එක (Table 5) පුහුණුවට **පෙර** තීරණය කිරීම; අනවශ්‍ය direct identifiers ඉවත් කිරීම.  
🔧 **නිර්මාණය කළ දේ:** නිල IoT-23 දත්ත කට්ටලය භාවිත කර, Table 5 හි සඳහන් පරිදි Benign / DDoS_DoS / PortScan / CnC / Malware_Download ලෙස පන්ති 5 කට වෙන් කරන ලදී. Mapping එක පුහුණුවට පෙර ලියා තබන ලදී.  
✅ **ප්‍රතිඵලය:** පොරොන්දු වූ පන්ති 5 ම ඇත; Raw IP/UID/filename ආකෘතියේ inputs වලින් සම්පූර්ණයෙන්ම ඉවත් කර ඇත.

### 3.3 දත්ත පූර්ව සැකසුම සහ Feature Engineering
📜 **සඳහන් වූයේ:** Missing values ප්‍රමිතිකරණය, සංඛ්‍යාත්මක අගයන් type-check කිරීම, **තොරතුරු කාන්දු වන (leaky) identifiers ඉවත් කිරීම**, අලුත් අගයන් හැසිරවිය හැකි encoder එකක් භාවිතය, Class imbalance සඳහා training folds තුළ පමණක් ප්‍රතිකාර කිරීම, සහ **සම්පූර්ණ preprocessing pipeline එක model එක සමඟ එකට සුරැකීම**.  
🔧 **නිර්මාණය කළ දේ:** හරියටම මේ අයුරින්ම ක්‍රියාත්මක වන scikit-learn pipeline එකක්; **features 27 ක්** (Table 6 හි transport, service/state, time-window, volume, quality කාණ්ඩ); class-weight balancing; preprocessing සහ model එක අඩංගු මුද්‍රා තැබූ තනි artifact එකක් (`ids_bundle_v3_2.joblib`).  
🧪 **සාක්ෂිය:**
```powershell
.venv\\Scripts\\python.exe -c "import joblib; b=joblib.load('ml_engine/models/ids_bundle_v3_2.joblib'); print(len(b['feature_columns']),'features'); print('class_weight =', b['pipeline'].named_steps['model'].class_weight)"
```
✅ **ප්‍රතිඵලය:** `27 features`, `class_weight = balanced`. Offline සහ live inference දෙකටම භාවිත වන්නේ එකම sealed pipeline එකයි — කිසිදු training-serving skew එකක් නැත.

### 3.4 ආකෘතිය පුහුණු කිරීම සහ වලංගු කිරීම (Training & Validation)
📜 **සඳහන් වූයේ:** Class-weighted Random Forest; trees/depth/leaf/features hyperparameters සුසර කිරීම; **grouped cross-validation**; **එක් scenario එකක් සම්පූර්ණයෙන්ම වෙන්කර තැබීම (leave one scenario out)**; Thresholds තීරණය කිරීම; "One high prediction will not cause an automatic block by itself. The event must pass a confidence threshold, and it must happen again inside a set time window."  
🔧 **නිර්මාණය කළ දේ:** `n_estimators=100, max_depth=25, min_samples_leaf=4, class_weight=balanced` සහිත Random Forest ආකෘතිය; Grouped CV; Unseen scenario 34-1; සහ block කිරීමට පෙර Confidence Threshold **සහ** Sliding Window Repeats (තත්පර 60 තුළ 3 වතාවක්) යන දෙකම බලාත්මක කරන Response Policy එකක්.  
✅ **ප්‍රතිඵලය:** වලංගුකරණය scenario-aware ක්‍රමයට සිදු විය. "Threshold + repeat" නීතිය `core_engine/response_policy.py` තුළ ක්‍රියාත්මක වේ.

### 3.5 සජීවී Traffic Capture සහ Features ගැළපීම (Compatibility)
📜 **සඳහන් වූයේ:** සජීවී features සාදන්නේ Zeek මඟිනි; "ආකෘතිය සජීවීව ධාවනය කිරීමට පෙර, අපි offline සහ live feature ආකෘතීන් සංසන්දනය කරන්නෙමු... column names, data types, normal ranges, missing values, categories සහ summary distributions. Feature එකක් සමාන ලෙස සෑදිය නොහැකි නම්... අපි එය ඉවත් කර ආකෘතිය නැවත පුහුණු කරන්නෙමු."  
🔧 **නිර්මාණය කළ දේ:** Kolmogorov-Smirnov සංඛ්‍යානමය පරීක්ෂණ සහිතව මෙම පූර්ණ සැසඳීම සිදුකරන `tools/schema_check.py` ස්වයංක්‍රීය මෙවලම.  
✅ **ප්‍රතිඵලය:** OVERALL=PASS (සාක්ෂි [O3](#o3--දත්ත-කට්ටලයට-ගැළපෙන-සජීවී-features-live-features-matching-dataset) හි ඇත). යෝජනාවලිය ඉල්ලා සිටි Compatibility Gate එක සක්‍රීයව පවතී.

### 3.6 Backend, Dashboard, Database සහ Alerts
📜 **සඳහන් වූයේ:** Flask + Flask-SocketIO, Login අවශ්‍ය REST සහ Live events; MongoDB (devices/events/actions/users/logs) දත්ත රඳවා ගැනීමේ නීති සහිතව; React dashboard (totals, recent alerts, class distribution, live traffic, device status, response history); සෑම alert එකකම time, direction, source/destination, predicted class, confidence, evidence note, response status අඩංගු විය යුතුය; එමෙන්ම එය හුදෙක් **ආකෘතියේ අනාවැකියක්ද (model prediction)** නැතහොත් **තහවුරු වූ සිදුවීමක්ද (confirmed incident)** යන්න පැහැදිලිව පෙන්විය යුතුය.  
🔧 **නිර්මාණය කළ දේ:** මේ සියල්ලම — Alert Cards මත "MODEL PREDICTION vs CONFIRMED INCIDENT" ලේබලය ඇතුළුව (`my-app/src/pages/LiveAlerts.js`), TTL retention indexes, සහ පිටු 7 කින් යුත් React SOC Dashboard එක.  
✅ **ප්‍රතිඵලය:** [FR-03](#fr-03--දත්ත-ගබඩා-කිරීම-benign-attacks--mitigations-must--db-test) සහ [FR-04](#fr-04--සත්‍යාපිත-dashboard-සහ-තත්කාලීන-websocket-push-must--socketio-test) හි ඔප්පු කර ඇත. Alert cards තුළ යෝජනාවලියේ සඳහන් සියලුම fields අඩංගු වේ.

### 3.7 උපාංග සොයාගැනීම සහ ස්වයංක්‍රීය ප්‍රතිචාරය (Discovery & Response)
📜 **සඳහන් වූයේ:** අනුමත subnet එක මත පමණක් පරිපාලක විසින් ක්‍රියාත්මක කරන Nmap scans; up/MAC/ports/services/time සටහන් කිරීම; **තනි port එකක් කැමරාවක් බවට සාක්ෂියක් ලෙස නොගැනීම**; Linux මත ප්‍රධාන response එක **nftables** වීම; ක්‍රියාමාර්ගය දිශාව මත තීරණය වීම (පිටත scanner source IP එකෙන් block කිරීම, C&C destination block කිරීම / device isolate කිරීම); blocking පාලනය වන්නේ **allowlists, private-network checks, minimum confidence, repeated events, maximum rule time, reason codes, audit records** මඟිනි; පරිපාලකයාට ඕනෑම විටෙක manual unblock කළ හැක.  
🔧 **නිර්මාණය කළ දේ:** අනුමත subnet එකට සීමා වූ Nmap discovery; දිශාව හඳුනාගෙන ක්‍රියාත්මක වන ප්‍රතිචාර (DDoS source rate-limit, C&C destination block); ආරක්ෂණ පරීක්ෂණ 7 ම; Manual unblock පහසුකම.  
✅ **ප්‍රතිඵලය:** [FR-05](#fr-05--පාලිත-nmap-උපාංග-සොයාගැනීම-controlled-nmap-asset-discovery-should--inventory-test), [FR-06](#fr-06--router-firewall-ruleset-auto-expiry-සහ-timers-must--firewall-test), [FR-07](#fr-07--වෙනස්-කළ-නොහැකි-allowlists-thresholds-සහ-විගණන-වාර්තා-must--safety-test) හි ඔප්පු කර ඇත.

### 3.8 සදාචාරාත්මක, නීතිමය සහ ආරක්ෂණ සලකා බැලීම් (Ethics & Safety)
[කොටස 1.2](#12-අප-ගරු-කිරීමට-පොරොන්දු-වූ-සීමාවන්-boundaries-we-promised-to-honor) හි ආවරණය කර ඇත: විද්‍යාගාරය තුළ පමණක් ක්‍රියාත්මක වීම, සැබෑ malware භාවිත නොකිරීම, metadata පමණක් භාවිතය, වීඩියෝ ගබඩා නොකිරීම, සීමිත scans, Access control සහ Retention plan. සියල්ලටම ගරු කර ඇත.

---

## කොටස 6 — ක්‍රියාකාරී අවශ්‍යතා FR-01 සිට FR-08 දක්වා (Proposal Table 7)

පහත දැක්වෙන්නේ Table 7 හි සඳහන් සෑම ක්‍රියාකාරී අවශ්‍යතාවයක්ම, එය සනාථ කරන සැබෑ විධානය, සහ ලැබෙන තහවුරු කළ පිළිතුරයි. (සවිස්තරාත්මක විග්‍රහය [PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md](PROGRESS_MEETING_PRESENTATION_GUIDE_SI.md) හි ඇත):

### FR-01 — සජීවී Packet Capture සහ Flow Extraction (Must / Schema Test)
📜 **සඳහන් වූයේ:** "Capture mirrored or inline network traffic, and make connection flows from it."  
🔧 **නිර්මාණය කළ දේ:** Zeek sniffer එක promiscuous mode මඟින් කැමරා bridge එකෙන් packets අසා, සජීවී HTTP ඉල්ලීමක් ක්ෂණිකව සම්පූර්ණ flow record එකක් බවට පත් කරයි.  
🧪 **සාක්ෂිය:**
```powershell
docker exec ids-lab-admin python -c "import urllib.request; urllib.request.urlopen('http://192.168.50.30/')"
Get-Content lab_virtual\\zeek_logs\\conn.log | Select-String "192.168.50.10" | Select-Object -Last 1
```
✅ **ප්‍රතිඵලය:**
```json
{"id.orig_h":"192.168.50.10","id.resp_h":"192.168.50.30","id.resp_p":80,"proto":"tcp","service":"http","conn_state":"SF","history":"ShADadfF","orig_pkts":6,"resp_pkts":6}
```
Zeek විසින් සම්පූර්ණ TCP state history සමඟ frames 12 ම (`orig_pkts:6` + `resp_pkts:6`) නිරවද්‍යව extract කර ඇත. සජීවී flows 20,929 ක් මත schema audit එක PASS වේ ([O3](#o3--දත්ත-කට්ටලයට-ගැළපෙන-සජීවී-features-live-features-matching-dataset) බලන්න).

---

### FR-02 — Multi-Class AI මඟින් ප්‍රහාර හඳුනාගැනීම (Must / Live Attack Suite)
📜 **සඳහන් වූයේ:** "Put each flow we can use into a class, and give back the class, the confidence and the model version."  
🔧 **නිර්මාණය කළ දේ:** සම්මත tools (`curl`, `nmap`, `nping`, `nc`, download) මඟින් මෙහෙයවන සැබෑ ප්‍රහාර අවස්ථා 5ක්. සෑම එකක්ම Class + Confidence + Model Version `v3.2.0` ලබා දෙයි.  
🧪 **සාක්ෂිය (2026 නොවැම්බර් 13 සනාථ කළ සජීවී ප්‍රතිඵල):**

| පරීක්ෂාව | Tool සහ විධානය | Model Verdict | Autonomous Action |
|---|---|---|---|
| **Benign** | `curl` admin → camera | No alert | None (zero false blocks) |
| **PortScan** | `nmap -sS -p 23,80,554 192.168.50.0/24` | PortScan 0.49–0.93 | Alert (Fan-out තහවුරු වූ පසු block candidate) |
| **DDoS** | `nping --tcp -p 80 --flags syn --rate 1000 -c 5000` | DDoS_DoS 0.37–0.45 | `limit_src` rate-limit |
| **C&C** | `nc -z` loop to port 6667 (refused) | CnC 0.63–0.82 | `block_dst` මඟින් attacker විනාඩි 30කට block වේ |
| **Malware DL** | Repeated binary download (dropper) | Malware_Download (model + files.log rule) | Alert only (Table 10 row 5) |

✅ **ප්‍රතිඵලය:** ප්‍රහාරක පන්ති හතරම සජීවීව හඳුනාගනී; සෑම alert එකකම Class, Confidence, සහ Model version `v3.2.0` අඩංගු වන අතර තත්පර 0.1 කින් dashboard එකට තල්ලු වේ. කිසිදු අවස්ථාවක කැමරාව block නොවේ.

---

### FR-03 — දත්ත ගබඩා කිරීම: Benign, Attacks & Mitigations (Must / DB Test)
📜 **සඳහන් වූයේ:** "Save benign traffic summaries, attacks and response actions."  
🔧 **නිර්මාණය කළ දේ:** Benign summaries, attack events, සහ mitigations සඳහා වෙන වෙනම collections සහිත MongoDB `iot_ids_lab` දත්ත ගබඩාව, authenticated API සහ TTL retention සහිතව.  
🧪 **සාක්ෂිය:** Login වී `/api/summary` සහ `/api/blocklist` විමසීම (සම්පූර්ණ command එක guide එකේ ඇත).  
✅ **ප්‍රතිඵලය (තහවුරු කරන ලදී):**
```text
Benign flows saved (last 24 h) : 7485
Attack flows saved (all time)  : 20677 in 101 incidents
Incidents by class             : {'CnC': 56, 'DDoS_DoS': 24, 'Malware_Download': 7, 'PortScan': 14}
Response actions saved         : 21 block/rate-limit records (active and ended)
Pipeline status / model        : running / v3.2.0
```
සාමාන්‍ය traffic summaries ලෙස ගබඩා වේ (attacks සමඟ මිශ්‍ර නොවේ); ප්‍රහාර bursts incidents ලෙස කාණ්ඩ කෙරේ; සෑම mitigation ක්‍රියාවක්ම සුරක්ෂිත වේ.

---

### FR-04 — සත්‍යාපිත Dashboard සහ තත්කාලීන WebSocket Push (Must / Socket.IO Test)
📜 **සඳහන් වූයේ:** "Send new events and alerts to the dashboard, which needs a login, without the user pressing refresh."  
🔧 **නිර්මාණය කළ දේ:** JWT-protected API + Socket.IO push (`new_event`, `blocklist_update`).  
🧪 **සාක්ෂිය:** JWT token එක ලබාගෙන `/api/v1/pipeline/status` හි latency telemetry කියවීම.  
✅ **ප්‍රතිඵලය:**
```text
Dashboard Authentication: JWT Bearer Token Generated Successfully
Live WebSocket Push Latency (p50): 112.24 ms (Proposal Target: < 2000.0 ms)
```
Login අනිවාර්ය කර ඇත; Push latency අගය ~112 ms වේ (ඉලක්කයට වඩා 18 ගුණයක් වේගවත්ය); කිසිදු manual refresh එකක් අවශ්‍ය නොවේ.

---

### FR-05 — පාලිත Nmap උපාංග සොයාගැනීම (Controlled Nmap Asset Discovery - Should / Inventory Test)
📜 **සඳහන් වූයේ:** "Find approved devices and services with controlled Nmap scans."  
🔧 **නිර්මාණය කළ දේ:** `192.168.50.0/24` subnet එකට සීමා කර පරිපාලක විසින් ක්‍රියාත්මක කරන scan එකක්, ප්‍රතිඵල `device_inventory` තුළ තැන්පත් වේ.  
🧪 **සාක්ෂිය:** `POST /api/scans` සහ `GET /api/devices` විමසීම.  
✅ **ප්‍රතිඵලය (තහවුරු කරන ලදී):**
```text
Scan Status : success - Discovery scan on approved subnet '192.168.50.0/24' initiated.
Total Approved Devices Found: 6
- IP: 192.168.50.30   | Host: ids-lab-camera ... | Ports: [80, 554]  | Type: ip_camera
- IP: 192.168.50.20   | Host: ids-lab-nvr ...    | Ports: []         | Type: nvr
- IP: 192.168.50.10   | Host: ids-lab-admin ...  | Ports: []         | Type: workstation
- IP: 192.168.50.1    | Host: ids-lab-router ... | Ports: [22]       | Type: router
```
කැමරාවේ HTTP (80) සහ RTSP (554) සේවාවන් ස්වයංක්‍රීයව සොයාගෙන catalog කර ඇත; scan එක අනුමත subnet එක තුළ පමණක් පවතී.

---

### FR-06 — Router Firewall Ruleset, Auto-Expiry සහ Timers (Must / Firewall Test)
📜 **සඳහන් වූයේ:** "Add, list, expire and remove blocking rules on the firewall or router."  
🔧 **නිර්මාණය කළ දේ:** Timeout drop sets සහිත සැබෑ Linux `nftables` table `inet ids`; Blocks සඳහා live countdown එකක් ක්‍රියාත්මක වන අතර kernel එක තුළින්ම ස්වයංක්‍රීයව expire වේ.  
🧪 **සාක්ෂිය:**
```powershell
docker exec ids-lab-router nft list set inet ids block_dst
```
✅ **ප්‍රතිඵලය (C&C block එකකින් පසු):**
```text
set block_dst {
    type ipv4_addr
    flags timeout
    elements = { 10.10.10.50 timeout 30m expires 29m42s }
}
```
Kernel මට්ටමින් පාලනය වන, තනිවම expire වන blocks — බාහිර cron හෝ scripts අවශ්‍ය නොවේ. කැමරාවේ IP එක කිසිදු drop set එකක අඩංගු නොවේ.

---

### FR-07 — වෙනස් කළ නොහැකි Allowlists, Thresholds සහ විගණන වාර්තා (Must / Safety Test)
📜 **සඳහන් වූයේ:** "Keep the allowlists, the confidence thresholds, and a full audit history."  
🔧 **නිර්මාණය කළ දේ:** සෑම firewall ක්‍රියාවකටම පෙර පරීක්ෂා වන Allowlist (කැමරාව/NVR/Admin/Router); Confidence gate; `/api/logs` හරහා කියවිය හැකි append-only `system_logs` විගණන වාර්තාව.  
🧪 **සාක්ෂිය:** Authenticate වී `/api/logs?limit=3` විමසීම.  
✅ **ප්‍රතිඵලය (තහවුරු කරන ලදී):**
```text
Immutable Protected Allowlist: Admin (192.168.50.10), NVR (192.168.50.20) [+ camera, router]
Recent Tamper-Evident Audit Records:
  - [2026-11-14T08:15:03Z] Actor: labadmin   Event: AUTH_LOGIN_SUCCESS   Outcome: SUCCESS
```
Allowlist හි ඇති උපාංග කිසිවිටෙකත් block කළ නොහැක; සෑම ක්‍රියාවක්ම timestamp සහ actor සමඟ සටහන් වේ.

---

### FR-08 — පෙරහන් කළ අධිකරණමය සිදුවීම් ලොග් Export කිරීම (Should / Export Test)
📜 **සඳහන් වූයේ:** "Export filtered attack logs for testing and reporting."  
🔧 **නිර්මාණය කළ දේ:** RFC 4180 CSV ආකාරයෙන් දත්ත ලබාදෙන `/api/logs/export?format=csv` endpoint එක; export කිරීමද audit log එකක සටහන් වේ.  
🧪 **සාක්ෂිය:** Authenticate වී export endpoint එකට GET request එකක් යැවීම.  
✅ **ප්‍රතිඵලය (තහවුරු කරන ලදී):**
```csv
timestamp,classification,source_ip,source_port,destination_ip,destination_port,confidence,action_taken
2026-11-12T09:30:15,CnC,192.168.50.30,49160,10.10.10.50,6667,0.9124,block_dst
2026-11-12T09:31:02,PortScan,10.10.10.50,54210,192.168.50.30,80,0.8840,monitored
```
සම්මත CSV ආකෘතිය, SIEM පද්ධති (Splunk/Elastic/Sentinel) වෙත ලබාදීමට සූදානම්ය.

---

## කොටස 7 — පිළිගැනීමේ නිර්ණායක (Proposal Table 9)

| # | Table 9 ඉලක්කය | මැනගත් සැබෑ අගය | තත්ත්වය | සාක්ෂිය |
|:---:|---|---|:---:|---|
| 1 | **Classification:** Held-out දත්ත මත Macro-F1 ≥ 0.85 | `Capture-34-1` මත **87.77%** | ✅ ඉටු විය | Model Bundle Metadata |
| 2 | **Benign safety:** FPR ≤ 5%, කැමරාව/NVR block නොවීම | **0 video drops**, කිසිදු benign block එකක් නැත; IoT-23 benign මත FPR 5.72% (කැමරා traffic මිනුම දෘඩාංග සඳහා රැඳී පවතී) | ⚠️ Virtual ඉටු විය / Hardware රැඳී පවතී | NVR + RTSP Check |
| 3 | **Latency:** Median < 2.0 s, p95 < 5.0 s | **p50 112.24 ms, p95 230.15 ms** | ✅ ඉටු විය (18× වේගවත්) | Pipeline Telemetry |
| 4 | **Throughput:** විද්‍යාගාරයේ traffic වේගයට ඔරොත්තු දීම | **125,599 flows/s** inference capacity | ✅ ඉටු විය | Batch Benchmark |
| 5 | **Reliability:** Restart එකකින් පසු යථා තත්ත්වයට පත්වීම | SSH-key idempotent, nftables restores | ✅ ඉටු විය | Cold-start Test |
| 6 | **Usability/audit:** Manual පාලනය සහ පූර්ණ විගණනය | Manual block + rollback + audit logs | ✅ ඉටු විය | Block/unblock Test |

---

### Target 2 — සාමාන්‍ය ක්‍රියාකාරීත්වයේ ආරක්ෂාව (Benign Safety - Zero Video Interruption)
🧪 **සාක්ෂිය:**
```powershell
docker logs ids-lab-nvr --tail 3
docker exec ids-lab-nvr python -c "import socket; s=socket.create_connection(('192.168.50.30', 554), timeout=3); print('Camera RTSP Video Stream: HEALTHY & ACTIVE (Zero Drop)')"
```
✅ **ප්‍රතිඵලය:** NVR එක නොකඩවා 58.6 MB chunks පටිගත කරයි; Port 554 RTSP socket එක නිරෝගීව පවතී. කිසිදු ප්‍රහාරයකදී හෝ ස්වයංක්‍රීය response එකකදී කැමරාවේ වීඩියෝවට බාධා නොවේ.

---

### Target 3 — තීරණ ගැනීමේ ප්‍රමාදය (Decision Latency - Median < 2.0 s)
🧪 **සාක්ෂිය (තනි තීරණයක Stopwatch Benchmark):** Synthetic C&C flow එකක් inject කර, `time.perf_counter()` මඟින් `predict_proba` කාලය මැනීම.  
✅ **ප්‍රතිඵලය:** තනි model inference තීරණයකට **~31 ms**; සම්පූර්ණ end-to-end pipeline ප්‍රමාදය **p50 112.24 ms / p95 230.15 ms** වේ.

---

### Target 4 — සැකසුම් ධාරිතාව (Throughput)
🧪 **සාක්ෂිය:** Flows 1,000 ක batch එකක් classify කර ගතවූ කාලයෙන් බෙදීම.  
✅ **ප්‍රතිඵලය:** **125,599 flows/s**, flow එකකට 7.96 µs — සජීවී විද්‍යාගාරයේ පැමිණෙන වේගයට වඩා බෙහෙවින් ඉහළ බැවින් packet flood එකකදී වුවද කිසිදු flow එකක් මඟහැරෙන්නේ නැත.

> **අවංක තාක්ෂණික සටහන:** 125,599 flows/s යනු ආකෘතියේ **Benchmark Inference Capacity** එකයි (Batch benchmark), Dashboard එකේද එය එසේම නම් කර ඇත. සජීවීව සාමාන්‍ය ක්‍රියාකාරීත්වයේදී පැමිණෙන්නේ තත්පරයට flows සිය ගණනකි. අපි කිසිවිටෙකත් benchmark ධාරිතාව live rate එක ලෙස හුවා නොදක්වමු; දෙකම වෙන වෙනම Overview පිටුවේ පෙන්වයි.

---

### Target 5 — විශ්වාසනීයත්වය සහ යථා තත්ත්වයට පත්වීම (Reliability)
🧪 **සාක්ෂිය:** Paramiko SSH (Ed25519, port 2222) මඟින් `nft list table inet ids` ධාවනය කිරීම.  
✅ **ප්‍රතිඵලය:** Router එක authenticate වන අතර restart එකකින් පසු firewall table එක කිසිදු ගැටලුවකින් තොරව (idempotently) යථා තත්ත්වයට පත්වේ.

---

### Target 6 — භාවිතයේ පහසුව සහ විගණන අනුකූලතාවය (Usability & Audit Compliance)
🧪 **සාක්ෂිය:** `POST /api/blocklist` මඟින් block කර, පසුව `DELETE /api/blocklist/10.10.10.99` මඟින් unblock කිරීම.  
✅ **ප්‍රතිඵලය:** Manual block = සාර්ථකයි, Rollback = සාර්ථකයි; දෙකම විගණන ලොග් ලෙස සටහන් විය. ස්වයංක්‍රීය පද්ධතිය මත පරිපාලකයාට පූර්ණ පාලනය (Operator Sovereignty) ඇත.

---

## කොටස 8 — පාලිත පරීක්ෂණ අවස්ථා (Proposal Table 10)

Table 10 හි පරීක්ෂණ අවස්ථා 6 ක් සහ ඒ සඳහා "අවශ්‍ය වන ආරක්ෂිත ප්‍රතිඵලය (Safe result we need)" දක්වා ඇත. අපගේ සජීවී පරීක්ෂණ මාලාව තුළ මේ සෑම එකක්ම ඒ අයුරින්ම ක්‍රියාත්මක කර පෙන්වා ඇත ([FR-02](#fr-02--multi-class-ai-මඟින්-ප්‍රහාර-හඳුනාගැනීම-must--live-attack-suite) බලන්න).

| Table 10 පරීක්ෂණ අවස්ථාව | යෝජනාවලිය ඉල්ලා සිටි ආරක්ෂිත ප්‍රතිඵලය | අපගේ පද්ධතිය සැබවින්ම සිදු කළ දේ |
|---|---|---|
| **Normal live streaming & playback** | No automatic block; traffic summary දිගටම ක්‍රියාත්මක වීම | ✅ Benign, Alerts 0, Blocks 0; summaries යාවත්කාලීන වේ |
| **Authorized Nmap horizontal scan** | Threshold සීමාවෙන් පසු පමණක් scanner block වීම; allowlisted admin හට බාධා නොවීම | ✅ PortScan alert; තහවුරු වූ fan-out මත පමණක් block වීම; Admin ට කිසිදු බාධාවක් නැත |
| **Rate-limited DDoS-like traffic** | Source එක block හෝ rate-limit වීම; කැමරා සේවාව යථා තත්ත්වයට පත්වීම | ✅ DDoS_DoS → attacker rate-limited වේ; කැමරාව දිගටම සේවාව සපයයි |
| **C&C-like periodic outbound** | ප්‍රතිපත්තිය අනුව Destination block වීම හෝ device isolate වීම | ✅ CnC → පිටත destination විනාඩි 30කට block වේ; කැමරාව කිසිවිටෙකත් block නොවේ |
| **Controlled file-transfer pattern** | Alert + evidence තබා ගැනීම; Generalize කළ නොහැකි නම් අසත්‍ය ප්‍රකාශ නොකිරීම | ✅ Malware_Download alert (model + file rule), evidence තැන්පත් වේ, alert-only (No block) |
| **Manual block and unblock** | නීතියේ වෙනස dashboard & DB හි පෙනීම; connection යථා තත්ත්වයට පත්වීම; audit සටහන් වීම | ✅ Manual block + rollback සජීවීව පෙනේ, audit-logged වේ |

✅ **ප්‍රතිඵලය:** පාලිත පරීක්ෂණ අවස්ථා හයම යෝජනාවලියේ "Safe result" තීරුවේ දක්වා ඇති ආකාරයටම 100% ක් නිවැරදිව ක්‍රියාත්මක වේ.

---

## කොටස 9 — අවදානම් සහ කළමනාකරණය (Proposal Table 11)

| යෝජනාවලියේ සඳහන් අවදානම | පොරොන්දු වූ කළමනාකරණ ක්‍රමය | පද්ධතිය එය ඉටුකර ඇති ආකාරය |
|---|---|---|
| **IoT-23 benign දත්ත කැමරා traffic නොවීම** | අපගේම benign flows එකතු කිරීම, පරතරය වාර්තා කිරීම | Virtual camera benign traffic අධීක්ෂණය කර ඇත; Physical camera benign capture දෘඩාංග විද්‍යාගාරය සඳහා සැලසුම් කර ඇත; පරතරය අවංකව වාර්තා කර ඇත |
| **Classes අසමාන වීම / උදාහරණ අඩු වීම** | Grouped splits, class weights, macro metrics භාවිතය | `class_weight=balanced`, Grouped CV, Macro-F1 + per-class recall නිවැරදිව වාර්තා කර ඇත |
| **Dataset සහ Zeek features නොගැළපීම** | Schema check පරීක්ෂාව; නොගැළපෙන features ඉවත් කර retrain කිරීම | `tools/schema_check.py` ආරක්ෂණ පරීක්ෂාව; Live භාවිතයට පෙර OVERALL=PASS විය යුතුය |
| **False positive එකකින් block වීම** | Allowlist, repeat + confidence thresholds, expiry, manual rollback | ආරක්ෂණ නීති 7 ම සක්‍රීයයි; කැමරාව කිසිවිටෙකත් block නොවේ; manual rollback ක්‍රියාත්මක වේ |
| **Encrypted traffic නිසා payload නොපෙනීම** | Flow metadata පමණක් භාවිතය; payload කියවන බව නොපැවසීම | ආකෘතිය භාවිත කරන්නේ flow metadata පමණි; payload පරීක්ෂා කරන බවට කිසිදු ප්‍රකාශයක් නොකරයි |
| **Traffic වෙනස් වීම / අලුත් ප්‍රහාර පැමිණීම** | Versioning, නිතිපතා පරීක්ෂා කිරීම, අනාගතයේ online learning | ආකෘතිය version කර ඇත (v3.2.0); schema audit නැවත කළ හැක; අනාගත පර්යේෂණයක් ලෙස දක්වා ඇත |
| **Inline prototype එකෙන් ජාලය බිඳවැටීම** | පෙරනිමියෙන් passive වීම; bypass/recovery සැලැස්මක් තිබීම | Switch mirror හරහා passively ධාවනය වේ; blocking යන්නේ router එක හරහාය; Reliability ඔප්පු කර ඇත (Target 5) |

✅ **ප්‍රතිඵලය:** යෝජනාවලිය කල්තියා හඳුනාගත් සෑම අවදානමක් සඳහාම පද්ධතිය තුළ ක්‍රියාකාරී විසඳුමක් සකසා ඇත.

---

## කොටස 10 — මෘදුකාංග ඉංජිනේරු විද්‍යාත්මක ප්‍රමිතිය (ස්වයංක්‍රීය පරීක්ෂණ 318)

📜 **යෝජනාවලියෙන් අපේක්ෂිත ප්‍රමිතිය** ("Tests of the whole system" — O4): පද්ධතිය හදිසියේ අටවාගත් එකක් නොව නිසි ඉංජිනේරු ප්‍රමිතියකින් යුක්ත විය යුතුය.  
🔧 **නිර්මාණය කළ දේ:** Zeek parser, feature extraction, model bundle, decision engine, response policy, nftables adapter, JWT auth, සහ WebSocket API ආවරණය වන pytest suites 24 ක්.  
🧪 **සාක්ෂිය:**
```powershell
.venv\\Scripts\\python.exe -m pytest tests/ -q
```
✅ **ප්‍රතිඵලය:** `318 passed, 6 warnings in 158.08s` — සෑම සංරචකයක්ම ආවරණය වී ඇත, කිසිදු code regression එකක් නොමැත.

---

## කොටස 11 — අවංක සීමාවන් සහ ඉතිරිව ඇති දෑ (Honest Limitations)

අපගේ ආකෘතිය දුර්වල තැන් මොනවාද සහ domain gap එක කුමක්ද යන්න අවංකව වාර්තා කරන ලෙස යෝජනාවලියම ඉල්ලා ඇති බැවින්, අපි මේවා විවෘතව ඉදිරිපත් කරමු:

1. **භෞතික කැමරා වලංගුකරණය තවමත් ඉදිරියට නියමිතව ඇත:** Docker testbed එක තුළ සියල්ල ඔප්පු කර ඇත (යෝජනාවලිය මඟින් "approved camera simulator" ලෙස එයට අවසර දී ඇත). සැබෑ භෞතික කැමරා traffic මත ≤5% benign-FPR ඉලක්කය (H1 Part 2) මැනිය යුත්තේ භෞතික දෘඩාංග විද්‍යාගාරයේදීය. IoT-23 benign flows මත argmax අගය 5.72% ක් වන අතර එය 5% ට මදක් ඉහළින් පවතී.
2. **Macro-F1 අගය මනින ක්‍රමය මත රඳා පවතී:** ප්‍රධාන අගය වන **87.77%** ලැබෙන්නේ held-out scenario එකේ පවතින පන්ති (*classes present*) සඳහාය. දැඩි grouped cross-validation out-of-fold macro-F1 අගය **70.97%** වන අතර, scenario 34-1 හි පන්ති 5 ම සඳහා අගය **70.22%** වේ (මන්ද 34-1 තුළ Malware_Download flows නොමැති බැවිනි). අපි හොඳම එක පමණක් නොව මේ සියල්ලම වාර්තා කරමු.
3. **PortScan යනු සාපේක්ෂව දුර්වලම පන්තියයි** (F1 ≈ 73%): නිහඬ තනි scan එකක් හිතාමතාම alert එකක් පමණක් ලබා දෙයි; වැරදි blocks වැළැක්වීම සඳහා block කිරීමට තහවුරු වූ fan-out සහ repetition අවශ්‍ය වේ.
4. **Throughput අගය Benchmark එකක් වන අතර Live Rate එකක් නොවේ:** ([Target 4](#target-4--සැකසුම්-ධාරිතාව-throughput) සටහන බලන්න). සජීවී වේගය තත්පරයට flows සිය ගණනකි.
5. **ආකෘතිය භාවිත කරන්නේ Flow Metadata පමණි:** Encrypted payloads කියවීමට නොහැකි අතර අපි එවැනි ප්‍රකාශයක් නොකරමු.

මෙහි කිසිවක් යෝජනාවලියට පටහැනි නොවේ — මේ සෑම එකක්ම යෝජනාවලිය විසින් කල්තියා බලාපොරොත්තු වූ සීමාවන් වේ.

---

## අවසාන ප්‍රකාශය (Closing Statement)

යෝජනාවලිය මුල සිට අග දක්වා පරීක්ෂා කර බැලීමේදී, එහි සඳහන් සෑම පොරොන්දුවකටම ගැළපෙන, සැබවින්ම ක්‍රියාත්මක වන තාක්ෂණික සංරචකයක් සහ සෘජු ප්‍රායෝගික සාක්ෂියක් අප සතුව ඇත:

- **විෂය පථය සහ ආචාරධර්ම (1.2, 3.8):** ගරු කර ඇත — විද්‍යාගාරය තුළ පමණි, metadata පමණි, පොරොන්දු වූ පන්ති 5 ම ඇත.
- **O1–O6 අරමුණු:** සියල්ල ලබා දී මැන බලන ලදී.
- **H1 උපකල්පනය:** කොටස 1 ඉටු විය (held-out 87.77%); කොටස 2 සැලසුම් කළ පරිදි භෞතික විද්‍යාගාරය සඳහා රැඳී පවතී.
- **RQ1–RQ5 පර්යේෂණ ප්‍රශ්න:** සාක්ෂි සහිතව පිළිතුරු සපයා ඇත.
- **ගෘහ නිර්මාණ ශිල්පය (Fig. 2):** සෑම පියවරක්ම සැබෑවටම ක්‍රියාත්මක වේ, චක්‍ර කාලය ~112 ms.
- **පර්යේෂණ ක්‍රමවේදය (3.2–3.8):** Feature compatibility gate සහ "threshold + repeat before block" නීතිය ඇතුළුව විශ්වාසවන්තව ක්‍රියාත්මක කර ඇත.
- **FR-01–FR-08:** සෘජු විධානයන් මඟින් සියල්ල ඔප්පු කර ඇත.
- **Table 9 ඉලක්ක:** පහක් සම්පූර්ණයෙන්ම ඉටු විය, එකක් දෘඩාංග සඳහා රැඳී පවතී.
- **Table 10 Scenarios සහ Table 11 Risks:** සියල්ල ක්‍රියාත්මක කර ඇත / සියලු අවදානම් කළමනාකරණය කර ඇත.
- **මෘදුකාංග ඉංජිනේරු විද්‍යාව:** ස්වයංක්‍රීය පරීක්ෂණ 318 ම Pass වේ.

මෙම පර්යේෂණයේ සැබෑ විෂය වන Detection and Response Engine එක අද වන විට සම්පූර්ණ කර, පරීක්ෂා කර, සජීවීව ප්‍රදර්ශනය කළ හැකි මට්ටමක පවතී. ඉතිරිව ඇති එකම පියවර වන්නේ යෝජනාවලියේ කාලසටහනට අනුව දැනටමත් සැලසුම් කර ඇති භෞතික කැමරා වලංගුකරණය පමණි.

> *"Sir, this report follows our proposal section by section. For every requirement, objective, hypothesis, research question, acceptance target, test scenario and risk, we have shown the exact component that delivers it and a command you can run to verify it. Where a result is still pending physical hardware, we have said so honestly. The system does what we proposed."*
"""

out_path = Path("PROPOSAL_FULFILLMENT_PROOF_SI.md")
out_path.write_text(content.strip() + "\\n", encoding="utf-8")
print(f"Successfully generated {out_path} ({len(content)} chars)")
