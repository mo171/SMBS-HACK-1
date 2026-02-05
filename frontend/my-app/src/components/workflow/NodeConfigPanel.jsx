"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { X, Info } from "lucide-react";
import toast from "react-hot-toast";
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
    toast.success("Configuration saved!");
  };

  // Auto-save on change (debounced to prevent infinite loops)
  const currentValues = watch();
  useEffect(() => {
    if (selectedNode && currentValues) {
      const timeoutId = setTimeout(() => {
        updateNodeData(selectedNode.id, currentValues);
      }, 300); // Debounce for 300ms

      return () => clearTimeout(timeoutId);
    }
  }, [currentValues, selectedNode?.id, updateNodeData]);

  const isWhatsApp = selectedNode.data?.service === "whatsapp";
  const isRazorpay = selectedNode.data?.service === "razorpay";
  const isGoogleSheets = selectedNode.data?.service === "google_sheets";

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
          {/* Service Type Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
              Service Type
            </label>
            <select
              {...register("service")}
              className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
            >
              <option value="whatsapp">WhatsApp</option>
              <option value="razorpay">Razorpay</option>
              <option value="google_sheets">Google Sheets</option>
            </select>
          </div>

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

          {/* Task/Action Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
              Task
            </label>
            <select
              {...register("task")}
              className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
            >
              {isWhatsApp && (
                <>
                  <option value="send_message">Send Message</option>
                  <option value="send_media">Send Media</option>
                </>
              )}
              {isRazorpay && (
                <>
                  <option value="create_payment_link">
                    Create Payment Link
                  </option>
                  <option value="create_order">Create Order</option>
                  <option value="capture_payment">Capture Payment</option>
                </>
              )}
              {isGoogleSheets && (
                <>
                  <option value="read_data">Read Data</option>
                  <option value="write_data">Write Data</option>
                  <option value="append_data">Append Data</option>
                </>
              )}
            </select>
          </div>

          {/* WhatsApp Configuration */}
          {isWhatsApp && (
            <div className="space-y-4 pt-4 border-t border-white/5">
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Phone Number
                </label>
                <input
                  {...register("params.phone")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="+1234567890"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Message Body
                </label>
                <textarea
                  {...register("params.message")}
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

          {/* Razorpay Configuration */}
          {isRazorpay && (
            <div className="space-y-4 pt-4 border-t border-white/5">
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Amount (₹)
                </label>
                <input
                  {...register("params.amount")}
                  type="number"
                  step="0.01"
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="1000"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Currency
                </label>
                <select
                  {...register("params.currency")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                >
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Customer Name
                </label>
                <input
                  {...register("params.customer_name")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="{{trigger_data.customer_name}}"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Customer Email
                </label>
                <input
                  {...register("params.customer_email")}
                  type="email"
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="{{trigger_data.customer_email}}"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Customer Phone
                </label>
                <input
                  {...register("params.customer_phone")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="{{trigger_data.customer_phone}}"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Description
                </label>
                <input
                  {...register("params.description")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="Payment for order {{trigger_data.order_id}}"
                />
              </div>

              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex gap-3">
                <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[11px] font-medium text-blue-300">
                    Payment Link
                  </p>
                  <p className="text-[10px] text-blue-300/70 leading-relaxed">
                    Creates a secure payment link that can be shared with
                    customers via WhatsApp or email.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Google Sheets Configuration */}
          {isGoogleSheets && (
            <div className="space-y-4 pt-4 border-t border-white/5">
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Spreadsheet ID
                </label>
                <input
                  {...register("params.spreadsheet_id")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-mono text-xs"
                  placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Range
                </label>
                <input
                  {...register("params.range")}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                  placeholder="A1:C10"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Values (JSON)
                </label>
                <textarea
                  {...register("params.row_data")}
                  rows={4}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all resize-none font-mono"
                  placeholder='[["Name", "Email"], ["{{trigger_data.name}}", "{{trigger_data.email}}"]]'
                />
              </div>

              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex gap-3">
                <Info className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[11px] font-medium text-green-300">
                    Google Sheets Integration
                  </p>
                  <p className="text-[10px] text-green-300/70 leading-relaxed">
                    Make sure your Google Sheets API is configured and the
                    spreadsheet is accessible.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Generic Description for other services */}
          {!isWhatsApp && !isRazorpay && !isGoogleSheets && (
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
