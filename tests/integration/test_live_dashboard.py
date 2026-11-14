"""tests/integration/test_live_dashboard.py - Live dashboard data (FR-04, proposal 3.6) found in the
requirement check of 11 Nov 2026.

A real server (Flask-SocketIO, threading mode) runs on a free local port. tools/lab_common.SocketWatcher
connects to it like a logged-in dashboard tab, so these tests check what a browser really receives.
"""

import os
import socket
import threading
import time

import pytest
from pymongo import MongoClient

from core_engine.auth import AuthManager
from core_engine.db_service import DatabaseService
from tools.lab_common import Api, SocketWatcher

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
TEST_DB_NAME = "iot_ids_test_live"
SECRET = "test_secret_live_dashboard_2026"


def _mongo_up() -> bool:
    try:
        c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        c.admin.command("ping")
        c.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _mongo_up(), reason="MongoDB not reachable on localhost:27017")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    build = tmp_path_factory.mktemp("build")
    (build / "index.html").write_text("<!doctype html><title>IDS dashboard</title>", encoding="utf-8")
    (build / "static").mkdir()
    (build / "static" / "app.js").write_text("console.log('ok');", encoding="utf-8")
    os.environ["DASHBOARD_BUILD_DIR"] = str(build)
    from core_engine.app import create_app, start_summary_push

    db = DatabaseService(uri=MONGO_URI, db_name=TEST_DB_NAME)
    db.drop_database_for_testing()
    db.connect()
    auth = AuthManager(db_service=db, secret_key=SECRET, token_expiry_hours=1)
    db.create_user("admin_user", AuthManager.hash_password("AdminPass1234!"), role="admin")
    app, sio = create_app(db_service=db, auth_manager=auth,
                          test_config={"TESTING": True, "reconcile_on_startup": False})
    port = _free_port()
    t = threading.Thread(target=lambda: sio.run(app, host="127.0.0.1", port=port, allow_unsafe_werkzeug=True,
                                                use_reloader=False, log_output=False), daemon=True)
    t.start()
    api = Api(f"http://127.0.0.1:{port}")
    for _ in range(50):
        if api.up():
            break
        time.sleep(0.2)
    start_summary_push(app, sio, every_seconds=0.5)
    api.login("admin_user", "AdminPass1234!")
    yield {"api": api, "base": f"http://127.0.0.1:{port}", "db": db}
    os.environ.pop("DASHBOARD_BUILD_DIR", None)
    db.drop_database_for_testing()
    db.close()


def test_summary_has_measured_system_values(server):
    code, s = server["api"].call("GET", "/api/summary")
    assert code == 200
    assert {"total_incidents", "active_blocks", "active_rate_limits", "benign_flows_24h"} <= set(s["metrics"])
    sysinfo = s["system"]
    assert sysinfo["pipeline_status"] in ("stopped", "running", "error")
    assert sysinfo["model_version"].startswith("v3.")
    # model throughput is the saved benchmark capacity (flows/s), surfaced for the dashboard
    assert "model_throughput_fps" in sysinfo
    assert sysinfo["model_throughput_fps"] is None or sysinfo["model_throughput_fps"] > 0
    assert isinstance(sysinfo["auto_response"], bool) and sysinfo["allowlist_size"] >= 1


def test_dashboard_tab_gets_summary_pushes_without_refresh(server):
    w = SocketWatcher(server["base"], server["api"].token)
    assert w.start(), f"refused: {w.refused}"
    # the summary changes when a benign flow is counted; the push must follow without any refresh
    from datetime import datetime, timezone
    server["db"].record_traffic_summary(minute=datetime.now(timezone.utc), class_name="Benign", count=3)
    deadline = time.time() + 8
    while time.time() < deadline and not w.received("summary_update"):
        time.sleep(0.2)
    w.stop()
    got = w.received("summary_update")
    assert got, "no summary_update message reached the dashboard client"
    assert "metrics" in got[-1][2] and "system" in got[-1][2]


def test_socket_without_login_is_refused(server):
    w = SocketWatcher(server["base"], "not-a-valid-token")
    assert not w.start(wait=3)
    w.stop()


def test_log_export_is_announced_live(server):
    w = SocketWatcher(server["base"], server["api"].token)
    assert w.start()
    code, body = server["api"].call("GET", "/api/logs/export?type=events&format=csv", raw=True)
    assert code == 200
    deadline = time.time() + 5
    while time.time() < deadline and not w.received("log_export"):
        time.sleep(0.2)
    w.stop()
    assert w.received("log_export"), "no log_export message"


def test_backend_serves_the_dashboard_pages(server):
    code, html = server["api"].call("GET", "/", raw=True)
    assert code == 200 and b"IDS dashboard" in html
    code, js = server["api"].call("GET", "/static/app.js", raw=True)
    assert code == 200 and b"console.log" in js
    code, page = server["api"].call("GET", "/alerts", raw=True)       # a React route
    assert code == 200 and b"IDS dashboard" in page
    code, err = server["api"].call("GET", "/api/no-such-endpoint")
    assert code == 404


def test_confirming_an_incident_is_audited(server):
    eid = server["db"].record_attack_event({"src_ip": "10.10.10.50", "dst_ip": "192.168.50.30", "predicted_class": "CnC",
                                            "confidence": 0.9, "model_version": "v3.1.0"})
    code, _ = server["api"].call("PATCH", f"/api/events/{eid}", body={"status": "confirmed", "reason": "checked pcap"})
    assert code == 200
    code, logs = server["api"].call("GET", "/api/logs?event=INCIDENT_STATUS_CHANGED")
    rec = [l for l in logs.get("logs", []) if (l.get("details") or {}).get("event_id") == eid]
    assert rec and rec[0]["actor"] == "admin_user"
