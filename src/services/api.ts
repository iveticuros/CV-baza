export const API_BASE = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8000';

export async function fetchHealth(signal?: AbortSignal) {
  const res = await fetch(`${API_BASE}/users/health`, {
    method: 'GET',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    signal,
  });
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}