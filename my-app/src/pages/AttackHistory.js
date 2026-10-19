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

const AttackHistory = () => {
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
    low: 0
  });
  
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

  // Determine attack severity based on attack type
  const getAttackSeverity = (attackType) => {
    const criticalAttacks = ["Mirai Botnet", "DDoS", "Okiru-Attack", "C&C-Mirai"];
    const highAttacks = ["Okiru", "C&C-Torii", "C&C-FileDownload", "FileDownload"];
    const mediumAttacks = ["C&C", "C&C-HeartBeat", "C&C-HeartBeat-FileDownload"];
    
    if (criticalAttacks.includes(attackType)) return "critical";
    if (highAttacks.includes(attackType)) return "high";
    if (mediumAttacks.includes(attackType)) return "medium";
    return "low";
  };

  // Fetch attack history from MongoDB via the backend API
  useEffect(() => {
    const fetchAttackHistory = async () => {
      setLoading(true);
      try {
        // Create a new endpoint in your Flask app to retrieve MongoDB data
        const res = await axios.get("http://127.0.0.1:5005/iot23_logs2", { timeout: 30000 });
        
        if (res.data && Array.isArray(res.data.logs)) {
          setAttackHistory(res.data.logs);
          setFilteredHistory(res.data.logs);
          setTotalPages(Math.ceil(res.data.logs.length / itemsPerPage));
          calculateStats(res.data.logs);
          updateChartData(res.data.logs);
        } else {
          throw new Error("Invalid data format");
        }
      } catch (err) {
        console.error("Error fetching attack logs from MongoDB:", err);
        setError("Failed to load attack history. Backend service may be unavailable. Please check server connection and try again.");
        setAttackHistory([]);
        setFilteredHistory([]);
        setTotalPages(0);
        setAttackStats({
          total: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAttackHistory();
  }, []);

  // Calculate statistics from attack data
  const calculateStats = (data) => {
    const stats = {
      total: data.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
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
    csvContent += "Timestamp,Attack Type,Severity,Duration,Protocol,Orig Bytes,Resp Bytes,Orig Packets,Resp Packets\n";
    
    // Add data rows
    filteredHistory.forEach(attack => {
      const protocol = attack.features?.proto === 6 ? "TCP" : 
                      attack.features?.proto === 17 ? "UDP" : 
                      attack.features?.proto === 1 ? "ICMP" : 
                      attack.features?.proto || "Unknown";
                      
      const row = [
        attack.timestamp,
        attack.attack,
        getAttackSeverity(attack.attack).toUpperCase(),
        attack.features?.duration || "N/A",
        protocol,
        attack.features?.orig_bytes || "N/A",
        attack.features?.resp_bytes || "N/A",
        attack.features?.orig_pkts || "N/A",
        attack.features?.resp_pkts || "N/A"
      ].join(",");
      
      csvContent += row + "\n";
    });
    
    // Create download link and trigger download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `iot_attack_history_${new Date().toISOString().slice(0,10)}.csv`);
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
    <div className="dashboard-container">
      <MatrixEffect />
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <a href="/" className="back-link">
            <ArrowLeft className="terminal-icon" />
          </a>
          <Wifi className="terminal-icon" />
          <h1 className="dashboard-title">ATTACK HISTORY DATABASE</h1>
          <Terminal className="terminal-icon" />
          <div className="alert-counter">
            <AlertTriangle className="alert-icon" />
            <span className="alert-badge">{attackStats.total}</span>
          </div>
        </div>

        {/* Security Status Banner */}
        <div className="security-status">
          <div className="status-indicator"></div>
          <span>MONGODB INTRUSION DATABASE</span>
          <div className="status-indicator"></div>
        </div>
        
        {/* Statistics Cards */}
        <div className="stats-container">
          <div className="stat-card total">
            <div className="stat-icon">
              <Shield size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.total}</h3>
              <span>Total Attacks</span>
            </div>
          </div>
          <div className="stat-card critical">
            <div className="stat-icon">
              <AlertTriangle size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.critical}</h3>
              <span>Critical</span>
            </div>
          </div>
          <div className="stat-card high">
            <div className="stat-icon">
              <Activity size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.high}</h3>
              <span>High</span>
            </div>
          </div>
          <div className="stat-card medium">
            <div className="stat-icon">
              <Lock size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.medium}</h3>
              <span>Medium</span>
            </div>
          </div>
          <div className="stat-card low">
            <div className="stat-icon">
              <Server size={24} />
            </div>
            <div className="stat-info">
              <h3>{attackStats.low}</h3>
              <span>Low</span>
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

               {/* UPDATED Results Section */}
        <div className="results-section-container">
          <div className="results-header">
            <div style={{ display: 'flex', alignItems: 'center' }}>
                <Terminal className="content-icon" />
                <h3>CICIDS2017 ATTACK LOGS</h3>
            </div>
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
                <p>ACCESSING MONGODB DATABASE...</p>
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
                      <th>ORIG BYTES</th>
                      <th>RESP BYTES</th>
                      <th>ORIG PKTS</th>
                      <th>RESP PKTS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getCurrentPageItems().map((attack, index) => (
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
                        <td>{attack.features?.orig_pkts || "N/A"}</td>
                        <td>{attack.features?.resp_pkts || "N/A"}</td>
                      </tr>
                    ))}
                    {filteredHistory.length === 0 && (
                      <tr>
                        <td colSpan="9" className="no-data">NO MATCHING RECORDS FOUND</td>
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

        <div className="footer-text">
          IOT MONITORING TERMINAL v2.8 • MONGODB DATABASE • {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default AttackHistory;