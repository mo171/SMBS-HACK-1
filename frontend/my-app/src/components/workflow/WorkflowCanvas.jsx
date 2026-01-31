"use client";

import { useCallback, useMemo } from "react";
import { ReactFlow, Background, Controls, MiniMap, Panel } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import WorkflowNode from "./WorkflowNode";
import useWorkflowStore from "@/store/workflowStore";

const nodeTypes = {
  workflowNode: WorkflowNode,
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
  } = useWorkflowStore();

  const onNodeClick = useCallback(
    (_, node) => {
      setSelectedNode(node);
    },
    [setSelectedNode],
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

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
