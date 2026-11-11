import React, { useState, useEffect } from "react";
import {
  Shield,
  CheckCircle,
  Radio,
  ArrowRight,
  Pause,
  Play,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient, { withEventId } from "../services/api";
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

const LiveAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [confirmingId, setConfirmingId] = useState(null);
  const [blockingIp, setBlockingIp] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    // Load initial recent alerts
    const loadAlerts = async () => {
      try {
        const res = await apiClient.get("/api/events?limit=40");
        const list = (res.data?.events || []).map(withEventId);
        if (isMounted) {
          setAlerts(list);
        }
      } catch (err) {
        console.error("Failed to load initial alerts:", err);
      }
    };

    loadAlerts();

    const socket = getSocket();
    if (socket) {
      const handleNewEvent = (event) => {
        if (!isMounted || isPaused) return;
        const item = withEventId(event);
        setAlerts((prev) => {
          if (item.id && prev.some((e) => e.id === item.id)) {
            return prev.map((e) => (e.id === item.id ? { ...e, ...item } : e));
          }
          return [item, ...prev.slice(0, 99)];
        });
      };

      const handleEventUpdate = (updatedEvent) => {
        if (!isMounted) return;
        setAlerts((prev) =>
          prev.map((e) =>
            e.id === (updatedEvent.event_id || updatedEvent.id) ? { ...e, ...updatedEvent, id: e.id } : e
          )
        );
      };

      socket.on("new_event", handleNewEvent);
      socket.on("event_update", handleEventUpdate);

      return () => {
        isMounted = false;
        socket.off("new_event", handleNewEvent);
        socket.off("event_update", handleEventUpdate);
      };
    }

    return () => {
      isMounted = false;
    };
  }, [isPaused]);

  // Admin action: Mark as Confirmed Incident (PATCH /api/events/<id>)
  const handleConfirmIncident = async (eventId) => {
    setConfirmingId(eventId);
    setStatusMessage("");
    try {
      const res = await apiClient.patch(`/api/events/${eventId}`, {
        status: "confirmed",
      });
      if (res.data) {
        setAlerts((prev) =>
          prev.map((e) => (e.id === eventId ? { ...e, status: "confirmed" } : e))
        );
        setStatusMessage(`Event ${eventId} marked as CONFIRMED INCIDENT.`);
      }
    } catch (err) {
      setStatusMessage(
        err.response?.data?.error || "Failed to confirm incident. Admin rights required."
      );
    } finally {
      setConfirmingId(null);
    }
  };

  // Admin action: Quick Block Source IP (POST /api/blocklist)
  const handleBlockIp = async (ip, reason = "MANUAL_OPERATOR_BLOCK") => {
    if (!ip) return;
    setBlockingIp(ip);
    setStatusMessage("");
    try {
      const res = await apiClient.post("/api/blocklist", {
        ip,
        direction: "inbound",
        minutes: 60,
        reason,
      });
      if (res.data) {
        setStatusMessage(`IP address ${ip} successfully blocked in firewall.`);
      }
    } catch (err) {
      setStatusMessage(
        err.response?.data?.error || `Failed to block ${ip}. Allowlisted or unauthorized.`
      );
    } finally {
      setBlockingIp(null);
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (selectedFilter === "all") return true;
    if (selectedFilter === "confirmed") return alert.status === "confirmed";
    if (selectedFilter === "prediction") return alert.status !== "confirmed";
    if (selectedFilter === "attacks_only") {
      const cls = alert.predicted_class || "";
      return cls.toLowerCase() !== "benign";
    }
    return true;
  });

  return (
    <Layout>
      <div className="space-y-5 max-w-7xl mx-auto">
        {/* Header & Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-gray-800">
          <div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
              <Radio className="text-red-400 animate-pulse" size={24} />
              REAL-TIME INTRUSION ALERTS
            </h1>
            <p className="text-xs text-gray-400">
              Live Socket.IO Stream • Calibrated Inferences, Model Predictions & Confirmed Incidents
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded border transition ${
                isPaused
                  ? "bg-amber-950/80 border-amber-700 text-amber-300"
                  : "bg-gray-900 border-gray-700 text-gray-300 hover:bg-gray-800"
              }`}
            >
              {isPaused ? <Play size={13} /> : <Pause size={13} />}
              <span>{isPaused ? "RESUME STREAM" : "PAUSE STREAM"}</span>
            </button>

            {/* Filter buttons */}
            <div className="flex items-center bg-gray-900 border border-gray-800 rounded p-0.5">
              <button
                onClick={() => setSelectedFilter("all")}
                className={`px-2.5 py-1 rounded text-[11px] ${
                  selectedFilter === "all" ? "bg-emerald-950 text-emerald-300 font-semibold" : "text-gray-400"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setSelectedFilter("attacks_only")}
                className={`px-2.5 py-1 rounded text-[11px] ${
                  selectedFilter === "attacks_only" ? "bg-red-950 text-red-300 font-semibold" : "text-gray-400"
                }`}
              >
                Attacks
              </button>
              <button
                onClick={() => setSelectedFilter("confirmed")}
                className={`px-2.5 py-1 rounded text-[11px] ${
                  selectedFilter === "confirmed" ? "bg-purple-950 text-purple-300 font-semibold" : "text-gray-400"
                }`}
              >
                Confirmed
              </button>
            </div>
          </div>
        </div>

        {/* Status notification */}
        {statusMessage && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{statusMessage}</span>
            <button onClick={() => setStatusMessage("")} className="text-gray-400 hover:text-white">
              ✕
            </button>
          </div>
        )}

        {/* Alerts Stream List */}
        <div className="space-y-3">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map((evt, idx) => {
              const cls = evt.predicted_class || "Unknown";
              const isConfirmed = evt.status === "confirmed";
              const conf = evt.confidence ? (evt.confidence * 100).toFixed(1) : "0.0";
              const isBenign = cls.toLowerCase() === "benign";

              return (
                <div
                  key={evt.id || idx}
                  className={`p-4 bg-gray-950/70 border rounded-lg transition hover:border-gray-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                    isConfirmed
                      ? "border-red-900/80 bg-red-950/10"
                      : isBenign
                      ? "border-gray-800"
                      : "border-gray-800/80"
                  }`}
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Badge: Model Prediction vs Confirmed Incident */}
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider border ${
                          isConfirmed
                            ? "bg-red-950 text-red-300 border-red-700 shadow-[0_0_8px_rgba(239,68,68,0.4)]"
                            : "bg-blue-950/80 text-blue-300 border-blue-700"
                        }`}
                      >
                        {isConfirmed ? "CONFIRMED INCIDENT" : "MODEL PREDICTION"}
                      </span>

                      {/* Class pill */}
                      <span
                        className="px-2 py-0.5 rounded text-[11px] font-bold"
                        style={{
                          backgroundColor: `${CLASS_COLORS[cls] || "#6b7280"}22`,
                          color: CLASS_COLORS[cls] || "#9ca3af",
                          border: `1px solid ${CLASS_COLORS[cls] || "#6b7280"}44`,
                        }}
                      >
                        {cls}
                      </span>

                      <span className="text-xs text-gray-400">
                        Confidence: <strong className="text-gray-200">{conf}%</strong>
                      </span>

                      <span className="text-[11px] text-gray-500">
                        {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : "N/A"}
                      </span>

                      {/* Response status (proposal 3.6): what the response policy did */}
                      <span
                        title={evt.response_reason || ""}
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider border ${
                          evt.response_status === "blocked" || evt.response_status === "rate_limited"
                            ? "bg-red-950 text-red-300 border-red-700"
                            : evt.response_status === "already_blocked"
                            ? "bg-orange-950 text-orange-300 border-orange-700"
                            : "bg-gray-900 text-gray-300 border-gray-700"
                        }`}
                      >
                        RESPONSE: {(evt.response_status || "none").toUpperCase()}
                        {evt.response_reason ? ` (${evt.response_reason})` : ""}
                      </span>
                    </div>

                    {/* Flow Network Vectors */}
                    <div className="flex items-center gap-2 text-xs font-mono text-gray-300">
                      <span className="text-gray-400">{evt.src_ip || "unknown"}:{evt.src_port || "*"}</span>
                      <ArrowRight size={13} className="text-gray-500" />
                      <span className="text-gray-400">{evt.dst_ip || "unknown"}:{evt.dst_port || "*"}</span>
                      <span className="text-gray-500 text-[11px]">({evt.proto || "TCP"})</span>
                      {evt.direction && (
                        <span className="text-[10px] bg-gray-900 border border-gray-800 px-1.5 py-0.5 rounded text-gray-400">
                          {evt.direction}
                        </span>
                      )}
                    </div>

                    {/* Evidence Note */}
                    {evt.evidence_note && (
                      <p className="text-xs text-amber-300/90 bg-amber-950/20 border-l-2 border-amber-600 pl-2 py-0.5">
                        {evt.evidence_note}
                      </p>
                    )}
                  </div>

                  {/* Actions column */}
                  <div className="flex items-center gap-2 text-xs w-full md:w-auto justify-end border-t md:border-t-0 pt-2 md:pt-0 border-gray-900">
                    {!isConfirmed && (
                      <button
                        onClick={() => handleConfirmIncident(evt.id)}
                        disabled={confirmingId === evt.id}
                        className="flex items-center gap-1 px-2.5 py-1.5 bg-purple-950/80 hover:bg-purple-900 border border-purple-700 text-purple-200 rounded transition"
                      >
                        <CheckCircle size={13} />
                        <span>{confirmingId === evt.id ? "CONFIRMING..." : "CONFIRM INCIDENT"}</span>
                      </button>
                    )}

                    {!isBenign && evt.src_ip && (
                      <button
                        onClick={() => handleBlockIp(evt.src_ip)}
                        disabled={blockingIp === evt.src_ip}
                        className="flex items-center gap-1 px-2.5 py-1.5 bg-red-950/80 hover:bg-red-900 border border-red-700 text-red-200 rounded transition"
                      >
                        <Shield size={13} />
                        <span>{blockingIp === evt.src_ip ? "BLOCKING..." : "BLOCK SOURCE"}</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-12 text-center bg-gray-950/40 border border-gray-900 rounded-lg text-gray-500 text-xs">
              No live alerts in the buffer. Telemetry engine monitoring benign flows.
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default LiveAlerts;
