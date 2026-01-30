import ChatInterface from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <div className="h-screen p-4 flex flex-col">
      {/* Height is now full screen, padding is reduced to p-4 (1rem) */}
      <ChatInterface />
    </div>
  );
}
