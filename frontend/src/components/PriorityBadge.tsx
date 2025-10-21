import type { Priority } from "../api/types";
import { useTranslation } from "react-i18next";

export const PriorityBadge: React.FC<{ priority: Priority }> = ({ priority }) => {
  const { t } = useTranslation();
  return (
    <span className={`chip ${priority}`}>
      <span style={{ fontWeight: 700 }}>{t(`wishlist.priority.${priority}`)}</span>
    </span>
  );
};
