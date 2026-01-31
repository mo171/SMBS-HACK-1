"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import {
  MessageSquare,
  GitBranch,
  Database,
  Mail,
  Terminal,
  MessageCircle, // WhatsApp icon
  CreditCard, // Razorpay icon
  FileSpreadsheet, // Google Sheets icon
} from "lucide-react";

const NODE_CONFIG = {
  input: {
    icon: Terminal,
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    border: "border-blue-400/20",
  },
  process: {
    icon: MessageSquare,
    color: "text-purple-400",
    bg: "bg-purple-400/10",
    border: "border-purple-400/20",
  },
  router: {
    icon: GitBranch,
    color: "text-orange-400",
    bg: "bg-orange-400/10",
    border: "border-orange-400/20",
  },
  database: {
    icon: Database,
    color: "text-green-400",
    bg: "bg-green-400/10",
    border: "border-green-400/20",
  },
  whatsapp: {
    icon: MessageCircle,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-400/20",
  },
  razorpay: {
    icon: CreditCard,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  google_sheets: {
    icon: FileSpreadsheet,
    color: "text-green-500",
    bg: "bg-green-500/10",
    border: "border-green-500/20",
  },
  output: {
    icon: Mail,
    color: "text-pink-400",
    bg: "bg-pink-400/10",
    border: "border-pink-400/20",
  },
};

const WorkflowNode = ({ data, selected }) => {
  // Use data.service for config lookup, fallback to process
  const config = NODE_CONFIG[data.service] || NODE_CONFIG["process"];
  const Icon = config.icon;

  return (
    <div
      className={`w-[200px] rounded-xl border backdrop-blur-md transition-all ${
        selected ? "ring-2 ring-indigo-500 shadow-lg shadow-indigo-500/20" : ""
      } ${config.bg} ${config.border} hover:shadow-lg hover:shadow-indigo-500/10`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-gray-600 !border-2 !border-[#030014]"
      />

      {/* Header */}
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between select-none">
        <div className="flex items-center gap-3">
          <div
            className={`w-6 h-6 rounded-md flex items-center justify-center bg-black/20 ${config.color}`}
          >
            <Icon className="w-3.5 h-3.5" />
          </div>
          <span className="text-sm font-semibold text-white/90 capitalize">
            {data.service || data.label || "Node"}
          </span>
        </div>
        {/* Status Dot */}
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
      </div>

      {/* Body */}
      <div className="p-3 bg-black/20 select-none">
        <p className="text-[10px] text-gray-400">
          {data.task || data.description || "Configuration"}
        </p>
        <div className="mt-1 h-1 w-full bg-white/5 rounded-full overflow-hidden">
          <div className="h-full w-2/3 bg-white/10" />
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !bg-gray-600 !border-2 !border-[#030014]"
      />
    </div>
  );
};

export default memo(WorkflowNode);
