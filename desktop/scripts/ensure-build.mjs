import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const desktopRoot = process.cwd();
const repoRoot = path.resolve(desktopRoot, "..");

const sourceTargets = [
  path.join(desktopRoot, "src"),
  path.join(desktopRoot, "electron"),
  path.join(repoRoot, "src", "locales"),
  path.join(desktopRoot, "package.json"),
  path.join(desktopRoot, "tsconfig.json"),
  path.join(desktopRoot, "electron.tsconfig.json"),
  path.join(desktopRoot, "vite.config.ts"),
];

const outputTargets = [
  path.join(desktopRoot, "dist", "index.html"),
  path.join(desktopRoot, "dist-electron", "electron", "main.js"),
  path.join(desktopRoot, "dist-electron", "electron", "preload.js"),
];

function getNewestMtimeMs(targetPath) {
  if (!fs.existsSync(targetPath)) {
    return 0;
  }

  const stats = fs.statSync(targetPath);
  if (!stats.isDirectory()) {
    return stats.mtimeMs;
  }

  return fs.readdirSync(targetPath, { withFileTypes: true }).reduce(
    (latestMtime, entry) =>
      Math.max(latestMtime, getNewestMtimeMs(path.join(targetPath, entry.name))),
    stats.mtimeMs,
  );
}

function getOldestOutputMtimeMs() {
  let oldestMtime = Number.POSITIVE_INFINITY;

  for (const outputPath of outputTargets) {
    if (!fs.existsSync(outputPath)) {
      return null;
    }

    oldestMtime = Math.min(oldestMtime, fs.statSync(outputPath).mtimeMs);
  }

  return oldestMtime;
}

function runBuild() {
  const npmCliPath = process.env.npm_execpath;
  const result = npmCliPath
    ? spawnSync(process.execPath, [npmCliPath, "run", "build"], {
        cwd: desktopRoot,
        stdio: "inherit",
      })
    : spawnSync(process.platform === "win32" ? "npm.cmd" : "npm", ["run", "build"], {
        cwd: desktopRoot,
        stdio: "inherit",
      });

  if (result.error) {
    console.error("[desktop] Failed to start the desktop build.", result.error);
  }

  if (typeof result.status === "number") {
    process.exit(result.status);
  }

  process.exit(1);
}

const newestSourceMtime = sourceTargets.reduce(
  (latestMtime, sourcePath) => Math.max(latestMtime, getNewestMtimeMs(sourcePath)),
  0,
);
const oldestOutputMtime = getOldestOutputMtimeMs();
const buildMissing = oldestOutputMtime === null;
const buildOutdated = oldestOutputMtime !== null && newestSourceMtime > oldestOutputMtime;

if (buildMissing || buildOutdated) {
  console.log(
    buildMissing
      ? "[desktop] Build artifacts not found. Running a one-time build before launch..."
      : "[desktop] Frontend sources changed. Rebuilding desktop app before launch...",
  );
  runBuild();
}

console.log("[desktop] Existing build is up to date.");
