import { create } from "zustand";
import { addEdge, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";

const useWorkflowStore = create((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,

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
}));

export default useWorkflowStore;
