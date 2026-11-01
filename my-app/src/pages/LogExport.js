import React, { useState, useEffect } from "react";
import {
  FileText,
  Download,
  FileSpreadsheet,
  FileCode,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient from "../services/api";
import { API_URL } from "../config";

const LogExport = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [logType, setLogType] = useState("attack_events");
  const [classFilter, setClassFilter] = useState("");
  const [ipFilter, setIpFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [notification, setNotification] = useState("");

  const loadSystemLogs = async () => {
    try {
      const res = await apiClient.get("/api/logs?limit=30");
      const list = res.data?.logs || (Array.isArray(res.data) ? res.data : []);
      setLogs(list);
    } catch (err) {
      console.error("Failed to load system logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSystemLogs();
  }, []);

  const handleExport = async (format) => {
    setExporting(true);
    setNotification("");

    try {
      let query = `/api/logs/export?type=${logType}&format=${format}`;
      if (classFilter) query += `&class=${classFilter}`;
      if (ipFilter.trim()) query += `&ip=${encodeURIComponent(ipFilter.trim())}`;
      if (startDate) query += `&start_time=${startDate}`;
      if (endDate) query += `&end_time=${endDate}`;

      const token = localStorage.getItem("token");

      // Use fetch to trigger browser attachment download with auth header
      const res = await fetch(`${API_URL}${query}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error(`Export failed with HTTP ${res.status}`);
      }

      // Extract filename from Content-Disposition if present
      const disposition = res.headers.get("Content-Disposition");
      let filename = `ids_export_${logType}_${new Date().toISOString().slice(0, 10)}.${format}`;
      if (disposition && disposition.includes("filename=")) {
        filename = disposition.split("filename=")[1].replace(/["']/g, "").trim();
      }

      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setNotification(`Forensic export created and downloaded: ${filename}. Audit recorded.`);
      loadSystemLogs();
    } catch (err) {
      setNotification(`Failed to export logs: ${err.message}. Admin authorization required.`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="pb-4 border-b border-gray-800">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
            <FileText className="text-blue-400" size={24} />
            FORENSIC LOGS & EXPORT ENGINE
          </h1>
          <p className="text-xs text-gray-400">
            Requirement FR-08 Export Architecture • Multi-Attribute Filtered CSV & JSON Telemetry
          </p>
        </div>

        {notification && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{notification}</span>
            <button onClick={() => setNotification("")}>✕</button>
          </div>
        )}

        {/* Forensic Export Generator Panel */}
        <div className="p-5 bg-gray-900/40 border border-gray-800 rounded-lg space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <Download size={16} className="text-blue-400" />
            DISPATCH FORENSIC LOG EXPORT (FR-08)
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="block text-gray-400 mb-1">Target Collection</label>
              <select
                value={logType}
                onChange={(e) => setLogType(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-300 focus:outline-none"
              >
                <option value="attack_events">Attack Events (Detections)</option>
                <option value="system_logs">System & Audit Logs</option>
                <option value="response_actions">Firewall Response Actions</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Attack Class (Optional)</label>
              <select
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-300 focus:outline-none"
              >
                <option value="">All Classes</option>
                <option value="Benign">Benign</option>
                <option value="DDoS">DDoS</option>
                <option value="PortScan">PortScan</option>
                <option value="CnC">CnC</option>
                <option value="Malware_Download">Malware_Download</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Filter by IP Address</label>
              <input
                type="text"
                value={ipFilter}
                onChange={(e) => setIpFilter(e.target.value)}
                placeholder="e.g. 192.168.50.10"
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded font-mono text-gray-200 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Start Date (UTC)</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1">End Date (UTC)</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none"
              />
            </div>
          </div>

          <div className="pt-3 border-t border-gray-800 flex flex-wrap items-center justify-between gap-3 text-xs">
            <span className="text-gray-500 text-[11px]">
              Every export creates a permanent immutable audit entry (`LOGS_EXPORTED`) in `system_logs`.
            </span>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleExport("csv")}
                disabled={exporting}
                className="px-3.5 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 rounded font-semibold flex items-center gap-1.5 transition"
              >
                <FileSpreadsheet size={14} />
                <span>EXPORT RFC 4180 CSV</span>
              </button>

              <button
                onClick={() => handleExport("json")}
                disabled={exporting}
                className="px-3.5 py-1.5 bg-blue-950/80 hover:bg-blue-900 border border-blue-700 text-blue-300 rounded font-semibold flex items-center gap-1.5 transition"
              >
                <FileCode size={14} />
                <span>EXPORT STRUCTURED JSON</span>
              </button>
            </div>
          </div>
        </div>

        {/* System & Audit Logs Table */}
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-gray-950/60">
          <div className="p-3 bg-gray-900/60 border-b border-gray-800 flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-300">
              AUDIT TRAIL & SYSTEM LOGS (LAST {logs.length} RECORDS)
            </span>
            <span className="text-[11px] text-gray-500">Immutable MongoDB Audit Stream</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/90 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">TIMESTAMP</th>
                  <th className="py-2.5 px-3">EVENT</th>
                  <th className="py-2.5 px-3">ACTOR</th>
                  <th className="py-2.5 px-3">OUTCOME</th>
                  <th className="py-2.5 px-3">DETAILS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {logs.length > 0 ? (
                  logs.map((log, idx) => (
                    <tr key={log.id || idx} className="hover:bg-gray-900/50 transition">
                      <td className="py-2.5 px-3 text-gray-400">
                        {log.timestamp ? new Date(log.timestamp).toLocaleString() : "N/A"}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-semibold text-gray-200">
                        {log.event}
                      </td>
                      <td className="py-2.5 px-3 text-emerald-400">{log.actor || "system"}</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                            log.outcome === "SUCCESS" || log.outcome === "success"
                              ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                              : "bg-red-950 text-red-300 border-red-800"
                          }`}
                        >
                          {log.outcome || "INFO"}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-gray-400 font-mono text-[11px]">
                        {log.details ? JSON.stringify(log.details).slice(0, 70) : "—"}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center py-8 text-gray-500">
                      {loading ? "Loading audit stream..." : "No system logs recorded yet."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default LogExport;
