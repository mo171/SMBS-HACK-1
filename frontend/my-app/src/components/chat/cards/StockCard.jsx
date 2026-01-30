import { Package } from "lucide-react";

export default function StockCard({ data }) {
  // data matches CHECK_STOCK intent result
  // Backend returns: { found: boolean, name: string, stock: number } or { found: False } inside the 'reply' or separate analysis object
  // But wait, the `intent_service` returns `UserIntent` which has `data` as `CheckStockIntent` (product_name)
  // The ACTUAL stock data is fetched by `action_service` and returned in the final JSON response from `app.py`.
  // The 'analysis' object in the response contains the Intent data. The 'reply' contains the text.
  // We might want to pass the specific stock details if available.
  // For now, let's assume we pass the *result* of the stock check if available, or just the inquiry.

  // Actually, looking at `app.py`, it returns `reply` string.
  // If we want to show a card *after* the action, we need the action result.
  // The backend `app.py` returns { status, reply, analysis }.
  // If we want to show a *rich* stock card, we should modify the backend to return the stock object, OR parse the reply?
  // Use case: User asks "Check stock for X".
  // Bot replies: "You have 50 units..." (Text)
  // AND optionally we show a visual badge.

  // Let's assume `data` passed here is { name: "Product A", stock: 50, found: true }

  const isLowStock = data.stock < 10; // Threshold

  return (
    <div className="mt-3 inline-flex items-center gap-3 px-4 py-3 bg-[#0F1016] border border-white/5 rounded-xl">
      <div
        className={`p-2 rounded-lg ${isLowStock ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400"}`}
      >
        <Package className="w-5 h-5" />
      </div>
      <div>
        <div className="text-xs text-gray-400">Current Stock</div>
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-bold text-white">{data.stock}</span>
          <span className="text-sm text-gray-500">{data.name}</span>
        </div>
      </div>
    </div>
  );
}
