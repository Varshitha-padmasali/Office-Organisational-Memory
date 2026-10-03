import type { Decision } from "@/types";
import { formatDate } from "@/lib/utils";

export default function DecisionCard({ decision }: { decision: Decision }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium text-gray-900">{decision.summary}</p>
        <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 whitespace-nowrap">
          {decision.source_type}
        </span>
      </div>
      {decision.context && <p className="text-sm text-gray-600 mt-1">{decision.context}</p>}
      <p className="text-xs text-gray-400 mt-2">
        From {decision.source_title} &middot; {formatDate(decision.created_at)}
      </p>
    </div>
  );
}
