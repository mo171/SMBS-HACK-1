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
    halo: "node-halo-blue",
    border: "border-blue-500/40",
    progress: "bg-blue-500",
  },
  process: {
    icon: MessageSquare,
    color: "text-purple-400",
    halo: "node-halo-purple",
    border: "border-purple-500/40",
    progress: "bg-purple-500",
  },
  router: {
    icon: GitBranch,
    color: "text-orange-400",
    halo: "node-halo-orange",
    border: "border-orange-500/40",
    progress: "bg-orange-500",
  },
  database: {
    icon: Database,
    color: "text-emerald-400",
    halo: "node-halo-emerald",
    border: "border-emerald-500/40",
    progress: "bg-emerald-500",
  },
  whatsapp: {
    icon: MessageCircle,
    color: "text-emerald-400",
    halo: "node-halo-emerald",
    border: "border-emerald-500/40",
    progress: "bg-emerald-500",
  },
  razorpay: {
    icon: CreditCard,
    color: "text-blue-500",
    halo: "node-halo-blue",
    border: "border-blue-500/40",
    progress: "bg-blue-500",
  },
  google_sheets: {
    icon: FileSpreadsheet,
    color: "text-green-500",
    halo: "node-halo-emerald",
    border: "border-green-500/40",
    progress: "bg-green-500",
  },
  output: {
    icon: Mail,
    color: "text-pink-400",
    halo: "node-halo-pink",
    border: "border-pink-500/40",
    progress: "bg-pink-500",
  },
};

const WorkflowNode = ({ data, selected }) => {
  const config = NODE_CONFIG[data.service] || NODE_CONFIG["process"];
  const Icon = config.icon;

  return (
    <div
      className={`group relative w-[260px] rounded-xl transition-all duration-300 ${
        selected
          ? "node-selected-frame scale-[1.02]"
          : `node-frame ${config.halo}`
      }`}
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
        <div className="flex items-center gap-3 mb-3">
          <div
            className={`p-1.5 rounded-lg bg-white/5 border border-white/10 ${config.color}`}
          >
            <Icon size={16} strokeWidth={2.5} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-[14px] font-bold text-white truncate leading-tight">
              {data.label || data.service?.replace("_", " ") || "Node"}
            </h3>
            <span className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">
              {data.service || "Action"}
            </span>
          </div>
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
        </div>

        {/* Completion Bar */}
        <div className="space-y-1.5 mb-4">
          <div className="flex justify-between items-end">
            <span className="text-[10px] font-bold text-white/60 uppercase">
              Completion
            </span>
            <span className="text-[10px] font-bold text-white">85%</span>
          </div>
          <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
            <div
              className={`h-full ${config.progress} rounded-full transition-all duration-500`}
              style={{ width: "85%" }}
            />
          </div>
        </div>
      </div>

      {/* Description / Checklist Body */}
      <div className="px-4 pb-4 space-y-3">
        <p className="text-[11px] text-gray-400 leading-relaxed italic">
          "{data.description || data.task || "Process workflow event"}"
        </p>

        <div className="space-y-2 pt-1 border-t border-white/5">
          {[
            { label: "Verify payload signature", status: "bg-emerald-500" },
            { label: "Map dynamic variables", status: "bg-blue-500" },
            { label: "Execute service task", status: "bg-orange-500" },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-2.5">
              <div className={`w-1.5 h-1.5 rounded-full ${item.status}`} />
              <span className="text-[10px] text-white/70 font-medium">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Branding (Optional subtext) */}
      <div className="px-4 py-2 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
        <span className="text-[9px] text-gray-600 font-mono">
          ID: {data.service?.slice(0, 4).toUpperCase()}
        </span>
        <div className="flex gap-1">
          <div className="w-1 h-3 bg-white/5 rounded-full" />
          <div className="w-1 h-3 bg-white/5 rounded-full" />
        </div>
      </div>
    </div>
  );
};

export default memo(WorkflowNode);
