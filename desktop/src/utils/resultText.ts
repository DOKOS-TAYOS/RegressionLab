type ParsedResultText = {
  rawText: string;
  displayRawText: string;
  parameterValueLines: string[];
  displayParameterValueLines: string[];
  statsLines: string[];
  displayStatsLines: string[];
  confidenceLines: string[];
  displayConfidenceLines: string[];
  parameterLines: string[];
  displayParameterLines: string[];
};

function interleaveLines(primaryLines: string[], secondaryLines: string[]): string[] {
  const combined: string[] = [];
  const total = Math.max(primaryLines.length, secondaryLines.length);

  for (let index = 0; index < total; index += 1) {
    if (primaryLines[index]) {
      combined.push(primaryLines[index]);
    }
    if (secondaryLines[index]) {
      combined.push(secondaryLines[index]);
    }
  }

  return combined;
}

function isStatsStartLine(line: string): boolean {
  return line.includes("R²") || line.includes("RÂ²") || line.includes("RÃ‚Â²");
}

export function parseResultText(rawText: string): ParsedResultText {
  const normalizedText = rawText.replace(/\r\n/g, "\n").trim();
  const lines = normalizedText
    ? normalizedText
        .split("\n")
        .map((line) => line.trimEnd())
        .filter((line) => line.trim().length > 0)
    : [];
  const displayLines = lines;

  const statsStart = lines.findIndex(isStatsStartLine);
  if (statsStart < 0) {
    return {
      rawText: normalizedText,
      displayRawText: displayLines.join("\n"),
      parameterValueLines: lines,
      displayParameterValueLines: displayLines,
      statsLines: [],
      displayStatsLines: [],
      confidenceLines: [],
      displayConfidenceLines: [],
      parameterLines: lines,
      displayParameterLines: displayLines,
    };
  }

  const statsLines = lines.slice(statsStart, statsStart + 5);
  const parameterValueLines = lines.slice(0, statsStart);
  const confidenceLines = lines.slice(statsStart + 5);
  const displayStatsLines = displayLines.slice(statsStart, statsStart + 5);
  const displayParameterValueLines = displayLines.slice(0, statsStart);
  const displayConfidenceLines = displayLines.slice(statsStart + 5);

  return {
    rawText: normalizedText,
    displayRawText: displayLines.join("\n"),
    parameterValueLines,
    displayParameterValueLines,
    statsLines,
    displayStatsLines,
    confidenceLines,
    displayConfidenceLines,
    parameterLines: interleaveLines(parameterValueLines, confidenceLines),
    displayParameterLines: interleaveLines(displayParameterValueLines, displayConfidenceLines),
  };
}
