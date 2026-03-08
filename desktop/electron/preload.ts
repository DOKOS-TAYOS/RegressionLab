import { contextBridge, ipcRenderer } from "electron";

const desktopApi = {
  getBackendBaseUrl: (): Promise<string> => ipcRenderer.invoke("app:get-backend-url"),
  relaunch: (): Promise<void> => ipcRenderer.invoke("app:relaunch"),
  openDataFile: (): Promise<string | null> => ipcRenderer.invoke("dialog:open-data-file"),
  openDataFiles: (): Promise<string[]> => ipcRenderer.invoke("dialog:open-data-files"),
  saveFile: (options: {
    defaultPath?: string;
    filters?: Array<{ name: string; extensions: string[] }>;
  }): Promise<string | null> => ipcRenderer.invoke("dialog:save-file", options),
  openExternal: (url: string): Promise<void> => ipcRenderer.invoke("shell:open-external", url),
  revealPath: (targetPath: string): Promise<void> => ipcRenderer.invoke("shell:reveal-path", targetPath),
};

contextBridge.exposeInMainWorld("desktopApi", desktopApi);
