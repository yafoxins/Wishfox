export const getTelegramWebApp = (): TelegramWebApp | undefined => {
  if (typeof window === "undefined") {
    return undefined;
  }
  return window.Telegram?.WebApp;
};

export const getInitData = (): string | undefined => {
  return getTelegramWebApp()?.initData;
};

export const applyTelegramTheme = (root: HTMLElement, fallback: "light" | "dark" = "light") => {
  const webApp = getTelegramWebApp();
  const theme = webApp?.themeParams ?? {};
  const colorScheme = webApp?.colorScheme ?? fallback;

  root.style.setProperty("--tg-bg", theme.bg_color ?? (colorScheme === "dark" ? "#0d1117" : "#f5f7fb"));
  root.style.setProperty("--tg-text", theme.text_color ?? (colorScheme === "dark" ? "#f0f6fc" : "#161616"));
  root.style.setProperty("--tg-hint", theme.hint_color ?? (colorScheme === "dark" ? "#8b949e" : "#667085"));
  root.style.setProperty("--tg-link", theme.link_color ?? "#2a63f6");
  root.style.setProperty("--tg-button", theme.button_color ?? "#2a63f6");
  root.style.setProperty("--tg-button-text", theme.button_text_color ?? "#ffffff");
  root.style.setProperty("--tg-secondary-bg", theme.secondary_bg_color ?? (colorScheme === "dark" ? "#161b22" : "#ffffff"));
  root.dataset.theme = colorScheme;
};

export const expandApp = () => {
  const webApp = getTelegramWebApp();
  if (!webApp) return;
  webApp.ready();
  webApp.expand();
};

export const getStartParam = (): string | undefined => {
  const webApp = getTelegramWebApp();
  // @ts-ignore - initDataUnsafe is available in WebApp
  return webApp?.initDataUnsafe?.start_param ?? undefined;
};

export const buildDeepLink = (username?: string): string | undefined => {
  // __BOT_NAME__ is injected by Vite define
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const bot = typeof __BOT_NAME__ !== "undefined" ? __BOT_NAME__ : "";
  if (!bot) return undefined;
  return `https://t.me/${bot}?startapp=${username ?? ""}`;
};

const resolveLocale = (webApp: TelegramWebApp | undefined) => {
  // @ts-ignore - initDataUnsafe exists in Telegram WebApp
  const languageCode: string | undefined = webApp?.initDataUnsafe?.user?.language_code;
  if (!languageCode) return "en";
  return languageCode.startsWith("ru") ? "ru" : "en";
};

export const shareDeepLink = async (telegramUsername?: string | null) => {
  const webApp = getTelegramWebApp();
  const locale = resolveLocale(webApp);
  const messages = {
    en: {
      missingUsername: "Add a Telegram username in your profile to share your wishlist.",
      copied: "Link copied. Share it with friends in Telegram!",
    },
    ru: {
      missingUsername: "Add a Telegram username in your profile to share your wishlist.",
      copied: "Link copied. Share it with friends in Telegram!",
    },
  } as const;
  const text = messages[locale] ?? messages.en;

  if (!telegramUsername) {
    if (webApp?.showPopup) webApp.showPopup({ title: "", message: text.missingUsername });
    else alert(text.missingUsername);
    return;
  }

  const url = buildDeepLink(telegramUsername);
  if (!url) return;
  try {
    await navigator.clipboard.writeText(url);
    if (webApp?.showPopup) webApp.showPopup({ title: "", message: text.copied });
    else alert(text.copied);
  } catch {
    window.open(url, "_blank");
  }
};
