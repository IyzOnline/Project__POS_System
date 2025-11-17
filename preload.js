const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  sayHello: () => ipcRenderer.invoke('say-hello'),
})