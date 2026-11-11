import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Plus,
  Trash2,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient from "../services/api";
import { getSocket } from "../services/socket";

const Blocklist = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [manualIp, setManualIp] = useState("");
  const [direction, setDirection] = useState("inbound");
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [reason, setReason] = useState("MANUAL_OPERATOR_BLOCK");
  const [submitting, setSubmitting] = useState(false);
  const [unblockingIp, setUnblockingIp] = useState(null);
  const [notification, setNotification] = useState("");

  const loadRules = async () => {
    try {
      const res = await apiClient.get("/api/blocklist");
      const list = res.data?.blocks || res.data?.rules || (Array.isArray(res.data) ? res.data : []);
      setRules(list);
    } catch (err) {
      console.error("Failed to load blocklist:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();

    const socket = getSocket();
    if (socket) {
      const handleBlocklistUpdate = (data) => {
        loadRules();
      };

      socket.on("blocklist_update", handleBlocklistUpdate);
      return () => {
        socket.off("blocklist_update", handleBlocklistUpdate);
      };
    }
  }, []);

  const handleManualBlock = async (e) => {
    e.preventDefault();
    if (!manualIp.trim()) return;

    setSubmitting(true);
    setNotification("");

    try {
      const res = await apiClient.post("/api/blocklist", {
        ip: manualIp.trim(),
        direction,
        minutes: parseInt(durationMinutes, 10) || 60,
        duration_minutes: parseInt(durationMinutes, 10) || 60,
        reason: reason.trim() || "MANUAL_OPERATOR_BLOCK",
      });

      if (res.data) {
        setNotification(`Rule applied: IP ${manualIp} blocked for ${durationMinutes}m.`);
        setManualIp("");
        loadRules();
      }
    } catch (err) {
      setNotification(
        err.response?.data?.message || err.response?.data?.error || "Failed to block IP. Address may be allowlisted."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnblock = async (ruleIdOrIp) => {
    setUnblockingIp(ruleIdOrIp);
    setNotification("");

    try {
      const res = await apiClient.delete(`/api/blocklist/${ruleIdOrIp}`);
      if (res.data) {
        setNotification(res.data.message || `Unblocked ${ruleIdOrIp}.`);
        loadRules();
      }
    } catch (err) {
      setNotification(
        err.response?.data?.message || err.response?.data?.error || `Failed to unblock ${ruleIdOrIp}. Admin required.`
      );
    } finally {
      setUnblockingIp(null);
    }
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="pb-4 border-b border-gray-800">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
            <ShieldAlert className="text-red-400" size={24} />
            FIREWALL MITIGATIONS & BLOCKLIST
          </h1>
          <p className="text-xs text-gray-400">
            Autonomous nftables Rules • Timed Element Drop Sets & Operator Controls
          </p>
        </div>

        {notification && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{notification}</span>
            <button onClick={() => setNotification("")}>✕</button>
          </div>
        )}

        {/* Manual Block Form */}
        <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg">
          <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
            <Plus size={16} className="text-red-400" />
            CREATE MANUAL FIREWALL MITIGATION
          </h3>

          <form onSubmit={handleManualBlock} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-xs">
            <div>
              <label className="block text-gray-400 mb-1">Target IP Address</label>
              <input
                type="text"
                value={manualIp}
                onChange={(e) => setManualIp(e.target.value)}
                placeholder="e.g. 192.168.50.100"
                required
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded font-mono text-gray-200 focus:outline-none focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Traffic Direction</label>
              <select
                value={direction}
                onChange={(e) => setDirection(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-300 focus:outline-none"
              >
                <option value="inbound">Inbound (Source Drop)</option>
                <option value="outbound">Outbound (Destination Drop)</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Duration (Minutes)</label>
              <input
                type="number"
                min="1"
                max="1440"
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(e.target.value)}
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Reason Code / Note</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Reason code..."
                className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none"
              />
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={submitting}
                className="w-full px-3 py-2 bg-red-950/80 hover:bg-red-900 border border-red-700 text-red-200 rounded font-semibold transition"
              >
                {submitting ? "ENFORCING..." : "ENFORCE BLOCK"}
              </button>
            </div>
          </form>
        </div>

        {/* Active Rules Table */}
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-gray-950/60">
          <div className="p-3 bg-gray-900/60 border-b border-gray-800 flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-300">
              ACTIVE & TIMED MITIGATION RULES ({rules.length})
            </span>
            <span className="text-[11px] text-gray-500">
              Auto-expiry managed by nftables timeout sets
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/90 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">IP ADDRESS</th>
                  <th className="py-2.5 px-3">DIRECTION</th>
                  <th className="py-2.5 px-3">REASON CODE</th>
                  <th className="py-2.5 px-3">CREATED AT</th>
                  <th className="py-2.5 px-3">EXPIRES AT</th>
                  <th className="py-2.5 px-3">STATUS</th>
                  <th className="py-2.5 px-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {rules.length > 0 ? (
                  rules.map((rule, idx) => {
                    const ip = rule.ip || rule.target_ip || "N/A";
                    const isExpired = rule.status === "expired";

                    return (
                      <tr key={rule.id || idx} className="hover:bg-gray-900/50 transition">
                        <td className="py-2.5 px-3 font-mono font-semibold text-gray-200">
                          {ip}
                        </td>
                        <td className="py-2.5 px-3 capitalize text-gray-400">
                          {rule.direction || "inbound"}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-[11px] text-amber-300">
                          {rule.reason || "—"}
                        </td>
                        <td className="py-2.5 px-3 text-gray-400">
                          {rule.created_at ? new Date(rule.created_at).toLocaleTimeString() : "N/A"}
                        </td>
                        <td className="py-2.5 px-3 text-gray-400">
                          {rule.expires_at ? new Date(rule.expires_at).toLocaleTimeString() : "Manual"}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                              isExpired
                                ? "bg-gray-900 text-gray-500 border-gray-800"
                                : "bg-red-950 text-red-300 border-red-700"
                            }`}
                          >
                            {rule.status ? rule.status.toUpperCase() : "ACTIVE"}
                            {rule.action === "rate_limit" ? " · RATE-LIMIT" : " · BLOCK"}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => handleUnblock(ip)}
                            disabled={unblockingIp === ip}
                            className="px-2.5 py-1 bg-gray-900 hover:bg-gray-800 text-gray-300 hover:text-white border border-gray-700 rounded text-[11px] inline-flex items-center gap-1 transition"
                          >
                            <Trash2 size={12} className="text-red-400" />
                            <span>{unblockingIp === ip ? "REMOVING..." : "UNBLOCK"}</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-8 text-gray-500">
                      {loading ? "Loading firewall rules..." : "No active mitigation rules. Network operating normally."}
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

export default Blocklist;
