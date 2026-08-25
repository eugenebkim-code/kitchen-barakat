const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  minimizeApp: () => ipcRenderer.send('kitchen-app:minimize'),
  quitApp: () => ipcRenderer.send('kitchen-app:quit'),
});
