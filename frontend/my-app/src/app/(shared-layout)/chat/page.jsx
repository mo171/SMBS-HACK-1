import ChatInterface from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col">
      {/* Height is now full screen, padding removed for flush layout */}
      <ChatInterface />
    </div>
  );
}
