import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

import type { FeedItem, Subscription, WishStatus, Priority, Wish, Wishlist, PublicUser, LinkPreview, User } from "./api/types";
import { BottomSheet } from "./components/BottomSheet";
import { Layout } from "./components/Layout";
import { EmptyState } from "./components/EmptyState";
import { useAuth } from "./context/AuthContext";
import { useLocale } from "./hooks/useLocale";
import { useTelegramTheme } from "./hooks/useTelegramTheme";
import { getStartParam, getTelegramWebApp } from "./lib/telegram";
import { FeedPage } from "./pages/FeedPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SettingsPage } from "./pages/SettingsPage";
import { SubscriptionsPage } from "./pages/SubscriptionsPage";
import { WishlistPage } from "./pages/WishlistPage";
import { IconFeed, IconList, IconSettings, IconSubs, IconUser } from "./components/icons";

type ActiveTab = "wishlist" | "feed" | "subscriptions" | "profile" | "settings";

interface NewWishForm {
  title: string;
  description: string;
  url: string;
  price: string;
  tags: string;
  priority: Priority;
  status: WishStatus;
  imageFile: File | null;
  imagePreview: string | null;
  metadataImageUrl: string | null;
  metadataSourceUrl: string | null;
}

interface ExternalWishlistView {
  handle: string;
  owner?: PublicUser | null;
  wishlist: Wishlist | null;
}

const defaultWishForm: NewWishForm = {
  title: "",
  description: "",
  url: "",
  price: "",
  tags: "",
  priority: "medium",
  status: "planned",
  imageFile: null,
  imagePreview: null,
  metadataImageUrl: null,
  metadataSourceUrl: null,
};

const toPublicUser = (source?: User | PublicUser | Subscription["target"] | null): PublicUser | null => {
  if (!source) return null;
  const base: PublicUser = {
    id: source.id,
    display_name: source.display_name,
    username: "username" in source && source.username ? source.username : "",
    avatar_url: "avatar_url" in source ? source.avatar_url ?? null : null,
    bio: "bio" in source ? source.bio ?? null : null,
  };
  if ("tg_username" in source || "custom_username" in source) {
    const full = source as User;
    const username = full.tg_username ?? full.custom_username ?? full.username ?? base.username;
    return { ...base, username };
  }
  if (!base.username && "username" in source) {
    return { ...base, username: source.username ?? "" };
  }
  return base;
};

