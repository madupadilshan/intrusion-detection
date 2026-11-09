import React, { useState, useEffect } from "react";
import {
  Settings as SettingsIcon,
  Shield,
  Sliders,
  Save,
  History,
} from "lucide-react";
import Layout from "../components/Layout";
import apiClient from "../services/api";

const Settings = () => {
  // Shown until the server answers; the real values come from GET /api/settings
  const [settings, setSettings] = useState({
    min_confidence: 0.30,
    min_repeats: 3,
    repeat_window_seconds: 60,
    max_rule_minutes: 30,
    auto_response: false,
    adapter: "unknown",
    firewall_simulated: true,
    management_allowlist: [],
  });
  const [original, setOriginal] = useState({});
  const [history, setHistory] = useState([]);
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState("");

  const loadSettings = async () => {
    try {
      const [setRes, histRes] = await Promise.all([
        apiClient.get("/api/settings").catch(() => ({ data: {} })),
        apiClient.get("/api/settings/history").catch(() => ({ data: { history: [] } })),
      ]);

      const server = setRes.data?.settings;
      if (server) {
        const merged = {
          ...server,
          min_confidence: server.min_confidence ?? 0.30,
          management_allowlist: server.allowlist || [],
        };
        setSettings((prev) => ({ ...prev, ...merged }));
        setOriginal(merged);
      }
      if (histRes.data?.history) {
        setHistory(histRes.data.history);
      }
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setNotification("");

    try {
      // The API saves ONE setting per request ({key, value, reason}) with its history (FR-07)
      const keys = ["min_confidence", "min_repeats", "repeat_window_seconds", "max_rule_minutes"];
      const changed = keys.filter((k) => settings[k] !== original[k]);
      if (changed.length === 0) {
        setNotification("No change to save.");
        return;
      }
      for (const k of changed) {
        await apiClient.put("/api/settings", {
          key: k,
          value: settings[k],
          reason: "Changed from the dashboard Settings page",
        });
      }
      setNotification("Saved: " + changed.join(", ") + ". Each change is kept in the audit history.");
      loadSettings();
    } catch (err) {
      setNotification(
        err.response?.data?.message || err.response?.data?.error || "Failed to save settings. Admin privileges required."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-5xl mx-auto">
        {/* Header */}
        <div className="pb-4 border-b border-gray-800">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
            <SettingsIcon className="text-emerald-400" size={24} />
            SECURITY SYSTEM SETTINGS & SAFETY POLICY
          </h1>
          <p className="text-xs text-gray-400">
            Allowlist Management • Operational Mitigation Thresholds • Audit Configuration
          </p>
        </div>

        {notification && (
          <div className="p-3 bg-gray-900 border border-emerald-800 text-emerald-300 text-xs rounded flex items-center justify-between">
            <span>{notification}</span>
            <button onClick={() => setNotification("")}>✕</button>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Autonomous Response Master Switch */}
          <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-lg flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-gray-200">
                Autonomous Mitigation Master Switch
              </h3>
              <p className="text-xs text-gray-400 mt-0.5">
                When on, a block happens only after every safety rule passes (allowlist, local-network protection, confidence, repeats, rule expiry).
              </p>
            </div>
            <div className="text-right text-xs">
              <span
                className={`px-2 py-1 rounded border font-semibold ${
                  settings.auto_response
                    ? "bg-red-950 text-red-300 border-red-700"
                    : "bg-gray-900 text-gray-300 border-gray-700"
                }`}
              >
                {settings.auto_response ? "ON" : "OFF"}
              </span>
              <p className="text-[11px] text-gray-500 mt-1">
                Set in config/settings.yaml (response.auto_response). Turn on only for planned lab tests.
                {" "}Adapter: {settings.adapter}{settings.firewall_simulated ? " (simulation: nothing is really blocked)" : ""}
              </p>
            </div>
          </div>

          {/* Operational Thresholds Grid */}
          <div className="p-5 bg-gray-900/40 border border-gray-800 rounded-lg space-y-4">
            <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
              <Sliders size={16} className="text-emerald-400" />
              DETECTION & MITIGATION THRESHOLDS
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">
                  Minimum Confidence for Any Block (0.30 – 0.99)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0.3"
                    max="0.99"
                    step="0.01"
                    value={settings.min_confidence}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        min_confidence: parseFloat(e.target.value),
                      })
                    }
                    className="flex-1 accent-emerald-500"
                  />
                  <span className="font-mono text-emerald-400 font-bold w-12 text-right">
                    {(settings.min_confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <span className="text-[11px] text-gray-500">
                  Lowest confidence for any automatic block. Each class also has its own block threshold from Step 17 (D-046).
                </span>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">
                  Minimum Repeated Events (`min_repeats`)
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={settings.min_repeats}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      min_repeats: parseInt(e.target.value, 10) || 1,
                    })
                  }
                  className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-gray-500">
                  Number of repeat attack flows required to trigger automated block.
                </span>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">
                  Sliding Window Duration (Seconds)
                </label>
                <input
                  type="number"
                  min="5"
                  max="600"
                  value={settings.repeat_window_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      repeat_window_seconds: parseInt(e.target.value, 10) || 60,
                    })
                  }
                  className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-gray-500">
                  Time window for repeat event counting (`repeat_window_seconds`).
                </span>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">
                  Firewall Rule Expiry (`max_rule_minutes`)
                </label>
                <input
                  type="number"
                  min="5"
                  max="1440"
                  value={settings.max_rule_minutes}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      max_rule_minutes: parseInt(e.target.value, 10) || 60,
                    })
                  }
                  className="w-full px-3 py-1.5 bg-gray-950 border border-gray-800 rounded text-gray-200 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-gray-500">
                  nftables set timeout in minutes before drop rule expires.
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-gray-800/80 flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 rounded font-semibold text-xs flex items-center gap-1.5 transition"
              >
                <Save size={14} />
                <span>{saving ? "SAVING SETTINGS..." : "SAVE OPERATIONAL SETTINGS"}</span>
              </button>
            </div>
          </div>
        </form>

        {/* Management Allowlist Card */}
        <div className="p-5 bg-gray-900/40 border border-gray-800 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
              <Shield size={16} className="text-emerald-400" />
              MANAGEMENT ALLOWLIST (IMMUNITY LIST)
            </h3>
            <span className="text-[11px] text-emerald-400 font-mono">
              Strictly Protected
            </span>
          </div>

          <p className="text-xs text-gray-400">
            Per Group 03 Proposal Section 3.7, allowlisted nodes are permanently immune to blocking. Any incoming attack attributed to these IPs is alerted only and never dropped by the firewall.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
            {settings.management_allowlist.map((ip, idx) => (
              <div
                key={idx}
                className="p-2.5 bg-gray-950 border border-gray-800 rounded flex items-center justify-between"
              >
                <span className="text-emerald-300">{ip}</span>
                <span className="text-[10px] text-gray-500 font-sans">
                  never blocked
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Settings Change History Audit */}
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-gray-950/60">
          <div className="p-3 bg-gray-900/60 border-b border-gray-800 flex items-center gap-2 text-xs font-semibold text-gray-300">
            <History size={14} className="text-gray-400" />
            <span>AUDIT TRAIL: RECENT SETTINGS MODIFICATIONS</span>
          </div>
          <div className="divide-y divide-gray-800/60 text-xs">
            {history.length > 0 ? (
              history.slice(0, 10).map((h, idx) => (
                <div key={idx} className="p-3 flex items-center justify-between text-gray-400">
                  <div className="space-y-0.5">
                    <span className="text-gray-200 font-semibold">
                      {h.updated_by || "admin"} changed {h.key}
                    </span>
                    <span className="text-gray-500 block text-[11px]">
                      {JSON.stringify(h.old_value)} → {JSON.stringify(h.new_value)}
                      {h.reason ? " — " + h.reason : ""}
                    </span>
                  </div>
                  <span className="text-gray-500 text-[11px]">
                    {h.updated_at ? new Date(h.updated_at).toLocaleString() : ""}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-gray-500 text-xs">
                No administrative changes recorded yet. Default baseline active.
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;
