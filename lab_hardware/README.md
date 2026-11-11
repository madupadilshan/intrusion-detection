# Hardware lab: test the project with a real IP camera (decision D-054)

This folder has everything needed to run the proposal's tests with real devices: guide Steps 3b, 5, 19, 20, 22 and 35–39.
The virtual lab (`lab_virtual/`) already ran the same tests in Docker. The hardware lab gives the results that count.

**Rules (proposal 3.8, guide Part E):**
- Only use the separated lab network.
- Write a logbook line (`docs/lab_logbook.md`) **before** every test.
- Never put test software on the real camera. Keep no video or audio as research data.
- Scans and floods only target `192.168.50.0/24`. The scripts refuse other targets.

---

## 1. What you need (proposal 5.1)

| Item | Lab address | Notes |
| --- | --- | --- |
| IP camera | 192.168.50.30 | Set a fixed IP address and gateway 192.168.50.1. If it needs the internet or an app for its first setup, do that **before** it joins the lab. |
| NVR or a recording PC | 192.168.50.20 | Recording software, or `ffmpeg` (see section 6). |
| Managed switch with port mirroring | — | "Port mirroring" or "SPAN" must be in its feature list. |
| Linux sensor with **two** network ports | 192.168.50.5 (port 1) + mirror port with no IP (port 2) | Ubuntu 22.04 LTS. A USB Ethernet adapter is fine for port 2. |
| Lab router you control | 192.168.50.1 (LAN) and 10.10.10.1 (outside) | OpenWrt (22.03 or newer) or a Linux PC with two ports. SSH as root with a key. |
| Attack test computer | 10.10.10.50 | Linux with `nmap`, `python3`, `hping3` (optional), and a copy of `tests/lab_scenarios/`. |
| Camera-side lab computer ("infected camera" stand-in) | 192.168.50.31 | A Raspberry Pi or a laptop with `python3` and `tests/lab_scenarios/`. Used **only** in scenarios 4 and 5. |
| Admin workstation | 192.168.50.10 | Any PC with a browser (your Windows PC). Opens the dashboard at `http://192.168.50.5:5000`. |

## 2. Wiring (passive mode, proposal Figure 5 left)

```
 attack computer 10.10.10.50 ── router "outside" port 10.10.10.1
                                router LAN port 192.168.50.1 ── switch ── camera 192.168.50.30
                                                                       ├─ NVR 192.168.50.20
                                                                       ├─ admin PC 192.168.50.10
                                                                       ├─ camera-side lab computer 192.168.50.31
                                                                       ├─ sensor port 1 192.168.50.5 (management)
                                                                       └─ sensor port 2 = MIRROR port (no IP)
```

- The attack computer must be **behind the router**. Only then can the router block it (guide Step 5).
- **Switch:** mirror the **incoming** traffic of every used port to the sensor's port 2. Each packet is then copied once.
- Write the switch settings, with screenshots, in `docs/lab_network.md`.
- No lab device may reach the university or the public internet. The router must have **no** internet port connected during tests.

## 3. Set up the lab router

### OpenWrt (22.03 or newer; nftables is built in)

Find the port names first: `ip link` (often `lan1..lan4` and `wan`). Then:

```sh
# LAN = camera network
uci set network.lan.ipaddr='192.168.50.1'
uci set network.lan.netmask='255.255.255.0'
# the "outside" lab network on the former WAN port (removes the internet uplink)
uci -q delete network.wan; uci -q delete network.wan6
uci set network.outside=interface
uci set network.outside.device='wan'
uci set network.outside.proto='static'
uci set network.outside.ipaddr='10.10.10.1'
uci set network.outside.netmask='255.255.255.0'
# firewall zone without NAT, forwarding both ways
uci add firewall zone
uci set firewall.@zone[-1].name='outside'
uci set firewall.@zone[-1].network='outside'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='ACCEPT'
uci set firewall.@zone[-1].masq='0'
uci add firewall forwarding; uci set firewall.@forwarding[-1].src='lan'; uci set firewall.@forwarding[-1].dest='outside'
uci add firewall forwarding; uci set firewall.@forwarding[-1].src='outside'; uci set firewall.@forwarding[-1].dest='lan'
uci commit; /etc/init.d/network restart; /etc/init.d/firewall restart
```

