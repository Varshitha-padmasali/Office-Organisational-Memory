"use client";

import { useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import MeetingForm from "@/components/meetings/MeetingForm";
import MeetingList from "@/components/meetings/MeetingList";
import { useAuth } from "@/lib/auth";

/**
 * Meetings page.
 *
 * STATUS (Day 6): fully functional for authenticated users. Logging a
 * meeting triggers real summarization and decision extraction on the
 * backend (see backend/app/services/meeting_service.py).
 */
export default function MeetingsPage() {
  const { isAuthenticated, loading } = useAuth();
  const [refreshToken, setRefreshToken] = useState(0);

  return (
    <div>
      <PageHeader
        title="Meetings"
        description="Log meeting notes to get an automatic summary and any decisions made."
      />

      {loading && <p className="text-sm text-gray-400">Checking your session...</p>}

      {!loading && !isAuthenticated && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
          <p className="text-sm text-gray-500 mb-3">You need to sign in to log meetings.</p>
          <Link href="/login" className="text-brand-600 text-sm font-medium hover:underline">
            Go to login
          </Link>
        </div>
      )}

      {!loading && isAuthenticated && (
        <div className="space-y-6">
          <MeetingForm onCreated={() => setRefreshToken((n) => n + 1)} />
          <MeetingList refreshToken={refreshToken} />
        </div>
      )}
    </div>
  );
}
