#!/usr/bin/env bash
# ==============================================================================
# lab_hardware/inline_bridge.sh - Inline mode (proposal Figure 5, right side; guide Step 5 item 4).
# The sensor becomes a transparent bridge (br0) between the camera switch and the router, and
# blocks with its own nftables (sensor/ids_inline.nft, table "bridge ids").
#
#   sudo bash lab_hardware/inline_bridge.sh up   <port-to-switch> <port-to-router>
#   sudo bash lab_hardware/inline_bridge.sh down <port-to-switch> <port-to-router>
#   sudo bash lab_hardware/inline_bridge.sh status
#
# For inline mode, also change lab_hardware/settings.hardware.yaml:
#   response.deployment_mode: inline, response.adapter: nftables,
#   firewall.table_family: bridge, firewall.use_sudo: true, lab.sensor_mirror_interface: br0
#
# BYPASS PLAN (proposal Table 11: "Have a bypass and recovery plan for inline tests"):
#   If the sensor fails, unplug both cables from the sensor and plug the switch cable straight
#   into the router. The network works again at once. Test this once and write it in
#   docs/lab_network.md and the logbook (guide Step 38 item 4).
# ==============================================================================
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cmd="${1:-status}"

case "$cmd" in
  up)
    A="${2:?port to the switch}"; B="${3:?port to the router}"
    ip link add name br0 type bridge 2>/dev/null || true
    for p in "$A" "$B"; do
        ip addr flush dev "$p"
        ip link set "$p" master br0
        ip link set "$p" up
        ethtool -K "$p" gro off lro off || true
    done
    ip link set br0 up
    # bridged IPv4 must pass the bridge family hooks (the ids table uses "bridge" family)
    nft -c -f "$PROJECT/sensor/ids_inline.nft"
    nft delete table bridge ids 2>/dev/null || true
    nft -f "$PROJECT/sensor/ids_inline.nft"
    echo "br0 up with $A + $B; nftables table 'bridge ids' loaded. Run Zeek on br0."
    ;;
  down)
    A="${2:?port to the switch}"; B="${3:?port to the router}"
    nft delete table bridge ids 2>/dev/null || true
    for p in "$A" "$B"; do ip link set "$p" nomaster || true; done
    ip link set br0 down 2>/dev/null || true
    ip link delete br0 type bridge 2>/dev/null || true
    echo "bridge removed; use the bypass cable or passive mode."
    ;;
  status)
    ip -br link show master br0 2>/dev/null || echo "no br0"
    nft list table bridge ids 2>/dev/null | head -30 || echo "no bridge ids table"
    ;;
  *) echo "usage: $0 up|down <port-to-switch> <port-to-router> | status"; exit 1 ;;
esac
