"use client";

import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import DecisionList from "@/components/decisions/DecisionList";
import { useAuth } from "@/lib/auth";

/**
 * Decisions page.
 *
 * STATUS (Day 6): fully functional for authenticated users. See
 * backend/app/services/decision_service.py for how decisions are
 * extracted and linked back to their source meeting or document.
 */
export default function DecisionsPage() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <div>
      <PageHeader
        title="Decisions"
        description="A log of decisions found in your meetings and documents."
      />

      {loading && <p className="text-sm text-gray-400">Checking your session...</p>}

      {!loading && !isAuthenticated && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
          <p className="text-sm text-gray-500 mb-3">You need to sign in to view decisions.</p>
          <Link href="/login" className="text-brand-600 text-sm font-medium hover:underline">
            Go to login
          </Link>
        </div>
      )}

      {!loading && isAuthenticated && <DecisionList />}
    </div>
  );
}
