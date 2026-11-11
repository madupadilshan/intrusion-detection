"""core_engine/zeek_adapter.py - Real-Time Streaming Zeek Log Adapter & Telemetry Ingestion Engine.

Governing Standards:
- Group 03 Proposal: Sections 3.3, 3.5, 3.7; Figure 3; Table 7 (FR-01)
- Step-by-Step Guide: Step 21 (Build the Zeek adapter)
- Decision Log: D-025

Responsibilities:
1. Stream/tail Zeek JSON conn.log in real time (following new records as written).
2. Robust file rotation detection (POSIX inode checking + truncation/re-creation checks for Windows).
3. Offset & state persistence across sensor restarts (Step 38 crash recovery).
4. Preserve incomplete flows (zero-payload, unanswered SYNs) with is_incomplete flag for ml_engine.features.
5. Telemetry enrichment:
   - observed_at: UTC ISO-8601 observation timestamp.
   - traffic_direction: inbound, outbound, internal, or external based on CIDR subnets.
   - device_tag: IP-camera / IoT device inventory attribution.
6. Micro-batching engine: buffers flows by batch_size or batch_timeout to maintain high throughput during floods.
7. Telemetry metrics & system health counters (FR-01, Section 5.3, Step 37).
8. One-shot static log reader for PCAP replay evaluation (zeek -r sample.pcap).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from enum import Enum
import ipaddress
import json
import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import yaml

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.features import FEATURE_COLUMNS, make_features
from ml_engine.window_features import WINDOW_FEATURES, WindowState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [zeek_adapter] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("zeek_adapter")

# Default paths and configurations
# IDS_SETTINGS_FILE lets a test setup (e.g. lab_virtual/) use its own settings file.
DEFAULT_SETTINGS_PATH = Path(os.getenv("IDS_SETTINGS_FILE") or PROJECT_ROOT / "config" / "settings.yaml")
DEFAULT_STATE_PATH = PROJECT_ROOT / "data" / "local" / ".zeek_adapter_state.json"
DEFAULT_CONN_LOG = PROJECT_ROOT / "sensor" / "logs" / "conn.log"


class NetworkDirection(str, Enum):
    """Network flow direction relative to monitored local subnets."""
    INTERNAL = "internal"
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    EXTERNAL = "external"


class DirectionClassifier:
    """Classifies network flow direction using configured local CIDR subnets."""

    def __init__(self, local_networks: Optional[List[str]] = None) -> None:
        self.networks: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = []
        subnets = local_networks or ["192.168.50.0/24", "192.168.1.0/24"]
        for cidr in subnets:
            try:
                self.networks.append(ipaddress.ip_network(str(cidr).strip(), strict=False))
            except ValueError as e:
                logger.warning(f"Invalid CIDR subnet ignored: {cidr} ({e})")

    def is_local(self, ip_str: Optional[str]) -> bool:
        """Check if an IP string belongs to any configured local subnet."""
        if not ip_str or not isinstance(ip_str, str):
            return False
        clean_ip = ip_str.strip()
        # Strip port if accidentally formatted as ip:port
        if ":" in clean_ip and not clean_ip.count(":") > 1:
            clean_ip = clean_ip.split(":")[0]
        try:
            ip_obj = ipaddress.ip_address(clean_ip)
            return any(ip_obj in net for net in self.networks)
        except ValueError:
            return False

    def classify(self, orig_h: Optional[str], resp_h: Optional[str]) -> NetworkDirection:
        """Determine flow direction relative to the protected local network."""
        orig_local = self.is_local(orig_h)
        resp_local = self.is_local(resp_h)

        if orig_local and resp_local:
            return NetworkDirection.INTERNAL
        elif orig_local and not resp_local:
            return NetworkDirection.OUTBOUND
        elif not orig_local and resp_local:
            return NetworkDirection.INBOUND
        else:
            return NetworkDirection.EXTERNAL


class DeviceTagger:
    """Tags flows with known device inventory metadata."""

    def __init__(self, known_devices: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        # Default device inventory matching Proposal 3.8 and Step 4
        self.devices: Dict[str, Dict[str, Any]] = known_devices or {
            "192.168.50.60": {
                "device_id": "cam_01",
                "name": "Tapo C200",
                "type": "ip_camera",
                "role": "monitored_device",
            },
            "192.168.50.101": {
                "device_id": "cam_01",
                "name": "Tapo C200 (Sensor Lab)",
                "type": "ip_camera",
                "role": "monitored_device",
            },
            "192.168.50.20": {
                "device_id": "nvr_01",
                "name": "Lab NVR",
                "type": "nvr",
                "role": "video_recorder",
            },
            "192.168.50.200": {
                "device_id": "nvr_01",
                "name": "Lab NVR (Streaming Target)",
                "type": "nvr",
                "role": "video_recorder",
            },
            "192.168.50.1": {
                "device_id": "gw_01",
                "name": "Gateway Router",
                "type": "router",
                "role": "gateway",
            },
            "192.168.50.5": {
                "device_id": "ids_01",
                "name": "IDS Sensor",
                "type": "sensor",
                "role": "security_monitor",
            },
            "192.168.50.10": {
                "device_id": "admin_01",
                "name": "Admin Workstation",
                "type": "workstation",
                "role": "management",
            },
            # Development/home lab alias
            "192.168.1.150": {
                "device_id": "cam_01_dev",
                "name": "Tapo C200 (Dev Lab)",
                "type": "ip_camera",
                "role": "monitored_device",
            },
        }

    def tag(self, orig_h: Optional[str], resp_h: Optional[str]) -> Optional[Dict[str, Any]]:
        """Identify if flow originates from or terminates at a known monitored device."""
        if orig_h and orig_h in self.devices:
            meta = dict(self.devices[orig_h])
            meta["direction_role"] = "source"
            meta["matched_ip"] = orig_h
            return meta
        elif resp_h and resp_h in self.devices:
            meta = dict(self.devices[resp_h])
            meta["direction_role"] = "destination"
            meta["matched_ip"] = resp_h
            return meta
        return None


class StateStore:
    """Manages persistent tracking of file offsets and processed lines."""

    def __init__(self, state_path: Union[str, Path]) -> None:
        self.state_path = Path(state_path)

    def load(self) -> Dict[str, Any]:
        """Load state from disk. Returns empty dict if absent or corrupted."""
        if not self.state_path.exists():
            return {}
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load state from {self.state_path}: {e}")
            return {}

    def save(self, state: Dict[str, Any]) -> bool:
        """Atomically persist state to disk via temporary file."""
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.state_path.with_suffix(".tmp")
            state["saved_at"] = datetime.now(timezone.utc).isoformat()
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            # Atomic replace
            os.replace(tmp_path, self.state_path)
            return True
        except Exception as e:
            logger.error(f"Failed to persist state to {self.state_path}: {e}")
            return False

    def clear(self) -> None:
        """Remove state file."""
        try:
            if self.state_path.exists():
                self.state_path.unlink()
        except Exception as e:
            logger.warning(f"Error removing state file {self.state_path}: {e}")


class AdapterMetrics:
    """Thread-safe statistics counter for telemetry and health monitoring."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.lines_read: int = 0
        self.flows_parsed: int = 0
        self.flows_corrupted: int = 0
        self.batches_emitted: int = 0
        self.bytes_read: int = 0
        self.start_time: float = time.time()
        self.last_event_time: Optional[float] = None

    def record_read(self, byte_count: int) -> None:
        with self._lock:
            self.lines_read += 1
            self.bytes_read += byte_count

    def record_parsed(self, event_ts: Optional[float] = None) -> None:
        with self._lock:
            self.flows_parsed += 1
            if event_ts:
                self.last_event_time = event_ts

    def record_corrupted(self) -> None:
        with self._lock:
            self.flows_corrupted += 1

    def record_batch(self) -> None:
        with self._lock:
            self.batches_emitted += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Return snapshot dictionary of current adapter telemetry."""
        with self._lock:
            uptime = max(0.001, time.time() - self.start_time)
            fps = self.flows_parsed / uptime
            error_rate = (self.flows_corrupted / max(1, self.lines_read)) * 100.0
            return {
                "lines_read": self.lines_read,
                "flows_parsed": self.flows_parsed,
                "flows_corrupted": self.flows_corrupted,
                "batches_emitted": self.batches_emitted,
                "bytes_read": self.bytes_read,
                "uptime_seconds": round(uptime, 2),
                "flows_per_second": round(fps, 2),
                "error_rate_pct": round(error_rate, 4),
                "last_event_time": self.last_event_time,
            }


def is_incomplete_flow(record: Dict[str, Any]) -> bool:
    """
    Check if a flow represents an incomplete connection attempt.
    Matches logic in ml_engine.features.make_features (Proposal Table 6).
    """
    conn_state = str(record.get("conn_state", "")).strip().upper()
    incomplete_states = {"S0", "REJ", "RSTOS0", "RSTRH", "SH", "SHR"}
    if conn_state in incomplete_states:
        return True

    try:
        resp_pkts = float(record.get("resp_pkts") or 0)
        if resp_pkts == 0:
            return True
    except (ValueError, TypeError):
        pass

    try:
        duration = float(record.get("duration") or 0.0)
        orig_b = float(record.get("orig_bytes") or 0)
        resp_b = float(record.get("resp_bytes") or 0)
        if duration == 0.0 and (orig_b == 0 or resp_b == 0):
            return True
    except (ValueError, TypeError):
        pass

    return False


class ZeekLogFollower:
    """
    Tails a continuous JSON log file with rotation detection and partial-line safety.
    Cross-platform support: works on POSIX (inode change) and Windows (size/mtime changes).
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        poll_interval: float = 0.05,
        state_store: Optional[StateStore] = None,
    ) -> None:
        self.file_path = Path(file_path).resolve()
        self.poll_interval = poll_interval
        self.state_store = state_store
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Signal follower to stop following."""
        self._stop_event.set()

    @property
    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def _get_file_stat(self) -> Tuple[int, int, float]:
        """Return (inode, size, mtime) safely, returning (0, 0, 0.0) if missing."""
        try:
            st = self.file_path.stat()
            inode = getattr(st, "st_ino", 0)
            return inode, st.st_size, st.st_mtime
        except (FileNotFoundError, PermissionError):
            return 0, 0, 0.0

    def follow(
        self,
        seek_end: bool = False,
        stop_event: Optional[threading.Event] = None,
        yield_idle: bool = False,
    ) -> Generator[Tuple[Optional[str], int], None, None]:
        """
        Yield (raw_line, byte_offset) as new complete lines are appended to the log.
        If yield_idle=True, yields (None, current_offset) on EOF poll ticks for batch timers.
        """
        active_stop = stop_event or self._stop_event

        # 1. Wait until file exists
        while not active_stop.is_set():
            if self.file_path.exists():
                break
            time.sleep(self.poll_interval)

        if active_stop.is_set():
            return

        # 2. Determine initial starting offset
        saved_state = self.state_store.load() if self.state_store else {}
        curr_inode, curr_size, curr_mtime = self._get_file_stat()

        initial_offset = 0
        if saved_state.get("file_path") == str(self.file_path):
            saved_offset = saved_state.get("offset", 0)
            saved_inode = saved_state.get("inode", 0)
            # Check if saved offset is valid (file size >= saved_offset and inode matches if non-zero)
            if curr_size >= saved_offset and (saved_inode == 0 or curr_inode == 0 or saved_inode == curr_inode):
                initial_offset = saved_offset
                logger.info(f"Resuming {self.file_path.name} from saved offset: {initial_offset} bytes")
        elif seek_end and curr_size > 0:
            initial_offset = curr_size
            logger.info(f"Seeking to end of {self.file_path.name}: {initial_offset} bytes")

        # 3. Open file and follow
        f = None
        try:
            f = open(self.file_path, "r", encoding="utf-8", errors="replace")
            if initial_offset > 0:
                f.seek(initial_offset)
            current_offset = f.tell()
            tracked_inode = curr_inode

            while not active_stop.is_set():
                line = f.readline()
                if line:
                    if line.endswith("\n"):
                        current_offset = f.tell()
                        yield line, current_offset
                    else:
                        # Partial write in progress: rewind to line start and wait for writer to flush
                        f.seek(current_offset)
                        time.sleep(self.poll_interval)
                else:
                    # EOF reached. Check for file rotation or truncation.
                    new_inode, new_size, _ = self._get_file_stat()

                    rotated = False
                    if new_inode != 0 and tracked_inode != 0 and new_inode != tracked_inode:
                        logger.info(f"Log rotation detected: inode changed from {tracked_inode} to {new_inode}")
                        rotated = True
                    elif new_size < current_offset:
                        logger.info(f"Log truncation detected: file shrunk from {current_offset} to {new_size}")
                        rotated = True

                    if rotated:
                        f.close()
                        # Reopen new file from beginning
                        try:
                            f = open(self.file_path, "r", encoding="utf-8", errors="replace")
                            tracked_inode, _, _ = self._get_file_stat()
                            current_offset = 0
                            continue
                        except (FileNotFoundError, PermissionError):
                            pass

                    time.sleep(self.poll_interval)
                    if yield_idle:
                        yield None, current_offset
        finally:
            if f and not f.closed:
                f.close()


class ZeekAdapter:
    """
    Main Telemetry Adapter connecting Zeek conn.log to the ML Engine & Core Services.
    Handles JSON parsing, schema normalization, metadata enrichment, micro-batching,
    and state persistence.
    """

    def __init__(
        self,
        conn_log_path: Optional[Union[str, Path]] = None,
        settings_path: Optional[Union[str, Path]] = None,
        local_networks: Optional[List[str]] = None,
        known_devices: Optional[Dict[str, Dict[str, Any]]] = None,
        state_path: Optional[Union[str, Path]] = None,
        batch_size: int = 100,
        batch_timeout: float = 0.5,
        enable_state_persistence: bool = True,
    ) -> None:
        self.settings = self._load_settings(settings_path)

        # 1. Resolve conn_log_path
        if conn_log_path:
            self.conn_log_path = Path(conn_log_path)
        else:
            configured_path = self.settings.get("zeek", {}).get("conn_log_path")
            if configured_path:
                p = Path(configured_path)
                # a relative path in settings.yaml starts at the project folder
                self.conn_log_path = p if p.is_absolute() else PROJECT_ROOT / p
            else:
                self.conn_log_path = DEFAULT_CONN_LOG

        # 2. Resolve subnets and devices
        subnets = local_networks or self.settings.get("lab", {}).get("local_networks")
        self.direction_classifier = DirectionClassifier(subnets)
        self.device_tagger = DeviceTagger(known_devices)

        # 3. Batching parameters
        self.batch_size = max(1, batch_size)
        self.batch_timeout = max(0.01, batch_timeout)

        # 4. State store
        self.enable_state_persistence = enable_state_persistence
        st_path = state_path or self.settings.get("zeek", {}).get("state_path") or DEFAULT_STATE_PATH
        self.state_store = StateStore(st_path) if enable_state_persistence else None

        # 5. Metrics counter
        self.metrics = AdapterMetrics()

        # 6. Window features (D-051): the same WindowState code as in training, fed in the
        #    order Zeek writes the lines. It starts empty after a restart.
        self.window_state = WindowState()
        self._stop_event = threading.Event()

    def _load_settings(self, settings_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        path = Path(settings_path) if settings_path else DEFAULT_SETTINGS_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed loading settings from {path}: {e}")
        return {}

    def stop(self) -> None:
        """Signal adapter to terminate active tailing loops."""
        self._stop_event.set()

    def reset_state(self) -> None:
        """Clear persistent offset state and the window-feature memory."""
        if self.state_store:
            self.state_store.clear()
        self.window_state.reset()

    def parse_and_enrich(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse raw Zeek JSON line, normalize schema variations, and enrich with telemetry metadata.
        Returns None for malformed JSON or empty lines.
        """
        line_str = line.strip()
        if not line_str:
            return None

        self.metrics.record_read(len(line))
        try:
            record = json.loads(line_str)
        except json.JSONDecodeError:
            self.metrics.record_corrupted()
            return None

        if not isinstance(record, dict):
            self.metrics.record_corrupted()
            return None

        # Normalize nested id structure: {"id": {"orig_h": ...}} -> {"id.orig_h": ...}
        if "id" in record and isinstance(record["id"], dict):
            nested_id = record.pop("id")
            for sub_k, sub_v in nested_id.items():
                record[f"id.{sub_k}"] = sub_v

        # Normalize underscore aliases
        aliases = {
            "id_orig_h": "id.orig_h",
            "id_orig_p": "id.orig_p",
            "id_resp_h": "id.resp_h",
            "id_resp_p": "id.resp_p",
        }
        for old_k, new_k in aliases.items():
            if old_k in record and new_k not in record:
                record[new_k] = record[old_k]

        orig_h = str(record.get("id.orig_h", ""))
        resp_h = str(record.get("id.resp_h", ""))

        # Metadata enrichment
        direction = self.direction_classifier.classify(orig_h, resp_h)
        device_meta = self.device_tagger.tag(orig_h, resp_h)
        incomplete = is_incomplete_flow(record)
        window_values = self.window_state.update(
            record.get("id.orig_h"), record.get("id.resp_h"), record.get("id.resp_p"), record.get("ts"),
            record.get("proto"), record.get("conn_state"),
        )

        now = datetime.now(timezone.utc)
        record["observed_at"] = now.isoformat()
        record["observed_epoch"] = now.timestamp()
        record["traffic_direction"] = direction.value
        record["device_tag"] = device_meta
        record["is_incomplete"] = incomplete
        for name, value in zip(WINDOW_FEATURES, window_values):
            record[name] = value

        # Record metrics
        event_ts = record.get("ts")
        self.metrics.record_parsed(float(event_ts) if event_ts is not None else now.timestamp())
        return record

    def read_file(self, file_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        One-shot synchronous reader for static conn.log files (e.g. PCAP evaluations).
        Returns list of enriched flow records.
        """
        target_path = Path(file_path or self.conn_log_path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Zeek log file not found: {target_path}")

        flows: List[Dict[str, Any]] = []
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                enriched = self.parse_and_enrich(line)
                if enriched:
                    flows.append(enriched)
        return flows

    def tail_flows(
        self,
        seek_end: bool = False,
        stop_event: Optional[threading.Event] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streaming generator yielding individual enriched flows in real-time as they are written.
        """
        active_stop = stop_event or self._stop_event
        follower = ZeekLogFollower(self.conn_log_path, state_store=self.state_store)

        for line, offset in follower.follow(seek_end=seek_end, stop_event=active_stop, yield_idle=False):
            if line is not None:
                enriched = self.parse_and_enrich(line)
                if enriched:
                    if self.state_store:
                        self._persist_offset(offset, enriched.get("ts"))
                    yield enriched

    def tail_batches(
        self,
        seek_end: bool = False,
        stop_event: Optional[threading.Event] = None,
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Streaming generator yielding micro-batches of enriched flows.
        Flushes when len(batch) >= batch_size OR elapsed_time >= batch_timeout.
        """
        active_stop = stop_event or self._stop_event
        follower = ZeekLogFollower(self.conn_log_path, state_store=self.state_store)

        batch: List[Dict[str, Any]] = []
        last_flush = time.time()
        last_offset = 0
        last_flow_ts = None

        for line, offset in follower.follow(seek_end=seek_end, stop_event=active_stop, yield_idle=True):
            if line is not None:
                enriched = self.parse_and_enrich(line)
                if enriched:
                    batch.append(enriched)
                    last_offset = offset
                    last_flow_ts = enriched.get("ts")

                # Check batch_size condition
                if len(batch) >= self.batch_size:
                    self.metrics.record_batch()
                    if self.state_store and last_offset > 0:
                        self._persist_offset(last_offset, last_flow_ts)
                    yield list(batch)
                    batch.clear()
                    last_flush = time.time()
            else:
                # Idle tick on EOF poll: check batch_timeout condition
                if batch and (time.time() - last_flush >= self.batch_timeout):
                    self.metrics.record_batch()
                    if self.state_store and last_offset > 0:
                        self._persist_offset(last_offset, last_flow_ts)
                    yield list(batch)
                    batch.clear()
                    last_flush = time.time()

        # Flush any remaining items on shutdown
        if batch:
            self.metrics.record_batch()
            if self.state_store and last_offset > 0:
                self._persist_offset(last_offset, last_flow_ts)
            yield list(batch)

    def _persist_offset(self, offset: int, last_flow_ts: Optional[float] = None) -> None:
        """Save current offset to state file."""
        if not self.state_store:
            return
        curr_ino = 0
        try:
            curr_ino = getattr(self.conn_log_path.stat(), "st_ino", 0)
        except Exception:
            pass

        state = {
            "file_path": str(self.conn_log_path.resolve()),
            "inode": curr_ino,
            "offset": offset,
            "lines_read": self.metrics.lines_read,
            "flows_parsed": self.metrics.flows_parsed,
            "last_flow_ts": last_flow_ts,
        }
        self.state_store.save(state)

    def to_feature_dataframe(self, flows: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert a batch of enriched flows into the locked feature matrix X (26 columns, D-051)
        using the unified ml_engine.features.make_features engine.
        """
        if not flows:
            return pd.DataFrame(columns=FEATURE_COLUMNS)
        return make_features(flows)

    def get_metrics(self) -> Dict[str, Any]:
        """Return current adapter telemetry."""
        return self.metrics.get_metrics()


def main() -> None:
    """CLI entry point for running or testing the Zeek adapter."""
    parser = argparse.ArgumentParser(
        description="Zeek conn.log Streaming Adapter and Telemetry Ingestion Engine."
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default=str(DEFAULT_CONN_LOG),
        help=f"Path to Zeek conn.log (default: {DEFAULT_CONN_LOG})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Micro-batch size for downstream ingestion (default: 50)",
    )
    parser.add_argument(
        "--batch-timeout",
        type=float,
        default=0.5,
        help="Batch flush timeout in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Read from the beginning of the file instead of seeking to EOF",
    )
    parser.add_argument(
        "--one-shot",
        action="store_true",
        help="Read the entire file once and print summary statistics",
    )
    args = parser.parse_args()

    adapter = ZeekAdapter(
        conn_log_path=args.log_path,
        batch_size=args.batch_size,
        batch_timeout=args.batch_timeout,
    )

    if args.one_shot:
        logger.info(f"Executing one-shot static evaluation on: {args.log_path}")
        flows = adapter.read_file()
        feat_df = adapter.to_feature_dataframe(flows)
        metrics = adapter.get_metrics()
        print("\n=== One-Shot Ingestion Summary ===")
        print(f"Total Flows Parsed: {len(flows)}")
        print(f"Feature Matrix Shape: {feat_df.shape}")
        print(f"Feature Matrix Nulls: {feat_df.isna().sum().sum()}")
        print(f"Adapter Telemetry: {json.dumps(metrics, indent=2)}")
        return

    logger.info(f"Starting live streaming adapter on: {args.log_path}")
    logger.info(f"Configuration: batch_size={args.batch_size}, batch_timeout={args.batch_timeout}s")
    print("Press Ctrl+C to terminate live tailing...\n")

    try:
        for batch in adapter.tail_batches(seek_end=not args.from_beginning):
            feat_df = adapter.to_feature_dataframe(batch)
            metrics = adapter.get_metrics()
            print(
                f"[{metrics['uptime_seconds']}s] Batch of {len(batch)} flows emitted | "
                f"Feature Matrix: {feat_df.shape} | Total Parsed: {metrics['flows_parsed']} | "
                f"Rate: {metrics['flows_per_second']} fps"
            )
    except KeyboardInterrupt:
        logger.info("Termination signal received. Stopping adapter...")
        adapter.stop()


if __name__ == "__main__":
    main()
