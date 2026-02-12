"use client";

import useSWR from "swr";
import { useEffect, useRef } from "react";
import ReplyInput from "./ReplyInput";
import { Loader2 } from "lucide-react";
import { toast } from "react-hot-toast"; // Assuming user has this, else simple alert

import { api } from "../../lib/axios";
import { supabase } from "../../lib/supabase";

// Axios fetcher
const fetcher = (url) => api.get(url).then((res) => res.data);

export default function ChatWindow({ sessionId, platform }) {
  // For WhatsApp aggregate view, fetch all WhatsApp messages
  const apiUrl =
    sessionId === "whatsapp-aggregate"
      ? "/api/messages/whatsapp/all"
      : `/api/messages/${sessionId}`;

  const { data, error, isLoading, mutate } = useSWR(
    sessionId ? apiUrl : null,
    fetcher,
    { refreshInterval: 0 }, // Disable polling, rely on Realtime
  );

  const bottomRef = useRef(null);

  useEffect(() => {
    if (data) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [data]);

  // Realtime Subscription
  useEffect(() => {
    if (!sessionId) return;

    const channel = supabase
      .channel(`realtime-messages-${sessionId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "unified_messages",
          filter: `session_id=eq.${sessionId}`,
        },
        (payload) => {
          // Optimistically update or just re-fetch
          mutate();
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [sessionId, mutate]);

  const handleSend = async (text) => {
    try {
      // For WhatsApp aggregate, we need to get the actual session ID
      let targetSessionId = sessionId;

      if (sessionId === "whatsapp-aggregate") {
        // Get the first WhatsApp session to send the message
        const sessionsResponse = await api.get("/api/messages/sessions");
        const whatsappSessions = sessionsResponse.data.data.filter(
          (s) => s.platform === "whatsapp",
        );

        if (whatsappSessions.length > 0) {
          targetSessionId = whatsappSessions[0].id;
        } else {
          throw new Error("No WhatsApp sessions found");
        }
      }

      await api.post("/api/messages/send", {
        session_id: targetSessionId,
        text: text,
      });

      mutate(); // Refresh the list
    } catch (e) {
      console.error("Failed to send", e);
      // Using alert if toast is missing, or toast if configured (package.json has react-hot-toast)
      try {
        toast.error("Failed to send message");
      } catch {
        alert("Failed to send");
      }
    }
  };

  if (!sessionId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-500 bg-[#030014]">
        <div className="p-4 rounded-full bg-white/5 mb-4">
          <Loader2 className="w-8 h-8 opacity-50" />
        </div>
        <p>Select a conversation from the sidebar</p>
      </div>
    );
  }

  if (error)
    return (
      <div className="flex-1 flex items-center justify-center text-red-400 bg-[#030014]">
        Error loading messages
      </div>
    );
  if (isLoading)
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 bg-[#030014]">
        <Loader2 className="animate-spin mr-2" />
        Loading history...
      </div>
    );

  const messages = data?.data || [];

  return (
    <div className="flex flex-col h-full bg-[#030014] relative">
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-10">
            No messages yet. Start the conversation!
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.direction === "outbound" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] rounded-2xl p-3 text-sm shadow-sm ${
                msg.direction === "outbound"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-[#1e1f2b] text-white rounded-bl-sm border border-white/5"
              }`}
            >
              {/* Platform Badge */}
              {msg.platform && (
                <div className="flex items-center gap-1 mb-2">
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wide ${
                      msg.platform === "whatsapp"
                        ? "bg-green-500/20 text-green-400 border border-green-500/30"
                        : msg.platform === "instagram"
                          ? "bg-pink-500/20 text-pink-400 border border-pink-500/30"
                          : "bg-gray-500/20 text-gray-400 border border-gray-500/30"
                    }`}
                  >
                    {msg.platform === "whatsapp"
                      ? "WhatsApp"
                      : msg.platform === "instagram"
                        ? "Instagram"
                        : msg.platform}
                  </span>
                </div>
              )}
              <p className="break-words whitespace-pre-wrap">{msg.content}</p>
              <span className="text-[10px] opacity-50 block text-right mt-1">
                {new Date(msg.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ReplyInput onSend={handleSend} />
    </div>
  );
}
