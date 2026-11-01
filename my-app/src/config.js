/**
 * Central Backend Configuration for IP Camera IoT IDS Dashboard
 * Group 03 - University of Sri Jayewardenepura
 * 
 * Replaces disjoint legacy ports (5002, 5005, 5006, 5007, 5012)
 * with a single unified backend endpoint.
 */

export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";
export const WS_URL = process.env.REACT_APP_WS_URL || API_URL;

const config = {
  API_URL,
  WS_URL,
};

export default config;
