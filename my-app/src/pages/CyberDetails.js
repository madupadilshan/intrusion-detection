import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { Bug, Shield, Terminal, AlertTriangle, Lock, Activity, Server, Cpu } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Dashboard.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const CyberDetails = () => {
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
  const [cyberData, setCyberData] = useState({
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
    // Create WebSocket connection to backend
    const socket = new WebSocket('ws://127.0.0.1:5006');
    
    socket.onopen = () => {
      console.log('WebSocket Connected');
    };
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Handle both attack and new_packet events from Python backend
      if ((data.attack && data.attack !== "BENIGN") || 
          (data.traffic_type && data.traffic_type !== "BENIGN")) {
        // Extract attack information
        const attackType = data.attack || data.traffic_type;
        triggerAttackAlert(attackType, data);
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
    
    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    const fetchAttackData = async () => {
      try {
        // Updated endpoint to match Python backend
        const res = await axios.get("http://127.0.0.1:5006/cicids_attack_details", { timeout: 5000 });
        setAttackDetails(res.data.attacks);
        updateChartData(res.data.attacks); // Update chart data
        
        // Update alert count - filtering out benign traffic
        const attackCount = res.data.attacks.filter(attack => 
          attack.attack !== "BENIGN"
        ).length;
        setAlertCount(attackCount);
      } catch (err) {
        console.error("Error fetching attack details:", err);
        setError("No attack details available.");
        
        // Sample data for preview if API fails - updated to match CICIDS2017 attack types
        const sampleData = [
          { 
            timestamp: "14:32:05", 
            attack: "DoS Hulk", 
            harmfulness: "Critical",
            features: {
              duration: 15,
              proto: 6,
              orig_bytes: 540,
              resp_bytes: 120,
              missed_bytes: 0,
              orig_pkts: 12,
              resp_pkts: 8,
              conn_state: 1,
              history: 7,
              service: 80
            }
          },
          { 
            timestamp: "14:35:12", 
            attack: "Web Attack", 
            harmfulness: "High",
            features: {
              duration: 8,
              proto: 6,
              orig_bytes: 280,
              resp_bytes: 420,
              missed_bytes: 0,
              orig_pkts: 5,
              resp_pkts: 6,
              conn_state: 1,
              history: 5,
              service: 443
            }
          },
          { 
            timestamp: "14:37:45", 
            attack: "PortScan", 
            harmfulness: "Medium",
            features: {
              duration: 12,
              proto: 6,
              orig_bytes: 180,
              resp_bytes: 0,
              missed_bytes: 0,
              orig_pkts: 15,
              resp_pkts: 0,
              conn_state: 2,
              history: 1,
              service: 0
            }
          },
          { 
            timestamp: "14:40:20", 
            attack: "DDoS", 
            harmfulness: "Critical",
            features: {
              duration: 5,
              proto: 17,
              orig_bytes: 3500,
              resp_bytes: 0,
              missed_bytes: 0,
              orig_pkts: 200,
              resp_pkts: 0,
              conn_state: 0,
              history: 0,
              service: 53
            }
          },
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
    
    // Extract features that match the Python backend
    const duration = data.map((item) => item.features?.duration || 0);
    const origPackets = data.map((item) => item.features?.orig_pkts || 0);
    const respPackets = data.map((item) => item.features?.resp_pkts || 0);

    setCyberData({
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
          label: "Original Packets",
          data: origPackets,
          borderColor: "rgba(0, 200, 100, 1)",
          backgroundColor: "rgba(0, 200, 100, 0.2)",
          fill: false,
          tension: 0.4
        },
        {
          label: "Response Packets",
          data: respPackets,
          borderColor: "rgba(100, 255, 100, 1)",
          backgroundColor: "rgba(100, 255, 100, 0.2)",
          fill: false,
          tension: 0.4
        },
      ],
    });
  };

  // Determine attack severity based on attack type from CICIDS dataset
  const getAttackSeverity = (attackType) => {
    if (!attackType) return "low";
    
    // Updated to match CICIDS2017 attack types
    const criticalAttacks = ["DoS Hulk", "DDoS", "Heartbleed"];
    const highAttacks = ["DoS GoldenEye", "Web Attack", "Infiltration", "Botnet"];
    const mediumAttacks = ["DoS slowloris", "DoS Slowhttptest", "PortScan", "Brute Force"];
    
    if (criticalAttacks.some(attack => attackType.includes(attack))) return "critical";
    if (highAttacks.some(attack => attackType.includes(attack))) return "high";
    if (mediumAttacks.some(attack => attackType.includes(attack))) return "medium";
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
    
    // Auto close attack alert after a delay
    const timeout = severity === "critical" ? 8000 : (severity === "high" ? 6000 : 5000);
    setTimeout(() => {
      setIsAttackDetected(false);
      // Keep modal visible slightly longer
      setTimeout(() => setShowAlertModal(false), 1000);
    }, timeout);
  };

  // Fetch terminal data
  const fetchTerminalData = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5006/latest_cicids_attack", { timeout: 5000 });
      if (res.data.attack) {
        const newEntry = `${new Date().toLocaleTimeString()} - ${res.data.attack}`;
        setTerminalOutput((prev) => [...prev, newEntry]);

        // Auto-scroll terminal
        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }

        // Check for attack detection and trigger popup with appropriate severity
        if (res.data.attack !== "BENIGN" && !isAttackDetected) {
          triggerAttackAlert(res.data.attack, res.data);
        }
      }
    } catch (err) {
      console.error("Error fetching terminal data:", err);
      // Updated sample attacks to match CICIDS2017 attack types
      const fakeAttacks = [
        "DoS Hulk attack detected from 192.168.1.45",
        "Multiple PortScan activities detected on port 80",
        "Potential Web Attack identified in HTTP traffic",
        "DDoS attempt detected targeting main server"
      ];
      const randomAttack = fakeAttacks[Math.floor(Math.random() * fakeAttacks.length)];
      const newEntry = `${new Date().toLocaleTimeString()} - ${randomAttack}`;
      setTerminalOutput((prev) => [...prev, newEntry]);
    }
  };

  // Function to simulate DDoS for testing the interface
  const simulateFloodAttack = async () => {
    try {
      // Send multiple rapid requests to trigger the flood detection in the backend
      for (let i = 0; i < 7; i++) {
        await axios.get("http://127.0.0.1:5006/flood_attack");
      }
      console.log("Flood attack simulation triggered");
    } catch (err) {
      console.error("Error simulating flood attack:", err);
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
          <Bug className="terminal-icon" />
          <h1 className="dashboard-title">CICIDS2017 THREAT ANALYSIS</h1>
          <Terminal className="terminal-icon" />
          <div className="alert-counter">
            <AlertTriangle className="alert-icon" />
            <span className="alert-badge">{alertCount}</span>
          </div>
        </div>

        {/* Security Status Banner */}
        <div className={`security-status ${isAttackDetected ? 'under-attack' : ''}`}>
          <div className="status-indicator"></div>
          <span>{isAttackDetected ? `⚠️ NETWORK UNDER ATTACK: ${popupMessage}` : "MONITORING CICIDS THREATS"}</span>
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
                    <span className="detail-value">{attackDetails3D?.attack || attackDetails3D?.traffic_type || "Unknown"}</span>
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
                      "Unknown"
                    }</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Packet Count:</span>
                    <span className="detail-value">
                      {(attackDetails3D?.features?.orig_pkts || 0) + (attackDetails3D?.features?.resp_pkts || 0)}
                    </span>
                  </div>
                </div>
                <div className="response-actions">
                  <button className="action-button block-button">
                    <Shield size={16} /> Block Traffic
                  </button>
                  <button className="action-button analyze-button">
                    <Activity size={16} /> Analyze Pattern
                  </button>
                  <button className="action-button isolate-button">
                    <Lock size={16} /> Quarantine Network
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
            className={`tab ${activeTab === "network" ? "active" : ""}`} 
            onClick={() => setActiveTab("network")}
          >
            <Cpu className="tab-icon" />
            <span>SIMULATION</span>
          </div>
        </div>

        {/* Content Section */}
        <div className="content-container">
          <div className="content-header">
            {activeTab === "history" && (
              <>
                <Terminal className="content-icon" />
                <h3>CICIDS2017 ATTACK DATABASE</h3>
              </>
            )}
            {activeTab === "chart" && (
              <>
                <Activity className="content-icon" />
                <h3>TRAFFIC METRICS</h3>
              </>
            )}
            {activeTab === "terminal" && (
              <>
                <Server className="content-icon" />
                <h3>LIVE IDS MONITOR</h3>
              </>
            )}
            {activeTab === "network" && (
              <>
                <Cpu className="content-icon" />
                <button 
                  className="action-button simulate-button"
                  onClick={simulateFloodAttack}
                >
                  SIMULATE DDOS ATTACK
                </button>
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
                      <th>THREAT LEVEL</th>
                      <th>DURATION</th>
                      <th>PROTOCOL</th>
                      <th>ORIG PACKETS</th>
                      <th>RESP PACKETS</th>
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
                            "TCP"
                          }</td>
                          <td>{attack.features?.orig_pkts || "N/A"}</td>
                          <td>{attack.features?.resp_pkts || "N/A"}</td>
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
                  <h4>CICIDS2017 ATTACK CLASSIFICATIONS</h4>
                  <ul>
                    <li><span className="attack-type severity-critical">DoS Hulk:</span> High-volume HTTP flooding attack</li>
                    <li><span className="attack-type severity-high">DoS GoldenEye:</span> HTTP/S denial of service attack</li>
                    <li><span className="attack-type severity-medium">DoS slowloris:</span> Slow HTTP header DoS attack</li>
                    <li><span className="attack-type severity-medium">PortScan:</span> Scanning target ports to find vulnerabilities</li>
                    <li><span className="attack-type severity-critical">DDoS:</span> Distributed denial of service attack</li>
                    <li><span className="attack-type severity-high">Web Attack:</span> Includes SQL injections, XSS, etc.</li>
                    <li><span className="attack-type severity-high">Botnet:</span> Network of compromised machines</li>
                    <li><span className="attack-type severity-medium">Brute Force:</span> Attempting to crack passwords</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === "chart" && (
              <div className="threat-data chart-container">
                <Line data={cyberData} options={chartOptions} height={300} />
              </div>
            )}
            
            {activeTab === "terminal" && (
              <div className="terminal-container" ref={terminalRef}>
                {terminalOutput.length > 0 ? (
                  terminalOutput.map((entry, index) => (
                    <div key={index} className={`terminal-line ${
                      entry.includes("DoS Hulk") || entry.includes("DDoS") || entry.includes("Heartbleed") ? "severity-critical" :
                      entry.includes("DoS GoldenEye") || entry.includes("Web Attack") || entry.includes("Botnet") ? "severity-high" :
                      entry.includes("PortScan") || entry.includes("Brute Force") ? "severity-medium" : ""
                    }`}>
                      {entry}
                    </div>
                  ))
                ) : (
                  <div className="terminal-line">Initializing CICIDS2017 threat monitor...</div>
                )}
                <div className="terminal-cursor"></div>
              </div>
            )}
            
            {activeTab === "network" && (
              <div className="network-map">
                <h3>CICIDS2017 Attack Simulation</h3>
                <p className="simulation-info">
                  Click the "SIMULATE DDOS ATTACK" button above to trigger a simulated DDoS attack. 
                  This will send multiple rapid requests to the backend to activate the flood detection mechanism.
                </p>
                
                <div className="simulation-description">
                  <h4>About CICIDS2017 Dataset</h4>
                  <p>
                    The CICIDS2017 dataset contains benign and common attack network flows, including:
                    Brute Force, Heartbleed, Botnet, DoS, DDoS, Web Attacks, and Infiltration attacks.
                    This dashboard monitors and classifies these attacks in real-time.
                  </p>
                  
                  <h4>Features Used for Detection</h4>
                  <div className="feature-grid">
                    <div className="feature-column">
                      <ul>
                        <li>Flow Duration</li>
                        <li>Protocol Type</li>
                        <li>Packet Count</li>
                        <li>Byte Count</li>
                      </ul>
                    </div>
                    <div className="feature-column">
                      <ul>
                        <li>IAT (Inter-Arrival Time)</li>
                        <li>Flag Counts</li>
                        <li>Flow Patterns</li>
                        <li>Packet Sizes</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div className="network-legend">
                  <div className="legend-item">
                    <div className="legend-indicator low"></div>
                    <span>Low Severity</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-indicator medium"></div>
                    <span>Medium Severity</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-indicator high"></div>
                    <span>High Severity</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-indicator critical"></div>
                    <span>Critical Severity</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* View Complete History Button - Moved to bottom of page outside tab content */}
        <div className="view-history-btn-container">
          <a href="/attack-history-cicids" className="view-history-btn">
            <Server size={16} /> VIEW COMPLETE CICIDS2017 ATTACK HISTORY
          </a>
        </div>

        <div className="footer-text">
          CICIDS2017 THREAT TERMINAL v1.0 • ACTIVE MONITORING • {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default CyberDetails;