import PageHeader from "@/components/layout/PageHeader";

/**
 * STATUS: NOT IMPLEMENTED YET — planned for Day 7. Rendered as an explicit
 * placeholder rather than mocked content.
 */
export default function KnowledgeGapsPage() {
  return (
    <div>
      <PageHeader title="Knowledge Gaps" description="Questions the system couldn't confidently answer." />
      <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
        <p className="text-sm text-gray-500">
          This feature isn&apos;t built yet. Planned for Day 7.
        </p>
      </div>
    </div>
  );
}
