const { app, BrowserWindow, powerSaveBlocker, ipcMain } = require('electron');
const path = require('path');

let mainWindow;
const DEFAULT_ALWAYS_ON_TOP = true;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 640,
    minHeight: 480,
    resizable: true,
    backgroundColor: '#0a0a0f',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.setMenuBarVisibility(false);
  mainWindow.maximize();
  mainWindow.setAlwaysOnTop(DEFAULT_ALWAYS_ON_TOP, 'screen-saver');
  mainWindow.loadFile('index.html');

  // This is a kitchen alert board - the screen must never sleep or the
  // announcement could go unnoticed.
  powerSaveBlocker.start('prevent-display-sleep');

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
  mainWindow?.minimize();
});

ipcMain.on('kitchen-app:quit', () => {
  app.quit();
});

ipcMain.on('kitchen-app:set-always-on-top', (_event, enabled) => {
  mainWindow?.setAlwaysOnTop(!!enabled, enabled ? 'screen-saver' : undefined);
});

ipcMain.handle('kitchen-app:get-always-on-top', () => {
  return mainWindow ? mainWindow.isAlwaysOnTop() : DEFAULT_ALWAYS_ON_TOP;
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