SSH: put the sensor's public key (from `hwlab.py setup`) in `/etc/dropbear/authorized_keys`.

### A Linux PC as the router (Ubuntu, two ports)

- Give port 1 `192.168.50.1/24` and port 2 `10.10.10.1/24` (netplan).
- Turn routing on: `echo net.ipv4.ip_forward=1 | sudo tee /etc/sysctl.d/90-lab.conf && sudo sysctl --system`.
- Do **not** add NAT.
- Install the tools: `sudo apt install nftables openssh-server`.
- Put the sensor's key in `/root/.ssh/authorized_keys`, and set `PermitRootLogin prohibit-password` in `/etc/ssh/sshd_config`.
- To load the rules at boot: `echo 'include "/etc/ids_router.nft"' | sudo tee -a /etc/nftables.conf && sudo systemctl enable nftables`.

### Both kinds of router

`hwlab.py router-install` (section 5) copies `sensor/ids_router.nft` to `/etc/ids_router.nft` and loads it. It puts the allowlist from `settings.hardware.yaml` into the file.

On OpenWrt, also add `nft -f /etc/ids_router.nft` to `/etc/rc.local`, so the rules come back after a restart. After any firewall restart, `hwlab.py check` shows whether the `ids` table is still loaded.

## 4. Install the sensor (guide Step 3b)

The sensor needs the internet for this step only.

1. **On the PC:** build the dashboard (`cd my-app && npm run build`), then run `.venv\Scripts\python.exe lab_hardware\pack_for_sensor.py`. This makes `dist/sensor_files.zip`, with the model, the training features and the dashboard. Git does not hold these files.
2. **On the sensor:** `git clone https://github.com/madupadilshan/intrusion-detection.git && cd intrusion-detection`, and copy `sensor_files.zip` into this folder.
3. Run `bash lab_hardware/install_sensor.sh`. It installs Zeek 8.0 (in `/opt/zeek`), MongoDB 8.0, `nmap`, `nftables`, `tcpdump`, `tshark` and the Python packages. It also unpacks and checks the zip, and runs `tools/check_env.py`.
4. Disconnect the sensor from the internet. Connect it to the lab as in section 2.
5. Edit `lab_hardware/settings.hardware.yaml`. Every line marked `CHANGE` must match your lab: the mirror port name (see `ip link`), the camera IP and ports, and the router IP.
6. Optional: `sudo bash lab_hardware/install_services.sh`. This starts Zeek and the backend at boot.

## 5. First start

```bash
.venv/bin/python lab_hardware/hwlab.py setup            # router SSH key + dashboard login (lab_hardware/keys/, not in Git)
#   -> put the printed public key on the router (section 3)
.venv/bin/python lab_hardware/hwlab.py trust-router     # compare the fingerprint with the router's own, then type yes
.venv/bin/python lab_hardware/hwlab.py router-install   # load the ids nftables table on the router
.venv/bin/python lab_hardware/hwlab.py zeek-start       # Zeek on the mirror port (sudo)
.venv/bin/python lab_hardware/hwlab.py ids-start --auto-response off
.venv/bin/python lab_hardware/hwlab.py check            # all checks should PASS; report in reports/lab_tests/hardware/
```

Open `http://192.168.50.5:5000` on the admin PC. The login is in `lab_hardware/keys/dashboard_login.txt`.

## 6. Order of the tests (guide)

