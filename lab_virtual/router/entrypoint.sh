#!/bin/sh
# Lab router start-up: load the project's nftables table, then run the SSH server.
set -e
nft -f /lab/ids_router.nft
echo "nftables table loaded:"; nft list table inet ids | head -5

# root may log in with the lab key only (no password), as the router adapter expects (D-038)
sed -i 's/^root:[^:]*:/root:*:/' /etc/shadow
mkdir -p /root/.ssh && chmod 700 /root/.ssh
cp /keys/router_admin.pub /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys
cp /keys/router_host_ed25519 /etc/ssh/ssh_host_ed25519_key && chmod 600 /etc/ssh/ssh_host_ed25519_key
cat > /etc/ssh/sshd_config <<CFG
Port 22
HostKey /etc/ssh/ssh_host_ed25519_key
PermitRootLogin prohibit-password
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
Subsystem sftp internal-sftp
CFG
ip -o -4 addr show | awk '{print "interface", $2, $4}'
echo "lab router ready"
exec /usr/sbin/sshd -D -e
