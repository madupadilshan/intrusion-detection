import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { 
  Shield, 
  Wifi, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Search, 
  Eye, 
  Activity,
  Zap,
  Globe,
  Router,
  Camera,
  Printer,
  Tv,
  Speaker,
  Thermometer,
  Lock,
  Cpu,
  RefreshCw,
  Filter,
  X,
  ArrowUpDown
} from 'lucide-react';
import './IoTDevicesDashboard.css';

// Constants
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5012/api',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
};

const DEVICE_TYPES = Object.freeze({
  camera: { icon: Camera, label: 'IP Camera', priority: 1 },
  router: { icon: Router, label: 'Router/Gateway', priority: 2 },
  printer: { icon: Printer, label: 'Network Printer', priority: 3 },
  smart_tv: { icon: Tv, label: 'Smart TV', priority: 4 },
  speaker: { icon: Speaker, label: 'Smart Speaker', priority: 5 },
  thermostat: { icon: Thermometer, label: 'Smart Thermostat', priority: 6 },
  lock: { icon: Lock, label: 'Smart Lock', priority: 7 },
  sensor: { icon: Cpu, label: 'IoT Sensor', priority: 8 },
  unknown: { icon: Globe, label: 'Unknown Device', priority: 99 }
});

const SEVERITY_CONFIG = Object.freeze({
  danger: { label: 'Critical', threshold: 3 },
  warning: { label: 'Warning', threshold: 1 },
  safe: { label: 'Safe', threshold: 0 }
});

const SCAN_CONFIG = {
  PROGRESS_INTERVAL: 1000,
  DEFAULT_NETWORK: '192.168.8.0/24', // As seen in your DB screenshot
  TIMEOUT: 300000 // 5 minutes
};

