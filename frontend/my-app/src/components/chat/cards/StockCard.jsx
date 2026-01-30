import { Package, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function StockCard({ data }) {
  // Safeguard: Ensure data exists
  if (!data) return null;

  // The 'data' now contains: name (string), stock (number), found (boolean)
  // mapped from the backend analysis.data object
  const { name, stock, found } = data;

  if (!found) {
    return (
      <div className="mt-3 inline-flex items-center gap-3 px-4 py-3 bg-[#0F1016] border border-red-500/20 rounded-xl">
        <div className="p-2 rounded-lg bg-red-500/10 text-red-500">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="text-sm text-gray-300">
          Product not found in inventory
        </div>
      </div>
    );
  }

  const isLowStock = stock < 10;

  return (
    <div className="mt-3 w-full max-w-[280px] bg-[#0F1016] border border-white/5 rounded-xl overflow-hidden shadow-xl">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div
              className={`p-1.5 rounded-md ${isLowStock ? "bg-orange-500/10 text-orange-400" : "bg-[#5865F2]/10 text-[#5865F2]"}`}
            >
              <Package className="w-4 h-4" />
            </div>
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Inventory Status
            </span>
          </div>
          {isLowStock ? (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-500 text-[10px] font-bold">
              <AlertTriangle className="w-3 h-3" />
              LOW STOCK
            </span>
          ) : (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 text-[10px] font-bold">
              <CheckCircle2 className="w-3 h-3" />
              IN STOCK
            </span>
          )}
        </div>

        <div className="space-y-1">
          <h3
            className="text-sm font-medium text-gray-200 truncate"
            title={name}
          >
            {name || "Unnamed Product"}
          </h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white leading-none">
              {stock ?? 0}
            </span>
            <span className="text-xs text-gray-500 font-medium">
              units remaining
            </span>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-[10px] text-gray-500 uppercase tracking-tighter">
              Last Checked
            </span>
            <span className="text-[10px] text-gray-400">Just now</span>
          </div>
          <button className="text-[10px] font-bold text-[#5865F2] hover:text-[#4d59d9] transition-colors">
            VIEW DETAILS
          </button>
        </div>
      </div>
    </div>
  );
}
