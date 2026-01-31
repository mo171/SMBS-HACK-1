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

  const getStatusStyles = () => {
    if (!state) return "border-gray-600 opacity-50 bg-slate-900/50";

    if (state.status === "running") {
      return "border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)] animate-pulse bg-blue-900/10";
    }

    if (state.status === "completed") {
      return "border-green-500 bg-green-900/10 shadow-[0_0_10px_rgba(34,197,94,0.3)]";
    }

    if (state.status === "failed") {
      return "border-red-500 bg-red-900/10 shadow-[0_0_10px_rgba(239,68,68,0.3)]";
    }

    return "border-gray-400 bg-slate-900/50";
  };

  const getStatusIcon = () => {
    if (!state) return null;

    if (state.status === "running") {
      return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
    }

    if (state.status === "completed") {
      return <CheckCircle2 className="w-4 h-4 text-green-400" />;
    }

    if (state.status === "failed") {
      return <XCircle className="w-4 h-4 text-red-400" />;
    }

    return null;
  };

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

  return (
    <div
      className={`min-w-[200px] rounded-xl border-2 backdrop-blur-md transition-all ${getStatusStyles()}`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-gray-600 !border-2 !border-[#030014]"
      />

      {/* Header */}
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white text-sm">
            {data.service || data.label}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span
            className={`text-xs font-medium ${
              state?.status === "completed"
                ? "text-green-400"
                : state?.status === "failed"
                  ? "text-red-400"
                  : state?.status === "running"
                    ? "text-blue-400"
                    : "text-gray-500"
            }`}
          >
            {getStatusText()}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-3 bg-black/20 select-none">
        <p className="text-[10px] text-slate-400 uppercase tracking-wide">
          {data.task || data.description || "No task specified"}
        </p>
      </div>

      {/* Inspect Tray */}
      {state && (state.data || state.error) && (
        <div className="border-t border-white/5">
          <button
            onClick={() => setInspectOpen(!inspectOpen)}
            className="w-full px-3 py-2 flex items-center justify-between text-xs text-gray-400 hover:bg-white/5 transition-colors"
          >
            <span>Inspect Data</span>
            {inspectOpen ? (
              <ChevronUp className="w-3 h-3" />
            ) : (
              <ChevronDown className="w-3 h-3" />
            )}
          </button>

          {inspectOpen && (
            <div className="px-3 pb-3 max-h-[200px] overflow-auto">
              {state.error ? (
                <div className="bg-red-950/30 border border-red-500/20 rounded p-2">
                  <p className="text-[9px] text-red-300 font-mono">
                    {state.error}
                  </p>
                </div>
              ) : (
                <pre className="text-[9px] text-blue-300 font-mono overflow-x-auto bg-slate-950/50 rounded p-2">
                  {JSON.stringify(state.data, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !bg-gray-600 !border-2 !border-[#030014]"
      />
    </div>
  );
};

export default memo(MonitorNode);
