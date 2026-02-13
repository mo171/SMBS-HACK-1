import dagre from "dagre";

/**
 * Automatically layout workflow nodes using the dagre algorithm.
 * Arranges nodes left-to-right based on their connections.
 *
 * @param {Array} nodes - Array of workflow nodes
 * @param {Array} edges - Array of workflow edges
 * @returns {Array} - Nodes with updated positions
 */
export function applyAutoLayout(nodes, edges) {
  if (!nodes || nodes.length === 0) {
    return nodes;
  }

  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  // Configure layout direction and spacing
  dagreGraph.setGraph({
    rankdir: "LR", // Left-to-right layout
    ranksep: 200, // Horizontal spacing between ranks (reduced from 350)
    nodesep: 120, // Vertical spacing between nodes (reduced from 200)
    marginx: 50, // Margin around the graph
    marginy: 50,
  });

  // Node dimensions (matching WorkflowNode component)
  const nodeWidth = 260;
  const nodeHeight = 200;

  // Add nodes to dagre graph
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: nodeWidth,
      height: nodeHeight,
    });
  });

  // Add edges to dagre graph
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Calculate layout
  dagre.layout(dagreGraph);

  // Apply calculated positions back to nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);

    // Dagre returns center position, adjust for top-left positioning
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  console.log(
    "🎨 [AutoLayout] Applied layout to",
    layoutedNodes.length,
    "nodes",
  );
  return layoutedNodes;
}
