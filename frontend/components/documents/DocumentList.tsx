"use client";

import { useEffect, useState } from "react";
import type { OrgDocument } from "@/types";
import { listDocuments } from "@/lib/api";
import DocumentCard from "./DocumentCard";

/**
 * STATUS: the backend's GET /api/v1/documents/ returns HTTP 501 today
 * (planned Day 2-3). This component calls the real function and displays
 * the honest error rather than mocked documents.
 */
export default function DocumentList() {
  const [documents, setDocuments] = useState<OrgDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch((err) => setError(err instanceof Error ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

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
    return <p className="text-sm text-gray-400">No documents yet.</p>;
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
