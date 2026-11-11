# Virtual lab: run the real project on this PC (decision D-053)

This folder builds a small copy of the proposal's lab with Docker. It runs the **real** system:

- real network packets between lab machines,
- real Zeek,
- the real IDS backend (model, decision rules, safety checks),
- real firewall rules (nftables) on a real Linux router,
- the real database and dashboard.

Only the devices are containers, not physical devices.

It does **not** replace the hardware lab. A real camera, a real switch mirror port and real camera traffic (guide Steps 5, 19, 20) are still needed. Always report these results as "virtual lab".

## The lab

```
 outside network 10.10.10.0/24                 camera LAN 192.168.50.0/24
 attack laptop  10.10.10.50 (Nmap) --+     +-- camera simulator 192.168.50.30
 camera "cloud" 10.10.10.123 --------+-- router --+-- NVR              192.168.50.20
                                10.10.10.1  |  +-- admin PC          192.168.50.10
                                   192.168.50.1
 Zeek listens on the camera LAN (like the switch mirror port).
 The IDS on Windows reads Zeek's logs and blocks through the router (SSH, nftables).
```

| Machine | What it does |
|---|---|
| router | Routes between the two networks without NAT. Runs `sensor/ids_router.nft`. SSH for the IDS on 127.0.0.1:2222, with a key only. |
| sensor | Zeek with `sensor/local.zeek`. Writes `zeek_logs/conn.log` and `zeek_logs/files.log`. |
| camera | `tests/lab_scenarios/camera_sim.py normal`: a web page, a video stream, and status, time and name requests to its cloud. |
| nvr, admin | Record the video stream, and open the camera page now and then (normal traffic). |
| cloud | The camera's normal cloud (`lab_server.py --role cloud`). |
| attacker, attack-server | The attack laptop: Nmap, the SYN flood script, a harmless web server and the lab C&C server. |

## Use it (PowerShell, in the project folder)

```
.venv\Scripts\python.exe lab_virtual\lab.py setup       # once: make the lab SSH keys
.venv\Scripts\python.exe lab_virtual\lab.py up          # build and start the lab machines
.venv\Scripts\python.exe lab_virtual\lab.py ids-start   # start the IDS on the lab (port 5000)
.venv\Scripts\python.exe lab_virtual\lab.py status
```

Open the dashboard at http://localhost:5000. The backend serves the built dashboard; build it once with `cd my-app; npm run build`.

The login is in `lab_virtual\keys\dashboard_login.txt`.

To run the proposal's Table 10 tests:

```
.venv\Scripts\python.exe lab_virtual\lab.py scenario 1   # normal traffic only
.venv\Scripts\python.exe lab_virtual\lab.py scenario 2   # Nmap scan from the attack laptop
.venv\Scripts\python.exe lab_virtual\lab.py scenario 3   # SYN flood, 1000/s for 20 s
.venv\Scripts\python.exe lab_virtual\lab.py scenario 4   # C&C-like traffic from the camera
.venv\Scripts\python.exe lab_virtual\lab.py scenario 5   # camera downloads a harmless program
.venv\Scripts\python.exe lab_virtual\lab.py scenario 6   # manual block and unblock
.venv\Scripts\python.exe lab_virtual\lab.py reset        # remove all blocks before the next test
```

Each scenario writes a report to `reports/lab_tests/virtual/`. The report shows:
- what the system detected;
- what it blocked, both in the database and in the router's real firewall sets;
- whether the camera was blocked (it must never be).

To stop everything:

```
.venv\Scripts\python.exe lab_virtual\lab.py ids-stop
.venv\Scripts\python.exe lab_virtual\lab.py down
```

## Safety

- All traffic stays inside the Docker networks on this PC. Nothing is sent to other networks.
- The scan and flood scripts refuse any target outside 192.168.50.0/24.
- The test "program" is a copy of the `true` command, which does nothing.
- `auto_response` is on **only** in `settings.lab.yaml`. Your `config/settings.yaml` is not changed.
- The lab uses its own SSH keys and its own `known_hosts` in `keys/` (not in Git). Your `~/.ssh` folder is not used.
