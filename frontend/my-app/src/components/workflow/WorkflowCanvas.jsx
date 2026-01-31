"use client";

import React, { useCallback, useMemo } from "react";
import { ReactFlow, Background, Controls, MiniMap, Panel } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import WorkflowNode from "./WorkflowNode";
import MonitorNode from "./MonitorNode";
import useWorkflowStore from "@/store/workflowStore";

const nodeTypes = {
  workflowNode: WorkflowNode,
  monitorNode: MonitorNode,
};

const defaultEdgeOptions = {
  type: "smoothstep",
  animated: true,
  style: { stroke: "#585858", strokeWidth: 2 },
};

export default function WorkflowCanvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    setSelectedNode,
    monitorMode,
    setMonitorMode,
    initLiveMonitor,
    clearNodeStates,
    setNodes,
  } = useWorkflowStore();

  const [isExecuting, setIsExecuting] = React.useState(false);

  const onNodeClick = useCallback(
    (_, node) => {
      setSelectedNode(node);
    },
    [setSelectedNode],
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  const handleExecuteWorkflow = async () => {
    console.log("▶️ [WorkflowCanvas] Execute Workflow button pressed");
    console.log("📊 [WorkflowCanvas] Current nodes:", nodes);
    console.log("🔗 [WorkflowCanvas] Current edges:", edges);

    try {
      setIsExecuting(true);

      // Convert nodes to blueprint format
      const blueprint = {
        name: "Test Workflow",
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.data.type || "action",
          data: {
            service: n.data.service || "test",
            task: n.data.task || n.data.label,
            params: n.data.params || {},
          },
        })),
        edges: edges,
      };

      console.log("🏗️ [WorkflowCanvas] Blueprint constructed:", blueprint);
      console.log("📡 [WorkflowCanvas] Calling /workflow/execute endpoint");
      console.log(
        "🌐 [WorkflowCanvas] API URL:",
        process.env.NEXT_PUBLIC_API_URL,
      );

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/workflow/execute`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ blueprint, payload: {} }),
        },
      );

      console.log("📥 [WorkflowCanvas] Response status:", response.status);
      const data = await response.json();
      console.log("📥 [WorkflowCanvas] Response data:", data);

      if (data.run_id) {
        console.log("🆔 [WorkflowCanvas] Run ID received:", data.run_id);
        console.log("🔴 [WorkflowCanvas] Initializing live monitor");

        // Initialize realtime monitoring
        const cleanup = initLiveMonitor(data.run_id);

        console.log("✅ [WorkflowCanvas] Live monitor initialized");
        // Store cleanup function for later
        window.__workflowCleanup = cleanup;
      } else {
        console.warn("⚠️ [WorkflowCanvas] No run_id in response");
      }
    } catch (error) {
      console.error("❌ [WorkflowCanvas] Failed to execute workflow:", error);
      console.error(
        "❌ [WorkflowCanvas] Error details:",
        error.message,
        error.stack,
      );
      alert("Failed to execute workflow: " + error.message);
    } finally {
      setIsExecuting(false);
      console.log("🏁 [WorkflowCanvas] Execution process ended");
    }
  };

  const handleToggleMode = useCallback(() => {
    const currentNodes = useWorkflowStore.getState().nodes;
    const newMode = !monitorMode;
    setMonitorMode(newMode);

    if (newMode) {
      // Switching to monitor mode - update node types
      setNodes(currentNodes.map((n) => ({ ...n, type: "monitorNode" })));
    } else {
      // Switching to edit mode - restore original node types
      setNodes(currentNodes.map((n) => ({ ...n, type: "workflowNode" })));
      clearNodeStates();
    }
  }, [monitorMode, setMonitorMode, setNodes, clearNodeStates]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (window.__workflowCleanup) {
        window.__workflowCleanup();
      }
    };
  }, []);

  return (
    <div className="flex-1 bg-[#030014] relative h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        colorMode="dark"
      >
        <Background color="#4d4d4d" gap={20} size={1} />
        <Controls className="!bg-[#0F1016] !border-white/10 !fill-white" />
        <MiniMap
          className="!bg-[#0F1016] !border-white/10"
          maskColor="rgba(0, 0, 0, 0.5)"
          nodeColor={(n) => {
            if (n.type === "workflowNode") return "#4f46e5";
            return "#333";
          }}
        />
        <Panel
          position="top-right"
          className="bg-[#0F1016]/80 p-2 rounded-md border border-white/10 text-xs text-gray-400 backdrop-blur-md"
        >
          Use scroll to zoom • Drag to pan • Click node to configure
        </Panel>

        {/* Monitor Mode Controls */}
        <Panel
          position="top-left"
          className="bg-[#0F1016]/90 p-3 rounded-lg border border-white/10 backdrop-blur-md space-y-2"
        >
          <div className="flex items-center gap-2">
            <button
              onClick={handleToggleMode}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                monitorMode
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {monitorMode ? "📊 Monitor Mode" : "✏️ Edit Mode"}
            </button>

            {monitorMode && nodes.length > 0 && (
              <button
                onClick={handleExecuteWorkflow}
                disabled={isExecuting}
                className="px-3 py-1.5 rounded-md text-xs font-medium bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-green-500/30"
              >
                {isExecuting ? "⏳ Running..." : "▶️ Start Workflow"}
              </button>
            )}
          </div>

          {monitorMode && (
            <p className="text-[10px] text-gray-500">
              Live monitoring enabled • Updates in realtime
            </p>
          )}
        </Panel>
      </ReactFlow>

      {/* Empty State Overlay */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="text-center text-gray-500">
            <p className="text-lg font-medium">Canvas is empty</p>
            <p className="text-sm opacity-50">
              Generate a workflow using AI in the sidebar
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
