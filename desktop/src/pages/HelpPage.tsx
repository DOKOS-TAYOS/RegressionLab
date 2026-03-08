import { useEffect, useState } from "react";

import { desktopClient } from "@/api/client";
import { HelpSection } from "@/components/HelpSection";
import { FormattedText } from "@/components/FormattedText";
import { translate } from "@/i18n";
import { useAppStore } from "@/store/appStore";
import type { UpdatesCheckPayload } from "@/types";

export function HelpPage() {
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const help = useAppStore((state) => state.help);
  const loadHelp = useAppStore((state) => state.loadHelp);
  const bootstrap = useAppStore((state) => state.bootstrap);
  const setBanner = useAppStore((state) => state.setBanner);
  const [updates, setUpdates] = useState<UpdatesCheckPayload | null>(null);

  useEffect(() => {
    void loadHelp();
  }, []);

  const checkUpdates = async () => {
    try {
      setUpdates(await desktopClient.checkUpdates());
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  const applyUpdates = async () => {
    try {
      const response = await desktopClient.applyUpdates();
      if (response.success && response.restartRequired) {
        await window.desktopApi.relaunch();
      }
      setBanner({
        tone: response.success ? "success" : "error",
        messageKey: response.messageKey ?? "desktop.error.backend",
        details: response.message,
      });
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      setBanner({
        tone: "error",
        messageKey: payload.error?.messageKey ?? "desktop.error.internal",
        details: payload.error?.details,
      });
    }
  };

  return (
    <section className="page-grid">
      <div className="panel">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">{translate(activeLanguage, "desktop.help")}</span>
            <h2>{translate(activeLanguage, "dialog.help_title")}</h2>
          </div>
          {bootstrap && bootstrap.links.donationsUrl ? (
            <button
              className="ghost-button"
              onClick={() => void window.desktopApi.openExternal(bootstrap.links.donationsUrl)}
            >
              {translate(activeLanguage, "dialog.donations")}
            </button>
          ) : null}
        </div>

        <FormattedText
          text={translate(activeLanguage, help?.sectionsHintKey ?? "help.sections_hint")}
          className="muted-note"
        />

        <div className="accordion-stack">
          {(help?.sections ?? []).map((section, index) => (
            <HelpSection
              key={section.id}
              headerKey={section.headerKey}
              contentKeys={section.contentKeys}
              language={activeLanguage}
              defaultOpen={index === 0}
            />
          ))}
        </div>

        <section className="subpanel help-updates-panel">
          <div className="section-title-row">
            <div>
              <span className="eyebrow">{translate(activeLanguage, "desktop.frontend_label")}</span>
              <h3>{translate(activeLanguage, "desktop.updates_title")}</h3>
            </div>
          </div>

          <div className="row actions">
            <button className="primary-button" onClick={() => void checkUpdates()}>
              {translate(activeLanguage, "desktop.check_updates")}
            </button>
            {updates?.supported && updates.available ? (
              <button className="ghost-button" onClick={() => void applyUpdates()}>
                {translate(activeLanguage, "desktop.apply_update")}
              </button>
            ) : null}
          </div>

          {updates ? (
            <div className="inline-note">
              <strong>
                {translate(activeLanguage, updates.supported ? "desktop.updates_supported" : "desktop.updates_disabled")}
              </strong>
              <span>
                {updates.available
                  ? translate(activeLanguage, "desktop.updates_available", { version: updates.latestVersion ?? "-" })
                  : translate(activeLanguage, "desktop.updates_unavailable")}
              </span>
            </div>
          ) : null}
        </section>
      </div>
    </section>
  );
}
