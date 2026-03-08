import { useEffect, useMemo, useState } from "react";

import { desktopClient } from "@/api/client";
import { translate } from "@/i18n";
import { useAppStore } from "@/store/appStore";
import { isBooleanSchemaItem, parseStoredBoolean, stringifyStoredBoolean } from "@/utils/configFields";

function getSection(key: string): string {
  if (key === "LANGUAGE") {
    return "language";
  }
  if (key.startsWith("UI_")) {
    return "ui";
  }
  if (key.startsWith("PLOT_") || key === "DPI") {
    return "plot";
  }
  if (key.startsWith("FONT_")) {
    return "font";
  }
  if (key.startsWith("FILE_")) {
    return "paths";
  }
  if (key === "DONATIONS_URL") {
    return "links";
  }
  if (key.startsWith("CHECK_") || key === "UPDATE_CHECK_URL") {
    return "updates";
  }
  if (key.startsWith("LOG_")) {
    return "logging";
  }
  return "other";
}

export function ConfigPage() {
  const bootstrap = useAppStore((state) => state.bootstrap);
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const setBanner = useAppStore((state) => state.setBanner);
  const setLanguage = useAppStore((state) => state.setLanguage);
  const [values, setValues] = useState<Record<string, string>>(bootstrap?.config.values ?? {});
  const [saving, setSaving] = useState(false);
  const schema = bootstrap?.config.schema ?? [];

  useEffect(() => {
    if (bootstrap) {
      setValues(bootstrap.config.values);
    }
  }, [bootstrap]);

  const sections = useMemo(() => {
    const ordered: Record<string, typeof schema> = {};
    schema.forEach((item) => {
      const section = getSection(item.key);
      ordered[section] = ordered[section] ?? [];
      ordered[section].push(item);
    });
    return ordered;
  }, [schema]);

  const updateValue = (key: string, value: string) => {
    setValues((current) => ({ ...current, [key]: value }));
  };

  const onSave = async () => {
    setSaving(true);
    try {
      const response = await desktopClient.updateConfig(values);
      setValues(response.values);
      if (response.values.LANGUAGE) {
        setLanguage(response.values.LANGUAGE);
      }
      setBanner({
        tone: "success",
        messageKey: "desktop.config_saved",
      });
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-grid config-layout">
      <div className="panel wide">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">{translate(activeLanguage, "desktop.config")}</span>
            <h2>{translate(activeLanguage, "config.title")}</h2>
          </div>
          <div className="row actions">
            <button className="ghost-button" onClick={() => void window.desktopApi.relaunch()}>
              {translate(activeLanguage, "desktop.restart_app")}
            </button>
            <button className="primary-button" disabled={saving} onClick={() => void onSave()}>
              {saving ? translate(activeLanguage, "desktop.saving") : translate(activeLanguage, "dialog.accept")}
            </button>
          </div>
        </div>

        <div className="config-sections">
          {Object.entries(sections).map(([section, items]) => (
            <section className="subpanel" key={section}>
              <div className="section-title-row">
                <h3>{translate(activeLanguage, `config.section_${section}`)}</h3>
              </div>
              <div className="field-grid">
                {items.map((item) => {
                  const currentValue = values[item.key] ?? String(item.default);

                  if (isBooleanSchemaItem(item)) {
                    const checked = parseStoredBoolean(values[item.key], item.default);

                    return (
                      <div className="field checkbox-field" key={item.key}>
                        <span>{translate(activeLanguage, `config.label_${item.key}`)}</span>
                        <label className="checkbox-control">
                          <input
                            checked={checked}
                            onChange={(event) => updateValue(item.key, stringifyStoredBoolean(event.target.checked))}
                            type="checkbox"
                          />
                          <span>{translate(activeLanguage, checked ? "menu.yes" : "menu.no")}</span>
                        </label>
                        <small>{translate(activeLanguage, `config.desc_${item.key}`)}</small>
                      </div>
                    );
                  }

                  return (
                    <label className="field" key={item.key}>
                      <span>{translate(activeLanguage, `config.label_${item.key}`)}</span>
                      {item.options ? (
                        <select
                          value={currentValue}
                          onChange={(event) => updateValue(item.key, event.target.value)}
                        >
                          {item.options.map((option) => (
                            <option key={String(option)} value={String(option)}>
                              {String(option)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <input
                          value={currentValue}
                          onChange={(event) => updateValue(item.key, event.target.value)}
                        />
                      )}
                      <small>{translate(activeLanguage, `config.desc_${item.key}`)}</small>
                    </label>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}
