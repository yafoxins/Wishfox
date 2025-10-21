interface SettingsPageProps {
  notifications: {
    newWish: boolean;
    updatedWish: boolean;
    digest: boolean;
  };
  onToggle: (key: keyof SettingsPageProps["notifications"]) => void;
  language: string;
  onLanguageChange: (locale: string) => void;
  t: (key: string) => string;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ notifications, onToggle, language, onLanguageChange, t }) => {
  return (
    <div className="cozy-card fade-in" style={{ display: "grid", gap: 20 }}>
      <section style={{ display: "grid", gap: 12 }}>
        <h3 style={{ margin: 0 }}>{t("settings.notifications")}</h3>
        {(
          [
            ["newWish", t("settings.new_wish")],
            ["updatedWish", t("settings.updated_wish")],
            ["digest", t("settings.digest")],
          ] as const
        ).map(([key, label]) => (
          <label
            key={key}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              background: "rgba(15,23,42,0.04)",
              padding: "12px 16px",
              borderRadius: "16px",
              border: "1px solid rgba(15,23,42,0.08)",
            }}
          >
            <span>{label}</span>
            <input
              type="checkbox"
              checked={notifications[key]}
              onChange={() => onToggle(key)}
              style={{ width: 22, height: 22, accentColor: "var(--tg-link)", cursor: "pointer" }}
            />
          </label>
        ))}
      </section>

      <section style={{ display: "grid", gap: 12 }}>
        <h3 style={{ margin: 0 }}>{t("settings.language")}</h3>
        <div style={{ display: "flex", gap: 12 }}>
          {["en", "ru"].map((locale) => (
            <button
              key={locale}
              type="button"
              onClick={() => onLanguageChange(locale)}
              style={{
                flex: 1,
                padding: "12px",
                borderRadius: "16px",
                background: language === locale ? "var(--tg-button)" : "rgba(15,23,42,0.06)",
                color: language === locale ? "var(--tg-button-text)" : "var(--tg-text)",
                fontWeight: 600,
              }}
            >
              {locale.toUpperCase()}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
};
