import React, { useEffect, useState, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Wifi, Terminal, AlertTriangle, Activity, Server, Cpu } from "lucide-react";
import MatrixEffect from "../components/MatrixEffect";
import apiClient from "../services/api";
import { getSocket } from "../services/socket";
import "./Dashboard.css";
import "./AttackHistory.css";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const IOTDetails = () => {
  const [attackDetails, setAttackDetails] = useState([]);
  const [terminalOutput, setTerminalOutput] = useState([]);
  const terminalRef = useRef(null);
  const [activeTab, setActiveTab] = useState("history");
  const [isAttackDetected, setIsAttackDetected] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [attackSeverity, setAttackSeverity] = useState("medium");
  const [alertCount, setAlertCount] = useState(0);
  const [hackingSequence, setHackingSequence] = useState([]);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [attackDetails3D, setAttackDetails3D] = useState(null);

  // Chart.js data for Attack Frequency / Bytes
  const [iotData, setIotData] = useState({
    labels: [],
    datasets: [
      {
        label: "Duration (s)",
        data: [],
        borderColor: "rgba(0, 255, 0, 1)",
        backgroundColor: "rgba(0, 255, 0, 0.2)",
        fill: false,
        tension: 0.4,
      },
    ],
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        ticks: { color: "#0f0" },
        grid: { color: "rgba(0, 255, 0, 0.1)" },
      },
      x: {
        ticks: { color: "#0f0" },
        grid: { color: "rgba(0, 255, 0, 0.1)" },
      },
    },
    plugins: {
      legend: {
        labels: { color: "#0f0" },
      },
    },
  };

  // Determine attack severity based on attack type or confidence
  const getAttackSeverity = (attackType) => {
    if (!attackType) return "low";
    const criticalAttacks = ["DDoS", "DoS", "Mirai"];
    const highAttacks = ["Malware", "C&C", "Port Scan"];
    if (criticalAttacks.some((k) => attackType.toLowerCase().includes(k.toLowerCase()))) {
      return "critical";
    }
    if (highAttacks.some((k) => attackType.toLowerCase().includes(k.toLowerCase()))) {
      return "high";
    }
    return "medium";
  };

  const triggerAttackAlert = (attackType, details) => {
    const severity = getAttackSeverity(attackType);
    setAttackSeverity(severity);
    setIsAttackDetected(true);
    setPopupMessage(`ALERT: ${attackType}`);
    setAttackDetails3D(details);
    setShowAlertModal(true);

    const timeout = severity === "critical" ? 8000 : severity === "high" ? 6000 : 5000;
    setTimeout(() => {
      setIsAttackDetected(false);
      setTimeout(() => setShowAlertModal(false), 1000);
    }, timeout);
  };

  // Update chart data from events
  const updateChartData = (events) => {
    if (!events || events.length === 0) return;
    const recent = events.slice(0, 20).reverse();
    const labels = recent.map((e) =>
      e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : e.time || "N/A"
    );
    const durations = recent.map((e) => e.duration || e.features?.duration || 0);
    const origBytes = recent.map((e) => e.orig_bytes || e.features?.orig_bytes || 0);
    const respBytes = recent.map((e) => e.resp_bytes || e.features?.resp_bytes || 0);

    setIotData({
      labels,
      datasets: [
        {
          label: "Duration (s)",
          data: durations,
          borderColor: "rgba(0, 255, 0, 1)",
          backgroundColor: "rgba(0, 255, 0, 0.2)",
          fill: false,
          tension: 0.4,
        },
        {
          label: "Orig Bytes",
          data: origBytes,
          borderColor: "rgba(0, 200, 100, 1)",
          backgroundColor: "rgba(0, 200, 100, 0.2)",
          fill: false,
          tension: 0.4,
        },
        {
          label: "Resp Bytes",
          data: respBytes,
          borderColor: "rgba(100, 255, 100, 1)",
          backgroundColor: "rgba(100, 255, 100, 0.2)",
          fill: false,
          tension: 0.4,
        },
      ],
    });
  };

  // Fetch initial attack details from unified backend
  useEffect(() => {
    let isMounted = true;

    const fetchAttackData = async () => {
      try {
        const res = await apiClient.get("/api/events?limit=50");
        const events = res.data?.events || res.data || [];
        if (isMounted) {
          const attacks = events.filter(
            (e) =>
              (e.predicted_class || e.attack) &&
              (e.predicted_class || e.attack).toLowerCase() !== "benign"
          );
          setAttackDetails(events);
          setAlertCount(attacks.length);
          updateChartData(events);

          const initialLines = events.slice(0, 15).map((e) => {
            const time = e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : "N/A";
            const cls = e.predicted_class || e.attack || "Unknown";
            const src = e.src_ip || "unknown";
            const dst = e.dst_ip || "unknown";
            return `${time} - [${cls}] ${src} -> ${dst}`;
          });
          setTerminalOutput(initialLines);
        }
      } catch (err) {
        console.error("Error fetching attack details:", err);
      }
    };

    fetchAttackData();

    // Setup Socket.IO for real-time telemetry (Step 29 requirement 3)
    const socket = getSocket();
    if (socket) {
      const handleNewEvent = (event) => {
        if (!isMounted) return;
        const cls = event.predicted_class || event.attack || "Unknown";
        const time = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        const logLine = `${time} - [${cls}] ${event.src_ip || "unknown"} -> ${event.dst_ip || "unknown"}`;

        setTerminalOutput((prev) => [...prev.slice(-49), logLine]);
        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }

        if (cls.toLowerCase() !== "benign") {
          setAttackDetails((prev) => [event, ...prev.slice(0, 49)]);
          setAlertCount((prev) => prev + 1);
          triggerAttackAlert(cls, event);
        }
      };

      socket.on("new_event", handleNewEvent);

      return () => {
        isMounted = false;
        socket.off("new_event", handleNewEvent);
      };
    }

    return () => {
      isMounted = false;
    };
  }, []);

  // Binary animation sequence
  useEffect(() => {
    const interval = setInterval(() => {
      const seq = Array.from({ length: 30 }, () => (Math.random() > 0.5 ? "1" : "0"));
      setHackingSequence(seq);
    }, 250);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`dashboard-container ${isAttackDetected ? `attack-detected attack-${attackSeverity}` : ""}`}>
      <MatrixEffect />

      {isAttackDetected && (
        <div className="binary-overlay">
          {hackingSequence.map((bit, idx) => (
            <span
              key={idx}
              className="binary-bit"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${idx * 0.05}s`,
              }}
            >
              {bit}
            </span>
          ))}
        </div>
      )}

      {isAttackDetected && <div className={`alert-ripple attack-${attackSeverity}`}></div>}

      <div className="dashboard-content">
        <div className="dashboard-header">
          <Wifi className="terminal-icon" />
          <h1 className="dashboard-title">IOT THREAT ANALYSIS</h1>
          <Terminal className="terminal-icon" />
          <div className="alert-counter">
            <AlertTriangle className="alert-icon" />
            <span className="alert-badge">{alertCount}</span>
          </div>
        </div>

        <div className={`security-status ${isAttackDetected ? "under-attack" : ""}`}>
          <div className="status-indicator"></div>
          <span>
            {isAttackDetected
              ? `⚠️ IOT NETWORK UNDER ATTACK: ${popupMessage}`
              : "MONITORING IOT NETWORK"}
          </span>
          <div className="status-indicator"></div>
        </div>

        {isAttackDetected && (
          <div className={`alert-popup attack-${attackSeverity}`}>
            <AlertTriangle size={24} />
            <span>{popupMessage}</span>
          </div>
        )}

        {showAlertModal && (
          <div className="attack-modal">
            <div className={`attack-modal-content attack-${attackSeverity}`}>
              <div className="modal-header">
                <AlertTriangle size={24} />
                <h3>THREAT DETECTED</h3>
                <button className="close-button" onClick={() => setShowAlertModal(false)}>
                  ×
                </button>
              </div>
              <div className="modal-body">
                <div className="attack-details-grid">
                  <div className="detail-item">
                    <span className="detail-label">Attack Type:</span>
                    <span className="detail-value">
                      {attackDetails3D?.predicted_class || attackDetails3D?.attack || "Unknown"}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Source IP:</span>
                    <span className="detail-value">{attackDetails3D?.src_ip || "N/A"}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Destination IP:</span>
                    <span className="detail-value">{attackDetails3D?.dst_ip || "N/A"}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Confidence:</span>
                    <span className="detail-value">
                      {attackDetails3D?.confidence
                        ? `${(attackDetails3D.confidence * 100).toFixed(1)}%`
                        : "N/A"}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Severity:</span>
                    <span className={`detail-value severity-${attackSeverity}`}>
                      {attackSeverity.toUpperCase()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    <span className="detail-value">
                      {attackDetails3D?.status || "Prediction"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="tabs-container">
          <div
            className={`tab ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            <Terminal className="tab-icon" />
            <span>ATTACK HISTORY</span>
          </div>
          <div
            className={`tab ${activeTab === "chart" ? "active" : ""}`}
            onClick={() => setActiveTab("chart")}
          >
            <Activity className="tab-icon" />
            <span>DATA ANALYTICS</span>
          </div>
          <div
            className={`tab ${activeTab === "terminal" ? "active" : ""}`}
            onClick={() => setActiveTab("terminal")}
          >
            <Server className="tab-icon" />
            <span>LIVE TERMINAL</span>
          </div>
          <div
            className={`tab ${activeTab === "devices" ? "active" : ""}`}
            onClick={() => setActiveTab("devices")}
          >
            <Cpu className="tab-icon" />
            <span>IOT DEVICES</span>
          </div>
        </div>

        <div className="content-container">
          <div className="content-header">
            {activeTab === "history" && (
              <>
                <Terminal className="content-icon" /> <h3>IOT ATTACK DATABASE</h3>
              </>
            )}
            {activeTab === "chart" && (
              <>
                <Activity className="content-icon" /> <h3>IOT THREAT METRICS</h3>
              </>
            )}
            {activeTab === "terminal" && (
              <>
                <Server className="content-icon" /> <h3>IOT NETWORK MONITOR</h3>
              </>
            )}
            {activeTab === "devices" && (
              <>
                <Cpu className="content-icon" /> <h3>CONNECTED DEVICES</h3>
              </>
            )}
          </div>

          <div className="content-body">
            {activeTab === "history" && (
              <div className="threat-data">
                <table className="attack-table">
                  <thead>
                    <tr>
                      <th>TIMESTAMP</th>
                      <th>ATTACK VECTOR</th>
                      <th>SOURCE</th>
                      <th>DESTINATION</th>
                      <th>CONFIDENCE</th>
                      <th>STATUS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attackDetails.length > 0 ? (
                      attackDetails.map((attack, index) => {
                        const cls = attack.predicted_class || attack.attack || "Unknown";
                        const sev = getAttackSeverity(cls);
                        const time = attack.timestamp
                          ? new Date(attack.timestamp).toLocaleTimeString()
                          : attack.time || "N/A";
                        return (
                          <tr key={index} className={`severity-${sev}`}>
                            <td>{time}</td>
                            <td>{cls}</td>
                            <td>{attack.src_ip || "N/A"}</td>
                            <td>{attack.dst_ip || "N/A"}</td>
                            <td>
                              {attack.confidence
                                ? `${(attack.confidence * 100).toFixed(1)}%`
                                : "N/A"}
                            </td>
                            <td>{attack.status || "Prediction"}</td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan="6" className="no-data">
                          No events recorded yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "chart" && (
              <div className="threat-data chart-container">
                <Line data={iotData} options={chartOptions} height={300} />
              </div>
            )}

            {activeTab === "terminal" && (
              <div className="terminal-container" ref={terminalRef}>
                {terminalOutput.length > 0 ? (
                  terminalOutput.map((entry, index) => (
                    <div key={index} className="terminal-line">
                      {entry}
                    </div>
                  ))
                ) : (
                  <div className="terminal-line">Listening for network telemetry events...</div>
                )}
                <div className="terminal-cursor"></div>
              </div>
            )}

            {activeTab === "devices" && (
              <div className="devices-placeholder">
                <p>Live camera and IoT device monitoring is managed via the Devices page.</p>
                <div className="view-history-btn-container" style={{ marginTop: "1rem" }}>
                  <a href="/devices" className="view-history-btn">
                    <Cpu size={16} /> VIEW NETWORK DEVICES
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="footer-text">
          IOT IDS TERMINAL v2.8 • EVENTS MONITORED: {attackDetails.length} •{" "}
          {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default IOTDetails;
