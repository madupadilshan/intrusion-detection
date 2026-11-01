/**
 * Authenticated Socket.IO Client Manager
 * Group 03 - University of Sri Jayewardenepura
 * 
 * Establishes real-time push telemetry connection with unified Flask backend
 * passing JWT token in handshake authentication payload.
 */

import { io } from "socket.io-client";
import { WS_URL } from "../config";

let socketInstance = null;

export const getSocket = () => {
  const token = localStorage.getItem("token");
  if (!token) {
    if (socketInstance) {
      socketInstance.disconnect();
      socketInstance = null;
    }
    return null;
  }

  if (!socketInstance || socketInstance.disconnected) {
    socketInstance = io(WS_URL, {
      auth: { token },
      transports: ["websocket", "polling"],
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
    });

    socketInstance.on("connect_error", (err) => {
      console.warn("Socket.IO connection error:", err.message);
    });
  }

  return socketInstance;
};

export const disconnectSocket = () => {
  if (socketInstance) {
    socketInstance.disconnect();
    socketInstance = null;
  }
};

export default getSocket;
