import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, ShieldAlert, Lock, User, Terminal } from "lucide-react";
import MatrixEffect from "./MatrixEffect";
import apiClient from "../services/api";
import "./Login.css";

const Login = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    try {
      const res = await apiClient.post("/api/auth/login", formData);
      if (res.data && res.data.token) {
        localStorage.setItem("token", res.data.token);
        localStorage.setItem(
          "user",
          JSON.stringify(res.data.user || { username: formData.username })
        );
        setMessage("Authentication successful. Loading security dashboard...");
        setTimeout(() => navigate("/overview"), 600);
      } else {
        setMessage(res.data?.message || "Invalid authentication response.");
      }
    } catch (error) {
      const errorMsg =
        error.response?.data?.error ||
        error.response?.data?.message ||
        "Access denied. Invalid credentials or backend unavailable.";
      setMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Matrix background effect */}
      <MatrixEffect />

      <div className="login-card-container">
        {/* Security shield logo */}
        <div className="shield-logo">
          {isLoading ? (
            <ShieldAlert className="shield-icon alert" />
          ) : (
            <Shield className="shield-icon" />
          )}
        </div>

        <div className="login-card">
          <h2 className="login-title">
            <Terminal className="terminal-icon" />
            IP CAMERA IOT IDS
          </h2>
          <p style={{ color: "#9ca3af", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Real-Time Network Intrusion Detection & Response Terminal
          </p>

          {message && (
            <div
              className={`message ${
                message.includes("successful") ? "success" : "error"
              }`}
            >
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div className="input-group">
              <User className="input-icon" />
              <input
                type="text"
                name="username"
                placeholder="OPERATOR ID"
                required
                value={formData.username}
                onChange={handleChange}
                disabled={isLoading}
                autoComplete="username"
              />
            </div>

            <div className="input-group">
              <Lock className="input-icon" />
              <input
                type="password"
                name="password"
                placeholder="ACCESS CODE"
                required
                value={formData.password}
                onChange={handleChange}
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={isLoading ? "loading" : ""}
            >
              {isLoading ? (
                <span className="loading-text">
                  <span>AUTHENTICATING</span>
                  <span className="loading-dots">...</span>
                </span>
              ) : (
                "AUTHENTICATE"
              )}
            </button>
          </form>

          <div className="footer-text">
            UNIVERSITY OF SRI JAYEWARDENEPURA • BICT GROUP 03
          </div>
          <p className="register-link" style={{ fontSize: "0.8rem", color: "#6b7280" }}>
            Authorized Personnel Only • Contact System Administrator for Access
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
