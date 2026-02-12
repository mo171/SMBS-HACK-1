"use client";

import { useState } from "react";
import { Send, Loader2 } from "lucide-react";

export default function ReplyInput({ onSend, disabled }) {
  const [text, setText] = useState("");
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim() || disabled || isSending) return;

    setIsSending(true);
    try {
      await onSend(text);
      setText("");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border-t border-white/10 bg-[#0b0c15]"
    >
      <div className="flex gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a reply..."
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-colors"
          disabled={disabled || isSending}
        />
        <button
          type="submit"
          disabled={!text.trim() || disabled || isSending}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors flex items-center justify-center min-w-[40px]"
        >
          {isSending ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
    </form>
  );
}
