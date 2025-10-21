import type { Subscription } from "../api/types";
import { EmptyState } from "../components/EmptyState";

interface SubscriptionsPageProps {
  subscriptions: Subscription[];
  onUnsubscribe?: (username: string) => void;
  onSubscribe?: (username: string) => void;
  onViewWishlist?: (target: Subscription["target"]) => void;
  onViewProfile?: (target: Subscription["target"]) => void;
  activeHandle?: string;
  t: (key: string) => string;
}

export const SubscriptionsPage: React.FC<SubscriptionsPageProps> = ({
  subscriptions,
  onUnsubscribe,
  onSubscribe,
  onViewWishlist,
  onViewProfile,
  activeHandle,
  t,
}) => {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div className="cozy-card subscription-input">
        <input
          id="subscribe-input"
          placeholder="@username"
          style={{ flex: 1, padding: "12px 16px", borderRadius: 14, border: "1px solid rgba(15,23,42,0.1)", background: "rgba(15,23,42,0.04)", color: "var(--tg-text)" }}
        />
        {onSubscribe && (
          <button
            type="button"
            onClick={() => {
              const el = document.getElementById("subscribe-input") as HTMLInputElement | null;
              const raw = el?.value.trim() ?? "";
              const username = raw.startsWith("@") ? raw.slice(1) : raw;
              if (username) onSubscribe(username);
            }}
            style={{ padding: "12px 16px", borderRadius: 14, background: "var(--tg-button)", color: "var(--tg-button-text)", fontWeight: 600 }}
          >
            {t("actions.subscribe")}
          </button>
        )}
      </div>

      {!subscriptions.length ? (
        <EmptyState
          title={t("subscriptions.empty_title")}
          description={t("subscriptions.empty_body")}
          illustration="*"
        />
      ) : null}

      {subscriptions.map((subscription) => {
        const baseHandle =
          subscription.target?.tg_username ??
          subscription.target?.custom_username ??
          subscription.target?.username ??
          (subscription.target ? String(subscription.target.id) : "");
        const displayHandle =
          subscription.target?.tg_username ??
          subscription.target?.custom_username ??
          subscription.target?.username ??
          "";
        const isActive = Boolean(activeHandle && baseHandle && activeHandle === baseHandle);

        return (
        <div
          key={subscription.id}
          className="cozy-card fade-in subscription-card"
          style={{
            border: isActive ? "1.5px solid rgba(42,99,246,0.35)" : "1px solid rgba(15,23,42,0.04)",
          }}
        >
          <div className="subscription-card__info">
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: "16px",
                background: subscription.target?.avatar_url
                  ? `url(${subscription.target.avatar_url}) center/cover`
                  : "linear-gradient(135deg, rgba(52,211,153,0.16), rgba(59,130,246,0.16))",
              }}
            />
            <div>
              <div style={{ fontWeight: 600 }}>{subscription.target?.display_name}</div>
              <div style={{ fontSize: 12, color: "var(--tg-hint)" }}>
                {displayHandle ? `@${displayHandle}` : ""}
              </div>
            </div>
          </div>
          <div className="subscription-card__actions">
            {onViewWishlist && subscription.target && baseHandle && (
              <button
                type="button"
                onClick={() => {
                  if (subscription.target && baseHandle) onViewWishlist(subscription.target);
                }}
                style={{
                  padding: "10px 16px",
                  borderRadius: "16px",
                  background: "rgba(42, 99, 246, 0.12)",
                  color: "var(--tg-link)",
                  fontWeight: 600,
                }}
              >
                {t("actions.view")}
              </button>
            )}
            {onViewProfile && subscription.target && baseHandle && (
              <button
                type="button"
                onClick={() => {
                  if (subscription.target && baseHandle) onViewProfile(subscription.target);
                }}
                style={{
                  padding: "10px 16px",
                  borderRadius: "16px",
                  background: "rgba(15, 23, 42, 0.08)",
                  color: "var(--tg-text)",
                  fontWeight: 600,
                }}
              >
                {t("actions.view_profile")}
              </button>
            )}
            {onUnsubscribe && (
              <button
                type="button"
                onClick={() => onUnsubscribe(baseHandle)}
                style={{
                  padding: "10px 16px",
                  borderRadius: "16px",
                  background: "rgba(15,23,42,0.08)",
                  color: "var(--tg-hint)",
                  fontWeight: 600,
                }}
              >
                {t("actions.unsubscribe")}
              </button>
            )}
          </div>
        </div>
        );
      })}
    </div>
  );
};

