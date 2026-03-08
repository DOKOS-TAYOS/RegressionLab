import type { ConfigSchemaItem } from "@/types";

function normalizeBooleanString(value: unknown): "true" | "false" | null {
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (normalized === "true" || normalized === "false") {
      return normalized;
    }
  }
  return null;
}

export function isBooleanSchemaItem(item: ConfigSchemaItem): boolean {
  if (item.cast_type === "bool") {
    return true;
  }

  const normalizedOptions = (item.options ?? [])
    .map((option) => normalizeBooleanString(option))
    .filter((option): option is "true" | "false" => option !== null);

  return normalizedOptions.length === 2 && new Set(normalizedOptions).size === 2;
}

export function parseStoredBoolean(value: unknown, fallback: unknown = false): boolean {
  return (normalizeBooleanString(value) ?? normalizeBooleanString(fallback) ?? "false") === "true";
}

export function stringifyStoredBoolean(value: boolean): "true" | "false" {
  return value ? "true" : "false";
}
