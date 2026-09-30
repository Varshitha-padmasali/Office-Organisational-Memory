/**
 * STATUS: NOT IMPLEMENTED YET. There is no activity feed backend
 * endpoint — this renders an explicit empty state rather than mocked
 * activity items, per the "no fake functionality" requirement.
 */
export default function RecentActivity() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-sm font-semibold text-gray-900 mb-2">Recent activity</h2>
      <p className="text-sm text-gray-500">
        Not implemented yet — this will show recent uploads, questions, and
        decisions once the backend endpoints for those exist (Day 3+).
      </p>
    </div>
  );
}
