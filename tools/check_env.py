"""
tools/check_env.py
Verification script for the IDS development and sensor environment.
Checks Python version, package imports, MongoDB connection, and system tools.
Outputs report to stdout and reports/environment_versions.txt.
Based on proposal Table 8 and STEP_BY_STEP_GUIDE.md Step 3.
"""

import sys
import platform
import os
from datetime import datetime
from importlib.metadata import version as get_pkg_version

REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "environment_versions.txt")

REQUIRED_PACKAGES = [
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("pyarrow", "pyarrow"),
    ("scikit-learn", "sklearn"),
    ("joblib", "joblib"),
    ("matplotlib", "matplotlib"),
    ("pyyaml", "yaml"),
    ("python-dotenv", "dotenv"),
    ("flask", "flask"),
    ("flask-socketio", "flask_socketio"),
    ("flask-cors", "flask_cors"),
    ("flask-jwt-extended", "flask_jwt_extended"),
    ("bcrypt", "bcrypt"),
    ("pymongo", "pymongo"),
    ("python-nmap", "nmap"),
    ("psutil", "psutil"),
    ("scapy", "scapy"),
    ("pytest", "pytest"),
]

def check_packages():
    results = []
    all_ok = True
    for pkg_name, import_name in REQUIRED_PACKAGES:
        try:
            mod = __import__(import_name)
            try:
                pkg_ver = get_pkg_version(pkg_name)
            except Exception:
                pkg_ver = getattr(mod, "__version__", "installed")
            results.append((pkg_name, True, pkg_ver))
        except ImportError as e:
            results.append((pkg_name, False, str(e)))
            all_ok = False
    return results, all_ok

def check_mongodb():
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        info = client.server_info()
        version = info.get("version", "unknown")
        return True, f"MongoDB Connected (v{version})"
    except Exception as e:
        return False, f"MongoDB connection failed: {e}"

def check_npcap():
    if platform.system() == "Windows":
        npcap_dir = r"C:\Program Files\Npcap"
        if os.path.exists(npcap_dir):
            return True, f"Npcap detected at {npcap_dir}"
        return False, "Npcap not found at C:\\Program Files\\Npcap"
    return True, "Not Windows (Npcap not needed)"

def check_nmap_binary():
    import shutil
    nmap_path = shutil.which("nmap")
    if nmap_path:
        return True, f"Nmap executable found at {nmap_path}"
    return False, "Nmap binary not found in PATH (deferred to Step 27 or install from nmap.org)"

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 60)
    lines.append(f"IDS Software Environment Verification Report")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Host: {platform.node()} ({platform.system()} {platform.release()} {platform.machine()})")
    lines.append(f"Python: {platform.python_version()} ({sys.executable})")
    lines.append("=" * 60)
    lines.append("")
    
    # Packages
    lines.append("--- Python Packages ---")
    pkg_results, packages_ok = check_packages()
    for name, ok, ver in pkg_results:
        status = "[OK]" if ok else "[FAIL]"
        lines.append(f"  {status:<7} {name:<22}: {ver}")
    lines.append("")

    # MongoDB
    lines.append("--- Database Service ---")
    mongo_ok, mongo_msg = check_mongodb()
    lines.append(f"  {'[OK]' if mongo_ok else '[FAIL]':<7} {mongo_msg}")
    lines.append("")

    # System & Network Drivers
    lines.append("--- Network & System Tools ---")
    npcap_ok, npcap_msg = check_npcap()
    lines.append(f"  {'[OK]' if npcap_ok else '[INFO]':<7} {npcap_msg}")
    nmap_ok, nmap_msg = check_nmap_binary()
    lines.append(f"  {'[OK]' if nmap_ok else '[INFO]':<7} {nmap_msg}")
    lines.append("")

    lines.append("=" * 60)
    overall_status = "PASSED" if (packages_ok and mongo_ok) else "ATTENTION NEEDED"
    lines.append(f"OVERALL STATUS: {overall_status}")
    lines.append("=" * 60)

    report_text = "\n".join(lines)
    print(report_text)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")
    print(f"\nReport written to: {REPORT_PATH}")

    return 0 if overall_status == "PASSED" else 1

if __name__ == "__main__":
    sys.exit(main())