// Custom Hooks
const useAPI = () => {
  const abortControllerRef = useRef(null);

  const makeRequest = useCallback(async (endpoint, options = {}) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      signal: abortControllerRef.current.signal,
      ...options
    };

    let attempts = 0;
    while (attempts < API_CONFIG.RETRY_ATTEMPTS) {
      try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, config);
        
        if (!response.ok) {
          const errorBody = await response.text();
          throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorBody}`);
        }

        const data = await response.json();
        return { success: true, data };
      } catch (error) {
        attempts++;
        if (error.name === 'AbortError') {
          return { success: false, error: 'Request cancelled' };
        }
        if (attempts >= API_CONFIG.RETRY_ATTEMPTS) {
          return { success: false, error: error.message };
        }
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000));
      }
    }
  }, []);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { makeRequest };
};

// MODIFIED HOOK to fetch from /api/scan-results
const useDeviceManager = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { makeRequest } = useAPI();

  const fetchDevices = useCallback(async () => {
    setLoading(true);
    setError(null);

    // Fetch from the new endpoint that returns devices from the latest scan
    const result = await makeRequest('/scan-results');
    
    if (result.success) {
      // The new endpoint directly returns the array of devices
      setDevices(result.data || []);
      setLastUpdate(new Date());
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  }, [makeRequest]);

  const stats = useMemo(() => {
    const total = devices.length;
    // Assuming status might not be present, default to offline
    const online = devices.filter(d => d.status === 'Online').length;
    const offline = total - online;
    const vulnerable = devices.filter(d => d.severity === 'danger').length;
    
    return { total, online, offline, vulnerable };
  }, [devices]);

  return { 
    devices, 
    loading, 
    error, 
    stats, 
    lastUpdate,
    fetchDevices 
  };
};

const useNetworkScanner = (onScanComplete) => {
  const [scanState, setScanState] = useState({
    isScanning: false,
    progress: 0,
    error: null,
    startTime: null
  });
  
  const { makeRequest } = useAPI();
  const progressIntervalRef = useRef(null);

  const startScan = useCallback(async (networkRange) => {
    if (!networkRange?.trim()) {
      setScanState(prev => ({ ...prev, error: 'Network range is required' }));
      return;
    }

    setScanState({
      isScanning: true,
      progress: 0,
      error: null,
      startTime: Date.now()
    });

    const result = await makeRequest('/scan', {
      method: 'POST',
      body: JSON.stringify({ network_range: networkRange.trim() })
    });

    if (!result.success) {
      setScanState(prev => ({
        ...prev,
        isScanning: false,
        error: result.error
      }));
    }
  }, [makeRequest]);

  const checkProgress = useCallback(async () => {
    const result = await makeRequest('/scan/progress');
    
    if (result.success) {
      // CORRECTED SYNTAX: Removed the stray dot from the destructuring assignment
      const { progress = 0, scanning = false } = result.data;
      
      setScanState(prev => ({
        ...prev,
        progress,
        isScanning: scanning,
        // If scan just finished, call the callback
        ...(prev.isScanning && !scanning && { progress: 100 })
      }));
      
      // When scanning stops, trigger the onScanComplete callback
      if (!scanning && progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
        onScanComplete?.();
      }

    } else {
      setScanState(prev => ({
        ...prev,
        isScanning: false,
        error: 'Failed to check scan progress'
      }));
    }
  }, [makeRequest, onScanComplete]);

  useEffect(() => {
    if (scanState.isScanning && !progressIntervalRef.current) {
      progressIntervalRef.current = setInterval(checkProgress, SCAN_CONFIG.PROGRESS_INTERVAL);
      
      const timeout = setTimeout(() => {
        if(progressIntervalRef.current) {
            setScanState(prev => ({
              ...prev,
              isScanning: false,
              error: 'Scan timeout - operation took too long'
            }));
        }
      }, SCAN_CONFIG.TIMEOUT);

      return () => {
        clearTimeout(timeout);
      };
    } else if (!scanState.isScanning && progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
    }
  }, [scanState.isScanning, checkProgress]);

  return {
    ...scanState,
    startScan,
    resetError: () => setScanState(prev => ({ ...prev, error: null }))
  };
};

// --- Components (No changes needed below this line) ---

const MatrixBackground = React.memo(() => {
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = new Array(columns).fill(1);

    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#0f0';
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(char, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }

      animationFrameRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return <canvas ref={canvasRef} className="matrix-background" aria-hidden="true" />;
});

const StatCard = React.memo(({ title, value, icon: Icon, className, isLoading }) => (
  <div className={`stat-card ${className} ${isLoading ? 'loading' : ''}`}>
    <div className="stat-content">
      <div className="stat-info">
        <p className="stat-title">{title}</p>
        <span className="stat-value" aria-live="polite">
          {isLoading ? '...' : value}
        </span>
      </div>
      <Icon className="stat-icon" aria-hidden="true" />
    </div>
  </div>
));

const ScanControls = React.memo(({ 
  networkRange, 
  onNetworkRangeChange, 
  onStartScan, 
  isScanning, 
  progress, 
  error,
  onResetError 
}) => (
  <div className="scan-controls">
    <div className="scan-header">
      <h2 className="scan-title">
        <Search className="scan-icon" aria-hidden="true" />
        Network Scanner
      </h2>
      <div className="scan-status">
        <Zap className="status-icon" aria-hidden="true" />
        <span>Real-time Detection</span>
      </div>
    </div>
    
    <div className="scan-input-group">
      <input
        type="text"
        value={networkRange}
        onChange={(e) => onNetworkRangeChange(e.target.value)}
        placeholder="Network Range (e.g., 192.168.1.0/24)"
        className="scan-input"
        disabled={isScanning}
        aria-label="Network range to scan"
      />
      
      <button
        onClick={() => onStartScan(networkRange)}
        disabled={isScanning || !networkRange.trim()}
        className={`scan-button ${isScanning ? 'scanning' : ''}`}
        aria-describedby={error ? 'scan-error' : undefined}
      >
        {isScanning ? (
          <>
            <div className="scan-spinner" aria-hidden="true" />
            <span>Scanning...</span>
          </>
        ) : (
          <>
            <Search className="button-icon" aria-hidden="true" />
            <span>Start Scan</span>
          </>
        )}
      </button>
    </div>

    {error && (
      <div id="scan-error" className="scan-error" role="alert">
        <AlertTriangle className="error-icon" aria-hidden="true" />
        <span>{error}</span>
        <button onClick={onResetError} className="error-close" aria-label="Dismiss error">
          <X size={16} />
        </button>
      </div>
    )}

    {isScanning && (
      <div className="scan-progress">
        <div className="progress-header">
          <span className="progress-label">Scanning Progress</span>
          <span className="progress-value" aria-live="polite">{progress}%</span>
        </div>
        <div className="progress-bar" role="progressbar" aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
    )}
  </div>
));

const DeviceCard = React.memo(({ device, onViewDetails }) => {
  const deviceType = DEVICE_TYPES[device.type] || DEVICE_TYPES.unknown;
  const IconComponent = deviceType.icon;
  const severityClass = `severity-${device.severity}`;
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onViewDetails(device);
    }
  };

  return (
    <article 
      className={`device-card ${severityClass} ${device.status === 'Online' ? 'online' : 'offline'}`}
      tabIndex="0"
      role="button"
      onClick={() => onViewDetails(device)}
      onKeyPress={handleKeyPress}
      aria-label={`${device.name} - ${device.status} - ${device.severity} security level`}
    >
      <div className="device-header">
        <div className="device-info">
          <IconComponent className="device-type-icon" aria-hidden="true" />
          <div className="device-details">
            <h3 className="device-name">{device.name}</h3>
            <p className="device-ip">{device.ip}</p>
          </div>
        </div>
        <div className={`device-status ${device.status?.toLowerCase()}`}>
          <div className="status-indicator" aria-hidden="true" />
          <span className="status-text">{device.status}</span>
        </div>
      </div>
      
      <div className="device-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Type:</span>
          <span className="metadata-value">{deviceType.label}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Vulns:</span>
          <span className="metadata-value vulnerability-count">{device.vulnerabilities}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Ports:</span>
          <span className="metadata-value">{device.open_ports?.length || 0}</span>
        </div>
      </div>
      
      <div className="device-footer">
        <div className="threat-level" aria-label={`Threat level: ${device.vulnerabilities} out of 5`}>
          {[1, 2, 3, 4, 5].map((level) => (
            <div
              key={level}
              className={`threat-indicator ${level <= (device.vulnerabilities || 0) ? 'active' : ''}`}
              aria-hidden="true"
            />
          ))}
        </div>
        <span className={`severity-badge ${severityClass}`}>
          {SEVERITY_CONFIG[device.severity]?.label || device.severity?.toUpperCase()}
        </span>
      </div>
    </article>
  );
});

const DeviceModal = React.memo(({ device, onClose }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };

    const handleClickOutside = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('mousedown', handleClickOutside);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [onClose]);

  if (!device) return null;

  const deviceType = DEVICE_TYPES[device.type] || DEVICE_TYPES.unknown;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-content" ref={modalRef}>
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">Device Details</h2>
          <button 
            onClick={onClose} 
            className="modal-close"
            aria-label="Close device details"
          >
            <XCircle size={24} />
          </button>
        </div>
        
        <div className="modal-body">
          <div className="device-detail-grid">
            <div className="detail-item">
              <label className="detail-label">Device Name</label>
              <p className="detail-value">{device.name}</p>
            </div>
            
            <div className="detail-item">
              <label className="detail-label">IP Address</label>
              <p className="detail-value device-ip">{device.ip}</p>
            </div>
            
            <div className="detail-item">
              <label className="detail-label">Device Type</label>
              <p className="detail-value">{deviceType.label}</p>
            </div>
            
            <div className="detail-item">
              <label className="detail-label">Status</label>
              <p className={`detail-value status-${device.status?.toLowerCase()}`}>
                {device.status}
              </p>
            </div>
            
            <div className="detail-item">
              <label className="detail-label">MAC Address</label>
              <p className="detail-value device-mac">{device.mac_address || 'N/A'}</p>
            </div>
            
            <div className="detail-item">
              <label className="detail-label">Security Level</label>
              <p className={`detail-value severity-${device.severity}`}>
                {SEVERITY_CONFIG[device.severity]?.label || device.severity}
              </p>
            </div>
          </div>
          
          <div className="detail-section">
            <label className="detail-label">Open Ports</label>
            <div className="ports-container">
              {device.open_ports && device.open_ports.length > 0 ? (
                // CORRECTED SYNTAX: Removed the stray dot from the map function
                device.open_ports.map((port) => (
                  <span key={port} className="port-badge">
                    {port}
                  </span>
                ))
              ) : (
                <span className="no-ports">No open ports detected</span>
              )}
            </div>
          </div>
          
          <div className="detail-section">
            <label className="detail-label">Last Seen</label>
            <p className="detail-value">
              {device.lastSeen ? new Date(device.lastSeen).toLocaleString() : 'Unknown'}
            </p>
          </div>
          
          {device.vulnerabilities > 0 && (
            <div className="detail-section vulnerability-section">
              <label className="detail-label">
                <AlertTriangle className="vulnerability-icon" size={16} />
                Security Vulnerabilities ({device.vulnerabilities})
              </label>
              <p className="vulnerability-description">
                This device has been flagged with {device.vulnerabilities} potential security 
                issue{device.vulnerabilities > 1 ? 's' : ''}. Please review and update device 
                firmware, change default credentials, and ensure proper network segmentation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

// Main Component
const IoTDevicesDashboard = () => {
  const [networkRange, setNetworkRange] = useState(SCAN_CONFIG.DEFAULT_NETWORK);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('name');

  // Custom hooks
  const { devices, loading, error, stats, lastUpdate, fetchDevices } = useDeviceManager();
  const scanControls = useNetworkScanner(fetchDevices);

  // Effects
  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  // Auto-refresh every 30 seconds is disabled to only show latest scan results
  // You can re-enable it if you want the dashboard to poll for changes continuously
  /*
  useEffect(() => {
    const interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, [fetchDevices]);
  */

  // Filtered and sorted devices
  const filteredDevices = useMemo(() => {
    let filtered = devices;
    
    if (filterType !== 'all') {
      filtered = devices.filter(device => {
        switch (filterType) {
          case 'online': return device.status === 'Online';
          case 'offline': return device.status === 'Offline';
          case 'vulnerable': return device.severity === 'danger';
          default: return true;
        }
      });
    }

    // CORRECTED SYNTAX: Removed the stray dot from the sort function
    return [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name': return a.name.localeCompare(b.name);
        case 'ip': return a.ip.localeCompare(b.ip, undefined, { numeric: true });
        case 'severity': return (SEVERITY_CONFIG[b.severity]?.threshold || 0) - (SEVERITY_CONFIG[a.severity]?.threshold || 0);
        case 'type': return (DEVICE_TYPES[a.type]?.priority || 99) - (DEVICE_TYPES[b.type]?.priority || 99);
        default: return 0;
      }
    });
  }, [devices, filterType, sortBy]);

  return (
    <div className="iot-details-container">
      <MatrixBackground />
      
      <div className="content">
        {/* Header */}
        <header className="dashboard-header">
          <div className="header-content">
            <div className="header-info">
              <Shield className="header-icon" size={40} aria-hidden="true" />
              <div className="header-text">
                <h1 className="header-title">IoT Security Dashboard</h1>
                <p className="header-subtitle">Network Device Monitor & Threat Detection</p>
              </div>
            </div>
            
            <div className="header-status">
              <div className="system-status">
                <Activity className="status-icon active" size={20} aria-hidden="true" />
                <span className="status-text">SYSTEM ACTIVE</span>
              </div>
              {lastUpdate && (
                <div className="last-update">
                  <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Stats Cards */}
        <section className="stats-section" aria-label="Device statistics">
          <div className="stats-grid">
            <StatCard
              title="Total Devices"
              value={stats.total}
              icon={Globe}
              className="stat-total"
              isLoading={loading}
            />
            <StatCard
              title="Online"
              value={stats.online}
              icon={CheckCircle}
              className="stat-online"
              isLoading={loading}
            />
            <StatCard
              title="Offline"
              value={stats.offline}
              icon={XCircle}
              className="stat-offline"
              isLoading={loading}
            />
            <StatCard
              title="Vulnerable"
              value={stats.vulnerable}
              icon={AlertTriangle}
              className="stat-vulnerable"
              isLoading={loading}
            />
          </div>
        </section>

        {/* Scan Controls */}
        <section className="scan-section" aria-label="Network scanning controls">
          <ScanControls
            networkRange={networkRange}
            onNetworkRangeChange={setNetworkRange}
            onStartScan={scanControls.startScan}
            isScanning={scanControls.isScanning}
            progress={scanControls.progress}
            error={scanControls.error}
            onResetError={scanControls.resetError}
          />
        </section>

        {/* Device Controls */}
        <section className="devices-section">
          <div className="devices-header">
            <div className="devices-title">
              <Wifi className="devices-icon" size={20} aria-hidden="true" />
              <h2>Discovered Devices</h2>
              <span className="device-count">{filteredDevices.length}</span>
            </div>
            
            <div className="devices-controls">
              <div className="control-group">
                <Filter size={16} aria-hidden="true" />
                <select 
                  value={filterType} 
                  onChange={(e) => setFilterType(e.target.value)}
                  className="device-filter"
                  aria-label="Filter devices"
                >
                  <option value="all">All Devices</option>
                  <option value="online">Online Only</option>
                  <option value="offline">Offline Only</option>
                  <option value="vulnerable">Vulnerable Only</option>
                </select>
              </div>
              
              <div className="control-group">
                <ArrowUpDown size={16} aria-hidden="true" />
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  className="device-sort"
                  aria-label="Sort devices"
                >
                  <option value="name">Sort by Name</option>
                  <option value="ip">Sort by IP</option>
                  <option value="severity">Sort by Risk</option>
                  <option value="type">Sort by Type</option>
                </select>
              </div>
              
              <button 
                onClick={fetchDevices}
                disabled={loading || scanControls.isScanning}
                className="refresh-button"
                aria-label="Refresh device list"
              >
                <RefreshCw className={loading ? 'spinning' : ''} size={16} />
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-banner" role="alert">
              <AlertTriangle className="error-icon" size={20} />
              <span>Error loading devices: {error}</span>
            </div>
          )}

          {/* Devices Grid */}
          <div className="devices-grid">
            {loading && devices.length === 0 ? (
              <div className="loading-state">
                <div className="loading-spinner" />
                <p>Loading devices...</p>
              </div>
            ) : filteredDevices.length > 0 ? (
              filteredDevices.map((device) => (
                <DeviceCard
                  key={`${device.ip}-${device.mac_address}`}
                  device={device}
                  onViewDetails={setSelectedDevice}
                />
              ))
            ) : (
              <div className="empty-state">
                <Globe className="empty-icon" size={64} />
                <h3>No Devices Found</h3>
                <p>
                  {devices.length === 0 
                    ? 'Start a network scan to discover IoT devices.'
                    : 'No devices match the current filter criteria.'
                  }
                </p>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Device Details Modal */}
      {selectedDevice && (
        <DeviceModal 
          device={selectedDevice} 
          onClose={() => setSelectedDevice(null)} 
        />
      )}

      {/* Attack Detection Popup */}
      {stats.vulnerable > 0 && (
        <div className="attack-popup" role="alert" aria-live="assertive">
          <AlertTriangle size={24} />
          <span>Security Alert: {stats.vulnerable} vulnerable device{stats.vulnerable > 1 ? 's' : ''} detected!</span>
        </div>
      )}
    </div>
  );
};

export default IoTDevicesDashboard;