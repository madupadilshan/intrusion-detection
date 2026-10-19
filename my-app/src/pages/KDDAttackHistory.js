import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { Wifi, Shield, Terminal, AlertTriangle, Lock, Activity, Server, Download, ArrowLeft, Filter } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Dashboard.css';
import './AttackHistory.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const KDDAttackHistory = () => {
  const [attackHistory, setAttackHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("all");
  const [dateRange, setDateRange] = useState({ 
    startDate: null, 
    startTime: "00:00", 
    endDate: null, 
    endTime: "23:59" 
  });
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [attackStats, setAttackStats] = useState({
    total: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    normal: 0
  });
  
  // Animation states (adding binary hacking effect from TraditionalDetails.js)
  const [isAttackDetected, setIsAttackDetected] = useState(false);
  const [attackSeverity, setAttackSeverity] = useState("medium");
  const [popupMessage, setPopupMessage] = useState("");
  const [hackingSequence, setHackingSequence] = useState([]);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [attackDetails3D, setAttackDetails3D] = useState(null);
  
  const itemsPerPage = 50;

  // Chart.js data for Attack Distribution
  const [attackDistribution, setAttackDistribution] = useState({
    labels: [],
    datasets: [
      {
        label: "Attack Count",
        data: [],
        backgroundColor: [
          'rgba(255, 0, 0, 0.7)',
          'rgba(255, 165, 0, 0.7)',
          'rgba(255, 255, 0, 0.7)',
          'rgba(0, 0, 255, 0.7)',
          'rgba(0, 255, 0, 0.7)',
        ],
        borderWidth: 1
      },
    ],
  });

  // Chart options
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

  // Create binary sequence for hacking animation (from TraditionalDetails.js)
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

  // Determine attack severity based on attack type
  const getAttackSeverity = (attackType) => {
    // NSL-KDD attack classification
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

  // Fetch attack history from MongoDB via the backend API
  useEffect(() => {
    const fetchAttackHistory = async () => {
      setLoading(true);
      try {
        // Use the KDD endpoint
        const res = await axios.get("http://127.0.0.1:5007/kdd_logs2", { timeout: 10000 });
        
        if (res.data && Array.isArray(res.data.logs)) {
          setAttackHistory(res.data.logs);
          setFilteredHistory(res.data.logs);
          setTotalPages(Math.ceil(res.data.logs.length / itemsPerPage));
          calculateStats(res.data.logs);
          updateChartData(res.data.logs);
          
          // Randomly trigger an attack alert for demonstration (if there are non-normal traffic entries)
          const attacks = res.data.logs.filter(attack => 
            attack.attack !== "Normal" && attack.attack !== "Benign"
          );
          
          if (attacks.length > 0 && Math.random() > 0.7) {
            const randomAttack = attacks[Math.floor(Math.random() * attacks.length)];
            triggerAttackAlert(randomAttack.attack, randomAttack);
          }
        } else {
          throw new Error("Invalid data format");
        }
      } catch (err) {
        console.error("Error fetching KDD attack logs from MongoDB:", err);
        setError("Failed to load KDD attack history. Backend service may be unavailable. Please check server connection and try again.");
        
        // Sample data for preview if API fails
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
              dst_bytes: 1024
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
              dst_bytes: 512
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
              dst_bytes: 1024
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
              dst_bytes: 768
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
              dst_bytes: 512
            }
          }
        ];
        
        setAttackHistory(sampleData);
        setFilteredHistory(sampleData);
        setTotalPages(Math.ceil(sampleData.length / itemsPerPage));
        calculateStats(sampleData);
        updateChartData(sampleData);
      } finally {
        setLoading(false);
      }
    };

    fetchAttackHistory();
    
    // Refresh data every 30 seconds
    const intervalId = setInterval(fetchAttackHistory, 30000);
    
    return () => clearInterval(intervalId);
  }, []);

  // Calculate statistics from attack data
  const calculateStats = (data) => {
    const stats = {
      total: data.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      normal: 0
    };
    
    data.forEach(attack => {
      const severity = getAttackSeverity(attack.attack);
      stats[severity]++;
    });
    
    setAttackStats(stats);
  };

  // Update chart data with attack distribution
  const updateChartData = (data) => {
    // Count attack types
    const attackCounts = {};
    data.forEach(attack => {
      if (!attackCounts[attack.attack]) {
        attackCounts[attack.attack] = 0;
      }
      attackCounts[attack.attack]++;
    });
    
    // Sort by count (descending)
    const sortedAttacks = Object.entries(attackCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5); // Top 5 attack types
    
    setAttackDistribution({
      labels: sortedAttacks.map(item => item[0]),
      datasets: [
        {
          label: "Attack Count",
          data: sortedAttacks.map(item => item[1]),
          backgroundColor: [
            'rgba(255, 0, 0, 0.7)',
            'rgba(255, 165, 0, 0.7)',
            'rgba(255, 255, 0, 0.7)',
            'rgba(0, 0, 255, 0.7)',
            'rgba(0, 255, 0, 0.7)',
          ],
          borderWidth: 1
        },
      ],
    });
  };

  // Filter attacks by type and date/time range
  const applyFilters = () => {
    let filtered = [...attackHistory];
    
    // Filter by attack type
    if (filterType !== "all") {
      filtered = filtered.filter(attack => attack.attack === filterType);
    }
    
    // Filter by date and time range
    if (dateRange.startDate && dateRange.endDate) {
      const startDateTime = new Date(`${dateRange.startDate}T${dateRange.startTime}:00`).getTime();
      const endDateTime = new Date(`${dateRange.endDate}T${dateRange.endTime}:00`).getTime();
      
      filtered = filtered.filter(attack => {
        const attackDate = new Date(attack.timestamp).getTime();
        return attackDate >= startDateTime && attackDate <= endDateTime;
      });
    }
    
    setFilteredHistory(filtered);
    setTotalPages(Math.ceil(filtered.length / itemsPerPage));
    setPage(1); // Reset to first page after filtering
    calculateStats(filtered);
    updateChartData(filtered);
  };

  // Reset filters
  const resetFilters = () => {
    setFilterType("all");
    setDateRange({ 
      startDate: null, 
      startTime: "00:00", 
      endDate: null, 
      endTime: "23:59" 
    });
    setFilteredHistory(attackHistory);
    setTotalPages(Math.ceil(attackHistory.length / itemsPerPage));
    setPage(1);
    calculateStats(attackHistory);
    updateChartData(attackHistory);
  };

  // Export data as CSV
  const exportToCSV = () => {
    if (filteredHistory.length === 0) {
      alert("No data to export");
      return;
    }
    
    // Create CSV content
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // Add headers
    csvContent += "Timestamp,Attack Type,Severity,Duration,Protocol,Src Bytes,Dst Bytes\n";
    
    // Add data rows
    filteredHistory.forEach(attack => {
      const protocol = attack.features?.protocol === 6 ? "TCP" : 
                      attack.features?.protocol === 17 ? "UDP" : 
                      attack.features?.protocol === 1 ? "ICMP" : 
                      attack.features?.protocol || "Unknown";
                      
      const row = [
        attack.timestamp,
        attack.attack,
        getAttackSeverity(attack.attack).toUpperCase(),
        attack.features?.duration || "N/A",
        protocol,
        attack.features?.src_bytes || "N/A",
        attack.features?.dst_bytes || "N/A"
      ].join(",");
      
      csvContent += row + "\n";
    });
    
    // Create download link and trigger download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `kdd_attack_history_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Get unique attack types for filter dropdown
  const getAttackTypes = () => {
    const types = new Set();
    attackHistory.forEach(attack => {
      types.add(attack.attack);
    });
    return ["all", ...Array.from(types)];
  };

  // Get current page items
  const getCurrentPageItems = () => {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredHistory.slice(startIndex, endIndex);
  };

  // Format time for UI
  const formatTime = (timeStr) => {
    return timeStr || "";
  };

  return (
    <div className={`dashboard-container ${isAttackDetected ? `attack-detected attack-${attackSeverity}` : ""}`}>
      <MatrixEffect />
      
      {/* Binary Overlay (only visible during attack) */}
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
          <a href="/" className="back-link">
            <ArrowLeft className="terminal-icon" />
          </a>
          <Wifi className="terminal-icon" />
          <h1 className="dashboard-title">NSL-KDD ATTACK DATABASE</h1>
          <Terminal className="terminal-icon" />
          <div className="alert-counter">
            <AlertTriangle className="alert-icon" />
            <span className="alert-badge">{attackStats.total - attackStats.normal}</span>
          </div>
        </div>

        {/* Security Status Banner */}
        <div className={`security-status ${isAttackDetected ? 'under-attack' : ''}`}>
          <div className="status-indicator"></div>
          <span>{isAttackDetected ? `⚠️ SYSTEM ALERT: ${popupMessage}` : "NSL-KDD INTRUSION DATABASE"}</span>
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
        
        {/* Statistics Cards */}
        <div className="stats-container">
          <div className="stat-card total">
            <div className="stat-icon">
              <Shield size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.total}</h3>
              <span>Total Records</span>
            </div>
          </div>
          <div className="stat-card critical">
            <div className="stat-icon">
              <AlertTriangle size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.critical}</h3>
              <span>DoS Attacks</span>
            </div>
          </div>
          <div className="stat-card high">
            <div className="stat-icon">
              <Activity size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.high}</h3>
              <span>R2L/U2R</span>
            </div>
          </div>
          <div className="stat-card medium">
            <div className="stat-icon">
              <Lock size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.medium}</h3>
              <span>Probe</span>
            </div>
          </div>
          <div className="stat-card normal">
            <div className="stat-icon">
              <Server size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.normal}</h3>
              <span>Normal</span>
            </div>
          </div>
        </div>

        {/* Charts and Filters Row */}
        <div className="data-row">
          <div className="chart-panel">
            <div className="panel-header">
              <Activity className="panel-icon" />
              <h3>ATTACK DISTRIBUTION</h3>
            </div>
            <div className="panel-body">
              <div className="chart-container">
                {attackHistory.length > 0 ? (
                  <Line data={attackDistribution} options={chartOptions} height={200} />
                ) : (
                  <div className="no-data-chart">NO DATA AVAILABLE</div>
                )}
              </div>
            </div>
          </div>
          
          <div className="filters-panel">
            <div className="panel-header">
              <Filter className="panel-icon" />
              <h3>FILTER ATTACKS</h3>
              <button className="toggle-filters-btn" onClick={() => setShowFilters(!showFilters)}>
                {showFilters ? "HIDE" : "SHOW"}
              </button>
            </div>
            {showFilters && (
              <div className="panel-body filters-body">
                <div className="filter-group">
                  <label>Attack Type:</label>
                  <select 
                    value={filterType} 
                    onChange={(e) => setFilterType(e.target.value)}
                    className="filter-select"
                    disabled={attackHistory.length === 0}
                  >
                    {getAttackTypes().map((type, index) => (
                      <option key={index} value={type}>
                        {type === "all" ? "All Types" : type}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>Date & Time Range:</label>
                  <div className="datetime-inputs">
                    <div className="datetime-row">
                      <input 
                        type="date" 
                        value={dateRange.startDate || ''} 
                        onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
                        className="date-input"
                        disabled={attackHistory.length === 0}
                      />
                      <input 
                        type="time" 
                        value={formatTime(dateRange.startTime)} 
                        onChange={(e) => setDateRange({...dateRange, startTime: e.target.value})}
                        className="time-input"
                        disabled={attackHistory.length === 0}
                      />
                    </div>
                    <span className="to-text">to</span>
                    <div className="datetime-row">
                      <input 
                        type="date" 
                        value={dateRange.endDate || ''} 
                        onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
                        className="date-input"
                        disabled={attackHistory.length === 0}
                      />
                      <input 
                        type="time" 
                        value={formatTime(dateRange.endTime)} 
                        onChange={(e) => setDateRange({...dateRange, endTime: e.target.value})}
                        className="time-input"
                        disabled={attackHistory.length === 0}
                      />
                    </div>
                  </div>
                </div>
                
                <div className="filter-actions">
                  <button 
                    className="filter-btn apply" 
                    onClick={applyFilters}
                    disabled={attackHistory.length === 0}
                  >
                    APPLY FILTERS
                  </button>
                  <button 
                    className="filter-btn reset" 
                    onClick={resetFilters}
                    disabled={attackHistory.length === 0}
                  >
                    RESET
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        <div className="content-container attack-history-table">
          <div className="content-header">
            <Terminal className="content-icon" />
            <h3>NSL-KDD INTRUSION LOGS</h3>
            <div className="header-actions">
              <button 
                className="action-btn export-btn" 
                onClick={exportToCSV}
                disabled={filteredHistory.length === 0}
              >
                <Download size={16} /> EXPORT CSV
              </button>
            </div>
          </div>
          
          <div className="content-body">
            {loading ? (
              <div className="loading-container">
                <div className="loading-indicator"></div>
                <p>ACCESSING DATABASE...</p>
              </div>
            ) : error ? (
              <div className="error-container">
                <AlertTriangle size={24} />
                <p>{error}</p>
              </div>
            ) : (
              <>
                <table className="attack-table history-table">
                  <thead>
                    <tr>
                      <th>TIMESTAMP</th>
                      <th>ATTACK VECTOR</th>
                      <th>THREAT LEVEL</th>
                      <th>DURATION</th>
                      <th>PROTOCOL</th>
                      <th>SRC BYTES</th>
                      <th>DST BYTES</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getCurrentPageItems().map((attack, index) => (
                      <tr key={index} className={`severity-${getAttackSeverity(attack.attack)}`}>
                        <td>{attack.timestamp}</td>
                        <td>{getDisplayAttackName(attack.attack)}</td>
                        <td>{getAttackSeverity(attack.attack).toUpperCase()}</td>
                        <td>{attack.features?.duration || "N/A"}</td>
                        <td>{
                          attack.features?.protocol === 6 ? "TCP" : 
                          attack.features?.protocol === 17 ? "UDP" : 
                          attack.features?.protocol === 1 ? "ICMP" : 
                          attack.features?.protocol || "N/A"
                        }</td>
                        <td>{attack.features?.src_bytes || "N/A"}</td>
                        <td>{attack.features?.dst_bytes || "N/A"}</td>
                      </tr>
                    ))}
                    {filteredHistory.length === 0 && (
                      <tr>
                        <td colSpan="7" className="no-data">NO MATCHING RECORDS FOUND</td>
                      </tr>
                    )}
                  </tbody>
                </table>
                
                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="pagination-controls">
                    <button 
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="page-btn"
                    >
                      PREVIOUS
                    </button>
                    <span className="page-info">PAGE {page} OF {totalPages}</span>
                    <button 
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                      className="page-btn"
                    >
                      NEXT
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div className="attack-type-info">
          <h4>NSL-KDD ATTACK CLASSIFICATIONS</h4>
          <ul>
            <li><span className="attack-type severity-critical">DoS (Denial of Service):</span> Attacks that attempt to make network resources unavailable to intended users</li>
            <li><span className="attack-type severity-high">R2L (Remote to Local):</span> Unauthorized access from a remote machine</li>
            <li><span className="attack-type severity-high">U2R (User to Root):</span> Unauthorized access to local superuser privileges</li>
            <li><span className="attack-type severity-medium">Probe:</span> Surveillance and other probing attacks</li>
            <li><span className="attack-type severity-normal">Normal:</span> Standard network traffic</li>
          </ul>
        </div>

        <div className="footer-text">
          NSL-KDD MONITORING TERMINAL v2.1 • MONGODB DATABASE • {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default KDDAttackHistory;