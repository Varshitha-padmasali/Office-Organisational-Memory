"use client";

import { useState } from "react";
import type { OrgDocument } from "@/types";
import { formatDate } from "@/lib/utils";
import { extractDocumentDecisions, ApiError } from "@/lib/api";

/**
 * STATUS (Day 6): the "Extract decisions" action is fully functional -
 * calls the real POST /api/v1/documents/{id}/extract-decisions endpoint.
 * Only shown once a document's status is "ready" (processed into
 * searchable chunks), since extraction reads from those chunks.
 */
export default function DocumentCard({ document }: { document: OrgDocument }) {
  const [extracting, setExtracting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleExtract() {
    setExtracting(true);
    setMessage(null);
    try {
      const decisions = await extractDocumentDecisions(document.id);
      setMessage(
        decisions.length > 0
          ? `Found ${decisions.length} decision${decisions.length === 1 ? "" : "s"}. See the Decisions page.`
          : "No decisions found in this document."
      );
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not extract decisions.");
    } finally {
      setExtracting(false);
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">{document.original_filename}</p>
          <p className="text-xs text-gray-400">
            Uploaded {formatDate(document.uploaded_at)} &middot; {document.content_type}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
            {document.status}
          </span>
          {document.status === "ready" && (
            <button
              onClick={handleExtract}
              disabled={extracting}
              className="text-xs font-medium text-brand-600 hover:underline disabled:opacity-50"
            >
              {extracting ? "Extracting..." : "Extract decisions"}
            </button>
          )}
        </div>
      </div>
      {message && <p className="text-xs text-gray-500 mt-2">{message}</p>}
    </div>
  );
}
