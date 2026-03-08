export type ParsedResultText = {
  rawText: string;
  parameterValueLines: string[];
  statsLines: string[];
  confidenceLines: string[];
  parameterLines: string[];
};

export function parseResultText(rawText: string): ParsedResultText {
  const normalizedText = rawText.replace(/\r\n/g, "\n").trim();
  const lines = normalizedText
    ? normalizedText
        .split("\n")
        .map((line) => line.trimEnd())
        .filter((line) => line.trim().length > 0)
    : [];

  const statsStart = lines.findIndex((line) => line.includes("R²"));
  if (statsStart < 0) {
    return {
      rawText: normalizedText,
      parameterValueLines: lines,
      statsLines: [],
      confidenceLines: [],
      parameterLines: lines,
    };
  }

  const statsLines = lines.slice(statsStart, statsStart + 5);
  const parameterValueLines = lines.slice(0, statsStart);
  const confidenceLines = lines.slice(statsStart + 5);

  return {
    rawText: normalizedText,
    parameterValueLines,
    statsLines,
    confidenceLines,
    parameterLines: [...parameterValueLines, ...confidenceLines],
  };
}
