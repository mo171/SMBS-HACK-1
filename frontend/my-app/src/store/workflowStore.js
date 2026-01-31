import { create } from "zustand";
import { addEdge, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";

const useWorkflowStore = create((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,

  // Realtime monitoring state
  nodeStates: {}, // Map of node_id -> { status, data, error }
  currentRunId: null,
  monitorMode: false,
  realtimeChannel: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge({ ...connection, type: "smoothstep" }, get().edges),
    });
  },

  setElements: (nodes, edges) => {
    set({ nodes, edges });
  },

  setSelectedNode: (node) => {
    set({ selectedNode: node });
  },

  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...data } }
          : node,
      ),
    });
  },

  // Realtime monitoring actions
  setMonitorMode: (enabled) => {
    set({ monitorMode: enabled });
    if (!enabled) {
      // Clear monitoring state when exiting monitor mode
      get().clearNodeStates();
    }
  },

  initLiveMonitor: (runId) => {
    console.log("🔴 [workflowStore] initLiveMonitor called with runId:", runId);
    const { supabase } = require("@/lib/supabase");

    // Clean up existing subscription if any
    if (get().realtimeChannel) {
      console.log("🧹 [workflowStore] Cleaning up existing channel");
      supabase.removeChannel(get().realtimeChannel);
    }

    // Create new subscription
    console.log(
      "📡 [workflowStore] Creating new realtime channel:",
      `live-run-${runId}`,
    );
    const channel = supabase
      .channel(`live-run-${runId}`)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "workflow_logs",
          filter: `run_id=eq.${runId}`,
        },
        (payload) => {
          console.log("📨 [workflowStore] Realtime update received:", payload);
          if (payload.new && payload.new.step_results) {
            console.log(
              "📊 [workflowStore] Step results:",
              payload.new.step_results,
            );
            set({ nodeStates: payload.new.step_results });
            console.log("✅ [workflowStore] Node states updated");
          } else {
            console.warn("⚠️ [workflowStore] No step_results in payload");
          }
        },
      )
      .subscribe();

    console.log("✅ [workflowStore] Channel subscribed");
    set({ realtimeChannel: channel, currentRunId: runId });

    // Return cleanup function
    return () => {
      console.log("🧹 [workflowStore] Cleanup function called");
      supabase.removeChannel(channel);
      set({ realtimeChannel: null, currentRunId: null });
    };
  },

  clearNodeStates: () => {
    console.log("🧹 [workflowStore] clearNodeStates called");
    const { supabase } = require("@/lib/supabase");

    // Clean up subscription
    if (get().realtimeChannel) {
      console.log("📡 [workflowStore] Removing realtime channel");
      supabase.removeChannel(get().realtimeChannel);
    }

    set({
      nodeStates: {},
      currentRunId: null,
      realtimeChannel: null,
    });
    console.log("✅ [workflowStore] Node states cleared");
  },
}));

export default useWorkflowStore;
