import { Send, Mic, Image as ImageIcon, Square } from "lucide-react";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useState, useEffect } from "react";

const SUGGESTIONS = [
  "Create Invoice",
  "Send Reminder",
  "Check Overdue",
  "Update Inventory",
];

export default function ChatInput({
  onSend,
  inputText,
  setInputText,
  onSendVoice,
}) {
  const { isRecording, startRecording, stopRecording } = useAudioRecorder();
  const [recordingTime, setRecordingTime] = useState(0);

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleMicClick = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      if (audioBlob) {
        onSendVoice(audioBlob);
      }
    } else {
      await startRecording();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend(inputText);
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSend(suggestion)}
            className="flex-shrink-0 px-4 py-2 bg-[#0F1016] hover:bg-white/5 border border-white/5 hover:border-white/20 rounded-xl text-xs text-gray-300 font-medium transition-all"
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-[#5865F2]/20 to-purple-600/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative bg-[#0A0A0A] border border-white/10 rounded-2xl flex items-center p-2 pl-4 focus-within:border-[#5865F2]/50 transition-colors">
          <input
            type="text"
            className="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-gray-600"
            placeholder="Tell me what you need..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <div className="flex items-center gap-1 pr-2">
            <button
              onClick={handleMicClick}
              className={`p-2 transition-all rounded-lg ${
                isRecording
                  ? "bg-red-500/20 text-red-500 hover:bg-red-500/30 animate-pulse"
                  : "text-gray-500 hover:text-white hover:bg-white/5"
              }`}
            >
              {isRecording ? (
                <Square className="w-4 h-4 fill-current" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </button>
            {isRecording && (
              <span className="text-xs text-red-400 font-mono min-w-[40px]">
                {formatTime(recordingTime)}
              </span>
            )}
            <button className="p-2 text-gray-500 hover:text-white transition-colors rounded-lg hover:bg-white/5">
              <ImageIcon className="w-4 h-4" />
            </button>
            <div className="w-px h-6 bg-white/10 mx-1" />
            <button
              onClick={() => onSend(inputText)}
              disabled={!inputText.trim()}
              className={`p-2 rounded-lg transition-all ${
                inputText.trim()
                  ? "bg-[#5865F2] hover:bg-[#4752C4] text-white shadow-lg shadow-indigo-500/20"
                  : "bg-white/5 text-gray-600 cursor-not-allowed"
              }`}
            >
              <div className="flex items-center gap-2 px-2">
                <span className="text-xs font-semibold">Send</span>
                <Send className="w-3 h-3" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
