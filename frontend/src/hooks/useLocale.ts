import { useCallback } from "react";
import { useTranslation } from "react-i18next";

export const useLocale = () => {
  const { i18n } = useTranslation();

  const setLocale = useCallback(
    async (locale: string) => {
      await i18n.changeLanguage(locale);
    },
    [i18n],
  );

  return {
    locale: i18n.language,
    setLocale,
  };
};
