import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Overview from "./pages/Overview";
import LiveAlerts from "./pages/LiveAlerts";
import AttackHistory from "./pages/AttackHistory";
import Devices from "./pages/Devices";
import Blocklist from "./pages/Blocklist";
import Settings from "./pages/Settings";
import LogExport from "./pages/LogExport";

// Protected Route wrapper checking JWT token presence
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public Login */}
        <Route path="/login" element={<Login />} />

        {/* 7 Canonical Dashboard Pages (Proposal Table 8 & Section 3.6) */}
        <Route
          path="/overview"
          element={
            <ProtectedRoute>
              <Overview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <LiveAlerts />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <AttackHistory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/devices"
          element={
            <ProtectedRoute>
              <Devices />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mitigations"
          element={
            <ProtectedRoute>
              <Blocklist />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/export"
          element={
            <ProtectedRoute>
              <LogExport />
            </ProtectedRoute>
          }
        />

        {/* Backward Compatibility Redirects */}
        <Route path="/dashboard" element={<Navigate to="/overview" replace />} />
        <Route path="/attack-history" element={<Navigate to="/history" replace />} />
        <Route path="/iot-dashboard" element={<Navigate to="/devices" replace />} />
        <Route path="/IOTDetails" element={<Navigate to="/alerts" replace />} />

        {/* Root & Catch-all */}
        <Route path="/" element={<Navigate to="/overview" replace />} />
        <Route path="*" element={<Navigate to="/overview" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
