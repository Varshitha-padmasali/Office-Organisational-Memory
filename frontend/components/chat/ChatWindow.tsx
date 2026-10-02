"use client";

import { useState } from "react";
import type { ChatMessage as ChatMessageType, SourceCitation as SourceCitationType } from "@/types";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { sendChatMessage, ApiError } from "@/lib/api";

/**
 * Chat window.
 *
 * STATUS (Day 5): fully functional. Each question is answered by Gemini,
 * grounded only on the chunks retrieved from the signed-in user's own
 * processed documents (see backend/app/services/rag_service.py) - the
 * generated text is the message content, and the chunks it was grounded
 * on are shown below as citations. If nothing relevant was found, the
 * backend says so directly instead of guessing, and no citations are
 * shown.
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
      const response = await sendChatMessage(text);

      const citations: SourceCitationType[] = response.citations.map((c) => ({
        document_id: c.document_id,
        document_name: c.document_name,
        snippet: c.snippet,
        score: c.score,
      }));

      const assistantMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        citations,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const content =
        err instanceof ApiError
          ? err.message
          : "Something went wrong generating an answer. Please try again.";
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
            Ask a question about your uploaded documents.
          </p>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {sending && <p className="text-xs text-gray-400 text-center">Thinking…</p>}
      </div>
      <ChatInput onSend={handleSend} disabled={sending} />
    </div>
  );
}
