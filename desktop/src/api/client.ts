import type {
  ApiEnvelope,
  ApiErrorPayload,
  BootstrapPayload,
  DatasetPayload,
  FitResultPayload,
  HelpPayload,
  PlotPayload,
  PredictionPayload,
  RunAllFitsPayload,
  UpdatesApplyPayload,
  UpdatesCheckPayload,
} from "@/types";

let backendBaseUrlPromise: Promise<string> | null = null;

async function getBackendBaseUrl(): Promise<string> {
  if (!backendBaseUrlPromise) {
    backendBaseUrlPromise = window.desktopApi.getBackendBaseUrl();
  }
  return backendBaseUrlPromise;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = await getBackendBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const body = (await response.json()) as ApiEnvelope<T> | ApiErrorPayload;
  if (!response.ok || !("ok" in body) || body.ok === false) {
    throw body;
  }
  return body.data;
}

export const desktopClient = {
  getBootstrap: () => request<BootstrapPayload>("/bootstrap"),
  getHelp: () => request<HelpPayload>("/help"),
  getConfig: () =>
    request<{
      schema: BootstrapPayload["config"]["schema"];
      values: Record<string, string>;
      restartRequired: boolean;
    }>("/config"),
  updateConfig: (values: Record<string, string>) =>
    request<{
      values: Record<string, string>;
      restartRequired: boolean;
    }>("/config", {
      method: "PUT",
      body: JSON.stringify({ values }),
    }),
  loadDataset: (filePath: string) =>
    request<DatasetPayload>("/datasets/load", {
      method: "POST",
      body: JSON.stringify({ file_path: filePath, include_records: true }),
    }),
  getDataset: (datasetId: string) => request<DatasetPayload>(`/datasets/${datasetId}?include_records=true`),
  transformDataset: (datasetId: string, transformId: string, columns?: string[]) =>
    request<DatasetPayload>(`/datasets/${datasetId}/transform`, {
      method: "POST",
      body: JSON.stringify({
        transform_id: transformId,
        columns,
        in_place: true,
        include_records: true,
      }),
    }),
  cleanDataset: (datasetId: string, cleanId: string, columns?: string[]) =>
    request<DatasetPayload>(`/datasets/${datasetId}/clean`, {
      method: "POST",
      body: JSON.stringify({
        clean_id: cleanId,
        columns,
        include_records: true,
      }),
    }),
  saveDataset: (datasetId: string, filePath: string) =>
    request<{ savedPath: string }>(`/datasets/${datasetId}/save`, {
      method: "POST",
      body: JSON.stringify({ file_path: filePath }),
    }),
  getPairPlot: (datasetId: string, variables?: string[]) =>
    request<Extract<PlotPayload, { kind: "splom" }>>(`/datasets/${datasetId}/pair-plot`, {
      method: "POST",
      body: JSON.stringify({ variables }),
    }),
  runFit: (payload: Record<string, unknown>) =>
    request<FitResultPayload>("/fits/run", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  runAllFits: (payload: Record<string, unknown>) =>
    request<RunAllFitsPayload>("/fits/run-all", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  predict: (fitId: string, xValues: number[]) =>
    request<PredictionPayload>("/predict", {
      method: "POST",
      body: JSON.stringify({ fit_id: fitId, x_values: xValues }),
    }),
  checkUpdates: () => request<UpdatesCheckPayload>("/updates/check", { method: "POST" }),
  applyUpdates: () => request<UpdatesApplyPayload>("/updates/apply", { method: "POST" }),
};
