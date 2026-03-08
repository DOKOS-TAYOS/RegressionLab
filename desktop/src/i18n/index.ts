import de from "@locales/de.json";
import en from "@locales/en.json";
import es from "@locales/es.json";

const locales = {
  de,
  en,
  es,
} as const;

type LocaleCode = keyof typeof locales;

function getValue(source: Record<string, unknown>, path: string): string | null {
  const value = path.split(".").reduce<unknown>((current, key) => {
    if (current && typeof current === "object" && key in current) {
      return (current as Record<string, unknown>)[key];
    }
    return null;
  }, source);

  return typeof value === "string" ? value : null;
}

export function translate(
  language: string,
  key: string,
  params?: Record<string, unknown>,
): string {
  const locale = locales[(language in locales ? language : "es") as LocaleCode];
  const fallback = locales.es;
  const template = getValue(locale as unknown as Record<string, unknown>, key)
    ?? getValue(fallback as unknown as Record<string, unknown>, key)
    ?? key;

  if (!params) {
    return template;
  }

  return template.replace(/\{(\w+)\}/g, (_match, paramKey: string) => {
    const value = params[paramKey];
    return value === undefined || value === null ? `{${paramKey}}` : String(value);
  });
}
