import { useState } from "react";
import { Check, X, Loader2, FileText } from "lucide-react";

export default function InvoiceCard({ data, onConfirm, onReject }) {
  const [isConfirming, setIsConfirming] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [isRejected, setIsRejected] = useState(false);

  // Safeguard: Ensure data exists
  if (!data) {
    return (
      <div className="mt-3 p-4 bg-red-900/20 border border-red-500/50 rounded-xl text-red-200 text-xs">
        Error: No invoice data received.
      </div>
    );
  }

  const { customer_name, items } = data;

  // Safeguard: Ensure items is an array
  const safeItems = Array.isArray(items) ? items : [];

  const totalAmount = safeItems.reduce(
    (sum, item) => sum + (item.quantity || 0) * (item.price || 0),
    0,
  );

  const handleConfirm = async () => {
    setIsConfirming(true);
    try {
      await onConfirm(data);
      setIsConfirmed(true);
    } catch (error) {
      console.error("Confirmation failed", error);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleReject = async () => {
    setIsRejecting(true);
    try {
      await onReject();
      setIsRejected(true);
    } catch (error) {
      console.error("Rejection failed", error);
    } finally {
      setIsRejecting(false);
    }
  };

  if (isConfirmed) {
    return (
      <div className="mt-3 w-full max-w-[320px] bg-[#5865F2]/10 border border-[#5865F2]/20 rounded-xl p-4 flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="w-8 h-8 rounded-full bg-[#5865F2] flex items-center justify-center flex-shrink-0">
          <Check className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Invoice Created</h3>
          <p className="text-xs text-[#5865F2]">
            Sent to {customer_name || "Customer"}
          </p>
        </div>
      </div>
    );
  }

  if (isRejected) {
    return (
      <div className="mt-3 w-full max-w-[320px] bg-red-900/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
          <X className="w-5 h-5 text-red-500" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-red-200">Invoice Rejected</h3>
          <p className="text-xs text-red-400">This invoice has been deleted.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl overflow-hidden transition-all duration-300">
      <div className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-[#5865F2]" />
              <h3 className="text-lg font-bold text-white">Invoice Draft</h3>
            </div>
            <p className="text-xs text-gray-400">
              Customer: {customer_name || "Unknown Customer"}
            </p>
          </div>
        </div>

        {/* Line Items */}
        <div className="mb-4 space-y-2 bg-white/5 p-3 rounded-lg">
          {safeItems.length > 0 ? (
            safeItems.map((item, idx) => (
              <div
                key={idx}
                className="flex justify-between text-sm text-gray-300"
              >
                <span>
                  {item.name || "Item"} (x{item.quantity || 0})
                </span>
                <span>₹{(item.price || 0) * (item.quantity || 0)}</span>
              </div>
            ))
          ) : (
            <p className="text-xs text-gray-500 italic">No items found</p>
          )}
        </div>

        <div className="flex justify-between items-center mb-2 px-1">
          <span className="text-sm text-gray-400">Total Amount</span>
          <span className="text-xl font-bold text-white">₹{totalAmount}</span>
        </div>

        {data.amount_paid > 0 && (
          <div className="flex justify-between items-center mb-2 px-1 pt-2 border-t border-white/5">
            <span className="text-xs text-green-400 font-medium italic">
              Amount Paid Upfront
            </span>
            <span className="text-sm font-bold text-green-400">
              - ₹{data.amount_paid}
            </span>
          </div>
        )}

        <div className="flex justify-between items-center mb-6 px-1 pt-2 border-t border-white/5">
          <span className="text-sm text-gray-400">Balance Due</span>
          <span className="text-xl font-bold text-[#5865F2]">
            ₹{totalAmount - (data.amount_paid || 0)}
          </span>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleConfirm}
            disabled={isConfirming || isRejecting}
            className="flex-1 bg-[#5865F2] hover:bg-[#4752C4] disabled:opacity-50 disabled:cursor-not-allowed text-white py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-[#5865F2]/20"
          >
            {isConfirming ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Check className="w-3 h-3" />
                Confirm & Send
              </>
            )}
          </button>
          <button
            onClick={handleReject}
            disabled={isConfirming || isRejecting}
            className="flex-1 bg-white/5 hover:bg-white/10 disabled:opacity-50 text-gray-400 hover:text-white py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors border border-white/10"
          >
            {isRejecting ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <X className="w-3 h-3" />
                Reject
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
