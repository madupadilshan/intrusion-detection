# ==============================================================================
# sensor/local.zeek - Zeek Configuration for IoT IP-Camera IDS Sensor
# ==============================================================================
# Governing Standards:
# - Research Proposal: Sections 3.3, 3.5, 3.7; Table 7 (FR-01); Table 8
# - Step-by-Step Guide: Step 19 (Run Zeek on the sensor)
#
# Key Requirements:
# 1. Output all logs in streaming Line-Delimited JSON format for real-time tailing.
# 2. Disable checksum verification (-C flag / ignore_checksums) for port mirroring.
# 3. Disable automated hourly log rotation (rotation_interval = 0 sec) so that
#    the live Python log tailer (Step 21) can stream conn.log continuously.
# 4. Standardize timestamps to UNIX epoch seconds matching IoT-23 float timestamps.
# ==============================================================================

# 1. Enable Streaming JSON Logging Policy
@load policy/tuning/json-logs.zeek

# 2. Redefine Log Manager Settings for Real-Time Streaming IDS
# Disable automatic log rotation so conn.log remains a single continuously growing stream
redef Log::default_rotation_interval = 0 sec;

# Enable UNIX Epoch floating-point timestamps in JSON output
redef LogAscii::json_timestamps = JSON::TS_EPOCH;

# Checksum override: mirrored traffic frequently contains NIC offload or hardware checksum anomalies
redef ignore_checksums = T;

# 3. Load Core Protocols and Connection Tracker
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl

