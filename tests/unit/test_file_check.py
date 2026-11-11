"""Tests for the file-type check on Zeek files.log (decision D-052, change 3)."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core_engine.file_check import REASON_CODE, FileCheck, FilesLogFollower, sender_receiver  # noqa: E402

LAN = ["192.168.50.0/24"]
ALLOW = ["192.168.50.1", "192.168.50.10"]


class FakeDB:
    def __init__(self):
        self.events = []

    def record_attack_event(self, event, aggregate_window_seconds=None):
        self.events.append(event)
        return f"e{len(self.events)}"


class FakeSocket:
    def __init__(self):
        self.sent = []

    def emit(self, name, payload):
        self.sent.append((name, payload))


def zeek6(mime, sender="10.10.10.60", receiver="192.168.50.30", filename=None, size=104000):
    """files.log record as written by Zeek >= 5 (connection ids; is_orig False = sent by the server)."""
    rec = {"ts": 1700000000.0, "fuid": "F1", "uid": "C1", "id.orig_h": receiver, "id.orig_p": 40000,
           "id.resp_h": sender, "id.resp_p": 80, "source": "HTTP", "is_orig": False,
           "mime_type": mime, "seen_bytes": size, "total_bytes": size}
    if filename:
        rec["filename"] = filename
    return rec


def test_program_download_from_outside_raises_alert():
    db, sock = FakeDB(), FakeSocket()
    fc = FileCheck(LAN, ALLOW, db=db, socketio=sock)
    alert = fc.handle(zeek6("application/x-executable"))
    assert alert["predicted_class"] == "Malware_Download"
    assert alert["reason_code"] == REASON_CODE and alert["model_version"] == "rule:files.log"
    assert alert["src_ip"] == "10.10.10.60" and alert["dst_ip"] == "192.168.50.30"
    assert alert["src_port"] == 80 and alert["dst_port"] == 40000
    assert alert["response_status"] == "none"       # alert only, never a block
    assert len(db.events) == 1 and sock.sent[0][0] == "new_event"


def test_script_types_and_script_name():
    fc = FileCheck(LAN, ALLOW)
    assert fc.check(zeek6("text/x-shellscript")) is not None
    assert fc.check(zeek6("text/plain", filename="bins.sh")) is not None


def test_no_alert_for_normal_files_local_senders_allowlist_or_outbound():
    fc = FileCheck(LAN, ALLOW)
    assert fc.check(zeek6("image/jpeg")) is None                                    # not a program
    assert fc.check(zeek6("application/x-executable", sender="192.168.50.20")) is None  # local sender
    assert fc.check(zeek6("application/x-executable", sender="192.168.50.1")) is None   # allowlisted
    assert fc.check(zeek6("application/x-executable", receiver="10.10.10.70")) is None  # not to the LAN
    up = zeek6("application/x-executable")
    up["is_orig"] = True   # the camera SENT the file (upload): receiver is outside
    assert fc.check(up) is None


def test_old_zeek_format_tx_rx_hosts():
    rec = {"tx_hosts": ["10.10.10.60"], "rx_hosts": ["192.168.50.30"], "mime_type": "application/x-dosexec"}
    assert sender_receiver(rec) == ("10.10.10.60", "192.168.50.30")
    assert FileCheck(LAN, ALLOW).check(rec) is not None


def test_follower_reads_complete_lines_and_restarts_after_truncation(tmp_path):
    db = FakeDB()
    log = tmp_path / "files.log"
    fol = FilesLogFollower(log, FileCheck(LAN, ALLOW, db=db))
    assert fol.poll_once() == 0                                     # no file yet
    log.write_text(json.dumps(zeek6("application/x-executable")) + "\n"
                   + json.dumps(zeek6("image/png")) + "\n" + '{"partial": ', encoding="utf-8")
    assert fol.poll_once() == 2 and len(db.events) == 1             # the partial line waits
    with log.open("a", encoding="utf-8") as f:
        f.write('1}\n')
    assert fol.poll_once() == 1
    log.write_text(json.dumps(zeek6("text/x-shellscript")) + "\n", encoding="utf-8")  # file replaced
    assert fol.poll_once() == 1 and len(db.events) == 2
