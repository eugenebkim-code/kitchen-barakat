// Copy this file to config.js and fill in your real backend details.
// config.js is gitignored on purpose - it holds your KITCHEN_WS_SECRET.
window.KITCHEN_CONFIG = {
  // Base WebSocket URL of the backend, WITHOUT the ?token= query string.
  // Use wss:// for a production (HTTPS) backend, ws:// only for local testing.
  WS_URL: "wss://your-backend.up.railway.app/ws/kitchen",

  // Must match KITCHEN_WS_SECRET on the backend.
  WS_TOKEN: "your_kitchen_ws_secret",

  // Base HTTP(S) URL of the backend, used to resolve receipt screenshot
  // paths like "/uploads/receipt_x.jpg" into full image URLs.
  API_BASE_URL: "https://your-backend.up.railway.app"
};
