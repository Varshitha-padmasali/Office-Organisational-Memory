"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import StatCard from "@/components/dashboard/StatCard";
import RecentActivity from "@/components/dashboard/RecentActivity";
import { getHealth, listDocuments } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { HealthStatus } from "@/types";

/**
 * Dashboard page.
 *
 * Two "real" pieces of data now: the backend connectivity check (Day 1,
 * calls the actual GET /health) and the signed-in user (Day 2, calls the
 * actual GET /api/v1/auth/me via useAuth()). Document/question/decision
 * counts are still explicit placeholders until their Day 3+ endpoints
 * exist.
 */
export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const { user, loading: authLoading, isAuthenticated, logout } = useAuth();
  const [documentCount, setDocumentCount] = useState<number | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err) => setHealthError(err instanceof Error ? err.message : "Unknown error"))
      .finally(() => setHealthLoading(false));
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setDocumentCount(null);
      return;
    }
    listDocuments()
      .then((docs) => setDocumentCount(docs.length))
      .catch(() => setDocumentCount(null));
  }, [isAuthenticated]);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of your organization's knowledge base."
      />

      <div className="mb-4 rounded-xl border p-4 text-sm bg-white flex items-center justify-between flex-wrap gap-2">
        <div>
          <span className="font-medium text-gray-700">Backend connection: </span>
          {healthLoading && <span className="text-gray-500">Checking…</span>}
          {!healthLoading && health && (
            <span
              className={
                health.status === "ok" ? "text-green-600 font-medium" : "text-amber-600 font-medium"
              }
            >
              {health.status.toUpperCase()} — database {health.database} (env: {health.environment})
            </span>
          )}
          {!healthLoading && healthError && (
            <span className="text-red-600 font-medium">{healthError}</span>
          )}
        </div>
      </div>

      <div className="mb-6 rounded-xl border p-4 text-sm bg-white flex items-center justify-between flex-wrap gap-2">
        <div>
          <span className="font-medium text-gray-700">Account: </span>
          {authLoading && <span className="text-gray-500">Checking session…</span>}
          {!authLoading && isAuthenticated && user && (
            <span className="text-gray-700">
              Signed in as <span className="font-medium">{user.email}</span>
            </span>
          )}
          {!authLoading && !isAuthenticated && (
            <span className="text-gray-500">
              Not signed in —{" "}
              <Link href="/login" className="text-brand-600 hover:underline">
                sign in
              </Link>
            </span>
          )}
        </div>
        {!authLoading && isAuthenticated && (
          <button
            onClick={logout}
            className="text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md px-3 py-1.5"
          >
            Sign out
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Documents"
          value={documentCount !== null ? String(documentCount) : "—"}
          hint={isAuthenticated ? undefined : "Sign in to see your documents"}
        />
        <StatCard label="Questions answered" value="—" hint="Not implemented yet (Day 4-5)" />
        <StatCard label="Decisions logged" value="—" hint="Not implemented yet (Day 6)" />
        <StatCard label="Knowledge gaps" value="—" hint="Not implemented yet (Day 7)" />
      </div>

      <RecentActivity />
    </div>
  );
}
