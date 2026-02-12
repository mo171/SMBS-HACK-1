"use client";

import useSWR from "swr";
import { User, MessageSquare, Clock, Bot } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { api } from "../../lib/axios";

// Axios fetcher
const fetcher = (url) => api.get(url).then((res) => res.data);

export default function SessionList({
  selectedSessionId,
  onSelectSession,
  activePlatform,
}) {
  const { data, error, isLoading } = useSWR("/api/messages/sessions", fetcher, {
    refreshInterval: 5000,
  });

  if (error)
    return <div className="p-4 text-red-400 text-sm">Failed to load chats</div>;
  if (isLoading)
    return (
      <div className="p-4 text-gray-400 text-sm animate-pulse">
        Loading chats...
      </div>
    );

  const allSessions = data?.data || [];

  // Filter sessions by active platform
  const filteredSessions = allSessions.filter(
    (session) => session.platform === activePlatform,
  );

  // For WhatsApp, aggregate all sessions into one "AI Assistant" item
  const displaySessions =
    activePlatform === "whatsapp" && filteredSessions.length > 0
      ? [
          {
            id: "whatsapp-aggregate",
            platform: "whatsapp",
            sender_handle: "AI Assistant",
            external_id: "whatsapp",
            last_message: filteredSessions[0]?.last_message || "No messages",
            last_active: filteredSessions[0]?.last_active,
            isAggregate: true,
          },
        ]
      : filteredSessions;

  return (
    <div className="flex flex-col flex-1 bg-[#0b0c15] overflow-hidden">
      <div className="p-4 border-b border-white/10">
        <h2 className="text-white font-semibold flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-blue-400" />
          {activePlatform === "whatsapp"
            ? "WhatsApp"
            : activePlatform === "instagram"
              ? "Instagram DMs"
              : activePlatform === "bluesky"
                ? "Bluesky Mentions"
                : "Pixelfed Notifications"}
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {displaySessions.length === 0 ? (
          <div className="p-4 text-gray-500 text-sm text-center">
            No active chats
          </div>
        ) : (
          displaySessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`w-full p-4 text-left border-b border-white/5 transition-colors hover:bg-white/5 ${
                selectedSessionId === session.id
                  ? "bg-blue-500/10 border-l-2 border-l-blue-500"
                  : ""
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                {/* Avatar */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    session.isAggregate ? "bg-green-500/20" : "bg-purple-500/20"
                  }`}
                >
                  {session.isAggregate ? (
                    <Bot className="w-5 h-5 text-green-400" />
                  ) : (
                    <User className="w-5 h-5 text-purple-400" />
                  )}
                </div>

                {/* Name and Platform Badge */}
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-white font-medium truncate pr-2">
                      {session.sender_handle || session.external_id}
                    </span>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-semibold ${
                        session.platform === "whatsapp"
                          ? "bg-green-500/20 text-green-400"
                          : session.platform === "instagram"
                            ? "bg-pink-500/20 text-pink-400"
                            : session.platform === "bluesky"
                              ? "bg-blue-500/20 text-blue-400"
                              : "bg-purple-500/20 text-purple-400"
                      }`}
                    >
                      {session.platform === "whatsapp"
                        ? "WA"
                        : session.platform === "instagram"
                          ? "IG"
                          : session.platform === "bluesky"
                            ? "BS"
                            : "PX"}
                    </span>
                  </div>

                  <p className="text-gray-400 text-sm truncate mb-1">
                    {session.last_message || "No messages"}
                  </p>

                  <div className="flex items-center gap-1 text-[10px] text-gray-600">
                    <Clock className="w-3 h-3" />
                    <span>
                      {session.last_active
                        ? new Date(session.last_active).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "New"}
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
