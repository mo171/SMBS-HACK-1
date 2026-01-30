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

// Initial Mock Data to match the design
const INITIAL_MESSAGES = [
  {
    id: "1",
    role: "ai",
    type: "text",
    content:
      "Hi Rajesh! 👋 I'm your AI assistant. I can help you create invoices, send reminders, and manage your business. What would you like to do today?",
    timestamp: "05:02",
  },
  {
    id: "2",
    role: "user",
    type: "text",
    content: "Create an Invoice for Acme Corp. Amount 50000, due in 30 days",
    timestamp: "05:04",
  },
  {
    id: "3",
    role: "ai",
    type: "rich-card", // This helps us distinguish special UI elements
    content:
      "Perfect! I've created a draft invoice. Please review the details:",
    data: {
      cardType: "invoice_draft",
      details: {
        id: "INV-0025",
        client: "Acme Corp",
        dueDate: "Feb 29, 2026",
        amount: "₹50,000",
      },
    },
    timestamp: "05:05",
  },
  {
    id: "4",
    role: "ai",
    type: "loading", // Simulating a processing state
    content: "Creating invoice",
    timestamp: "05:05",
  },
];

export default function ChatInterface() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);
  const { user } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(false);

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
