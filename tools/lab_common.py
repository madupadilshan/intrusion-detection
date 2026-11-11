#!/usr/bin/env python3
"""
tools/lab_common.py - Shared helpers for the lab tools (virtual lab and hardware lab).

Used by lab_virtual/lab.py, lab_hardware/hwlab.py, tools/fr_tests.py and tools/measure_latency.py.
Only the Python standard library is used, so nothing extra must be installed on the sensor.

- Api: log in to the IDS backend and call its REST API.
- SocketWatcher: a small Socket.IO client (Engine.IO v4 long-polling, like a dashboard tab),
  logged in with the same token. It records every pushed message with the time it arrived.
  Used to measure "prediction -> dashboard" (proposal Table 9, RQ4) and to check FR-04.
- nft_sets(): read the block_src / block_dst / limit_src sets from `nft -j list table ...` output.
- group_events(), scenario_report(): the Markdown report of one Table 10 scenario run.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SETS = ("block_src", "block_dst", "limit_src")


# ----------------------------------------------------------------------------- REST API
class Api:
    """Small REST client for the IDS backend (core_engine/app.py)."""

    def __init__(self, base: str = "http://127.0.0.1:5000", timeout: float = 10.0) -> None:
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.token: Optional[str] = None

    def call(self, method: str, path: str, body: Any = None, timeout: Optional[float] = None,
             raw: bool = False) -> Tuple[int, Any]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base + path, method=method, headers=headers,
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                data = r.read()
                return r.status, (data if raw else json.loads(data or b"{}"))
        except urllib.error.HTTPError as e:
            data = e.read()
            try:
                return e.code, json.loads(data or b"{}")
            except ValueError:
                return e.code, {"raw": data[:300].decode("utf-8", "replace")}

    def up(self) -> bool:
        try:
            code, _ = self.call("GET", "/api/health", timeout=3)
            return code == 200
        except (urllib.error.URLError, ConnectionError, OSError):
            return False

    def login(self, user: str, password: str) -> str:
        code, data = self.call("POST", "/api/auth/login", body={"username": user, "password": password})
        tok = data.get("token") or data.get("access_token")
        if code != 200 or not tok:
            raise RuntimeError(f"login failed ({code}): {data}")
        self.token = tok
        return tok


def read_login(path: Path) -> Tuple[str, str]:
    """A login file holds 'user password' on one line (lab files, not in Git)."""
    user, pw = path.read_text(encoding="utf-8").split()[:2]
    return user, pw


# ----------------------------------------------------------------------------- Socket.IO
class SocketWatcher:
    """Socket.IO client over Engine.IO v4 long-polling (standard library only).

    It connects to the default namespace with {"token": ...} (the same check the dashboard
    passes), then records (arrival_time, event_name, data) for every pushed message.
    """

    def __init__(self, base: str, token: str, timeout: float = 30.0) -> None:
        self.base = base.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.sid: Optional[str] = None
        self.events: List[Tuple[float, str, Any]] = []
        self.connected = threading.Event()
        self.refused: Optional[str] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def _url(self) -> str:
        q = {"EIO": "4", "transport": "polling", "t": str(time.time())}
        if self.sid:
            q["sid"] = self.sid
        return f"{self.base}/socket.io/?{urllib.parse.urlencode(q)}"

    def _get(self) -> str:
        with urllib.request.urlopen(self._url(), timeout=self.timeout) as r:
            return r.read().decode("utf-8", "replace")

    def _post(self, payload: str) -> None:
        req = urllib.request.Request(self._url(), data=payload.encode(), method="POST",
                                     headers={"Content-Type": "text/plain;charset=UTF-8"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            r.read()

    def start(self, wait: float = 10.0) -> bool:
        first = self._get()
        if not first.startswith("0"):
            raise RuntimeError(f"unexpected Engine.IO open packet: {first[:80]}")
        self.sid = json.loads(first[1:])["sid"]
        self._post("40" + json.dumps({"token": self.token}))
        self._thread = threading.Thread(target=self._loop, name="SocketWatcher", daemon=True)
        self._thread.start()
        self.connected.wait(wait)
        return self.connected.is_set()

    def _handle(self, packet: str, now: float) -> None:
        if packet == "2":            # ping -> pong
            self._post("3")
        elif packet.startswith("40"):
            self.connected.set()
        elif packet.startswith("44"):  # connect refused
            self.refused = packet[2:]
            self._stop.set()
        elif packet.startswith("42"):
            try:
                msg = json.loads(packet[2:])
                with self._lock:
                    self.events.append((now, msg[0], msg[1] if len(msg) > 1 else None))
            except (ValueError, IndexError):
                pass
        elif packet.startswith("1"):  # close
            self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                body = self._get()
            except Exception:
                if self._stop.is_set():
                    break
                time.sleep(0.5)
                continue
            now = time.time()
            for packet in body.split("\x1e"):
                if packet:
                    self._handle(packet, now)

    def stop(self) -> None:
        self._stop.set()
        try:
            self._post("1")
        except Exception:
            pass

    def received(self, name: Optional[str] = None) -> List[Tuple[float, str, Any]]:
        with self._lock:
            return [e for e in self.events if name is None or e[1] == name]


# ----------------------------------------------------------------------------- nftables
def nft_sets(nft_json_text: str) -> Dict[str, List[str]]:
    """block_src / block_dst / limit_src elements from `nft -j list table <family> ids`."""
    sets: Dict[str, List[str]] = {}
    try:
        for item in json.loads(nft_json_text).get("nftables", []):
            s = item.get("set")
            if s and s.get("name") in SETS:
                elems = []
                for e in s.get("elem", []) or []:
                    if isinstance(e, dict):
                        v = e.get("elem", {}).get("val")
                        t = e.get("elem", {}).get("expires")
                        elems.append(f"{v}" + (f" (ends in {t}s)" if t else ""))
                    else:
                        elems.append(str(e))
                sets[s["name"]] = elems
    except (ValueError, AttributeError):
        sets["error"] = [nft_json_text.strip()[:300]]
    return sets


def ip_in_sets(ip: str, sets: Dict[str, List[str]], names: Iterable[str] = SETS) -> List[str]:
    return [n for n in names if any(str(v).split(" ")[0] == ip for v in sets.get(n, []))]


# ----------------------------------------------------------------------------- reports
def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def events_since(api: Api, start: datetime, limit: int = 1000) -> List[Dict[str, Any]]:
    code, ev = api.call("GET", f"/api/events?limit={limit}")
    stamp = start.isoformat()[:19]
    return [e for e in ev.get("events", []) if str(e.get("created_at", ""))[:19] >= stamp]


def group_events(events: List[Dict[str, Any]]) -> Dict[Tuple, Dict[str, Any]]:
    by: Dict[Tuple, Dict[str, Any]] = {}
    for e in events:
        k = (e.get("predicted_class"), e.get("src_ip"), e.get("dst_ip"), e.get("reason_code"),
             e.get("response_status"))
        b = by.setdefault(k, {"events": 0, "flows": 0, "max_conf": 0.0})
        b["events"] += 1
        b["flows"] += int(e.get("flow_count") or 1)
        b["max_conf"] = max(b["max_conf"], float(e.get("confidence") or 0))
    return by


def scenario_report(*, path: Path, title: str, where: str, start: datetime, end: datetime, how: str,
                    expect: str, safe: str, model: str, flows: Optional[int], events: List[Dict[str, Any]],
                    blocks: List[Dict[str, Any]], fw_sets: Dict[str, List[str]], protected: Dict[str, str],
                    checks: List[Tuple[str, str]], notes: List[str]) -> str:
    """Write the Markdown report of one scenario run and return its text.

    protected: {ip: name} of devices that must never be blocked (camera, NVR, admin PC, ...).
    checks: (question, answer) pairs, e.g. the Table 10 safe-result checks.
    """
    by = group_events(events)
    md = [f"# {title}", "",
          f"- **When (UTC):** {start:%Y-%m-%d %H:%M:%S} to {end:%H:%M:%S}",
          f"- **Where:** {where}",
          f"- **How:** {how}", f"- **Expected (written before):** {expect}", f"- **Safe result needed:** {safe}",
          f"- **Model:** {model}" + (f"; Zeek flows during the run: {flows:,}" if flows is not None else ""),
          "", "## What the system did", "",
          "| Class | Source | Destination | Reason | Response | Events | Flows | Max confidence |",
          "| --- | --- | --- | --- | --- | ---: | ---: | ---: |"]
    for (c, s, d, r, rs), b in sorted(by.items(), key=lambda x: -x[1]["flows"]):
        md.append(f"| {c} | {s} | {d} | {r} | {rs} | {b['events']} | {b['flows']} | {b['max_conf']:.2f} |")
    if not by:
        md.append("| (no alerts) | | | | | | | |")
    wrong = []
    for ip, name in protected.items():
        in_db = any(b.get("ip") == ip for b in blocks)
        in_fw = ip_in_sets(ip, fw_sets)
        if in_db or in_fw:
            wrong.append(f"{name} {ip}")
    md += ["", "## Blocks and rate-limits", "",
           "- IDS blocklist (database): "
           + (", ".join(f"{b['ip']} ({b.get('action', 'block')}, {b.get('direction')}, {b.get('reason')})"
                        for b in blocks) or "none"),
           f"- Firewall sets (what is really enforced): {fw_sets}",
           "- Protected devices blocked: " + ("**YES - WRONG: " + ", ".join(wrong) + "**" if wrong
                                              else "none (correct)"),
           "", "## Checks of the safe result (Table 10)", ""]
    md += [f"- {q}: **{a}**" for q, a in checks] or ["- (none)"]
    md += ["", "## Notes", ""] + [f"```\n{x}\n```" for x in notes]
    text = "\n".join(md) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text
