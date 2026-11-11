#!/usr/bin/env python3
"""
tests/lab_scenarios/camera_sim.py - IP-camera simulator for the lab (proposal Table 10).

Runs on a lab device on the CAMERA side (a Raspberry Pi or PC in the real lab; a container in
lab_virtual/). Never run this on someone else's real camera (guide Step 35).

Modes:
  normal    camera services and normal background traffic (Table 10 row 1):
              - web page on TCP 80 and a video stream on TCP 554 (RTSP-like) for the NVR/admin PC
              - every 30 s: a small "cloud status" request to the cloud server (TCP 443)
              - every 60 s: a time request (UDP 123) and a name lookup (UDP 53)
  bot       C&C-like periodic outbound connections (Table 10 row 4): connect to the lab C&C
            server every --every seconds; when it answers, keep a short chat session (~30 s),
            close, and connect again. While the server is down, the tries fail (like IoT-23).
  nvr       the NVR (192.168.50.20): records the camera stream, reconnecting every 5 minutes
  admin     the admin PC (192.168.50.10): opens the camera web page every 60 s (live viewing)
  download  controlled file-transfer pattern (Table 10 row 5): download a HARMLESS file from the
            lab web server --count times, --every seconds apart.

Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import http.server
import random
import socket
import socketserver
import struct
import threading
import time
import urllib.request


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- normal mode
class CameraWeb(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = (b"<html><body><h1>Lab IP camera</h1><p>status: recording</p></body></html>"
                if self.path in ("/", "/index.html") else b'{"status":"ok"}')
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class Stream(socketserver.BaseRequestHandler):
    """RTSP-like video stream: ~200 KB/s of data while the client stays connected."""

    def handle(self):
        self.request.settimeout(5)
        try:
            self.request.recv(1024)  # the client's "PLAY" line
            frame = bytes(random.getrandbits(8) for _ in range(1400)) * 14  # ~20 KB "frame"
            while True:
                self.request.sendall(frame)
                time.sleep(0.1)
        except OSError:
            pass


class TS(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def cloud_status(cloud: str) -> None:
    while True:
        try:
            with socket.create_connection((cloud, 443), timeout=5) as s:
                s.sendall(b'{"camera":"cam-01","status":"recording","storage":"72%"}\n')
                s.recv(512)
        except OSError as e:
            log(f"cloud status failed: {e}")
        time.sleep(30)


def time_and_dns(cloud: str) -> None:
    ntp = b"\x1b" + 47 * b"\0"
    dns = (struct.pack(">HHHHHH", random.randint(0, 65535), 0x0100, 1, 0, 0, 0)
           + b"\x05cloud\x03lab\x00\x00\x01\x00\x01")
    while True:
        for port, payload in ((123, ntp), (53, dns)):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
                    u.settimeout(3)
                    u.sendto(payload, (cloud, port))
                    u.recvfrom(512)
            except OSError:
                pass
        time.sleep(60)


def run_normal(args) -> None:
    web = TS(("0.0.0.0", 80), CameraWeb)
    stream = TS(("0.0.0.0", 554), Stream)
    for target in (web.serve_forever, stream.serve_forever):
        threading.Thread(target=target, daemon=True).start()
    threading.Thread(target=cloud_status, args=(args.cloud,), daemon=True).start()
    threading.Thread(target=time_and_dns, args=(args.cloud,), daemon=True).start()
    log(f"camera services up (web :80, stream :554); cloud = {args.cloud}")
    while True:
        time.sleep(3600)


# ---------------------------------------------------------------- nvr / admin modes
def run_nvr(args) -> None:
    while True:
        got, start = 0, time.time()
        try:
            with socket.create_connection((args.camera, 554), timeout=5) as s:
                s.settimeout(10)
                s.sendall(b"PLAY rtsp://camera/stream1 RTSP/1.0\r\n\r\n")
                while time.time() - start < args.segment:
                    data = s.recv(65536)
                    if not data:
                        break
                    got += len(data)
            log(f"NVR: recorded {got / 1e6:.1f} MB")
        except OSError as e:
            log(f"NVR: stream error {e}")
            time.sleep(5)


def run_admin(args) -> None:
    while True:
        try:
            with urllib.request.urlopen(f"http://{args.camera}/", timeout=5) as r:
                r.read()
            with urllib.request.urlopen(f"http://{args.camera}/api/status", timeout=5) as r:
                r.read()
        except OSError as e:
            log(f"admin: camera page error {e}")
        time.sleep(args.every)


# ---------------------------------------------------------------- bot mode
def run_bot(args) -> None:
    end = time.time() + args.duration
    tries = sessions = 0
    while time.time() < end:
        tries += 1
        try:
            with socket.create_connection((args.server, args.port), timeout=5) as s:
                sessions += 1
                s.settimeout(15)
                s.sendall(f"NICK cam{random.randint(1000, 9999)}\r\nUSER cam 0 * :cam\r\n".encode())
                stop = time.time() + args.session
                while time.time() < stop:
                    data = s.recv(512)
                    if not data:
                        break
                    if data.startswith(b"PING"):
                        s.sendall(b"PONG" + data[4:])
                s.sendall(b"QUIT\r\n")
            log(f"session {sessions} done")
        except OSError as e:
            log(f"try {tries}: no answer ({e.__class__.__name__})")
        time.sleep(args.every)
    log(f"bot finished: {tries} tries, {sessions} sessions")


# ---------------------------------------------------------------- download mode
def run_download(args) -> None:
    for i in range(1, args.count + 1):
        try:
            with urllib.request.urlopen(args.url, timeout=20) as r:
                n = len(r.read())
            log(f"download {i}: {n} bytes from {args.url}")
        except OSError as e:
            log(f"download {i} failed: {e}")
        time.sleep(args.every)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    n = sub.add_parser("normal")
    n.add_argument("--cloud", default="10.10.10.123", help="the camera's cloud server")
    b = sub.add_parser("bot")
    b.add_argument("--server", default="10.10.10.50", help="lab C&C server (the attack computer)")
    b.add_argument("--port", type=int, default=6667)
    b.add_argument("--every", type=float, default=5.0, help="seconds between tries")
    b.add_argument("--session", type=float, default=30.0, help="seconds per chat session")
    b.add_argument("--duration", type=float, default=600.0, help="total seconds")
    v = sub.add_parser("nvr")
    v.add_argument("--camera", default="192.168.50.30")
    v.add_argument("--segment", type=float, default=300.0, help="seconds per recording segment")
    a = sub.add_parser("admin")
    a.add_argument("--camera", default="192.168.50.30")
    a.add_argument("--every", type=float, default=60.0)
    d = sub.add_parser("download")
    d.add_argument("--url", default="http://10.10.10.50/bins/lab_test.x86")
    d.add_argument("--count", type=int, default=5)
    d.add_argument("--every", type=float, default=20.0)
    args = ap.parse_args()
    {"normal": run_normal, "bot": run_bot, "download": run_download, "nvr": run_nvr,
     "admin": run_admin}[args.mode](args)


if __name__ == "__main__":
    main()
