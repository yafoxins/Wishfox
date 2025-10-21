import classNames from "classnames";

import "../styles/global.css";

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface LayoutProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  header?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ tabs, activeTab, onTabChange, header, actions, children }) => {
  return (
    <div className="app-shell">
      {header && (
        <header className="layout-header">
          <div className="hero-card">{header}</div>
        </header>
      )}
      {actions && (
        <div className="layout-actions">{actions}</div>
      )}
      <main className="layout-main">{children}</main>
      <nav className="bottom-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={classNames("bottom-nav__button", {
              "bottom-nav__button--active": tab.id === activeTab,
            })}
          >
            <span className="bottom-nav__icon">{tab.icon}</span>
            <span className="bottom-nav__label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};
