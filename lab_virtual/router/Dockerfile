# Lab router: Linux with nftables and an SSH server (like the OpenWrt/Linux lab router, Step 5).
FROM alpine:latest
RUN apk add --no-cache nftables openssh-server
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
