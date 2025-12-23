import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type Role = 'student' | 'company' | 'admin';

export type User = {
  id: string;
  name: string;
  role: Role;
};

type AuthContextValue = {
  user: User | null;
  login: (args: { name: string; role: Role }) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_KEY = 'cv-baza-auth';

export function AuthProvider(props: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as User;
        setUser(parsed);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  const login = (args: { name: string; role: Role }) => {
    const newUser: User = {
      id: crypto.randomUUID(),
      name: args.name,
      role: args.role
    };
    setUser(newUser);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo<AuthContextValue>(() => ({ user, login, logout }), [user]);
  return <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
