import type { OrgDocument } from "@/types";
import { formatDate } from "@/lib/utils";

export default function DocumentCard({ document }: { document: OrgDocument }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-900">{document.original_filename}</p>
        <p className="text-xs text-gray-400">
          Uploaded {formatDate(document.uploaded_at)} · {document.content_type}
        </p>
      </div>
      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
        {document.status}
      </span>
    </div>
  );
}
