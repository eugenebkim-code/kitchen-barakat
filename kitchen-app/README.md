# Kitchen Barakat — Windows Kitchen Client

Standalone Electron desktop app for the kitchen. Connects to the backend's
`/ws/kitchen` WebSocket, and shows a high-contrast alert with a looping
voice announcement ("У вас новый заказ в Телеграм") whenever a new order
comes in.

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

- The app launches maximized and connects automatically.
- A new order plays the selected alert sound on loop and shows order
  details (phone, address, comment, items, total, receipt screenshot)
  until the kitchen clicks **"Заказ принят / Остановить оповещение"**.
- Multiple orders queue up; acknowledging one shows the next (the sound
  keeps looping until the queue is empty).
- **🔊 Звук** in the status bar opens the sound picker: three built-in
  presets (a neural-TTS voice announcement, a bell chime, a classic
  siren — each has a ▶️ preview), or **📁 Загрузить свою мелодию** to pick
  any local mp3/wav/ogg/m4a file. The choice is copied into the app's
  user-data folder and persists across restarts.
  - To change the built-in voice phrase: regenerate
    `sound/preset-voice.wav` with [Piper TTS](https://github.com/rhasspy/piper)
    (`pip install piper-tts`, download a `ru_RU-*` voice model, then
    `echo "your text" | python -m piper -m <model>.onnx -f sound/preset-voice.wav`).
- If the connection drops, it retries with backoff: 1s, 2s, 5s, then 10s
  from then on. The status dot in the top-left shows connection state.
- The window opens maximized but is a normal, resizable window - drag an
  edge/corner to resize it like any other app.
- **📌 Поверх окон** checkbox in the status bar toggles always-on-top
  (checked by default, so a new order alert is never hidden behind another
  window). Uncheck it if you need the kitchen display to behave like a
  normal background window.
- **🗕 Свернуть** / **✕ Закрыть** in the status bar minimize or quit (quit
  asks for confirmation first). **Ctrl+Shift+Q** also quits, as a keyboard
  backup.
