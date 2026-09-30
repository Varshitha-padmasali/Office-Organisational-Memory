"use client";

import { useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import DocumentUpload from "@/components/documents/DocumentUpload";
import DocumentList from "@/components/documents/DocumentList";
import { useAuth } from "@/lib/auth";

/**
 * Documents page.
 *
 * STATUS (Day 2): fully functional for authenticated users — upload and
 * listing both hit the real backend. Gated behind sign-in because the
 * backend's document endpoints require a bearer token; rather than let
 * every request fail with 401, we show an honest "sign in first" prompt.
 */
export default function DocumentsPage() {
  const { isAuthenticated, loading } = useAuth();
  const [refreshToken, setRefreshToken] = useState(0);

  return (
    <div>
      <PageHeader
        title="Documents"
        description="Upload organizational documents to make them searchable."
      />

      {loading && <p className="text-sm text-gray-400">Checking your session…</p>}

      {!loading && !isAuthenticated && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
          <p className="text-sm text-gray-500 mb-3">
            You need to sign in to upload or view documents.
          </p>
          <Link href="/login" className="text-brand-600 text-sm font-medium hover:underline">
            Go to login
          </Link>
        </div>
      )}

      {!loading && isAuthenticated && (
        <div className="space-y-6">
          <DocumentUpload onUploaded={() => setRefreshToken((n) => n + 1)} />
          <DocumentList refreshToken={refreshToken} />
        </div>
      )}
    </div>
  );
}
