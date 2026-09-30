"use client";

import { useRef, useState } from "react";
import { uploadDocument, ApiError } from "@/lib/api";

interface DocumentUploadProps {
  /** Called after a successful upload, so the parent can refresh the list. */
  onUploaded?: () => void;
}

/**
 * STATUS (Day 2): fully functional — uploads go to the real
 * POST /api/v1/documents/upload endpoint and are stored on disk +
 * Postgres. Text extraction/chunking (Day 3) hasn't happened yet, so
 * uploaded files aren't searchable in chat until then.
 */
export default function DocumentUpload({ onUploaded }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus("uploading");
    setMessage(null);

    try {
      await uploadDocument(file);
      setStatus("success");
      setMessage(`"${file.name}" uploaded successfully.`);
      onUploaded?.();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof ApiError ? err.message : "Upload failed. Please try again.");
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center bg-white">
      <p className="text-sm text-gray-600 mb-1">
        Drag and drop files here, or click to select.
      </p>
      <p className="text-xs text-gray-400 mb-3">Accepted: PDF, DOCX, TXT — up to 20MB.</p>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        disabled={status === "uploading"}
        className="block mx-auto text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100 disabled:opacity-50"
      />

      {status === "uploading" && (
        <p className="mt-4 text-xs text-gray-500">Uploading…</p>
      )}
      {status === "success" && message && (
        <div className="mt-4 rounded-md bg-green-50 border border-green-200 px-3 py-2 text-xs text-green-700 inline-block">
          {message}
        </div>
      )}
      {status === "error" && message && (
        <div className="mt-4 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 inline-block">
          {message}
        </div>
      )}
    </div>
  );
}