| # | Guide step | Command | What it gives |
| --- | --- | --- | --- |
| 1 | Step 19 + 22 | Use the camera normally for 10 minutes. Then: `.venv/bin/python tools/schema_check.py --live-path /var/log/ids-zeek/conn.log --source real` | `reports/schema_check.md`. It answers **RQ3**. If a feature fails, drop it and retrain (proposal 3.5). Write the drop in the decision log. |
| 2 | Step 20 | Normal use only, for **several hours on different days**, with `ids-start --auto-response on` (this also counts wrong blocks). Then copy `conn.log` to `data/local/benign/<date>/conn.log` and run `.venv/bin/python sensor/collect_camera_traffic.py --conn-log data/local/benign/<date>/conn.log --source real` | The false-alarm rate on real camera traffic: **H1 part 2**, target ≤ 5% |
| 3 | Step 35 | `hwlab.py reset`, then `hwlab.py scenario N --run R` for N = 1..6, about 5 runs each | `reports/lab_tests/hardware/scenario_N_runR_*.md` |
| 4 | Step 36 | `.venv/bin/python tools/fr_tests.py --where hardware --login-file lab_hardware/keys/dashboard_login.txt --conn-log /var/log/ids-zeek/conn.log` | `reports/fr_tests.md` (FR-01 to FR-08) |
| 5 | Step 37 | `.venv/bin/python tools/measure_latency.py --label normal --seconds 600`, and again with `--label attack` during scenarios 2 and 3 | `reports/performance/` (median and 95th percentile; target < 2 s and < 5 s) |
| 6 | Step 38 | `hwlab.py reliability restart`; `hwlab.py reliability expiry`; restart the sensor and run `hwlab.py check` | `reports/lab_tests/hardware/reliability_*.md` |
| 7 | Step 39 | Give `docs/usability_tasks.md` to 3–5 people | `reports/usability.md` |

How each scenario runs: `hwlab.py scenario N` prints the commands to run on the attack computer or the camera-side lab computer, and waits while you run them. Then it reads what the system did: alerts, the database blocklist, and the router's real nftables sets. It checks the proposal's "safe result", asks you a few yes/no questions (for example "did live view come back?"), and writes the report.

The `ffmpeg` recording for the NVR PC (only if you have no NVR). The video stays on the NVR and is **not** research data (proposal 3.8):
`ffmpeg -rtsp_transport tcp -i "rtsp://USER:PASS@192.168.50.30:554/<stream path>" -c copy -f segment -segment_time 300 rec_%03d.mp4`

## 7. What the system is expected to do (written before the tests)

Model v3.1.0 (WCD, D-054). The thresholds come from Step 17: `reports/experiments/operational_thresholds.json`.

| Scenario | Expected | Automatic action (if `--auto-response on`) |
| --- | --- | --- |
| 1 Normal use | Few or no alerts | None. A camera that keeps retrying an unreachable cloud server may look like C&C (issue 39). Record any alert and any block. |
| 2 Nmap scan | PortScan alerts | Block of the scanner only at confidence ≥ 0.88 with 3 repeats in 60 s. Otherwise alerts only (issue 46). |
| 3 SYN flood | DDoS alerts | **Rate-limit** of the source (D-055; must be confirmed with the supervisor first). The camera must come back. |
| 4 C&C-like traffic from 192.168.50.31 | CnC alerts | The C&C destination 10.10.10.50 is blocked (block threshold 0.30, 3 repeats). |
| 5 Program download on 192.168.50.31 | Alert `RULE_EXECUTABLE_DOWNLOAD` (files.log rule) | None (alert only) |
| 6 Manual block / unblock | The rule appears, then disappears | Done by the admin, not automatic |

## 8. Inline mode (proposal Figure 5 right; optional test)

`sudo bash lab_hardware/inline_bridge.sh up <port-to-switch> <port-to-router>` makes the sensor a bridge that blocks with `sensor/ids_inline.nft`. The script explains the settings to change. It also gives the **bypass plan**: if the sensor fails, plug the switch cable straight into the router.

The backend user also needs passwordless `sudo` for `nft` only. Add this with `visudo`: `<user> ALL=(root) NOPASSWD: /usr/sbin/nft`.

## 9. If something does not work

| Problem | Check |
| --- | --- |
| `conn.log` stays empty | `sudo tcpdump -i <mirror port> -c 20` shows packets? If not, check the switch mirror settings. |
| Router SSH fails | `hwlab.py trust-router` again. Is the key in `authorized_keys`? Run `ssh -v -p 22 root@192.168.50.1` to see the reason. |
| The dashboard does not load on the admin PC | Open `http://192.168.50.5:5000`. Does `settings.hardware.yaml` → `server.cors_origins` have this address? Check the sensor's firewall: `sudo ufw status`. |
| Blocks do not happen | Did you start with `ids-start --auto-response on`? The Overview page shows "Automatic response ON" and the firewall name. Simulated must say no. |
