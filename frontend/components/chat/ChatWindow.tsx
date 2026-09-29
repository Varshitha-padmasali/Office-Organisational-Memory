"use client";

import { useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/types";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

/**
 * Chat window.
 *
 * STATUS: NOT FUNCTIONAL YET. The backend's /api/v1/chat endpoint returns
 * HTTP 501 (planned for Day 4-5, once retrieval + Gemini generation are
 * wired up). Sending a message here appends an honest system notice
 * instead of a fake AI response.
 */
export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);

  function handleSend(text: string) {
    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };

    const systemNotice: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        "The RAG chat pipeline isn't built yet — this is a UI placeholder. Real answers with citations are planned for Day 4-5.",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, systemNotice]);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-gray-400 text-center mt-10">
            Ask a question to get started. (Answers aren&apos;t functional yet — Day 4-5.)
          </p>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
      </div>
      <ChatInput onSend={handleSend} />
    </div>
  );
}
