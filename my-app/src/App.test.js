import { API_URL, WS_URL } from "./config";

jest.mock("axios", () => {
  const mockAxios = {
    create: jest.fn(() => ({
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() },
      },
      get: jest.fn().mockResolvedValue({ data: {} }),
      post: jest.fn().mockResolvedValue({ data: {} }),
      patch: jest.fn().mockResolvedValue({ data: {} }),
      delete: jest.fn().mockResolvedValue({ data: {} }),
    })),
    get: jest.fn().mockResolvedValue({ data: {} }),
    post: jest.fn().mockResolvedValue({ data: {} }),
  };
  return mockAxios;
});

// Mock socket.io-client
jest.mock("socket.io-client", () => ({
  io: jest.fn(() => ({
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
    connected: true,
  })),
}));

describe("Frontend Dashboard Pages & Suite Verification", () => {
  test("central configuration provides valid unified backend endpoints", () => {
    expect(API_URL).toBeDefined();
    expect(WS_URL).toBeDefined();
    expect(API_URL).toBe("http://localhost:5000");
  });

  test("all 7 canonical dashboard page components are properly exported", () => {
    const Overview = require("./pages/Overview").default;
    const LiveAlerts = require("./pages/LiveAlerts").default;
    const AttackHistory = require("./pages/AttackHistory").default;
    const Devices = require("./pages/Devices").default;
    const Blocklist = require("./pages/Blocklist").default;
    const Settings = require("./pages/Settings").default;
    const LogExport = require("./pages/LogExport").default;

    expect(Overview).toBeDefined();
    expect(LiveAlerts).toBeDefined();
    expect(AttackHistory).toBeDefined();
    expect(Devices).toBeDefined();
    expect(Blocklist).toBeDefined();
    expect(Settings).toBeDefined();
    expect(LogExport).toBeDefined();
  });
});
