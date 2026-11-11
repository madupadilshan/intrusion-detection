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
CAMERA_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lab IP Camera - Live Web Interface</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }
        .container { max-width: 900px; margin: 0 auto; background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .header { background: #0f172a; padding: 16px 24px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        h1 { margin: 0; font-size: 1.25rem; font-weight: 600; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .badge { background: #065f46; color: #34d399; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
        .badge::before { content: ""; width: 8px; height: 8px; background: #10b981; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }
        .content { padding: 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .viewport { grid-column: span 2; background: #020617; border-radius: 8px; height: 300px; border: 1px solid #1e293b; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .viewport-grid { position: absolute; inset: 0; background-image: radial-gradient(#334155 1px, transparent 1px); background-size: 24px 24px; opacity: 0.3; }
        .viewport-overlay { position: absolute; top: 12px; left: 16px; font-family: monospace; font-size: 0.85rem; color: #f8fafc; text-shadow: 0 1px 3px black; }
        .viewport-rec { position: absolute; top: 12px; right: 16px; color: #ef4444; font-family: monospace; font-weight: bold; font-size: 0.85rem; display: flex; align-items: center; gap: 6px; }
        .viewport-rec::before { content: ""; width: 10px; height: 10px; background: #ef4444; border-radius: 50%; }
        .viewport-center { text-align: center; color: #64748b; z-index: 1; }
        .viewport-center svg { width: 48px; height: 48px; margin-bottom: 8px; fill: #475569; }
        .card { background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; }
        .card h3 { margin-top: 0; font-size: 0.95rem; color: #94a3b8; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }
        .row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 8px; }
        .label { color: #64748b; }
        .val { font-family: monospace; color: #e2e8f0; font-weight: 500; }
        .footer { background: #0f172a; padding: 12px 24px; border-top: 1px solid #334155; font-size: 0.75rem; color: #64748b; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Lab IP camera</h1>
            <span class="badge">RECORDING / STREAMING</span>
        </div>
        <div class="content">
            <div class="viewport">
                <div class="viewport-grid"></div>
                <div class="viewport-overlay">CH01 - LAB ENVIRONMENT &bull; RTSP 1080P</div>
                <div class="viewport-rec">REC</div>
                <div class="viewport-center">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>
                    <div>LIVE RTSP STREAM ACTIVE (PORT 554)</div>
                    <div style="font-size:0.75rem; color:#475569; margin-top:4px;">Transmitting ~200 KB/s to NVR</div>
                </div>
            </div>
            <div class="card">
                <h3>Camera Properties</h3>
                <div class="row"><span class="label">IP Address:</span><span class="val">192.168.50.30</span></div>
                <div class="row"><span class="label">Status:</span><span class="val">status: recording</span></div>
                <div class="row"><span class="label">Subnet Mask:</span><span class="val">255.255.255.0</span></div>
                <div class="row"><span class="label">Default Gateway:</span><span class="val">192.168.50.1 (ids-lab-router)</span></div>
                <div class="row"><span class="label">Firmware:</span><span class="val">v2.14-USJ-SEC</span></div>
            </div>
            <div class="card">
                <h3>Live Streaming Feeds</h3>
                <div class="row"><span class="label">RTSP Stream:</span><span class="val">rtsp://192.168.50.30:554/ch0</span></div>
                <div class="row"><span class="label">Resolution / FPS:</span><span class="val">1920x1080 @ 25 fps</span></div>
                <div class="row"><span class="label">Connected NVR:</span><span class="val">192.168.50.20 (58.6 MB / 5m)</span></div>
                <div class="row"><span class="label">Cloud Heartbeat:</span><span class="val">10.10.10.123 (Port 443)</span></div>
                <div class="row"><span class="label">Security Sensor:</span><span class="val">Zeek Sniffing br-ids-lan</span></div>
            </div>
        </div>
        <div class="footer">
            Real-Time Intrusion Detection and Autonomous Response System for IP Cameras &bull; Group 03 USJ
        </div>
    </div>
</body>
</html>
"""


class CameraWeb(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = (CAMERA_HTML if self.path in ("/", "/index.html") else b'{"status":"ok"}')
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
            first = self.request.recv(1024)  # the client's request line
            if not first.startswith(b"PLAY"):
                # Like a real camera: answer other RTSP requests (an NVR's or Nmap's OPTIONS) with a
                # short RTSP reply, and stream video only after PLAY. Before 11 Nov 2026 any first
                # message started the endless stream, so Nmap version detection hung on port 554.
                cseq = b"1"
                for line in first.split(b"\r\n"):
                    if line.lower().startswith(b"cseq:"):
                        cseq = line.split(b":", 1)[1].strip() or b"1"
                if first.startswith((b"OPTIONS", b"DESCRIBE", b"SETUP")):
                    reply = (b"RTSP/1.0 200 OK\r\nCSeq: " + cseq + b"\r\nServer: Lab IP camera RTSP\r\n"
                             b"Public: OPTIONS, DESCRIBE, SETUP, PLAY, TEARDOWN\r\n\r\n")
                else:
                    reply = b"RTSP/1.0 400 Bad Request\r\nCSeq: " + cseq + b"\r\nServer: Lab IP camera RTSP\r\n\r\n"
                self.request.sendall(reply)
                return
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
