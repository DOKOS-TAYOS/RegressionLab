import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { useAppStore } from "@/store/appStore";
import { translate } from "@/i18n";

const navigation = [
  { to: "/", labelKey: "menu.title", exact: true },
  { to: "/data", labelKey: "menu.view_data" },
  { to: "/help", labelKey: "menu.information" },
  { to: "/config", labelKey: "menu.config" },
];

const SIDEBAR_STORAGE_KEY = "regressionlab.sidebarCollapsed";

export function Shell() {
  const activeLanguage = useAppStore((state) => state.activeLanguage);
  const banner = useAppStore((state) => state.banner);
  const setBanner = useAppStore((state) => state.setBanner);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
  });
  const bannerDetails =
    typeof banner?.details === "string" ? banner.details : banner?.details ? JSON.stringify(banner.details, null, 2) : null;

  useEffect(() => {
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, sidebarCollapsed ? "true" : "false");
  }, [sidebarCollapsed]);

  return (
    <div className={`app-shell ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        <div className="sidebar-header">
          <div className="brand-block">
            <h1>{translate(activeLanguage, "menu.title")}</h1>
          </div>
          <button
            aria-label={translate(activeLanguage, "desktop.collapse_sidebar")}
            className="sidebar-toggle-button"
            onClick={() => setSidebarCollapsed(true)}
            title={translate(activeLanguage, "desktop.collapse_sidebar")}
            type="button"
          >
            <span aria-hidden="true">‹</span>
          </button>
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

      <main className={`content-shell ${sidebarCollapsed ? "sidebar-hidden" : ""}`}>
        {sidebarCollapsed ? (
          <button
            aria-label={translate(activeLanguage, "desktop.expand_sidebar")}
            className="sidebar-reopen-button"
            onClick={() => setSidebarCollapsed(false)}
            title={translate(activeLanguage, "desktop.expand_sidebar")}
            type="button"
          >
            <span aria-hidden="true">›</span>
          </button>
        ) : null}
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
