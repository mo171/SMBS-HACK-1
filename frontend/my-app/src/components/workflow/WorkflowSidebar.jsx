import {
  Sparkles,
  LayoutTemplate,
  MessageSquare,
  GitBranch,
  Play,
} from "lucide-react";
import { useState } from "react";

export default function WorkflowSidebar({ onGenerate, isGenerating }) {
  const [prompt, setPrompt] = useState("");

  return (
    <div className="w-80 border-r border-white/10 flex flex-col bg-[#050510] z-10">
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="space-y-6">
          <div>
            <label className="text-xs font-semibold text-gray-400 uppercase mb-2 block">
              AI Workflow Prompt
            </label>
            <textarea
              className="w-full h-40 bg-[#0F1016] border border-white/10 rounded-xl p-4 text-sm text-white resize-none focus:border-[#5865F2] outline-none transition-colors placeholder:text-gray-600"
              placeholder="Describe your workflow... e.g., 'Check sentiment of user input, if negative send email, if positive save to database'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <button
            onClick={() => onGenerate(prompt)}
            disabled={!prompt.trim() || isGenerating}
            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              !prompt.trim() || isGenerating
                ? "bg-white/5 text-gray-600 cursor-not-allowed"
                : "bg-white text-black hover:bg-gray-200"
            }`}
          >
            {isGenerating ? (
              <>Generating...</>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Workflow
              </>
            )}
          </button>

          <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/20 rounded-xl">
            <h4 className="text-[#5865F2] text-xs font-bold mb-1 flex items-center gap-2">
              <Sparkles className="w-3 h-3" />
              AI Tip
            </h4>
            <p className="text-xs text-indigo-200/70 leading-relaxed">
              Try asking logic questions like "If X then Y, else Z" to get
              router nodes automatically.
            </p>
          </div>
        </div>
      </div>

      {/* Footer Run Button */}
      <div className="p-4 border-t border-white/10 bg-[#050510]">
        <button className="w-full bg-[#5865F2] hover:bg-[#4752C4] text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20">
          <Play className="w-4 h-4 fill-current" />
          Run Workflow
        </button>
      </div>
    </div>
  );
}

function NodeItem({ icon: Icon, label, color }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-[#0F1016] border border-white/5 rounded-lg hover:border-white/20 cursor-grab active:cursor-grabbing group transition-colors">
      <div
        className={`w-8 h-8 rounded-lg ${color}/20 flex items-center justify-center ${color.replace("bg-", "text-")}`}
      >
        <Icon className="w-4 h-4" />
      </div>
      <span className="text-sm font-medium text-gray-300 group-hover:text-white">
        {label}
      </span>
    </div>
  );
}
