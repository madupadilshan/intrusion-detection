import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  Shield,
  Camera,
  ArrowRight,
  Radio,
  CheckCircle2,
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import Layout from "../components/Layout";
import apiClient from "../services/api";
import { getSocket } from "../services/socket";

const CLASS_COLORS = {
  Benign: "#10b981",
  DDoS: "#ef4444",
  DDoS_DoS: "#ef4444",
  PortScan: "#f59e0b",
  CnC: "#8b5cf6",
  Malware_Download: "#ec4899",
  Unknown: "#6b7280",
};

const Overview = () => {
  const [summary, setSummary] = useState({
    total_events: 0,
    attacks_detected: 0,
    blocked_ips: 0,
    active_devices: 0,
    class_distribution: {},
    traffic_volume_24h: [],
  });
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchOverview = async () => {
      try {
        const [sumRes, evRes] = await Promise.all([
          apiClient.get("/api/summary").catch(() => ({ data: {} })),
          apiClient.get("/api/events?limit=6").catch(() => ({ data: { events: [] } })),
        ]);

        if (isMounted) {
          if (sumRes.data) setSummary((prev) => ({ ...prev, ...sumRes.data }));
          if (evRes.data?.events) setRecentAlerts(evRes.data.events);
        }
      } catch (err) {
        console.error("Failed to load overview data:", err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchOverview();

    const socket = getSocket();
    if (socket) {
      const handleSummaryUpdate = (data) => {
        if (!isMounted) return;
        setSummary((prev) => ({ ...prev, ...data }));
      };

      const handleNewEvent = (event) => {
        if (!isMounted) return;
        setRecentAlerts((prev) => [event, ...prev.slice(0, 5)]);
      };

      socket.on("summary_update", handleSummaryUpdate);
      socket.on("new_event", handleNewEvent);

      return () => {
        isMounted = false;
        socket.off("summary_update", handleSummaryUpdate);
        socket.off("new_event", handleNewEvent);
      };
    }

    return () => {
      isMounted = false;
    };
  }, []);

  // Format class distribution data for chart
  const classData = Object.entries(summary.class_distribution || {}).map(([key, val]) => ({
    name: key,
    count: val,
    color: CLASS_COLORS[key] || CLASS_COLORS.Unknown,
  }));

  return (
    <Layout>
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-gray-800">
          <div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
              <Radio className="text-emerald-400" size={24} />
              SYSTEM OVERVIEW
            </h1>
            <p className="text-xs text-gray-400">
              IP-Camera Real-Time Intrusion Detection & Autonomous Mitigation Engine
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2.5 py-1 bg-emerald-950/60 border border-emerald-800 text-emerald-300 rounded flex items-center gap-1.5">
              <CheckCircle2 size={13} /> SENSOR & PIPELINE ACTIVE
            </span>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          <div className="p-4 bg-gray-900/60 border border-emerald-900/80 rounded-lg">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span>MONITORED FLOWS</span>
              <Activity size={16} className="text-emerald-400" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-emerald-400">
              {summary.total_events?.toLocaleString() || 0}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Total connection telemetry</div>
          </div>

          <div className="p-4 bg-gray-900/60 border border-red-900/80 rounded-lg">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span>ATTACKS DETECTED</span>
              <AlertTriangle size={16} className="text-red-400" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-red-400">
              {summary.attacks_detected?.toLocaleString() || 0}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Classified intrusion events</div>
          </div>

          <div className="p-4 bg-gray-900/60 border border-amber-900/80 rounded-lg">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span>ACTIVE BLOCKS</span>
              <Shield size={16} className="text-amber-400" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-amber-400">
              {summary.blocked_ips || 0}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">nftables firewall drop rules</div>
          </div>

          <div className="p-4 bg-gray-900/60 border border-cyan-900/80 rounded-lg">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span>CONNECTED ASSETS</span>
              <Camera size={16} className="text-cyan-400" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-cyan-400">
              {summary.active_devices || 0}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Discovered IP cameras & nodes</div>
          </div>
        </div>

        {/* Charts & Graphs Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Attack Class Distribution */}
          <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center justify-between">
              <span>ATTACK CLASS DISTRIBUTION</span>
              <span className="text-[11px] text-gray-500">Multiclass Inferences</span>
            </h3>
            {classData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={classData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                    <XAxis
                      dataKey="name"
                      tick={{ fill: "#9ca3af", fontSize: 11 }}
                      interval={0}
                      angle={-15}
                      textAnchor="end"
                    />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#111827",
                        borderColor: "#374151",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {classData.map((entry, idx) => (
                        <Cell key={`cell-${idx}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 text-xs">
                No classification events logged yet.
              </div>
            )}
          </div>

          {/* Quick Security Status / Lab Topology */}
          <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center justify-between">
                <span>LAB INFRASTRUCTURE & SAFETY</span>
                <span className="text-[11px] text-emerald-400">Subnet: 192.168.50.0/24</span>
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2.5 bg-gray-950/60 border border-gray-800 rounded">
                  <span className="text-gray-400">Autonomous Mitigation</span>
                  <span className="text-emerald-400 font-semibold">Direction-Aware Policy</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-gray-950/60 border border-gray-800 rounded">
                  <span className="text-gray-400">Allowlist Protection</span>
                  <span className="text-emerald-400 font-semibold">Active (4 nodes immune)</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-gray-950/60 border border-gray-800 rounded">
                  <span className="text-gray-400">Zeek Ingestion Throughput</span>
                  <span className="text-cyan-400 font-semibold">23,108 fps (Adapter locked)</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-gray-950/60 border border-gray-800 rounded">
                  <span className="text-gray-400">ML Model Latency</span>
                  <span className="text-purple-400 font-semibold">6.46 µs / inference</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-800 flex items-center justify-between text-xs">
              <span className="text-gray-500">Managed via Group 03 Decision Engine</span>
              <Link to="/mitigations" className="text-emerald-400 hover:underline flex items-center gap-1">
                View Mitigations <ArrowRight size={13} />
              </Link>
            </div>
          </div>
        </div>

        {/* Recent Alerts Feed Table */}
        <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
              <AlertTriangle size={16} className="text-red-400" />
              RECENT INTRUSION ALERTS
            </h3>
            <Link to="/alerts" className="text-xs text-emerald-400 hover:underline flex items-center gap-1">
              Live Stream <ArrowRight size={13} />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-950 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-2 px-3">TIMESTAMP</th>
                  <th className="py-2 px-3">CLASS</th>
                  <th className="py-2 px-3">SOURCE</th>
                  <th className="py-2 px-3">DESTINATION</th>
                  <th className="py-2 px-3">CONFIDENCE</th>
                  <th className="py-2 px-3">BADGE</th>
                  <th className="py-2 px-3">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {recentAlerts.length > 0 ? (
                  recentAlerts.map((evt, idx) => {
                    const cls = evt.predicted_class || "Unknown";
                    const isConfirmed = evt.status === "confirmed";
                    return (
                      <tr key={evt.id || idx} className="hover:bg-gray-900/60 transition">
                        <td className="py-2.5 px-3 text-gray-400">
                          {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : "N/A"}
                        </td>
                        <td className="py-2.5 px-3 font-semibold">
                          <span style={{ color: CLASS_COLORS[cls] || "#9ca3af" }}>{cls}</span>
                        </td>
                        <td className="py-2.5 px-3 text-gray-300 font-mono">{evt.src_ip || "N/A"}</td>
                        <td className="py-2.5 px-3 text-gray-300 font-mono">{evt.dst_ip || "N/A"}</td>
                        <td className="py-2.5 px-3 text-gray-300">
                          {evt.confidence ? `${(evt.confidence * 100).toFixed(1)}%` : "N/A"}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide border ${
                              isConfirmed
                                ? "bg-red-950 text-red-300 border-red-700"
                                : "bg-blue-950 text-blue-300 border-blue-700"
                            }`}
                          >
                            {isConfirmed ? "CONFIRMED INCIDENT" : "MODEL PREDICTION"}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-gray-400 capitalize">
                          {evt.response_status || "Logged"}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-6 text-gray-500">
                      {isLoading ? "Loading telemetry..." : "No alerts recorded yet. Network benign."}
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

export default Overview;
