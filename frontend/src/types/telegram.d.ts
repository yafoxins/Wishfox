interface TelegramThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
}

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
}

interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: TelegramUser;
  };
  colorScheme: "light" | "dark";
  themeParams: TelegramThemeParams;
  platform: string;
  version: string;
  ready(): void;
  expand(): void;
  close(): void;
  enableClosingConfirmation(): void;
  disableClosingConfirmation(): void;
  showPopup(params: { title: string; message: string; buttons: { id: string; type: string; text: string }[] }): void;
  onEvent?(event: string, handler: () => void): void;
  offEvent?(event: string, handler: () => void): void;
  MainButton: {
    setText(text: string): void;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
  };
  HapticFeedback?: {
    selectionChanged(): void;
    impactOccurred(style: "light" | "medium" | "heavy" | "rigid" | "soft"): void;
  };
}

interface Telegram {
  WebApp: TelegramWebApp;
}

interface Window {
  Telegram: Telegram;
}
