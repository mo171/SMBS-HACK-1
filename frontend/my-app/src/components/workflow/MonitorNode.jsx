"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import useWorkflowStore from "@/store/workflowStore";
import { useState } from "react";

const MonitorNode = ({ id, data }) => {
  const nodeStates = useWorkflowStore((s) => s.nodeStates);
  const [inspectOpen, setInspectOpen] = useState(false);

  const state = nodeStates[id];

  const getStatusText = () => {
    if (!state) return "Pending";

    switch (state.status) {
      case "running":
        return "Running";
      case "completed":
        return "Done";
      case "failed":
        return "Failed";
      default:
        return "Pending";
    }
  };

  const getStatusStyles = () => {
    if (!state)
      return {
        halo: "opacity-50",
        border: "border-gray-600/30",
        dot: "bg-gray-500",
        progress: "bg-gray-700",
      };

    if (state.status === "running") {
      return {
        halo: "node-halo-blue",
        border: "border-blue-500/50",
        dot: "bg-blue-400 animate-pulse",
        progress: "bg-blue-500",
      };
    }

    if (state.status === "completed") {
      return {
        halo: "node-halo-emerald",
        border: "border-emerald-500/50",
        dot: "bg-emerald-400",
        progress: "bg-emerald-500",
      };
    }

    if (state.status === "failed") {
      return {
        halo: "node-halo-pink",
        border: "border-red-500/50",
        dot: "bg-red-400",
        progress: "bg-red-500",
      };
    }

    return {
      halo: "opacity-70",
      border: "border-gray-500/30",
      dot: "bg-gray-400",
      progress: "bg-gray-600",
    };
  };

  const statusStyle = getStatusStyles();

  return (
    <div
      className={`group relative w-[260px] rounded-xl transition-all duration-500 node-frame ${statusStyle.halo}`}
    >
      {/* Handles */}
      <Handle
        id="top"
        type="target"
        position={Position.Top}
        className="!w-2 !h-2 !bg-white !border-none !-top-1 z-50 opacity-0 group-hover:opacity-100 transition-opacity"
      />
      <Handle
        id="left"
        type="target"
        position={Position.Left}
        className="!w-2 !h-2 !bg-white !border-none !-left-1 z-50 opacity-0 group-hover:opacity-100 transition-opacity"
      />
      <Handle
        id="right"
        type="source"
        position={Position.Right}
        className="!w-2 !h-2 !bg-white !border-none !-right-1 z-50 opacity-0 group-hover:opacity-100 transition-opacity"
      />
      <Handle
        id="bottom"
        type="source"
        position={Position.Bottom}
        className="!w-2 !h-2 !bg-white !border-none !-bottom-1 z-50 opacity-0 group-hover:opacity-100 transition-opacity"
      />

      {/* Header Area */}
      <div className="p-4 pb-2">
        <div className="flex items-center justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-[14px] font-bold text-white truncate leading-tight">
              {data.service || data.label || "Monitor"}
            </h3>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className={`w-1.5 h-1.5 rounded-full ${statusStyle.dot}`} />
              <span className="text-[10px] font-bold text-gray-500 uppercase tracking-tight">
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>

        {/* Completion Bar (Live) */}
        <div className="space-y-1.5 mb-4">
          <div className="flex justify-between items-end">
            <span className="text-[10px] font-bold text-white/60 uppercase">
              Execution
            </span>
            <span className="text-[10px] font-bold text-white">
              {state?.status === "completed"
                ? "100%"
                : state?.status === "running"
                  ? "45%"
                  : "0%"}
            </span>
          </div>
          <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
            <div
              className={`h-full ${statusStyle.progress} rounded-full transition-all duration-1000 ${state?.status === "running" ? "animate-progress shadow-[0_0_8px_rgba(59,130,246,0.5)]" : ""}`}
              style={{
                width:
                  state?.status === "completed"
                    ? "100%"
                    : state?.status === "running"
                      ? "45%"
                      : "0%",
              }}
            />
          </div>
        </div>
      </div>

      {/* Body / Task Info */}
      <div className="px-4 pb-4 space-y-3">
        <p className="text-[11px] text-gray-400 leading-relaxed italic">
          "{data.task || data.description || "Executing workflow task..."}"
        </p>
      </div>

      {/* Inspect Tray */}
      {state && (state.data || state.error) && (
        <div className="border-t border-white/10 bg-white/[0.02]">
          <button
            onClick={() => setInspectOpen(!inspectOpen)}
            className="w-full px-4 py-2 flex items-center justify-between text-[11px] text-gray-400 hover:text-white transition-colors"
          >
            <span className="font-bold uppercase tracking-tighter">
              Debug Log
            </span>
            {inspectOpen ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {inspectOpen && (
            <div className="px-4 pb-4 max-h-[200px] overflow-auto scrollbar-thin scrollbar-thumb-white/10">
              {state.error ? (
                <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                  <p className="text-[10px] text-red-300 font-mono break-words leading-relaxed leading-6">
                    Error: {state.error}
                  </p>
                </div>
              ) : (
                <div className="relative">
                  <pre className="text-[10px] text-blue-300 font-mono overflow-x-auto bg-slate-950/40 rounded-lg p-3 border border-white/10">
                    {JSON.stringify(state.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Footer Meta */}
      <div className="px-4 py-2 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
        <span className="text-[9px] text-gray-600 font-mono">
          NODE_EXEC_ID: {id?.slice(-6).toUpperCase()}
        </span>
      </div>
    </div>
  );
};

export default memo(MonitorNode);
