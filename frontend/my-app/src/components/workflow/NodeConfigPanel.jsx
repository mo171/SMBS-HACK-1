"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { X, Info } from "lucide-react";
import useWorkflowStore from "@/store/workflowStore";

export default function NodeConfigPanel() {
  const { selectedNode, setSelectedNode, updateNodeData } = useWorkflowStore();

  const { register, handleSubmit, reset, watch } = useForm({
    defaultValues: selectedNode?.data || {},
  });

  useEffect(() => {
    if (selectedNode) {
      reset(selectedNode.data);
    }
  }, [selectedNode, reset]);

  if (!selectedNode) return null;

  const onSubmit = (data) => {
    updateNodeData(selectedNode.id, data);
  };

  // Auto-save on change
  const currentValues = watch();
  useEffect(() => {
    if (selectedNode) {
      updateNodeData(selectedNode.id, currentValues);
    }
  }, [currentValues]);

  const isWhatsApp = selectedNode.data?.type === "whatsapp";

  return (
    <div className="w-80 border-l border-white/10 bg-[#0F1016]/95 backdrop-blur-xl flex flex-col h-full animate-in slide-in-from-right duration-300">
      <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
        <h3 className="text-sm font-semibold text-white/90">Configure Node</h3>
        <button
          onClick={() => setSelectedNode(null)}
          className="p-1 hover:bg-white/10 rounded-md transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
              Node Label
            </label>
            <input
              {...register("label")}
              className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
              placeholder="Enter node name..."
            />
          </div>

          {isWhatsApp && (
            <div className="space-y-4 pt-4 border-t border-white/5">
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Phone Number
                </label>
                <input
                  {...register("phoneNumber")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="+1234567890"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Message Body
                </label>
                <textarea
                  {...register("message")}
                  rows={4}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all resize-none"
                  placeholder="Hello, {{trigger_data.name}}!"
                />
              </div>

              <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg flex gap-3">
                <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[11px] font-medium text-indigo-300">
                    Dynamic Variables
                  </p>
                  <p className="text-[10px] text-indigo-300/70 leading-relaxed">
                    Use{" "}
                    <code className="bg-indigo-500/20 px-1 rounded">
                      {"{{trigger_data.field}}"}
                    </code>{" "}
                    to map data from previous steps.
                  </p>
                </div>
              </div>
            </div>
          )}

          {!isWhatsApp && (
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                Description
              </label>
              <textarea
                {...register("description")}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all resize-none"
                placeholder="Describe what this node does..."
              />
            </div>
          )}
        </form>
      </div>

      <div className="p-4 border-t border-white/10 bg-white/5">
        <button
          onClick={handleSubmit(onSubmit)}
          className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-500/20"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
}
