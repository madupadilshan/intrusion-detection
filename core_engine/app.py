"""
Unified Flask + Socket.IO Backend Server for IoT Intrusion Detection and Response System.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Group 03 Proposal:
- Section 3.6 (System Architecture, Figure 2, Single Server Architecture on Port 5000)
- Table 7 (FR-01, FR-03, FR-04: Real-Time Socket.IO Telemetry, FR-05, FR-06, FR-07, FR-08: Log Export)
- Decision D-029 (Consolidated Flask + Socket.IO server, RBAC, authenticated WebSocket streams)
"""

import os
import sys
import csv
import io
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

from flask import Flask, request, jsonify, g, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_engine.db_service import DatabaseService, _load_settings
from core_engine.file_check import FileCheck
from core_engine.auth import (
    AuthManager,
    AuthError,
    InvalidCredentialsError,
    TokenMissingError,
    TokenExpiredError,
    InvalidTokenError,
    PermissionDeniedError,
)
from core_engine.scanner_service import ScannerService, UnauthorizedSubnetError
from core_engine.export_service import ExportService
from core_engine.firewall import (
    get_firewall_adapter,
    firewall_config_from_settings,
    BaseFirewallAdapter,
    AllowlistImmunityError,
)
from core_engine.detector import Detector
from core_engine.decision_engine import DecisionEngine
from core_engine.zeek_adapter import ZeekAdapter
from core_engine.runner import LivePipelineRunner
from core_engine.rule_worker import (
    RuleExpiryWorker,
    reconcile_on_startup,
    sweep_expired_rules,
)

load_dotenv()
logger = logging.getLogger("ids_app")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]


def _project_path(value):
    """A settings path; a relative path starts at the project folder. None stays None."""
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else PROJECT_ROOT / p


