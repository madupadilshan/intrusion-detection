#!/usr/bin/env python3
"""
tests/lab_scenarios/lab_server.py - Lab servers for the Table 10 tests (outside network only).

Roles:
  attack  runs on the ATTACK computer (proposal Table 10 rows 4 and 5):
            - web server on TCP 80; /bins/lab_test.x86 is a HARMLESS program (a copy of the
              system's `true` command, which does nothing), so Zeek's files.log sees a real
              Linux program being downloaded;
            - lab "C&C" server on TCP 6667 (IRC-like). It starts listening only after
              --cnc-open-after seconds, so the camera simulator's first tries fail, as in IoT-23.
  cnc     only the lab C&C server (to start it on its own for Table 10 row 4).
  cloud   the camera's normal "cloud" (Table 10 row 1): status on TCP 443, time on UDP 123,
          names on UDP 53. --outage-after makes it stop answering (to test issue 39: a camera
          that keeps retrying an unreachable cloud server must NOT be blocked as C&C).

Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import http.server
import os
import shutil
import socket
import socketserver
import struct
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


class TS(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class US(socketserver.ThreadingMixIn, socketserver.UDPServer):
    allow_reuse_address = True
    daemon_threads = True


# ------------------------------------------------------------------ attack role
def make_test_program(folder: Path) -> Path:
    """A harmless Linux program: a copy of `true` (it only exits with code 0)."""
    folder.mkdir(parents=True, exist_ok=True)
    dst = folder / "lab_test.x86"
    src = shutil.which("true") or "/bin/true"
    if os.path.exists(src):
        shutil.copyfile(src, dst)
    else:  # no `true` (e.g. Windows): a minimal ELF header is enough for file-type detection
        dst.write_bytes(b"\x7fELF\x02\x01\x01" + b"\0" * 9 + struct.pack("<HHI", 2, 62, 1) + b"\0" * 40)
    return dst


def run_web(folder: Path) -> None:
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(folder), **k)  # noqa: E731
    TS(("0.0.0.0", 80), handler).serve_forever()


class Cnc(socketserver.BaseRequestHandler):
    def handle(self):
        peer = self.client_address[0]
        log(f"C&C: bot connected from {peer}")
        s = self.request
        s.settimeout(12)
        try:
            s.sendall(b":lab-cnc 001 bot :Welcome\r\n")
            while True:
                s.sendall(b"PING :lab-cnc\r\n")
                data = s.recv(512)
                if not data or b"QUIT" in data:
                    break
                time.sleep(10)
        except OSError:
            pass
        log(f"C&C: bot {peer} left")


def run_cnc(open_after: float) -> None:
    if open_after > 0:
        log(f"C&C: port 6667 stays closed for {open_after:.0f} s (tries will fail)")
        time.sleep(open_after)
    log("C&C: listening on 6667")
    TS(("0.0.0.0", 6667), Cnc).serve_forever()


# ------------------------------------------------------------------ cloud role
STATE = {"outage": False}


class Status(socketserver.BaseRequestHandler):
    def handle(self):
        if STATE["outage"]:
            return
        try:
            self.request.settimeout(5)
            self.request.recv(1024)
            self.request.sendall(b'{"ok":true}\n')
        except OSError:
            pass


class Udp(socketserver.BaseRequestHandler):
    def handle(self):
        if STATE["outage"]:
            return
        data, sock = self.request
        port = self.server.server_address[1]
        if port == 123:
            reply = b"\x1c" + b"\0" * 39 + struct.pack(">I", int(time.time()) + 2208988800) + b"\0" * 4
        else:  # a DNS answer: same id, one A record 10.10.10.123
            reply = (data[:2] + b"\x81\x80" + data[4:6] + b"\x00\x01\x00\x00\x00\x00" + data[12:]
                     + b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton("10.10.10.123"))
        sock.sendto(reply, self.client_address)


def run_cloud(outage_after: float) -> None:
    for srv in (TS(("0.0.0.0", 443), Status), US(("0.0.0.0", 123), Udp), US(("0.0.0.0", 53), Udp)):
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    log("cloud up: TCP 443, UDP 123, UDP 53")
    if outage_after > 0:
        time.sleep(outage_after)
        STATE["outage"] = True
        log("cloud OUTAGE: no answers from now on")
    while True:
        time.sleep(3600)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--role", choices=["attack", "cnc", "cloud"], required=True)
    ap.add_argument("--files", type=Path, default=Path("/tmp/lab_files"), help="web server folder (attack role)")
    ap.add_argument("--cnc-open-after", type=float, default=120.0)
    ap.add_argument("--no-cnc", action="store_true", help="attack role: web server only")
    ap.add_argument("--outage-after", type=float, default=0.0, help="cloud role: stop answering after N s")
    args = ap.parse_args()
    if args.role == "cnc":
        run_cnc(args.cnc_open_after)
    elif args.role == "attack":
        prog = make_test_program(args.files / "bins")
        log(f"web server on 80, harmless test program {prog} ({prog.stat().st_size} bytes)")
        threading.Thread(target=run_web, args=(args.files,), daemon=True).start()
        if args.no_cnc:
            while True:
                time.sleep(3600)
        run_cnc(args.cnc_open_after)
    else:
        run_cloud(args.outage_after)


if __name__ == "__main__":
    main()
