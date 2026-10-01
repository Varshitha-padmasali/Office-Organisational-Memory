"use client";

import { useState } from "react";
import type { ChatMessage as ChatMessageType, SourceCitation as SourceCitationType } from "@/types";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { searchDocuments, ApiError } from "@/lib/api";

const MAX_SNIPPET_LENGTH = 280;

/**
 * Chat window.
 *
 * STATUS (Day 4): "chat" currently means real semantic search
 * (GET /api/v1/search) over your own uploaded, processed documents — each
 * "assistant" turn is the ranked list of matching passages, shown as
 * citations, with NO generated summary sentence synthesizing them. That's
 * deliberate: writing a one-paragraph answer from these passages without
 * actually calling an LLM to do it would be fabricating content. Real
 * generated answers (an LLM reading these same passages and writing a
 * grounded response) are planned for Day 5 — see app/services/rag_service.py.
 */
export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [sending, setSending] = useState(false);

  async function handleSend(text: string) {
    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setSending(true);

    try {
      const response = await searchDocuments(text);

      const citations: SourceCitationType[] = response.results.map((r) => ({
        document_id: r.document_id,
        document_name: r.document_name,
        snippet:
          r.content.length > MAX_SNIPPET_LENGTH
            ? `${r.content.slice(0, MAX_SNIPPET_LENGTH)}…`
            : r.content,
      }));

      const assistantMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          citations.length > 0
            ? `Found ${citations.length} relevant passage${citations.length === 1 ? "" : "s"} (raw search results — not yet a generated answer; that's planned for Day 5):`
            : 'No relevant passages found. Make sure you\'ve uploaded a document and it finished processing with status "ready".',
        citations,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const content =
        err instanceof ApiError
          ? err.message
          : "Something went wrong running search. Please try again.";
      const errorMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: "assistant",
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-gray-400 text-center mt-10">
            Ask a question to search your uploaded documents.
            <br />
            (This returns matching passages — generated answers are Day 5.)
          </p>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {sending && <p className="text-xs text-gray-400 text-center">Searching…</p>}
      </div>
      <ChatInput onSend={handleSend} disabled={sending} />
    </div>
  );
}
