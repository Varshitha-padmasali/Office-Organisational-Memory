"use client";

import { useState } from "react";
import { createMeeting, ApiError } from "@/lib/api";

interface MeetingFormProps {
  /** Called after a successful save, so the parent can refresh the list. */
  onCreated?: () => void;
}

/**
 * STATUS (Day 6): fully functional. Submitting saves the raw notes
 * immediately, then the backend synchronously summarizes them and
 * extracts any decisions before responding, so this can take a few
 * seconds.
 */
export default function MeetingForm({ onCreated }: MeetingFormProps) {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createMeeting({ title, raw_notes: notes });
      setTitle("");
      setNotes("");
      onCreated?.();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not save the meeting. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div>
        <label htmlFor="meeting-title" className="block text-sm font-medium text-gray-700 mb-1">
          Title
        </label>
        <input
          id="meeting-title"
          type="text"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Weekly sync"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <div>
        <label htmlFor="meeting-notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          id="meeting-notes"
          required
          rows={6}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Paste or write your raw meeting notes here."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <button
        type="submit"
        disabled={submitting}
        className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 transition-colors disabled:opacity-50"
      >
        {submitting ? "Summarizing..." : "Save meeting"}
      </button>
      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
          {error}
        </div>
      )}
    </form>
  );
}
