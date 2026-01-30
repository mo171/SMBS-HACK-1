import { useRef, useState, useEffect } from "react";
import WorkflowNode from "./WorkflowNode";

export default function WorkflowCanvas({ nodes, edges, setNodes }) {
  // Viewport State (Pan & Zoom)
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });

  // Drag State for Canvas Panning
  const [isPanning, setIsPanning] = useState(false);
  const lastMousePos = useRef({ x: 0, y: 0 });

  // Drag State for Nodes
  const [draggingNodeId, setDraggingNodeId] = useState(null);

  // Handlers for Canvas Panning
  const handleMouseDown = (e) => {
    // Since nodes stop propagation, any click reaching here is a background click
    setIsPanning(true);
    lastMousePos.current = { x: e.clientX, y: e.clientY };
  };

  const handleWheel = (e) => {
    e.preventDefault();
    // Zoom logic
    const zoomSensitivity = 0.001;
    const newZoom = Math.min(
      Math.max(viewport.zoom - e.deltaY * zoomSensitivity, 0.5),
      2,
    );

    setViewport((prev) => ({
      ...prev,
      zoom: newZoom,
    }));
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      // 1. Handle Canvas Panning
      if (isPanning) {
        const dx = e.clientX - lastMousePos.current.x;
        const dy = e.clientY - lastMousePos.current.y;

        setViewport((prev) => ({
          ...prev,
          x: prev.x + dx,
          y: prev.y + dy,
        }));

        lastMousePos.current = { x: e.clientX, y: e.clientY };
      }

      // 2. Handle Node Dragging
      if (draggingNodeId) {
        // Calculate delta in viewport coordinates
        // We rely on "movementX/Y" for simplicity or calc diff
        // movementX/Y matches screen pixels, which equals viewport pixels if zoom is 1.
        // If zoom != 1, we divide by zoom.

        const dx = e.movementX / viewport.zoom;
        const dy = e.movementY / viewport.zoom;

        setNodes((prev) =>
          prev.map((node) => {
            if (node.id === draggingNodeId) {
              return { ...node, x: node.x + dx, y: node.y + dy };
            }
            return node;
          }),
        );
      }
    };

    const handleMouseUp = () => {
      setIsPanning(false);
      setDraggingNodeId(null);
    };

    if (isPanning || draggingNodeId) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isPanning, draggingNodeId, viewport.zoom, setNodes]);

  return (
    <div
      className={`flex-1 bg-[#030014] relative overflow-hidden ${isPanning ? "cursor-grabbing" : "cursor-grab"}`}
      onMouseDown={handleMouseDown}
      onWheel={handleWheel}
    >
      {/* Grid Pattern with transform */}
      <div
        className="absolute inset-0 opacity-20 pointer-events-none origin-top-left"
        style={{
          backgroundImage: "radial-gradient(#4d4d4d 1px, transparent 1px)",
          backgroundSize: `${20 * viewport.zoom}px ${20 * viewport.zoom}px`,
          // Visual offset for grid is tricky with just CSS background,
          // easier to apply transform to a big container or just offset background-position
          backgroundPosition: `${viewport.x}px ${viewport.y}px`,
        }}
      />

      {/* Transform Container for Nodes & Edges */}
      <div
        className="absolute inset-0 origin-top-left"
        style={{
          transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.zoom})`,
        }}
      >
        {/* Edges */}
        <svg className="absolute inset-0 overflow-visible w-full h-full pointer-events-none z-0">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#585858" />
            </marker>
          </defs>
          {edges.map((edge) => {
            const sourceNode = nodes.find((n) => n.id === edge.source);
            const targetNode = nodes.find((n) => n.id === edge.target);

            if (!sourceNode || !targetNode) return null;

            const startX = sourceNode.x + 200;
            const startY = sourceNode.y + 40;
            const endX = targetNode.x;
            const endY = targetNode.y + 40;

            const controlPoint1X = startX + 50;
            const controlPoint1Y = startY;
            const controlPoint2X = endX - 50;
            const controlPoint2Y = endY;

            const path = `M ${startX} ${startY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${endX} ${endY}`;

            return (
              <g key={edge.id}>
                <path
                  d={path}
                  stroke="#585858"
                  strokeWidth="2"
                  fill="none"
                  markerEnd="url(#arrowhead)"
                />
                {edge.label && (
                  <text
                    x={(startX + endX) / 2}
                    y={(startY + endY) / 2 - 10}
                    fill="#888"
                    fontSize="10"
                    textAnchor="middle"
                    className="bg-black"
                  >
                    {edge.label}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <WorkflowNode
            key={node.id}
            node={node}
            onMouseDown={(e) => {
              e.stopPropagation(); // Prevent canvas panning
              setDraggingNodeId(node.id);
            }}
          />
        ))}
      </div>

      {/* Empty State */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-gray-500">
            <p>Canvas is empty</p>
            <p className="text-sm opacity-50">Generate a workflow using AI</p>
          </div>
        </div>
      )}

      {/* Zoom Controls (Mock) */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={() =>
            setViewport((prev) => ({
              ...prev,
              zoom: Math.min(prev.zoom + 0.1, 2),
            }))
          }
          className="w-8 h-8 rounded-lg bg-[#0F1016] border border-white/10 text-white flex items-center justify-center hover:bg-white/5"
        >
          +
        </button>
        <button
          onClick={() =>
            setViewport((prev) => ({
              ...prev,
              zoom: Math.max(prev.zoom - 0.1, 0.5),
            }))
          }
          className="w-8 h-8 rounded-lg bg-[#0F1016] border border-white/10 text-white flex items-center justify-center hover:bg-white/5"
        >
          -
        </button>
      </div>
    </div>
  );
}