export const App: React.FC = () => {
  const { t } = useTranslation();
  const { locale, setLocale } = useLocale();
  const { loading, user, wishlists, refresh, updateUser, api } = useAuth();
  const [activeTab, setActiveTab] = useState<ActiveTab>("wishlist");
  const [filters, setFilters] = useState({ search: "", priority: undefined as Priority | undefined, status: undefined as WishStatus | undefined });
  const [sheetOpen, setSheetOpen] = useState(false);
  const [editWish, setEditWish] = useState<Wish | null>(null);
  const [form, setForm] = useState<NewWishForm>({ ...defaultWishForm });
  const [creating, setCreating] = useState(false);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [notificationsEnabled, setNotificationsEnabled] = useState({
    newWish: true,
    updatedWish: true,
    digest: false,
  });
  const [startParamHandled, setStartParamHandled] = useState(false);
  const [externalView, setExternalView] = useState<ExternalWishlistView | null>(null);
  const [externalLoading, setExternalLoading] = useState(false);
  const [profileView, setProfileView] = useState<{ handle: string; user: PublicUser | null } | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [metadataLoading, setMetadataLoading] = useState(false);

  const showHandleMissingAlert = useCallback(() => {
    const message = t("subscriptions.handle_missing");
    const webApp = getTelegramWebApp();
    if (webApp?.showAlert) {
      webApp.showAlert(message);
    } else if (webApp?.showPopup) {
      webApp.showPopup({ title: "", message });
    } else {
      alert(message);
    }
  }, [t]);

  useTelegramTheme();

  const resetWishlistFilters = useCallback(() => {
    setFilters({ search: "", priority: undefined, status: undefined });
  }, [setFilters]);

  // Prompt to set username if Telegram username is missing
  const [usernamePromptOpen, setUsernamePromptOpen] = useState(false);
  const [customUsername, setCustomUsername] = useState("");

  useEffect(() => {
    if (user && user.requires_custom_username) {
      setUsernamePromptOpen(true);
      setCustomUsername("");
    }
  }, [user]);

  const activeWishlist = useMemo(() => wishlists[0], [wishlists]);

  const fetchFeed = useCallback(async () => {
    const response = await api.get<FeedItem[]>("/feed");
    setFeed(response.data);
  }, [api]);

  const fetchSubscriptions = useCallback(async () => {
    const response = await api.get<Subscription[]>("/subscriptions");
    setSubscriptions(response.data);
  }, [api]);

  useEffect(() => {
    if (!user) return;
    fetchFeed().catch(console.error);
    fetchSubscriptions().catch(console.error);
  }, [user, fetchFeed, fetchSubscriptions]);

  const resetForm = useCallback(() => {
    if (form.imageFile && form.imagePreview) {
      URL.revokeObjectURL(form.imagePreview);
    }
    setForm({ ...defaultWishForm });
  }, [form.imageFile, form.imagePreview]);

  const handleCreateWish = useCallback(async () => {
    if (!activeWishlist) return;
    setCreating(true);
    try {
      let imageUrl: string | undefined;
      if (form.imageFile) {
        const formData = new FormData();
        formData.append("file", form.imageFile);
        const uploadResponse = await api.post<{ url: string }>("/media/upload", formData);
        imageUrl = uploadResponse.data.url;
      }

      const payload = {
        wishlist_id: activeWishlist.id,
        title: form.title,
        description: form.description || undefined,
        url: form.url || undefined,
        price: form.price || undefined,
        priority: form.priority,
        status: form.status,
        image_url: imageUrl,
        tags: form.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      };
      if (editWish) {
        await api.patch(`/wishes/${editWish.id}`, {
          title: form.title || undefined,
          description: form.description || undefined,
          url: form.url || undefined,
          price: form.price || undefined,
          image_url: imageUrl,
          priority: form.priority,
          status: form.status,
          tags: payload.tags,
        });
      } else {
        await api.post("/wishes", payload);
      }
      resetForm();
      setSheetOpen(false);
      setEditWish(null);
      await refresh();
      await fetchFeed();
    } catch (error) {
      console.error("Failed to create wish", error);
    } finally {
      setCreating(false);
    }
  }, [activeWishlist, api, fetchFeed, form, refresh, resetForm, editWish]);

  const handleReorder = useCallback(
    async (orderedWishes: Wish[]) => {
      try {
        const payload = orderedWishes.map((wish, index) => ({
          id: wish.id,
          position: index,
        }));
        await api.post("/wishes/reorder", payload);
        await refresh();
      } catch (error) {
        console.error("Failed to reorder wishes", error);
      }
    },
    [api, refresh],
  );

  const handleDeleteWish = useCallback(async () => {
    if (!editWish) return;
    try {
      await api.delete(`/wishes/${editWish.id}`);
      resetForm();
      setSheetOpen(false);
      setEditWish(null);
      await refresh();
      await fetchFeed();
    } catch (error) {
      console.error("Failed to delete wish", error);
    }
  }, [api, editWish, fetchFeed, refresh, resetForm]);

  const handleUnsubscribe = useCallback(
    async (username: string) => {
      await api.delete(`/subscriptions/${username}`);
      await fetchSubscriptions();
    },
    [api, fetchSubscriptions],
  );

  const handleSubscribe = useCallback(
    async (username: string) => {
      await api.post(`/subscriptions/${username}`);
      await fetchSubscriptions();
    },
    [api, fetchSubscriptions],
  );

  const handleViewSubscriptionWishlist = useCallback(
    async (target: Subscription["target"]) => {
      if (!target) return;
      const handle =
        target.tg_username ??
        target.custom_username ??
        target.username ??
        (target.id ? String(target.id) : "");
      if (!handle) {
        showHandleMissingAlert();
        return;
      }

      setSheetOpen(false);
      setEditWish(null);
      setActiveTab("wishlist");
      const initialOwner = toPublicUser(target);
      setExternalView({ handle, owner: initialOwner, wishlist: null });
      setExternalLoading(true);
      resetWishlistFilters();
      try {
        const wishlistResponse = await api.get<Wishlist>(`/users/${handle}/wishlist`);
        let owner = initialOwner;
        try {
          const userResponse = await api.get<PublicUser>(`/users/${handle}`);
          owner = userResponse.data;
          if (profileView?.handle === handle) {
            setProfileView({ handle, user: owner });
          }
        } catch (error) {
          console.warn("Failed to load user profile", error);
        }
        setExternalView({ handle, owner, wishlist: wishlistResponse.data });
      } catch (error) {
        console.error("Failed to load user wishlist", error);
        setExternalView(null);
      } finally {
        setExternalLoading(false);
      }
    },
    [api, profileView, resetWishlistFilters, showHandleMissingAlert],
  );

  const handleViewProfile = useCallback(
    async (target: Subscription["target"]) => {
      if (!target) return;
      const handle =
        target.tg_username ??
        target.custom_username ??
        target.username ??
        (target.id ? String(target.id) : "");
      if (!handle) {
        showHandleMissingAlert();
        return;
      }

      setExternalView(null);
      setExternalLoading(false);
      resetWishlistFilters();
      setSheetOpen(false);
      setEditWish(null);
      setActiveTab("profile");
      setProfileLoading(true);
      setProfileView({ handle, user: null });
      try {
        const response = await api.get<PublicUser>(`/users/${handle}`);
        setProfileView({ handle, user: response.data });
      } catch (error) {
        console.error("Failed to load profile", error);
        setProfileView({ handle, user: toPublicUser(target) });
      } finally {
        setProfileLoading(false);
      }
    },
    [api, showHandleMissingAlert],
  );

  const handleCloseExternalView = useCallback(() => {
    setExternalView(null);
    setExternalLoading(false);
    resetWishlistFilters();
  }, [resetWishlistFilters]);

  useEffect(() => {
    if (!user || startParamHandled) return;
    const startParam = getStartParam();
    if (!startParam) {
      setStartParamHandled(true);
      return;
    }
    const normalized = startParam.trim();
    if (!normalized) {
      setStartParamHandled(true);
      return;
    }
    const selfIdentifiers = [user.tg_username, user.custom_username, user.username].filter(Boolean) as string[];
    if (selfIdentifiers.includes(normalized)) {
      setStartParamHandled(true);
      return;
    }
    const alreadySubscribed = subscriptions.some((subscription) => {
      const target = subscription.target;
      if (!target) return false;
      const handles = [target.username, target.tg_username, target.custom_username].filter(Boolean) as string[];
      return handles.includes(normalized);
    });
    if (alreadySubscribed) {
      setStartParamHandled(true);
      return;
    }
    handleSubscribe(normalized)
      .catch((error) => {
        console.error("Failed to auto-subscribe", error);
      })
      .finally(() => setStartParamHandled(true));
  }, [handleSubscribe, startParamHandled, subscriptions, user]);

  useEffect(() => {
    if (!sheetOpen) return;
    if (!form.url) return;
    if (metadataLoading) return;

    let parsed: URL;
    try {
      parsed = new URL(form.url);
    } catch {
      return;
    }
    if (!/^https?:/i.test(parsed.protocol)) return;

    const normalizedUrl = parsed.toString();
    if (form.metadataSourceUrl === normalizedUrl) return;

    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setMetadataLoading(true);
      api
        .get<LinkPreview>("/links/preview", {
          params: { url: normalizedUrl },
          signal: controller.signal,
        })
        .then((response) => {
          const preview = response.data;
          setForm((prev) => {
            if (prev.url !== normalizedUrl) return prev;
            const next = { ...prev, metadataSourceUrl: normalizedUrl };
            if (!prev.title && preview.title) {
              next.title = preview.title;
            }
            if (!prev.description && preview.description) {
              next.description = preview.description;
            }
            if (!prev.imageFile && preview.image) {
              next.imagePreview = preview.image;
              next.metadataImageUrl = preview.image;
            } else if (preview.image && !prev.imageFile) {
              next.metadataImageUrl = preview.image;
              next.imagePreview = preview.image;
            }
            return next;
          });
        })
        .catch((error) => {
          if (!controller.signal.aborted) {
            console.warn("Link preview failed", error);
            setForm((prev) => {
              if (prev.url !== normalizedUrl) return prev;
              return { ...prev, metadataSourceUrl: normalizedUrl };
            });
          }
        })
        .finally(() => {
          setMetadataLoading(false);
        });
    }, 600);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [api, form.imageFile, form.metadataSourceUrl, form.url, sheetOpen]);

  const tabs = useMemo(
    () => [
      { id: "wishlist", label: t("tabs.wishlist"), icon: <IconList /> },
      { id: "feed", label: t("tabs.feed"), icon: <IconFeed /> },
      { id: "subscriptions", label: t("tabs.subscriptions"), icon: <IconSubs /> },
      { id: "profile", label: t("tabs.profile"), icon: <IconUser /> },
      { id: "settings", label: t("tabs.settings"), icon: <IconSettings /> },
    ],
    [t],
  );

  const selfPublic = useMemo(() => (user ? toPublicUser(user) : null), [user]);

  if (loading) {
    return (
      <div className="app-shell" style={{ alignItems: "center", justifyContent: "center" }}>
        <EmptyState title={t("app.title")} description={t("app.loading")} illustration="*" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app-shell" style={{ alignItems: "center", justifyContent: "center" }}>
        <EmptyState title={t("app.title")} description={t("app.error")} illustration="*" />
      </div>
    );
  }

  const firstName = user.display_name.split(" ")[0] || user.display_name;
  const ownHandle = user.tg_username ?? user.custom_username ?? user.username ?? "";
  const isExternalWishlistView = activeTab === "wishlist" && externalView !== null;
  const viewingWishlist = isExternalWishlistView ? externalView?.wishlist ?? null : activeWishlist ?? null;
  const viewingOwner = isExternalWishlistView ? externalView?.owner ?? selfPublic : selfPublic;
  const ownerName = viewingOwner?.display_name ?? firstName;
  const handleForWishlist = isExternalWishlistView ? externalView?.handle ?? viewingOwner?.username ?? "" : ownHandle;
  const handleLabel = handleForWishlist ? `@${handleForWishlist}` : "";

  const wishlistMetrics: string[] = [];
  if (viewingWishlist) {
    wishlistMetrics.push(t("app.hero_total_wishes", { count: viewingWishlist.wishes.length }));
  }
  if (!isExternalWishlistView) {
    wishlistMetrics.push(t("app.hero_following", { count: subscriptions.length }));
  }

  const isExternalProfile = activeTab === "profile" && profileView !== null;
  const profileHandle = isExternalProfile ? profileView?.handle ?? "" : ownHandle;
  const profileUserPublic = isExternalProfile ? profileView?.user : selfPublic;
  const profileName = profileUserPublic?.display_name ?? (profileHandle ? `@${profileHandle}` : firstName);

  let headerBadge = "Wishfox";
  let headerTitle = "";
  let headerSubtitle = "";
  let headerMetrics: string[] = [];
  let headerActions: ReactNode | undefined;

  switch (activeTab) {
    case "wishlist":
      headerBadge = "Wishfox";
      headerTitle = handleLabel
        ? t("app.hero_title_with_handle", { handle: handleLabel })
        : t("app.hero_title_default", { name: ownerName });
      headerSubtitle = ownerName;
      headerMetrics = wishlistMetrics;
      headerActions = isExternalWishlistView ? (
        <button
          key="wishlist-back"
          type="button"
          onClick={handleCloseExternalView}
          className="button-secondary"
        >
          {t("actions.back_to_mine")}
        </button>
      ) : (
        <button
          key="wishlist-add"
          type="button"
          onClick={() => setSheetOpen(true)}
          className="button-primary"
          disabled={creating}
        >
          {t("wishlist.add_button")}
        </button>
      );
      break;
    case "feed":
      headerBadge = t("tabs.feed");
      headerTitle = t("app.hero_feed_title");
      headerSubtitle = t("app.hero_feed_subtitle");
      headerMetrics = feed.length ? [t("feed.items_count", { count: feed.length })] : [];
      break;
    case "subscriptions":
      headerBadge = t("tabs.subscriptions");
      headerTitle = t("app.hero_subscriptions_title");
      headerSubtitle = t("app.hero_subscriptions_subtitle");
      headerMetrics = subscriptions.length ? [t("subscriptions.count", { count: subscriptions.length })] : [];
      break;
    case "profile":
      headerBadge = t("tabs.profile");
      headerTitle = t("app.hero_profile_title", { name: profileName });
      headerSubtitle = t(isExternalProfile ? "app.hero_profile_subtitle_external" : "app.hero_profile_subtitle_self");
      headerMetrics = [];
      headerActions = isExternalProfile
        ? (
          <button
            key="profile-back"
            type="button"
            onClick={() => {
              setProfileView(null);
              setProfileLoading(false);
            }}
            className="button-secondary"
            disabled={profileLoading}
          >
            {t("actions.back_to_mine")}
          </button>
        )
        : undefined;
      break;
    case "settings":
      headerBadge = t("tabs.settings");
      headerTitle = t("app.hero_settings_title");
      headerSubtitle = t("app.hero_settings_subtitle");
      headerMetrics = [];
      break;
    default:
      headerBadge = "Wishfox";
      headerTitle = t("tabs.wishlist");
      headerSubtitle = ownerName;
      headerMetrics = wishlistMetrics;
  }

  return (
    <>
      <Layout
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={(tabId) => {
          const next = tabId as ActiveTab;
          setActiveTab(next);
          if (next !== "wishlist") {
            setExternalLoading(false);
          }
          if (next !== "wishlist" && externalView) {
            setExternalView(null);
            resetWishlistFilters();
          }
          if (next !== "profile") {
            setProfileView(null);
            setProfileLoading(false);
          }
        }}
        header={
          <div className="hero-card__content">
            <div className="hero-card__branding">
              <div className="hero-card__badge">{headerBadge}</div>
              <div>
                <h1 className="hero-card__title">{headerTitle}</h1>
                {headerSubtitle ? <p className="hero-card__subtitle">{headerSubtitle}</p> : null}
              </div>
            </div>
            {headerMetrics.length ? (
              <div className="hero-card__metrics">
                {headerMetrics.map((metric) => (
                  <span key={metric} className="hero-card__metric">
                    {metric}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        }
        actions={headerActions}
      >
        {activeTab === "wishlist" && (
          externalLoading ? (
            <EmptyState title={t("app.title")} description={t("app.loading")} illustration="..." />
          ) : viewingWishlist ? (
            <WishlistPage
              wishes={viewingWishlist.wishes as Wish[]}
              filters={filters}
              onFiltersChange={setFilters}
              onAdd={!isExternalWishlistView ? () => setSheetOpen(true) : undefined}
              onReorder={!isExternalWishlistView ? handleReorder : undefined}
              onEdit={
                !isExternalWishlistView
                  ? (w) => {
                      setEditWish(w);
                      setForm({
                        title: w.title,
                        description: w.description ?? "",
                        url: w.url ?? "",
                        price: w.price ?? "",
                        tags: w.tags.join(", "),
                        priority: w.priority,
                        status: w.status,
                        imageFile: null,
                        imagePreview: w.image_url ?? null,
                        metadataImageUrl: w.image_url ?? null,
                        metadataSourceUrl: w.url ?? null,
                      });
                      setSheetOpen(true);
                    }
                  : undefined
              }
              t={t}
            />
          ) : (
            <EmptyState
              title={t("wishlist.empty_title")}
              description={t("wishlist.empty_body")}
              action={
                !isExternalWishlistView ? (
                  <button
                    type="button"
                    onClick={() => setSheetOpen(true)}
                    className="button-primary"
                  >
                    {t("wishlist.add_button")}
                  </button>
                ) : undefined
              }
            />
          )
        )}
        {activeTab === "feed" && <FeedPage feed={feed} t={t} />}
        {activeTab === "subscriptions" && (
          <SubscriptionsPage
            subscriptions={subscriptions}
            onUnsubscribe={handleUnsubscribe}
            onSubscribe={handleSubscribe}
            onViewWishlist={handleViewSubscriptionWishlist}
            onViewProfile={handleViewProfile}
            activeHandle={externalView?.handle ?? profileView?.handle}
            t={t}
          />
        )}
        {activeTab === "profile" && (
          profileLoading && isExternalProfile && !profileUserPublic ? (
            <EmptyState title={t("tabs.profile")} description={t("app.loading")} illustration="..." />
          ) : (
            <ProfilePage
              user={isExternalProfile ? profileUserPublic : user}
              onSave={!isExternalProfile ? updateUser : undefined}
              editable={!isExternalProfile}
              t={t}
            />
          )
        )}
        {activeTab === "settings" && (
          <SettingsPage
            notifications={notificationsEnabled}
            onToggle={(key) => setNotificationsEnabled((prev) => ({ ...prev, [key]: !prev[key] }))}
            language={locale}
            onLanguageChange={setLocale}
            t={t}
          />
        )}
      </Layout>

      <BottomSheet
        open={sheetOpen}
        onClose={() => {
          resetForm();
          setSheetOpen(false);
          setEditWish(null);
        }}
        title={editWish ? t("actions.save") : t("wishlist.add_button")}
      >
        <div style={{ display: "grid", gap: 12 }}>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 13, color: "var(--tg-hint)", textTransform: "uppercase", letterSpacing: 0.06 }}>
              {t("wishlist.form.title")}
            </span>
            <input className="field"
            placeholder={t("wishlist.form.title")}
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            style={{}}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 13, color: "var(--tg-hint)", textTransform: "uppercase", letterSpacing: 0.06 }}>
              {t("wishlist.form.description")}
            </span>
            <textarea className="field"
            placeholder={t("wishlist.form.description")}
            value={form.description}
            onChange={(event) => setForm({ ...form, description: event.target.value })}
            rows={3}
            style={{}}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 13, color: "var(--tg-hint)", textTransform: "uppercase", letterSpacing: 0.06 }}>
              {t("wishlist.form.url")}
            </span>
            <input
              className="field"
              placeholder={t("wishlist.form.url")}
              value={form.url}
              onChange={(event) => {
                const value = event.target.value;
                if (!value) {
                  setForm({
                    ...form,
                    url: value,
                    metadataSourceUrl: null,
                    metadataImageUrl: form.imageFile ? form.metadataImageUrl : null,
                    imagePreview: form.imageFile ? form.imagePreview : null,
                  });
                } else {
                  setForm({ ...form, url: value });
                }
              }}
              style={{}}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 13, color: "var(--tg-hint)", textTransform: "uppercase", letterSpacing: 0.06 }}>
              {t("wishlist.form.price")}
            </span>
            <input className="field"
            type="number"
            placeholder={t("wishlist.form.price")}
            value={form.price}
            onChange={(event) => setForm({ ...form, price: event.target.value })}
            style={{}}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 13, color: "var(--tg-hint)", textTransform: "uppercase", letterSpacing: 0.06 }}>
              {t("wishlist.form.tags")}
            </span>
            <input className="field"
            placeholder={t("wishlist.form.tags")}
            value={form.tags}
            onChange={(event) => setForm({ ...form, tags: event.target.value })}
            style={{}}
            />
          </label>
          <div style={{ display: "grid", gap: 8 }}>
            <label
              style={{
                padding: "12px 16px",
                borderRadius: "14px",
                background: "rgba(15,23,42,0.06)",
                fontWeight: 600,
                color: "var(--tg-hint)",
                cursor: "pointer",
                textAlign: "center",
              }}
            >
              <input
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null;
                  if (form.imageFile && form.imagePreview) {
                    URL.revokeObjectURL(form.imagePreview);
                  }
                  if (file) {
                    setForm({
                      ...form,
                      imageFile: file,
                      imagePreview: URL.createObjectURL(file),
                      metadataImageUrl: null,
                    });
                  } else {
                    setForm({
                      ...form,
                      imageFile: null,
                      imagePreview: form.metadataImageUrl,
                    });
                  }
                }}
              />
              {form.imageFile ? form.imageFile.name : t("wishlist.form.image")}
            </label>
            {form.imagePreview && (
              <div
                style={{
                  width: "100%",
                  height: 160,
                  borderRadius: "18px",
                  background: `url(${form.imagePreview}) center/cover`,
                }}
              />
            )}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {(["low", "medium", "high"] as Priority[]).map((priority) => (
              <button
                key={priority}
                type="button"
                onClick={() => setForm({ ...form, priority })}
                className="chip"
                style={{
                  flex: 1,
                  justifyContent: "center",
                  background: form.priority === priority ? "rgba(42, 99, 246, 0.2)" : "rgba(15,23,42,0.06)",
                  color: form.priority === priority ? "var(--tg-link)" : "var(--tg-hint)",
                  border: "1px solid rgba(15,23,42,0.1)",
                  textTransform: "capitalize",
                }}
              >
                {t(`wishlist.priority.${priority}`)}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {(["planned", "ordered", "gifted"] as WishStatus[]).map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setForm({ ...form, status })}
                className="chip"
                style={{
                  flex: 1,
                  justifyContent: "center",
                  background: form.status === status ? "rgba(42, 99, 246, 0.2)" : "rgba(15,23,42,0.06)",
                  color: form.status === status ? "var(--tg-link)" : "var(--tg-hint)",
                  border: "1px solid rgba(15,23,42,0.1)",
                  textTransform: "capitalize",
                }}
              >
                {t(`wishlist.status.${status}`)}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {editWish && (
              <button
                type="button"
                onClick={handleDeleteWish}
                style={{
                  flex: 1,
                  padding: "14px",
                  borderRadius: "18px",
                  background: "rgba(214,92,92,0.16)",
                  color: "#d14343",
                  fontWeight: 700,
                }}
              >
                {t("actions.delete")}
              </button>
            )}
            <button
            type="button"
            onClick={handleCreateWish}
            disabled={!form.title || creating}
            style={{
              padding: "14px",
              borderRadius: "18px",
              background: "var(--tg-button)",
              color: "var(--tg-button-text)",
              fontWeight: 600,
              opacity: creating ? 0.7 : 1,
            }}
          >
            {creating ? "Saving..." : t("actions.save")}
            </button>
          </div>
        </div>
      </BottomSheet>

      {/* Prompt to set username if missing */}
      <BottomSheet
        open={usernamePromptOpen}
        onClose={() => setUsernamePromptOpen(false)}
        title={t("profile.username")}
      >
        <div style={{ display: "grid", gap: 12 }}>
          <p style={{ margin: 0, color: "var(--tg-hint)" }}>{t("profile.custom_username_hint")}</p>
          <input
            placeholder="@username"
            value={customUsername}
            onChange={(e) => setCustomUsername(e.target.value.replace(/^@/, ""))}
            style={{ padding: "12px 16px", borderRadius: 14, border: "1px solid rgba(15,23,42,0.1)", background: "rgba(15,23,42,0.04)", color: "var(--tg-text)" }}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <button
              type="button"
              onClick={() => setUsernamePromptOpen(false)}
              style={{ flex: 1, padding: "12px 16px", borderRadius: 14, background: "rgba(15,23,42,0.06)", color: "var(--tg-text)" }}
            >
              {t("actions.cancel")}
            </button>
            <button
              type="button"
              disabled={!customUsername}
              onClick={async () => {
                await updateUser({ custom_username: customUsername });
                setUsernamePromptOpen(false);
                await refresh();
              }}
              style={{ flex: 1, padding: "12px 16px", borderRadius: 14, background: "var(--tg-button)", color: "var(--tg-button-text)", fontWeight: 600 }}
            >
              {t("actions.save")}
            </button>
          </div>
        </div>
      </BottomSheet>
    </>
  );
};

export default App;







