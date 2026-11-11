"""
tests/unit/test_scanner_service.py - Comprehensive Unit Tests for Authorized Scanner Service (Step 27).
======================================================================================================

Tests strictly adhere to Group 03 Proposal:
- Section 3.7: Subnet restriction (approved lab subnets only: 192.168.50.0/24, never internet or university).
- Section 3.7: Multi-evidence camera identification (never assume camera from port 554 alone; check OUI, RTSP, ONVIF, HTTP).
- Table 7 (FR-05): Active device discovery.
"""

import pytest
from unittest.mock import MagicMock

from core_engine.scanner_service import (
    ScannerService,
    UnauthorizedSubnetError,
    analyze_camera_evidence,
    classify_device_type,
    CAMERA_VENDOR_SIGNATURES,
    CAMERA_SERVICE_PORTS,
)


# =============================================================================
# 1. Subnet Safety Guardrails (Proposal Section 3.7)
# =============================================================================

def test_validate_subnet_approved():
    """Verify approved lab subnets and single host IPs pass validation."""
    scanner = ScannerService(approved_subnets=["192.168.50.0/24"])

    # Approved full subnet
    assert scanner.validate_subnet("192.168.50.0/24") is True

    # Approved single host within subnet
    assert scanner.validate_subnet("192.168.50.60/32") is True
    assert scanner.validate_subnet("192.168.50.1") is True


def test_validate_subnet_unauthorized_rejection():
    """Verify unauthorized external, campus, and public subnets are rejected."""
    scanner = ScannerService(approved_subnets=["192.168.50.0/24"])

    # Public internet IP
    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("8.8.8.8")

    # Campus / corporate subnets
    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("10.0.0.0/24")

    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("172.16.0.0/16")

    # Unapproved home subnet
    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("192.168.1.0/24")

    # Supernet containing lab subnet (must NOT allow scanning wider network)
    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("192.168.0.0/16")

    # Entire IPv4 space
    with pytest.raises(UnauthorizedSubnetError, match="outside authorized lab scan subnets"):
        scanner.validate_subnet("0.0.0.0/0")


def test_validate_subnet_invalid_syntax():
    """Verify malformed subnet strings raise UnauthorizedSubnetError."""
    scanner = ScannerService(approved_subnets=["192.168.50.0/24"])

    with pytest.raises(UnauthorizedSubnetError, match="cannot be empty"):
        scanner.validate_subnet("")

    with pytest.raises(UnauthorizedSubnetError, match="Invalid CIDR"):
        scanner.validate_subnet("invalid_ip_string")

    with pytest.raises(UnauthorizedSubnetError, match="Invalid CIDR"):
        scanner.validate_subnet("999.999.999.999/24")


# =============================================================================
# 2. Multi-Evidence Camera Identification (Proposal Section 3.7)
# =============================================================================

def test_camera_evidence_dahua_full_profile():
    """Verify Dahua IP camera with OUI, RTSP, ONVIF, and web interface is detected."""
    is_cam, evidence = analyze_camera_evidence(
        ip="192.168.50.60",
        mac="3C:EF:8C:11:22:33",
        vendor="Dahua Technology Co., Ltd.",
        hostname="ipc-hfw1230",
        open_ports=[80, 554, 8899, 37777],
        services=["http Dahua-Web", "rtsp live555", "onvif Device", "dahua-control"],
    )

    assert is_cam is True
    assert len(evidence) >= 5
    # Verify specific evidence items
    assert any("Dahua" in e for e in evidence)
    assert any("RTSP streaming port 554" in e for e in evidence)
    assert any("37777" in e for e in evidence)
    assert any("8899" in e for e in evidence)
    assert any("live555" in e for e in evidence)


def test_camera_evidence_hikvision_nvr():
    """Verify Hikvision surveillance unit with port 8000 and RTSP is detected."""
    is_cam, evidence = analyze_camera_evidence(
        ip="192.168.50.20",
        mac="00:1A:2B:3C:4D:20",
        vendor="Hikvision Digital Technology",
        hostname="embedded-nvr",
        open_ports=[80, 554, 8000, 8080],
        services=["http Hikvision-Web", "rtsp", "hikvision-mgmt"],
    )

    assert is_cam is True
    assert any("Hikvision" in e for e in evidence)
    assert any("8000" in e for e in evidence)


def test_camera_evidence_workstation_negative():
    """Verify admin workstation with SSH and RDP is NOT tagged as a camera."""
    is_cam, evidence = analyze_camera_evidence(
        ip="192.168.50.10",
        mac="00:1A:2B:3C:4D:10",
        vendor="Dell Inc.",
        hostname="admin-workstation",
        open_ports=[22, 3389],
        services=["ssh OpenSSH", "ms-wbt-server RDP"],
    )

    assert is_cam is False
    assert len(evidence) == 0


def test_camera_evidence_router_negative():
    """Verify gateway router with DNS and HTTP is NOT tagged as a camera."""
    is_cam, evidence = analyze_camera_evidence(
        ip="192.168.50.1",
        mac="00:1A:2B:3C:4D:01",
        vendor="Cisco Systems",
        hostname="lab-gateway",
        open_ports=[22, 53, 80],
        services=["ssh OpenSSH", "domain dnsmasq", "http lighttpd"],
    )

    assert is_cam is False
    assert len(evidence) == 0


