#!/usr/bin/env bash
# ==============================================================================
# lab_hardware/install_sensor.sh - Install the Linux sensor (guide Step 3b).
# Ubuntu 22.04 LTS (same Python 3.10 as the development PC). Run ONCE, in the project
# folder, while the sensor still has internet access (before it joins the lab):
#     bash lab_hardware/install_sensor.sh
# Then disconnect the sensor from the internet and connect it to the lab (guide Step 5).
#
# Sources (checked 11 Nov 2026):
#   Zeek binary packages: https://docs.zeek.org/en/current/install.html  (LTS line zeek-8.0, in /opt/zeek)
#   MongoDB 8.0 on Ubuntu 22.04: https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/
# ==============================================================================
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT"
. /etc/os-release
if [[ "${VERSION_ID}" != "22.04" ]]; then
    echo "Warning: this script was written for Ubuntu 22.04 (found ${VERSION_ID}). Python must be 3.10 for the pinned packages."
fi

echo "== 1. System packages"
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nftables nmap tcpdump tshark ethtool git curl gnupg \
    openssh-client unzip

echo "== 2. Zeek (official binary packages, LTS line 8.0, installed in /opt/zeek)"
echo "deb https://download.opensuse.org/repositories/security:/zeek/xUbuntu_${VERSION_ID}/ /" \
    | sudo tee /etc/apt/sources.list.d/security:zeek.list >/dev/null
curl -fsSL "https://download.opensuse.org/repositories/security:zeek/xUbuntu_${VERSION_ID}/Release.key" \
    | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security_zeek.gpg >/dev/null
sudo apt-get update
sudo apt-get install -y zeek-8.0
grep -q /opt/zeek/bin ~/.bashrc || echo 'export PATH=/opt/zeek/bin:$PATH' >> ~/.bashrc
sudo ln -sf /opt/zeek/bin/zeek /usr/local/bin/zeek

echo "== 3. MongoDB Community 8.0 (same major version as the development PC)"
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg --yes -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" \
    | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list >/dev/null
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl daemon-reload
sudo systemctl enable --now mongod

echo "== 4. Project Python environment (the same pinned versions as the PC)"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "== 5. Zeek log folder"
sudo mkdir -p /var/log/ids-zeek
sudo chown "$USER" /var/log/ids-zeek

echo "== 6. Files that are not in Git (model, training features, built dashboard)"
if [[ -f sensor_files.zip ]]; then
    unzip -o sensor_files.zip && sha256sum -c SHA256SUMS.txt
else
    echo "   sensor_files.zip not found. On the PC run: python lab_hardware/pack_for_sensor.py"
    echo "   then copy dist/sensor_files.zip into $PROJECT and run this step again:"
    echo "   unzip -o sensor_files.zip && sha256sum -c SHA256SUMS.txt"
fi

echo "== 7. Checks"
zeek --version || /opt/zeek/bin/zeek --version
nft --version
mongod --version | head -1
.venv/bin/python tools/check_env.py || true

cat <<EOF

Done. Next (see lab_hardware/README.md):
  1. Edit lab_hardware/settings.hardware.yaml (interface name, camera IP, router IP).
  2. .venv/bin/python lab_hardware/hwlab.py setup         (router key + dashboard login)
  3. Put the printed key on the router, then: hwlab.py trust-router, hwlab.py router-install
  4. Optional, start at boot: sudo bash lab_hardware/install_services.sh
EOF
