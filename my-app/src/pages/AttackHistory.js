import React, { useState, useEffect } from "react";
import {
  History,
  Search,
  Filter,
  CheckCircle,
  Eye,
  X,
  ShieldAlert,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient, { withEventId } from "../services/api";

const CLASS_COLORS = {
  Benign: "#10b981",
  DDoS: "#ef4444",
  DDoS_DoS: "#ef4444",
  PortScan: "#f59e0b",
  CnC: "#8b5cf6",
  Malware_Download: "#ec4899",
  Unknown: "#6b7280",
};

const AttackHistory = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [searchIp, setSearchIp] = useState("");
  const [classFilter, setClassFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [confirmingId, setConfirmingId] = useState(null);
  const [notification, setNotification] = useState("");

  const loadEvents = async () => {
    setLoading(true);
    try {
      let query = "/api/events?limit=100";
      if (classFilter !== "all") query += `&class=${classFilter}`;
      if (statusFilter !== "all") query += `&status=${statusFilter}`;
      if (searchIp.trim()) query += `&ip=${encodeURIComponent(searchIp.trim())}`;

      const res = await apiClient.get(query);
      const list = (res.data?.events || []).map(withEventId);
      setEvents(list);
    } catch (err) {
      console.error("Failed to load attack history:", err);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, [classFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadEvents();
  };

  const handleConfirmIncident = async (id) => {
    setConfirmingId(id);
    try {
      const res = await apiClient.patch(`/api/events/${id}`, { status: "confirmed" });
      if (res.data) {
        setEvents((prev) =>
          prev.map((e) => (e.id === id ? { ...e, status: "confirmed" } : e))
        );
        if (selectedEvent && selectedEvent.id === id) {
          setSelectedEvent((prev) => ({ ...prev, status: "confirmed" }));
        }
        setNotification(`Event ${id} confirmed as incident.`);
      }
    } catch (err) {
      setNotification(err.response?.data?.error || "Failed to confirm incident.");
    } finally {
      setConfirmingId(null);
    }
  };

  return (
    <Layout>
      <div className="space-y-5 max-w-7xl mx-auto">
        {/* Header */}
        <div className="pb-4 border-b border-gray-800">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
            <History className="text-cyan-400" size={24} />
            ATTACK HISTORY & FORENSIC DATABASE
          </h1>
          <p className="text-xs text-gray-400">
            Searchable MongoDB Incident Records • Evidence Inspection & Administrative Confirmation
          </p>
        </div>

        {notification && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{notification}</span>
            <button onClick={() => setNotification("")}>✕</button>
          </div>
        )}

        {/* Search & Filter Bar */}
        <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg flex flex-col md:flex-row gap-3 items-center justify-between">
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 w-full md:w-auto flex-1">
            <div className="relative flex-1 max-w-md">
              <Search size={14} className="absolute left-3 top-3 text-gray-500" />
              <input
                type="text"
                value={searchIp}
                onChange={(e) => setSearchIp(e.target.value)}
                placeholder="Search by IP address (source or destination)..."
                className="w-full pl-9 pr-3 py-2 bg-gray-950 border border-gray-800 rounded text-xs text-gray-200 placeholder-gray-600 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <button
              type="submit"
              className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded text-xs border border-gray-700"
            >
              SEARCH
            </button>
          </form>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto text-xs">
            <div className="flex items-center gap-1.5">
              <Filter size={13} className="text-gray-500" />
              <span className="text-gray-400">Class:</span>
              <select
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
                className="bg-gray-950 border border-gray-800 rounded px-2 py-1 text-gray-300 text-xs focus:outline-none"
              >
                <option value="all">All Classes</option>
                <option value="Benign">Benign</option>
                <option value="DDoS">DDoS</option>
                <option value="PortScan">PortScan</option>
                <option value="CnC">CnC</option>
                <option value="Malware_Download">Malware_Download</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 ml-2">
              <span className="text-gray-400">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-gray-950 border border-gray-800 rounded px-2 py-1 text-gray-300 text-xs focus:outline-none"
              >
                <option value="all">All Statuses</option>
                <option value="prediction">Model Prediction</option>
                <option value="confirmed">Confirmed Incident</option>
              </select>
            </div>
          </div>
        </div>

        {/* Events Table */}
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-gray-950/60">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/90 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">TIMESTAMP</th>
                  <th className="py-2.5 px-3">PREDICTED CLASS</th>
                  <th className="py-2.5 px-3">SOURCE</th>
                  <th className="py-2.5 px-3">DESTINATION</th>
                  <th className="py-2.5 px-3">CONFIDENCE</th>
                  <th className="py-2.5 px-3">STATUS</th>
                  <th className="py-2.5 px-3 text-right">DETAILS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {events.length > 0 ? (
                  events.map((evt, idx) => {
                    const cls = evt.predicted_class || "Unknown";
                    const isConfirmed = evt.status === "confirmed";
                    return (
                      <tr key={evt.id || idx} className="hover:bg-gray-900/50 transition">
                        <td className="py-2.5 px-3 text-gray-400">
                          {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : "N/A"}
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
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                              isConfirmed
                                ? "bg-red-950 text-red-300 border-red-700"
                                : "bg-blue-950 text-blue-300 border-blue-700"
                            }`}
                          >
                            {isConfirmed ? "CONFIRMED" : "PREDICTION"}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => setSelectedEvent(evt)}
                            className="px-2 py-1 bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700 rounded text-[11px] inline-flex items-center gap-1"
                          >
                            <Eye size={12} /> Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-8 text-gray-500">
                      {loading ? "Searching forensic database..." : "No events found matching query filters."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detailed Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-950 border border-gray-800 rounded-lg max-w-2xl w-full p-5 space-y-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
                  <ShieldAlert size={18} className="text-red-400" />
                  INCIDENT FORENSIC RECORD
                </h3>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800">
                  <div className="text-gray-500">Predicted Class</div>
                  <div className="font-bold text-sm text-gray-200 mt-0.5">
                    {selectedEvent.predicted_class}
                  </div>
                </div>
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800">
                  <div className="text-gray-500">Confidence</div>
                  <div className="font-bold text-sm text-gray-200 mt-0.5">
                    {selectedEvent.confidence
                      ? `${(selectedEvent.confidence * 100).toFixed(2)}%`
                      : "N/A"}
                  </div>
                </div>
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800 font-mono">
                  <div className="text-gray-500">Source IP & Port</div>
                  <div className="text-gray-200 mt-0.5">
                    {selectedEvent.src_ip}:{selectedEvent.src_port || "*"}
                  </div>
                </div>
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800 font-mono">
                  <div className="text-gray-500">Destination IP & Port</div>
                  <div className="text-gray-200 mt-0.5">
                    {selectedEvent.dst_ip}:{selectedEvent.dst_port || "*"}
                  </div>
                </div>
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800">
                  <div className="text-gray-500">Protocol & State</div>
                  <div className="text-gray-200 mt-0.5">
                    {selectedEvent.proto || "TCP"} / {selectedEvent.conn_state || "SF"}
                  </div>
                </div>
                <div className="p-2.5 bg-gray-900/60 rounded border border-gray-800">
                  <div className="text-gray-500">Model Version</div>
                  <div className="text-gray-200 mt-0.5">
                    {selectedEvent.model_version || "unknown"}
                  </div>
                </div>
              </div>

              {/* Evidence Note */}
              {selectedEvent.evidence_note && (
                <div className="p-3 bg-amber-950/20 border border-amber-900/60 rounded text-xs text-amber-200">
                  <strong className="block text-amber-400 mb-1">Empirical Evidence Note:</strong>
                  {selectedEvent.evidence_note}
                </div>
              )}

              {/* Confirmation Action */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-800 text-xs">
                <div>
                  <span className="text-gray-500">Current Status: </span>
                  <span className="font-semibold text-gray-200 uppercase">
                    {selectedEvent.status || "prediction"}
                  </span>
                </div>
                {selectedEvent.status !== "confirmed" ? (
                  <button
                    onClick={() => handleConfirmIncident(selectedEvent.id)}
                    disabled={confirmingId === selectedEvent.id}
                    className="px-3 py-1.5 bg-purple-950 hover:bg-purple-900 border border-purple-700 text-purple-200 rounded flex items-center gap-1.5 font-semibold"
                  >
                    <CheckCircle size={14} />
                    <span>{confirmingId === selectedEvent.id ? "CONFIRMING..." : "CONFIRM AS INCIDENT"}</span>
                  </button>
                ) : (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle size={14} /> Confirmed by Administrator
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AttackHistory;
