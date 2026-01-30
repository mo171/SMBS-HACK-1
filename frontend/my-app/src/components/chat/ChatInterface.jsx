"use client";

import { useState, useRef, useEffect } from "react";
import {
  Plus,
  Send,
  Mic,
  Image as ImageIcon,
  Sparkles,
  Loader2,
} from "lucide-react";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import { chatService } from "@/services/chatService";
import { useAuthStore } from "@/store/authStore";

export default function ChatInterface() {
  const { user } = useAuthStore();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);

  useEffect(() => {
    if (user && !hasInitialized) {
      // Get name from user metadata or email or default
      const userName =
        user.user_metadata?.full_name || user.email?.split("@")[0] || "User";

      const welcomeMsg = {
        id: "welcome",
        role: "ai",
        type: "text",
        content: `Hi ${userName}! 👋 I'm your AI assistant. I can help you create invoices, send reminders, and manage your business. Record your audio and I will do the work for you.`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages([welcomeMsg]);
      setHasInitialized(true);
    }
  }, [user, hasInitialized]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (text) => {
    // Current text support is limited, focus on voice for now or implement text API later
    if (!text.trim()) return;

    const userMsg = {
      id: Date.now().toString(),
      role: "user",
      type: "text",
      content: text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
  };

  const handleSendVoice = async (audioBlob) => {
    setIsProcessing(true);

    // 1. Add temporary user audio message (visual feedback)
    const tempId = Date.now().toString();
    const userMsg = {
      id: tempId,
      role: "user",
      type: "audio", // We can add an audio player here later if needed
      content: "🎤 Voice Command Sent",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages((prev) => [...prev, userMsg]);

    // 2. Add loading state
    const loadingId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        role: "ai",
        type: "loading",
        content: "Listening & Processing...",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);

    try {
      // 3. Call API
      const sessionId = user?.id || "default_guest";
      const response = await chatService.sendVoiceCommand(audioBlob, sessionId);

      // 4. Remove loading and add AI response
      setMessages((prev) => prev.filter((m) => m.id !== loadingId));

      const aiMsg = {
        id: (Date.now() + 2).toString(),
        role: "ai",
        type: response.analysis?.intent_type || "text",
        content: response.reply,
        data: response.analysis?.data, // The intent data for cards
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error("Voice command failed:", error);
      setMessages((prev) => prev.filter((m) => m.id !== loadingId));
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 3).toString(),
          role: "ai",
          type: "text",
          content:
            "Sorry, I encountered an error processing your voice command.",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#030014] rounded-2xl border border-white/10 overflow-hidden relative">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-white/5 bg-[#030014]/50 backdrop-blur-md z-10">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">Workflow Chat</h1>
          <p className="text-sm text-gray-400">
            Tell me what you need, and I'll handle it
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white text-sm font-medium transition-colors border border-white/10">
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 pt-2 bg-gradient-to-t from-[#030014] via-[#030014] to-transparent">
        <ChatInput
          onSend={handleSendMessage}
          onSendVoice={handleSendVoice}
          inputText={inputText}
          setInputText={setInputText}
        />
        <div className="text-center mt-3">
          <p className="text-[10px] text-gray-600">
            Press Enter to send - Use voice for hands-free workflow
          </p>
        </div>
      </div>
    </div>
  );
}
