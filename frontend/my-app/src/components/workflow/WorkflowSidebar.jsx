"use client";

import { Sparkles, Play, Save, FolderOpen, Trash2 } from "lucide-react";
import { useState, useEffect } from "react";
import useWorkflowStore from "@/store/workflowStore";
import { useAuthStore } from "@/store/authStore";
import { toast } from "react-hot-toast";
import { applyAutoLayout } from "@/lib/autoLayout";

export default function WorkflowSidebar() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [workflowName, setWorkflowName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [savedWorkflows, setSavedWorkflows] = useState([]);
  const [isLoadingWorkflows, setIsLoadingWorkflows] = useState(false);
  const [showSavedWorkflows, setShowSavedWorkflows] = useState(true); // Default to true

  const { setElements, nodes, edges } = useWorkflowStore();

  // Use the hook to subscribe to user changes
  const { user } = useAuthStore();

  // Load saved workflows when user becomes available
  useEffect(() => {
    if (user) {
      loadSavedWorkflows();
    }
  }, [user]); // Re-run when user changes

  const loadSavedWorkflows = async () => {
    if (!user) return; // Added early exit if no user

    setIsLoadingWorkflows(true);
    try {
      const { api } = await import("@/lib/axios");
      // Removed: const { useAuthStore } = await import("@/store/authStore");
      // Removed: const user = useAuthStore.getState().user;
      // Removed: if (!user) { console.log("⚠️ [WorkflowSidebar] No user found, skipping load"); return; }

      console.log("🔄 [WorkflowSidebar] Loading workflows for user:", user.id);
      const response = await api.get("/workflows", {
        params: { user_id: user.id },
      });

      console.log(
        "✅ [WorkflowSidebar] Loaded workflows:",
        response.data.workflows,
      );
      setSavedWorkflows(response.data.workflows || []);
      // Removed: Ensure the list is shown if we have items
      // Removed: if (response.data.workflows?.length > 0) { setShowSavedWorkflows(true); }
    } catch (error) {
      console.error("❌ [WorkflowSidebar] Failed to load workflows:", error);
      toast.error("Failed to load saved workflows");
    } finally {
      setIsLoadingWorkflows(false);
    }
  };

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

      const formattedNodes = workflow.nodes.map((node) => ({
        ...node,
        type: "workflowNode",
      }));

      const formattedEdges = (workflow.edges || []).map((edge) => ({
        ...edge,
        sourceHandle: edge.sourceHandle || "right",
        targetHandle: edge.targetHandle || "left",
        animated: true,
      }));

      // Apply auto-layout to arrange nodes systematically
      const layoutedNodes = applyAutoLayout(formattedNodes, formattedEdges);

      setElements(layoutedNodes, formattedEdges);

      console.log("✨ [WorkflowSidebar] Workflow generation complete!");
      toast.success("Workflow generated successfully!");
      setPrompt("");

      // Refresh saved workflows list
      loadSavedWorkflows();
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

  const handleSaveWorkflow = async () => {
    if (!workflowName.trim()) {
      toast.error("Please enter a workflow name");
      return;
    }

    if (nodes.length === 0) {
      toast.error("Cannot save empty workflow");
      return;
    }

    setIsSaving(true);
    try {
      const { api } = await import("@/lib/axios");
      const { useAuthStore } = await import("@/store/authStore");

      const user = useAuthStore.getState().user;
      if (!user) {
        toast.error("Please log in to save workflows");
        return;
      }

      console.log("💾 [WorkflowSidebar] Saving workflow:", workflowName);
      console.log("📊 [WorkflowSidebar] Nodes:", nodes.length);
      console.log("🔗 [WorkflowSidebar] Edges:", edges.length);

      const response = await api.post(
        "/workflow/save",
        {
          blueprint: {
            nodes: nodes.map((node) => ({
              id: node.id,
              type: node.data.type || "action",
              data: node.data,
              position: node.position,
            })),
            edges,
          },
        },
        {
          params: {
            user_id: user.id,
            workflow_name: workflowName,
          },
        },
      );

      console.log("✅ [WorkflowSidebar] Workflow saved:", response.data);
      toast.success("Workflow saved successfully!");
      setWorkflowName("");

      // Refresh saved workflows list
      loadSavedWorkflows();
    } catch (error) {
      console.error("❌ [WorkflowSidebar] Save error:", error);
      toast.error("Failed to save workflow");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadWorkflow = async (workflow) => {
    try {
      console.log("📂 [WorkflowSidebar] Loading workflow:", workflow.name);

      // Ensure nodes have the correct type and edges use sideways handles
      const formattedNodes = workflow.nodes.map((node) => ({
        ...node,
        type: "workflowNode",
      }));

      const formattedEdges = (workflow.edges || []).map((edge) => ({
        ...edge,
        sourceHandle: edge.sourceHandle || "right",
        targetHandle: edge.targetHandle || "left",
        animated: true,
      }));

      console.log(
        "🔄 [WorkflowSidebar] Formatted nodes for store:",
        formattedNodes.length,
        formattedNodes[0],
      );
      console.log(
        "🔄 [WorkflowSidebar] Formatted edges for store:",
        formattedEdges.length,
      );

      // Apply auto-layout to arrange nodes systematically
      const layoutedNodes = applyAutoLayout(formattedNodes, formattedEdges);

      setElements(layoutedNodes, formattedEdges);
      toast.success(`Loaded workflow: ${workflow.name}`);
      // Don't hide the list anymore
      // setShowSavedWorkflows(false);
    } catch (error) {
      console.error("❌ [WorkflowSidebar] Load error:", error);
      toast.error("Failed to load workflow");
    }
  };

  const handleDeleteWorkflow = async (workflowId, workflowName) => {
    if (!confirm(`Are you sure you want to delete "${workflowName}"?`)) {
      return;
    }

    try {
      const { api } = await import("@/lib/axios");
      const { useAuthStore } = await import("@/store/authStore");

      const user = useAuthStore.getState().user;
      if (!user) return;

      console.log(`🗑️ [WorkflowSidebar] Deleting workflow ${workflowId}`);

      // Use the new API endpoint
      await api.delete(`/workflows/${workflowId}`, {
        params: { user_id: user.id },
      });

      toast.success("Workflow deleted successfully");

      // Remove from local state immediately for better UI response
      setSavedWorkflows((prev) => prev.filter((w) => w.id !== workflowId));

      // Also reload to be safe
      loadSavedWorkflows();
    } catch (error) {
      console.error("❌ [WorkflowSidebar] Delete error:", error);
      toast.error("Failed to delete workflow");
    }
  };

  return (
    <div className="w-80 border-r border-white/10 flex flex-col bg-[#050510] z-10">
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="space-y-6">
          {/* AI Generation Section */}
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

          {/* Saved Workflows Section */}
          <div className="pt-4 border-t border-white/10">
            <div className="flex items-center justify-between mb-3">
              <label className="text-xs font-semibold text-gray-400 uppercase">
                Saved Workflows
              </label>
              <button
                onClick={() => setShowSavedWorkflows(!showSavedWorkflows)}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                {showSavedWorkflows ? "Hide" : "Show"}
              </button>
            </div>

            {showSavedWorkflows && (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {isLoadingWorkflows ? (
                  <div className="text-center py-4">
                    <div className="w-5 h-5 border-2 border-gray-600 border-t-gray-400 rounded-full animate-spin mx-auto" />
                    <p className="text-xs text-gray-500 mt-2">Loading...</p>
                  </div>
                ) : savedWorkflows.length === 0 ? (
                  <p className="text-xs text-gray-500 text-center py-4">
                    No saved workflows yet
                  </p>
                ) : (
                  savedWorkflows.map((workflow) => (
                    <div
                      key={workflow.id}
                      onClick={() => handleLoadWorkflow(workflow)}
                      className="bg-[#0F1016] border border-white/10 rounded-lg p-3 hover:border-white/20 hover:bg-white/5 transition-all cursor-pointer group"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-white truncate">
                            {workflow.name}
                          </h4>
                          <p className="text-xs text-gray-500">
                            {workflow.nodes?.length || 0} nodes •{" "}
                            {new Date(workflow.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 ml-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteWorkflow(workflow.id, workflow.name);
                            }}
                            className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                            title="Delete workflow"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

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
