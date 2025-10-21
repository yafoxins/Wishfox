import { useEffect } from "react";

import { applyTelegramTheme, getTelegramWebApp } from "../lib/telegram";

export const useTelegramTheme = () => {
  useEffect(() => {
    const root = document.documentElement;
    applyTelegramTheme(root);

    const webApp = getTelegramWebApp();
    const handler = () => applyTelegramTheme(root);
    webApp?.onEvent?.("themeChanged", handler);
    return () => {
      webApp?.offEvent?.("themeChanged", handler);
    };
  }, []);
};
