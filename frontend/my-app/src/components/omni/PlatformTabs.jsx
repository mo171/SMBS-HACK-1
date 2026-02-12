"use client";

import { MessageCircle, Instagram, Cloud, Image } from "lucide-react";

export default function PlatformTabs({ activePlatform, onPlatformChange }) {
  const tabs = [
    { id: "whatsapp", label: "WhatsApp", icon: MessageCircle },
    { id: "instagram", label: "Instagram", icon: Instagram },
    { id: "bluesky", label: "Bluesky", icon: Cloud },
    { id: "pixelfed", label: "Pixelfed", icon: Image },
  ];

  return (
    <div className="flex border-b border-white/10 bg-[#0b0c15]">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activePlatform === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => onPlatformChange(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors relative ${
              isActive ? "text-blue-400" : "text-gray-400 hover:text-gray-300"
            }`}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
            {isActive && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
            )}
          </button>
        );
      })}
    </div>
  );
}
