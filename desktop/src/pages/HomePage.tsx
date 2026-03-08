import { Link } from "react-router-dom";

import { useAppStore } from "@/store/appStore";
import { translate } from "@/i18n";

const logoUrl = new URL("../../../images/RegressionLab_logo.png", import.meta.url).href;

const cards = [
  {
    mode: "normal",
    titleKey: "menu.normal_fitting",
    copyKey: "desktop.mode_copy_normal",
  },
  {
    mode: "multiple",
    titleKey: "menu.multiple_datasets",
    copyKey: "desktop.mode_copy_multiple",
  },
  {
    mode: "checker",
    titleKey: "menu.checker_fitting",
    copyKey: "desktop.mode_copy_checker",
  },
  {
    mode: "total",
    titleKey: "menu.total_fitting",
    copyKey: "desktop.mode_copy_total",
  },
  {
    mode: "data",
    titleKey: "menu.view_data",
    copyKey: "desktop.mode_copy_data",
  },
];

export function HomePage() {
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const bootstrap = useAppStore((state) => state.bootstrap);

  return (
    <section className="page-grid">
      <header className="home-hero">
        <img
          src={logoUrl}
          alt={translate(activeLanguage, "menu.title")}
          className="home-hero-logo"
        />
        <div className="home-version-badge">
          <span className="eyebrow">{translate(activeLanguage, "desktop.version")}</span>
          <strong>
            {translate(activeLanguage, "desktop.version_short", {
              version: bootstrap?.version ?? "-",
            })}
          </strong>
        </div>
      </header>

      <div className="mode-card-grid">
        {cards.map((card) => (
          <Link
            key={card.mode}
            to={card.mode === "data" ? "/data" : `/mode/${card.mode}`}
            className="mode-card"
          >
            <span className="eyebrow">{translate(activeLanguage, "desktop.mode_label")}</span>
            <h3>{translate(activeLanguage, card.titleKey)}</h3>
            <p>{translate(activeLanguage, card.copyKey)}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
