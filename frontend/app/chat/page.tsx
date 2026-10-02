"use client";

import Link from "next/link";
import PageHeader from "@/components/layout/PageHeader";
import ChatWindow from "@/components/chat/ChatWindow";
import { useAuth } from "@/lib/auth";

/**
 * Chat page.
 *
 * STATUS (Day 5): fully functional. Gated behind sign-in because the
 * backend's chat endpoint requires a bearer token. See ChatWindow.tsx for
 * how answers are generated and grounded.
 */
export default function ChatPage() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <div>
      <PageHeader
        title="Chat"
        description="Ask questions and get answers generated from your uploaded documents, with citations."
      />

      {loading && <p className="text-sm text-gray-400">Checking your session…</p>}

      {!loading && !isAuthenticated && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
          <p className="text-sm text-gray-500 mb-3">
            You need to sign in to ask questions about your documents.
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
