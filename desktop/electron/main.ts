import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import http from "node:http";
import net from "node:net";
import path from "node:path";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";

function getDevServerUrl(): string | null {
  const argument = process.argv.find((item) => item.startsWith("--dev-server-url="));
  if (argument) {
    return argument.slice("--dev-server-url=".length);
  }
  return process.env.VITE_DEV_SERVER_URL ?? null;
}

const desktopRoot = path.resolve(__dirname, "..", "..");
const repoRoot = path.resolve(desktopRoot, "..");
const srcPath = path.join(repoRoot, "src");

let mainWindow: BrowserWindow | null = null;
let sidecarProcess: ChildProcessWithoutNullStreams | null = null;
let backendBaseUrl = "";
let isQuitting = false;

function getPythonExecutable(): string {
  if (process.env.REGRESSIONLAB_PYTHON) {
    return process.env.REGRESSIONLAB_PYTHON;
  }
  const venvPython =
    process.platform === "win32"
      ? path.join(repoRoot, ".venv", "Scripts", "python.exe")
      : path.join(repoRoot, ".venv", "bin", "python");
  return venvPython;
}

function getFreePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close(() => {
        if (address && typeof address === "object") {
          resolve(address.port);
          return;
        }
        reject(new Error("Unable to resolve a free port"));
      });
    });
  });
}

function waitForSidecar(url: string, attempts = 60): Promise<void> {
  return new Promise((resolve, reject) => {
    let tries = 0;
    const tick = () => {
      tries += 1;
      const req = http.get(`${url}/health`, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          resolve();
          return;
        }
        if (tries >= attempts) {
          reject(new Error(`Desktop API failed with status ${res.statusCode}`));
          return;
        }
        setTimeout(tick, 250);
      });
      req.on("error", () => {
        if (tries >= attempts) {
          reject(new Error("Desktop API did not become ready in time"));
          return;
        }
        setTimeout(tick, 250);
      });
    };
    tick();
  });
}

async function startSidecar(): Promise<void> {
  const port = await getFreePort();
  backendBaseUrl = `http://127.0.0.1:${port}`;

  const pythonPath = getPythonExecutable();
  const env = {
    ...process.env,
    PYTHONPATH: process.env.PYTHONPATH
      ? `${srcPath}${path.delimiter}${process.env.PYTHONPATH}`
      : srcPath,
  };

  sidecarProcess = spawn(
    pythonPath,
    ["-m", "regressionlab.desktop_api", "--port", String(port)],
    {
      cwd: repoRoot,
      env,
      stdio: "pipe",
    },
  );

  sidecarProcess.stdout.on("data", (chunk) => {
    process.stdout.write(`[desktop-api] ${chunk}`);
  });
  sidecarProcess.stderr.on("data", (chunk) => {
    process.stderr.write(`[desktop-api] ${chunk}`);
  });
  sidecarProcess.on("exit", (code) => {
    if (!isQuitting) {
      console.error(`Desktop API exited unexpectedly with code ${code}`);
    }
  });

  await waitForSidecar(backendBaseUrl);
}

function stopSidecar(): void {
  if (!sidecarProcess || sidecarProcess.killed) {
    return;
  }
  sidecarProcess.kill();
  sidecarProcess = null;
}

async function createWindow(): Promise<void> {
  const devServerUrl = getDevServerUrl();
  mainWindow = new BrowserWindow({
    width: 1520,
    height: 980,
    minWidth: 1180,
    minHeight: 780,
    backgroundColor: "#111111",
    titleBarStyle: "hiddenInset",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  if (devServerUrl) {
    await mainWindow.loadURL(devServerUrl);
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    await mainWindow.loadFile(path.join(desktopRoot, "dist", "index.html"));
  }
}

app.on("before-quit", () => {
  isQuitting = true;
  stopSidecar();
});

app.whenReady().then(async () => {
  await startSidecar();
  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

ipcMain.handle("app:get-backend-url", async () => backendBaseUrl);
ipcMain.handle("app:relaunch", async () => {
  app.relaunch();
  app.exit(0);
});

ipcMain.handle("dialog:open-data-file", async () => {
  const options = {
    properties: ["openFile"] as Array<"openFile">,
    defaultPath: path.join(repoRoot, "input"),
    filters: [
      { name: "Data files", extensions: ["csv", "txt", "xlsx"] },
      { name: "CSV", extensions: ["csv"] },
      { name: "Text", extensions: ["txt"] },
      { name: "Excel", extensions: ["xlsx"] },
    ],
  };
  const result = mainWindow
    ? await dialog.showOpenDialog(mainWindow, options)
    : await dialog.showOpenDialog(options);
  return result.canceled ? null : result.filePaths[0] ?? null;
});

ipcMain.handle("dialog:open-data-files", async () => {
  const options = {
    properties: ["openFile", "multiSelections"] as Array<"openFile" | "multiSelections">,
    defaultPath: path.join(repoRoot, "input"),
    filters: [
      { name: "Data files", extensions: ["csv", "txt", "xlsx"] },
      { name: "CSV", extensions: ["csv"] },
      { name: "Text", extensions: ["txt"] },
      { name: "Excel", extensions: ["xlsx"] },
    ],
  };
  const result = mainWindow
    ? await dialog.showOpenDialog(mainWindow, options)
    : await dialog.showOpenDialog(options);
  return result.canceled ? [] : result.filePaths;
});

ipcMain.handle(
  "dialog:save-file",
  async (_event, options: { defaultPath?: string; filters?: Array<{ name: string; extensions: string[] }> }) => {
    const dialogOptions = {
      defaultPath: options.defaultPath,
      filters: options.filters,
    };
    const result = mainWindow
      ? await dialog.showSaveDialog(mainWindow, dialogOptions)
      : await dialog.showSaveDialog(dialogOptions);
    return result.canceled ? null : result.filePath ?? null;
  },
);

ipcMain.handle("shell:open-external", async (_event, url: string) => {
  await shell.openExternal(url);
});

ipcMain.handle("shell:reveal-path", async (_event, targetPath: string) => {
  shell.showItemInFolder(targetPath);
});
