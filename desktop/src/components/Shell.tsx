import { NavLink, Outlet } from "react-router-dom";

import { useAppStore } from "@/store/appStore";
import { translate } from "@/i18n";

const navigation = [
  { to: "/", labelKey: "menu.title", exact: true },
  { to: "/data", labelKey: "menu.view_data" },
  { to: "/help", labelKey: "menu.information" },
  { to: "/config", labelKey: "menu.config" },
];

export function Shell() {
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const banner = useAppStore((state) => state.banner);
  const setBanner = useAppStore((state) => state.setBanner);
  const bannerDetails =
    typeof banner?.details === "string" ? banner.details : banner?.details ? JSON.stringify(banner.details, null, 2) : null;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <h1>{translate(activeLanguage, "menu.title")}</h1>
        </div>

        <nav className="nav-list">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.exact}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            >
              {translate(activeLanguage, item.labelKey)}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="content-shell">
        {banner ? (
          <div className={`banner ${banner.tone}`}>
            <div>
              <strong>{translate(activeLanguage, banner.messageKey, banner.params)}</strong>
              {bannerDetails ? <pre>{bannerDetails}</pre> : null}
            </div>
            <button className="ghost-button" onClick={() => setBanner(null)}>
              {translate(activeLanguage, "desktop.close")}
            </button>
          </div>
        ) : null}
        <Outlet />
      </main>
    </div>
  );
}
