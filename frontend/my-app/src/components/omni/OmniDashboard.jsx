"use client";

import { useState } from "react";
import PlatformTabs from "./PlatformTabs";
import SessionList from "./SessionList";
import ChatWindow from "./ChatWindow";

export default function OmniDashboard() {
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [activePlatform, setActivePlatform] = useState("whatsapp");

  const handlePlatformChange = (platform) => {
    setActivePlatform(platform);
    setSelectedSessionId(null); // Reset selection when switching platforms
  };

  return (
    <div className="flex h-screen w-full bg-[#030014] overflow-hidden text-gray-200">
      {/* Sidebar */}
      <div className="flex flex-col h-full w-80 border-r border-white/10">
        <PlatformTabs
          activePlatform={activePlatform}
          onPlatformChange={handlePlatformChange}
        />
        <SessionList
          selectedSessionId={selectedSessionId}
          onSelectSession={setSelectedSessionId}
          activePlatform={activePlatform}
        />
      </div>

      {/* Main Chat */}
      <div className="flex-1 h-full flex flex-col">
        {selectedSessionId ? (
          <ChatWindow sessionId={selectedSessionId} platform={activePlatform} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
            <h2 className="text-xl font-semibold mb-2">
              {activePlatform === "whatsapp" ? "WhatsApp" : "Instagram"}{" "}
              Messages
            </h2>
            <p>Select a conversation to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
}
