import { FormEvent, useEffect, useState } from "react";

import type { PublicUser, User } from "../api/types";
import { shareDeepLink } from "../lib/telegram";

interface ProfilePageProps {
  user: (User | PublicUser) | null;
  onSave?: (payload: Partial<User>) => Promise<void>;
  t: (key: string) => string;
  editable?: boolean;
}

const getInitial = (value: string | undefined) => {
  if (!value) return "W";
  const trimmed = value.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() : "W";
};

const isFullUser = (value: User | PublicUser): value is User => "requires_custom_username" in value;

export const ProfilePage: React.FC<ProfilePageProps> = ({ user, onSave, t, editable }) => {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Partial<User>>({
    display_name: user?.display_name,
    bio: user && "bio" in user ? user.bio ?? "" : "",
    custom_username: user && isFullUser(user) ? user.custom_username ?? "" : "",
  });
  const [saving, setSaving] = useState(false);

  if (!user) {
    return null;
  }

  const fullUser = isFullUser(user) ? user : null;
  const isEditable = Boolean(fullUser && onSave && (editable ?? true));

  useEffect(() => {
    if (user) {
      const full = isFullUser(user);
      setForm({
        display_name: user.display_name,
        bio: "bio" in user ? user.bio ?? "" : "",
        custom_username: full ? user.custom_username ?? "" : "",
      });
      setEditing(false);
    }
  }, [user]);

  const handle = fullUser
    ? fullUser.tg_username ?? fullUser.custom_username ?? fullUser.username ?? ""
    : user.username ?? "";
  const canShare = Boolean(fullUser?.tg_username);
  const avatarInitial = getInitial(user.display_name);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!isEditable || !onSave) return;
    setSaving(true);
    await onSave(form);
    setSaving(false);
    setEditing(false);
  };

  return (
    <section className="profile-card fade-in">
      <div className="profile-card__hero">
        <div className="profile-card__avatar">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.display_name} loading="lazy" />
          ) : (
            <span>{avatarInitial}</span>
          )}
        </div>
        <div className="profile-card__hero-info">
          <h2 className="profile-card__display">{user.display_name}</h2>
          {handle ? (
            <span className="profile-card__handle">@{handle}</span>
          ) : (
            <span className="profile-card__handle profile-card__handle--muted">{t("profile.handle_missing")}</span>
          )}
        </div>
        {isEditable && !editing && (
          <button
            type="button"
            className="ghost-button profile-card__edit"
            onClick={() => setEditing(true)}
          >
            {t("profile.edit_button")}
          </button>
        )}
      </div>

      {isEditable && editing ? (
        <form onSubmit={handleSubmit} className="profile-card__form">
          <label className="input-group">
            <span className="input-group__label">{t("profile.display_name")}</span>
            <input
              className="field"
              value={form.display_name ?? ""}
              onChange={(event) => setForm({ ...form, display_name: event.target.value })}
            />
          </label>

          <label className="input-group">
            <span className="input-group__label">{t("profile.bio")}</span>
            <textarea
              className="field"
              value={form.bio ?? ""}
              onChange={(event) => setForm({ ...form, bio: event.target.value })}
              rows={4}
            />
          </label>

          {fullUser?.requires_custom_username && (
            <div className="input-group">
              <span className="input-group__label">{t("profile.username")}</span>
              <input
                className="field"
                value={form.custom_username ?? ""}
                onChange={(event) => setForm({ ...form, custom_username: event.target.value })}
              />
              <span className="input-group__hint">{t("profile.custom_username_hint")}</span>
            </div>
          )}

          <div className="profile-card__actions">
            <button
              type="button"
              className="button-secondary"
              onClick={() => {
                setEditing(false);
                setForm({
                  display_name: user.display_name,
                  bio: "bio" in user ? user.bio ?? "" : "",
                  custom_username: fullUser?.custom_username ?? "",
                });
              }}
            >
              {t("actions.cancel")}
            </button>
            <button
              type="submit"
              className="button-primary"
              disabled={saving}
            >
              {saving ? `${t("profile.save")}...` : t("profile.save")}
            </button>
          </div>
        </form>
      ) : (
        <>
          <div className="profile-card__bio">
            <span className="profile-card__bio-label">{t("profile.bio")}</span>
            <p className={user && "bio" in user && user.bio ? "profile-card__bio-text" : "profile-card__bio-text profile-card__bio-text--muted"}>
              {("bio" in user && user.bio) || t("profile.empty_bio")}
            </p>
          </div>

          {isEditable && !editing ? (
            <div className="profile-card__actions profile-card__actions--single">
              <button
                type="button"
                className="button-primary"
                onClick={() => shareDeepLink(fullUser?.tg_username)}
                disabled={!canShare}
                title={!canShare ? t("profile.handle_missing") : undefined}
              >
                {t("actions.share")}
              </button>
            </div>
          ) : null}
          {isEditable && !editing && !canShare ? (
            <p className="profile-card__share-hint">{t("profile.share_hint")}</p>
          ) : null}
        </>
      )}
    </section>
  );
};


