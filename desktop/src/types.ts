export type ApiEnvelope<T> = {
  ok: boolean;
  data: T;
};

export type ApiErrorPayload = {
  ok: false;
  error: {
    code: string;
    messageKey: string;
    messageParams?: Record<string, unknown>;
    details?: unknown;
  };
};

export type ThemeTokens = {
  fontFamily: string;
  fontSize: number;
  fontSizeLarge: number;
  colors: {
    bg: string;
    fg: string;
    buttonBg: string;
    activeBg: string;
    accept: string;
    cancel: string;
    accent: string;
    fieldBg: string;
    hoverBg: string;
    textBg: string;
    textFg: string;
    selectionBg: string;
  };
  spacing: {
    padding: number;
    borderWidth: number;
  };
};

export type ConfigSchemaItem = {
  key: string;
  default: string | number | boolean;
  cast_type: "str" | "int" | "float" | "bool";
  options?: Array<string | number | boolean> | null;
};

export type BootstrapPayload = {
  version: string;
  supportedLanguages: string[];
  activeLanguage: string;
  theme: ThemeTokens;
  config: {
    schema: ConfigSchemaItem[];
    values: Record<string, string>;
    restartRequired: boolean;
  };
  equations: EquationCatalogItem[];
  availableEquationTypes: string[];
  dataAnalysis: {
    transforms: string[];
    cleaning: string[];
  };
  modes: Array<{ id: string; labelKey: string }>;
  links: {
    donationsUrl: string;
  };
};

export type EquationCatalogItem = {
  id: string;
  labelKey: string;
  descriptionKey: string;
  formula: string;
  paramNames: string[];
  type: string;
  numIndependentVars: number;
  initialGuess?: number[] | null;
  bounds?: unknown;
};

export type DatasetColumn = {
  name: string;
  dtype: string;
  isNumeric: boolean;
  isUncertainty: boolean;
  baseColumn?: string | null;
};

export type DatasetPayload = {
  id: string;
  filePath: string;
  fileType: string;
  rowCount: number;
  columns: DatasetColumn[];
  variableNames: string[];
  baseVariables: string[];
  uncertaintyPairs: Record<string, string>;
  previewRows: number;
  preview: Array<Record<string, unknown>>;
  records: Array<Record<string, unknown>> | null;
  pairPlotVariables: string[];
  updatedAt: string;
};

export type PlotPayload =
  | {
      kind: "curve2d";
      xLabel: string;
      yLabel: string;
      traces: Array<{
        name: string;
        mode: "markers" | "lines";
        x: Array<number | null>;
        y: Array<number | null>;
        errorX?: Array<number | null>;
        errorY?: Array<number | null>;
      }>;
    }
  | {
      kind: "surface3d";
      xLabel: string;
      yLabel: string;
      zLabel: string;
      scatter: {
        x: Array<number | null>;
        y: Array<number | null>;
        z: Array<number | null>;
      };
      surface: {
        x: Array<number | null>;
        y: Array<number | null>;
        z: Array<Array<number | null>> | null;
      };
      fittedPoints: {
        x: Array<number | null>;
        y: Array<number | null>;
        z: Array<number | null>;
      };
    }
  | {
      kind: "residuals";
      xLabel: string;
      yLabel: string;
      traces: Array<{
        name: string;
        mode: "markers" | "lines";
        x: Array<number | null>;
        y: Array<number | null>;
      }>;
    }
  | {
      kind: "splom";
      dimensions: Array<{ label: string; values: Array<number | null> }>;
      variables: string[];
    };

export type FitResultPayload = {
  fitId: string;
  mode: string;
  datasetId: string;
  equationId: string;
  plotName: string;
  xNames: string[];
  yName: string;
  rawText: string;
  formula: string;
  formattedEquation: string;
  equationString: string;
  parameters: Array<{
    name: string;
    value: number;
    uncertainty: number | null;
    displayValue: number;
    displayUncertainty: string;
    confidenceInterval: {
      available: boolean;
      low: number | null;
      high: number | null;
      displayLow: string | null;
      displayHigh: string | null;
    };
  }>;
  stats: Record<string, { value: number; display: string }>;
  plot: PlotPayload;
  exports: {
    plotPath: string | null;
    outputDir: string | null;
  };
};

export type RunAllFitsPayload = {
  results: FitResultPayload[];
  errors: Array<{
    equationId: string;
    error: ApiErrorPayload["error"];
  }>;
};

export type PredictionPayload = {
  fitId: string;
  xNames: string[];
  xValues: number[];
  y: number;
  displayY: string;
  uncertainty: number | null;
  displayUncertainty: string | null;
};

export type HelpPayload = {
  sections: Array<{
    id: string;
    headerKey: string;
    contentKeys: string[];
  }>;
  dataViewSections: Array<{
    id: string;
    headerKey: string;
    contentKeys: string[];
  }>;
  sectionsHintKey: string;
};

export type UpdatesCheckPayload = {
  supported: boolean;
  available: boolean;
  latestVersion: string | null;
  currentVersion?: string;
};

export type UpdatesApplyPayload = {
  supported: boolean;
  success: boolean;
  messageKey: string | null;
  message: string | null;
  restartRequired: boolean;
};
