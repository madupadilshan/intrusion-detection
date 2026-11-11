#!/usr/bin/env python3
"""
lab_hardware/hwlab.py - Run the project in the HARDWARE lab and record the proposal's tests.

Run it ON THE LINUX SENSOR, in the project folder, with the project's virtual environment:
    .venv/bin/python lab_hardware/hwlab.py <command>

Setup (once):
  setup                      make the lab SSH key for the router and the dashboard login
  trust-router               read the router's SSH host key, show its fingerprint, save it after you confirm
  router-install             copy sensor/ids_router.nft (with the settings allowlist) to the router and load it
  check                      pre-flight checks (guide Step 5 "Done when", Step 19), written to a report

Running:
  zeek-start / zeek-stop     Zeek on the mirror port (sensor/run_zeek.sh, needs sudo)
  ids-start [--auto-response on|off]   start the IDS backend and pipeline (default: off)
  ids-stop | status | reset  stop the backend | show state | remove all blocks (database and router)

Tests (proposal Table 10, guide Steps 35 and 38):
  scenario N [--run R] [--wait S]   guided run of Table 10 scenario N (1-6); writes a report
  reliability restart               restart the backend during traffic; check data and rules are kept
  reliability expiry                a 1-minute rule must expire and be removed

Reports go to reports/lab_tests/hardware/. Every test must have a line in docs/lab_logbook.md first.
The attack commands are run BY YOU on the attack computer (10.10.10.50) or on the camera-side lab
computer (192.168.50.31); this tool prints them, waits, and then reads what the system did.
No test software is ever put on the real camera (D-054).
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from tools.lab_common import Api, ip_in_sets, nft_sets, read_login, scenario_report, utc_now, events_since  # noqa: E402

KEYS = HERE / "keys"
RUN = HERE / "run"
SETTINGS = HERE / "settings.hardware.yaml"
RUNTIME_SETTINGS = HERE / "runtime_settings.yaml"
LOGIN_FILE = KEYS / "dashboard_login.txt"
PID_FILE = RUN / "ids_backend.pid"
BACKEND_LOG = RUN / "ids_backend.log"
REPORTS = ROOT / "reports" / "lab_tests" / "hardware"
PY = sys.executable
API = Api("http://127.0.0.1:5000")


def cfg() -> dict:
    return yaml.safe_load(SETTINGS.read_text(encoding="utf-8")) or {}


def lab(key, default=None):
    return (cfg().get("lab") or {}).get(key, default)


def fw(key, default=None):
    return (cfg().get("firewall") or {}).get(key, default)


def path_setting(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def run(cmd, check=True, capture=True, timeout=60, input_text=None):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=capture, text=True, timeout=timeout, input=input_text)
    if check and r.returncode != 0:
        sys.exit(f"Command failed ({r.returncode}): {' '.join(map(str, cmd))}\n{r.stdout or ''}{r.stderr or ''}")
    return r


def ask(question: str) -> str:
    """Ask the operator; the answer goes into the report."""
    try:
        return input(f"  ? {question} ").strip() or "(no answer)"
    except EOFError:
        return "(no answer)"


def pause(text: str) -> None:
    try:
        input(f"\n  >>> {text}\n      Press Enter when done ... ")
    except EOFError:
        pass


# ------------------------------------------------------------------ router over SSH
def ssh_base() -> List[str]:
    return ["ssh", "-p", str(fw("router_port", 22)), "-i", str(path_setting(fw("router_key_file"))),
            "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
            "-o", f"UserKnownHostsFile={path_setting(fw('router_known_hosts_file'))}",
            "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=5",
            f"{fw('router_user', 'root')}@{fw('router_host')}"]


def router(command: str, check=False, input_text=None) -> Tuple[int, str]:
    r = run(ssh_base() + [command], check=check, timeout=30, input_text=input_text)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def router_sets() -> Dict[str, List[str]]:
    code, out = router(f"nft -j list table {fw('table_family', 'inet')} {fw('table_name', 'ids')}")
    return nft_sets(out) if code == 0 else {"error": [out.strip()[:300]]}


# ------------------------------------------------------------------ setup
def cmd_setup(_):
    KEYS.mkdir(exist_ok=True)
    RUN.mkdir(exist_ok=True)
    key = path_setting(fw("router_key_file"))
    if not key.exists():
        run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "ids-hwlab-sensor", "-f", str(key)])
        os.chmod(key, 0o600)
    if not LOGIN_FILE.exists():
        pw = secrets.token_urlsafe(12)
        run([PY, "tools/create_admin.py", "-u", "labadmin", "-p", pw, "--force"])
        LOGIN_FILE.write_text(f"labadmin {pw}\n", encoding="utf-8")
        os.chmod(LOGIN_FILE, 0o600)
    print(f"Router key: {key}\nPublic key to put on the router (one line):\n")
    print("  " + Path(str(key) + ".pub").read_text().strip())
    print("\nOn OpenWrt: add it to /etc/dropbear/authorized_keys. On a Linux router: /root/.ssh/authorized_keys.")
    print(f"Dashboard login (keep it private): {LOGIN_FILE}")
    print("Next: python lab_hardware/hwlab.py trust-router")


def cmd_trust_router(args):
    host, port = fw("router_host"), int(fw("router_port", 22))
    r = run(["ssh-keyscan", "-p", str(port), "-t", "ed25519", host], check=False, timeout=20)
    lines = [l for l in (r.stdout or "").splitlines() if l and not l.startswith("#")]
    if not lines:
        sys.exit(f"No ED25519 host key from {host}:{port}. Is SSH running on the router? ({r.stderr.strip()})")
    tmp = KEYS / "known_hosts.new"
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fp = run(["ssh-keygen", "-lf", str(tmp)], check=False).stdout.strip()
    print(f"Router {host}:{port} host key fingerprint:\n  {fp}")
    print("Compare it with the router's own key (on the router: ssh-keygen -lf <host key>.pub, or on "
          "OpenWrt: dropbearkey -y -f /etc/dropbear/dropbear_ed25519_host_key).")
    if not args.yes and ask("Is this the same fingerprint? (yes/no)").lower() != "yes":
        tmp.unlink()
        sys.exit("Not saved.")
    tmp.replace(path_setting(fw("router_known_hosts_file")))
    code, out = router("nft --version")
    print(f"Saved. SSH test: {'OK, ' + out.strip() if code == 0 else 'FAILED: ' + out.strip()}")


def nft_with_allowlist() -> str:
    text = (ROOT / "sensor" / "ids_router.nft").read_text(encoding="utf-8")
    allow = ", ".join(cfg().get("allowlist") or [])
    out, done = [], False
    for line in text.splitlines():
        if line.strip().startswith("elements = {") and not done:
            line = line[: line.index("elements")] + f"elements = {{ {allow} }}"
            done = True
        out.append(line)
    return "\n".join(out) + "\n"


def cmd_router_install(_):
    body = nft_with_allowlist()
    code, out = router("cat > /etc/ids_router.nft && nft -c -f /etc/ids_router.nft && "
                       f"(nft delete table {fw('table_family', 'inet')} {fw('table_name', 'ids')} 2>/dev/null; true) && "
                       "nft -f /etc/ids_router.nft && echo LOADED", input_text=body)
    print(out.strip())
    if code != 0 or "LOADED" not in out:
        sys.exit("Router rules NOT loaded.")
    print("Loaded /etc/ids_router.nft on the router. To load it again after a router restart, add this line "
          "to /etc/rc.local (before 'exit 0') on OpenWrt, or make a systemd unit on a Linux router:\n"
          "  nft -f /etc/ids_router.nft")
    print("Router sets now:", router_sets())


# ------------------------------------------------------------------ checks
def tcp_open(host: str, port: int, timeout=2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def rx_packets(iface: str) -> Optional[int]:
    try:
        return int(Path(f"/sys/class/net/{iface}/statistics/rx_packets").read_text())
    except (OSError, ValueError):
        return None


def conn_log() -> Path:
    return Path((cfg().get("zeek") or {}).get("conn_log_path", "/var/log/ids-zeek/conn.log"))


def conn_lines() -> int:
    f = conn_log()
    try:
        with f.open("rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def login_api() -> None:
    if API.token:
        return
    if not LOGIN_FILE.exists():
        sys.exit("No dashboard login yet: run `hwlab.py setup` first.")
    API.login(*read_login(LOGIN_FILE))


def cmd_check(_):
    rows: List[Tuple[str, bool, str]] = []

    def add(name, ok, detail=""):
        rows.append((name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))

    print("Pre-flight checks (guide Steps 3b, 5, 19):")
    for tool in ("zeek", "nmap", "ssh"):
        add(f"`{tool}` installed", shutil.which(tool) or Path(f"/opt/zeek/bin/{tool}").exists())
    iface = lab("sensor_mirror_interface")
    a = rx_packets(iface)
    time.sleep(3)
    b = rx_packets(iface)
    add(f"mirror port {iface} receives packets", a is not None and b is not None and b > a,
        f"{(b or 0) - (a or 0)} packets in 3 s" if a is not None else "interface not found")
    l1 = conn_lines()
    add("Zeek writes conn.log", conn_log().exists(), f"{conn_log()} ({l1:,} lines)")
    bundle = path_setting((cfg().get("model") or {}).get("bundle_path", ""))
    add("model bundle present", bundle.exists(), str(bundle))
    add("MongoDB answers on 27017", tcp_open("127.0.0.1", 27017))
    cam = lab("camera_ip")
    for port in lab("camera_ports", [80, 554]):
        add(f"camera {cam}:{port} answers", tcp_open(cam, int(port)))
    code, out = router("nft list set {0} {1} allow".format(fw("table_family", "inet"), fw("table_name", "ids")))
    add("router SSH works and the ids table is loaded", code == 0, out.strip().splitlines()[0] if out.strip() else "")
    allow = cfg().get("allowlist") or []
    add("router allow set = settings allowlist", code == 0 and all(ip in out for ip in allow), ", ".join(allow))
    for host, port in (("1.1.1.1", 53), ("8.8.8.8", 53), ("9.9.9.9", 443)):
        add(f"no route to the public internet ({host}:{port})", not tcp_open(host, port, timeout=3))
    add("IDS backend running", API.up(), "start it with ids-start" if not API.up() else "")
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"preflight_{utc_now():%Y%m%d_%H%M%S}.md"
    md = [f"# Hardware lab pre-flight check ({utc_now():%Y-%m-%d %H:%M} UTC)", "",
          "| Check | Result | Detail |", "| --- | --- | --- |"]
    md += [f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n, ok, d in rows]
    md += ["", "Also check by hand (guide Step 5): the camera streams to the NVR; the attack computer reaches "
           "the camera through the router; Wi-Fi is off on all lab devices."]
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n{sum(ok for _, ok, _ in rows)}/{len(rows)} passed. Report: {path}")


# ------------------------------------------------------------------ Zeek and the backend
def cmd_zeek_start(_):
    iface = lab("sensor_mirror_interface")
    run(["sudo", "ip", "link", "set", iface, "up"], check=False)
    run(["sudo", "ethtool", "-K", iface, "gro", "off", "lro", "off"], check=False)
    logdir = str(conn_log().parent)
    r = run(["sudo", "bash", "sensor/run_zeek.sh", "--interface", iface, "--log-dir", logdir, "--daemon"], check=False)
    print((r.stdout or "") + (r.stderr or ""))


def cmd_zeek_stop(_):
    r = run(["sudo", "bash", "sensor/run_zeek.sh", "--stop", "--log-dir", str(conn_log().parent)], check=False)
    print((r.stdout or "") + (r.stderr or ""))


def write_runtime_settings(auto: bool) -> None:
    data = cfg()
    data.setdefault("response", {})["auto_response"] = auto
    RUNTIME_SETTINGS.write_text("# made by hwlab.py ids-start; do not edit (edit settings.hardware.yaml)\n"
                                + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def cmd_ids_start(args):
    if API.up():
        sys.exit("The backend already answers on port 5000 (stop it first: ids-stop).")
    RUN.mkdir(exist_ok=True)
    auto = args.auto_response == "on"
    write_runtime_settings(auto)
    env = dict(os.environ, IDS_SETTINGS_FILE=str(RUNTIME_SETTINGS), PORT="5000", HOST="0.0.0.0")
    log = open(BACKEND_LOG, "a", encoding="utf-8")
    p = subprocess.Popen([PY, "-m", "core_engine.app"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    PID_FILE.write_text(str(p.pid))
    for _ in range(90):
        if API.up():
            break
        time.sleep(1)
    else:
        sys.exit(f"Backend did not start; see {BACKEND_LOG}")
    login_api()
    code, st = API.call("GET", "/api/v1/pipeline/status")
    if st.get("status") != "running":
        API.call("POST", "/api/v1/pipeline/start")
    print(f"IDS backend running (pid {p.pid}); automatic response: {'ON' if auto else 'OFF'}")
    print("Dashboard: http://<sensor-ip>:5000 (from the admin PC); login in", LOGIN_FILE)


def cmd_ids_stop(_):
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.killpg(pid, 15)
        except (ProcessLookupError, PermissionError, AttributeError):
            try:
                os.kill(pid, 15)
            except ProcessLookupError:
                pass
        PID_FILE.unlink()
        print("IDS backend stopped")
    else:
        print("No backend started by hwlab.py (no pid file).")


def cmd_status(_):
    print("Router sets:", router_sets())
    print(f"Zeek conn.log: {conn_log()} ({conn_lines():,} lines)")
    if API.up():
        login_api()
        code, st = API.call("GET", "/api/v1/pipeline/status")
        print("Pipeline:", st.get("status"), st.get("metrics"))
        code, s = API.call("GET", "/api/summary")
        print("System:", s.get("system"))
    else:
        print("IDS backend: not running")


def cmd_reset(_):
    if API.up():
        login_api()
        code, bl = API.call("GET", "/api/blocklist")
        for b in bl.get("blocks", []):
            API.call("DELETE", f"/api/blocklist/{b['ip']}", body={"reason": "hardware lab reset before a test"})
        print(f"removed {len(bl.get('blocks', []))} block(s) through the IDS (audit kept)")
    fam, tab = fw("table_family", "inet"), fw("table_name", "ids")
    router(f"nft flush set {fam} {tab} block_src; nft flush set {fam} {tab} block_dst; nft flush set {fam} {tab} limit_src")
    print("router sets now:", router_sets())


# ------------------------------------------------------------------ Table 10 scenarios
def scenarios() -> Dict[int, dict]:
    cam, sim, att = lab("camera_ip"), lab("camera_sim_ip"), lab("attack_ip")
    return {
        1: dict(title="Normal live streaming and playback", wait=600,
                how="camera streams to the NVR; the admin logs in to the camera, uses live view and plays back video",
                expect="most flows benign; no high-confidence attack event",
                safe="no automatic block; the traffic summary keeps working",
                steps=["Keep the camera streaming to the NVR the whole time.",
                       f"On the admin PC: log in to the camera web page (http://{cam}), open live view, play back a recording."],
                questions=["Did live view and playback work the whole time? (y/n)"]),
        2: dict(title="Authorised Nmap horizontal scan", wait=90,
                how=f"attack computer: nmap -p 23,80,554 192.168.50.0/24",
                expect="port-scan class, or a scan alert",
                safe="the scanner is blocked only after the threshold; the allowlisted admin can still get in",
                steps=[f"On the ATTACK computer ({att}): nmap -p 23,80,554 192.168.50.0/24"],
                questions=["From the admin PC, do the camera page and the dashboard still open? (y/n)"]),
        3: dict(title="Rate-limited DDoS-like traffic", wait=90, probe=True,
                how=f"attack computer: sudo python3 tests/lab_scenarios/syn_flood.py {cam} --port 80 --rate 1000 --seconds 20",
                expect="a DDoS/DoS prediction, and more events than usual",
                safe="the source is blocked or rate-limited (D-055); the camera service comes back",
                steps=[f"On the ATTACK computer ({att}): sudo python3 tests/lab_scenarios/syn_flood.py {cam} "
                       "--port 80 --rate 1000 --seconds 20   (or: sudo hping3 -S -p 80 -i u1000 -c 20000 " + cam + ")"],
                questions=["Did the camera's live view on the NVR come back after the flood? (y/n)"]),
        4: dict(title="C&C-like periodic outbound simulation", wait=60,
                how=f"attack computer runs the lab C&C server (port 6667 opens after 120 s); the camera-side lab "
                    f"computer {sim} connects every 5 s and keeps short chat sessions (10 min)",
                expect="C&C or heartbeat evidence from a local device to the outside",
                safe="the destination is blocked, or the device is isolated, following the policy",
                steps=[f"On the ATTACK computer ({att}): python3 tests/lab_scenarios/lab_server.py --role cnc --cnc-open-after 120",
                       f"On the CAMERA-SIDE lab computer ({sim}): python3 tests/lab_scenarios/camera_sim.py bot "
                       f"--server {att} --every 5 --session 30 --duration 600",
                       "Wait until camera_sim.py finishes (10 minutes), then stop lab_server.py (Ctrl+C)."],
                questions=[]),
        5: dict(title="Controlled file-transfer pattern", wait=60,
                how=f"camera-side lab computer {sim} downloads a harmless test program from the attack computer 5 times",
                expect="a download or malware prediction, if the learned features can show it (file-type rule: "
                       "RULE_EXECUTABLE_DOWNLOAD)",
                safe="alert and evidence are kept; we claim nothing if the model cannot generalise",
                steps=[f"On the ATTACK computer ({att}): sudo python3 tests/lab_scenarios/lab_server.py --role attack --no-cnc",
                       f"On the CAMERA-SIDE lab computer ({sim}): python3 tests/lab_scenarios/camera_sim.py download "
                       f"--url http://{att}/bins/lab_test.x86 --count 5 --every 20",
                       "Then stop lab_server.py (Ctrl+C)."],
                questions=[]),
        6: dict(title="Manual block and unblock", wait=0,
                how="the admin blocks and then unblocks the attack computer (this tool uses the dashboard API; "
                    "you can also do it on the Blocklist page)",
                expect="the rule change can be seen in the dashboard and the database",
                safe="the connection comes back, and the full audit record is kept",
                steps=[], questions=[]),
    }


class Prober(threading.Thread):
    """Checks the camera ports every 2 s during a run (Table 10 row 3: 'the camera service comes back')."""

    def __init__(self, host: str, ports: List[int]):
        super().__init__(daemon=True)
        self.host, self.ports = host, ports
        self.samples: List[Tuple[float, bool]] = []
        self.stop_flag = threading.Event()

    def run(self):
        while not self.stop_flag.is_set():
            ok = all(tcp_open(self.host, p, timeout=1.5) for p in self.ports)
            self.samples.append((time.time(), ok))
            self.stop_flag.wait(2.0)

    def summary(self) -> str:
        if not self.samples:
            return "no samples"
        down = [t for t, ok in self.samples if not ok]
        last_ok = self.samples[-1][1]
        return (f"{len(self.samples)} checks every 2 s; camera ports {self.ports} unreachable in {len(down)} of them; "
                f"at the end: {'reachable' if last_ok else 'NOT reachable'}")


def threshold_text() -> str:
    code, s = API.call("GET", "/api/settings")
    st = s.get("settings", {})
    return (f"block thresholds {st.get('block_thresholds')}, rate-limit thresholds {st.get('rate_limit_thresholds')}, "
            f"repeats {st.get('min_repeats')} in {st.get('repeat_window_seconds')} s, auto_response {st.get('auto_response')}")


def cmd_scenario(args):
    n = args.n
    sc = scenarios()[n]
    if not API.up():
        sys.exit("Start the backend first: hwlab.py ids-start --auto-response on")
    login_api()
    code, bl = API.call("GET", "/api/blocklist")
    if bl.get("blocks") and not args.keep_blocks:
        sys.exit("There are active blocks. Start from a clean state: hwlab.py reset (or pass --keep-blocks).")
    cam, sim, att = lab("camera_ip"), lab("camera_sim_ip"), lab("attack_ip")
    print(f"\nTable 10 scenario {n} (run {args.run}): {sc['title']}\n  expected: {sc['expect']}\n  safe result: {sc['safe']}")
    print("  Write the logbook line in docs/lab_logbook.md before you start (date, who, what, scenario, run).")
    code, s0 = API.call("GET", "/api/summary")
    benign0 = (s0.get("metrics") or {}).get("benign_flows_24h", 0)
    thr = threshold_text()
    start, lines0 = utc_now(), conn_lines()
    notes, checks = [f"settings at start: {thr}"], []
    prober = None
    if sc.get("probe"):
        prober = Prober(cam, [int(p) for p in lab("camera_ports", [80])])
        prober.start()

    if n == 6:
        before = ask(f"On the ATTACK computer run: curl -m 3 -s -o /dev/null -w '%{{http_code}}\\n' http://{cam}/ "
                     "- did it answer? (y/n)")
        code1, res1 = API.call("POST", "/api/blocklist", body={"ip": att, "direction": "source", "duration_minutes": 10,
                                                               "reason": "Table 10 row 6 test"})
        time.sleep(3)
        sets_during = router_sets()
        during = ask("Run the same curl again - did it answer now? (y/n; expected: n)")
        code2, res2 = API.call("DELETE", f"/api/blocklist/{att}", body={"reason": "Table 10 row 6 test done"})
        time.sleep(3)
        sets_after = router_sets()
        after = ask("Run the same curl again - did it answer now? (y/n; expected: y)")
        code, logs = API.call("GET", "/api/logs?limit=50")
        audit = [f"{l.get('timestamp')} {l.get('actor')} {l.get('event')} {l.get('outcome')}"
                 for l in logs.get("logs", []) if l.get("event") in ("MANUAL_BLOCK", "MANUAL_UNBLOCK")][:4]
        checks += [("Manual block API answer", str(code1)),
                   (f"{att} in router block_src during the block", "yes" if ip_in_sets(att, sets_during, ["block_src"]) else "NO"),
                   (f"{att} gone from the router after unblock", "yes" if not ip_in_sets(att, sets_after) else "NO"),
                   ("Attack computer reached the camera before / during / after", f"{before} / {during} / {after}"),
                   ("Audit records (system_logs)", "; ".join(audit) or "NONE FOUND")]
    else:
        for i, step in enumerate(sc["steps"], 1):
            print(f"  {i}. {step}")
        if n == 1:
            print(f"  The tool now waits {args.wait or sc['wait']:.0f} s while the normal activities run.")
            time.sleep(args.wait or sc["wait"])
        else:
            pause("Run the command(s) above now.")
            print(f"  Waiting {args.wait if args.wait is not None else sc['wait']:.0f} s so Zeek writes the last flows ...")
            time.sleep(args.wait if args.wait is not None else sc["wait"])
    if prober:
        prober.stop_flag.set()
        prober.join(5)
        checks.append(("Camera service during and after the flood (probe from the sensor)", prober.summary()))
    end = utc_now()
    events = events_since(API, start)
    code, bl = API.call("GET", "/api/blocklist")
    blocks = bl.get("blocks", [])
    sets = router_sets()
    code, s1 = API.call("GET", "/api/summary")
    system = s1.get("system") or {}
    benign1 = (s1.get("metrics") or {}).get("benign_flows_24h", 0)
    auto_blocks = [b for b in blocks if str(b.get("actor", "")).startswith(("autonomous", "system"))]

    if n == 1:
        checks += [("Automatic blocks during the run", str(len(auto_blocks)) + (" (correct)" if not auto_blocks else " - WRONG")),
                   ("Traffic summary kept working (benign flows counted)", f"{benign0:,} -> {benign1:,}")]
    elif n == 2:
        top = max((float(e.get("confidence") or 0) for e in events if e.get("predicted_class") == "PortScan"), default=0)
        checks += [("Highest PortScan confidence", f"{top:.2f}"),
                   (f"Scanner {att} blocked", "yes" if ip_in_sets(att, sets, ["block_src"]) else "no")]
    elif n == 3:
        checks += [(f"Source {att} rate-limited (limit_src) or blocked (block_src)",
                    ", ".join(ip_in_sets(att, sets)) or "NO")]
    elif n == 4:
        checks += [(f"C&C destination {att} blocked (block_dst)", "yes" if ip_in_sets(att, sets, ["block_dst"]) else "NO"),
                   (f"Camera-side device {sim} blocked", "YES - WRONG" if ip_in_sets(sim, sets) else "no (correct)")]
    elif n == 5:
        rule = [e for e in events if e.get("reason_code") == "RULE_EXECUTABLE_DOWNLOAD"]
        model = [e for e in events if e.get("predicted_class") == "Malware_Download" and e not in rule]
        checks += [("File-type rule alerts (RULE_EXECUTABLE_DOWNLOAD)", str(len(rule))),
                   ("Model Malware_Download alerts", str(len(model))),
                   ("Any block for the download", "YES" if any(b.get("predicted_class") == "Malware_Download" for b in blocks) else "no")]
    for q in sc.get("questions", []):
        checks.append((q, ask(q)))

    protected = {cam: "camera", sim: "camera-side lab computer"}
    protected.update({ip: "allowlisted device" for ip in cfg().get("allowlist") or []})
    path = REPORTS / f"scenario_{n}_run{args.run}_{start:%Y%m%d_%H%M%S}.md"
    text = scenario_report(
        path=path, title=f"Hardware lab - Table 10 scenario {n}, run {args.run}: {sc['title']}",
        where="hardware lab (real IP camera, managed switch mirror port, Linux sensor with Zeek and the IDS, lab router "
              f"with nftables); automatic response {'ON' if system.get('auto_response') else 'OFF'}",
        start=start, end=end, how=sc["how"], expect=sc["expect"], safe=sc["safe"],
        model=system.get("model_version", "unknown"), flows=conn_lines() - lines0, events=events, blocks=blocks,
        fw_sets=sets, protected=protected, checks=checks, notes=notes)
    print("\n" + text.split("## What the system did", 1)[-1])
    print(f"report: {path}")


# ------------------------------------------------------------------ reliability (guide Step 38)
def cmd_reliability(args):
    if not API.up():
        sys.exit("Start the backend first (ids-start).")
    login_api()
    start = utc_now()
    checks: List[Tuple[str, str]] = []
    if args.test == "restart":
        code, st0 = API.call("GET", "/api/v1/pipeline/status")
        code, ev0 = API.call("GET", "/api/events?limit=1000")
        code, bl0 = API.call("GET", "/api/blocklist")
        sets0 = router_sets()
        print("Keep normal traffic running (camera streaming). The backend is stopped for 30 s and started again.")
        auto = "on" if (API.call("GET", "/api/summary")[1].get("system") or {}).get("auto_response") else "off"
        cmd_ids_stop(None)
        API.token = None
        time.sleep(30)
        cmd_ids_start(argparse.Namespace(auto_response=auto))
        time.sleep(20)
        code, st1 = API.call("GET", "/api/v1/pipeline/status")
        code, ev1 = API.call("GET", "/api/events?limit=1000")
        code, bl1 = API.call("GET", "/api/blocklist")
        sets1 = router_sets()
        ids0 = {e.get("event_id") for e in ev0.get("events", [])}
        ids1 = {e.get("event_id") for e in ev1.get("events", [])}
        checks += [("Events kept in MongoDB after the restart", f"{len(ids0 & ids1)} of {len(ids0)}"),
                   ("Active blocks before / after", f"{len(bl0.get('blocks', []))} / {len(bl1.get('blocks', []))}"),
                   ("Router sets before", str(sets0)), ("Router sets after", str(sets1)),
                   ("Pipeline running after the restart", str(st1.get("status"))),
                   ("Flows read after the restart (adapter continued from its saved place)",
                    str((st1.get("metrics") or {}).get("flows_processed")))]
    else:  # expiry
        test_ip = "10.10.10.99"
        code, res = API.call("POST", "/api/blocklist", body={"ip": test_ip, "direction": "source", "duration_minutes": 1,
                                                              "reason": "Step 38 expiry test"})
        s_before = router_sets()
        print("Rule added for 1 minute; waiting 90 s ...")
        time.sleep(90)
        s_after = router_sets()
        code, hist = API.call("GET", f"/api/blocklist?ip={test_ip}")
        recs = [b for b in hist.get("history", []) if b.get("ip") == test_ip]
        checks += [("Rule added (API answer)", str(code)),
                   ("In the router before expiry", "yes" if ip_in_sets(test_ip, s_before) else "NO"),
                   ("Gone from the router after 90 s", "yes" if not ip_in_sets(test_ip, s_after) else "NO"),
                   ("Database status after expiry", ", ".join(str(b.get("status")) for b in recs) or "see Blocklist history")]
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"reliability_{args.test}_{start:%Y%m%d_%H%M%S}.md"
    md = [f"# Reliability test ({args.test}), {start:%Y-%m-%d %H:%M} UTC (guide Step 38, proposal Table 9)", ""]
    md += [f"- {q}: **{a}**" for q, a in checks]
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"report: {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("setup", "router-install", "check", "zeek-start", "zeek-stop", "ids-stop", "status", "reset"):
        sub.add_parser(name)
    tr = sub.add_parser("trust-router")
    tr.add_argument("--yes", action="store_true", help="save without asking (only if you checked the fingerprint)")
    st = sub.add_parser("ids-start")
    st.add_argument("--auto-response", choices=["on", "off"], default="off")
    sc = sub.add_parser("scenario")
    sc.add_argument("n", type=int, choices=range(1, 7))
    sc.add_argument("--run", type=int, default=1, help="run number (the guide asks for about 5 runs)")
    sc.add_argument("--wait", type=float, default=None, help="seconds to wait for Zeek after the commands")
    sc.add_argument("--keep-blocks", action="store_true")
    rl = sub.add_parser("reliability")
    rl.add_argument("test", choices=["restart", "expiry"])
    args = ap.parse_args()
    {"setup": cmd_setup, "trust-router": cmd_trust_router, "router-install": cmd_router_install, "check": cmd_check,
     "zeek-start": cmd_zeek_start, "zeek-stop": cmd_zeek_stop, "ids-start": cmd_ids_start, "ids-stop": cmd_ids_stop,
     "status": cmd_status, "reset": cmd_reset, "scenario": cmd_scenario, "reliability": cmd_reliability}[args.cmd](args)


if __name__ == "__main__":
    main()
