/// <reference types="vite/client" />

interface DesktopBridge {
  getBackendBaseUrl(): Promise<string>;
  relaunch(): Promise<void>;
  openDataFile(): Promise<string | null>;
  openDataFiles(): Promise<string[]>;
  saveFile(options: {
    defaultPath?: string;
    filters?: Array<{ name: string; extensions: string[] }>;
  }): Promise<string | null>;
  openExternal(url: string): Promise<void>;
  revealPath(targetPath: string): Promise<void>;
  minimize(): Promise<void>;
  toggleMaximize(): Promise<boolean>;
  close(): Promise<void>;
}

declare global {
  interface Window {
    desktopApi: DesktopBridge;
  }
}

export {};
