import { User, Sparkles, Check, X, Loader2 } from "lucide-react";
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
                ? "bg-transparent text-gray-200"
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
                  // InvoiceCard handles the loading state UI, so we just wait
                  await chatService.confirmInvoice(message.data.invoice_id);
                  toast.success("Invoice Made");
                } catch (error) {
                  toast.error("Failed to confirm invoice");
                  console.error(error);
                  throw error; // Re-throw so InvoiceCard knows it failed
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
