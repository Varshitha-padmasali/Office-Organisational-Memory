"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/layout/PageHeader";
import StatCard from "@/components/dashboard/StatCard";
import RecentActivity from "@/components/dashboard/RecentActivity";
import { getHealth } from "@/lib/api";
import type { HealthStatus } from "@/types";

/**
 * Dashboard page.
 *
 * The only "real" data on this page today is the backend connectivity
 * check below, which calls the actual GET /health endpoint. Everything
 * else (document count, question count, etc.) is an explicit placeholder
 * until Day 2+ endpoints exist — see StatCard values.
 */
export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err) => setError(err instanceof Error ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of your organization's knowledge base."
      />

      <div className="mb-6 rounded-xl border p-4 text-sm bg-white">
        <span className="font-medium text-gray-700">Backend connection: </span>
        {loading && <span className="text-gray-500">Checking…</span>}
        {!loading && health && (
          <span
            className={
              health.status === "ok" ? "text-green-600 font-medium" : "text-amber-600 font-medium"
            }
          >
            {health.status.toUpperCase()} — database {health.database} (env: {health.environment})
          </span>
        )}
        {!loading && error && (
          <span className="text-red-600 font-medium">{error}</span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Documents" value="—" hint="Not implemented yet (Day 2-3)" />
        <StatCard label="Questions answered" value="—" hint="Not implemented yet (Day 4-5)" />
        <StatCard label="Decisions logged" value="—" hint="Not implemented yet (Day 6)" />
        <StatCard label="Knowledge gaps" value="—" hint="Not implemented yet (Day 7)" />
      </div>

      <RecentActivity />
    </div>
  );
}
