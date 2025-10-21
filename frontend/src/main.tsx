import React from "react";
import ReactDOM from "react-dom/client";
import { I18nextProvider } from "react-i18next";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import i18n, { initI18n } from "./i18n";
import "./styles/global.css";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

const root = ReactDOM.createRoot(rootElement);

const userLocale =
  window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code ??
  navigator.language?.split("-")[0] ??
  "en";

initI18n(userLocale).then(() => {
  root.render(
    <React.StrictMode>
      <I18nextProvider i18n={i18n}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </I18nextProvider>
    </React.StrictMode>,
  );
});
