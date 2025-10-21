import { useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import localizedFormat from "dayjs/plugin/localizedFormat";
import { useTranslation } from "react-i18next";
import "dayjs/locale/ru";

import type { FeedItem } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { PriorityBadge } from "../components/PriorityBadge";

dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);

interface FeedPageProps {
  feed: FeedItem[];
  t: (key: string) => string;
}

const formatPrice = (rawValue: string, locale: string) => {
  const compact = rawValue.replace(/\s/g, "");
  const cleaned = compact.replace(/[^\d,.-]/g, "");
  const hasComma = cleaned.includes(",");
  const hasDot = cleaned.includes(".");
  let normalized = cleaned;

  if (hasComma && hasDot) {
    normalized = cleaned.replace(/,/g, "");
  } else if (hasComma) {
    normalized = cleaned.replace(/,/g, ".");
  }

  const numericValue = Number(normalized);

  if (Number.isFinite(numericValue)) {
    const hasFraction = normalized.includes(".");
    const resolvedLocale = locale.includes("ru") ? "ru-RU" : "en-US";
    return new Intl.NumberFormat(resolvedLocale, {
      minimumFractionDigits: hasFraction ? 2 : 0,
      maximumFractionDigits: 2,
    }).format(numericValue);
  }

  return rawValue;
};

const getFallbackInitial = (displayName: string) => {
  const trimmed = displayName.trim();
  if (!trimmed) return "*";
  return trimmed.charAt(0).toUpperCase();
};

export const FeedPage: React.FC<FeedPageProps> = ({ feed, t }) => {
  const { t: translate, i18n } = useTranslation();
  const activeLanguage = i18n.language || "en";
  const localeCode = activeLanguage.includes("ru") ? "ru" : "en";

  useEffect(() => {
    dayjs.locale(localeCode);
  }, [localeCode]);

  if (!feed.length) {
    return (
      <EmptyState
        title={t("feed.empty_title")}
        description={t("feed.empty_body")}
        illustration="*"
      />
    );
  }

  return (
    <div className="feed-list">
      {feed.map((item) => {
        const statusLabel = translate(`wishlist.status.${item.wish.status}`);
        const relativeTimeLabel = dayjs(item.created_at).locale(localeCode).fromNow();
        const preciseTime = dayjs(item.created_at).locale(localeCode).format("LLL");
        const formattedPrice = item.wish.price ? formatPrice(item.wish.price, activeLanguage) : null;

        return (
          <article key={`${item.actor.id}-${item.wish.id}`} className="cozy-card fade-in feed-card">
            <header className="feed-card__header">
              <div className="feed-card__actor">
                <div className="feed-card__avatar">
                  {item.actor.avatar_url ? (
                    <img
                      src={item.actor.avatar_url}
                      alt={translate("feed.avatar_alt", { name: item.actor.display_name })}
                      loading="lazy"
                    />
                  ) : (
                    <span className="feed-card__avatar-fallback">{getFallbackInitial(item.actor.display_name)}</span>
                  )}
                </div>
                <div>
                  <div className="feed-card__actor-name">{item.actor.display_name}</div>
                  <div className="feed-card__action">{translate(`feed.activity.${item.action}`)}</div>
                </div>
              </div>
              <time className="feed-card__time" dateTime={item.created_at} title={preciseTime}>
                {relativeTimeLabel}
              </time>
            </header>

            <div className="feed-card__body">
              {item.wish.image_url && (
                <img
                  src={item.wish.image_url}
                  alt={translate("feed.image_alt", { title: item.wish.title })}
                  className="feed-card__image"
                  loading="lazy"
                />
              )}
              <div className="feed-card__content">
                <div className="feed-card__title-row">
                  <h3 className="feed-card__title">{item.wish.title}</h3>
                  <PriorityBadge priority={item.wish.priority} />
                </div>
                {item.wish.description && (
                  <p className="feed-card__description">{item.wish.description}</p>
                )}
                <div className="feed-card__meta">
                  <span className="chip chip-muted">{translate("feed.status_chip", { status: statusLabel })}</span>
                  {formattedPrice && (
                    <span className="chip chip-info">{translate("feed.price_chip", { value: formattedPrice })}</span>
                  )}
                  {item.wish.url && (
                    <a
                      href={item.wish.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="link-button"
                    >
                      {translate("feed.open_link")}
                    </a>
                  )}
                </div>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
};
