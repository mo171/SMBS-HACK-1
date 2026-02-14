import {
  User,
  Sparkles,
  Check,
  X,
  Loader2,
  FileText,
  CreditCard,
  Share2,
  ExternalLink,
} from "lucide-react";
import Image from "next/image";
import InvoiceCard from "./cards/InvoiceCard";
import StockCard from "./cards/StockCard";
import DebtCard from "./cards/DebtCard";
import SocialApprovalCard from "./cards/SocialApprovalCard";
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
            onReject={async () => {
              if (message.data?.invoice_id) {
                try {
                  // Reject & Delete the invoice
                  await chatService.deleteInvoice(message.data.invoice_id);
                  toast.success("Invoice rejected & deleted");
                } catch (error) {
                  toast.error("Failed to reject invoice");
                  console.error(error);
                }
              } else {
                toast.info("Invoice draft cancelled");
              }
            }}
          />
        )}

        {message.type === "GENERATE_REPORT" && (
          <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl p-5 flex flex-col gap-4 transition-all duration-300">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white capitalize">
                  {message.data?.report_type || "Inventory"} Report Ready
                </h3>
                <p className="text-[11px] text-gray-400">
                  Ready to download as {message.data?.format || "Excel"}
                </p>
              </div>
            </div>
            <button
              onClick={async () => {
                try {
                  const type = message.data?.report_type || "inventory";
                  const format = message.data?.format || "excel";

                  if (type === "ledger") {
                    if (format === "pdf") await chatService.downloadLedgerPDF();
                    else await chatService.downloadLedgerExcel();
                  } else if (type === "debtors") {
                    await chatService.downloadDebtorsExcel();
                  } else {
                    await chatService.downloadInventory();
                  }
                  toast.success(`Downloading ${type} report...`);
                } catch (error) {
                  toast.error("Failed to download report");
                  console.error(error);
                }
              }}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-green-600/10"
            >
              <Sparkles className="w-3 h-3" />
              Download {message.data?.format || "Excel"}
            </button>
          </div>
        )}

        {message.type === "GENERATE_PAYMENT_LINK" && (
          <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl p-5 flex flex-col gap-4 transition-all duration-300">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <CreditCard className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">
                  Payment Link Ready
                </h3>
                <p className="text-[11px] text-gray-400">
                  Amount: Rs. {message.data?.amount} for{" "}
                  {message.data?.customer_name}
                </p>
              </div>
            </div>
            <a
              href={message.data?.payment_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-600/10 text-center"
            >
              <ExternalLink className="w-3 h-3" />
              Open Payment Link
            </a>
          </div>
        )}

        {message.type === "PREVIEW_SOCIAL" && (
          <SocialApprovalCard
            data={message.data}
            onConfirm={async (updatedContent) => {
              const res = await chatService.confirmSocialPost(
                "default_session", // We should probably pass real sessionId here
                message.data.platform,
                updatedContent,
                message.data.image_url,
              );
              toast.success("Post Published Successfully!");
              return res; // Return so Card can get the URL
            }}
            onReject={async () => {
              await chatService.rejectSocialPost("default_session");
              toast.info("Post draft rejected");
            }}
          />
        )}

        {message.type === "POST_SOCIAL" && (
          <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl p-5 flex flex-col gap-4 transition-all duration-300">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-pink-500/10 flex items-center justify-center">
                <Share2 className="w-6 h-6 text-pink-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white capitalize">
                  Posted to {message.data?.platform}
                </h3>
                <p className="text-[11px] text-gray-400 line-clamp-1">
                  {message.data?.content}
                </p>
              </div>
            </div>
            {message.data?.url && (
              <a
                href={message.data?.url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full bg-pink-600 hover:bg-pink-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-pink-600/10 text-center"
              >
                <ExternalLink className="w-3 h-3" />
                View Post
              </a>
            )}
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
