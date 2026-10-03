"use client";

import { useEffect, useState } from "react";
import type { Meeting } from "@/types";
import { listMeetings, ApiError } from "@/lib/api";
import MeetingCard from "./MeetingCard";

interface MeetingListProps {
  /** Bump this (e.g. after saving a meeting) to trigger a refetch. */
  refreshToken?: number;
}

/**
 * STATUS (Day 6): fully functional - calls the real
 * GET /api/v1/meetings/ endpoint, scoped to the signed-in user.
 */
export default function MeetingList({ refreshToken }: MeetingListProps) {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listMeetings()
      .then(setMeetings)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, [refreshToken]);

  if (loading) {
    return <p className="text-sm text-gray-400">Loading...</p>;
  }

  if (error) {
    return (
      <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
        Could not load meetings: {error}
      </div>
    );
  }

  if (meetings.length === 0) {
    return <p className="text-sm text-gray-400">No meetings logged yet.</p>;
  }

  return (
    <div className="space-y-2">
      {meetings.map((m) => (
        <MeetingCard key={m.id} meeting={m} />
      ))}
    </div>
  );
}
