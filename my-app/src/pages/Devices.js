import React, { useState, useEffect } from "react";
import {
  Camera,
  Play,
  CheckCircle,
  Info,
  X,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient from "../services/api";
import { getSocket } from "../services/socket";

const Devices = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [subnet, setSubnet] = useState("192.168.50.0/24");
  const [scanning, setScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanMessage, setScanMessage] = useState("");
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [confirmingIp, setConfirmingIp] = useState(null);
  const [notification, setNotification] = useState("");

  const loadDevices = async () => {
    try {
      const res = await apiClient.get("/api/devices");
      const list = res.data?.devices || (Array.isArray(res.data) ? res.data : []);
      setDevices(list);
    } catch (err) {
      console.error("Failed to load devices:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();

    const socket = getSocket();
    if (socket) {
      const handleDeviceUpdate = (newDevice) => {
        setDevices((prev) => {
          const idx = prev.findIndex((d) => d.ip === newDevice.ip);
          if (idx >= 0) {
            const updated = [...prev];
            updated[idx] = { ...updated[idx], ...newDevice };
            return updated;
          }
          return [newDevice, ...prev];
        });
      };

      const handleScanProgress = (data) => {
        if (data.progress !== undefined) setScanProgress(data.progress);
        if (data.message) setScanMessage(data.message);
        if (data.status === "completed" || data.progress >= 100) {
          setScanning(false);
          loadDevices();
        }
      };

      socket.on("device_update", handleDeviceUpdate);
      socket.on("scan_progress", handleScanProgress);

      return () => {
        socket.off("device_update", handleDeviceUpdate);
        socket.off("scan_progress", handleScanProgress);
      };
    }
  }, []);

  const handleStartScan = async (e) => {
    e.preventDefault();
    if (!subnet.trim()) return;

    setScanning(true);
    setScanProgress(5);
    setScanMessage("Dispatching authorized Nmap scan request...");
    setNotification("");

    try {
      const res = await apiClient.post("/api/scans", { subnet: subnet.trim() });
      if (res.data?.scan_id) {
        setScanMessage(`Scan started on ${subnet}. Gathering telemetry...`);
      }
    } catch (err) {
      setScanning(false);
      setNotification(
        err.response?.data?.error || "Failed to trigger scan. Subnet may be unapproved."
      );
    }
  };

  const handleToggleCameraConfirm = async (ip, currentStatus) => {
    setConfirmingIp(ip);
    try {
      const isConfirmed = currentStatus === true;
      const res = await apiClient.patch(`/api/devices/${ip}/confirm-camera`, {
        confirmed_camera: !isConfirmed,
      });
      if (res.data) {
        setDevices((prev) =>
          prev.map((d) =>
            d.ip === ip ? { ...d, confirmed_camera: !isConfirmed } : d
          )
        );
        if (selectedDevice && selectedDevice.ip === ip) {
          setSelectedDevice((prev) => ({ ...prev, confirmed_camera: !isConfirmed }));
        }
        setNotification(`Device ${ip} camera confirmation updated.`);
      }
    } catch (err) {
      setNotification(
        err.response?.data?.error || "Failed to update camera status. Admin required."
      );
    } finally {
      setConfirmingIp(null);
    }
  };

  return (
    <Layout>
      <div className="space-y-5 max-w-7xl mx-auto">
        {/* Header */}
        <div className="pb-4 border-b border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
              <Camera className="text-yellow-400" size={24} />
              DISCOVERED NETWORK ASSETS & SCANS
            </h1>
            <p className="text-xs text-gray-400">
              Nmap Asset Discovery • Multi-Evidence Surveillance Camera Verification
            </p>
          </div>

          {/* Trigger Scan Form */}
          <form onSubmit={handleStartScan} className="flex items-center gap-2 text-xs">
            <input
              type="text"
              value={subnet}
              onChange={(e) => setSubnet(e.target.value)}
              placeholder="Subnet (e.g. 192.168.50.0/24)"
              disabled={scanning}
              className="px-3 py-1.5 bg-gray-950 border border-gray-800 rounded font-mono text-gray-200 focus:outline-none focus:border-yellow-500 w-44"
            />
            <button
              type="submit"
              disabled={scanning}
              className={`px-3 py-1.5 rounded flex items-center gap-1.5 font-semibold transition ${
                scanning
                  ? "bg-gray-800 text-gray-500 cursor-not-allowed"
                  : "bg-yellow-950/80 hover:bg-yellow-900 border border-yellow-700 text-yellow-300"
              }`}
            >
              <Play size={13} />
              <span>{scanning ? "SCANNING..." : "TRIGGER NMAP"}</span>
            </button>
          </form>
        </div>

        {/* Scan Progress Bar */}
        {scanning && (
          <div className="p-4 bg-gray-900/60 border border-yellow-800/80 rounded-lg space-y-2 text-xs">
            <div className="flex justify-between text-yellow-300 font-semibold">
              <span>{scanMessage || "Executing Nmap device discovery..."}</span>
              <span>{scanProgress}%</span>
            </div>
            <div className="w-full bg-gray-950 rounded-full h-2 overflow-hidden border border-gray-800">
              <div
                className="bg-yellow-400 h-full transition-all duration-300 ease-out"
                style={{ width: `${scanProgress}%` }}
              />
            </div>
          </div>
        )}

        {notification && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{notification}</span>
            <button onClick={() => setNotification("")}>✕</button>
          </div>
        )}

        {/* Devices Table */}
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-gray-950/60">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/90 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">IP ADDRESS</th>
                  <th className="py-2.5 px-3">MAC / VENDOR</th>
                  <th className="py-2.5 px-3">OPEN PORTS</th>
                  <th className="py-2.5 px-3">SERVICES</th>
                  <th className="py-2.5 px-3">CAMERA HEURISTIC</th>
                  <th className="py-2.5 px-3">ADMIN STATUS</th>
                  <th className="py-2.5 px-3 text-right">EVIDENCE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {devices.length > 0 ? (
                  devices.map((dev, idx) => {
                    const isCamera = dev.possible_camera;
                    const isConfirmed = dev.confirmed_camera;
                    const ports = dev.open_ports || dev.ports || [];
                    const services = dev.services || [];

                    return (
                      <tr key={dev.ip || idx} className="hover:bg-gray-900/50 transition">
                        <td className="py-2.5 px-3 font-mono text-gray-200 font-semibold">
                          {dev.ip}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-gray-400">
                          {dev.mac || "Unknown"}
                          <div className="text-[10px] text-gray-500 font-sans">
                            {dev.vendor || "Generic Device"}
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-gray-300 font-mono">
                          {ports.length > 0 ? ports.slice(0, 4).join(", ") : "None"}
                        </td>
                        <td className="py-2.5 px-3 text-gray-400">
                          {services.length > 0 ? services.slice(0, 3).join(", ") : "—"}
                        </td>
                        <td className="py-2.5 px-3">
                          {isCamera ? (
                            <span className="px-2 py-0.5 rounded text-[10px] bg-yellow-950 text-yellow-300 border border-yellow-700 font-semibold">
                              POSSIBLE CAMERA
                            </span>
                          ) : (
                            <span className="text-gray-500 text-[11px]">Standard Host</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3">
                          <button
                            onClick={() => handleToggleCameraConfirm(dev.ip, isConfirmed)}
                            disabled={confirmingIp === dev.ip}
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold border flex items-center gap-1 transition ${
                              isConfirmed
                                ? "bg-emerald-950 text-emerald-300 border-emerald-700 hover:bg-emerald-900"
                                : "bg-gray-900 text-gray-400 border-gray-700 hover:bg-gray-800"
                            }`}
                          >
                            <CheckCircle size={10} />
                            <span>{isConfirmed ? "CONFIRMED CAMERA" : "MARK CAMERA"}</span>
                          </button>
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => setSelectedDevice(dev)}
                            className="px-2 py-1 bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700 rounded text-[11px] inline-flex items-center gap-1"
                          >
                            <Info size={12} /> Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-8 text-gray-500">
                      {loading ? "Discovering devices..." : "No devices recorded in subnet. Run Nmap discovery above."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Device Evidence Modal */}
        {selectedDevice && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-950 border border-gray-800 rounded-lg max-w-lg w-full p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
                  <Camera size={18} className="text-yellow-400" />
                  DEVICE EVIDENCE DOSSIER
                </h3>
                <button
                  onClick={() => setSelectedDevice(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2 bg-gray-900 rounded font-mono">
                    <span className="text-gray-500 block">IP Address:</span>
                    <span className="text-gray-200 font-semibold">{selectedDevice.ip}</span>
                  </div>
                  <div className="p-2 bg-gray-900 rounded font-mono">
                    <span className="text-gray-500 block">MAC Address:</span>
                    <span className="text-gray-200 font-semibold">
                      {selectedDevice.mac || "N/A"}
                    </span>
                  </div>
                </div>

                <div className="p-2.5 bg-gray-900 rounded">
                  <span className="text-gray-500 block mb-1">Open Ports & Banners:</span>
                  <div className="flex flex-wrap gap-1 font-mono">
                    {(selectedDevice.open_ports || []).map((p, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-gray-950 border border-gray-800 rounded text-cyan-300"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Evidence List */}
                <div className="p-3 bg-yellow-950/20 border border-yellow-900/60 rounded space-y-1.5">
                  <strong className="block text-yellow-300 font-semibold">
                    Surveillance Camera Heuristic Indicators:
                  </strong>
                  {selectedDevice.camera_evidence && selectedDevice.camera_evidence.length > 0 ? (
                    <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                      {selectedDevice.camera_evidence.map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400">
                      No surveillance streaming signatures (RTSP, ONVIF, or NVR controls) detected.
                    </p>
                  )}
                </div>

                <div className="text-[11px] text-gray-500">
                  Last seen: {selectedDevice.last_seen ? new Date(selectedDevice.last_seen).toLocaleString() : "Recently active"}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Devices;
