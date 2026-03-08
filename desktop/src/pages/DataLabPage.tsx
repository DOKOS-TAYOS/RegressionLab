import { useEffect, useState } from "react";

import { desktopClient } from "@/api/client";
import { HelpSection } from "@/components/HelpSection";
import { PlotPanel } from "@/components/PlotPanel";
import { translate } from "@/i18n";
import { useAppStore } from "@/store/appStore";
import type { DatasetPayload, PlotPayload } from "@/types";

export function DataLabPage() {
  const bootstrap = useAppStore((state) => state.bootstrap);
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const help = useAppStore((state) => state.help);
  const loadHelp = useAppStore((state) => state.loadHelp);
  const setBanner = useAppStore((state) => state.setBanner);
  const [dataset, setDataset] = useState<DatasetPayload | null>(null);
  const [transformId, setTransformId] = useState<string>("");
  const [cleanId, setCleanId] = useState<string>("");
  const [pairPlot, setPairPlot] = useState<PlotPayload | null>(null);
  const [showHelp, setShowHelp] = useState(false);

  useEffect(() => {
    if (showHelp) {
      void loadHelp();
    }
  }, [showHelp, loadHelp]);

  const loadDataset = async () => {
    const filePath = await window.desktopApi.openDataFile();
    if (!filePath) {
      return;
    }
    try {
      const response = await desktopClient.loadDataset(filePath);
      setDataset(response);
      setPairPlot(await desktopClient.getPairPlot(response.id));
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  const applyTransform = async () => {
    if (!dataset || !transformId) {
      return;
    }
    try {
      const response = await desktopClient.transformDataset(dataset.id, transformId);
      setDataset(response);
      setPairPlot(await desktopClient.getPairPlot(response.id));
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  const applyCleaning = async () => {
    if (!dataset || !cleanId) {
      return;
    }
    try {
      const response = await desktopClient.cleanDataset(dataset.id, cleanId);
      setDataset(response);
      setPairPlot(await desktopClient.getPairPlot(response.id));
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  const saveDataset = async () => {
    if (!dataset) {
      return;
    }
    const targetPath = await window.desktopApi.saveFile({
      defaultPath: dataset.filePath,
      filters: [
        { name: "CSV", extensions: ["csv"] },
        { name: "Text", extensions: ["txt"] },
        { name: "Excel", extensions: ["xlsx"] },
      ],
    });
    if (!targetPath) {
      return;
    }
    try {
      const response = await desktopClient.saveDataset(dataset.id, targetPath);
      setBanner({
        tone: "success",
        messageKey: "data_analysis.saved_ok",
        params: { path: response.savedPath },
      });
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  return (
    <section className="page-grid">
      <div className="panel">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">{translate(activeLanguage, "desktop.data_lab")}</span>
            <h2>{translate(activeLanguage, "dialog.show_data_title")}</h2>
          </div>
          <div className="row actions">
            <button className="ghost-button" onClick={() => setShowHelp((value) => !value)}>
              {translate(activeLanguage, showHelp ? "desktop.hide_data_help" : "desktop.show_data_help")}
            </button>
            <button className="primary-button" onClick={() => void loadDataset()}>
              {translate(activeLanguage, "dialog.upload_file")}
            </button>
          </div>
        </div>

        {showHelp ? (
          <div className="subpanel data-help-panel">
            <div className="section-title-row">
              <div>
                <span className="eyebrow">{translate(activeLanguage, "menu.information")}</span>
                <h3>{translate(activeLanguage, "desktop.data_help_title")}</h3>
              </div>
            </div>
            <div className="accordion-stack">
              {(help?.dataViewSections ?? []).map((section) => (
                <HelpSection
                  key={section.id}
                  headerKey={section.headerKey}
                  contentKeys={section.contentKeys}
                  language={activeLanguage}
                />
              ))}
            </div>
          </div>
        ) : null}

        {dataset ? (
          <>
            <div className="file-path-block">
              <span className="muted-path">{dataset.filePath}</span>
              <button className="ghost-button" onClick={() => void saveDataset()}>
                {translate(activeLanguage, "data_analysis.save")}
              </button>
            </div>

            <div className="field-grid">
              <label className="field">
                <span>{translate(activeLanguage, "data_analysis.select_transform")}</span>
                <select value={transformId} onChange={(event) => setTransformId(event.target.value)}>
                  <option value="">-</option>
                  {(bootstrap?.dataAnalysis.transforms ?? []).map((transform) => (
                    <option key={transform} value={transform}>
                      {translate(activeLanguage, `data_analysis.transform_label_${transform}`)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>{translate(activeLanguage, "data_analysis.select_clean")}</span>
                <select value={cleanId} onChange={(event) => setCleanId(event.target.value)}>
                  <option value="">-</option>
                  {(bootstrap?.dataAnalysis.cleaning ?? []).map((clean) => (
                    <option key={clean} value={clean}>
                      {translate(activeLanguage, `data_analysis.clean_label_${clean}`)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="row actions">
              <button className="primary-button" onClick={() => void applyTransform()}>
                {translate(activeLanguage, "data_analysis.transform")}
              </button>
              <button className="ghost-button" onClick={() => void applyCleaning()}>
                {translate(activeLanguage, "data_analysis.clean")}
              </button>
            </div>

            <div className="data-content-grid single">
              <div className="subpanel data-view-panel">
                <div className="section-title-row">
                  <div>
                    <span className="eyebrow">{translate(activeLanguage, "desktop.data_lab")}</span>
                    <h3>{translate(activeLanguage, "dialog.show_data_title")}</h3>
                  </div>
                </div>

                <div className="table-shell data-table-shell">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {dataset.columns.map((column) => (
                          <th key={column.name}>{column.name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dataset.preview.map((row, rowIndex) => (
                        <tr key={`row-${rowIndex}`}>
                          {dataset.columns.map((column) => (
                            <td key={`${rowIndex}-${column.name}`}>{String(row[column.name] ?? "")}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="subpanel data-view-panel">
                <div className="section-title-row">
                  <div>
                    <span className="eyebrow">{translate(activeLanguage, "desktop.pair_plots")}</span>
                    <h3>{translate(activeLanguage, "dialog.pair_plots_title")}</h3>
                  </div>
                </div>

                {pairPlot ? (
                  <div className="plot-shell data-plot-shell">
                    <PlotPanel plot={pairPlot} />
                  </div>
                ) : (
                  <div className="empty-state compact">
                    <p>{translate(activeLanguage, "desktop.no_pair_plot")}</p>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>{translate(activeLanguage, "desktop.data_empty")}</p>
          </div>
        )}
      </div>
    </section>
  );
}
