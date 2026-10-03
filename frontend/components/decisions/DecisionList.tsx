"use client";

import { useEffect, useState } from "react";
import type { Decision } from "@/types";
import { listDecisions, ApiError } from "@/lib/api";
import DecisionCard from "./DecisionCard";

/**
 * STATUS (Day 6): fully functional - calls the real
 * GET /api/v1/decisions/ endpoint, which includes decisions found in
 * both meetings and documents, scoped to the signed-in user.
 */
export default function DecisionList() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDecisions()
      .then(setDecisions)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-sm text-gray-400">Loading...</p>;
  }

  if (error) {
    return (
      <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
        Could not load decisions: {error}
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <p className="text-sm text-gray-400">
        No decisions yet. They are extracted automatically when you log a meeting, or you can
        extract them from a document on the Documents page.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {decisions.map((d) => (
        <DecisionCard key={d.id} decision={d} />
      ))}
    </div>
  );
}
