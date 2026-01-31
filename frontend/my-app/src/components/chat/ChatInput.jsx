import { Send, Mic, Square, Loader2 } from "lucide-react";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useState, useEffect } from "react";

export default function ChatInput({ onSendVoice }) {
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

  return (
    <div className="w-full flex flex-col items-center justify-center py-2">
      <div className="relative group flex flex-col items-center gap-4">
        {/* Pulsing ring when recording */}
        {isRecording && (
          <div className="absolute inset-0 bg-[#5865F2]/20 rounded-full animate-ping scale-150 pointer-events-none" />
        )}

        {/* Glow effect */}
        <div
          className={`absolute inset-0 blur-2xl transition-all duration-500 opacity-20 pointer-events-none ${
            isRecording
              ? "bg-red-500 scale-125 opacity-40"
              : "bg-[#5865F2] group-hover:opacity-30"
          }`}
        />

        {/* The Button */}
        <button
          onClick={handleMicClick}
          className={`relative z-10 w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300 shadow-2xl ${
            isRecording
              ? "bg-red-500 hover:bg-red-600 shadow-red-500/30"
              : "bg-[#5865F2] hover:bg-[#4752C4] shadow-indigo-500/30"
          }`}
        >
          {isRecording ? (
            <Square className="w-6 h-6 text-white fill-current" />
          ) : (
            <Mic className="w-6 h-6 text-white" />
          )}
        </button>

        {/* Status Text/Timer */}
        <div className="relative h-6 text-center">
          {isRecording ? (
            <div className="flex items-center gap-2 text-red-500 font-mono text-lg animate-pulse">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              {formatTime(recordingTime)}
            </div>
          ) : (
            <span className="text-gray-400 text-sm font-medium transition-opacity">
              Tap to record & send workflow
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
