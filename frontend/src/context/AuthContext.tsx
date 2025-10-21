import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { createApiClient } from "../api/client";
import type { User, Wishlist } from "../api/types";
import { expandApp, getInitData, getTelegramWebApp } from "../lib/telegram";

interface AuthState {
  loading: boolean;
  user: User | null;
  csrfToken: string | null;
  wishlists: Wishlist[];
  refresh: () => Promise<void>;
  updateUser: (payload: Partial<User>) => Promise<void>;
  api: ReturnType<typeof createApiClient>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [wishlists, setWishlists] = useState<Wishlist[]>([]);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const api = useMemo(() => createApiClient(csrfToken ?? undefined), [csrfToken]);

  const loadWishlists = useCallback(async () => {
    const response = await api.get<Wishlist[]>("/wishlists/mine");
    setWishlists(response.data);
  }, [api]);

  const bootstrap = useCallback(async () => {
    const initData = getInitData();
    if (!initData) {
      setLoading(false);
      return;
    }
    try {
      const response = await api.post<{ user: User; csrf_token: string }>("/auth/telegram", {
        init_data: initData,
      });
      setUser(response.data.user);
      setCsrfToken(response.data.csrf_token);
      await loadWishlists();
    } catch (error) {
      console.error("Failed to authenticate", error);
    } finally {
      setLoading(false);
    }
  }, [api, loadWishlists]);

  const refresh = useCallback(async () => {
    if (!csrfToken) return;
    const meResponse = await api.get<User>("/me");
    setUser(meResponse.data);
    await loadWishlists();
  }, [api, csrfToken, loadWishlists]);

  const updateUser = useCallback(
    async (payload: Partial<User>) => {
      if (!csrfToken) return;
      const response = await api.patch<User>("/me", payload);
      setUser(response.data);
    },
    [api, csrfToken],
  );

  useEffect(() => {
    expandApp();
    const webApp = getTelegramWebApp();
    if (webApp?.HapticFeedback) {
      webApp.HapticFeedback.impactOccurred("light");
    }
    bootstrap();
  }, [bootstrap]);

  const value = useMemo<AuthState>(
    () => ({
      loading,
      user,
      csrfToken,
      wishlists,
      refresh,
      updateUser,
      api,
    }),
    [loading, user, csrfToken, wishlists, refresh, updateUser, api],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthState => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
