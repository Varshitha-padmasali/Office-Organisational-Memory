import type { Meeting } from "@/types";
import { formatDate } from "@/lib/utils";

export default function MeetingCard({ meeting }: { meeting: Meeting }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-gray-900">{meeting.title}</p>
        <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 whitespace-nowrap">
          {meeting.status}
        </span>
      </div>
      <p className="text-xs text-gray-400 mt-0.5">Logged {formatDate(meeting.created_at)}</p>
      {meeting.summary ? (
        <p className="text-sm text-gray-700 mt-2">{meeting.summary}</p>
      ) : (
        <p className="text-sm text-gray-400 mt-2">
          No summary available{meeting.status === "failed" ? " (processing failed)" : ""}.
        </p>
      )}
    </div>
  );
}
