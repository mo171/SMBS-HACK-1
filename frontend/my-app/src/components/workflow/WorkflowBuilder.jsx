"use client";

import WorkflowSidebar from "./WorkflowSidebar";
import WorkflowCanvas from "./WorkflowCanvas";
import NodeConfigPanel from "./NodeConfigPanel";
import useWorkflowStore from "@/store/workflowStore";

export default function WorkflowBuilder() {
  const { selectedNode } = useWorkflowStore();

  return (
    <div className="flex h-full bg-[#030014] overflow-hidden relative">
      <WorkflowSidebar />
      <WorkflowCanvas />
      {selectedNode && <NodeConfigPanel />}
    </div>
  );
}
