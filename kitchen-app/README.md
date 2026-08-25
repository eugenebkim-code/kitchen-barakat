# Kitchen Barakat — Windows Kitchen Client

Standalone Electron desktop app for the kitchen. Connects to the backend's
`/ws/kitchen` WebSocket, and shows a full-screen, high-contrast alert with a
looping siren whenever a new order comes in.

## Setup

1. Install dependencies:
   ```
   npm install
   ```
2. Create your config from the template and fill in real values:
   ```
   copy config.example.js config.js
   ```
   - `WS_URL` — the backend's WebSocket URL, e.g. `wss://your-backend.up.railway.app/ws/kitchen`
   - `WS_TOKEN` — must match `KITCHEN_WS_SECRET` on the backend
   - `API_BASE_URL` — the backend's HTTPS URL, used to resolve receipt screenshot links

   `config.js` is gitignored — it's never committed since it holds a secret.

## Run (development)

```
npm start
```

## Build the .exe

```
npm run build
```

Output lands in `dist/` (installer via NSIS). Run this on the machine
you'll actually deploy from — `config.js` gets bundled into the build.

> **Windows note:** `electron-builder` downloads a small cross-platform
> tool bundle (`winCodeSign`) that contains symlinks, even for an unsigned
> Windows-only build. Creating those symlinks needs either **Developer
> Mode** enabled (Settings → Privacy & security → For developers) or
> running the build from an **Administrator** terminal - otherwise you'll
> see `Cannot create symbolic link: A required privilege is not held by
> the client`. This is an `electron-builder` limitation, not specific to
> this app.

## Using it

- The app launches full-screen in kiosk mode and connects automatically.
- A new order plays the alarm on loop and shows order details (phone,
  address, comment, items, total, receipt screenshot) until the kitchen
  clicks **"Заказ принят / Отключить сирену"**.
- Multiple orders queue up; acknowledging one shows the next (siren keeps
  going until the queue is empty).
- If the connection drops, it retries with backoff: 1s, 2s, 5s, then 10s
  from then on. The status dot in the top-left shows connection state.
- Kiosk mode blocks the usual window controls on purpose (this is meant to
  stay full-screen on a kitchen display). To close it for maintenance,
  press **Ctrl+Shift+Q**.
