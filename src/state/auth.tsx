import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  fetchMe,
  getAccessToken,
  loginWithPassword,
  logoutApi,
  refreshAccessToken,
  setAccessToken,
} from '@services/api';

export type Role = 'student' | 'company' | 'admin';

export type AuthUser = {
  id: number;
  name: string;
  email: string;
  role: Role;
  email_verified?: boolean;
  admin_approved?: boolean;
};

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<Role>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider(props: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const me = await fetchMe();
    setUser({
      id: me.id,
      name: me.name,
      email: me.email,
      role: me.role as Role,
      email_verified: me.email_verified,
      admin_approved: me.admin_approved,
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const tok = await refreshAccessToken();
        if (cancelled) return;
        if (tok) {
          setAccessToken(tok);
          await refreshUser();
        }
      } catch {
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await loginWithPassword(email, password);
      setAccessToken(data.access_token);
      const role = data.user.role as Role;
      setUser({
        id: data.user.id,
        name: data.user.name,
        email: data.user.email,
        role,
      });
      await refreshUser();
      return role;
    },
    [refreshUser]
  );

  const logout = useCallback(async () => {
    await logoutApi();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout, refreshUser }),
    [user, loading, login, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { getAccessToken, setAccessToken };
