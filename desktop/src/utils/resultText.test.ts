import { describe, expect, it } from "vitest";

import { parseResultText } from "@/utils/resultText";

describe("parseResultText", () => {
  it("interleaves parameter values with their confidence intervals", () => {
    const text = `
a=12.3 , σ(a)=0.4
b=5.6 , σ(b)=0.1
R²=0.999999
RMSE=0.0123
χ²=0.0456
χ²\u1D63=0.0228
ν (g.l.)=2
a IC 95%: [11.1, 13.5]
b IC 95%: [5.2, 6.0]
    `;

    const parsed = parseResultText(text);

    expect(parsed.parameterValueLines).toEqual(["a=12.3 , σ(a)=0.4", "b=5.6 , σ(b)=0.1"]);
    expect(parsed.statsLines).toEqual(["R²=0.999999", "RMSE=0.0123", "χ²=0.0456", "χ²\u1D63=0.0228", "ν (g.l.)=2"]);
    expect(parsed.confidenceLines).toEqual(["a IC 95%: [11.1, 13.5]", "b IC 95%: [5.2, 6.0]"]);
    expect(parsed.parameterLines).toEqual([
      "a=12.3 , σ(a)=0.4",
      "a IC 95%: [11.1, 13.5]",
      "b=5.6 , σ(b)=0.1",
      "b IC 95%: [5.2, 6.0]",
    ]);
    expect(parsed.displayStatsLines[3]).toBe("χ²\u1D63=0.0228");
    expect(parsed.displayRawText).toContain("χ²\u1D63=0.0228");
  });

  it("returns all lines as parameter lines when statistics are missing", () => {
    const parsed = parseResultText("a=1 , σ(a)=0.1\nb=2 , σ(b)=0.2");

    expect(parsed.statsLines).toEqual([]);
    expect(parsed.parameterLines).toEqual(["a=1 , σ(a)=0.1", "b=2 , σ(b)=0.2"]);
    expect(parsed.displayParameterLines).toEqual(["a=1 , σ(a)=0.1", "b=2 , σ(b)=0.2"]);
  });

  it("supports legacy mojibake text from previous outputs", () => {
    const parsed = parseResultText(
      "a=1\nRÂ²=0.9\nRMSE=0.1\nÏ‡Â²=0.2\nÏ‡Â²\u1D63=0.3\nÎ½ (g.l.)=4\nlegacy IC 95%: [0, 1]",
    );

    expect(parsed.statsLines).toEqual(["RÂ²=0.9", "RMSE=0.1", "Ï‡Â²=0.2", "Ï‡Â²\u1D63=0.3", "Î½ (g.l.)=4"]);
    expect(parsed.displayStatsLines[3]).toBe("Ï‡Â²\u1D63=0.3");
  });
});
