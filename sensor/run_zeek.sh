#!/usr/bin/env bash
# ==============================================================================
# sensor/run_zeek.sh - Launch and Manage Zeek Sensor Daemon
# ==============================================================================
# Governing Standards:
# - Research Proposal: Sections 3.3, 3.5, 3.7; Table 7 (FR-01); Table 8
# - Step-by-Step Guide: Step 19 (Run Zeek on the sensor)
#
# Usage:
#   sudo ./sensor/run_zeek.sh --interface eth1 [--log-dir /var/log/ids-zeek] [--daemon]
#   sudo ./sensor/run_zeek.sh --pcap sample.pcap [--log-dir ./sensor/logs]
#   sudo ./sensor/run_zeek.sh --stop [--log-dir /var/log/ids-zeek]
#   sudo ./sensor/run_zeek.sh --status
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ZEEK_CONFIG="${SCRIPT_DIR}/local.zeek"

INTERFACE=""
PCAP_FILE=""
LOG_DIR="/var/log/ids-zeek"
DAEMON_MODE=false
STOP_MODE=false
STATUS_MODE=false

# Locate Zeek binary
ZEEK_BIN=""
if command -v zeek >/dev/null 2>&1; then
    ZEEK_BIN="$(command -v zeek)"
elif [[ -x "/opt/zeek/bin/zeek" ]]; then
    ZEEK_BIN="/opt/zeek/bin/zeek"
elif [[ -x "/usr/local/zeek/bin/zeek" ]]; then
    ZEEK_BIN="/usr/local/zeek/bin/zeek"
fi

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -i, --interface <iface>   Network interface to monitor (e.g. eth1, br0)
  -r, --pcap <file.pcap>    Replay and extract flows from an offline PCAP file
  -l, --log-dir <dir>       Directory for output logs (default: /var/log/ids-zeek)
  -d, --daemon              Run Zeek process in the background
  -s, --status              Check if Zeek sensor process is running
  -k, --stop                Stop running Zeek sensor process
  -h, --help                Show this help message
EOF
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--interface)
            INTERFACE="$2"
            shift 2
            ;;
        -r|--pcap)
            PCAP_FILE="$2"
            shift 2
            ;;
        -l|--log-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        -d|--daemon)
            DAEMON_MODE=true
            shift
            ;;
        -s|--status)
            STATUS_MODE=true
            shift
            ;;
        -k|--stop)
            STOP_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $1" >&2
            show_help
            exit 1
            ;;
    esac
done

PID_FILE="${LOG_DIR}/zeek.pid"

# Handle --status
if [[ "$STATUS_MODE" == true ]]; then
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "[INFO] Zeek sensor is RUNNING with PID $(cat "$PID_FILE"). Log dir: ${LOG_DIR}"
        exit 0
    else
        echo "[INFO] Zeek sensor is NOT running."
        exit 1
    fi
fi

# Handle --stop
if [[ "$STOP_MODE" == true ]]; then
    if [[ -f "$PID_FILE" ]]; then
        PID="$(cat "$PID_FILE")"
        if kill -0 "$PID" 2>/dev/null; then
            echo "[INFO] Stopping Zeek sensor (PID ${PID})..."
            kill "$PID" || true
            sleep 1
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID" || true
            fi
            echo "[INFO] Zeek sensor stopped."
        else
            echo "[WARN] PID file exists but process ${PID} is not running."
        fi
        rm -f "$PID_FILE"
    else
        echo "[INFO] No PID file found at ${PID_FILE}. Attempting pkill..."
        pkill -f "zeek.*local.zeek" || true
    fi
    exit 0
fi

# Verify Zeek binary exists
if [[ -z "$ZEEK_BIN" ]]; then
    echo "Error: Zeek binary not found in PATH, /opt/zeek/bin, or /usr/local/zeek/bin." >&2
    echo "Please install Zeek (Step 3b): sudo apt install -y zeek or install from https://zeek.org" >&2
    exit 1
fi

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Verify either interface or pcap is specified
if [[ -z "$INTERFACE" && -z "$PCAP_FILE" ]]; then
    echo "Error: You must specify either --interface <iface> or --pcap <file.pcap>." >&2
    show_help
    exit 1
fi

echo "=========================================================="
echo " Starting Zeek Network Security Monitor Sensor (Step 19)  "
echo "=========================================================="
echo "Zeek Binary:     ${ZEEK_BIN} ($("${ZEEK_BIN}" --version 2>&1 | head -n 1))"
echo "Configuration:   ${ZEEK_CONFIG}"
echo "Log Directory:   ${LOG_DIR}"

cd "$LOG_DIR"

if [[ -n "$PCAP_FILE" ]]; then
    if [[ ! -f "$PCAP_FILE" ]]; then
        echo "Error: PCAP file not found: $PCAP_FILE" >&2
        exit 1
    fi
    echo "Mode:            PCAP Offline Replay: ${PCAP_FILE}"
    echo "[INFO] Processing PCAP..."
    "$ZEEK_BIN" -C -r "$PCAP_FILE" "$ZEEK_CONFIG"
    echo "[INFO] PCAP processing complete. Connection logs written to: ${LOG_DIR}/conn.log"
    exit 0
fi

if [[ -n "$INTERFACE" ]]; then
    echo "Mode:            Live Traffic Capture on Interface: ${INTERFACE}"
    echo "Checksums:       Ignored (-C enabled for port mirroring)"
    
    if [[ "$DAEMON_MODE" == true ]]; then
        echo "[INFO] Starting Zeek in background daemon mode..."
        nohup "$ZEEK_BIN" -C -i "$INTERFACE" "$ZEEK_CONFIG" > "${LOG_DIR}/zeek_stdout.log" 2>&1 &
        ZEEK_PID=$!
        echo "$ZEEK_PID" > "$PID_FILE"
        echo "[INFO] Zeek sensor started with PID ${ZEEK_PID}."
        echo "[INFO] Monitoring live flows in: ${LOG_DIR}/conn.log"
    else
        echo "[INFO] Starting Zeek in foreground mode (Press Ctrl+C to stop)..."
        exec "$ZEEK_BIN" -C -i "$INTERFACE" "$ZEEK_CONFIG"
    fi
fi
