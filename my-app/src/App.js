import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import IOTDetails from "./pages/IOTDetails";
import AttackHistory from "./pages/AttackHistory";
import IoTDevicesDashboard from "./pages/IoTDevicesDashboard";

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
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Core Routes */}
        <Route
          path="/overview"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={<Navigate to="/overview" replace />}
        />
        <Route
          path="/IOTDetails"
          element={
            <ProtectedRoute>
              <IOTDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <IOTDetails />
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
          path="/attack-history"
          element={<Navigate to="/history" replace />}
        />
        <Route
          path="/devices"
          element={
            <ProtectedRoute>
              <IoTDevicesDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/iot-dashboard"
          element={<Navigate to="/devices" replace />}
        />

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/overview" replace />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/overview" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
