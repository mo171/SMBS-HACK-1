import { IndianRupee } from "lucide-react";

export default function DebtCard({ data }) {
  // data matches PAYMENT_REMINDER logic from action_service:
  // { customer: string, total_billed: number, total_paid: number, balance_due: number }

  return (
    <div className="mt-3 w-full min-w-[280px] bg-[#0F1016] border border-white/5 rounded-xl overflow-hidden relative">
      <div className="absolute top-0 right-0 p-3 opacity-10">
        <IndianRupee className="w-24 h-24 text-white" />
      </div>

      <div className="p-5 relative z-10">
        <h3 className="text-sm font-medium text-gray-400 mb-1">
          Outstanding Balance
        </h3>
        <div className="text-2xl font-bold text-white mb-4">
          {data.customer}
        </div>

        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Total Billed</span>
            <span className="text-white">₹{data.total_billed}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Total Paid</span>
            <span className="text-green-400">-₹{data.total_paid}</span>
          </div>
          <div className="h-px bg-white/10 my-2" />
          <div className="flex justify-between text-sm font-bold">
            <span className="text-gray-400">Due Amount</span>
            <span className="text-red-400">₹{data.balance_due}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
