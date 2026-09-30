"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/chat", label: "Chat" },
  { href: "/documents", label: "Documents" },
  { href: "/meetings", label: "Meetings" },
  { href: "/decisions", label: "Decisions" },
  { href: "/knowledge-gaps", label: "Knowledge Gaps" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, isAuthenticated, logout } = useAuth();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 border-r border-gray-200 bg-white">
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <span className="text-lg font-semibold text-brand-700">Org Memory</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-3 py-4 border-t border-gray-200">
        {loading && <p className="text-xs text-gray-400">Checking session…</p>}
        {!loading && isAuthenticated && user && (
          <div className="space-y-2">
            <p className="text-xs text-gray-500 truncate" title={user.email}>
              {user.email}
            </p>
            <button
              onClick={handleLogout}
              className="text-xs font-medium text-gray-600 hover:text-gray-900"
            >
              Sign out
            </button>
          </div>
        )}
        {!loading && !isAuthenticated && (
          <Link href="/login" className="text-xs font-medium text-brand-600 hover:underline">
            Sign in
          </Link>
        )}
      </div>
    </aside>
  );
}
