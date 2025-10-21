import classNames from "classnames";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";

import type { Wish } from "../api/types";
import { PriorityBadge } from "./PriorityBadge";
import { IconEdit } from "./icons";

interface WishCardProps {
  wish: Wish;
  onEdit?: (wish: Wish) => void;
  onDelete?: (wish: Wish) => void;
  onToggleStatus?: (wish: Wish) => void;
}

export const WishCard: React.FC<WishCardProps> = ({ wish, onEdit, onDelete, onToggleStatus }) => {
  const { t } = useTranslation();
  return (
    <article
      className={classNames("cozy-card", "fade-in")}
      style={{
        marginBottom: 16,
        display: "flex",
        gap: 16,
        alignItems: "flex-start",
        flexWrap: "wrap",
      }}
    >
      <div
        style={{
          width: 80,
          height: 80,
          borderRadius: "18px",
          background: wish.image_url
            ? `url(${wish.image_url}) center/cover`
            : "linear-gradient(135deg, rgba(42,99,246,0.12), rgba(180,70,226,0.12))",
          flexShrink: 0,
        }}
      />
      <div style={{ flex: 1, minWidth: 0 }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 8,
            flexWrap: "wrap",
          }}
        >
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>{wish.title}</h3>
          <PriorityBadge priority={wish.priority} />
        </header>
        {wish.description && (
          <p style={{ margin: "8px 0 0", fontSize: 13, color: "var(--tg-hint)" }}>{wish.description}</p>
        )}
        <footer style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
          <span className="chip" style={{ background: "rgba(100,116,139,0.12)" }}>
            {t(`wishlist.status.${wish.status}`)}
          </span>
          {wish.price && (
            <span className="chip" style={{ background: "rgba(42,99,246,0.12)", color: "var(--tg-link)" }}>
              {t("wishlist.form.price")} {wish.price}
            </span>
          )}
          <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--tg-hint)" }}>
            {dayjs().format("DD MMM")}
          </span>
          {(onEdit || onDelete || onToggleStatus) && (
            <div style={{ display: "flex", gap: 8 }}>
              {onToggleStatus && (
                <button
                  type="button"
                  onClick={() => onToggleStatus(wish)}
                  style={{
                    borderRadius: "12px",
                    padding: "6px 10px",
                    background: "rgba(42, 99, 246, 0.12)",
                    color: "var(--tg-link)",
                    fontWeight: 600,
                  }}
                >
                  TOGGLE
                </button>
              )}
              {onEdit && (
                <button
                  type="button"
                  onClick={() => onEdit(wish)}
                  aria-label="edit wish"
                  title="Edit"
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 12,
                    background: "rgba(42,99,246,0.12)",
                    color: "var(--tg-link)",
                    display: "grid",
                    placeItems: "center",
                  }}
                >
                  <IconEdit size={18} />
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  onClick={() => onDelete(wish)}
                  style={{
                    borderRadius: "12px",
                    padding: "6px 10px",
                    background: "rgba(214, 92, 92, 0.16)",
                    color: "var(--tg-hint)",
                    fontWeight: 600,
                  }}
                >
                  REMOVE
                </button>
              )}
            </div>
          )}
        </footer>
        {/* tags on a separate row under status/price */}
        {wish.tags.length > 0 && (
          <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
            {wish.tags.map((tag) => (
              <span key={tag} className="chip" style={{ background: "rgba(15,23,42,0.08)", color: "var(--tg-hint)" }}>
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
};
