/**
 * Authenticated API Service Client
 * Group 03 - University of Sri Jayewardenepura
 * 
 * Provides unified Axios instance with:
 * 1. Automatic Authorization: Bearer <token> injection from localStorage
 * 2. Automatic 401 Unauthorized interception and redirect to /login
 * 3. Base URL mapped to central config
 */

import axios from "axios";
import { API_URL } from "../config";

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach JWT bearer token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: handle 401 unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear expired credentials
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Redirect to login if not already there
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Attack events from the API and from Socket.IO carry `event_id` (and `_id`), not `id`.
// Give every event an `id` so pages can find, confirm and update it.
export const withEventId = (event) => ({
  ...event,
  id: event?.event_id || event?.id || event?._id,
});
