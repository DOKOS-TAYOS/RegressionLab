import { describe, expect, it } from "vitest";

import { translate } from "@/i18n";

describe("translate", () => {
  it("falls back to the key when the translation is missing", () => {
    expect(translate("en", "missing.translation.key")).toBe("missing.translation.key");
  });

  it("formats template params", () => {
    expect(translate("en", "workflow.fitting_title", { name: "example" })).toContain("example");
  });
});
