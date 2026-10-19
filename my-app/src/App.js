import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Register from "./components/Register";
import Login from "./components/Login";
import CyberDetails from "./pages/CyberDetails";
import TraditionalDetails from "./pages/TraditionalDetails";
import Dashboard from "./components/Dashboard";
import IOTDetails from "./pages/IOTDetails";
import AttackHistory from "./pages/AttackHistory";
import AttackHistoryCICIDS from "./pages/AttackHistoryCICIDS";
import KDDAttackHistory from "./pages/KDDAttackHistory";
import IoTDevicesDashboard from "./pages/IoTDevicesDashboard";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/IOTDetails" element={<IOTDetails />} />
        <Route path="/CyberDetails" element={<CyberDetails />} />
        <Route path="/TraditionalDetails" element={<TraditionalDetails />} />
        <Route path="/attack-history" element={<AttackHistory />} />
        <Route path="/attack-history-cicids" element={<AttackHistoryCICIDS />} />
        <Route path="/attack-history-kdd" element={<KDDAttackHistory />} />
        <Route path="/iot-dashboard" element={<IoTDevicesDashboard />} />
        
      </Routes>
    </Router>
  );
};

export default App;


