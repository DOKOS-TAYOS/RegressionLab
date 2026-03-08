import { describe, expect, it } from "vitest";

import { parseResultText } from "@/utils/resultText";

describe("parseResultText", () => {
  it("splits parameters, statistics and confidence intervals like the Tkinter output", () => {
    const text = `
a=12.3 , σ(a)=0.4
b=5.6 , σ(b)=0.1
R²=0.999999
RMSE=0.0123
χ²=0.0456
χ²_red=0.0228
ν (g.l.)=2
a IC 95%: [11.1, 13.5]
b IC 95%: [5.2, 6.0]
    `;

    const parsed = parseResultText(text);

    expect(parsed.parameterValueLines).toEqual(["a=12.3 , σ(a)=0.4", "b=5.6 , σ(b)=0.1"]);
    expect(parsed.statsLines).toEqual([
      "R²=0.999999",
      "RMSE=0.0123",
      "χ²=0.0456",
      "χ²_red=0.0228",
      "ν (g.l.)=2",
    ]);
    expect(parsed.confidenceLines).toEqual(["a IC 95%: [11.1, 13.5]", "b IC 95%: [5.2, 6.0]"]);
    expect(parsed.parameterLines).toEqual([
      "a=12.3 , σ(a)=0.4",
      "b=5.6 , σ(b)=0.1",
      "a IC 95%: [11.1, 13.5]",
      "b IC 95%: [5.2, 6.0]",
    ]);
  });

  it("returns all lines as parameter lines when statistics are missing", () => {
    const parsed = parseResultText("a=1 , σ(a)=0.1\nb=2 , σ(b)=0.2");

    expect(parsed.statsLines).toEqual([]);
    expect(parsed.parameterLines).toEqual(["a=1 , σ(a)=0.1", "b=2 , σ(b)=0.2"]);
  });
});
