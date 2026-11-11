"""
core_engine/file_check.py - File-type check on Zeek's files.log (decision D-052, change 3).

Why: IoT-23 has too few file downloads (67 malicious, 36 benign of the same shape) for the model
to learn them reliably. Zeek's files.log gives direct evidence: the type of each file it saw in
HTTP/FTP traffic. Infected IoT devices download Linux programs or shell scripts; a camera normally
does not.

Rule (fixed in D-052 before any test):
  A LOCAL device receives a file whose type is a program or a script, from a NON-LOCAL address
  that is not on the allowlist  ->  Malware_Download alert, reason RULE_EXECUTABLE_DOWNLOAD.
  It never blocks automatically (Malware_Download is alert only, D-046).

This is a rule, not the model. Its alerts carry model_version "rule:files.log" so they are
reported apart from the model scores. IoT-23 has no files.log, so the rule is tested with unit
tests and in the lab (proposal Table 10, scenario 5).
"""

from __future__ import annotations

import ipaddress
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger("core_engine.file_check")

# File types that are programs or scripts (Zeek / libmagic names).
PROGRAM_MIME_TYPES = frozenset({
    "application/x-executable",
    "application/x-elf",
    "application/x-sharedlib",
    "application/x-pie-executable",
    "application/x-object",
    "application/x-mach-o-executable",
    "application/x-dosexec",
    "application/x-msdownload",
    "application/x-sh",
    "application/x-shellscript",
    "text/x-shellscript",
    "text/x-sh",
})
SCRIPT_SUFFIXES = (".sh",)  # a script that Zeek typed as plain text, named like a script

REASON_CODE = "RULE_EXECUTABLE_DOWNLOAD"
MODEL_VERSION = "rule:files.log"


def _networks(cidrs: Iterable[str]) -> List[ipaddress._BaseNetwork]:
    out = []
    for c in cidrs or []:
        try:
            out.append(ipaddress.ip_network(str(c), strict=False))
        except ValueError:
            logger.warning("Ignoring bad network %r", c)
    return out


def _first(v: Any) -> Optional[str]:
    if isinstance(v, (list, tuple, set)):
        v = next(iter(v), None)
    return str(v) if v not in (None, "", "-") else None


def sender_receiver(rec: Dict[str, Any]) -> tuple:
    """(sender, receiver) of the file. Zeek >= 5 writes the connection ids and `is_orig`
    (True = the file was sent by the connection's originator); older Zeek writes tx_hosts/rx_hosts."""
    orig = rec.get("id.orig_h")
    resp = rec.get("id.resp_h")
    if isinstance(rec.get("id"), dict):
        orig = orig or rec["id"].get("orig_h")
        resp = resp or rec["id"].get("resp_h")
    if orig and resp and "is_orig" in rec:
        return (str(orig), str(resp)) if rec.get("is_orig") else (str(resp), str(orig))
    return _first(rec.get("tx_hosts")), _first(rec.get("rx_hosts"))