def test_camera_evidence_single_rtsp_flagged_with_evidence():
    """
    Verify device with ONLY port 554 open is flagged as possible camera,
    with clear evidence noted for administrator verification (Section 3.7).
    """
    is_cam, evidence = analyze_camera_evidence(
        ip="192.168.50.99",
        mac="unknown",
        vendor="unknown",
        hostname="",
        open_ports=[554],
        services=["rtsp"],
    )

    assert is_cam is True
    assert len(evidence) >= 1
    assert any("554" in e for e in evidence)


# =============================================================================
# 3. Device Classification (Proposal Section 3.7)
# =============================================================================

def test_classify_device_type():
    """Verify role classification for standard lab topology."""
    # Gateway router
    assert classify_device_type("192.168.50.1", [22, 53], [], "lab-gateway", False) == "router"

    # IDS Sensor
    assert classify_device_type("192.168.50.5", [22], [], "ids-sensor-linux", False) == "ids_sensor"

    # Workstation
    assert classify_device_type("192.168.50.10", [22, 3389], [], "admin-pc", False) == "workstation"

    # NVR
    assert classify_device_type("192.168.50.20", [80, 554, 8000], [], "embedded-nvr", True) == "nvr"

    # IP Camera
    assert classify_device_type("192.168.50.60", [80, 554, 8899], [], "ipc-hfw1230", True) == "ip_camera"

    # Generic Web Device
    assert classify_device_type("192.168.50.80", [80, 443], [], "web-server", False) == "web_device"

    # Generic IoT Device
    assert classify_device_type("192.168.50.90", [1883], [], "mqtt-broker", False) == "iot_device"


# =============================================================================
# 4. Mock Nmap Output Parsing
# =============================================================================

class MockPortScanner:
    """Mock for nmap.PortScanner to test real scanning parse path."""

    def __init__(self):
        self._hosts = ["192.168.50.1", "192.168.50.60"]
        self._host_data = {
            "192.168.50.1": {
                "addresses": {"ipv4": "192.168.50.1", "mac": "00:1A:2B:3C:4D:01"},
                "vendor": {"00:1A:2B:3C:4D:01": "Cisco Systems"},
                "hostname_str": "lab-gateway",
                "state_str": "up",
                "tcp": {
                    22: {"state": "open", "name": "ssh", "product": "OpenSSH 8.9"},
                    80: {"state": "open", "name": "http", "product": "lighttpd"},
                },
            },
            "192.168.50.60": {
                "addresses": {"ipv4": "192.168.50.60", "mac": "3C:EF:8C:11:22:33"},
                "vendor": {"3C:EF:8C:11:22:33": "Dahua Technology"},
                "hostname_str": "ipc-hfw1230",
                "state_str": "up",
                "tcp": {
                    80: {"state": "open", "name": "http", "product": "Dahua-Web"},
                    554: {"state": "open", "name": "rtsp", "product": "live555"},
                    37777: {"state": "open", "name": "dahua-control", "product": "Dahua"},
                },
            },
        }

    def scan(self, hosts, arguments):
        return {"nmap": {"command_line": f"nmap {arguments} {hosts}"}}

    def all_hosts(self):
        return self._hosts

    def __getitem__(self, host):
        class HostObj:
            def __init__(self, data):
                self._data = data

            def state(self):
                return self._data.get("state_str", "up")

            def hostname(self):
                return self._data.get("hostname_str", "")

            def get(self, key, default=None):
                return self._data.get(key, default)

            def __contains__(self, key):
                return key in self._data

            def __getitem__(self, key):
                return self._data[key]

        return HostObj(self._host_data.get(host, {}))


def test_mock_nmap_scan_parsing():
    """Verify _run_nmap_scan correctly extracts ports, vendors, and camera tags."""
    mock_scanner = MockPortScanner()
    service = ScannerService(
        approved_subnets=["192.168.50.0/24"],
        nmap_scanner=mock_scanner,
    )

    discovered = service._run_nmap_scan("192.168.50.0/24", "scan_test_01", "admin")

    assert len(discovered) == 2

    # Check Cisco Gateway
    cisco = next(d for d in discovered if d["ip"] == "192.168.50.1")
    assert cisco["device_type"] == "router"
    assert cisco["possible_camera"] is False
    assert 22 in cisco["open_ports"]
    assert 80 in cisco["open_ports"]

    # Check Dahua IP Camera
    dahua = next(d for d in discovered if d["ip"] == "192.168.50.60")
    assert dahua["device_type"] == "ip_camera"
    assert dahua["possible_camera"] is True
    assert dahua["confirmed_camera"] is False
    assert 554 in dahua["open_ports"]
    assert 37777 in dahua["open_ports"]
    assert len(dahua["camera_evidence"]) >= 3


# =============================================================================
# 5. Simulated Lab Network Discovery
# =============================================================================

