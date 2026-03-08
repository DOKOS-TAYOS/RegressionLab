import { useEffect } from "react";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "@/components/Shell";
import { HomePage } from "@/pages/HomePage";
import { FitWorkspacePage } from "@/pages/FitWorkspacePage";
import { DataLabPage } from "@/pages/DataLabPage";
import { HelpPage } from "@/pages/HelpPage";
import { ConfigPage } from "@/pages/ConfigPage";
import { useAppStore } from "@/store/appStore";
import { translate } from "@/i18n";

function applyThemeVariables(theme: NonNullable<ReturnType<typeof useAppStore.getState>["bootstrap"]>["theme"]) {
  const root = document.documentElement;
  root.style.setProperty("--bg-base", theme.colors.bg);
  root.style.setProperty("--fg-base", theme.colors.fg);
  root.style.setProperty("--bg-panel", theme.colors.fieldBg);
  root.style.setProperty("--accent-main", theme.colors.accept);
  root.style.setProperty("--accent-alt", theme.colors.accent);
  root.style.setProperty("--danger", theme.colors.cancel);
  root.style.setProperty("--hover-bg", theme.colors.hoverBg);
  root.style.setProperty("--button-bg", theme.colors.buttonBg);
  root.style.setProperty("--text-bg", theme.colors.textBg);
  root.style.setProperty("--font-main", `"${theme.fontFamily}", "Trebuchet MS", sans-serif`);
}

export function App() {
  const loading = useAppStore((state) => state.loading);
  const bootstrap = useAppStore((state) => state.bootstrap);
  const initialize = useAppStore((state) => state.initialize);
  const activeLanguage = useAppStore((state) => state.activeLanguage);

  useEffect(() => {
    void initialize();
  }, []);

  useEffect(() => {
    if (bootstrap) {
      applyThemeVariables(bootstrap.theme);
    }
  }, [bootstrap]);

  if (loading || !bootstrap) {
    return (
      <div className="loading-screen">
        {translate(activeLanguage, loading ? "desktop.loading" : "desktop.init_failed")}
      </div>
    );
  }

  return (
    <HashRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/mode/:mode" element={<FitWorkspacePage />} />
          <Route path="/data" element={<DataLabPage />} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/config" element={<ConfigPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}
