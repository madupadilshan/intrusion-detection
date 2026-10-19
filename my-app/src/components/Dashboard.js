import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Shield, Wifi, Network, Bug, AlertTriangle, Terminal, X } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Dashboard.css';

const Dashboard = () => {
  const [iotAttack, setIotAttack] = useState("Scanning network...");
  const [cyberAttack, setCyberAttack] = useState("Analyzing traffic...");
  const [traditionalAttack, setTraditionalAttack] = useState("Processing data...");
  const [selectedCategory, setSelectedCategory] = useState("iot");
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  
  // States for managing alerts/popups
  const [alertVisible, setAlertVisible] = useState(false);
  const [alertType, setAlertType] = useState("");
  const [alertMessage, setAlertMessage] = useState("");
  const [alertSeverity, setAlertSeverity] = useState("medium");
  const [alertTimestamp, setAlertTimestamp] = useState("");

  // Define normal traffic patterns to be excluded from alerts
  const normalTrafficPatterns = [
    "Scanning network...", 
    "Analyzing traffic...", 
    "Processing data...", 
    "Normal Traffic", 
    "Benign",
    "No threats detected",
    "Normal",
    "BENIGN"
  ];

  // List of actual attack patterns that should trigger alerts
  const attackPatterns = {
    iot: ["Mirai", "DDoS", "Okiru", "Torii", "HeartBeat", "FileDownload", "Botnet", "Exploit"],
    cyber: ["DoS", "DDoS", "PortScan", "Brute Force", "Web Attack", "Infiltration", "Botnet", "Heartbleed"],
    traditional: ["DoS", "DDoS", "R2L", "U2R", "Probe", "Brute Force"]
  };

  // Calculate attack severity based on content
  const getAttackSeverity = (attackString, type) => {
    if (!attackString) return "normal";
    
    const attackLower = attackString.toLowerCase();
    
    // Check if this is actually normal traffic
    if (normalTrafficPatterns.some(pattern => 
      attackLower.includes(pattern.toLowerCase()))) {
      return "normal";
    }

    // Critical attacks
    const criticalKeywords = {
      iot: ["mirai", "ddos", "okiru-attack"],
      cyber: ["dos hulk", "ddos", "heartbleed"],
      traditional: ["dos", "ddos"]
    };
    
    // High severity attacks
    const highKeywords = {
      iot: ["torii", "filedownload", "botnet"],
      cyber: ["goldeneye", "web attack", "infiltration", "botnet"],
      traditional: ["r2l", "u2r"]
    };
    
    // Medium severity attacks
    const mediumKeywords = {
      iot: ["heartbeat", "exploit"],
      cyber: ["slowloris", "portscan", "brute force"],
      traditional: ["probe"]
    };

    if (criticalKeywords[type].some(keyword => attackLower.includes(keyword))) {
      return "critical";
    } else if (highKeywords[type].some(keyword => attackLower.includes(keyword))) {
      return "high";
    } else if (mediumKeywords[type].some(keyword => attackLower.includes(keyword))) {
      return "medium";
    }
    
    // If it's not normal traffic but we don't recognize it, treat as low severity
    return normalTrafficPatterns.some(pattern => 
      attackLower.includes(pattern.toLowerCase())) ? "normal" : "low";
  };

  const shouldShowAlert = (attackString, type) => {
    if (!attackString || normalTrafficPatterns.some(pattern => 
      attackString.toLowerCase().includes(pattern.toLowerCase()))) {
      return false;
    }
    
    // Only show alert if it matches known attack patterns for this type
    return attackPatterns[type].some(pattern => 
      attackString.toLowerCase().includes(pattern.toLowerCase()));
  };

  useEffect(() => {
    const fetchAttackData = async () => {
      setIsLoading(true);
      
      try {
        // Fetch IoT attacks
        const iotRes = await axios.get("http://127.0.0.1:5005/latest_iot_attack", { timeout: 5000 });
        const iotAttackData = iotRes.data.attack;
        setIotAttack(iotAttackData);
        
        if (shouldShowAlert(iotAttackData, "iot")) {
          const severity = getAttackSeverity(iotAttackData, "iot");
          setAlertType("iot");
          setAlertMessage(iotAttackData);
          setAlertSeverity(severity);
          setAlertTimestamp(new Date().toLocaleTimeString());
          setAlertVisible(true);
        }
      } catch (error) {
        const errorMsg = "ALERT: IoT security breach detected. Connection compromised.";
        setIotAttack(errorMsg);
        setAlertType("iot");
        setAlertMessage(errorMsg);
        setAlertSeverity("critical");
        setAlertTimestamp(new Date().toLocaleTimeString());
        setAlertVisible(true);
      }

      try {
        // Fetch Cyber attacks (CICIDS)
        const cyberRes = await axios.get("http://127.0.0.1:5006/latest_cicids_attack", { timeout: 5000 });
        const cyberAttackData = cyberRes.data.attack;
        setCyberAttack(cyberAttackData);
        
        if (!alertVisible && shouldShowAlert(cyberAttackData, "cyber")) {
          const severity = getAttackSeverity(cyberAttackData, "cyber");
          setAlertType("cyber");
          setAlertMessage(cyberAttackData);
          setAlertSeverity(severity);
          setAlertTimestamp(new Date().toLocaleTimeString());
          setAlertVisible(true);
        }
      } catch (error) {
        const errorMsg = "WARNING: Cyber attack vectors identified. Implementing countermeasures.";
        setCyberAttack(errorMsg);
        
        if (!alertVisible) {
          setAlertType("cyber");
          setAlertMessage(errorMsg);
          setAlertSeverity("high");
          setAlertTimestamp(new Date().toLocaleTimeString());
          setAlertVisible(true);
        }
      }

      try {
        // Fetch Traditional attacks (NSL-KDD)
        const traditionalRes = await axios.get("http://127.0.0.1:5007/latest_kdd_attack", { timeout: 5000 });
        const traditionalAttackData = traditionalRes.data.attack;
        setTraditionalAttack(traditionalAttackData);
        
        if (!alertVisible && shouldShowAlert(traditionalAttackData, "traditional")) {
          const severity = getAttackSeverity(traditionalAttackData, "traditional");
          setAlertType("traditional");
          setAlertMessage(traditionalAttackData);
          setAlertSeverity(severity);
          setAlertTimestamp(new Date().toLocaleTimeString());
          setAlertVisible(true);
        }
      } catch (error) {
        const errorMsg = "CAUTION: Traditional attack signature detected. Firewall engaged.";
        setTraditionalAttack(errorMsg);
        
        if (!alertVisible) {
          setAlertType("traditional");
          setAlertMessage(errorMsg);
          setAlertSeverity("medium");
          setAlertTimestamp(new Date().toLocaleTimeString());
          setAlertVisible(true);
        }
      }
      
      setIsLoading(false);
    };

    fetchAttackData();
    const interval = setInterval(fetchAttackData, 5000);

    return () => clearInterval(interval);
  }, [alertVisible]);

  // Close alert popup
  const closeAlert = () => {
    setAlertVisible(false);
  };

  // Handle category click
  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
    if (category === "iot") navigate("/IOTDetails");
    if (category === "cyber") navigate("/CyberDetails");
    if (category === "traditional") navigate("/TraditionalDetails");
  };

  // Get appropriate icon for alert type
  const getAlertIcon = () => {
    switch (alertType) {
      case "iot":
        return <Wifi className="alert-icon" />;
      case "cyber":
        return <Bug className="alert-icon" />;
      case "traditional":
        return <Shield className="alert-icon" />;
      default:
        return <AlertTriangle className="alert-icon" />;
    }
  };

  // Get appropriate title for alert type
  const getAlertTitle = () => {
    switch (alertType) {
      case "iot":
        return "IOT THREAT DETECTED";
      case "cyber":
        return "CYBER THREAT DETECTED";
      case "traditional":
        return "NETWORK THREAT DETECTED";
      default:
        return "SECURITY ALERT";
    }
  };

  // Auto-close alert based on severity
  useEffect(() => {
    if (alertVisible) {
      let timeoutDuration;
      
      switch (alertSeverity) {
        case "critical":
          timeoutDuration = 10000; // 10 seconds for critical
          break;
        case "high":
          timeoutDuration = 8000; // 8 seconds for high
          break;
        case "medium":
          timeoutDuration = 6000; // 6 seconds for medium
          break;
        default:
          timeoutDuration = 5000; // 5 seconds for low
      }
      
      const timer = setTimeout(() => {
        closeAlert();
      }, timeoutDuration);
      
      return () => clearTimeout(timer);
    }
  }, [alertVisible, alertSeverity]);

  return (
    <div className="dashboard-container">
      <MatrixEffect />
      
      {/* Alert Popup - Only shown for actual attacks */}
      {alertVisible && (
        <div className={`alert-popup ${alertType} severity-${alertSeverity}`}>
          <div className="alert-header">
            {getAlertIcon()}
            <div className="alert-title-container">
              <h3>{getAlertTitle()}</h3>
              <span className="alert-timestamp">{alertTimestamp}</span>
            </div>
            <button className="close-btn" onClick={closeAlert}>
              <X size={18} />
            </button>
          </div>
          <div className="alert-body">
            <p>{alertMessage}</p>
          </div>
          <div className="alert-footer">
            <button 
              className="details-btn" 
              onClick={() => {
                handleCategoryClick(alertType);
                closeAlert();
              }}
            >
              VIEW DETAILS
            </button>
            <button className="dismiss-btn" onClick={closeAlert}>
              DISMISS
            </button>
          </div>
        </div>
      )}
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <Terminal className="terminal-icon" />
          <h1 className="dashboard-title">INTRUSION DETECTION SYSTEM</h1>
          <Terminal className="terminal-icon" />
        </div>

        {/* Security Status Banner */}
        <div className={`security-status ${alertVisible ? `alert-active severity-${alertSeverity}` : ''}`}>
          <div className="status-indicator"></div>
          <span>
            {alertVisible 
              ? `⚠️ ALERT: ${alertMessage.substring(0, 50)}${alertMessage.length > 50 ? '...' : ''}`
              : "SYSTEM OPERATIONAL"}
          </span>
          <div className="status-indicator"></div>
        </div>

        {/* Tabs Section */}
        <div className="tabs-container">
          <div 
            className={`tab ${selectedCategory === "iot" ? "active" : ""}`} 
            onClick={() => setSelectedCategory("iot")}
          >
            <Wifi className="tab-icon" />
            <span>IOT THREATS</span>
          </div>
          <div 
            className={`tab ${selectedCategory === "cyber" ? "active" : ""}`} 
            onClick={() => setSelectedCategory("cyber")}
          >
            <Bug className="tab-icon" />
            <span>CYBER THREATS</span>
          </div>
          <div 
            className={`tab ${selectedCategory === "traditional" ? "active" : ""}`} 
            onClick={() => setSelectedCategory("traditional")}
          >
            <Shield className="tab-icon" />
            <span>NETWORK THREATS</span>
          </div>
        </div>

        {/* Content Section */}
        <div className="content-container">
          <div className="content-header">
            {selectedCategory === "iot" && (
              <>
                <Wifi className="content-icon" />
                <h3>IOT THREAT ANALYSIS</h3>
              </>
            )}
            {selectedCategory === "cyber" && (
              <>
                <Bug className="content-icon" />
                <h3>CYBER THREAT ANALYSIS</h3>
              </>
            )}
            {selectedCategory === "traditional" && (
              <>
                <Shield className="content-icon" />
                <h3>NETWORK THREAT ANALYSIS</h3>
              </>
            )}
          </div>
          
          <div className="content-body">
            {selectedCategory === "iot" && (
              <div className="threat-data">
                <div className="threat-details">
                  {isLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <span>ANALYZING IOT NETWORK...</span>
                    </div>
                  ) : (
                    <pre className={!normalTrafficPatterns.includes(iotAttack) ? `severity-${getAttackSeverity(iotAttack, "iot")}` : ''}>
                      {iotAttack}
                    </pre>
                  )}
                </div>
              </div>
            )}
            
            {selectedCategory === "cyber" && (
              <div className="threat-data">
                <div className="threat-details">
                  {isLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <span>PROCESSING CYBER THREATS...</span>
                    </div>
                  ) : (
                    <pre className={!normalTrafficPatterns.includes(cyberAttack) ? `severity-${getAttackSeverity(cyberAttack, "cyber")}` : ''}>
                      {cyberAttack}
                    </pre>
                  )}
                </div>
              </div>
            )}
            
            {selectedCategory === "traditional" && (
              <div className="threat-data">
                <div className="threat-details">
                  {isLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <span>SCANNING TRADITIONAL VECTORS...</span>
                    </div>
                  ) : (
                    <pre className={!normalTrafficPatterns.includes(traditionalAttack) ? `severity-${getAttackSeverity(traditionalAttack, "traditional")}` : ''}>
                      {traditionalAttack}
                    </pre>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Attack Cards Section */}
        <div className="attack-cards">
          {/* IoT-Based Attacks */}
          <div
            className={`attack-card ${selectedCategory === "iot" ? "active-card" : ""} ${
              !normalTrafficPatterns.includes(iotAttack) ? `alert-card severity-${getAttackSeverity(iotAttack, "iot")}` : ''
            }`}
            onClick={() => handleCategoryClick("iot")}
          >
            <div className="card-icon-container">
              <Wifi size={32} className="card-icon" />
            </div>
            <h4>IOT INTRUSIONS</h4>
            <div className="card-status">
              <div className={`status-bar ${!normalTrafficPatterns.includes(iotAttack) ? 'active' : ''}`}></div>
            </div>
            <p className="card-description">{isLoading ? "Analyzing..." : iotAttack}</p>
          </div>

          {/* Cyber Attacks */}
          <div
            className={`attack-card ${selectedCategory === "cyber" ? "active-card" : ""} ${
              !normalTrafficPatterns.includes(cyberAttack) ? `alert-card severity-${getAttackSeverity(cyberAttack, "cyber")}` : ''
            }`}
            onClick={() => handleCategoryClick("cyber")}
          >
            <div className="card-icon-container">
              <Bug size={32} className="card-icon" />
            </div>
            <h4>CYBER THREATS</h4>
            <div className="card-status">
              <div className={`status-bar ${!normalTrafficPatterns.includes(cyberAttack) ? 'active' : ''}`}></div>
            </div>
            <p className="card-description">{isLoading ? "Processing..." : cyberAttack}</p>
          </div>

          {/* Traditional Attacks */}
          <div
            className={`attack-card ${selectedCategory === "traditional" ? "active-card" : ""} ${
              !normalTrafficPatterns.includes(traditionalAttack) ? `alert-card severity-${getAttackSeverity(traditionalAttack, "traditional")}` : ''
            }`}
            onClick={() => handleCategoryClick("traditional")}
          >
            <div className="card-icon-container">
              <Shield size={32} className="card-icon" />
            </div>
            <h4>NETWORK VECTORS</h4>
            <div className="card-status">
              <div className={`status-bar ${!normalTrafficPatterns.includes(traditionalAttack) ? 'active' : ''}`}></div>
            </div>
            <p className="card-description">{isLoading ? "Scanning..." : traditionalAttack}</p>
          </div>
        </div>
        
        <div className="footer-text">
          INTRUSION DETECTION TERMINAL v3.1 • ACTIVE MONITORING
        </div>
      </div>
    </div>
  );
};

export default Dashboard;