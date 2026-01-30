"use client";

import { useState } from "react";
import WorkflowSidebar from "./WorkflowSidebar";
import WorkflowCanvas from "./WorkflowCanvas";

export default function WorkflowBuilder() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = (prompt) => {
    setIsGenerating(true);
    setTimeout(() => {
      const newNodes = [
        { id: "1", type: "input", label: "Text Input", x: 50, y: 100 },
        {
          id: "2",
          type: "process",
          label: "Analyze Sentiment",
          x: 300,
          y: 100,
        },
        { id: "3", type: "router", label: "Semantic Router", x: 550, y: 100 },
        { id: "4", type: "process", label: "Notify Negative", x: 800, y: 50 },
        { id: "5", type: "database", label: "Save Positive", x: 800, y: 250 },
      ];

      const newEdges = [
        { id: "e1-2", source: "1", target: "2" },
        { id: "e2-3", source: "2", target: "3" },
        { id: "e3-4", source: "3", target: "4", label: "False" },
        { id: "e3-5", source: "3", target: "5", label: "True" },
      ];

      setNodes(newNodes);
      setEdges(newEdges);
      setIsGenerating(false);
    }, 1500);
  };

  const handleNodeDrag = (id, x, y) => {
    setNodes((prevNodes) =>
      prevNodes.map((node) => (node.id === id ? { ...node, x, y } : node)),
    );
  };

  return (
    <div className="flex h-full bg-[#030014] overflow-hidden relative">
      <WorkflowSidebar
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
      />
      {/* Remove onNodeDrag prop as we will handle drag internally in Canvas or pass cleaner handler */}
      <WorkflowCanvas nodes={nodes} edges={edges} setNodes={setNodes} />
    </div>
  );
}
