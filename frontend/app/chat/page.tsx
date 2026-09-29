import PageHeader from "@/components/layout/PageHeader";
import ChatWindow from "@/components/chat/ChatWindow";

export default function ChatPage() {
  return (
    <div>
      <PageHeader
        title="Chat"
        description="Ask natural-language questions about your organization's documents."
      />
      <ChatWindow />
    </div>
  );
}
