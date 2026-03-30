export const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const j = (await res.json()) as { error?: { message?: string }; detail?: string };
    if (j.error?.message) return j.error.message;
    if (typeof j.detail === 'string') return j.detail;
  } catch {
    /* ignore */
  }
  return `HTTP ${res.status}`;
}

let refreshPromise: Promise<string | null> | null = null;

export async function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const r = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!r.ok) return null;
      const j = (await r.json()) as { access_token: string };
      setAccessToken(j.access_token);
      return j.access_token;
    })().finally(() => {
      refreshPromise = null;
    });
  }
  const t = await refreshPromise;
  return t;
}

export type FetchOptions = RequestInit & { skipAuth?: boolean; _retried?: boolean };

export async function apiFetch(path: string, options: FetchOptions = {}): Promise<Response> {
  const { skipAuth, _retried, ...init } = options;
  const headers = new Headers(init.headers);
  if (init.body instanceof FormData) {
    /* browser sets multipart boundary */
  } else if (!headers.has('Content-Type') && init.body && typeof init.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }
  if (!skipAuth && accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  let res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  });
  if (res.status === 401 && !skipAuth && !_retried && path !== '/auth/refresh') {
    const newTok = await refreshAccessToken();
    if (newTok) {
      return apiFetch(path, { ...options, _retried: true });
    }
  }
  return res;
}

export async function apiJson<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const res = await apiFetch(path, options);
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function loginWithPassword(email: string, password: string) {
  const body = new URLSearchParams();
  body.set('username', email);
  body.set('password', password);
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }
  return res.json() as Promise<{
    access_token: string;
    token_type: string;
    user: { id: number; name: string; email: string; role: string };
  }>;
}

export async function logoutApi() {
  await apiFetch('/auth/logout', { method: 'POST' });
  setAccessToken(null);
}

export async function fetchMe() {
  return apiJson<{
    id: number;
    name: string;
    email: string;
    role: string;
    is_active: boolean;
    email_verified: boolean;
    admin_approved: boolean;
  }>('/auth/me');
}

export async function fetchHealth(signal?: AbortSignal) {
  const res = await fetch(`${API_BASE}/health`, { signal });
  if (!res.ok) throw new Error('Health failed');
  return res.json();
}
