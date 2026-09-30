/**
 * Auth state for client components.
 *
 * STATUS (Day 2): implemented for real. useAuth() resolves the stored JWT
 * (see lib/token.ts) to an actual user via GET /api/v1/auth/me, so
 * components can render "signed in as X" / gate content without each one
 * re-implementing the token -> user lookup.
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { getCurrentUser } from "@/lib/api";
import { clearToken, getToken, hasToken, setToken } from "@/lib/token";
import type { User } from "@/types";

export { clearToken, getToken, hasToken, setToken };

interface UseAuthResult {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  logout: () => void;
  refresh: () => void;
}

export function useAuth(): UseAuthResult {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    if (!hasToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return { user, loading, isAuthenticated: user !== null, logout, refresh };
}
