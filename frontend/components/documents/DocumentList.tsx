"use client";

import { useEffect, useState } from "react";
import type { OrgDocument } from "@/types";
import { listDocuments, ApiError } from "@/lib/api";
import DocumentCard from "./DocumentCard";

interface DocumentListProps {
  /** Bump this (e.g. after an upload) to trigger a refetch. */
  refreshToken?: number;
}

/**
 * STATUS (Day 2): fully functional — calls the real
 * GET /api/v1/documents/ endpoint, scoped to the signed-in user.
 */
export default function DocumentList({ refreshToken }: DocumentListProps) {
  const [documents, setDocuments] = useState<OrgDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listDocuments()
      .then(setDocuments)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, [refreshToken]);

  if (loading) {
    return <p className="text-sm text-gray-400">Loading…</p>;
  }

  if (error) {
    return (
      <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
        Couldn&apos;t load documents: {error}
      </div>
    );
  }

  if (documents.length === 0) {
    return <p className="text-sm text-gray-400">No documents yet — upload one above.</p>;
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
