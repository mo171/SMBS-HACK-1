import { User, Sparkles, Check, X, Loader2, FileText } from "lucide-react";
import Image from "next/image";
import InvoiceCard from "./cards/InvoiceCard";
import StockCard from "./cards/StockCard";
import DebtCard from "./cards/DebtCard";
import { toast } from "sonner";
import { chatService } from "@/services/chatService";

export default function MessageBubble({ message }) {
  const isAi = message.role === "ai";

  return (
    <div
      className={`flex gap-4 ${isAi ? "items-start" : "items-start flex-row-reverse"}`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isAi ? "bg-[#5865F2]" : "bg-purple-600"
        }`}
      >
        {isAi ? (
          // Use Sparkles or a Logo for AI
          <Sparkles className="w-4 h-4 text-white" />
        ) : (
          <span className="text-xs font-bold text-white">ME</span>
        )}
      </div>

      {/* Content */}
      <div
        className={`flex flex-col max-w-[80%] ${isAi ? "items-start" : "items-end"}`}
      >
        {/* Main Bubble */}
        {message.type !== "loading" && (
          <div
            className={`px-5 py-4 rounded-2xl text-sm leading-relaxed ${
              isAi
                ? "bg-white/5 text-gray-200 border border-white/10 rounded-tl-sm"
                : "bg-[#7047EB] text-white rounded-tr-sm"
            }`}
          >
            {message.content}
          </div>
        )}

        {/* Dynamic Cards */}
        {message.type === "CREATE_INVOICE" && (
          <InvoiceCard
            data={message.data}
            onConfirm={async () => {
              if (message.data?.invoice_id) {
                try {
                  // 1. Confirm the invoice status
                  await chatService.confirmInvoice(message.data.invoice_id);
                  toast.success("Invoice Confirmed & Status Updated");

                  // 2. Automatically trigger the PDF download
                  await chatService.downloadInvoice(message.data.invoice_id);
                  toast.info("Downloading Invoice PDF...");
                } catch (error) {
                  toast.error("Failed to process invoice confirmation");
                  console.error(error);
                  throw error;
                }
              } else {
                toast.error(
                  "Error: Invoice ID missing. Try creating a new invoice.",
                );
              }
            }}
            onReject={() => toast.info("Invoice cancelled")}
          />
        )}

        {message.type === "GENERATE_REPORT" && (
          <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl p-5 flex flex-col gap-4 transition-all duration-300">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">
                  Inventory Report Ready
                </h3>
                <p className="text-[11px] text-gray-400">
                  Ready to download as Excel
                </p>
              </div>
            </div>
            <button
              onClick={async () => {
                try {
                  await chatService.downloadInventory();
                  toast.success("Downloading Inventory Report...");
                } catch (error) {
                  toast.error("Failed to download report");
                  console.error(error);
                }
              }}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-green-600/10"
            >
              <Sparkles className="w-3 h-3" />
              Download Excel
            </button>
          </div>
        )}

        {message.type === "CHECK_STOCK" && <StockCard data={message.data} />}

        {message.type === "PAYMENT_REMINDER" && (
          <DebtCard data={message.data} />
        )}

        {/* Legacy Support for Mock Data (remove if not needed) */}
        {message.type === "rich-card" &&
          message.data?.cardType === "invoice_draft" && (
            <InvoiceCard
              data={{
                customer_name: message.data.details.client,
                items: [
                  {
                    name: "Service",
                    quantity: 1,
                    price: parseInt(
                      message.data.details.amount.replace(/[^0-9]/g, ""),
                    ),
                  },
                ],
              }}
              onConfirm={() => toast.success("Mock Invoice Confirmed")}
            />
          )}

        {/* Loading State */}
        {message.type === "loading" && (
          <div className="flex items-center gap-3 px-5 py-4 bg-[#0F1016] border border-white/5 rounded-2xl rounded-tl-sm text-sm text-gray-300">
            <Loader2 className="w-4 h-4 animate-spin text-[#5865F2]" />
            {message.content}
          </div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-gray-600 mt-2 px-1">
          {message.timestamp}
        </span>
      </div>
    </div>
  );
}
