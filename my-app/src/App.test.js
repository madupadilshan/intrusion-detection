import { API_URL, WS_URL } from "./config";

test("central configuration provides valid unified backend endpoints", () => {
  expect(API_URL).toBeDefined();
  expect(WS_URL).toBeDefined();
  expect(API_URL).toBe("http://localhost:5000");
});
