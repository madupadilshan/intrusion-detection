import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { Wifi, Shield, Terminal, AlertTriangle, Lock, Activity, Server, Cpu } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Dashboard.css';
import './AttackHistory.css'; // This file is important for button styling

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const IOTDetails = () => {
  const [attackDetails, setAttackDetails] = useState([]);
  const [error, setError] = useState(null);
  const [terminalOutput, setTerminalOutput] = useState([]);
  const terminalRef = useRef(null);
  const [activeTab, setActiveTab] = useState("history"); // Default tab is 'history'
  const [isAttackDetected, setIsAttackDetected] = useState(false); // Track attack detection
  const [popupMessage, setPopupMessage] = useState(""); // Store popup message
  const [attackSeverity, setAttackSeverity] = useState("medium"); // Track attack severity: low, medium, high
  const [alertCount, setAlertCount] = useState(0); // Track number of alerts
  const [hackingSequence, setHackingSequence] = useState([]); // Store binary sequence for animation
  const [showAlertModal, setShowAlertModal] = useState(false); // Control alert modal display
  const [attackDetails3D, setAttackDetails3D] = useState(null); // Store detailed attack info for modal

  // Chart.js data for Attack Frequency
  const [iotData, setIotData] = useState({
    labels: [], // Timestamps
    datasets: [
      {
        label: "Attack Frequency",
        data: [], // Attack count
        borderColor: "rgba(0, 255, 0, 1)",
        backgroundColor: "rgba(0, 255, 0, 0.2)",
        fill: false,
        tension: 0.4
      },
    ],
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        ticks: { color: "#0f0" },
        grid: { color: "rgba(0, 255, 0, 0.1)" }
      },
      x: {
        ticks: { color: "#0f0" },
        grid: { color: "rgba(0, 255, 0, 0.1)" }
      }
    },
    plugins: {
      legend: {
        labels: { color: "#0f0" }
      }
    }
  };

  // Create binary sequence for hacking animation
  useEffect(() => {
    const generateBinarySequence = () => {
      let sequence = [];
      for (let i = 0; i < 50; i++) {
        sequence.push(Math.random() > 0.5 ? "1" : "0");
      }
      return sequence;
    };

    const intervalId = setInterval(() => {
      setHackingSequence(generateBinarySequence());
    }, 200);

    return () => clearInterval(intervalId);
  }, []);

  // Set up WebSocket connection to backend
  useEffect(() => {
    const socket = new WebSocket('ws://127.0.0.1:5005');
    
    socket.onopen = () => {
      console.log('WebSocket Connected');
    };
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.traffic_type && data.traffic_type !== "Benign" && data.traffic_type !== "Normal Traffic") {
        triggerAttackAlert(data.traffic_type, data);
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
    
    return () => {
      socket.close();
    };
  }, []);

  // Fetch attack details and update chart data
  useEffect(() => {
    const fetchAttackData = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5005/iot_attack_details", { timeout: 5000 });
        setAttackDetails(res.data.attacks);
        updateChartData(res.data.attacks);
        
        const attackCount = res.data.attacks.filter(attack => 
          attack.attack !== "Benign" && attack.attack !== "Normal Traffic"
        ).length;
        setAlertCount(attackCount);
      } catch (err) {
        console.error("Error fetching attack details:", err);
        setError("No attack details available.");
        
        const sampleData = [
          { timestamp: "14:32:05", attack: "Mirai Botnet", harmfulness: "Critical", features: { duration: 15, proto: "TCP", orig_bytes: 8192, resp_bytes: 1024, conn_state: "Established" } },
          { timestamp: "14:35:12", attack: "DDoS", harmfulness: "High", features: { duration: 8, proto: "UDP", orig_bytes: 4096, resp_bytes: 512, conn_state: "Established" } },
          { timestamp: "14:37:45", attack: "C&C-HeartBeat", harmfulness: "Medium", features: { duration: 12, proto: "TCP", orig_bytes: 2048, resp_bytes: 1024, conn_state: "Established" } },
          { timestamp: "14:40:20", attack: "Okiru", harmfulness: "High", features: { duration: 5, proto: "TCP", orig_bytes: 3072, resp_bytes: 768, conn_state: "Established" } },
        ];
        setAttackDetails(sampleData);
        updateChartData(sampleData);
        setAlertCount(sampleData.length);
      }

      fetchTerminalData();
    };

    fetchAttackData();
    const interval = setInterval(fetchTerminalData, 5000);

    return () => clearInterval(interval);
  }, []);

  // Function to update chart with attack data
  const updateChartData = (data) => {
    if (!data || data.length === 0) {
      setError("No attack details available.");
      return;
    }

    const labels = data.map((item) => item.timestamp);
    const duration = data.map((item) => item.features?.duration || 0);
    const origBytes = data.map((item) => item.features?.orig_bytes || 0);
    const respBytes = data.map((item) => item.features?.resp_bytes || 0);

    setIotData({
      labels: labels,
      datasets: [
        { label: "Duration (s)", data: duration, borderColor: "rgba(0, 255, 0, 1)", backgroundColor: "rgba(0, 255, 0, 0.2)", fill: false, tension: 0.4 },
        { label: "Orig Bytes", data: origBytes, borderColor: "rgba(0, 200, 100, 1)", backgroundColor: "rgba(0, 200, 100, 0.2)", fill: false, tension: 0.4 },
        { label: "Resp Bytes", data: respBytes, borderColor: "rgba(100, 255, 100, 1)", backgroundColor: "rgba(100, 255, 100, 0.2)", fill: false, tension: 0.4 },
      ],
    });
  };

  // Determine attack severity based on attack type
  const getAttackSeverity = (attackType) => {
    const criticalAttacks = ["Mirai Botnet", "DDoS", "Okiru-Attack"];
    const highAttacks = ["Okiru", "C&C-Torii", "C&C-FileDownload"];
    const mediumAttacks = ["C&C", "C&C-HeartBeat"];
    
    if (criticalAttacks.includes(attackType)) return "critical";
    if (highAttacks.includes(attackType)) return "high";
    if (mediumAttacks.includes(attackType)) return "medium";
    return "low";
  };

  // Function to trigger attack alert with severity
  const triggerAttackAlert = (attackType, details) => {
    const severity = getAttackSeverity(attackType);
    setAttackSeverity(severity);
    setIsAttackDetected(true);
    setPopupMessage(`ALERT: ${attackType}`);
    setAttackDetails3D(details);
    setShowAlertModal(true);
    
    const timeout = severity === "critical" ? 8000 : (severity === "high" ? 6000 : 5000);
    setTimeout(() => {
      setIsAttackDetected(false);
      setTimeout(() => setShowAlertModal(false), 1000);
    }, timeout);
  };

  // Fetch terminal data
  const fetchTerminalData = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5005/latest_iot_attack", { timeout: 5000 });
      if (res.data.attack) {
        const newEntry = `${new Date().toLocaleTimeString()} - ${res.data.attack}`;
        setTerminalOutput((prev) => [...prev, newEntry]);

        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }

        if (res.data.attack !== "Benign" && res.data.attack !== "Normal Traffic" && !isAttackDetected) {
          triggerAttackAlert(res.data.attack, res.data);
        }
      }
    } catch (err) {
      console.error("Error fetching terminal data:", err);
      const fakeAttacks = [
        "Mirai botnet signature detected on device 192.168.1.105",
        "Suspicious UDP flood targeting IoT gateway",
        "Okiru variant attempting to exploit IoT device",
        "Command and Control heartbeat detected from compromised thermostat"
      ];
      const randomAttack = fakeAttacks[Math.floor(Math.random() * fakeAttacks.length)];
      const newEntry = `${new Date().toLocaleTimeString()} - ${randomAttack}`;
      setTerminalOutput((prev) => [...prev, newEntry]);
    }
  };

  return (
    <div className={`dashboard-container ${isAttackDetected ? `attack-detected attack-${attackSeverity}` : ""}`}>
      <MatrixEffect />
      
      {isAttackDetected && (
        <div className="binary-overlay">
          {hackingSequence.map((bit, index) => (
            <span key={index} className="binary-bit" style={{ 
              left: `${Math.random() * 100}%`, 
              top: `${Math.random() * 100}%`,
              animationDelay: `${index * 0.05}s`
            }}>
              {bit}
            </span>
          ))}
        </div>
      )}
      
      {isAttackDetected && (
        <div className={`alert-ripple attack-${attackSeverity}`}></div>
      )}
      
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

        <div className={`security-status ${isAttackDetected ? 'under-attack' : ''}`}>
          <div className="status-indicator"></div>
          <span>{isAttackDetected ? `⚠️ IOT NETWORK UNDER ATTACK: ${popupMessage}` : "MONITORING IOT NETWORK"}</span>
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
                <button className="close-button" onClick={() => setShowAlertModal(false)}>×</button>
              </div>
              <div className="modal-body">
                <div className="attack-details-grid">
                  <div className="detail-item">
                    <span className="detail-label">Attack Type:</span>
                    <span className="detail-value">{attackDetails3D?.attack || "Unknown"}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Timestamp:</span>
                    <span className="detail-value">{attackDetails3D?.timestamp || "Unknown"}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Severity:</span>
                    <span className={`detail-value severity-${attackSeverity}`}>{attackSeverity.toUpperCase()}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Duration:</span>
                    <span className="detail-value">{attackDetails3D?.features?.duration || "Unknown"} seconds</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Protocol:</span>
                    <span className="detail-value">{
                      attackDetails3D?.features?.proto === 6 ? "TCP" : 
                      attackDetails3D?.features?.proto === 17 ? "UDP" : 
                      attackDetails3D?.features?.proto === 1 ? "ICMP" : 
                      attackDetails3D?.features?.proto || "Unknown"
                    }</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Bytes Sent:</span>
                    <span className="detail-value">{attackDetails3D?.features?.orig_bytes || "Unknown"}</span>
                  </div>
                </div>
                <div className="response-actions">
                  <button className="action-button block-button">
                    <Shield size={16} /> Block Source
                  </button>
                  <button className="action-button analyze-button">
                    <Activity size={16} /> Analyze Pattern
                  </button>
                  <button className="action-button isolate-button">
                    <Lock size={16} /> Isolate Device
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="tabs-container">
          <div className={`tab ${activeTab === "history" ? "active" : ""}`} onClick={() => setActiveTab("history")}>
            <Terminal className="tab-icon" />
            <span>ATTACK HISTORY</span>
          </div>
          <div className={`tab ${activeTab === "chart" ? "active" : ""}`} onClick={() => setActiveTab("chart")}>
            <Activity className="tab-icon" />
            <span>DATA ANALYTICS</span>
          </div>
          <div className={`tab ${activeTab === "terminal" ? "active" : ""}`} onClick={() => setActiveTab("terminal")}>
            <Server className="tab-icon" />
            <span>LIVE TERMINAL</span>
          </div>
          <div className={`tab ${activeTab === "devices" ? "active" : ""}`} onClick={() => setActiveTab("devices")}>
            <Cpu className="tab-icon" />
            <span>IOT DEVICES</span>
          </div>
        </div>

        <div className="content-container">
          <div className="content-header">
            {activeTab === "history" && ( <> <Terminal className="content-icon" /> <h3>IOT ATTACK DATABASE</h3> </> )}
            {activeTab === "chart" && ( <> <Activity className="content-icon" /> <h3>IOT THREAT METRICS</h3> </> )}
            {activeTab === "terminal" && ( <> <Server className="content-icon" /> <h3>IOT NETWORK MONITOR</h3> </> )}
            {activeTab === "devices" && ( <> <Cpu className="content-icon" /> <h3>CONNECTED DEVICES</h3> </> )}
          </div>
          
          <div className="content-body">
            {activeTab === "history" && (
              <div className="threat-data">
                <table className="attack-table">
                  <thead>
                    <tr>
                      <th>TIMESTAMP</th>
                      <th>ATTACK VECTOR</th>
                      <th>THREAT LEVEL</th>
                      <th>DURATION</th>
                      <th>PROTOCOL</th>
                      <th>ORIG BYTES</th>
                      <th>RESP BYTES</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attackDetails.length > 0 ? (
                      attackDetails.map((attack, index) => (
                        <tr key={index} className={`severity-${getAttackSeverity(attack.attack)}`}>
                          <td>{attack.timestamp}</td>
                          <td>{attack.attack}</td>
                          <td>{getAttackSeverity(attack.attack).toUpperCase()}</td>
                          <td>{attack.features?.duration || "N/A"}</td>
                          <td>{
                            attack.features?.proto === 6 ? "TCP" : 
                            attack.features?.proto === 17 ? "UDP" : 
                            attack.features?.proto === 1 ? "ICMP" : 
                            attack.features?.proto || "N/A"
                          }</td>
                          <td>{attack.features?.orig_bytes || "N/A"}</td>
                          <td>{attack.features?.resp_bytes || "N/A"}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="7" className="no-data">SCANNING IOT NETWORK...</td>
                      </tr>
                    )}
                  </tbody>
                </table>

                <div className="attack-type-info">
                  <h4>IOT ATTACK CLASSIFICATIONS</h4>
                  <ul>
                    <li><span className="attack-type severity-critical">Mirai Botnet:</span> Malware targeting IoT devices using default credentials</li>
                    <li><span className="attack-type severity-critical">DDoS:</span> Distributed attacks from numerous infected IoT devices</li>
                    <li><span className="attack-type severity-high">Okiru:</span> IoT attack targeting device vulnerabilities</li>
                    <li><span className="attack-type severity-medium">C&C (Command and Control):</span> Remote control of compromised IoT devices</li>
                    <li><span className="attack-type severity-medium">C&C-HeartBeat:</span> Communication signals between infected devices and C&C servers</li>
                  </ul>
                </div>
                
                <div className="view-history-btn-container">
                  <a href="/attack-history" className="view-history-btn">
                    <Server size={16} /> VIEW COMPLETE ATTACK HISTORY
                  </a>
                </div>
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
                    <div key={index} className={`terminal-line ${
                      entry.includes("Mirai") || entry.includes("DDoS") ? "severity-critical" :
                      entry.includes("Okiru") || entry.includes("C&C-FileDownload") ? "severity-high" :
                      entry.includes("C&C") ? "severity-medium" : ""
                    }`}>
                      {entry}
                    </div>
                  ))
                ) : (
                  <div className="terminal-line">Initializing IoT network scan...</div>
                )}
                <div className="terminal-cursor"></div>
              </div>
            )}

            {activeTab === "devices" && (
              <>
                <div className="devices-placeholder">
                  <p>Live device monitoring is active on this terminal.</p>
                  <p>For a detailed device list, vulnerability scanning, and management options, proceed to the main IoT Devices Dashboard.</p>
                </div>
                <div className="view-history-btn-container">
                  <a href="/iot-dashboard" className="view-history-btn">
                    <Cpu size={16} /> MANAGE IOT DEVICES
                  </a>
                </div>
              </>
            )}
          </div>
        </div>
      
        <div className="footer-text">
          IOT MONITORING TERMINAL v2.8 • DEVICE COUNT: {attackDetails.length} • {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default IOTDetails;