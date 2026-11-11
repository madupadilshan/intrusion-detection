#!/usr/bin/env python3
"""
lab_virtual/lab.py - Control the virtual lab (Docker) and run the proposal's Table 10 scenarios.

This runs the REAL project: real packets between lab machines, real Zeek, the real IDS backend
(core_engine.app: Zeek adapter -> model -> decision engine -> response policy -> router
firewall over SSH -> MongoDB -> dashboard), and the real nftables table on the lab router.
Only the machines are containers instead of physical devices.

Commands (run from the project folder with the project's Python):
  python lab_virtual/lab.py setup        make the lab SSH keys (once)
  python lab_virtual/lab.py up           build and start the lab machines
  python lab_virtual/lab.py ids-start    start the IDS backend + pipeline on the lab (port 5000)
  python lab_virtual/lab.py status       machines, router blocks, Zeek log, IDS pipeline
  python lab_virtual/lab.py scenario N   run Table 10 scenario N (1-6) and write a report
  python lab_virtual/lab.py reset        remove all blocks (dashboard, database and router)
  python lab_virtual/lab.py ids-stop     stop the IDS backend
  python lab_virtual/lab.py down         stop and remove the lab machines

The dashboard login is written to lab_virtual/keys/dashboard_login.txt (not in Git).
Reports go to reports/lab_tests/virtual/.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from tools.lab_common import ip_in_sets, nft_sets, scenario_report  # noqa: E402

KEYS = HERE / "keys"
LOGS = HERE / "zeek_logs"
COMPOSE = ["docker", "compose", "-f", str(HERE / "docker-compose.yml")]
SETTINGS = HERE / "settings.lab.yaml"
DB_NAME = "iot_ids_lab"
API = "http://127.0.0.1:5000"
PID_FILE = HERE / "keys" / "ids_backend.pid"
BACKEND_LOG = HERE / "ids_backend.log"
LOGIN_FILE = KEYS / "dashboard_login.txt"
REPORTS = ROOT / "reports" / "lab_tests" / "virtual"
_venv_py = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PY = str(_venv_py) if _venv_py.exists() else sys.executable

CAMERA, ATTACKER, CLOUD = "192.168.50.30", "10.10.10.50", "10.10.10.123"
ADMIN, NVR = "192.168.50.10", "192.168.50.20"


def run(cmd, check=True, capture=False, timeout=None):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=capture, text=True, timeout=timeout)
    if check and r.returncode != 0:
        sys.exit(f"Command failed ({r.returncode}): {' '.join(map(str, cmd))}\n{r.stdout or ''}{r.stderr or ''}")
    return r


def router_ssh(command: str, check=True) -> str:
    cmd = ["ssh", "-p", "2222", "-i", str(KEYS / "router_admin"), "-o", "IdentitiesOnly=yes",
           "-o", "BatchMode=yes", "-o", f'UserKnownHostsFile="{KEYS / "known_hosts"}"',
           "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=5", "root@127.0.0.1", command]
    r = run(cmd, check=check, capture=True, timeout=20)
    return (r.stdout or "") + (r.stderr or "" if r.returncode else "")


# ------------------------------------------------------------------ setup / up / down
def cmd_setup(_):
    KEYS.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    keygen = shutil.which("ssh-keygen")
    if not keygen:
        sys.exit("ssh-keygen not found (install the Windows OpenSSH client or Git for Windows).")
    for name, comment in (("router_admin", "ids-lab-sensor"), ("router_host_ed25519", "ids-lab-router-host")):
        if not (KEYS / name).exists():
            run([keygen, "-q", "-t", "ed25519", "-N", "", "-C", comment, "-f", str(KEYS / name)])
            print(f"made key {KEYS / name}")
    if os.name == "nt":  # Windows OpenSSH refuses private keys that other users may read
        for name in ("router_admin", "router_host_ed25519"):
            run(["icacls", str(KEYS / name), "/inheritance:r", "/grant:r", f"{os.environ.get('USERNAME')}:F"],
                check=False, capture=True)
    host_pub = (KEYS / "router_host_ed25519.pub").read_text().split()
    (KEYS / "known_hosts").write_text(f"[127.0.0.1]:2222 {host_pub[0]} {host_pub[1]}\n")
    print("lab keys ready in", KEYS, "(the lab's own known_hosts; ~/.ssh is not used)")


def cmd_up(_):
    if not (KEYS / "router_admin").exists():
        cmd_setup(None)
    run(COMPOSE + ["up", "-d", "--build"])
    print("waiting for the router's SSH ...")
    for _ in range(40):
        out = router_ssh("nft list table inet ids", check=False)
        if "table inet ids" in out:
            print("router reachable over SSH; nftables table 'ids' is loaded")
            break
        time.sleep(2)
    else:
        sys.exit("router SSH not reachable; see: docker logs ids-lab-router")
    cmd_status(None)


def cmd_down(_):
    run(COMPOSE + ["down"], check=False)


# ------------------------------------------------------------------ IDS backend
def api(method, path, token=None, body=None, timeout=10):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def login():
    if not LOGIN_FILE.exists():
        sys.exit("No lab login yet; run: python lab_virtual/lab.py ids-start")
    user, pw = LOGIN_FILE.read_text().split()[:2]
    code, data = api("POST", "/api/auth/login", body={"username": user, "password": pw})
    tok = data.get("token") or data.get("access_token")
    if code != 200 or not tok:
        sys.exit(f"Login failed ({code}): {data}")
    return tok


def cmd_ids_start(_):
    try:
        code, _ = api("GET", "/api/health", timeout=2)
        sys.exit("Something already answers on port 5000; stop it first (ids-stop, or the demo backend).")
    except (urllib.error.URLError, ConnectionError, OSError):
        pass
    if not LOGIN_FILE.exists():
        pw = secrets.token_urlsafe(12)
        run([PY, "tools/create_admin.py", "--db-name", DB_NAME, "-u", "labadmin", "-p", pw, "--force"], capture=True)
        LOGIN_FILE.write_text(f"labadmin {pw}\n")
    env = dict(os.environ, IDS_SETTINGS_FILE=str(SETTINGS), DB_NAME=DB_NAME, PORT="5000", HOST="127.0.0.1")
    log = open(BACKEND_LOG, "a", encoding="utf-8")
    flags = (subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008) if os.name == "nt" else 0
    p = subprocess.Popen([PY, "-m", "core_engine.app"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                         creationflags=flags)
    PID_FILE.write_text(str(p.pid))
    for _ in range(60):
        try:
            code, h = api("GET", "/api/health", timeout=2)
            if code == 200:
                break
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(1)
    else:
        sys.exit(f"IDS backend did not start; see {BACKEND_LOG}")
    tok = login()
    code, st = api("POST", "/api/v1/pipeline/start", tok)
    print(f"IDS backend running (pid {p.pid}), database {DB_NAME}; pipeline start: {code} {st.get('status', st)}")
    print(f"Dashboard: http://localhost:5000 (served by the backend)  login in {LOGIN_FILE}")


def cmd_ids_stop(_):
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        if os.name == "nt":
            run(["taskkill", "/PID", pid, "/T", "/F"], check=False, capture=True)
        else:
            run(["kill", pid], check=False)
        PID_FILE.unlink()
        print("IDS backend stopped")


# ------------------------------------------------------------------ status / reset
def router_blocks() -> dict:
    return nft_sets(router_ssh("nft -j list table inet ids", check=False))


def conn_lines() -> int:
    f = LOGS / "conn.log"
    return sum(1 for _ in f.open(encoding="utf-8", errors="replace")) if f.exists() else 0


def cmd_status(_):
    r = run(COMPOSE + ["ps", "--format", "{{.Name}}\t{{.State}}"], check=False, capture=True)
    print("Lab machines:\n  " + (r.stdout.strip().replace("\n", "\n  ") or "(none)"))
    print("Router blocks (real nftables sets):", router_blocks())
    print(f"Zeek conn.log lines: {conn_lines():,}; files.log present: {(LOGS / 'files.log').exists()}")
    try:
        tok = login()
        code, st = api("GET", "/api/v1/pipeline/status", tok)
        print("IDS pipeline:", st.get("status"), st.get("metrics"), "file check:", st.get("file_check"))
    except SystemExit as e:
        print("IDS backend:", e)
    except (urllib.error.URLError, OSError):
        print("IDS backend: not running")


def cmd_reset(_):
    try:
        tok = login()
        code, bl = api("GET", "/api/blocklist", tok)
        for b in bl.get("blocks", []):
            api("DELETE", f"/api/blocklist/{b['ip']}", tok, body={"reason": "virtual lab reset"})
        print(f"removed {len(bl.get('blocks', []))} block(s) through the IDS")
    except (SystemExit, urllib.error.URLError, OSError):
        print("IDS backend not reachable; only the router sets are cleared")
    router_ssh("nft flush set inet ids block_src; nft flush set inet ids block_dst; nft flush set inet ids limit_src",
               check=False)
    print("router sets now:", router_blocks())


# ------------------------------------------------------------------ scenarios (Table 10)
def dexec(container, *args, detach=False, check=True, timeout=None):
    cmd = ["docker", "exec"] + (["-d"] if detach else []) + [container] + list(args)
    return run(cmd, check=check, capture=True, timeout=timeout)


def reach(src_container, host, port) -> bool:
    """Can src open a TCP connection to host:port? (shows whether a block works)"""
    r = dexec(src_container, "python", "-c",
              f"import socket;socket.create_connection(('{host}',{port}),timeout=3);print('open')",
              check=False, timeout=15)
    return "open" in (r.stdout or "")


SCENARIOS = {
    1: ("Normal live streaming and playback",
        "camera, NVR and admin PC run their normal traffic; nothing extra is started",
        "most flows benign; no high-confidence attack event", "no automatic block"),
    2: ("Authorised Nmap horizontal scan",
        "attack laptop: nmap -p 23,80,554 192.168.50.0/24",
        "port-scan class or a scan alert",
        "the scanner blocked only after the threshold; the allowlisted admin can still get in; camera never blocked"),
    3: ("Rate-limited DDoS-like traffic",
        "attack laptop: SYN flood to the camera port 80, 1000 packets/s for 20 s (tests/lab_scenarios/syn_flood.py)",
        "DDoS/DoS prediction; more events than usual",
        "the source rate-limited (D-055) or blocked; the camera service comes back"),
    4: ("C&C-like periodic outbound simulation",
        "lab C&C server on the attack laptop (port 6667 closed for the first 120 s); camera simulator "
        "connects every 5 s and keeps short chat sessions",
        "C&C evidence from the camera to the outside", "the C&C destination blocked; the camera never blocked"),
    5: ("Controlled file-transfer pattern",
        "camera simulator downloads a harmless test program (copy of `true`) from the attack laptop 5 times",
        "file-type rule alert (RULE_EXECUTABLE_DOWNLOAD) and/or a model Malware_Download alert",
        "alert and evidence only; no block"),
    6: ("Manual block and unblock",
        "admin blocks the attack laptop from the dashboard API, then unblocks it",
        "the rule appears and disappears in the dashboard, the database and the router",
        "the connection comes back after unblock"),
}


def run_scenario(n: int, wait: float) -> dict:
    notes, checks = [], []
    if n == 1:
        notes.append(f"waited {wait:.0f} s with normal traffic only")
        time.sleep(wait)
    elif n == 2:
        r = dexec("ids-lab-attacker", "nmap", "-p", "23,80,554", "192.168.50.0/24", timeout=600)
        notes.append("nmap output:\n" + "\n".join(l for l in r.stdout.splitlines() if l.strip())[-1500:])
        time.sleep(wait)
        checks.append(("Admin PC can still open the camera page (admin -> camera:80)",
                       "yes" if reach("ids-lab-admin", CAMERA, 80) else "NO"))
    elif n == 3:
        before = reach("ids-lab-nvr", CAMERA, 554)
        r = dexec("ids-lab-attack-server", "python", "-u", "/lab/syn_flood.py", CAMERA, "--port", "80",
                  "--rate", "1000", "--seconds", "20", timeout=120)
        notes.append(r.stdout.strip())
        time.sleep(wait)
        after = reach("ids-lab-nvr", CAMERA, 554) and reach("ids-lab-admin", CAMERA, 80)
        checks.append(("Camera service (NVR -> camera:554, admin -> camera:80) before / after the flood",
                       f"{'up' if before else 'DOWN'} / {'up (comes back)' if after else 'DOWN'}"))
    elif n == 4:
        # Stop a C&C server or bot left from an earlier run first. Otherwise port 6667 is already
        # open, the camera never fails before its conversations, and the run is not the scenario
        # written in the guide (found 11 Nov 2026: a second run gave no block).
        dexec("ids-lab-attack-server", "pkill", "-f", "lab_server.py --role cnc", check=False)
        dexec("ids-lab-camera", "pkill", "-f", "camera_sim.py bot", check=False)
        time.sleep(2)
        if reach("ids-lab-camera", ATTACKER, 6667):
            notes.append("WARNING: port 6667 was still open before the run; the result is not valid")
        dexec("ids-lab-attack-server", "python", "-u", "/lab/lab_server.py", "--role", "cnc",
              "--cnc-open-after", "120", detach=True)
        dexec("ids-lab-camera", "python", "-u", "/lab/camera_sim.py", "bot", "--server", ATTACKER,
              "--every", "5", "--session", "30", "--duration", str(int(wait)), detach=True)
        notes.append(f"C&C server opens after 120 s; bot runs {wait:.0f} s")
        time.sleep(wait + 20)
        dexec("ids-lab-attack-server", "pkill", "-f", "lab_server.py --role cnc", check=False)  # clean up
    elif n == 5:
        r = dexec("ids-lab-camera", "python", "-u", "/lab/camera_sim.py", "download", "--url",
                  f"http://{ATTACKER}/bins/lab_test.x86", "--count", "5", "--every", "20", timeout=300)
        notes.append(r.stdout.strip())
        time.sleep(wait)
    elif n == 6:
        tok = login()
        before = reach("ids-lab-attack-server", CAMERA, 80)
        code, res = api("POST", "/api/blocklist", tok, body={"ip": ATTACKER, "direction": "source",
                                                             "duration_minutes": 10, "reason": "Table 10 row 6 test"})
        time.sleep(3)
        blocked_router = router_blocks()
        during = reach("ids-lab-attack-server", CAMERA, 80)
        code2, res2 = api("DELETE", f"/api/blocklist/{ATTACKER}", tok, body={"reason": "Table 10 row 6 test done"})
        time.sleep(3)
        after = reach("ids-lab-attack-server", CAMERA, 80)
        notes.append(f"router sets during the block: {blocked_router}")
        checks += [("Manual block / unblock API answers", f"{code} / {code2}"),
                   ("Attack laptop -> camera:80 before / during / after the block",
                    f"{'open' if before else 'blocked'} / {'open' if during else 'blocked'} / "
                    f"{'open' if after else 'blocked'}")]
    return {"notes": notes, "checks": checks}


def cmd_scenario(args):
    n = args.n
    title, how, expect, safe = SCENARIOS[n]
    tok = login()
    start = datetime.utcnow()
    lines0 = conn_lines()
    print(f"Scenario {n}: {title}\n  how: {how}\n  expected: {expect}; safe result: {safe}")
    res = run_scenario(n, args.wait)
    time.sleep(5)
    end = datetime.utcnow()
    code, ev = api("GET", "/api/events?limit=500", tok)
    events = [e for e in ev.get("events", []) if str(e.get("created_at", "")) >= start.isoformat()[:19]]
    code, bl = api("GET", "/api/blocklist", tok)
    blocks = bl.get("blocks", [])
    rblocks = router_blocks()
    checks = res["checks"]
    if n == 1:
        auto = [b for b in blocks if str(b.get("actor", "")).startswith("autonomous")]
        checks.append(("Automatic blocks during the run", str(len(auto))))
    elif n == 2:
        top = max((float(e.get("confidence") or 0) for e in events if e.get("predicted_class") == "PortScan"), default=0)
        checks += [("Highest PortScan confidence", f"{top:.2f}"),
                   (f"Scanner {ATTACKER} blocked", ", ".join(ip_in_sets(ATTACKER, rblocks)) or "no")]
    elif n == 3:
        checks.append((f"Source {ATTACKER} rate-limited (limit_src) or blocked (block_src)",
                       ", ".join(ip_in_sets(ATTACKER, rblocks)) or "NO"))
    elif n == 4:
        checks.append((f"C&C destination {ATTACKER} blocked (block_dst)",
                       "yes" if ip_in_sets(ATTACKER, rblocks, ["block_dst"]) else "NO"))
    elif n == 5:
        checks.append(("File-type rule alerts (RULE_EXECUTABLE_DOWNLOAD)",
                       str(sum(1 for e in events if e.get("reason_code") == "RULE_EXECUTABLE_DOWNLOAD"))))
    code, summ = api("GET", "/api/summary", tok)
    path = REPORTS / f"scenario_{n}_{start.strftime('%Y%m%d_%H%M%S')}.md"
    text = scenario_report(
        path=path, title=f"Virtual lab - Table 10 scenario {n}: {title}",
        where="virtual lab (Docker, `lab_virtual/`): real packets, real Zeek, the real IDS backend and pipeline, "
              "real nftables on the lab router. The devices are containers, not physical devices.",
        start=start, end=end, how=how, expect=expect, safe=safe,
        model=(summ.get("system") or {}).get("model_version", "unknown"), flows=conn_lines() - lines0,
        events=events, blocks=blocks, fw_sets=rblocks,
        protected={CAMERA: "camera", ADMIN: "admin PC", NVR: "NVR"}, checks=checks, notes=res["notes"])
    print(text.split("## What the system did", 1)[-1])
    print(f"\nreport: {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("setup", "up", "down", "status", "reset", "ids-start", "ids-stop"):
        sub.add_parser(name)
    sc = sub.add_parser("scenario")
    sc.add_argument("n", type=int, choices=sorted(SCENARIOS))
    sc.add_argument("--wait", type=float, default=90.0, help="seconds to wait for Zeek to write the flows")
    args = ap.parse_args()
    {"setup": cmd_setup, "up": cmd_up, "down": cmd_down, "status": cmd_status, "reset": cmd_reset,
     "ids-start": cmd_ids_start, "ids-stop": cmd_ids_stop, "scenario": cmd_scenario}[args.cmd](args)


if __name__ == "__main__":
    main()
