/**
 * Local JWT storage.
 *
 * Kept in its own module (rather than lib/auth.ts) so both lib/api.ts
 * (which needs to attach the token to requests) and lib/auth.ts (which
 * exposes the useAuth() hook, and itself calls lib/api.ts) can import it
 * without a circular dependency.
 */

const TOKEN_KEY = "org_memory_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export function hasToken(): boolean {
  return getToken() !== null;
}
