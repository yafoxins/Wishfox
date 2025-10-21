import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./en.json";
import ru from "./ru";

const resources = {
  en: { translation: en },
  ru: { translation: ru }
} as const;

export const initI18n = async (initialLocale: string | undefined) => {
  if (!i18n.isInitialized) {
    await i18n.use(initReactI18next).init({
      resources,
      lng: initialLocale ?? "en",
      fallbackLng: "en",
      interpolation: {
        escapeValue: false
      }
    });
  } else if (initialLocale) {
    await i18n.changeLanguage(initialLocale);
  }
  return i18n;
};

export default i18n;
