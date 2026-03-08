import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { desktopClient } from "@/api/client";
import { PlotPanel } from "@/components/PlotPanel";
import { ThemedSelect } from "@/components/ThemedSelect";
import { translate } from "@/i18n";
import { useAppStore } from "@/store/appStore";
import { parseResultText } from "@/utils/resultText";
import type { DatasetPayload, EquationCatalogItem, FitResultPayload } from "@/types";

type ModeId = "normal" | "multiple" | "checker" | "total";

type DatasetDraft = {
  dataset: DatasetPayload | null;
  xNames: string[];
  yName: string;
  plotName: string;
};

type CustomEquationDraft = {
  formula: string;
  parameterNames: string;
  numIndependentVars: number;
};

function buildDefaultDraft(dataset: DatasetPayload | null, independentVars = 1): DatasetDraft {
  const baseVariables = dataset?.baseVariables ?? [];
  const xNames = baseVariables.slice(0, independentVars);
  const yName = baseVariables[independentVars] ?? baseVariables[0] ?? "";
  return {
    dataset,
    xNames,
    yName,
    plotName: dataset ? `${dataset.baseVariables[0] ?? "fit"}_${yName || "result"}` : "",
  };
}

function ensureSized(values: string[], size: number): string[] {
  if (values.length === size) {
    return values;
  }
  return Array.from({ length: size }, (_, index) => values[index] ?? "");
}

function parseParamNames(raw: string): string[] {
  return raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall back to document.execCommand below when clipboard access is denied.
    }
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  textarea.style.pointerEvents = "none";
  document.body.appendChild(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  document.body.removeChild(textarea);
  return copied;
}

function ResultCardSection({
  title,
  lines,
}: {
  title: string;
  lines: string[];
}) {
  if (lines.length === 0) {
    return null;
  }

  return (
    <section className="subpanel">
      <div className="section-title-row">
        <h4>{title}</h4>
      </div>
      <div className="result-value-grid">
        {lines.map((line, index) => (
          <div className="result-value-card" key={`${title}-${index}`}>
            <code className="formatted-line">{line}</code>
          </div>
        ))}
      </div>
    </section>
  );
}

function ResultDetailContent({
  result,
  parsedResult,
  activeLanguage,
  onCopy,
  expanded = false,
}: {
  result: FitResultPayload;
  parsedResult: ReturnType<typeof parseResultText>;
  activeLanguage: string;
  onCopy: (rawText: string) => void;
  expanded?: boolean;
}) {
  const copyRows = Math.min(Math.max(parsedResult.rawText.split("\n").length + 1, 6), expanded ? 18 : 14);

  return (
    <div className={`result-content ${expanded ? "expanded" : ""}`}>
      <div className="equation-block">
        <strong>{result.formula}</strong>
        <span>{result.formattedEquation}</span>
      </div>

      <div className={`plot-shell ${expanded ? "plot-shell-expanded" : ""}`}>
        <PlotPanel plot={result.plot} />
      </div>

      <div className="result-sections-stack">
        <ResultCardSection
          lines={parsedResult.statsLines}
          title={translate(activeLanguage, "dialog.results_stats_heading")}
        />
        <ResultCardSection
          lines={parsedResult.parameterLines}
          title={translate(activeLanguage, "dialog.results_params_heading")}
        />

        <section className="subpanel result-copy-panel">
          <div className="section-title-row">
            <h4>{translate(activeLanguage, "desktop.solution_text")}</h4>
            <button className="ghost-button" onClick={() => onCopy(parsedResult.rawText)}>
              {translate(activeLanguage, "desktop.copy_values")}
            </button>
          </div>
          <textarea
            className="result-copy-textarea"
            readOnly
            rows={copyRows}
            value={parsedResult.rawText}
          />
        </section>

        <PredictionPanel result={result} />
      </div>
    </div>
  );
}

