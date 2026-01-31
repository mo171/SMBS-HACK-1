"use client";

import { Sparkles, Play } from "lucide-react";
import { useState } from "react";
import useWorkflowStore from "@/store/workflowStore";
import { toast } from "react-hot-toast";

export default function WorkflowSidebar() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const { setElements } = useWorkflowStore();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    console.log("🚀 [WorkflowSidebar] Generate button pressed");
    console.log("📝 [WorkflowSidebar] Prompt:", prompt);

    setIsGenerating(true);
    try {
      const { api } = await import("@/lib/axios");
      const { supabase } = await import("@/lib/supabase");
      const { useAuthStore } = await import("@/store/authStore");

      // Get current user
      const user = useAuthStore.getState().user;
      console.log("👤 [WorkflowSidebar] Current user:", user?.id);

      if (!user) {
        console.error("❌ [WorkflowSidebar] No user logged in");
        toast.error("Please log in to generate workflows");
        return;
      }

      // Call the new endpoint with query params
      console.log("📡 [WorkflowSidebar] Calling /workflow/draft endpoint");
      console.log("📤 [WorkflowSidebar] Request params:", {
        prompt,
        user_id: user.id,
      });

      const response = await api.post("/workflow/draft", null, {
        params: {
          prompt: prompt,
          user_id: user.id,
        },
      });

      console.log("📥 [WorkflowSidebar] API response:", response.data);
      const { workflow_id } = response.data;
      console.log("🆔 [WorkflowSidebar] Workflow ID:", workflow_id);

      // Fetch the workflow from Supabase
      console.log("🔍 [WorkflowSidebar] Fetching workflow from Supabase");
      const { data: workflow, error } = await supabase
        .from("workflow_blueprints")
        .select("*")
        .eq("id", workflow_id)
        .single();

      if (error) {
        console.error("❌ [WorkflowSidebar] Supabase fetch error:", error);
        throw new Error("Failed to fetch workflow: " + error.message);
      }

      console.log("✅ [WorkflowSidebar] Workflow fetched:", workflow);
      console.log("📊 [WorkflowSidebar] Nodes count:", workflow.nodes?.length);
      console.log("🔗 [WorkflowSidebar] Edges count:", workflow.edges?.length);

      // Ensure nodes have the correct type for our custom components
      const formattedNodes = workflow.nodes.map((node) => ({
        ...node,
        type: "workflowNode",
      }));

      console.log("🎨 [WorkflowSidebar] Formatted nodes:", formattedNodes);
      console.log("💾 [WorkflowSidebar] Setting elements to store");

      setElements(formattedNodes, workflow.edges);

      console.log("✨ [WorkflowSidebar] Workflow generation complete!");
      toast.success("Workflow generated successfully!");
      setPrompt("");
    } catch (error) {
      console.error("❌ [WorkflowSidebar] Generation error:", error);
      console.error(
        "❌ [WorkflowSidebar] Error details:",
        error.message,
        error.stack,
      );
      toast.error("Failed to generate workflow. Please try again.");
    } finally {
      setIsGenerating(false);
      console.log("🏁 [WorkflowSidebar] Generation process ended");
    }
  };

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
              placeholder="Describe your workflow... e.g., 'When a new order comes in, send a WhatsApp message to the customer'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isGenerating}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              !prompt.trim() || isGenerating
                ? "bg-white/5 text-gray-600 cursor-not-allowed"
                : "bg-white text-black hover:bg-gray-200 shadow-lg shadow-white/10"
            }`}
          >
            {isGenerating ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                <span>Generating...</span>
              </div>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Workflow
              </>
            )}
          </button>

          <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
            <h4 className="text-indigo-400 text-xs font-bold mb-1 flex items-center gap-2">
              <Sparkles className="w-3 h-3" />
              AI Tip
            </h4>
            <p className="text-xs text-indigo-200/70 leading-relaxed">
              Describe your business process in natural language. Our AI will
              draft the nodes and connections for you.
            </p>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-white/10 bg-[#050510]">
        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20">
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
