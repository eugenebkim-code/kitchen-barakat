const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  minimizeApp: () => ipcRenderer.send('kitchen-app:minimize'),
  quitApp: () => ipcRenderer.send('kitchen-app:quit'),
  setAlwaysOnTop: (enabled) => ipcRenderer.send('kitchen-app:set-always-on-top', enabled),
  getAlwaysOnTop: () => ipcRenderer.invoke('kitchen-app:get-always-on-top'),
});
