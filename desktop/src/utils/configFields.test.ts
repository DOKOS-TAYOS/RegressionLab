import { describe, expect, it } from "vitest";

import type { ConfigSchemaItem } from "@/types";
import { isBooleanSchemaItem, parseStoredBoolean, stringifyStoredBoolean } from "@/utils/configFields";

describe("configFields", () => {
  it("detects boolean items by cast_type", () => {
    const item: ConfigSchemaItem = {
      key: "LOG_CONSOLE",
      default: true,
      cast_type: "bool",
    };

    expect(isBooleanSchemaItem(item)).toBe(true);
  });

  it("detects boolean items by true/false options", () => {
    const item: ConfigSchemaItem = {
      key: "EXAMPLE",
      default: "true",
      cast_type: "str",
      options: ["true", "false"],
    };

    expect(isBooleanSchemaItem(item)).toBe(true);
  });

  it("parses and serializes stored boolean values robustly", () => {
    expect(parseStoredBoolean("TRUE")).toBe(true);
    expect(parseStoredBoolean(" false ")).toBe(false);
    expect(parseStoredBoolean(undefined, true)).toBe(true);
    expect(stringifyStoredBoolean(true)).toBe("true");
    expect(stringifyStoredBoolean(false)).toBe("false");
  });
});
