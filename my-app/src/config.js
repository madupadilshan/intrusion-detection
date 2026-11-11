/**
 * Central Backend Configuration for IP Camera IoT IDS Dashboard
 * Group 03 - University of Sri Jayewardenepura
 * 
 * Replaces disjoint legacy ports (5002, 5005, 5006, 5007, 5012)
 * with a single unified backend endpoint.
 */

// Without REACT_APP_API_URL the API is on port 5000 of the same machine that served the page.
// So the dashboard works from the admin PC (http://<sensor-ip>:5000) and on this PC
// (http://localhost:3000 or :5000). A fixed "localhost" would point the admin PC at itself.
const pageHost = typeof window !== "undefined" && window.location && window.location.hostname
  ? `${window.location.protocol}//${window.location.hostname}:5000`
  : "http://localhost:5000";
export const API_URL = process.env.REACT_APP_API_URL || pageHost;
export const WS_URL = process.env.REACT_APP_WS_URL || API_URL;

const config = {
  API_URL,
  WS_URL,
};

export default config;