function PredictionPanel({ result }: { result: FitResultPayload }) {
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const setBanner = useAppStore((state) => state.setBanner);
  const [values, setValues] = useState<string[]>(result.xNames.map(() => "0"));
  const [prediction, setPrediction] = useState<string>("");
  const placeholderText = translate(activeLanguage, "dialog.prediction_result_placeholder");
  const invalidInputText = translate(activeLanguage, "dialog.prediction_invalid_input");

  useEffect(() => {
    const trimmedValues = values.map((value) => value.trim());
    if (trimmedValues.some((value) => value.length === 0)) {
      setPrediction(placeholderText);
      return;
    }

    const numericValues = trimmedValues.map((value) => Number(value));
    if (numericValues.some((value) => Number.isNaN(value))) {
      setPrediction(invalidInputText);
      return;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await desktopClient.predict(result.fitId, numericValues);
        if (cancelled) {
          return;
        }

        setPrediction(
          response.displayUncertainty
            ? translate(activeLanguage, "dialog.prediction_result_with_uncertainty", {
                y: response.displayY,
                uy: response.displayUncertainty,
              })
            : translate(activeLanguage, "dialog.prediction_result", { y: response.displayY }),
        );
      } catch (error) {
        if (cancelled) {
          return;
        }
        const payload = error as { error?: { messageKey?: string; details?: unknown } };
        setBanner({
          tone: "error",
          messageKey: payload.error?.messageKey ?? "desktop.error.internal",
          details: payload.error?.details,
        });
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [activeLanguage, invalidInputText, placeholderText, result.fitId, setBanner, values]);

  return (
    <div className="subpanel">
      <div className="section-title-row">
        <h4>{translate(activeLanguage, "dialog.prediction")}</h4>
      </div>
      <div className="field-grid compact">
        {result.xNames.map((name, index) => (
          <label key={name} className="field">
            <span>{name}</span>
            <input
              value={values[index] ?? ""}
              onChange={(event) =>
                setValues((current) => current.map((item, itemIndex) => (itemIndex === index ? event.target.value : item)))
              }
            />
          </label>
        ))}
      </div>
      <div className="prediction-row">
        <span className="prediction-output">{prediction || translate(activeLanguage, "dialog.prediction_result_placeholder")}</span>
      </div>
    </div>
  );
}

function ResultThumbnailButton({
  result,
  active,
  activeLanguage,
  onSelect,
}: {
  result: FitResultPayload;
  active: boolean;
  activeLanguage: string;
  onSelect: (fitId: string) => void;
}) {
  return (
    <button
      className={`result-thumbnail-button ${active ? "active" : ""}`}
      onClick={() => onSelect(result.fitId)}
    >
      <div className="plot-shell result-thumbnail-shell">
        <PlotPanel plot={result.plot} />
      </div>
      <div className="result-thumbnail-meta">
        <strong>{result.plotName}</strong>
        <span>
          {result.equationId === "custom"
            ? translate(activeLanguage, "equations.custom_formula")
            : result.equationId}
        </span>
      </div>
    </button>
  );
}

function ComparisonPlotPanel({
  result,
  sideLabel,
  activeLanguage,
}: {
  result: FitResultPayload;
  sideLabel: string;
  activeLanguage: string;
}) {
  return (
    <section className="subpanel comparison-panel">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">{sideLabel}</span>
          <h3>{result.plotName}</h3>
        </div>
        <span className="muted-note">
          {result.equationId === "custom"
            ? translate(activeLanguage, "equations.custom_formula")
            : result.equationId}
        </span>
      </div>
      <div className="plot-shell comparison-plot-shell">
        <PlotPanel plot={result.plot} />
      </div>
    </section>
  );
}

export function FitWorkspacePage() {
  const params = useParams();
  const mode = (params.mode as ModeId | undefined) ?? "normal";
  const bootstrap = useAppStore((state) => state.bootstrap);
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const setBanner = useAppStore((state) => state.setBanner);

  const equations = bootstrap?.equations ?? [];
  const equationOptions = useMemo(
    () => [
      ...equations.map((equation) => ({
        value: equation.id,
        label: translate(activeLanguage, equation.labelKey),
      })),
      {
        value: "custom",
        label: translate(activeLanguage, "equations.custom_formula"),
      },
    ],
    [activeLanguage, equations],
  );
  const defaultEquationId = equations[0]?.id ?? "";
  const [selectedEquationId, setSelectedEquationId] = useState<string>("");
  const [datasets, setDatasets] = useState<DatasetDraft[]>([buildDefaultDraft(null)]);
  const [customEquation, setCustomEquation] = useState<CustomEquationDraft>({
    formula: "",
    parameterNames: "a, b",
    numIndependentVars: 1,
  });
  const [configureParams, setConfigureParams] = useState(false);
  const [initialGuess, setInitialGuess] = useState<string[]>([]);
  const [lowerBounds, setLowerBounds] = useState<string[]>([]);
  const [upperBounds, setUpperBounds] = useState<string[]>([]);
  const [loopMode, setLoopMode] = useState(false);
  const [results, setResults] = useState<FitResultPayload[]>([]);
  const [running, setRunning] = useState(false);
  const [checkerSelection, setCheckerSelection] = useState<string[]>([]);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [expandedResultId, setExpandedResultId] = useState<string | null>(null);
  const [comparisonOpen, setComparisonOpen] = useState(false);
  const [comparisonLeftId, setComparisonLeftId] = useState<string>("");
  const [comparisonRightId, setComparisonRightId] = useState<string>("");

  useEffect(() => {
    if (!selectedEquationId && defaultEquationId) {
      setSelectedEquationId(defaultEquationId);
      setCheckerSelection([defaultEquationId]);
    }
  }, [defaultEquationId, selectedEquationId]);

  const activeEquation: EquationCatalogItem | undefined =
    selectedEquationId === "custom"
      ? undefined
      : equations.find((equation) => equation.id === selectedEquationId);

  const activeParamNames =
    selectedEquationId === "custom"
      ? parseParamNames(customEquation.parameterNames)
      : activeEquation?.paramNames ?? [];

  const activeIndependentVars =
    selectedEquationId === "custom"
      ? customEquation.numIndependentVars
      : activeEquation?.numIndependentVars ?? 1;

  useEffect(() => {
    setInitialGuess((current) => ensureSized(current, activeParamNames.length));
    setLowerBounds((current) => ensureSized(current, activeParamNames.length));
    setUpperBounds((current) => ensureSized(current, activeParamNames.length));
    setDatasets((current) =>
      current.map((draft) => ({
        ...draft,
        xNames: ensureSized(draft.xNames, activeIndependentVars).map(
          (value, index) => value || draft.dataset?.baseVariables[index] || "",
        ),
      })),
    );
  }, [selectedEquationId, customEquation.parameterNames, customEquation.numIndependentVars]);

  useEffect(() => {
    if (results.length === 0) {
      setSelectedResultId(null);
      setComparisonLeftId("");
      setComparisonRightId("");
      setComparisonOpen(false);
      return;
    }

    setSelectedResultId((current) => {
      if (current && results.some((result) => result.fitId === current)) {
        return current;
      }
      return mode === "normal" || results.length === 1 ? results[0].fitId : null;
    });
    setComparisonLeftId((current) =>
      current && results.some((result) => result.fitId === current) ? current : results[0].fitId,
    );
    setComparisonRightId((current) => {
      if (current && results.some((result) => result.fitId === current)) {
        return current;
      }
      return results[1]?.fitId ?? results[0].fitId;
    });
  }, [mode, results]);

  const loadDataset = async (index: number) => {
    const filePath = await window.desktopApi.openDataFile();
    if (!filePath) {
      return;
    }

    try {
      const dataset = await desktopClient.loadDataset(filePath);
      setDatasets((current) =>
        current.map((draft, draftIndex) =>
          draftIndex === index ? buildDefaultDraft(dataset, activeIndependentVars) : draft,
        ),
      );
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  const loadMultipleDatasets = async () => {
    const filePaths = await window.desktopApi.openDataFiles();
    if (filePaths.length === 0) {
      return;
    }

    const settled = await Promise.allSettled(filePaths.map((filePath) => desktopClient.loadDataset(filePath)));
    const loadedDatasets = settled
      .filter((item): item is PromiseFulfilledResult<DatasetPayload> => item.status === "fulfilled")
      .map((item) => item.value);
    const failedDatasets = settled
      .filter((item): item is PromiseRejectedResult => item.status === "rejected")
      .map((item) => item.reason);

    if (loadedDatasets.length > 0) {
      setDatasets(loadedDatasets.map((dataset) => buildDefaultDraft(dataset, activeIndependentVars)));
    }

    if (failedDatasets.length > 0) {
      const failedDetails = failedDatasets.map((item) => {
        const payload = item as { error?: { messageKey?: string; details?: unknown } };
        return {
          messageKey: payload.error?.messageKey ?? "desktop.error.internal",
          details: payload.error?.details,
        };
      });
      setBanner({
        tone: loadedDatasets.length > 0 ? "info" : "error",
        messageKey: loadedDatasets.length > 0 ? "desktop.error.batch_partial" : "desktop.error.internal",
        details: failedDetails,
      });
    }
  };

  const addDatasetSlot = () => {
    setDatasets((current) => [...current, buildDefaultDraft(null, activeIndependentVars)]);
  };

  const updateDraft = (index: number, patch: Partial<DatasetDraft>) => {
    setDatasets((current) =>
      current.map((draft, draftIndex) => (draftIndex === index ? { ...draft, ...patch } : draft)),
    );
  };

  const buildBoundsPayload = () => {
    if (!configureParams) {
      return undefined;
    }

    return {
      lower: lowerBounds.map((value) => (value.trim() ? Number(value) : null)),
      upper: upperBounds.map((value) => (value.trim() ? Number(value) : null)),
    };
  };

  const buildInitialGuessPayload = () => {
    if (!configureParams) {
      return undefined;
    }
    return initialGuess.map((value) => (value.trim() ? Number(value) : null));
  };

  const buildFitPayload = (draft: DatasetDraft, modeId: ModeId) => {
    const payload: Record<string, unknown> = {
      dataset_id: draft.dataset?.id,
      mode: modeId,
      x_names: draft.xNames,
      y_name: draft.yName,
      plot_name: draft.plotName || undefined,
      initial_guess_override: buildInitialGuessPayload(),
      bounds_override: buildBoundsPayload(),
      export_plot: true,
    };

    if (selectedEquationId === "custom") {
      payload.custom_equation = {
        formula: customEquation.formula,
        parameter_names: parseParamNames(customEquation.parameterNames),
        num_independent_vars: customEquation.numIndependentVars,
      };
    } else {
      payload.equation_id = selectedEquationId;
    }

    return payload;
  };

  const runFits = async () => {
    setRunning(true);
    setBanner(null);

    try {
      if (mode === "checker" || mode === "total") {
        const firstDataset = datasets[0];
        if (!firstDataset.dataset) {
          throw { error: { messageKey: "error.data_is_null" } };
        }
        if (mode === "checker" && checkerSelection.length === 0) {
          throw { error: { messageKey: "desktop.select_at_least_one_equation" } };
        }
        const response = await desktopClient.runAllFits({
          dataset_id: firstDataset.dataset.id,
          mode,
          x_names: firstDataset.xNames,
          y_name: firstDataset.yName,
          plot_name_base: firstDataset.plotName || undefined,
          equation_ids: mode === "checker" ? checkerSelection : undefined,
          export_plot: true,
        });
        setResults(response.results);
        if (response.errors.length > 0) {
          setBanner({
            tone: "info",
            messageKey: "desktop.error.batch_partial",
            details: response.errors,
          });
        }
      } else if (mode === "multiple") {
        const readyDrafts = datasets.filter((draft) => draft.dataset);
        if (readyDrafts.length === 0) {
          throw { error: { messageKey: "error.data_is_null" } };
        }
        const payloads = readyDrafts.map((draft) => buildFitPayload(draft, mode));
        const runResults = await Promise.all(payloads.map((payload) => desktopClient.runFit(payload)));
        setResults(runResults);
      } else {
        const draft = datasets[0];
        if (!draft.dataset) {
          throw { error: { messageKey: "error.data_is_null" } };
        }
        const response = await desktopClient.runFit(buildFitPayload(draft, mode));
        setResults([response]);
      }
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    } finally {
      setRunning(false);
    }
  };

  const modeTitleKey =
    mode === "multiple"
      ? "menu.multiple_datasets"
      : mode === "checker"
        ? "menu.checker_fitting"
        : mode === "total"
          ? "menu.total_fitting"
          : "menu.normal_fitting";

  const parsedResults = useMemo(
    () =>
      new Map(
        results.map((result) => [
          result.fitId,
          parseResultText(result.rawText),
        ]),
      ),
    [results],
  );

  const isMultiResultMode = mode === "multiple" || mode === "checker" || mode === "total";
  const selectedResult = selectedResultId
    ? results.find((result) => result.fitId === selectedResultId) ?? results[0] ?? null
    : results[0] ?? null;
  const selectedParsedResult = selectedResult
    ? parsedResults.get(selectedResult.fitId) ?? parseResultText(selectedResult.rawText)
    : null;
  const comparisonLeftResult = comparisonLeftId
    ? results.find((result) => result.fitId === comparisonLeftId) ?? null
    : null;
  const comparisonRightResult = comparisonRightId
    ? results.find((result) => result.fitId === comparisonRightId) ?? null
    : null;

  const handleCopyResultText = async (rawText: string) => {
    const copied = await copyTextToClipboard(rawText);
    setBanner({
      tone: copied ? "success" : "error",
      messageKey: copied ? "desktop.copy_success" : "desktop.copy_failed",
    });
  };

  const expandedResult = expandedResultId ? results.find((result) => result.fitId === expandedResultId) ?? null : null;
  const expandedParsedResult = expandedResult ? parsedResults.get(expandedResult.fitId) ?? parseResultText(expandedResult.rawText) : null;

  useEffect(() => {
    if (!expandedResultId && !comparisonOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setExpandedResultId(null);
        setComparisonOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [comparisonOpen, expandedResultId]);

  return (
    <section className="page-grid fit-layout">
      <div className="panel">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">{translate(activeLanguage, "desktop.workflow")}</span>
            <h2>{translate(activeLanguage, modeTitleKey)}</h2>
          </div>
          <label className="toggle-chip">
            <input type="checkbox" checked={loopMode} onChange={() => setLoopMode((value) => !value)} />
            <span>{translate(activeLanguage, "desktop.loop_mode")}</span>
          </label>
        </div>

        {mode === "normal" || mode === "multiple" ? (
          <div className="subpanel">
            <div className="section-title-row">
              <h3>{translate(activeLanguage, "dialog.equation_type")}</h3>
            </div>
            <label className="field">
              <span>{translate(activeLanguage, "dialog.select_equation")}</span>
              <ThemedSelect
                ariaLabel={translate(activeLanguage, "dialog.equation_type")}
                onChange={setSelectedEquationId}
                options={equationOptions}
                placeholder={translate(activeLanguage, "dialog.select_equation")}
                value={selectedEquationId}
              />
            </label>

            {selectedEquationId === "custom" ? (
              <div className="field-grid">
                <label className="field span-2">
                  <span>{translate(activeLanguage, "dialog.custom_formula_prompt")}</span>
                  <textarea
                    value={customEquation.formula}
                    onChange={(event) => setCustomEquation((current) => ({ ...current, formula: event.target.value }))}
                    rows={4}
                  />
                </label>
                <label className="field">
                  <span>{translate(activeLanguage, "dialog.parameter_names_title")}</span>
                  <input
                    value={customEquation.parameterNames}
                    onChange={(event) =>
                      setCustomEquation((current) => ({ ...current, parameterNames: event.target.value }))
                    }
                  />
                </label>
                <label className="field">
                  <span>{translate(activeLanguage, "dialog.num_independent_variables")}</span>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={customEquation.numIndependentVars}
                    onChange={(event) =>
                      setCustomEquation((current) => ({
                        ...current,
                        numIndependentVars: Math.max(1, Number(event.target.value)),
                      }))
                    }
                  />
                </label>
              </div>
            ) : activeEquation ? (
              <div className="inline-note">
                <strong>{activeEquation.formula}</strong>
                <span>{translate(activeLanguage, activeEquation.descriptionKey)}</span>
              </div>
            ) : null}

            <label className="toggle-chip">
              <input
                type="checkbox"
                checked={configureParams}
                onChange={() => setConfigureParams((value) => !value)}
              />
              <span>{translate(activeLanguage, "dialog.configure_initial_params")}</span>
            </label>

            {configureParams && activeParamNames.length > 0 ? (
              <div className="parameter-table">
                <div className="parameter-row header">
                  <span>{translate(activeLanguage, "dialog.param_column_name")}</span>
                  <span>{translate(activeLanguage, "dialog.param_column_initial")}</span>
                  <span>{translate(activeLanguage, "dialog.param_column_range_start")}</span>
                  <span>{translate(activeLanguage, "dialog.param_column_range_end")}</span>
                </div>
                {activeParamNames.map((name, index) => (
                  <div className="parameter-row" key={name}>
                    <span>{name}</span>
                    <input
                      value={initialGuess[index] ?? ""}
                      onChange={(event) =>
                        setInitialGuess((current) =>
                          current.map((item, itemIndex) => (itemIndex === index ? event.target.value : item)),
                        )
                      }
                    />
                    <input
                      value={lowerBounds[index] ?? ""}
                      onChange={(event) =>
                        setLowerBounds((current) =>
                          current.map((item, itemIndex) => (itemIndex === index ? event.target.value : item)),
                        )
                      }
                    />
                    <input
                      value={upperBounds[index] ?? ""}
                      onChange={(event) =>
                        setUpperBounds((current) =>
                          current.map((item, itemIndex) => (itemIndex === index ? event.target.value : item)),
                        )
                      }
                    />
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}

        {mode === "checker" ? (
          <div className="subpanel">
            <div className="section-title-row">
              <h3>{translate(activeLanguage, "menu.checker_fitting")}</h3>
            </div>
            <div className="checkbox-grid">
              {equations.map((equation) => (
                <label key={equation.id} className="toggle-chip">
                  <input
                    type="checkbox"
                    checked={checkerSelection.includes(equation.id)}
                    onChange={() =>
                      setCheckerSelection((current) =>
                        current.includes(equation.id)
                          ? current.filter((item) => item !== equation.id)
                          : [...current, equation.id],
                      )
                    }
                  />
                  <span>{translate(activeLanguage, equation.labelKey)}</span>
                </label>
              ))}
            </div>
          </div>
        ) : null}

        <div className="subpanel">
          <div className="section-title-row">
            <h3>{translate(activeLanguage, "dialog.data")}</h3>
            {mode === "multiple" ? (
              <div className="row actions">
                <button className="ghost-button" onClick={() => void loadMultipleDatasets()}>
                  {translate(activeLanguage, "desktop.upload_multiple_datasets")}
                </button>
                <button className="ghost-button" onClick={addDatasetSlot}>
                  {translate(activeLanguage, "desktop.add_dataset")}
                </button>
              </div>
            ) : null}
          </div>

          {datasets.map((draft, index) => (
            <div className="dataset-card" key={`${index}-${draft.dataset?.id ?? "empty"}`}>
              <div className="row actions">
                <button className="primary-button" onClick={() => void loadDataset(index)}>
                  {draft.dataset
                    ? translate(activeLanguage, "desktop.replace_dataset")
                    : translate(activeLanguage, "dialog.upload_file")}
                </button>
                <span className="muted-path">
                  {draft.dataset?.filePath ?? translate(activeLanguage, "desktop.no_dataset_loaded")}
                </span>
              </div>
              {draft.dataset ? (
                <div className="field-grid">
                  <label className="field">
                    <span>{translate(activeLanguage, "dialog.plot_name")}</span>
                    <input
                      value={draft.plotName}
                      onChange={(event) => updateDraft(index, { plotName: event.target.value })}
                    />
                  </label>
                  {Array.from({ length: activeIndependentVars }).map((_, variableIndex) => (
                    <label className="field" key={`x-${variableIndex}`}>
                      <span>{`${translate(activeLanguage, "dialog.independent_variable")} ${variableIndex + 1}`}</span>
                      <select
                        value={draft.xNames[variableIndex] ?? ""}
                        onChange={(event) =>
                          updateDraft(index, {
                            xNames: ensureSized(draft.xNames, activeIndependentVars).map((item, itemIndex) =>
                              itemIndex === variableIndex ? event.target.value : item,
                            ),
                          })
                        }
                      >
                        {draft.dataset.baseVariables.map((name) => (
                          <option key={name} value={name}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </label>
                  ))}
                  <label className="field">
                    <span>{translate(activeLanguage, "dialog.dependent_variable")}</span>
                    <select
                      value={draft.yName}
                      onChange={(event) => updateDraft(index, { yName: event.target.value })}
                    >
                      {draft.dataset.baseVariables.map((name) => (
                        <option key={name} value={name}>
                          {name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              ) : null}
            </div>
          ))}
        </div>

        <div className="row actions">
          <button className="primary-button large" disabled={running} onClick={() => void runFits()}>
            {running ? translate(activeLanguage, "desktop.running") : translate(activeLanguage, "dialog.accept")}
          </button>
          {loopMode ? <span className="muted-note">{translate(activeLanguage, "workflow.loop_help")}</span> : null}
        </div>
      </div>

      <div className="panel results-panel">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">{translate(activeLanguage, "desktop.results")}</span>
            <h2>{translate(activeLanguage, "dialog.results_title")}</h2>
          </div>
        </div>
        {results.length === 0 ? (
          <div className="empty-state">
            <p>{translate(activeLanguage, "desktop.no_fits")}</p>
          </div>
        ) : (
          <div className="results-stack">
            {isMultiResultMode && results.length > 1 ? (
              <section className="subpanel result-gallery-panel">
                <div className="section-title-row">
                  <div>
                    <span className="eyebrow">{translate(activeLanguage, "desktop.result_gallery")}</span>
                    <h3>{translate(activeLanguage, "desktop.browse_results")}</h3>
                  </div>
                  <button
                    className="ghost-button"
                    onClick={() => {
                      const anchorResult = selectedResult ?? results[0];
                      setComparisonLeftId(anchorResult.fitId);
                      setComparisonRightId(
                        results.find((result) => result.fitId !== anchorResult.fitId)?.fitId ?? anchorResult.fitId,
                      );
                      setComparisonOpen(true);
                    }}
                  >
                    {translate(activeLanguage, "desktop.compare_results")}
                  </button>
                </div>
                <div className="result-thumbnail-grid">
                  {results.map((result) => (
                    <ResultThumbnailButton
                      key={result.fitId}
                      active={result.fitId === selectedResult?.fitId}
                      activeLanguage={activeLanguage}
                      onSelect={setSelectedResultId}
                      result={result}
                    />
                  ))}
                </div>
              </section>
            ) : null}

            {selectedResult && selectedParsedResult ? (
              <article className="result-card">
                <div className="section-title-row">
                  <div>
                    <span className="eyebrow">
                      {selectedResult.equationId === "custom"
                        ? translate(activeLanguage, "equations.custom_formula")
                        : selectedResult.equationId}
                    </span>
                    <h3>{selectedResult.plotName}</h3>
                  </div>
                  <div className="row actions">
                    <button className="ghost-button" onClick={() => setExpandedResultId(selectedResult.fitId)}>
                      {translate(activeLanguage, "desktop.expand_plot")}
                    </button>
                    {selectedResult.exports.plotPath ? (
                      <button
                        className="ghost-button"
                        onClick={() => void window.desktopApi.revealPath(selectedResult.exports.plotPath!)}
                      >
                        {translate(activeLanguage, "desktop.reveal_plot")}
                      </button>
                    ) : null}
                  </div>
                </div>

                <ResultDetailContent
                  activeLanguage={activeLanguage}
                  onCopy={(rawText) => void handleCopyResultText(rawText)}
                  parsedResult={selectedParsedResult}
                  result={selectedResult}
                />
              </article>
            ) : (
              <div className="empty-state compact">
                <p>{translate(activeLanguage, "desktop.select_result_to_preview")}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {expandedResult && expandedParsedResult ? (
        <div className="result-overlay" onClick={() => setExpandedResultId(null)}>
          <div className="result-overlay-panel" onClick={(event) => event.stopPropagation()}>
            <div className="section-title-row">
              <div>
                <span className="eyebrow">{expandedResult.equationId}</span>
                <h2>{expandedResult.plotName}</h2>
              </div>
              <div className="row actions">
                {expandedResult.exports.plotPath ? (
                  <button
                    className="ghost-button"
                    onClick={() => void window.desktopApi.revealPath(expandedResult.exports.plotPath!)}
                  >
                    {translate(activeLanguage, "desktop.reveal_plot")}
                  </button>
                ) : null}
                <button className="ghost-button" onClick={() => setExpandedResultId(null)}>
                  {translate(activeLanguage, "desktop.close")}
                </button>
              </div>
            </div>

            <ResultDetailContent
              activeLanguage={activeLanguage}
              expanded
              onCopy={(rawText) => void handleCopyResultText(rawText)}
              parsedResult={expandedParsedResult}
              result={expandedResult}
            />
          </div>
        </div>
      ) : null}

      {comparisonOpen && comparisonLeftResult && comparisonRightResult ? (
        <div className="result-overlay" onClick={() => setComparisonOpen(false)}>
          <div className="result-overlay-panel comparison-overlay-panel" onClick={(event) => event.stopPropagation()}>
            <div className="section-title-row">
              <div>
                <span className="eyebrow">{translate(activeLanguage, "desktop.compare_results")}</span>
                <h2>{translate(activeLanguage, "dialog.results_title")}</h2>
              </div>
              <button className="ghost-button" onClick={() => setComparisonOpen(false)}>
                {translate(activeLanguage, "desktop.close")}
              </button>
            </div>

            <div className="comparison-controls">
              <label className="field">
                <span>{translate(activeLanguage, "desktop.compare_left")}</span>
                <select value={comparisonLeftId} onChange={(event) => setComparisonLeftId(event.target.value)}>
                  {results.map((result) => (
                    <option key={`left-${result.fitId}`} value={result.fitId}>
                      {result.plotName}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>{translate(activeLanguage, "desktop.compare_right")}</span>
                <select value={comparisonRightId} onChange={(event) => setComparisonRightId(event.target.value)}>
                  {results.map((result) => (
                    <option key={`right-${result.fitId}`} value={result.fitId}>
                      {result.plotName}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="comparison-grid">
              <ComparisonPlotPanel
                activeLanguage={activeLanguage}
                result={comparisonLeftResult}
                sideLabel={translate(activeLanguage, "desktop.compare_left")}
              />
              <ComparisonPlotPanel
                activeLanguage={activeLanguage}
                result={comparisonRightResult}
                sideLabel={translate(activeLanguage, "desktop.compare_right")}
              />
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
