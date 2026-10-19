import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { User, Mail, Lock, Key, Terminal } from 'lucide-react';
import MatrixEffect from './MatrixEffect';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    admin_password: ""
  });
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
      setMessage("Verifying credentials...");
      
      // Simulate security scan
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Proceed with actual registration
      await axios.post("http://127.0.0.1:5002/register", formData);
      
      setMessage("Registration successful. Initializing user account...");
      setTimeout(() => navigate("/login"), 2000); // Redirect after showing success message
    } catch (error) {
      if (error.response && error.response.status === 403) {
        setMessage("Access denied. Invalid admin credentials.");
      } else {
        setMessage("Registration failed. Security violation detected.");
      }
    } finally {
      setIsLoading(false);
      setTimeout(() => setSecurityScan(false), 1500);
    }
  };

  return (
    <div className="register-container">
      {/* Matrix-like background */}
      <MatrixEffect />

      <div className="register-card-container">
        {/* Security shield logo */}
        <div className="shield-logo">
          <Key className="shield-icon" />
        </div>

        <div className="register-card">
          <h2 className="register-title">
            <Terminal className="terminal-icon" />
            OPERATOR REGISTRATION
          </h2>

          {message && (
            <div className={`message ${message.includes('successful') ? 'success' : message.includes('Verifying') ? 'scanning' : 'error'}`}>
              {message}
            </div>
          )}

          {securityScan && (
            <div className="security-scan">
              <div className="scan-line"></div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="register-form">
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
              <Mail className="input-icon" />
              <input
                type="email"
                name="email"
                placeholder="SECURE EMAIL"
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

            <div className="input-group">
              <Key className="input-icon" />
              <input
                type="password"
                name="admin_password"
                placeholder="ADMIN VERIFICATION"
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
                  <span>PROCESSING</span>
                  <span className="loading-dots">...</span>
                </span>
              ) : (
                'REGISTER'
              )}
            </button>
          </form>

          <div className="footer-text">
            SECURE REGISTRATION TERMINAL v2.5
          </div>
          <p className="login-link">Already authorized? <a href="/login">Access terminal</a></p>
        </div>
      </div>
    </div>
  );
};

export default Register;