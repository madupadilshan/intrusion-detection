"""
MongoDB Database Service for IoT Intrusion Detection and Response System.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Compliant with Group 03 Proposal:
- Section 3.6 (System Architecture, MongoDB Database, Figure 4)
- Table 7 (Functional Requirements: FR-01, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08)
- Table 11 & Decision D-011 (Data Retention Policy: 90 days attacks/logs, 30 days summaries/scans)
- Decision D-027 (MongoDB 9-collection schema, full block history audit trail, TTL indexes)
"""

import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
import yaml

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, ConnectionFailure

logger = logging.getLogger("db_service")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# IDS_SETTINGS_FILE lets a test setup (e.g. lab_virtual/) use its own settings file.
DEFAULT_SETTINGS_PATH = Path(os.getenv("IDS_SETTINGS_FILE") or PROJECT_ROOT / "config" / "settings.yaml")

# Standard retention periods per Proposal Decision D-011
DEFAULT_RETENTION_DAYS = {
    "attack_events": 90,
    "traffic_summaries": 30,
    "system_logs": 90,
    "response_actions": 90,
    "scans": 30,
}

DEFAULT_MAX_RULE_MINUTES = 30
DEFAULT_REPEAT_WINDOW_SECONDS = 60


def _load_settings(settings_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load configuration settings from settings.yaml if available."""
    path = Path(settings_path) if settings_path else DEFAULT_SETTINGS_PATH
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not load settings from {path}: {e}")
    return {}


class DatabaseService:
    """
    MongoDB Database Service managing the 9 core and supporting collections
    defined in Proposal Section 3.6, Figure 4, and Requirements FR-01 through FR-08:
      1. devices (Figure 4, FR-05)
      2. attack_events (Figure 4, FR-01, FR-02, FR-06)
      3. response_actions (Figure 4, FR-06, FR-07)
      4. blocklist (Figure 4, FR-06, FR-07)
      5. system_logs (Figure 4, FR-07, FR-08)
      6. users (Figure 4, FR-04)
      7. traffic_summaries (FR-03, Table 5)
      8. settings (FR-07)
      9. scans (FR-05, Section 3.7)
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        settings_path: Optional[Union[str, Path]] = None,
        server_selection_timeout_ms: int = 3000,
        auto_connect: bool = True,
    ) -> None:
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name or os.getenv("DB_NAME", "iot_ids_db")
        self.server_selection_timeout_ms = server_selection_timeout_ms
        self.client: Optional[MongoClient] = None
        self.db = None

        # Load dynamic configurations from settings.yaml
        settings = _load_settings(settings_path)
        configured_retention = settings.get("retention_days", {})
        self.retention_days = {
            "attack_events": int(configured_retention.get("attack_events", DEFAULT_RETENTION_DAYS["attack_events"])),
            "traffic_summaries": int(configured_retention.get("traffic_summaries", DEFAULT_RETENTION_DAYS["traffic_summaries"])),
            "system_logs": int(configured_retention.get("system_logs", DEFAULT_RETENTION_DAYS["system_logs"])),
            "response_actions": int(configured_retention.get("response_actions", DEFAULT_RETENTION_DAYS["response_actions"])),
            "scans": int(configured_retention.get("scans", DEFAULT_RETENTION_DAYS["scans"])),
        }

        response_cfg = settings.get("response", {})
        self.max_rule_minutes = int(response_cfg.get("max_rule_minutes", DEFAULT_MAX_RULE_MINUTES))
        self.repeat_window_seconds = int(response_cfg.get("repeat_window_seconds", DEFAULT_REPEAT_WINDOW_SECONDS))

        # Collection references placeholder
        self.devices = None
        self.attack_events = None
        self.response_actions = None
        self.blocklist = None
        self.system_logs = None
        self.users = None
        self.traffic_summaries = None
        self.settings = None
        self.scans = None

        if auto_connect:
            self.connect()

    def connect(self) -> bool:
        """Establish connection to MongoDB server and initialize all 9 collections."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=self.server_selection_timeout_ms)
            # Verify connectivity via admin ping command
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]

            # 6 Core Collections from Proposal Figure 4
            self.devices = self.db["devices"]
            self.attack_events = self.db["attack_events"]
            self.response_actions = self.db["response_actions"]
            self.blocklist = self.db["blocklist"]
            self.system_logs = self.db["system_logs"]
            self.users = self.db["users"]

            # 3 Supporting Collections from Requirements (FR-03, FR-05, FR-07)
            self.traffic_summaries = self.db["traffic_summaries"]
            self.settings = self.db["settings"]
            self.scans = self.db["scans"]

            self._ensure_indexes()
            logger.info(f"Connected to MongoDB database '{self.db_name}' at {self.uri}.")
            return True
        except (ConnectionFailure, PyMongoError) as e:
            logger.error(f"Failed to connect to MongoDB at {self.uri}: {e}")
            self.client = None
            self.db = None
            return False
        except Exception as e:
            logger.error(f"Unexpected MongoDB initialization error: {e}")
            self.client = None
            self.db = None
            return False

    def close(self) -> None:
        """Close MongoDB connection pool."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB client connection closed.")

    def is_connected(self) -> bool:
        """Check if connection is alive."""
        if not self.client or self.db is None:
            return False
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    # =========================================================================
    # Index Management & Retention Rules
    # =========================================================================

    def _ensure_indexes(self) -> None:
        """
        Create functional, compound, and TTL retention indexes across all 9 collections.
        Safely handles schema migrations (e.g. dropping obsolete unique indexes).
        """
        if self.db is None:
            return

        try:
            # 1. devices
            self.devices.create_index([("ip", ASCENDING)], unique=True)
            self.devices.create_index([("last_seen", DESCENDING)])
            self.devices.create_index([("possible_camera", ASCENDING)])

            # 2. attack_events (TTL: 90 days per D-011)
            self._ensure_ttl_index(
                self.attack_events,
                "timestamp",
                self.retention_days["attack_events"] * 86400,
            )
            self.attack_events.create_index([("src_ip", ASCENDING), ("timestamp", DESCENDING)])
            self.attack_events.create_index([("dst_ip", ASCENDING), ("timestamp", DESCENDING)])
            self.attack_events.create_index([("predicted_class", ASCENDING), ("timestamp", DESCENDING)])
            self.attack_events.create_index([("status", ASCENDING)])
            self.attack_events.create_index([("response_status", ASCENDING)])
            # Compound index for fast burst-event aggregation
            self.attack_events.create_index([
                ("src_ip", ASCENDING),
                ("dst_ip", ASCENDING),
                ("predicted_class", ASCENDING),
                ("last_seen", DESCENDING),
            ])

            # 3. response_actions (TTL: 90 days per D-011)
            self._ensure_ttl_index(
                self.response_actions,
                "executed_at",
                self.retention_days["response_actions"] * 86400,
            )
            self.response_actions.create_index([("target_ip", ASCENDING)])
            self.response_actions.create_index([("event_id", ASCENDING)])
            self.response_actions.create_index([("action", ASCENDING)])

            # 4. blocklist: Fix deficiency #1 (Preserve full audit history)
            # Remove legacy unique index on 'ip' if present
            self._drop_index_if_unique(self.blocklist, "ip_1")
            # Compound NON-UNIQUE index on (ip, status)
            self.blocklist.create_index([("ip", ASCENDING), ("status", ASCENDING)], unique=False)
            self.blocklist.create_index([("status", ASCENDING)])
            self.blocklist.create_index([("created_at", DESCENDING)])
            self.blocklist.create_index([("expires_at", ASCENDING)])

            # 5. system_logs (TTL: 90 days per D-011)
            self._ensure_ttl_index(
                self.system_logs,
                "timestamp",
                self.retention_days["system_logs"] * 86400,
            )
            self.system_logs.create_index([("actor", ASCENDING)])
            self.system_logs.create_index([("event", ASCENDING)])

            # 6. users
            self.users.create_index([("username", ASCENDING)], unique=True)

            # 7. traffic_summaries (TTL: 30 days per D-011)
            self._ensure_ttl_index(
                self.traffic_summaries,
                "minute",
                self.retention_days["traffic_summaries"] * 86400,
            )
            self.traffic_summaries.create_index([("minute", ASCENDING), ("class_name", ASCENDING)], unique=True)

            # 8. settings (FR-07)
            self.settings.create_index([("key", ASCENDING)], unique=True)

            # 9. scans (TTL: 30 days per D-011)
            self._ensure_ttl_index(
                self.scans,
                "start_time",
                self.retention_days["scans"] * 86400,
            )
            self.scans.create_index([("scan_id", ASCENDING)], unique=True)
            self.scans.create_index([("status", ASCENDING)])

            logger.info("MongoDB indexes verified across all 9 collections.")
        except PyMongoError as e:
            logger.error(f"Error ensuring indexes: {e}")

    def _ensure_ttl_index(self, collection, field_name: str, expire_seconds: int) -> None:
        """Create or update a TTL expiration index safely."""
        try:
            indexes = collection.index_information()
            target_index_name = f"{field_name}_ttl"
            # Check if any existing index covers this field with different options
            for idx_name, idx_info in list(indexes.items()):
                keys = idx_info.get("key", [])
                if len(keys) == 1 and keys[0][0] == field_name:
                    current_expire = idx_info.get("expireAfterSeconds")
                    if current_expire == expire_seconds:
                        return  # Already configured correctly
                    # Drop outdated index
                    collection.drop_index(idx_name)
                    break
            # Create TTL index
            collection.create_index(
                [(field_name, ASCENDING)],
                name=target_index_name,
                expireAfterSeconds=expire_seconds,
            )
        except PyMongoError as e:
            logger.warning(f"TTL index setup on {collection.name}.{field_name}: {e}")

    def _drop_index_if_unique(self, collection, index_name: str) -> None:
        """Drop an index if it exists with unique=True to allow historical duplicates."""
        try:
            indexes = collection.index_information()
            if index_name in indexes and indexes[index_name].get("unique"):
                collection.drop_index(index_name)
                logger.info(f"Dropped legacy unique index '{index_name}' on collection '{collection.name}'.")
        except PyMongoError as e:
            logger.warning(f"Could not drop index {index_name} on {collection.name}: {e}")

    # =========================================================================
    # Helpers: Formatting & Serialization
    # =========================================================================

    @staticmethod
    def _format_doc(doc: Optional[Dict[str, Any]], format_dates: bool = True) -> Optional[Dict[str, Any]]:
        """Format MongoDB BSON document for clean Python/JSON presentation."""
        if doc is None:
            return None
        out = dict(doc)
        if "_id" in out:
            out["_id"] = str(out["_id"])
        if format_dates:
            for k, v in list(out.items()):
                if isinstance(v, datetime):
                    out[k] = v.isoformat()
                elif isinstance(v, list):
                    out[k] = [
                        DatabaseService._format_doc(item, format_dates=True)
                        if isinstance(item, dict)
                        else item
                        for item in v
                    ]
        return out

    # =========================================================================
    # 1. Device Operations (Figure 4, FR-05)
    # =========================================================================

    def upsert_device(self, device_data: Dict[str, Any]) -> bool:
        """
        Insert or update a network device discovered via Nmap or passive monitoring.
        Mandatory field: 'ip'.
        """
        if not self.is_connected():
            return False
        ip = device_data.get("ip")
        if not ip or not isinstance(ip, str) or not ip.strip():
            raise ValueError("Device record requires a valid, non-empty 'ip' string.")

        clean_ip = ip.strip()
        now = datetime.now(timezone.utc)
        possible_cam = bool(device_data.get("possible_camera", False))
        camera_evidence = device_data.get("camera_evidence") or device_data.get("evidence", [])
        if isinstance(camera_evidence, str):
            camera_evidence = [camera_evidence]

        update_payload = {
            "$set": {
                "mac": device_data.get("mac") or "unknown",
                "vendor": device_data.get("vendor") or "unknown",
                "device_type": device_data.get("device_type") or ("ip_camera" if possible_cam else "unknown"),
                "possible_camera": possible_cam,
                "camera_evidence": camera_evidence,
                "open_ports": [int(p) for p in device_data.get("open_ports", []) if str(p).isdigit()],
                "possible_services": list(device_data.get("possible_services") or device_data.get("services", [])),
                "hostname": device_data.get("hostname") or "",
                "status": device_data.get("status") or "online",
                "last_seen": now,
                # True only for the scanner's invented test devices (never a real scan result)
                "simulated": bool(device_data.get("simulated", False)),
            },
            "$setOnInsert": {
                "created_at": now,
                "confirmed_camera": bool(device_data.get("confirmed_camera", False)),
                "notes": device_data.get("notes") or "",
            },
        }

        if "last_scan_time" in device_data:
            last_scan = device_data["last_scan_time"]
            if isinstance(last_scan, str):
                try:
                    last_scan = datetime.fromisoformat(last_scan)
                except ValueError:
                    last_scan = now
            update_payload["$set"]["last_scan_time"] = last_scan

        try:
            self.devices.update_one({"ip": clean_ip}, update_payload, upsert=True)
            return True
        except PyMongoError as e:
            logger.error(f"Error upserting device {clean_ip}: {e}")
            return False

    def get_devices(self, camera_only: bool = False, limit: int = 200, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve registered devices, optionally filtering for IP cameras."""
        if not self.is_connected():
            return []
        query = {"possible_camera": True} if camera_only else {}
        try:
            cursor = self.devices.find(query).sort("last_seen", DESCENDING).limit(limit)
            return [self._format_doc(d, format_dates=format_dates) for d in cursor]
        except PyMongoError as e:
            logger.error(f"Error fetching devices: {e}")
            return []

    def get_device_by_ip(self, ip: str, format_dates: bool = True) -> Optional[Dict[str, Any]]:
        """Find a single device by its IP address."""
        if not self.is_connected() or not ip:
            return None
        try:
            doc = self.devices.find_one({"ip": ip.strip()})
            return self._format_doc(doc, format_dates=format_dates)
        except PyMongoError as e:
            logger.error(f"Error finding device by IP {ip}: {e}")
            return None

    def update_device_status(self, ip: str, status: str) -> bool:
        """Update operational status ('online', 'offline') of a registered device."""
        if not self.is_connected() or not ip:
            return False
        try:
            res = self.devices.update_one(
                {"ip": ip.strip()},
                {"$set": {"status": status, "last_seen": datetime.now(timezone.utc)}},
            )
            return res.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating device status for {ip}: {e}")
            return False

    def confirm_camera_role(self, ip: str, confirmed: bool = True, notes: str = "") -> bool:
        """
        Confirm or revoke the IP camera classification for a discovered device (Proposal Section 3.7).
        Adheres to: 'A device is labelled as a possible camera with evidence, and the administrator confirms the role.'

        Args:
            ip: Target device IP address.
            confirmed: True to confirm camera role, False to revoke.
            notes: Optional administrator justification notes.

        Returns:
            True if device document was found and updated, False otherwise.
        """
        if not self.is_connected() or not ip:
            return False
        clean_ip = ip.strip()
        update_doc: Dict[str, Any] = {
            "confirmed_camera": bool(confirmed),
            "updated_at": datetime.now(timezone.utc),
        }
        if notes:
            update_doc["notes"] = notes
        if confirmed:
            update_doc["device_type"] = "ip_camera"

        try:
            res = self.devices.update_one(
                {"ip": clean_ip},
                {"$set": update_doc},
            )
            return res.matched_count > 0
        except PyMongoError as e:
            logger.error(f"Error confirming camera role for {clean_ip}: {e}")
            return False

    # =========================================================================
    # 2. Attack Events (Figure 4, FR-01, FR-02, FR-06)
    # =========================================================================

    def record_attack_event(
        self,
        event_data: Dict[str, Any],
        aggregate_window_seconds: Optional[int] = None,
        allow_benign: bool = False,
    ) -> Optional[str]:
        """
        Record a detected security incident in 'attack_events'.
        Enforces strict schema validation (no fake defaults):
        - Mandatory: src_ip, dst_ip, predicted_class, confidence
        - Benign flows are rejected unless allow_benign=True (Proposal FR-03: Benign flows
          must update traffic_summaries only).
        - Repeated flows from same (src_ip, dst_ip, predicted_class) inside aggregate_window_seconds
          are coalesced into one event (increments flow_count and updates last_seen).
        """
        if not self.is_connected():
            return None

        src_ip = event_data.get("src_ip")
        dst_ip = event_data.get("dst_ip")
        predicted_class = event_data.get("predicted_class")
        confidence = event_data.get("confidence")

        # Validation: Reject missing critical fields
        if not src_ip or not isinstance(src_ip, str) or not src_ip.strip():
            raise ValueError("Attack event requires a valid, non-empty 'src_ip'.")
        if not dst_ip or not isinstance(dst_ip, str) or not dst_ip.strip():
            raise ValueError("Attack event requires a valid, non-empty 'dst_ip'.")
        if not predicted_class or not isinstance(predicted_class, str) or not predicted_class.strip():
            raise ValueError("Attack event requires a non-empty 'predicted_class'.")
        if confidence is None:
            raise ValueError("Attack event requires a numerical 'confidence' value (0.0 to 1.0).")

        confidence_val = float(confidence)
        if not (0.0 <= confidence_val <= 1.0):
            raise ValueError(f"Confidence {confidence_val} out of valid range [0.0, 1.0].")

        # Deficiency #8: Benign flows do not belong in attack_events
        if predicted_class == "Benign" and not allow_benign:
            raise ValueError(
                "Benign traffic flows must be recorded via record_traffic_summary(), "
                "not attack_events (Proposal FR-03, Table 5)."
            )

        clean_src = src_ip.strip()
        clean_dst = dst_ip.strip()
        clean_class = predicted_class.strip()
        now = datetime.now(timezone.utc)

        window_sec = (
            aggregate_window_seconds
            if aggregate_window_seconds is not None
            else self.repeat_window_seconds
        )

        # Extra: Coalesce burst attacks into an ongoing incident
        if window_sec > 0:
            window_start = now - timedelta(seconds=window_sec)
            existing = self.attack_events.find_one({
                "src_ip": clean_src,
                "dst_ip": clean_dst,
                "predicted_class": clean_class,
                "last_seen": {"$gte": window_start},
                "status": "prediction",
            })
            if existing:
                try:
                    self.attack_events.update_one(
                        {"event_id": existing["event_id"]},
                        {
                            "$inc": {"flow_count": 1},
                            "$set": {
                                "last_seen": now,
                                "confidence": max(float(existing.get("confidence", 0.0)), confidence_val),
                            },
                        },
                    )
                    return existing["event_id"]
                except PyMongoError as e:
                    logger.error(f"Error updating burst event {existing.get('event_id')}: {e}")

        # Insert new distinct event document
        event_id = event_data.get("event_id") or str(uuid.uuid4())
        ts = event_data.get("timestamp") or now
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = now

        doc = {
            "event_id": event_id,
            "timestamp": ts,
            "direction": event_data.get("direction") or event_data.get("traffic_direction") or "unknown",
            "src_ip": clean_src,
            "src_port": int(event_data.get("src_port") or 0),
            "dst_ip": clean_dst,
            "dst_port": int(event_data.get("dst_port") or 0),
            "proto": str(event_data.get("proto") or "unknown").lower(),
            "service": str(event_data.get("service") or "-"),
            "predicted_class": clean_class,
            "confidence": confidence_val,
            "probabilities": event_data.get("probabilities") or {},
            "model_version": str(event_data.get("model_version") or "unknown"),
            "flow_features": event_data.get("flow_features") or event_data.get("features") or {},
            "evidence_note": str(event_data.get("evidence_note") or event_data.get("evidence") or ""),
            "reason_code": str(event_data.get("reason_code") or "GENERIC_ANOMALY"),
            "severity": str(event_data.get("severity") or "high"),
            "status": str(event_data.get("status") or "prediction"),  # "prediction" or "confirmed"
            "response_status": str(event_data.get("response_status") or "pending"),  # "pending", "mitigated", "alert_only", "ignored", "candidate"
            "is_allowlisted": bool(event_data.get("is_allowlisted", False)),
            "timestamps": event_data.get("timestamps") or {},
            "flow_count": 1,
            "first_seen": ts,
            "last_seen": ts,
            "created_at": now,
        }

        try:
            self.attack_events.insert_one(doc)
            return event_id
        except PyMongoError as e:
            logger.error(f"Error inserting attack event: {e}")
            return None

    def get_attack_events(
        self,
        limit: int = 50,
        class_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        response_status_filter: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format_dates: bool = True,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        ip: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve recorded attack events with flexible query filtering."""
        if not self.is_connected():
            return []
        query: Dict[str, Any] = {}
        if class_filter:
            query["predicted_class"] = class_filter
        if status_filter:
            query["status"] = status_filter
        if response_status_filter:
            query["response_status"] = response_status_filter
        if src_ip:
            query["src_ip"] = src_ip.strip()
        if dst_ip:
            query["dst_ip"] = dst_ip.strip()
        if ip:
            clean_ip = ip.strip()
            query["$or"] = [{"src_ip": clean_ip}, {"dst_ip": clean_ip}]
        if severity:
            query["severity"] = severity.strip()
        if start_time or end_time:
            time_query: Dict[str, Any] = {}
            if start_time:
                time_query["$gte"] = start_time
            if end_time:
                time_query["$lte"] = end_time
            query["timestamp"] = time_query

        try:
            cursor = self.attack_events.find(query).sort("timestamp", DESCENDING).limit(limit)
            return [self._format_doc(e, format_dates=format_dates) for e in cursor]
        except PyMongoError as e:
            logger.error(f"Error querying attack events: {e}")
            return []

    def update_attack_event_status(
        self,
        event_id: str,
        status: Optional[str] = None,
        response_status: Optional[str] = None,
        response_reason: Optional[str] = None,
    ) -> bool:
        """Update incident confirmation status, response outcome, or the policy reason code."""
        if not self.is_connected() or not event_id:
            return False
        updates: Dict[str, Any] = {}
        if status:
            updates["status"] = status
        if response_status:
            updates["response_status"] = response_status
        if response_reason:
            updates["response_reason"] = response_reason
        if not updates:
            return False
        try:
            res = self.attack_events.update_one({"event_id": event_id}, {"$set": updates})
            return res.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating attack event {event_id}: {e}")
            return False

    def get_attack_stats(self, time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """Aggregate detection statistics grouped by predicted attack class."""
        if not self.is_connected():
            return {"total_events": 0, "classes": {}}
        match_stage: Dict[str, Any] = {}
        if time_window_hours and time_window_hours > 0:
            since = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
            match_stage = {"$match": {"timestamp": {"$gte": since}}}

        pipeline = []
        if match_stage:
            pipeline.append(match_stage)
        pipeline.append({
            "$group": {
                "_id": "$predicted_class",
                "count": {"$sum": "$flow_count"},
                "incidents": {"$sum": 1},
            }
        })

        try:
            results = list(self.attack_events.aggregate(pipeline))
            classes = {item["_id"]: item["count"] for item in results}
            incidents = {item["_id"]: item["incidents"] for item in results}
            total_flows = sum(classes.values())
            total_incidents = sum(incidents.values())
            return {
                "total_flows": total_flows,
                "total_incidents": total_incidents,
                "classes": classes,
                "incidents_by_class": incidents,
            }
        except PyMongoError as e:
            logger.error(f"Error aggregating attack stats: {e}")
            return {"total_events": 0, "classes": {}}

    # =========================================================================
    # 3. Blocklist Operations (Figure 4, FR-06, FR-07 - Full History Audit Trail)
    # =========================================================================

    def add_to_blocklist(
        self,
        ip: str,
        direction: str,
        reason: str,
        duration_minutes: Optional[int] = None,
        linked_event_id: Optional[str] = None,
        predicted_class: Optional[str] = None,
        confidence: Optional[float] = None,
        actor: str = "system_auto",
        action: str = "block",
    ) -> Optional[str]:
        """
        Add an IP block record to the blocklist.
        `action` is "block" or "rate_limit" (D-055), so startup recovery restores the same rule.
        Preserves complete historical audit trail: NEVER overwrites prior blocks!
        Inserts a distinct document with unique block_id.
        """
        if not self.is_connected():
            return None
        if not ip or not isinstance(ip, str) or not ip.strip():
            raise ValueError("Blocklist entry requires a valid 'ip' string.")
        if not reason or not isinstance(reason, str) or not reason.strip():
            raise ValueError("Blocklist entry requires an explicit 'reason' description.")

        clean_ip = ip.strip()
        clean_dir = direction.strip() if direction else "source"
        if clean_dir not in ("source", "destination", "both"):
            clean_dir = "source"

        mins = duration_minutes if duration_minutes is not None else self.max_rule_minutes
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=mins)
        block_id = str(uuid.uuid4())

        doc = {
            "block_id": block_id,
            "ip": clean_ip,
            "direction": clean_dir,
            "action": "rate_limit" if str(action).strip().lower() == "rate_limit" else "block",
            "reason": reason.strip(),
            "linked_event_id": linked_event_id,
            "predicted_class": predicted_class,
            "confidence": float(confidence) if confidence is not None else None,
            "actor": actor or "system_auto",
            "status": "active",  # "active", "expired", "removed"
            "created_at": now,
            "expires_at": expires_at,
            "duration_minutes": mins,
            "unblocked_at": None,
            "unblock_reason": None,
            "unblock_actor": None,
        }

        try:
            self.blocklist.insert_one(doc)
            return block_id
        except PyMongoError as e:
            logger.error(f"Error inserting blocklist record for {clean_ip}: {e}")
            return None

    def remove_from_blocklist(
        self,
        ip: str,
        reason: str = "Manual administrator removal",
        actor: str = "admin",
    ) -> int:
        """
        Mark any active blocks for this IP as 'removed'.
        Preserves history by updating audit fields rather than deleting.
        Returns count of active blocks transitioned.
        """
        if not self.is_connected() or not ip:
            return 0
        clean_ip = ip.strip()
        now = datetime.now(timezone.utc)

        try:
            res = self.blocklist.update_many(
                {"ip": clean_ip, "status": "active"},
                {
                    "$set": {
                        "status": "removed",
                        "unblocked_at": now,
                        "unblock_reason": reason,
                        "unblock_actor": actor,
                    }
                },
            )
            return res.modified_count
        except PyMongoError as e:
            logger.error(f"Error removing {clean_ip} from blocklist: {e}")
            return 0

    def is_ip_blocked(self, ip: str) -> bool:
        """
        Check if an IP address currently has an active, unexpired block.
        Automatically sweeps and transitions expired entries.
        """
        if not self.is_connected() or not ip:
            return False
        clean_ip = ip.strip()
        now = datetime.now(timezone.utc)

        try:
            cursor = self.blocklist.find({"ip": clean_ip, "status": "active"})
            has_active = False
            for record in cursor:
                exp = record.get("expires_at")
                if exp:
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if now >= exp:
                        # Mark this record as expired
                        self.blocklist.update_one(
                            {"block_id": record["block_id"]},
                            {"$set": {"status": "expired"}},
                        )
                        continue
                has_active = True
            return has_active
        except PyMongoError as e:
            logger.error(f"Error checking if IP {clean_ip} is blocked: {e}")
            return False

    def get_blocked_ips(self, active_only: bool = True, limit: int = 100, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve blocklist entries. If active_only=True, sweeps expired rules first."""
        if not self.is_connected():
            return []
        now = datetime.now(timezone.utc)

        if active_only:
            # Transition expired records
            try:
                self.blocklist.update_many(
                    {"status": "active", "expires_at": {"$lte": now}},
                    {"$set": {"status": "expired"}},
                )
            except PyMongoError as e:
                logger.warning(f"Failed to sweep expired blocks: {e}")

        query = {"status": "active"} if active_only else {}
        try:
            cursor = self.blocklist.find(query).sort("created_at", DESCENDING).limit(limit)
            return [self._format_doc(b, format_dates=format_dates) for b in cursor]
        except PyMongoError as e:
            logger.error(f"Error fetching blocked IPs: {e}")
            return []

    def get_block_history_for_ip(self, ip: str, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve complete audit history of all blocks and removals for a specific IP."""
        if not self.is_connected() or not ip:
            return []
        try:
            cursor = self.blocklist.find({"ip": ip.strip()}).sort("created_at", DESCENDING)
            return [self._format_doc(b, format_dates=format_dates) for b in cursor]
        except PyMongoError as e:
            logger.error(f"Error querying block history for {ip}: {e}")
            return []

    def sweep_expired_blocks(self) -> List[Dict[str, Any]]:
        """
        Transition all active blocklist entries that have expired (now >= expires_at)
        to status 'expired'. Preserves full audit trail with unblocked_at,
        unblock_reason, and unblock_actor fields.
        Returns the list of transitioned block documents.
        """
        if not self.is_connected():
            return []
        now = datetime.now(timezone.utc)
        expired_docs = []
        try:
            cursor = self.blocklist.find({"status": "active", "expires_at": {"$lte": now}})
            expired_docs = list(cursor)
            if expired_docs:
                ids = [d["_id"] for d in expired_docs]
                self.blocklist.update_many(
                    {"_id": {"$in": ids}},
                    {
                        "$set": {
                            "status": "expired",
                            "unblocked_at": now,
                            "unblock_reason": "RULE_TIMEOUT_EXPIRED",
                            "unblock_actor": "system_auto",
                        }
                    },
                )
        except PyMongoError as e:
            logger.error(f"Error sweeping expired blocks: {e}")
        return expired_docs

    def get_active_blocks(self, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve all currently active block documents without mutating them."""
        if not self.is_connected():
            return []
        try:
            cursor = self.blocklist.find({"status": "active"}).sort("created_at", DESCENDING)
            return [self._format_doc(b, format_dates=format_dates) for b in cursor]
        except PyMongoError as e:
            logger.error(f"Error fetching active blocks: {e}")
            return []

    # =========================================================================
    # 4. Response Actions (Figure 4, FR-06, FR-07)
    # =========================================================================

    def log_response_action(self, action_data: Dict[str, Any]) -> Optional[str]:
        """Record an automated or manual mitigation action executed by the response engine."""
        if not self.is_connected():
            return None

        target_ip = action_data.get("target_ip")
        action = action_data.get("action") or action_data.get("action_type")
        reason_code = action_data.get("reason_code") or action_data.get("reason", "UNSPECIFIED")
        actor = action_data.get("actor") or "system_auto"

        if not target_ip:
            raise ValueError("Response action requires a valid 'target_ip'.")
        if not action or action not in ("block", "rate-limit", "isolate", "unblock"):
            raise ValueError(f"Invalid action '{action}'. Must be one of: block, rate-limit, isolate, unblock.")

        action_id = action_data.get("action_id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        exec_at = action_data.get("executed_at") or now
        if isinstance(exec_at, str):
            try:
                exec_at = datetime.fromisoformat(exec_at)
            except ValueError:
                exec_at = now

        doc = {
            "action_id": action_id,
            "event_id": action_data.get("event_id"),
            "action": action,
            "rule": action_data.get("rule") or action_data.get("firewall_rule") or "",
            "target_ip": target_ip.strip(),
            "direction": action_data.get("direction") or "source",
            "reason_code": reason_code,
            "actor": actor,
            "status": action_data.get("status") or "applied",  # "applied", "failed", "reverted"
            "executed_at": exec_at,
            "details": action_data.get("details") or {},
        }

        try:
            self.response_actions.insert_one(doc)
            return action_id
        except PyMongoError as e:
            logger.error(f"Error logging response action: {e}")
            return None

    def get_response_actions(
        self,
        limit: int = 50,
        target_ip: Optional[str] = None,
        event_id: Optional[str] = None,
        format_dates: bool = True,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve logged mitigation actions."""
        if not self.is_connected():
            return []
        query: Dict[str, Any] = {}
        if target_ip:
            query["target_ip"] = target_ip.strip()
        if event_id:
            query["event_id"] = event_id
        if status:
            query["status"] = status.strip()
        if actor:
            query["actor"] = actor.strip()
        if start_time or end_time:
            time_query: Dict[str, Any] = {}
            if start_time:
                time_query["$gte"] = start_time
            if end_time:
                time_query["$lte"] = end_time
            query["executed_at"] = time_query

        try:
            cursor = self.response_actions.find(query).sort("executed_at", DESCENDING).limit(limit)
            return [self._format_doc(a, format_dates=format_dates) for a in cursor]
        except PyMongoError as e:
            logger.error(f"Error querying response actions: {e}")
            return []

    # =========================================================================
    # 5. System Logs (Figure 4, FR-07, FR-08)
    # =========================================================================

    def log_system_event(
        self,
        actor: str,
        event: Optional[str] = None,
        outcome: str = "INFO",
        details: Optional[Dict[str, Any]] = None,
        event_type: Optional[str] = None,
    ) -> Optional[str]:
        """Record general operational and security audit events."""
        if not self.is_connected():
            return None
        log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        resolved_event = event or event_type or "GENERAL_EVENT"

        doc = {
            "log_id": log_id,
            "timestamp": now,
            "actor": actor or "system",
            "event": resolved_event,
            "outcome": outcome or "INFO",
            "details": details or {},
        }

        try:
            self.system_logs.insert_one(doc)
            return log_id
        except PyMongoError as e:
            logger.error(f"Error logging system event: {e}")
            return None

    def get_system_logs(
        self,
        limit: int = 100,
        actor: Optional[str] = None,
        event: Optional[str] = None,
        format_dates: bool = True,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        outcome: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch system audit log records."""
        if not self.is_connected():
            return []
        query: Dict[str, Any] = {}
        if actor:
            query["actor"] = actor
        if event:
            query["event"] = event
        if outcome:
            query["outcome"] = outcome.strip()
        if start_time or end_time:
            time_query: Dict[str, Any] = {}
            if start_time:
                time_query["$gte"] = start_time
            if end_time:
                time_query["$lte"] = end_time
            query["timestamp"] = time_query

        try:
            cursor = self.system_logs.find(query).sort("timestamp", DESCENDING).limit(limit)
            return [self._format_doc(l, format_dates=format_dates) for l in cursor]
        except PyMongoError as e:
            logger.error(f"Error querying system logs: {e}")
            return []

    # =========================================================================
    # 6. Users Collection (Figure 4, FR-04, Section 3.6)
    # =========================================================================

    def create_user(self, username: str, password_hash: str, role: str = "admin") -> Optional[str]:
        """Create a new authenticated system user."""
        if not self.is_connected():
            return None
        if not username or not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be a non-empty string.")
        if not password_hash or not isinstance(password_hash, str) or not password_hash.strip():
            raise ValueError("Password hash must be provided.")

        clean_user = username.strip()
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        doc = {
            "user_id": user_id,
            "username": clean_user,
            "password_hash": password_hash,
            "role": role or "admin",
            "created_at": now,
            "last_login": None,
            "is_active": True,
        }

        try:
            self.users.insert_one(doc)
            return user_id
        except PyMongoError as e:
            logger.error(f"Error creating user {clean_user}: {e}")
            return None

    def get_user_by_username(self, username: str, format_dates: bool = True) -> Optional[Dict[str, Any]]:
        """Find a user document by username."""
        if not self.is_connected() or not username:
            return None
        try:
            doc = self.users.find_one({"username": username.strip()})
            return self._format_doc(doc, format_dates=format_dates)
        except PyMongoError as e:
            logger.error(f"Error finding user {username}: {e}")
            return None

    def update_last_login(self, username: str) -> bool:
        """Record successful authentication timestamp."""
        if not self.is_connected() or not username:
            return False
        try:
            res = self.users.update_one(
                {"username": username.strip()},
                {"$set": {"last_login": datetime.now(timezone.utc)}},
            )
            return res.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating login for {username}: {e}")
            return False

    def update_user_password(self, username: str, password_hash: str) -> bool:
        """Update password hash for an existing registered user."""
        if not self.is_connected() or not username or not password_hash:
            return False
        try:
            res = self.users.update_one(
                {"username": username.strip()},
                {"$set": {"password_hash": password_hash.strip()}},
            )
            return res.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating password for {username}: {e}")
            return False

    def list_users(self, format_dates: bool = True) -> List[Dict[str, Any]]:
        """List registered users (excluding password hashes for security)."""
        if not self.is_connected():
            return []
        try:
            cursor = self.users.find({}, {"password_hash": 0}).sort("username", ASCENDING)
            return [self._format_doc(u, format_dates=format_dates) for u in cursor]
        except PyMongoError as e:
            logger.error(f"Error listing users: {e}")
            return []

    # =========================================================================
    # 7. Traffic Summaries (FR-03, Table 5, Section 3.6)
    # =========================================================================

    def record_traffic_summary(
        self,
        minute: datetime,
        class_name: str = "Benign",
        count: int = 1,
        orig_bytes: int = 0,
        resp_bytes: int = 0,
        pkts: int = 0,
    ) -> bool:
        """
        Increment traffic summary for a 1-minute time bucket (Proposal FR-03).
        Enables efficient reporting and retention without bloating attack_events.
        """
        if not self.is_connected():
            return False
        if not isinstance(minute, datetime):
            raise ValueError("Minute bucket must be a datetime object.")

        # Floor datetime to minute boundary (second=0, microsecond=0)
        bucket_minute = minute.replace(second=0, microsecond=0)
        if bucket_minute.tzinfo is None:
            bucket_minute = bucket_minute.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        filter_doc = {"minute": bucket_minute, "class_name": class_name}
        update_doc = {
            "$inc": {
                "flow_count": int(count),
                "total_orig_bytes": int(orig_bytes),
                "total_resp_bytes": int(resp_bytes),
                "total_pkts": int(pkts),
            },
            "$set": {
                "updated_at": now,
            },
        }

        try:
            self.traffic_summaries.update_one(filter_doc, update_doc, upsert=True)
            return True
        except PyMongoError as e:
            logger.error(f"Error updating traffic summary: {e}")
            return False

    def sum_traffic_flows(self, start_time: Optional[datetime] = None, class_name: Optional[str] = "Benign") -> int:
        """Total flow count in traffic_summaries since start_time (database aggregate, no row limit)."""
        if not self.is_connected():
            return 0
        match: Dict[str, Any] = {}
        if class_name:
            match["class_name"] = class_name
        if start_time:
            match["minute"] = {"$gte": start_time}
        try:
            rows = list(self.traffic_summaries.aggregate([
                {"$match": match},
                {"$group": {"_id": None, "n": {"$sum": "$flow_count"}}},
            ]))
            return int(rows[0]["n"]) if rows else 0
        except PyMongoError as e:
            logger.error(f"Error summing traffic summaries: {e}")
            return 0

    def get_traffic_summaries(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        class_name: Optional[str] = None,
        limit: int = 1000,
        format_dates: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retrieve aggregated flow volume statistics."""
        if not self.is_connected():
            return []
        query: Dict[str, Any] = {}
        if class_name:
            query["class_name"] = class_name
        if start_time or end_time:
            time_query: Dict[str, Any] = {}
            if start_time:
                time_query["$gte"] = start_time
            if end_time:
                time_query["$lte"] = end_time
            query["minute"] = time_query

        try:
            cursor = self.traffic_summaries.find(query).sort("minute", ASCENDING).limit(limit)
            return [self._format_doc(s, format_dates=format_dates) for s in cursor]
        except PyMongoError as e:
            logger.error(f"Error querying traffic summaries: {e}")
            return []

    # =========================================================================
    # 8. Settings Collection (FR-07: Allowlists, Thresholds & Audit History)
    # =========================================================================

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Fetch current setting value by key."""
        if not self.is_connected() or not key:
            return default
        try:
            doc = self.settings.find_one({"key": key.strip()})
            return doc["value"] if doc and "value" in doc else default
        except PyMongoError as e:
            logger.error(f"Error fetching setting {key}: {e}")
            return default

    def set_setting(self, key: str, value: Any, updated_by: str = "admin", reason: str = "") -> bool:
        """
        Update or create a system setting with an immutable audit change history.
        """
        if not self.is_connected() or not key:
            return False
        clean_key = key.strip()
        now = datetime.now(timezone.utc)

        try:
            existing = self.settings.find_one({"key": clean_key})
            old_value = existing["value"] if existing and "value" in existing else None

            history_entry = {
                "updated_at": now,
                "updated_by": updated_by or "admin",
                "old_value": old_value,
                "new_value": value,
                "reason": reason or "",
            }

            self.settings.update_one(
                {"key": clean_key},
                {
                    "$set": {
                        "value": value,
                        "updated_by": updated_by or "admin",
                        "updated_at": now,
                    },
                    "$push": {
                        "change_history": history_entry,
                    },
                },
                upsert=True,
            )
            return True
        except PyMongoError as e:
            logger.error(f"Error saving setting {clean_key}: {e}")
            return False

    def get_setting_history(self, key: str, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve audit log of all changes made to a configuration parameter."""
        if not self.is_connected() or not key:
            return []
        try:
            doc = self.settings.find_one({"key": key.strip()})
            if not doc or "change_history" not in doc:
                return []
            history = doc["change_history"]
            if format_dates:
                for item in history:
                    if isinstance(item.get("updated_at"), datetime):
                        item["updated_at"] = item["updated_at"].isoformat()
            return history
        except PyMongoError as e:
            logger.error(f"Error fetching setting history for {key}: {e}")
            return []

    # =========================================================================
    # 9. Scans Collection (FR-05, Section 3.7)
    # =========================================================================

    def record_scan_start(self, subnet: str, started_by: str = "admin") -> Optional[str]:
        """Record the initiation of an authorized Nmap device discovery scan."""
        if not self.is_connected():
            return None
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        doc = {
            "scan_id": scan_id,
            "subnet": subnet.strip(),
            "started_by": started_by or "admin",
            "start_time": now,
            "end_time": None,
            "status": "running",
            "devices_found": 0,
            "discovered_ips": [],
            "summary": {},
        }

        try:
            self.scans.insert_one(doc)
            return scan_id
        except PyMongoError as e:
            logger.error(f"Error recording scan start: {e}")
            return None

    def record_scan_complete(
        self,
        scan_id: str,
        status: str = "completed",
        devices_found: int = 0,
        discovered_ips: Optional[List[str]] = None,
        summary: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record scan completion metrics and discovered target devices."""
        if not self.is_connected() or not scan_id:
            return False
        now = datetime.now(timezone.utc)

        try:
            res = self.scans.update_one(
                {"scan_id": scan_id},
                {
                    "$set": {
                        "end_time": now,
                        "status": status,
                        "devices_found": int(devices_found),
                        "discovered_ips": discovered_ips or [],
                        "summary": summary or {},
                    }
                },
            )
            return res.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error recording scan complete: {e}")
            return False

    def get_recent_scans(self, limit: int = 20, format_dates: bool = True) -> List[Dict[str, Any]]:
        """Retrieve recent device discovery scan records."""
        if not self.is_connected():
            return []
        try:
            cursor = self.scans.find().sort("start_time", DESCENDING).limit(limit)
            return [self._format_doc(s, format_dates=format_dates) for s in cursor]
        except PyMongoError as e:
            logger.error(f"Error fetching scans: {e}")
            return []

    # =========================================================================
    # Test Isolation Helper
    # =========================================================================

    def drop_database_for_testing(self) -> bool:
        """
        Safely drop database if and only if 'test' is part of the database name.
        Intended exclusively for clean pytest tear-down.
        """
        if not self.is_connected() or "test" not in self.db_name.lower():
            logger.warning(f"Refusing to drop non-test database '{self.db_name}'.")
            return False
        try:
            self.client.drop_database(self.db_name)
            logger.info(f"Dropped test database '{self.db_name}'.")
            return True
        except PyMongoError as e:
            logger.error(f"Error dropping test database {self.db_name}: {e}")
            return False