class FileCheck:
    """Applies the D-052 rule to files.log records and saves/sends the alerts."""

    def __init__(self, local_networks: Iterable[str], allowlist: Iterable[str] = (),
                 db: Any = None, socketio: Any = None, repeat_window_seconds: int = 60) -> None:
        self.local = _networks(local_networks)
        self.allowlist = {str(a) for a in allowlist or []}
        self.db = db
        self.socketio = socketio
        self.repeat_window_seconds = repeat_window_seconds
        self.metrics = {"files_seen": 0, "alerts": 0}

    def is_local(self, ip: Optional[str]) -> bool:
        try:
            a = ipaddress.ip_address(str(ip))
        except ValueError:
            return False
        return any(a in n for n in self.local)

    @staticmethod
    def is_program(rec: Dict[str, Any]) -> bool:
        mime = str(rec.get("mime_type") or "").lower()
        name = str(rec.get("filename") or "").lower()
        return mime in PROGRAM_MIME_TYPES or name.endswith(SCRIPT_SUFFIXES)

    def check(self, rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return the alert payload if the rule fires for this files.log record, else None."""
        self.metrics["files_seen"] += 1
        if not self.is_program(rec):
            return None
        sender, receiver = sender_receiver(rec)
        if not sender or not receiver:
            return None
        if not self.is_local(receiver) or self.is_local(sender) or sender in self.allowlist:
            return None
        mime = rec.get("mime_type") or "-"
        name = rec.get("filename") or "-"
        size = rec.get("seen_bytes") or rec.get("total_bytes") or 0
        proto = str(rec.get("source") or "").lower() or "-"
        note = (f"File-type check: {receiver} downloaded a program/script file "
                f"(type {mime}, name {name}, {size} bytes, over {proto}) from {sender}. "
                f"Rule on Zeek files.log, not the model (D-052); alert only.")
        return {
            "src_ip": sender,
            "src_port": rec.get("id.resp_p") if rec.get("is_orig") is False else rec.get("id.orig_p"),
            "dst_ip": receiver,
            "dst_port": rec.get("id.orig_p") if rec.get("is_orig") is False else rec.get("id.resp_p"),
            "proto": "tcp",
            "service": proto,
            "conn_state": "-",
            "direction": "inbound",
            "traffic_direction": "inbound",
            "predicted_class": "Malware_Download",
            "confidence": 1.0,
            "probabilities": {},
            "model_version": MODEL_VERSION,
            "evidence_note": note,
            "reason_code": REASON_CODE,
            "severity": "high",
            "status": "prediction",
            "response_status": "none",
            "is_allowlisted": receiver in self.allowlist,
            "flow_features": {},
            "features": {},
            "file": {k: rec.get(k) for k in ("fuid", "uid", "mime_type", "filename", "seen_bytes",
                                              "total_bytes", "md5", "sha1", "sha256", "source")},
            "timestamps": {"zeek_ts": rec.get("ts"), "decision_ts": time.time()},
        }

    def handle(self, rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check one record; save and send the alert if the rule fires."""
        alert = self.check(rec)
        if alert is None:
            return None
        self.metrics["alerts"] += 1
        logger.warning("RULE_EXECUTABLE_DOWNLOAD: %s", alert["evidence_note"])
        if self.db is not None:
            try:
                eid = self.db.record_attack_event(alert, aggregate_window_seconds=self.repeat_window_seconds)
                alert["event_id"] = str(eid) if eid else None
            except Exception as e:  # never stop the pipeline because of one record
                logger.error("Failed to save file-type alert: %s", e)
        if self.socketio is not None:
            try:
                self.socketio.emit("new_event", {k: v for k, v in alert.items() if k != "file"})
            except Exception as e:
                logger.error("Failed to send file-type alert: %s", e)
        return alert

    def handle_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line or line.startswith("#"):
            return None
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            return None
        return self.handle(rec) if isinstance(rec, dict) else None


class FilesLogFollower:
    """Follows files.log (JSON lines) in a background thread and passes each line to FileCheck.

    The reading place is saved in `state_path` (with the file's inode), so a restart of the backend
    continues where it stopped and does not raise the old alerts again (found 11 Nov 2026, D-056).
    Without a saved place it starts at the beginning. If the file becomes shorter or is a new file
    (Zeek restarted), it starts again from the beginning."""

    def __init__(self, path: Path, check: FileCheck, poll_seconds: float = 0.5,
                 state_path: Optional[Path] = None) -> None:
        self.path = Path(path)
        self.check = check
        self.poll_seconds = poll_seconds
        self.state_path = Path(state_path) if state_path else None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._offset = 0
        self._load_state()

    def _inode(self) -> int:
        try:
            return int(getattr(self.path.stat(), "st_ino", 0) or 0)
        except OSError:
            return 0

    def _load_state(self) -> None:
        if not self.state_path or not self.state_path.exists():
            return
        try:
            st = json.loads(self.state_path.read_text(encoding="utf-8"))
            size = self.path.stat().st_size if self.path.exists() else 0
            same = st.get("path") == str(self.path) and (not st.get("inode") or st.get("inode") == self._inode())
            if same and 0 <= int(st.get("offset", 0)) <= size:
                self._offset = int(st["offset"])
                logger.info("files.log: resuming at byte %d", self._offset)
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("files.log state not used: %s", exc)

    def _save_state(self) -> None:
        if not self.state_path:
            return
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"path": str(self.path), "inode": self._inode(), "offset": self._offset}),
                           encoding="utf-8")
            os.replace(tmp, self.state_path)
        except OSError as exc:
            logger.warning("Could not save the files.log place: %s", exc)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="FilesLogFollower", daemon=True)
        self._thread.start()
        logger.info("File-type check following %s", self.path)

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def poll_once(self) -> int:
        """Read the new complete lines; return how many were read."""
        if not self.path.exists():
            return 0
        size = self.path.stat().st_size
        if size < self._offset:
            self._offset = 0
        if size == self._offset:
            return 0
        n = 0
        with self.path.open("rb") as f:
            f.seek(self._offset)
            data = f.read(size - self._offset)
        end = data.rfind(b"\n")
        if end < 0:
            return 0  # no complete line yet
        for raw in data[: end + 1].splitlines():
            self.check.handle_line(raw.decode("utf-8", errors="replace"))
            n += 1
        self._offset += end + 1
        self._save_state()
        return n

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.poll_once()
            except Exception as e:
                logger.error("files.log follower error: %s", e)
            self._stop.wait(self.poll_seconds)
