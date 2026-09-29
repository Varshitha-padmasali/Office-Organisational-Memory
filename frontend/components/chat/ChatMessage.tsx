import type { ChatMessage as ChatMessageType } from "@/types";
import { cn } from "@/lib/utils";
import SourceCitation from "./SourceCitation";

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-xl px-4 py-2 text-sm",
          isUser ? "bg-brand-500 text-white" : "bg-gray-100 text-gray-900"
        )}
      >
        <p>{message.content}</p>
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.citations.map((c, i) => (
              <SourceCitation key={i} citation={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
