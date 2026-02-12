"use client";

import useSWR from "swr";
import { useEffect, useRef, useState } from "react";
import ReplyInput from "./ReplyInput";
import { Loader2, Bot, BotOff, Reply, X } from "lucide-react";
import { toast } from "react-hot-toast";

import { api } from "../../lib/axios";
import { supabase } from "../../lib/supabase";

// Axios fetcher
const fetcher = (url) => api.get(url).then((res) => res.data);

export default function ChatWindow({ sessionId, platform }) {
  const [replyingTo, setReplyingTo] = useState(null);
  const [isBotActive, setIsBotActive] = useState(true);

  // For WhatsApp aggregate view, fetch all WhatsApp messages
  const apiUrl =
    sessionId === "whatsapp-aggregate"
      ? "/api/messages/whatsapp/all"
      : `/api/messages/${sessionId}`;

  const { data, error, isLoading, mutate } = useSWR(
    sessionId ? apiUrl : null,
    fetcher,
    { refreshInterval: 0 },
  );

  // Fetch session details for bot status
  const { data: sessionData, mutate: mutateSession } = useSWR(
    sessionId && sessionId !== "whatsapp-aggregate"
      ? `/api/messages/sessions/${sessionId}/detail`
      : null,
    fetcher,
  );

  useEffect(() => {
    if (sessionData?.data) {
      setIsBotActive(sessionData.data.is_bot_active);
    }
  }, [sessionData]);

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
        () => {
          mutate();
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [sessionId, mutate]);

  const handleToggleBot = async () => {
    try {
      const res = await api.post(
        `/api/messages/sessions/${sessionId}/toggle-bot`,
      );
      setIsBotActive(res.data.is_bot_active);
      mutateSession();
      toast.success(
        res.data.is_bot_active ? "Bot mode enabled" : "Bot mode disabled",
      );
    } catch (e) {
      toast.error("Failed to toggle bot");
    }
  };

  const handleSend = async (text) => {
    try {
      let targetSessionId = sessionId;

      if (sessionId === "whatsapp-aggregate") {
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
        reply_to_id: replyingTo?.id,
      });

      setReplyingTo(null);
      mutate();
    } catch (e) {
      console.error("Failed to send", e);
      toast.error("Failed to send message");
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
      {/* Header */}
      <div className="p-4 border-b border-white/10 bg-[#0b0c15] flex justify-between items-center">
        <div>
          <h3 className="text-white font-medium">
            {sessionData?.data?.sender_handle ||
              sessionData?.data?.external_id ||
              "Chat"}
          </h3>
          <p className="text-[10px] text-gray-500 uppercase tracking-wider">
            {platform}
          </p>
        </div>

        {sessionId !== "whatsapp-aggregate" && (
          <button
            onClick={handleToggleBot}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
              isBotActive
                ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : "bg-gray-500/20 text-gray-400 border border-gray-500/30"
            }`}
          >
            {isBotActive ? (
              <>
                <Bot className="w-3 h-3" />
                Bot Talking
              </>
            ) : (
              <>
                <BotOff className="w-3 h-3" />
                Manual Mode
              </>
            )}
          </button>
        )}
      </div>

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
            className={`flex group ${msg.direction === "outbound" ? "justify-end" : "justify-start"}`}
          >
            <div className="flex items-end gap-2 max-w-[80%]">
              {msg.direction === "inbound" && (
                <button
                  onClick={() => setReplyingTo(msg)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white/5 rounded-full text-gray-500 hover:text-blue-400"
                  title="Reply"
                >
                  <Reply className="w-4 h-4" />
                </button>
              )}

              <div
                className={`rounded-2xl p-3 text-sm shadow-sm ${
                  msg.direction === "outbound"
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-[#1e1f2b] text-white rounded-bl-sm border border-white/5"
                }`}
              >
                {/* Platform Badge (Only for aggregate or multi-service) */}
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
                      {msg.platform}
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

              {msg.direction === "outbound" && (
                <button
                  onClick={() => setReplyingTo(msg)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white/5 rounded-full text-gray-500 hover:text-blue-400 order-first"
                  title="Reply"
                >
                  <Reply className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Reply Preview */}
      {replyingTo && (
        <div className="mx-4 p-3 bg-[#1e1f2b] border border-white/10 border-b-0 rounded-t-lg flex items-center justify-between gap-3 animate-in slide-in-from-bottom-2">
          <div className="min-w-0 flex-1 border-l-2 border-blue-500 pl-3">
            <p className="text-blue-400 text-[10px] font-bold uppercase mb-0.5">
              Replying to {replyingTo.sender_handle || "User"}
            </p>
            <p className="text-gray-400 text-xs truncate italic">
              {replyingTo.content}
            </p>
          </div>
          <button
            onClick={() => setReplyingTo(null)}
            className="p-1 hover:bg-white/10 rounded-full text-gray-500 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Input */}
      <ReplyInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
