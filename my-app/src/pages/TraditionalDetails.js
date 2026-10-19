import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { Wifi, Shield, Terminal, AlertTriangle, Lock, Activity, Server, Cpu } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Dashboard.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TraditionalDetails = () => {
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
  const [traditionalData, setTraditionalData] = useState({
    labels: [], // Timestamps
    datasets: [
      {
        label: "Duration (s)",
        data: [], // Duration
        borderColor: "rgba(0, 255, 0, 1)",
        backgroundColor: "rgba(0, 255, 0, 0.2)",
        fill: false,
        tension: 0.4
      },
      {
        label: "Src Bytes",
        data: [], // Source bytes
        borderColor: "rgba(0, 200, 100, 1)",
        backgroundColor: "rgba(0, 200, 100, 0.2)",
        fill: false,
        tension: 0.4
      },
      {
        label: "Dst Bytes",
        data: [], // Destination bytes
        borderColor: "rgba(100, 255, 100, 1)",
        backgroundColor: "rgba(100, 255, 100, 0.2)",
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
    // Create WebSocket connection to backend
    const socket = new WebSocket('ws://127.0.0.1:5007');
    
    socket.onopen = () => {
      console.log('WebSocket Connected');
    };
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle all traffic types, not just attacks
        if (data.traffic_type) {
          // Add to terminal output for all traffic
          const newEntry = `${data.timestamp} - ${getDisplayAttackName(data.traffic_type)}`;
          setTerminalOutput(prev => [...prev, newEntry]);
          
          // Auto-scroll terminal
          if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
          }
          
          // Only trigger alert for non-normal traffic
          if (data.traffic_type !== "Normal" && data.traffic_type !== "Benign") {
            triggerAttackAlert(data.traffic_type, data);
          }
        }
      } catch (err) {
        console.error('WebSocket message parsing error:', err);
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
    
    return () => {
      socket.close();
    };
  }, []);

  // Generate attack attempts periodically for simulation
  useEffect(() => {
    // Periodically trigger flood detection API to simulate attack
    const simulateAttackIntervalId = setInterval(() => {
      axios.get("http://127.0.0.1:5007/flood_attack")
        .then(res => {
          console.log("Flood simulation response:", res.data);
        })
        .catch(err => {
          console.error("Error in flood simulation:", err);
        });
    }, 15000); // Every 15 seconds

    return () => clearInterval(simulateAttackIntervalId);
  }, []);

  // Fetch attack details and update chart data
  useEffect(() => {
    const fetchAttackData = async () => {
      try {
        // Use the correct endpoint from server_kdd.py
        const res = await axios.get("http://127.0.0.1:5007/kdd_attack_details", { timeout: 5000 });
        
        if (res.data && res.data.attacks) {
          setAttackDetails(res.data.attacks);
          updateChartData(res.data.attacks); // Update chart data
          
          // Update alert count - only count actual attacks (not Normal traffic)
          const attackCount = res.data.attacks.filter(attack => 
            attack.attack !== "Normal" && attack.attack !== "Benign"
          ).length;
          setAlertCount(attackCount);
        }
      } catch (err) {
        console.error("Error fetching attack details:", err);
        setError("No attack details available.");
        
        // Sample data for preview if API fails - using NSL-KDD classifications
        const sampleData = [
          { 
            timestamp: "14:32:05", 
            attack: "DoS", 
            features: {
              duration: 15,
              protocol: 6, // TCP
              service: 0,
              flag: 5,
              src_bytes: 8192,
              dst_bytes: 1024,
              land: 0,
              wrong_fragment: 0,
              urgent: 0,
              hot: 0
            }
          },
          { 
            timestamp: "14:35:12", 
            attack: "Probe", 
            features: {
              duration: 8,
              protocol: 17, // UDP
              service: 0,
              flag: 2,
              src_bytes: 4096,
              dst_bytes: 512,
              land: 0,
              wrong_fragment: 0,
              urgent: 0,
              hot: 0
            }
          },
          { 
            timestamp: "14:37:45", 
            attack: "R2L", 
            features: {
              duration: 12,
              protocol: 6, // TCP
              service: 0,
              flag: 5,
              src_bytes: 2048,
              dst_bytes: 1024,
              land: 0,
              wrong_fragment: 0,
              urgent: 0,
              hot: 0
            }
          },
          { 
            timestamp: "14:40:20", 
            attack: "U2R", 
            features: {
              duration: 5,
              protocol: 6, // TCP
              service: 0,
              flag: 5,
              src_bytes: 3072,
              dst_bytes: 768,
              land: 0,
              wrong_fragment: 0,
              urgent: 0,
              hot: 0
            }
          },
          {
            timestamp: "14:42:15",
            attack: "Normal",
            features: {
              duration: 2,
              protocol: 6, // TCP
              service: 0,
              flag: 5,
              src_bytes: 1024,
              dst_bytes: 512,
              land: 0,
              wrong_fragment: 0,
              urgent: 0,
              hot: 0
            }
          }
        ];
        setAttackDetails(sampleData);
        updateChartData(sampleData);
        setAlertCount(sampleData.filter(item => item.attack !== "Normal" && item.attack !== "Benign").length);
      }

      fetchTerminalData();
    };

    fetchAttackData();
    const interval = setInterval(fetchAttackData, 10000); // Refresh every 10 seconds

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
    const srcBytes = data.map((item) => item.features?.src_bytes || 0);
    const dstBytes = data.map((item) => item.features?.dst_bytes || 0);

    setTraditionalData({
      labels: labels,
      datasets: [
        {
          label: "Duration (s)",
          data: duration,
          borderColor: "rgba(0, 255, 0, 1)",
          backgroundColor: "rgba(0, 255, 0, 0.2)",
          fill: false,
          tension: 0.4
        },
        {
          label: "Src Bytes",
          data: srcBytes,
          borderColor: "rgba(0, 200, 100, 1)",
          backgroundColor: "rgba(0, 200, 100, 0.2)",
          fill: false,
          tension: 0.4
        },
        {
          label: "Dst Bytes",
          data: dstBytes,
          borderColor: "rgba(100, 255, 100, 1)",
          backgroundColor: "rgba(100, 255, 100, 0.2)",
          fill: false,
          tension: 0.4
        },
      ],
    });
  };

  // Determine attack severity based on attack type from NSL-KDD model
  const getAttackSeverity = (attackType) => {
    const criticalAttacks = ["DoS"];
    const highAttacks = ["R2L", "U2R"];
    const mediumAttacks = ["Probe"];
    
    if (criticalAttacks.includes(attackType)) return "critical";
    if (highAttacks.includes(attackType)) return "high";
    if (mediumAttacks.includes(attackType)) return "medium";
    if (attackType === "Normal" || attackType === "Benign") return "normal";
    return "low";
  };

  // Function to get more user-friendly attack names for display
  const getDisplayAttackName = (attackType) => {
    const attackNames = {
      "DoS": "Denial of Service",
      "R2L": "Remote to Local",
      "U2R": "User to Root",
      "Probe": "Network Probe",
      "Normal": "Normal Traffic",
      "Benign": "Benign Traffic"
    };
    
    return attackNames[attackType] || attackType;
  };

  // Function to trigger attack alert with severity
  const triggerAttackAlert = (attackType, details) => {
    // Only trigger alerts for actual attacks
    if (attackType === "Normal" || attackType === "Benign") {
      return;
    }
    
    const severity = getAttackSeverity(attackType);
    setAttackSeverity(severity);
    setIsAttackDetected(true);
    setPopupMessage(`ALERT: ${getDisplayAttackName(attackType)}`);
    setAttackDetails3D(details);
    setShowAlertModal(true);
    
    // Auto close attack alert after a delay
    const timeout = severity === "critical" ? 8000 : (severity === "high" ? 6000 : 5000);
    setTimeout(() => {
      setIsAttackDetected(false);
      // Keep modal visible slightly longer
      setTimeout(() => setShowAlertModal(false), 1000);
    }, timeout);
  };

  // Fetch latest attack data for terminal display
  const fetchTerminalData = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5007/latest_kdd_attack", { timeout: 5000 });
      if (res.data && res.data.attack) {
        // Include all traffic types
        const newEntry = `${res.data.timestamp} - ${getDisplayAttackName(res.data.attack)}`;
        setTerminalOutput((prev) => [...prev, newEntry]);

        // Auto-scroll terminal
        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }

        // Only trigger alert for non-normal traffic
        if (!isAttackDetected && res.data.attack !== "Normal" && res.data.attack !== "Benign") {
          triggerAttackAlert(res.data.attack, res.data);
        }
      }
    } catch (err) {
      console.error("Error fetching terminal data:", err);
      const fakeAttacks = [
        "DoS attack detected targeting server",
        "Probe activity detected in network",
        "Potential R2L attempt on admin portal",
        "U2R privilege escalation warning",
        "Normal traffic detected"
      ];
      const randomAttack = fakeAttacks[Math.floor(Math.random() * fakeAttacks.length)];
      const newEntry = `${new Date().toLocaleTimeString()} - ${randomAttack}`;
      setTerminalOutput((prev) => [...prev, newEntry]);
    }
  };

  return (
    <div className={`dashboard-container ${isAttackDetected ? `attack-detected attack-${attackSeverity}` : ""}`}>
      <MatrixEffect />
      
      {/* Hacking Binary Overlay (only visible during attack) */}
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
      
      {/* Alert Ripple Effect (only visible during attack) */}
      {isAttackDetected && (
        <div className={`alert-ripple attack-${attackSeverity}`}></div>
      )}
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <Wifi className="terminal-icon" />
          <h1 className="dashboard-title">NSL-KDD THREAT ANALYSIS</h1>
          <Terminal className="terminal-icon" />
          <div className="alert-counter">
            <AlertTriangle className="alert-icon" />
            <span className="alert-badge">{alertCount}</span>
          </div>
        </div>

        {/* Security Status Banner */}
        <div className={`security-status ${isAttackDetected ? 'under-attack' : ''}`}>
          <div className="status-indicator"></div>
          <span>{isAttackDetected ? `⚠️ NETWORK UNDER ATTACK: ${popupMessage}` : "MONITORING NETWORK TRAFFIC"}</span>
          <div className="status-indicator"></div>
        </div>
        
        {/* Alert Popup */}
        {isAttackDetected && (
          <div className={`alert-popup attack-${attackSeverity}`}>
            <AlertTriangle size={24} />
            <span>{popupMessage}</span>
          </div>
        )}

        {/* Detailed Attack Modal */}
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
                    <span className="detail-value">{getDisplayAttackName(attackDetails3D?.attack || "Unknown")}</span>
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
                      attackDetails3D?.features?.protocol === 6 ? "TCP" : 
                      attackDetails3D?.features?.protocol === 17 ? "UDP" : 
                      attackDetails3D?.features?.protocol === 1 ? "ICMP" : 
                      "Unknown"
                    }</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Bytes Sent:</span>
                    <span className="detail-value">{attackDetails3D?.features?.src_bytes || "Unknown"}</span>
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

        {/* Tabs Section */}
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
            <span>NETWORK DEVICES</span>
          </div>
        </div>

        {/* Content Section */}
        <div className="content-container">
          <div className="content-header">
            {activeTab === "history" && (
              <>
                <Terminal className="content-icon" />
                <h3>ATTACK DATABASE</h3>
              </>
            )}
            {activeTab === "chart" && (
              <>
                <Activity className="content-icon" />
                <h3>THREAT METRICS</h3>
              </>
            )}
            {activeTab === "terminal" && (
              <>
                <Server className="content-icon" />
                <h3>NETWORK MONITOR</h3>
              </>
            )}
            {activeTab === "devices" && (
              <>
                <Cpu className="content-icon" />
                <h3>CONNECTED DEVICES</h3>
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
                      <th>TRAFFIC TYPE</th>
                      <th>STATUS</th>
                      <th>DURATION</th>
                      <th>PROTOCOL</th>
                      <th>SRC BYTES</th>
                      <th>DST BYTES</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attackDetails.length > 0 ? (
                      // Show all traffic types including Normal
                      attackDetails.map((attack, index) => (
                        <tr key={index} className={`severity-${getAttackSeverity(attack.attack)}`}>
                          <td>{attack.timestamp}</td>
                          <td>{getDisplayAttackName(attack.attack)}</td>
                          <td>{getAttackSeverity(attack.attack).toUpperCase()}</td>
                          <td>{attack.features?.duration || "N/A"}</td>
                          <td>{
                            attack.features?.protocol === 6 ? "TCP" : 
                            attack.features?.protocol === 17 ? "UDP" : 
                            attack.features?.protocol === 1 ? "ICMP" : 
                            "Unknown"
                          }</td>
                          <td>{attack.features?.src_bytes || "N/A"}</td>
                          <td>{attack.features?.dst_bytes || "N/A"}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="7" className="no-data">SCANNING NETWORK...</td>
                      </tr>
                    )}
                  </tbody>
                </table>

                <div className="attack-type-info">
                  <h4>NSL-KDD TRAFFIC CLASSIFICATIONS</h4>
                  <ul>
                    <li><span className="attack-type severity-critical">DoS (Denial of Service):</span> Attacks that attempt to make network resources unavailable to intended users</li>
                    <li><span className="attack-type severity-high">R2L (Remote to Local):</span> Unauthorized access from a remote machine</li>
                    <li><span className="attack-type severity-high">U2R (User to Root):</span> Unauthorized access to local superuser privileges</li>
                    <li><span className="attack-type severity-medium">Probe:</span> Surveillance and other probing attacks</li>
                    <li><span className="attack-type severity-normal">Normal:</span> Standard network traffic</li>
                  </ul>
                </div>
              </div>
            )}
            
            {activeTab === "chart" && (
              <div className="threat-data chart-container">
                <Line data={traditionalData} options={chartOptions} height={300} />
              </div>
            )}
            
            {activeTab === "terminal" && (
              <div className="terminal-container" ref={terminalRef}>
                {terminalOutput.length > 0 ? (
                  terminalOutput.map((entry, index) => (
                    <div key={index} className={`terminal-line ${
                      entry.includes("Denial of Service") ? "severity-critical" :
                      entry.includes("Remote to Local") || entry.includes("User to Root") ? "severity-high" :
                      entry.includes("Network Probe") ? "severity-medium" :
                      entry.includes("Normal Traffic") ? "severity-normal" : ""
                    }`}>
                      {entry}
                    </div>
                  ))
                ) : (
                  <div className="terminal-line">Initializing network scan...</div>
                )}
                <div className="terminal-cursor"></div>
              </div>
            )}
            
            {activeTab === "devices" && (
              <div className="devices-grid">
                {/* Sample network devices */}
                <div className="device-card">
                  <Cpu className="device-icon" />
                  <div className="device-info">
                    <h4>Web Server</h4>
                    <p>IP: 192.168.1.10</p>
                    <p>Status: <span className="status-online">Online</span></p>
                  </div>
                  <div className="device-status safe"></div>
                </div>
                <div className="device-card">
                  <Cpu className="device-icon" />
                  <div className="device-info">
                    <h4>Database Server</h4>
                    <p>IP: 192.168.1.12</p>
                    <p>Status: <span className="status-online">Online</span></p>
                  </div>
                  <div className="device-status warning"></div>
                </div>
                <div className="device-card">
                  <Cpu className="device-icon" />
                  <div className="device-info">
                    <h4>Admin Workstation</h4>
                    <p>IP: 192.168.1.15</p>
                    <p>Status: <span className="status-offline">Online</span></p>
                  </div>
                  <div className="device-status safe"></div>
                </div>
                <div className="device-card">
                  <Cpu className="device-icon" />
                  <div className="device-info">
                    <h4>File Server</h4>
                    <p>IP: 192.168.1.20</p>
                    <p>Status: <span className="status-offline">Offline</span></p>
                  </div>
                  <div className="device-status danger"></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* View History Button - Now moved to the bottom of the page outside of tab content */}
        <div className="view-history-btn-container">
          <a href="/attack-history-kdd" className="view-history-btn">
            <Server size={16} /> VIEW COMPLETE KDD ATTACK HISTORY
          </a>
        </div>

        <div className="footer-text">
          NSL-KDD MONITORING SYSTEM v1.3 • DEVICE COUNT: 18 • {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default TraditionalDetails;