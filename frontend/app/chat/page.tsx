"use client";

import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import ChatWindow from "@/components/chat/ChatWindow";
import { useAuth } from "@/lib/auth";

/**
 * Chat page.
 *
 * STATUS (Day 4): gated behind sign-in because the backend's search
 * endpoint requires a bearer token. See ChatWindow.tsx for what "chat"
 * actually does right now (real search, not yet generated answers).
 */
export default function ChatPage() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <div>
      <PageHeader
        title="Chat"
        description="Ask natural-language questions about your organization's documents."
      />

      {loading && <p className="text-sm text-gray-400">Checking your session…</p>}

      {!loading && !isAuthenticated && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
          <p className="text-sm text-gray-500 mb-3">
            You need to sign in to search your documents.
          </p>
          <Link href="/login" className="text-brand-600 text-sm font-medium hover:underline">
            Go to login
          </Link>
        </div>
      )}

      {!loading && isAuthenticated && <ChatWindow />}
    </div>
  );
}
