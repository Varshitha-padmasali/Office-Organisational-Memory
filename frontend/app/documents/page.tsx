import PageHeader from "@/components/layout/PageHeader";
import DocumentUpload from "@/components/documents/DocumentUpload";
import DocumentList from "@/components/documents/DocumentList";

export default function DocumentsPage() {
  return (
    <div>
      <PageHeader
        title="Documents"
        description="Upload organizational documents to make them searchable."
      />
      <div className="space-y-6">
        <DocumentUpload />
        <DocumentList />
      </div>
    </div>
  );
}
