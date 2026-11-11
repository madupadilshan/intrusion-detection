#!/usr/bin/env bash
# ==============================================================================
# lab_hardware/install_services.sh - Optional: start Zeek and the IDS backend at boot (systemd).
# Run on the sensor, in the project folder:  sudo bash lab_hardware/install_services.sh
# The backend service uses lab_hardware/runtime_settings.yaml. Make it first with
#   .venv/bin/python lab_hardware/hwlab.py ids-start --auto-response off   (then ids-stop)
# Automatic response stays as that file says; for planned tests use hwlab.py instead.
# Remove:  sudo systemctl disable --now ids-zeek ids-backend && sudo rm /etc/systemd/system/ids-*.service
# ==============================================================================
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_NAME="${SUDO_USER:-$USER}"
IFACE="$(python3 -c "import yaml;print(yaml.safe_load(open('$PROJECT/lab_hardware/settings.hardware.yaml'))['lab']['sensor_mirror_interface'])" 2>/dev/null \
        || grep -oP 'sensor_mirror_interface:\s*"\K[^"]+' "$PROJECT/lab_hardware/settings.hardware.yaml")"

cat > /etc/systemd/system/ids-zeek.service <<EOF
[Unit]
Description=Zeek on the IDS mirror port ($IFACE)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/var/log/ids-zeek
ExecStartPre=/usr/sbin/ip link set $IFACE up
ExecStartPre=-/usr/sbin/ethtool -K $IFACE gro off lro off
ExecStart=/opt/zeek/bin/zeek -C -i $IFACE $PROJECT/sensor/local.zeek
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/ids-backend.service <<EOF
[Unit]
Description=IP-camera IDS backend (detector, decision engine, dashboard on port 5000)
After=network-online.target mongod.service ids-zeek.service
Wants=mongod.service

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT
Environment=IDS_SETTINGS_FILE=$PROJECT/lab_hardware/runtime_settings.yaml
Environment=HOST=0.0.0.0
Environment=PORT=5000
ExecStart=$PROJECT/.venv/bin/python -m core_engine.app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ids-zeek ids-backend
systemctl --no-pager status ids-zeek ids-backend | head -20
