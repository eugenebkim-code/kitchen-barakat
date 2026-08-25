const { app, BrowserWindow, powerSaveBlocker, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    fullscreen: true,
    kiosk: true,
    backgroundColor: '#0a0a0f',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.setMenuBarVisibility(false);
  mainWindow.setAlwaysOnTop(true, 'screen-saver');
  mainWindow.loadFile('index.html');

  // This is a kitchen alert board - the screen must never sleep or the
  // siren/order alert could go unnoticed.
  powerSaveBlocker.start('prevent-display-sleep');

  // Kiosk mode intentionally blocks normal window controls (Alt+F4, close
  // button). Keep a hidden keyboard escape hatch alongside the on-screen
  // buttons for maintenance / updating config.js.
  mainWindow.webContents.on('before-input-event', (_event, input) => {
    if (input.control && input.shift && input.key.toLowerCase() === 'q') {
      app.quit();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.on('kitchen-app:minimize', () => {
  if (!mainWindow) return;
  // Kiosk mode has to be turned off before the window can actually minimize.
  mainWindow.setKiosk(false);
  mainWindow.setFullScreen(false);
  mainWindow.minimize();
});

ipcMain.on('kitchen-app:quit', () => {
  app.quit();
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
