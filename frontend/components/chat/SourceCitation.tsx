import type { SourceCitation as SourceCitationType } from "@/types";

export default function SourceCitation({ citation }: { citation: SourceCitationType }) {
  return (
    <div className="text-xs bg-white/60 border border-gray-200 rounded px-2 py-1">
      <span className="font-medium">{citation.document_name}</span>
      {citation.page !== undefined && <span> p.{citation.page}</span>}
      {citation.score !== undefined && (
        <span className="text-gray-400"> {Math.round(citation.score * 100)}% match</span>
      )}
      <p className="text-gray-500 mt-0.5 line-clamp-2">{citation.snippet}</p>
    </div>
  );
}