def test_simulated_scan_discovery():
    """Verify fallback simulated lab scan discovers standard lab topology."""
    service = ScannerService(approved_subnets=["192.168.50.0/24"])
    service.is_nmap_available = False

    discovered = service._run_simulated_scan("192.168.50.0/24", "sim_01", "admin")

    assert len(discovered) == 5
    ips = [d["ip"] for d in discovered]
    assert "192.168.50.1" in ips
    assert "192.168.50.5" in ips
    assert "192.168.50.10" in ips
    assert "192.168.50.20" in ips
    assert "192.168.50.60" in ips

    # Verify Dahua camera has possible_camera = True
    dahua = next(d for d in discovered if d["ip"] == "192.168.50.60")
    assert dahua["possible_camera"] is True
    assert dahua["device_type"] == "ip_camera"

    # Verify Gateway router has possible_camera = False
    router = next(d for d in discovered if d["ip"] == "192.168.50.1")
    assert router["possible_camera"] is False
    assert router["device_type"] == "router"


# =============================================================================
# 6. Scanner State Tracking
# =============================================================================

def test_scanner_state_tracking():
    """Verify is_scanning reports running status accurately."""
    service = ScannerService(approved_subnets=["192.168.50.0/24"])
    assert service.is_scanning() is False

    service.active_scans["test_scan"] = {"status": "running"}
    assert service.is_scanning() is True

    service.active_scans["test_scan"] = {"status": "completed"}
    assert service.is_scanning() is False



# ---------------------------------------------------------------- D-056: no silent simulation
NMAP_XML = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -oX - 192.168.50.0/24" start="1" version="7.95">
<host><status state="up" reason="arp-response"/>
<address addr="192.168.50.30" addrtype="ipv4"/><address addr="02:42:C0:A8:32:1E" addrtype="mac"/>
<hostnames></hostnames>
<ports>
<port protocol="tcp" portid="80"><state state="open" reason="syn-ack"/><service name="http" product="BaseHTTPServer"/></port>
<port protocol="tcp" portid="554"><state state="open" reason="syn-ack"/><service name="rtsp"/></port>
<port protocol="tcp" portid="22"><state state="closed" reason="reset"/><service name="ssh"/></port>
</ports></host>
<runstats><finished time="2" elapsed="1.5"/><hosts up="1" down="255" total="256"/></runstats>
</nmaprun>"""


def _fake_nmap(tmp_path):
    """A tiny program that answers like Nmap: '-V' gives the version, a scan gives NMAP_XML."""
    import sys
    script = tmp_path / "fake_nmap.py"
    script.write_text(
        "import sys\n"
        "if '-V' in sys.argv: print('Nmap version 7.95 ( https://nmap.org )'); sys.exit(0)\n"
        f"print({NMAP_XML!r})\n",
        encoding="utf-8",
    )
    return [sys.executable, str(script)]


def test_scan_fails_clearly_when_nmap_missing_and_simulation_off():
    from core_engine.scanner_service import SimulationNotAllowedError
    service = ScannerService(approved_subnets=["192.168.50.0/24"], allow_simulation=False)
    service.is_nmap_available, service.nm = False, None
    with pytest.raises(SimulationNotAllowedError):
        service.scan_network("192.168.50.0/24")


def test_simulated_scan_is_always_marked():
    service = ScannerService(approved_subnets=["192.168.50.0/24"], allow_simulation=True)
    service.is_nmap_available, service.nm = False, None
    res = service.scan_network("192.168.50.0/24")
    assert res["simulated"] is True and res["summary"]["simulated"] is True
    assert all(d["simulated"] is True for d in res["devices"])


def test_command_nmap_backend_reads_real_nmap_xml(tmp_path):
    service = ScannerService(approved_subnets=["192.168.50.0/24"], nmap_command=_fake_nmap(tmp_path))
    assert service.is_nmap_available and service.backend.startswith("command:")
    res = service.scan_network("192.168.50.0/24")
    assert res["simulated"] is False and res["devices_found"] == 1
    dev = res["devices"][0]
    assert dev["ip"] == "192.168.50.30" and dev["mac"] == "02:42:C0:A8:32:1E"
    assert sorted(dev["open_ports"]) == [80, 554] and dev["simulated"] is False
    assert dev["vendor"] == "unknown"        # nothing is invented


def test_camera_needs_two_pieces_of_evidence_and_own_hostname_only():
    """Proposal 3.7: one port is not proof; the network's DNS suffix is not the device's name."""
    from core_engine.scanner_service import analyze_camera_evidence
    nvr_like, _ = analyze_camera_evidence("192.168.50.20", hostname="ids-lab-nvr.ids-lab_camlan", open_ports=[])
    only_554, ev = analyze_camera_evidence("192.168.50.40", open_ports=[554])
    real_cam, ev2 = analyze_camera_evidence("192.168.50.30", hostname="ids-lab-camera-net.ids-lab_camlan",
                                            open_ports=[80, 554], services=["http BaseHTTPServer", "rtsp"])
    assert nvr_like is False                     # "camlan" in the domain is no evidence
    assert only_554 is False and len(ev) == 1    # a single open port is not enough
    assert real_cam is True and len(ev2) >= 3
