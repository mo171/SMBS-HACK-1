import { User, Sparkles, Check, X, Loader2 } from "lucide-react";
import Image from "next/image";

export default function MessageBubble({ message }) {
  const isAi = message.role === "ai";

  return (
    <div
      className={`flex gap-4 ${isAi ? "items-start" : "items-start flex-row-reverse"}`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isAi ? "bg-[#5865F2]" : "bg-purple-600"
        }`}
      >
        {isAi ? (
          // Use Sparkles or a Logo for AI
          <Sparkles className="w-4 h-4 text-white" />
        ) : (
          <span className="text-xs font-bold text-white">ME</span>
        )}
      </div>

      {/* Content */}
      <div
        className={`flex flex-col max-w-[80%] ${isAi ? "items-start" : "items-end"}`}
      >
        {/* Main Bubble */}
        {message.type !== "loading" && (
          <div
            className={`px-5 py-4 rounded-2xl text-sm leading-relaxed ${
              isAi
                ? "bg-transparent text-gray-200"
                : "bg-[#7047EB] text-white rounded-tr-sm"
            }`}
          >
            {message.content}
          </div>
        )}

        {/* Rich Content: Invoice Card */}
        {message.type === "rich-card" &&
          message.data?.cardType === "invoice_draft" && (
            <div className="mt-3 w-full min-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl overflow-hidden">
              <div className="p-5">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">
                      {message.data.details.id.split(" ")[0]}{" "}
                      <span className="text-[#5865F2]">
                        {message.data.details.id.split(" ")[1]}
                      </span>
                    </h3>
                    <p className="text-xs text-gray-400 mt-1">
                      {message.data.details.client} | Due:{" "}
                      {message.data.details.dueDate}
                    </p>
                  </div>
                </div>
                <div className="text-2xl font-bold text-[#5865F2] mb-6">
                  {message.data.details.amount}
                </div>

                <div className="flex gap-3">
                  <button className="flex-1 bg-[#5865F2] hover:bg-[#4752C4] text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors">
                    <Check className="w-3 h-3" />
                    Confirm & Send
                  </button>
                  <button className="flex-1 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors border border-white/10">
                    <X className="w-3 h-3" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          )}

        {/* Loading State */}
        {message.type === "loading" && (
          <div className="flex items-center gap-3 px-5 py-4 bg-[#0F1016] border border-white/5 rounded-2xl rounded-tl-sm text-sm text-gray-300">
            <Loader2 className="w-4 h-4 animate-spin text-[#5865F2]" />
            {message.content}
          </div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-gray-600 mt-2 px-1">
          {message.timestamp}
        </span>
      </div>
    </div>
  );
}
