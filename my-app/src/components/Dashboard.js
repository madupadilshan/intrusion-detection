import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Terminal, AlertTriangle, Activity, Cpu } from "lucide-react";
import MatrixEffect from "./MatrixEffect";
import apiClient from "../services/api";
import { getSocket } from "../services/socket";
import "./Dashboard.css";

const Dashboard = () => {
  const [summary, setSummary] = useState({
    total_events: 0,
    attacks_detected: 0,
    blocked_ips: 0,
    active_devices: 0,
  });
  const [latestEvents, setLatestEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [alertVisible, setAlertVisible] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertSeverity, setAlertSeverity] = useState("medium");
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  useEffect(() => {
    let isMounted = true;

    const fetchSummary = async () => {
      try {
        const [sumRes, evRes] = await Promise.all([
          apiClient.get("/api/summary").catch(() => ({ data: {} })),
          apiClient.get("/api/events?limit=5").catch(() => ({ data: { events: [] } })),
        ]);

        if (isMounted) {
          if (sumRes.data) {
            setSummary((prev) => ({ ...prev, ...sumRes.data }));
          }
          if (evRes.data && evRes.data.events) {
            setLatestEvents(evRes.data.events);
          }
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchSummary();

    const socket = getSocket();
    if (socket) {
      const handleNewEvent = (event) => {
        if (!isMounted) return;
        const cls = event.predicted_class || event.attack || "Benign";
        if (cls.toLowerCase() !== "benign") {
          setAlertMessage(`Alert: [${cls}] detected from ${event.src_ip || "unknown"}`);
          setAlertSeverity("high");
          setAlertVisible(true);
          setTimeout(() => setAlertVisible(false), 5000);
        }
        setLatestEvents((prev) => [event, ...prev.slice(0, 4)]);
      };

      const handleSummaryUpdate = (data) => {
        if (!isMounted) return;
        setSummary((prev) => ({ ...prev, ...data }));
      };

      socket.on("new_event", handleNewEvent);
      socket.on("summary_update", handleSummaryUpdate);

      return () => {
        isMounted = false;
        socket.off("new_event", handleNewEvent);
        socket.off("summary_update", handleSummaryUpdate);
      };
    }

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard-container">
      <MatrixEffect />

      {alertVisible && (
        <div className={`alert-popup attack-${alertSeverity}`}>
          <AlertTriangle size={24} />
          <span>{alertMessage}</span>
        </div>
      )}

      <div className="dashboard-content">
        <div className="dashboard-header flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Shield className="terminal-icon" />
            <h1 className="dashboard-title">SECURITY OPERATIONS CENTER</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-3 py-1 text-sm bg-red-900 hover:bg-red-800 text-red-200 border border-red-500 rounded"
          >
            LOGOUT
          </button>
        </div>

        <div className="security-status">
          <div className="status-indicator"></div>
          <span>REAL-TIME INTRUSION DETECTION ENGINE ACTIVE</span>
          <div className="status-indicator"></div>
        </div>

        {/* KPI Summary Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", margin: "1.5rem 0" }}>
          <div className="p-4 bg-gray-900 border border-emerald-500 rounded text-center">
            <h4 style={{ color: "#9ca3af", fontSize: "0.85rem" }}>TOTAL MONITORED FLOWS</h4>
            <p style={{ color: "#10b981", fontSize: "1.8rem", fontWeight: "bold" }}>
              {summary.total_events || 0}
            </p>
          </div>
          <div className="p-4 bg-gray-900 border border-red-500 rounded text-center">
            <h4 style={{ color: "#9ca3af", fontSize: "0.85rem" }}>ATTACKS DETECTED</h4>
            <p style={{ color: "#ef4444", fontSize: "1.8rem", fontWeight: "bold" }}>
              {summary.attacks_detected || 0}
            </p>
          </div>
          <div className="p-4 bg-gray-900 border border-yellow-500 rounded text-center">
            <h4 style={{ color: "#9ca3af", fontSize: "0.85rem" }}>ACTIVE MITIGATIONS</h4>
            <p style={{ color: "#f59e0b", fontSize: "1.8rem", fontWeight: "bold" }}>
              {summary.blocked_ips || 0}
            </p>
          </div>
          <div className="p-4 bg-gray-900 border border-cyan-500 rounded text-center">
            <h4 style={{ color: "#9ca3af", fontSize: "0.85rem" }}>DISCOVERED DEVICES</h4>
            <p style={{ color: "#06b6d4", fontSize: "1.8rem", fontWeight: "bold" }}>
              {summary.active_devices || 0}
            </p>
          </div>
        </div>

        {/* Quick Nav Tiles */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
          <div
            onClick={() => navigate("/overview")}
            style={{ cursor: "pointer" }}
            className="p-5 bg-gray-900 border border-gray-700 hover:border-emerald-500 rounded transition"
          >
            <Activity className="text-emerald-400 mb-2" size={28} />
            <h3 className="text-lg font-bold text-gray-100">Overview</h3>
            <p className="text-sm text-gray-400">System health, traffic volume & class distribution.</p>
          </div>

          <div
            onClick={() => navigate("/alerts")}
            style={{ cursor: "pointer" }}
            className="p-5 bg-gray-900 border border-gray-700 hover:border-red-500 rounded transition"
          >
            <AlertTriangle className="text-red-400 mb-2" size={28} />
            <h3 className="text-lg font-bold text-gray-100">Live Alerts</h3>
            <p className="text-sm text-gray-400">Real-time Socket.IO incident feed & verification.</p>
          </div>

          <div
            onClick={() => navigate("/history")}
            style={{ cursor: "pointer" }}
            className="p-5 bg-gray-900 border border-gray-700 hover:border-cyan-500 rounded transition"
          >
            <Terminal className="text-cyan-400 mb-2" size={28} />
            <h3 className="text-lg font-bold text-gray-100">Attack History</h3>
            <p className="text-sm text-gray-400">Searchable log database with forensic evidence.</p>
          </div>

          <div
            onClick={() => navigate("/devices")}
            style={{ cursor: "pointer" }}
            className="p-5 bg-gray-900 border border-gray-700 hover:border-yellow-500 rounded transition"
          >
            <Cpu className="text-yellow-400 mb-2" size={28} />
            <h3 className="text-lg font-bold text-gray-100">Devices & Scans</h3>
            <p className="text-sm text-gray-400">Nmap discovery, surveillance camera validation.</p>
          </div>
        </div>

        {/* Recent Events Table Preview */}
        <div className="mt-8 bg-gray-900 p-4 border border-gray-800 rounded">
          <h3 className="text-md font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Terminal size={18} /> RECENT LOGGED INCIDENTS
          </h3>
          <table className="attack-table w-full">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>PREDICTED CLASS</th>
                <th>SOURCE</th>
                <th>DESTINATION</th>
                <th>CONFIDENCE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {latestEvents.length > 0 ? (
                latestEvents.map((evt, idx) => (
                  <tr key={idx}>
                    <td>{evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : "N/A"}</td>
                    <td>{evt.predicted_class || "N/A"}</td>
                    <td>{evt.src_ip || "N/A"}</td>
                    <td>{evt.dst_ip || "N/A"}</td>
                    <td>{evt.confidence ? `${(evt.confidence * 100).toFixed(1)}%` : "N/A"}</td>
                    <td>{evt.status || "prediction"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="text-center text-gray-500 py-3">
                    {isLoading ? "Loading telemetry..." : "No incidents logged yet."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="footer-text mt-8">
          IP CAMERA IOT INTRUSION DETECTION SYSTEM • GROUP 03 SOC v2.5
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
