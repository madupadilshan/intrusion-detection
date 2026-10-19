import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Shield, ShieldAlert, Lock, User, Terminal } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [securityScan, setSecurityScan] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setSecurityScan(true);
    
    try {
      // First show the security scan message
      setMessage("Scanning for security threats...");
      
      // Simulate security scan
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Proceed with actual login
      const res = await axios.post("http://127.0.0.1:5002/login", formData);
      localStorage.setItem("token", res.data.token); // Store JWT token
      
      setMessage("Access granted. Initializing security protocols...");
      setTimeout(() => navigate("/dashboard"), 1500); // Redirect after showing success message
    } catch (error) {
      setMessage(error.response?.data?.message || "Access denied. Security violation detected.");
    } finally {
      setIsLoading(false);
      setTimeout(() => setSecurityScan(false), 1500);
    }
  };

  return (
    <div className="login-container">
      {/* Matrix-like background */}
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
            IOT INTRUSION DETECTION
          </h2>

          {message && (
            <div className={`message ${message.includes('granted') ? 'success' : message.includes('Scanning') ? 'scanning' : 'error'}`}>
              {message}
            </div>
          )}

          {securityScan && (
            <div className="security-scan">
              <div className="scan-line"></div>
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
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <div className="input-group">
              <Lock className="input-icon" />
              <input
                type="password"
                name="password"
                placeholder="ACCESS CODE"
                required
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={isLoading ? 'loading' : ''}
            >
              {isLoading ? (
                <span className="loading-text">
                  <span>VERIFYING</span>
                  <span className="loading-dots">...</span>
                </span>
              ) : (
                'AUTHENTICATE'
              )}
            </button>
          </form>

          <div className="footer-text">
            SECURE ACCESS TERMINAL v2.5
          </div>
          <p className="register-link">Need access? <a href="/register">Request credentials</a></p>
        </div>
      </div>
    </div>
  );
};

export default Login;