def create_app(
    db_service: Optional[DatabaseService] = None,
    auth_manager: Optional[AuthManager] = None,
    scanner_service: Optional[Any] = None,
    export_service: Optional[Any] = None,
    firewall_adapter: Optional[BaseFirewallAdapter] = None,
    detector: Optional[Detector] = None,
    decision_engine: Optional[DecisionEngine] = None,
    zeek_adapter: Optional[ZeekAdapter] = None,
    pipeline_runner: Optional[LivePipelineRunner] = None,
    rule_worker: Optional[RuleExpiryWorker] = None,
    test_config: Optional[Dict[str, Any]] = None,
) -> Tuple[Flask, SocketIO]:
    """
    Application factory for the IoT IDS Flask + Socket.IO server.
    Consolidates the 5 legacy backend ports into one unified, authenticated service.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "ids_flask_secret_key_default_2026")
    app.config["JSON_SORT_KEYS"] = False

    if test_config:
        app.config.update(test_config)

    # CORS Configuration
    env_origins = os.getenv("CORS_ORIGINS", "")
    allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()] or DEFAULT_CORS_ORIGINS
    CORS(app, origins=allowed_origins, supports_credentials=True)

    # SocketIO Initialization
    socketio = SocketIO(
        app,
        cors_allowed_origins=allowed_origins,
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )

    # Bind Services
    db = db_service or DatabaseService()
    auth = auth_manager or AuthManager(db_service=db)
    app.config["db"] = db
    app.config["auth"] = auth
    app.config["socketio"] = socketio

    # Load Lab Safety Settings
    settings_cfg = _load_settings()
    approved_subnets = settings_cfg.get("lab", {}).get("approved_scan_subnets", ["192.168.50.0/24"])
    management_allowlist = set(settings_cfg.get("allowlist", [
        "192.168.50.1", "192.168.50.5", "192.168.50.10", "192.168.50.20"
    ]))

    scanner = scanner_service or ScannerService(
        db_service=db,
        socketio=socketio,
        approved_subnets=approved_subnets,
    )
    app.config["scanner"] = scanner

    exporter = export_service or ExportService(db_service=db)
    app.config["exporter"] = exporter

    # Firewall Response Adapter (Step 33, Problem 3 Fix)
    firewall_cfg = firewall_config_from_settings(settings_cfg)

    firewall = firewall_adapter or get_firewall_adapter(
        config=firewall_cfg,
        allowlist=management_allowlist,
        max_rule_minutes=int(settings_cfg.get("response", {}).get("max_rule_minutes", 60)),
    )
    app.config["firewall"] = firewall

    # Machine Learning Detector & Decision Engine (Step 26)
    settings_file = Path(os.getenv("IDS_SETTINGS_FILE") or PROJECT_ROOT / "config" / "settings.yaml")
    # settings.yaml model.bundle_path decides the model (relative paths start at the project folder)
    bundle_cfg = (settings_cfg.get("model", {}) or {}).get("bundle_path")
    bundle_file = None
    if bundle_cfg:
        bundle_file = Path(bundle_cfg) if Path(bundle_cfg).is_absolute() else PROJECT_ROOT / bundle_cfg
    detector_inst = detector or Detector(bundle_path=bundle_file)
    app.config["detector"] = detector_inst

    decision_inst = decision_engine or DecisionEngine(
        db_service=db,
        socketio=socketio,
        detector=detector_inst,
        firewall_adapter=firewall,
        settings_path=settings_file if settings_file.exists() else None,
    )
    app.config["decision_engine"] = decision_inst

    # Re-apply settings the administrator changed earlier from the dashboard (FR-07)
    if decision_engine is None:
        try:
            stored = {k: db.get_setting(k) for k in DecisionEngine.RUNTIME_SETTING_KEYS}
            decision_inst.apply_runtime_settings({k: v for k, v in stored.items() if v is not None})
        except Exception as exc:
            logger.warning("Could not apply stored runtime settings: %s", exc)

    # Live Pipeline Runner (Problem 1 Fix)
    zeek_inst = zeek_adapter or ZeekAdapter(
        settings_path=settings_file if settings_file.exists() else None
    )
    resp_cfg = settings_cfg.get("response", {}) or {}
    file_check_inst = FileCheck(
        local_networks=settings_cfg.get("lab", {}).get("local_networks", ["192.168.50.0/24"]),
        allowlist=management_allowlist,
        db=db,
        socketio=socketio,
        repeat_window_seconds=int(resp_cfg.get("repeat_window_seconds", 60)),
    )
    runner_inst = pipeline_runner or LivePipelineRunner(
        zeek_adapter=zeek_inst,
        decision_engine=decision_inst,
        socketio=socketio,
        file_check=file_check_inst,
        files_log_path=_project_path((settings_cfg.get("zeek", {}) or {}).get("files_log_path")),
    )
    app.config["zeek_adapter"] = zeek_inst
    app.config["runner"] = runner_inst

    # Step 34: Restart Recovery & Firewall Reconciliation
    should_reconcile = True
    if test_config and not test_config.get("reconcile_on_startup", True):
        should_reconcile = False

    reconcile_summary = None
    if should_reconcile:
        try:
            reconcile_summary = reconcile_on_startup(
                db=db,
                firewall=firewall,
                socketio=socketio,
                decision_engine=decision_inst,
            )
        except Exception as exc:
            logger.warning("Startup firewall reconciliation encountered error: %s", exc)
    app.config["startup_reconciliation"] = reconcile_summary

    # Background Rule Expiry Worker (Step 34)
    worker_inst = rule_worker or RuleExpiryWorker(
        db=db,
        firewall=firewall,
        socketio=socketio,
        decision_engine=decision_inst,
        interval_seconds=int(settings_cfg.get("response", {}).get("sweep_interval_seconds", 10)),
    )
    app.config["rule_worker"] = worker_inst
    if test_config and test_config.get("autostart_rule_worker", False):
        worker_inst.start()

    # =========================================================================
    # Error Handlers
    # =========================================================================

    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"error": "Not Found", "message": "The requested API endpoint was not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method Not Allowed", "message": str(e)}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

    # =========================================================================
    # 1. Authentication Endpoints (Proposal Section 3.6, FR-04)
    # =========================================================================

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """
        Authenticate user credentials and return a signed 8-hour JWT access token.
        Request body: {"username": "admin", "password": "..."}
        """
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        client_ip = request.remote_addr or "unknown"

        try:
            auth_res = auth.authenticate(username, password, client_ip=client_ip)
            return jsonify({
                "status": "success",
                "message": "Authentication successful.",
                **auth_res,
            }), 200
        except InvalidCredentialsError as e:
            return jsonify({"error": "Unauthorized", "message": str(e), "code": "INVALID_CREDENTIALS"}), 401
        except Exception as e:
            logger.warning(f"Login failed for {username}: {e}")
            return jsonify({"error": "Unauthorized", "message": str(e), "code": "AUTH_FAILED"}), 401

    @app.route("/api/auth/me", methods=["GET"])
    @auth.token_required
    def get_current_user(current_user):
        """Return the identity and role payload of the currently authenticated token."""
        return jsonify({
            "username": current_user.get("sub"),
            "role": current_user.get("role", "operator"),
            "issued_at": current_user.get("iat"),
            "expires_at": current_user.get("exp"),
        }), 200

    # =========================================================================
    # 2. System Summary & Metrics (FR-03, FR-04, Table 8)
    # =========================================================================

    @app.route("/api/summary", methods=["GET"])
    @auth.token_required
    def get_summary():
        """
        Aggregate overview metrics for the React Dashboard:
        - Total detected flows and incidents grouped by attack class
        - Total registered devices and active IP camera counts
        - Active firewall blocking rules count
        - Recent 24-hour traffic volumes
        """
        attack_stats = db.get_attack_stats()
        devices = db.get_devices(limit=500)
        camera_count = sum(1 for d in devices if d.get("possible_camera"))
        blocked_ips = db.get_blocked_ips(active_only=True)

        # 24-hour traffic summary
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        traffic_recent = db.get_traffic_summaries(start_time=since, limit=288)

        total_benign_flows = sum(t.get("flow_count", 0) for t in traffic_recent if t.get("class_name") == "Benign")

        return jsonify({
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_attack_flows": attack_stats.get("total_flows", 0),
                "total_incidents": attack_stats.get("total_incidents", 0),
                "active_blocks": len(blocked_ips),
                "total_devices": len(devices),
                "camera_devices": camera_count,
                "benign_flows_24h": total_benign_flows,
            },
            "class_distribution": attack_stats.get("classes", {}),
            "incidents_by_class": attack_stats.get("incidents_by_class", {}),
        }), 200

    # =========================================================================
    # 3. Attack Events & Forensic Evidence (FR-01, FR-02, FR-04, Table 8)
    # =========================================================================

    @app.route("/api/events", methods=["GET"])
    @auth.token_required
    def list_attack_events():
        """
        Query attack history with multi-attribute filtering:
        Query params: limit, class, status, response_status, start_time, end_time
        """
        limit = min(int(request.args.get("limit", 50)), 500)
        class_filter = request.args.get("class")
        status_filter = request.args.get("status")
        response_status_filter = request.args.get("response_status")

        start_time = None
        if request.args.get("start_time"):
            try:
                start_time = datetime.fromisoformat(request.args.get("start_time"))
            except ValueError:
                pass

        end_time = None
        if request.args.get("end_time"):
            try:
                end_time = datetime.fromisoformat(request.args.get("end_time"))
            except ValueError:
                pass

        events = db.get_attack_events(
            limit=limit,
            class_filter=class_filter,
            status_filter=status_filter,
            response_status_filter=response_status_filter,
            start_time=start_time,
            end_time=end_time,
        )
        return jsonify({"status": "success", "count": len(events), "events": events}), 200

    @app.route("/api/events/<event_id>", methods=["GET"])
    @auth.token_required
    def get_event_detail(event_id):
        """Retrieve full forensic evidence, features, and mitigation actions for an incident."""
        if not db.is_connected():
            return jsonify({"error": "Database unavailable"}), 503

        doc = db.attack_events.find_one({"event_id": event_id})
        if not doc:
            return jsonify({"error": "Not Found", "message": f"Event '{event_id}' not found."}), 404

        formatted = db._format_doc(doc, format_dates=True)
        # Fetch related mitigation actions
        actions = db.get_response_actions(event_id=event_id)
        formatted["mitigation_actions"] = actions

        return jsonify({"status": "success", "event": formatted}), 200

    @app.route("/api/events/<event_id>", methods=["PATCH"])
    @auth.admin_required
    def update_event_status(event_id):
        """
        Mark event as 'confirmed incident' or update mitigation status (Admin only).
        Request body: {"status": "confirmed", "response_status": "mitigated"}
        """
        data = request.get_json(silent=True) or {}
        new_status = data.get("status")
        new_resp_status = data.get("response_status")

        if not new_status and not new_resp_status:
            return jsonify({"error": "Bad Request", "message": "Provide 'status' or 'response_status' to update."}), 400

        success = db.update_attack_event_status(
            event_id=event_id,
            status=new_status,
            response_status=new_resp_status,
        )
        if not success:
            return jsonify({"error": "Not Found", "message": f"Incident '{event_id}' could not be updated."}), 404

        # Broadcast live update to Dashboard clients
        broadcast_payload = {
            "event_id": event_id,
            "status": new_status,
            "response_status": new_resp_status,
            "updated_by": getattr(g, "current_user", {}).get("sub", "admin"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        socketio.emit("event_update", broadcast_payload)

        return jsonify({"status": "success", "message": "Incident status updated.", "update": broadcast_payload}), 200

    # =========================================================================
    # 4. Device Inventory & Camera Discovery (FR-05, Section 3.7)
    # =========================================================================

    @app.route("/api/devices", methods=["GET"])
    @auth.token_required
    def list_devices():
        """
        List network devices discovered on the approved subnet.
        Query params: camera_only (bool), limit (int)
        """
        camera_only = request.args.get("camera_only", "false").lower() in ("true", "1", "yes")
        limit = min(int(request.args.get("limit", 200)), 500)

        devs = db.get_devices(camera_only=camera_only, limit=limit)
        return jsonify({"status": "success", "count": len(devs), "devices": devs}), 200

    @app.route("/api/devices/<ip>/confirm-camera", methods=["PATCH", "POST"])
    @auth.admin_required
    def confirm_camera(ip):
        """
        Confirm or revoke the IP camera classification for a discovered device (Proposal Section 3.7).
        Request body: {"confirmed": true, "notes": "Confirmed Dahua IP camera in lab"}
        """
        data = request.get_json(silent=True) or {}
        confirmed = data.get("confirmed", True)
        notes = data.get("notes", "")

        existing = db.get_device_by_ip(ip)
        if not existing:
            return jsonify({"error": "Not Found", "message": f"Device '{ip}' not found in registered devices."}), 404

        success = db.confirm_camera_role(ip=ip, confirmed=confirmed, notes=notes)
        if not success:
            return jsonify({"error": "Database error", "message": f"Failed to update camera status for {ip}."}), 500

        admin_user = getattr(g, "current_user", {}).get("sub", "admin")
        db.log_system_event(
            actor=admin_user,
            event="DEVICE_CAMERA_CONFIRMED" if confirmed else "DEVICE_CAMERA_REVOKED",
            outcome="success",
            details={"ip": ip, "confirmed": confirmed, "notes": notes},
        )

        updated_device = db.get_device_by_ip(ip)
        socketio.emit("device_update", updated_device)

        action_word = "confirmed" if confirmed else "revoked"
        return jsonify({
            "status": "success",
            "message": f"Device {ip} camera role {action_word} successfully.",
            "device": updated_device,
        }), 200

    # =========================================================================
    # 5. Device Discovery Scans (FR-05, Section 3.7)
    # =========================================================================

    @app.route("/api/scans", methods=["GET"])
    @auth.token_required
    def list_scans():
        """Retrieve recent authorized Nmap device discovery scans."""
        limit = min(int(request.args.get("limit", 20)), 100)
        scans = db.get_recent_scans(limit=limit)
        return jsonify({"status": "success", "count": len(scans), "scans": scans}), 200

    @app.route("/api/scans", methods=["POST"])
    @auth.admin_required
    def trigger_scan():
        """
        Initiate an authorized device discovery scan on approved subnet (Proposal Section 3.7).
        Request body: {"subnet": "192.168.50.0/24"}
        """
        data = request.get_json(silent=True) or {}
        subnet = (data.get("subnet") or "192.168.50.0/24").strip()

        # Enforce lab safety guardrail: Only approved subnets can be scanned
        try:
            scanner.validate_subnet(subnet)
        except UnauthorizedSubnetError as e:
            return jsonify({
                "error": "Forbidden",
                "message": f"Subnet '{subnet}' is not in approved scan subnets {approved_subnets} (Proposal Section 3.7).",
                "code": "UNAUTHORIZED_SUBNET",
            }), 403

        started_by = getattr(g, "current_user", {}).get("sub", "admin")
        scan_id = scanner.start_scan_async(subnet=subnet, started_by=started_by)
        if not scan_id:
            return jsonify({"error": "Failed to initiate scan record"}), 500

        # Broadcast scan started event to dashboard
        scan_payload = {
            "scan_id": scan_id,
            "subnet": subnet,
            "started_by": started_by,
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return jsonify({
            "status": "success",
            "message": f"Discovery scan on approved subnet '{subnet}' initiated.",
            "scan": scan_payload,
        }), 202

    @app.route("/api/scans/<scan_id>", methods=["GET"])
    @auth.token_required
    def get_scan_status(scan_id):
        """Retrieve execution progress and discovered devices for a scan."""
        if not db.is_connected():
            return jsonify({"error": "Database unavailable"}), 503

        doc = db.scans.find_one({"scan_id": scan_id})
        if not doc:
            return jsonify({"error": "Not Found", "message": f"Scan '{scan_id}' not found."}), 404

        return jsonify({"status": "success", "scan": db._format_doc(doc, format_dates=True)}), 200

    # =========================================================================
    # 6. Blocklist & Mitigation Rules (FR-06, FR-07)
    # =========================================================================

    @app.route("/api/blocklist", methods=["GET"])
    @auth.token_required
    def list_blocklist():
        """
        Retrieve active blocking rules or full audit history.
        Query params: active_only (bool), ip (str)
        """
        active_only = request.args.get("active_only", "true").lower() in ("true", "1", "yes")
        ip = request.args.get("ip")

        if ip:
            # Full audit history for specific IP
            history = db.get_block_history_for_ip(ip)
            return jsonify({"status": "success", "ip": ip, "count": len(history), "history": history}), 200

        blocks = db.get_blocked_ips(active_only=active_only)
        return jsonify({
            "status": "success",
            "count": len(blocks),
            "active_only": active_only,
            "adapter_mode": firewall.mode,
            "is_simulated": firewall.is_simulated,
            "blocks": blocks,
            "rules": blocks,
        }), 200

    @app.route("/api/blocklist", methods=["POST"])
    @auth.admin_required
    def add_block():
        """
        Manually enforce an IP block on the firewall/router (Admin only).
        Enforces management allowlist safety guardrail (Proposal Section 3.7, FR-07).
        Request body: {"ip": "10.0.0.45", "direction": "source", "reason": "...", "duration_minutes": 30}
        """
        data = request.get_json(silent=True) or {}
        ip = data.get("ip", "").strip()
        direction = data.get("direction", "source")
        reason = data.get("reason", "Manual administrator block")
        duration = data.get("duration_minutes") or data.get("minutes")

        if not ip:
            return jsonify({"error": "Bad Request", "message": "Target 'ip' must be specified."}), 400

        # Safety Guardrail: Never block management allowlist IPs
        if ip in management_allowlist:
            return jsonify({
                "error": "Forbidden",
                "message": f"IP '{ip}' belongs to protected management allowlist and cannot be blocked (Proposal Section 3.7, FR-07).",
                "code": "ALLOWLIST_PROTECTED",
            }), 403

        actor = getattr(g, "current_user", {}).get("sub", "admin")

        # Enforce on firewall adapter (Step 33)
        dir_code = "dst" if direction in ("destination", "dst") else "src"
        dur_mins = int(duration) if duration else 30
        try:
            fw_rule = firewall.block(
                ip=ip,
                direction=dir_code,
                minutes=dur_mins,
                reason=reason,
            )
        except AllowlistImmunityError as e:
            return jsonify({
                "error": "Forbidden",
                "message": str(e),
                "code": "ALLOWLIST_PROTECTED",
            }), 403
        except Exception as e:
            logger.error("Firewall adapter block failed: %s", e)
            db.log_response_action({
                "action": "block",
                "target_ip": ip,
                "direction": direction,
                "rule": f"block ip {ip} direction {direction}",
                "reason_code": "ADMIN_MANUAL_ENFORCEMENT",
                "actor": actor,
                "status": "failed",
                "error": str(e),
                "simulated": firewall.is_simulated,
            })
            if hasattr(db, "log_system_event"):
                db.log_system_event(
                    actor=actor,
                    event="MANUAL_BLOCK",
                    outcome="FAILURE",
                    details={"ip": ip, "direction": direction, "duration_minutes": dur_mins,
                             "reason": reason, "error": str(e)},
                )
            return jsonify({
                "error": "Firewall Error",
                "message": f"The firewall did not apply the block for '{ip}': {e}. Nothing was recorded as blocked.",
                "code": "FIREWALL_ERROR",
            }), 502

        block_id = db.add_to_blocklist(
            ip=ip,
            direction=direction,
            reason=reason,
            duration_minutes=dur_mins,
            actor=actor,
        )

        if not block_id:
            return jsonify({"error": "Failed to insert blocklist record."}), 500

        # Log mitigation response action
        db.log_response_action({
            "action": "block",
            "target_ip": ip,
            "direction": direction,
            "rule": f"block ip {ip} direction {direction}",
            "reason_code": "ADMIN_MANUAL_ENFORCEMENT",
            "actor": actor,
            "status": "applied",
            "simulated": firewall.is_simulated,
        })

        # Log system audit event (Step 34, FR-07)
        if hasattr(db, "log_system_event"):
            db.log_system_event(
                actor=actor,
                event="MANUAL_BLOCK",
                outcome="SUCCESS",
                details={
                    "ip": ip,
                    "direction": direction,
                    "duration_minutes": dur_mins,
                    "reason": reason,
                    "block_id": block_id,
                },
            )

        # Broadcast blocklist update
        block_update = {
            "block_id": block_id,
            "ip": ip,
            "direction": direction,
            "status": "active",
            "actor": actor,
            "reason": reason,
            "simulated": firewall.is_simulated,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        socketio.emit("blocklist_update", block_update)

        return jsonify({
            "status": "success",
            "message": f"Blocking rule for '{ip}' enacted successfully.",
            "block": block_update,
        }), 201

    @app.route("/api/blocklist/<target_ip>", methods=["DELETE"])
    @auth.admin_required
    def remove_block(target_ip):
        """
        Manually remove active block rules for target IP (Admin only).
        Updates audit records to status 'removed' without destroying history (FR-07).
        """
        clean_ip = target_ip.strip()
        data = request.get_json(silent=True) or {}
        reason = data.get("reason", "Manual administrator unblock")
        actor = getattr(g, "current_user", {}).get("sub", "admin")

        # Enforce unblock on firewall adapter (Step 33)
        fw_error = None
        try:
            firewall.unblock(ip=clean_ip, direction="all")
        except Exception as e:
            fw_error = str(e)
            logger.error("Firewall adapter unblock failed: %s", e)
        engine_obj = app.config.get("decision_engine")
        if engine_obj is not None and hasattr(engine_obj, "forget_block"):
            engine_obj.forget_block(clean_ip)

        unblocked_count = db.remove_from_blocklist(ip=clean_ip, reason=reason, actor=actor)
        if unblocked_count == 0:
            return jsonify({"error": "Not Found", "message": f"No active block found for '{clean_ip}'."}), 404

        # Log unblock response action
        db.log_response_action({
            "action": "unblock",
            "target_ip": clean_ip,
            "direction": "both",
            "rule": f"unblock ip {clean_ip}",
            "reason_code": "ADMIN_MANUAL_UNBLOCK",
            "actor": actor,
            "status": "applied" if fw_error is None else "firewall_error",
            "error": fw_error,
            "simulated": firewall.is_simulated,
        })

        # Log system audit event (Step 34, FR-07)
        if hasattr(db, "log_system_event"):
            db.log_system_event(
                actor=actor,
                event="MANUAL_UNBLOCK",
                outcome="SUCCESS" if fw_error is None else "PARTIAL",
                details={
                    "ip": clean_ip,
                    "reason": reason,
                    "unblocked_count": unblocked_count,
                    "firewall_error": fw_error,
                },
            )

        # Broadcast update
        unblock_payload = {
            "ip": clean_ip,
            "status": "removed",
            "unblock_actor": actor,
            "unblock_reason": reason,
            "simulated": firewall.is_simulated,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        socketio.emit("blocklist_update", unblock_payload)

        message = f"Unblocked '{clean_ip}'. {unblocked_count} rule(s) transitioned to 'removed'."
        if fw_error is not None:
            message += f" Warning: the firewall reported an error ({fw_error}); check the firewall rules."
        return jsonify({
            "status": "success" if fw_error is None else "partial",
            "message": message,
            "unblocked": unblock_payload,
            "firewall_error": fw_error,
        }), 200

    # =========================================================================
    # 7. Operational Settings & Allowlist (FR-07)
    # =========================================================================

    @app.route("/api/settings", methods=["GET"])
    @auth.token_required
    def get_settings():
        """Retrieve operational configuration parameters (allowlist, thresholds)."""
        key = request.args.get("key")
        if key:
            val = db.get_setting(key)
            return jsonify({"status": "success", "key": key, "value": val}), 200

        # Return the values the running response policy uses now (FR-07).
        # Values saved from the dashboard override settings.yaml; read-only items
        # (auto_response, adapter) come from settings.yaml.
        engine_obj = app.config.get("decision_engine")
        settings_map: Dict[str, Any] = {}
        if engine_obj is not None and hasattr(engine_obj, "get_runtime_settings"):
            settings_map.update(engine_obj.get_runtime_settings())
        for k in DecisionEngine.RUNTIME_SETTING_KEYS:
            stored = db.get_setting(k)
            if stored is not None:
                settings_map[k] = stored
        settings_map["adapter"] = getattr(firewall, "name", "unknown")
        settings_map["firewall_simulated"] = bool(getattr(firewall, "is_simulated", True))
        settings_map["editable_keys"] = list(DecisionEngine.RUNTIME_SETTING_KEYS)
        return jsonify({"status": "success", "settings": settings_map}), 200

    @app.route("/api/settings", methods=["PUT"])
    @auth.admin_required
    def update_settings():
        """
        Update an operational setting with immutable audit history (Admin only per FR-07).
        Request body: {"key": "min_confidence", "value": 0.88, "reason": "Tuned after test"}
        """
        data = request.get_json(silent=True) or {}
        key = data.get("key", "").strip()
        value = data.get("value")
        reason = data.get("reason", "Administrative update")

        if not key:
            return jsonify({"error": "Bad Request", "message": "Setting 'key' must be specified."}), 400

        engine_obj = app.config.get("decision_engine")
        if key in DecisionEngine.RUNTIME_SETTING_KEYS:
            try:
                value = DecisionEngine.validate_runtime_setting(key, value)
            except (ValueError, TypeError) as exc:
                return jsonify({"error": "Bad Request", "message": str(exc)}), 400

        actor = getattr(g, "current_user", {}).get("sub", "admin")
        success = db.set_setting(key=key, value=value, updated_by=actor, reason=reason)
        if not success:
            return jsonify({"error": "Failed to update setting."}), 500

        # Apply the new value to the running response policy at once (FR-07)
        if engine_obj is not None and key in DecisionEngine.RUNTIME_SETTING_KEYS:
            engine_obj.apply_runtime_settings({key: value})

        # Broadcast settings update
        settings_payload = {
            "key": key,
            "value": value,
            "updated_by": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        socketio.emit("settings_update", settings_payload)

        return jsonify({
            "status": "success",
            "message": f"Setting '{key}' updated successfully.",
            "setting": settings_payload,
        }), 200

    @app.route("/api/settings/history", methods=["GET"])
    @auth.token_required
    def get_settings_history():
        """Retrieve full immutable change history for an operational setting."""
        key = request.args.get("key", "").strip()
        if key:
            history = db.get_setting_history(key)
            return jsonify({"status": "success", "key": key, "history": history}), 200

        # No key: combined history of all dashboard settings, newest first
        combined: List[Dict[str, Any]] = []
        for k in DecisionEngine.RUNTIME_SETTING_KEYS:
            for item in db.get_setting_history(k):
                combined.append({**item, "key": k})
        combined.sort(key=lambda h: str(h.get("updated_at", "")), reverse=True)
        return jsonify({"status": "success", "key": None, "history": combined}), 200

    # =========================================================================
    # 8. Log Export & System Audit (FR-08)
    # =========================================================================

    @app.route("/api/logs", methods=["GET"])
    @auth.admin_required
    def get_system_audit_logs():
        """Retrieve administrative and security audit trail from system_logs."""
        limit = min(int(request.args.get("limit", 100)), 500)
        actor = request.args.get("actor")
        event = request.args.get("event")

        logs = db.get_system_logs(limit=limit, actor=actor, event=event)
        return jsonify({"status": "success", "count": len(logs), "logs": logs}), 200

    @app.route("/api/logs/export", methods=["GET"])
    @auth.admin_required
    def export_logs():
        """
        Export filtered incident logs, audit logs, or response actions (Proposal FR-08).
        Query params:
            type: 'events' (default), 'system_logs', 'actions'
            format: 'json' (default) or 'csv'
            class: class filter
            status: status filter ('prediction', 'confirmed')
            response_status: response status filter
            ip: IP filter (src or dst)
            src_ip, dst_ip: specific direction IP filters
            severity: severity filter
            actor: actor filter
            event: event filter
            start_time, end_time: ISO 8601 timestamps
            limit: record limit (up to 10000)
        """
        log_type = request.args.get("type", "events").strip().lower()
        export_fmt = request.args.get("format", "json").strip().lower()
        actor = getattr(g, "current_user", {}).get("sub", "admin")

        filters = {
            "start_time": request.args.get("start_time"),
            "end_time": request.args.get("end_time"),
            "class_filter": request.args.get("class"),
            "ip": request.args.get("ip"),
            "src_ip": request.args.get("src_ip"),
            "dst_ip": request.args.get("dst_ip"),
            "status": request.args.get("status"),
            "response_status": request.args.get("response_status"),
            "severity": request.args.get("severity"),
            "actor": request.args.get("actor"),
            "event": request.args.get("event"),
            "limit": min(int(request.args.get("limit", 1000)), 10000),
        }

        try:
            content, mime_type, filename, row_count = exporter.export_logs(
                log_type=log_type,
                filters=filters,
                export_format=export_fmt,
                actor=actor,
            )
        except ValueError as e:
            return jsonify({"error": "Bad Request", "message": str(e)}), 400

        output = make_response(content)
        output.headers["Content-Disposition"] = f"attachment; filename={filename}"
        output.headers["Content-Type"] = mime_type
        return output

    # =========================================================================
    # 9. Health & Subsystem Status
    # =========================================================================

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Public health endpoint monitoring status of MongoDB, model bundle,
        Zeek telemetry stream, and response adapters.
        """
        db_alive = db.is_connected()
        # Report the model and the Zeek log that are really in use (settings.yaml), not fixed paths.
        det = app.config.get("detector")
        model_ready = bool(det is not None and getattr(det, "model", None) is not None)
        zeek_log_path = Path(app.config["zeek_adapter"].conn_log_path) if app.config.get("zeek_adapter") \
            else PROJECT_ROOT / "sensor" / "logs" / "conn.log"
        zeek_ready = zeek_log_path.is_file() or (PROJECT_ROOT / "data" / "local" / ".zeek_adapter_state.json").is_file()

        is_healthy = db_alive and model_ready
        status_str = "healthy" if is_healthy else "degraded"

        return jsonify({
            "status": status_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subsystems": {
                "mongodb": "online" if db_alive else "offline",
                "ml_model_bundle": "ready" if model_ready else "missing",
                "zeek_telemetry": "active" if zeek_ready else "idle",
                "auth_engine": "active" if bool(auth.secret_key) else "unconfigured",
            },
        }), 200 if is_healthy else 503

    # =========================================================================
    # 9B. Live Streaming Pipeline Control Endpoints (Problem 1 Fix)
    # =========================================================================

    @app.route("/api/v1/pipeline/status", methods=["GET"])
    @auth.token_required
    def get_pipeline_status():
        """Return runtime state and metrics for the streaming Zeek -> Decision pipeline."""
        runner_obj = app.config.get("runner")
        if not runner_obj:
            return jsonify({"status": "unavailable", "message": "Pipeline runner not configured."}), 503
        return jsonify(runner_obj.get_status()), 200

    @app.route("/api/v1/pipeline/start", methods=["POST"])
    @auth.admin_required
    def start_pipeline():
        """Start the background streaming Zeek pipeline runner."""
        runner_obj = app.config.get("runner")
        if not runner_obj:
            return jsonify({"error": "Runner not configured"}), 503
        started = runner_obj.start()
        return jsonify({
            "success": started,
            "status": runner_obj.get_status()["status"],
            "message": "Pipeline started" if started else "Pipeline was already running",
        }), 200

    @app.route("/api/v1/pipeline/stop", methods=["POST"])
    @auth.admin_required
    def stop_pipeline():
        """Stop the background streaming Zeek pipeline runner."""
        runner_obj = app.config.get("runner")
        if not runner_obj:
            return jsonify({"error": "Runner not configured"}), 503
        stopped = runner_obj.stop()
        return jsonify({
            "success": stopped,
            "status": runner_obj.get_status()["status"],
            "message": "Pipeline stopped" if stopped else "Pipeline stop timed out",
        }), 200

    # =========================================================================
    # 9C. Firewall Synchronization & Rule Expiry Worker (Step 34, FR-06, FR-07)
    # =========================================================================

    @app.route("/api/v1/firewall/sync", methods=["GET"])
    @auth.token_required
    def get_firewall_sync():
        """
        Inspect synchronization status between firewall adapter and database blocklist.
        """
        fw_rules = firewall.list_active() if hasattr(firewall, "list_active") else []
        db_blocks = db.get_active_blocks() if hasattr(db, "get_active_blocks") else []
        fw_ips = {r.get("ip") for r in fw_rules if r.get("ip")}
        db_ips = {b.get("ip") for b in db_blocks if b.get("ip")}
        worker_obj = app.config.get("rule_worker")
        worker_status = worker_obj.get_status() if worker_obj else {}

        return jsonify({
            "status": "success",
            "in_sync": fw_ips == db_ips,
            "firewall_rules_count": len(fw_rules),
            "db_active_blocks_count": len(db_blocks),
            "firewall_rules": fw_rules,
            "db_active_blocks": db_blocks,
            "worker": worker_status,
        }), 200

    @app.route("/api/v1/firewall/sync", methods=["POST"])
    @auth.admin_required
    def trigger_firewall_sync():
        """
        Manually trigger reconciliation between firewall adapter and database blocklist.
        """
        summary = reconcile_on_startup(
            db=db,
            firewall=firewall,
            socketio=socketio,
            decision_engine=decision_inst,
        )
        return jsonify({
            "status": "success",
            "message": "Firewall reconciliation completed.",
            "reconciliation": summary,
        }), 200

    @app.route("/api/v1/firewall/worker/status", methods=["GET"])
    @auth.token_required
    def get_worker_status():
        """Get status of the background rule expiry worker."""
        worker_obj = app.config.get("rule_worker")
        if not worker_obj:
            return jsonify({"status": "unavailable", "running": False}), 200
        return jsonify({"status": "success", "worker": worker_obj.get_status()}), 200

    @app.route("/api/v1/firewall/worker/start", methods=["POST"])
    @auth.admin_required
    def start_worker():
        """Start the background rule expiry worker."""
        worker_obj = app.config.get("rule_worker")
        if not worker_obj:
            return jsonify({"error": "Worker not configured"}), 503
        started = worker_obj.start()
        return jsonify({
            "success": started,
            "worker": worker_obj.get_status(),
            "message": "Worker started" if started else "Worker already running",
        }), 200

    @app.route("/api/v1/firewall/worker/stop", methods=["POST"])
    @auth.admin_required
    def stop_worker():
        """Stop the background rule expiry worker."""
        worker_obj = app.config.get("rule_worker")
        if not worker_obj:
            return jsonify({"error": "Worker not configured"}), 503
        stopped = worker_obj.stop()
        return jsonify({
            "success": stopped,
            "worker": worker_obj.get_status(),
            "message": "Worker stopped" if stopped else "Worker stop timed out",
        }), 200

    # =========================================================================
    # 10. Real-Time Socket.IO Handshake & Channels (FR-04)
    # =========================================================================

    @socketio.on("connect")
    def handle_socket_connect(auth_data=None):
        """
        Authenticate incoming Socket.IO WebSocket connections.
        Refuses connection if valid JWT token is not provided (Proposal Section 3.6).
        """
        token = None
        if isinstance(auth_data, dict):
            token = auth_data.get("token")
        if not token:
            token = request.args.get("token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()

        if not token:
            logger.warning("Rejected unauthenticated Socket.IO connection attempt (token missing).")
            return False  # Refuse connection

        try:
            payload = auth.decode_token(token)
            logger.info(f"Socket.IO client connected: user '{payload.get('sub')}' (role: {payload.get('role')}).")
            emit("connected", {
                "status": "authenticated",
                "user": payload.get("sub"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return True
        except AuthError as e:
            logger.warning(f"Rejected Socket.IO connection: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected Socket.IO authentication failure: {e}")
            return False

    @socketio.on("disconnect")
    def handle_socket_disconnect():
        """Handle WebSocket client disconnection."""
        logger.debug("Socket.IO client disconnected.")

    return app, socketio


# Module-level instance for direct WSGI execution (e.g. gunicorn or python core_engine/app.py)
app, socketio = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting IoT IDS Unified Server on http://{host}:{port}...")

    # Auto-start Live Pipeline Runner (Problem 1 Fix)
    runner_obj = app.config.get("runner")
    if runner_obj:
        print(f"Auto-starting LivePipelineRunner tailing: {runner_obj.zeek_adapter.conn_log_path}")
        runner_obj.start()

    # Start the rule expiry worker (Step 34): expired rules are marked 'expired' and removed.
    worker_obj = app.config.get("rule_worker")
    if worker_obj:
        print(f"Auto-starting RuleExpiryWorker (every {worker_obj.interval_seconds} s)")
        worker_obj.start()

    socketio.run(app, host=host, port=port, debug=False)

