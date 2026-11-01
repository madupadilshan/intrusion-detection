import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  AlertTriangle,
  History,
  Camera,
  ShieldAlert,
  Settings,
  FileText,
  LogOut,
  Menu,
  X,
  Radio,
  User,
} from "lucide-react";
import { getSocket } from "../services/socket";

const navItems = [
  { name: "Overview", path: "/overview", icon: LayoutDashboard },
  { name: "Live Alerts", path: "/alerts", icon: AlertTriangle },
  { name: "Attack History", path: "/history", icon: History },
  { name: "Devices & Scans", path: "/devices", icon: Camera },
  { name: "Blocklist / Mitigations", path: "/mitigations", icon: ShieldAlert },
  { name: "Settings", path: "/settings", icon: Settings },
  { name: "Logs & Export", path: "/export", icon: FileText },
];

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState("admin");

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) {
        const u = JSON.parse(stored);
        setCurrentUser(u.username || "admin");
      }
    } catch {
      setCurrentUser("admin");
    }

    const socket = getSocket();
    if (socket) {
      if (socket.connected) setIsConnected(true);
      const onConnect = () => setIsConnected(true);
      const onDisconnect = () => setIsConnected(false);

      socket.on("connect", onConnect);
      socket.on("disconnect", onDisconnect);

      return () => {
        socket.off("connect", onConnect);
        socket.off("disconnect", onDisconnect);
      };
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-black text-gray-100 flex flex-col font-mono selection:bg-emerald-500 selection:text-black">
      {/* Top Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-1.5 rounded text-gray-400 hover:text-white hover:bg-gray-800"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center gap-2">
            <Radio className={isConnected ? "text-emerald-400 animate-pulse" : "text-gray-600"} size={20} />
            <span className="font-bold tracking-wider text-sm md:text-base text-gray-200">
              IP-CAMERA <span className="text-emerald-400">IOT IDS</span>
            </span>
            <span className="hidden sm:inline-block text-xs text-gray-500 border border-gray-800 px-1.5 py-0.5 rounded">
              v2.5 SOC
            </span>
          </div>
        </div>

        {/* Telemetry status & User Controls */}
        <div className="flex items-center gap-3 md:gap-5 text-xs">
          <div className="hidden sm:flex items-center gap-1.5">
            <span
              className={`inline-block w-2 h-2 rounded-full ${
                isConnected ? "bg-emerald-400 shadow-[0_0_8px_#10b981]" : "bg-red-500"
              }`}
            />
            <span className="text-gray-400">
              {isConnected ? "SOCKET.IO LIVE" : "TELEMETRY OFFLINE"}
            </span>
          </div>

          <div className="flex items-center gap-2 border-l border-gray-800 pl-3">
            <div className="flex items-center gap-1.5 text-gray-300">
              <User size={14} className="text-emerald-400" />
              <span className="font-semibold text-gray-200">{currentUser}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 px-2.5 py-1 bg-red-950/60 hover:bg-red-900 border border-red-800/80 text-red-300 rounded transition"
              title="Logout session"
            >
              <LogOut size={13} />
              <span className="hidden md:inline">EXIT</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Body with Sidebar + Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Desktop Sidebar */}
        <aside className="hidden md:flex flex-col w-64 border-r border-gray-800 bg-gray-950/40 p-3 space-y-1">
          <div className="px-3 py-2 text-[11px] font-semibold text-gray-500 tracking-wider">
            OPERATIONAL NAVIGATION
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded text-xs transition ${
                  active
                    ? "bg-emerald-950/40 text-emerald-300 border border-emerald-500/40 font-semibold"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
                }`}
              >
                <Icon size={16} className={active ? "text-emerald-400" : "text-gray-500"} />
                <span>{item.name}</span>
              </Link>
            );
          })}

          <div className="mt-auto pt-4 border-t border-gray-900 text-[10px] text-gray-600 px-3">
            USJP • BICT HONOURS • GROUP 03
          </div>
        </aside>

        {/* Mobile Slide-down Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-[53px] inset-x-0 bg-gray-950 border-b border-gray-800 z-40 p-3 space-y-1 shadow-2xl">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded text-sm ${
                    active
                      ? "bg-emerald-950/60 text-emerald-300 border border-emerald-500/40 font-semibold"
                      : "text-gray-300 hover:bg-gray-900"
                  }`}
                >
                  <Icon size={18} className={active ? "text-emerald-400" : "text-gray-500"} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        )}

        {/* Content Pane */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gradient-to-b from-black via-gray-950 to-black">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
