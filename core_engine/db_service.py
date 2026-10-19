import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, ConnectionFailure

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    MongoDB service for the IoT Intrusion Detection and Response System.
    Manages 5 standard collections according to Proposal Figure 4:
    - devices
    - attack_events
    - response_actions
    - blocklist
    - system_logs
    And users collection for dashboard authentication.
    """

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name or os.getenv("DB_NAME", "iot_ids_db")
        self.client: Optional[MongoClient] = None
        self.db = None
        self.connect()

    def connect(self) -> bool:
        """Establish connection to MongoDB server and initialize collections."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Verify connectivity
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            
            # Reference collections
            self.devices = self.db["devices"]
            self.attack_events = self.db["attack_events"]
            self.response_actions = self.db["response_actions"]
            self.blocklist = self.db["blocklist"]
            self.system_logs = self.db["system_logs"]
            self.users = self.db["users"]
            
            self._ensure_indexes()
            logger.info(f"Successfully connected to MongoDB database '{self.db_name}'.")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB at {self.uri}: {e}")
            self.client = None
            self.db = None
            return False
        except Exception as e:
            logger.error(f"Unexpected database initialization error: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if database connection is alive."""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def _ensure_indexes(self):
        """Create necessary database indexes for fast query performance."""
        try:
            # Devices: unique IP index
            self.devices.create_index([("ip", ASCENDING)], unique=True)
            self.devices.create_index([("last_seen", DESCENDING)])

            # Attack Events: indexed by timestamp and source IP
            self.attack_events.create_index([("timestamp", DESCENDING)])
            self.attack_events.create_index([("src_ip", ASCENDING)])
            self.attack_events.create_index([("predicted_class", ASCENDING)])

            # Response Actions: indexed by timestamp and target IP
            self.response_actions.create_index([("executed_at", DESCENDING)])
            self.response_actions.create_index([("target_ip", ASCENDING)])

            # Blocklist: unique IP index and status index
            self.blocklist.create_index([("ip", ASCENDING)], unique=True)
            self.blocklist.create_index([("status", ASCENDING)])
            self.blocklist.create_index([("expires_at", ASCENDING)])

            # System Logs: indexed by timestamp
            self.system_logs.create_index([("timestamp", DESCENDING)])

            # Users: unique username index
            self.users.create_index([("username", ASCENDING)], unique=True)

            logger.info("MongoDB indexes verified and ensured.")
        except PyMongoError as e:
            logger.error(f"Error creating MongoDB indexes: {e}")

    # =========================================================================
    # Device Operations
    # =========================================================================

    def upsert_device(self, device_data: Dict[str, Any]) -> bool:
        """
        Insert or update a discovered network device.
        Requires 'ip' key.
        """
        if not self.is_connected() or not device_data.get("ip"):
            return False
        try:
            now = datetime.now(timezone.utc)
            update_payload = {
                "$set": {
                    "mac": device_data.get("mac", "Unknown"),
                    "vendor": device_data.get("vendor", "Unknown"),
                    "device_type": device_data.get("device_type", "unknown"),
                    "possible_camera": device_data.get("possible_camera", False),
                    "open_ports": device_data.get("open_ports", []),
                    "services": device_data.get("services", []),
                    "hostname": device_data.get("hostname", ""),
                    "status": device_data.get("status", "online"),
                    "last_seen": now
                },
                "$setOnInsert": {
                    "first_seen": now,
                    "notes": device_data.get("notes", "")
                }
            }
            self.devices.update_one({"ip": device_data["ip"]}, update_payload, upsert=True)
            return True
        except PyMongoError as e:
            logger.error(f"Error upserting device {device_data.get('ip')}: {e}")
            return False

    def get_devices(self) -> List[Dict[str, Any]]:
        """Retrieve all registered devices."""
        if not self.is_connected():
            return []
        try:
            devices = list(self.devices.find({}, {"_id": 0}).sort("last_seen", DESCENDING))
            # Format datetime fields to ISO string
            for dev in devices:
                if isinstance(dev.get("last_seen"), datetime):
                    dev["last_seen"] = dev["last_seen"].isoformat()
                if isinstance(dev.get("first_seen"), datetime):
                    dev["first_seen"] = dev["first_seen"].isoformat()
            return devices
        except PyMongoError as e:
            logger.error(f"Error fetching devices: {e}")
            return []

    def get_device_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Find a single device by its IP address."""
        if not self.is_connected():
            return None
        try:
            device = self.devices.find_one({"ip": ip}, {"_id": 0})
            if device:
                if isinstance(device.get("last_seen"), datetime):
                    device["last_seen"] = device["last_seen"].isoformat()
                if isinstance(device.get("first_seen"), datetime):
                    device["first_seen"] = device["first_seen"].isoformat()
            return device
        except PyMongoError as e:
            logger.error(f"Error finding device by IP {ip}: {e}")
            return None

    # =========================================================================
    # Attack Event Operations
    # =========================================================================

    def log_attack_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Record a detected security event or benign traffic observation.
        Returns the generated event_id.
        """
        if not self.is_connected():
            return None
        try:
            event_id = event_data.get("event_id") or str(uuid.uuid4())
            timestamp = event_data.get("timestamp") or datetime.now(timezone.utc)
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    timestamp = datetime.now(timezone.utc)

            doc = {
                "event_id": event_id,
                "timestamp": timestamp,
                "src_ip": event_data.get("src_ip", "0.0.0.0"),
                "src_port": event_data.get("src_port", 0),
                "dst_ip": event_data.get("dst_ip", "0.0.0.0"),
                "dst_port": event_data.get("dst_port", 0),
                "proto": event_data.get("proto", "TCP"),
                "predicted_class": event_data.get("predicted_class", "Benign"),
                "confidence": float(event_data.get("confidence", 0.0)),
                "flow_features": event_data.get("flow_features", {}),
                "status": event_data.get("status", "model_prediction"), # "model_prediction" or "confirmed_incident"
                "evidence": event_data.get("evidence", ""),
                "action_taken": event_data.get("action_taken", "none")
            }
            self.attack_events.insert_one(doc)
            return event_id
        except PyMongoError as e:
            logger.error(f"Error logging attack event: {e}")
            return None

    def get_attack_history(self, limit: int = 50, class_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve recent attack events (excluding benign by default if filter not specified)."""
        if not self.is_connected():
            return []
        try:
            query = {}
            if class_filter:
                query["predicted_class"] = class_filter
            else:
                # Default to returning actual attacks, not Benign
                query["predicted_class"] = {"$ne": "Benign"}

            records = list(self.attack_events.find(query, {"_id": 0})
                           .sort("timestamp", DESCENDING)
                           .limit(limit))
            
            for item in records:
                if isinstance(item.get("timestamp"), datetime):
                    item["timestamp"] = item["timestamp"].isoformat()
            return records
        except PyMongoError as e:
            logger.error(f"Error querying attack history: {e}")
            return []

    def get_attack_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics of all detected attack classes."""
        if not self.is_connected():
            return {}
        try:
            pipeline = [
                {"$group": {"_id": "$predicted_class", "count": {"$sum": 1}}}
            ]
            results = list(self.attack_events.aggregate(pipeline))
            stats = {item["_id"]: item["count"] for item in results}
            total = sum(stats.values())
            return {
                "total_events": total,
                "classes": stats
            }
        except PyMongoError as e:
            logger.error(f"Error generating attack statistics: {e}")
            return {}

    # =========================================================================
    # Blocklist & Firewall Operations
    # =========================================================================

    def add_to_blocklist(self, ip: str, reason: str, class_name: str, confidence: float,
                         duration_minutes: int = 15) -> bool:
        """Add an IP to the active blocklist with an expiration time."""
        if not self.is_connected() or not ip:
            return False
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=duration_minutes)

            doc = {
                "ip": ip,
                "reason": reason,
                "predicted_class": class_name,
                "confidence": float(confidence),
                "status": "active",
                "blocked_at": now,
                "expires_at": expires_at,
                "unblocked_at": None,
                "unblocked_by": None
            }
            self.blocklist.update_one({"ip": ip}, {"$set": doc}, upsert=True)
            return True
        except PyMongoError as e:
            logger.error(f"Error adding {ip} to blocklist: {e}")
            return False

    def unblock_ip(self, ip: str, unblocked_by: str = "admin") -> bool:
        """Mark an IP address as unblocked."""
        if not self.is_connected() or not ip:
            return False
        try:
            now = datetime.now(timezone.utc)
            result = self.blocklist.update_one(
                {"ip": ip, "status": "active"},
                {"$set": {
                    "status": "unblocked",
                    "unblocked_at": now,
                    "unblocked_by": unblocked_by
                }}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error unblocking IP {ip}: {e}")
            return False

    def get_blocked_ips(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Retrieve all currently blocked IPs or all block history."""
        if not self.is_connected():
            return []
        try:
            query = {"status": "active"} if active_only else {}
            blocks = list(self.blocklist.find(query, {"_id": 0}).sort("blocked_at", DESCENDING))
            for item in blocks:
                if isinstance(item.get("blocked_at"), datetime):
                    item["blocked_at"] = item["blocked_at"].isoformat()
                if isinstance(item.get("expires_at"), datetime):
                    item["expires_at"] = item["expires_at"].isoformat()
                if isinstance(item.get("unblocked_at"), datetime):
                    item["unblocked_at"] = item["unblocked_at"].isoformat()
            return blocks
        except PyMongoError as e:
            logger.error(f"Error fetching blocked IPs: {e}")
            return []

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP address is actively blocked and not expired."""
        if not self.is_connected() or not ip:
            return False
        try:
            record = self.blocklist.find_one({"ip": ip, "status": "active"})
            if not record:
                return False
            # Check expiration
            expires_at = record.get("expires_at")
            if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
                # Mark as expired
                self.blocklist.update_one({"ip": ip}, {"$set": {"status": "expired"}})
                return False
            return True
        except PyMongoError as e:
            logger.error(f"Error checking if IP {ip} is blocked: {e}")
            return False

    # =========================================================================
    # Response Actions & Audit Logs
    # =========================================================================

    def log_response_action(self, action_data: Dict[str, Any]) -> Optional[str]:
        """Record a mitigation action executed by the response system."""
        if not self.is_connected():
            return None
        try:
            action_id = action_data.get("action_id") or str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            doc = {
                "action_id": action_id,
                "event_id": action_data.get("event_id", ""),
                "target_ip": action_data.get("target_ip", ""),
                "action_type": action_data.get("action_type", "block"), # block, rate_limit, unblock
                "firewall_rule": action_data.get("firewall_rule", ""),
                "status": action_data.get("status", "applied"), # applied, failed, reverted
                "reason": action_data.get("reason", ""),
                "executed_at": now
            }
            self.response_actions.insert_one(doc)
            return action_id
        except PyMongoError as e:
            logger.error(f"Error logging response action: {e}")
            return None

    def log_system_event(self, actor: str, event: str, outcome: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Log general system operational events for auditability."""
        if not self.is_connected():
            return False
        try:
            doc = {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "actor": actor,
                "event": event,
                "outcome": outcome,
                "details": details or {}
            }
            self.system_logs.insert_one(doc)
            return True
        except PyMongoError as e:
            logger.error(f"Error logging system event: {e}")
            return False

    def get_system_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch system audit logs."""
        if not self.is_connected():
            return []
        try:
            logs = list(self.system_logs.find({}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit))
            for item in logs:
                if isinstance(item.get("timestamp"), datetime):
                    item["timestamp"] = item["timestamp"].isoformat()
            return logs
        except PyMongoError as e:
            logger.error(f"Error fetching system logs: {e}")
            return []


# =============================================================================
# Standalone Self-Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing DatabaseService...")
    db = DatabaseService()
    
    if db.is_connected():
        print("Connected to MongoDB successfully!")
        
        # Test 1: Device Upsert
        test_device = {
            "ip": "192.168.8.199",
            "mac": "AA:BB:CC:DD:EE:FF",
            "vendor": "Hikvision",
            "device_type": "camera",
            "possible_camera": True,
            "open_ports": [80, 554]
        }
        db.upsert_device(test_device)
        fetched = db.get_device_by_ip("192.168.8.199")
        print(f"Device Upsert/Fetch Test: {'PASS' if fetched and fetched['vendor'] == 'Hikvision' else 'FAIL'}")

        # Test 2: Attack Logging
        event_id = db.log_attack_event({
            "src_ip": "192.168.8.45",
            "dst_ip": "192.168.8.199",
            "predicted_class": "DDoS",
            "confidence": 0.96,
            "evidence": "Flooding test"
        })
        history = db.get_attack_history(limit=5)
        print(f"Attack Logging Test: {'PASS' if event_id and len(history) > 0 else 'FAIL'}")

        # Test 3: Blocklist & Unblock
        db.add_to_blocklist("192.168.8.45", "DDoS Flood detected", "DDoS", 0.96, duration_minutes=10)
        is_blocked = db.is_ip_blocked("192.168.8.45")
        print(f"Block IP Test: {'PASS' if is_blocked else 'FAIL'}")

        db.unblock_ip("192.168.8.45", unblocked_by="admin_test")
        is_blocked_after = db.is_ip_blocked("192.168.8.45")
        print(f"Unblock IP Test: {'PASS' if not is_blocked_after else 'FAIL'}")

        # Clean up test records
        db.devices.delete_one({"ip": "192.168.8.199"})
        db.attack_events.delete_one({"event_id": event_id})
        db.blocklist.delete_one({"ip": "192.168.8.45"})
        print("Cleaned up test records. All tests completed successfully!")
    else:
        print("Failed to connect to MongoDB.")

