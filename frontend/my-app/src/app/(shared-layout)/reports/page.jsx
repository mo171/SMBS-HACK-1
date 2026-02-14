"use client";

import { useState } from "react";
import { api } from "@/lib/axios";
import {
  BarChart,
  Download,
  FileSpreadsheet,
  FileText,
  Search,
  Filter,
  ArrowRight,
  TrendingUp,
  Package,
  CheckCircle2,
  Clock,
} from "lucide-react";

export default function ReportsPage() {
  const [loading, setLoading] = useState({});

  const downloadReport = async (type, id = null) => {
    setLoading((prev) => ({ ...prev, [type]: true }));
    try {
      let url = "";
      let filename = "";

      if (type === "inventory") {
        url = "/export/inventory";
        filename = "inventory.xlsx";
      } else if (type === "invoice-pdf") {
        url = `/export/invoice/${id}`;
        filename = `invoice_${id}.pdf`;
      } else if (type === "invoice-excel") {
        url = `/export/invoice-excel/${id}`;
        filename = `invoice_${id}.xlsx`;
      } else if (type === "ledger") {
        url = "/export/overall-ledger";
        filename = "overall_ledger.pdf";
      } else if (type === "aging") {
        url = "/export/aging-debtors";
        filename = "aging_debtors.xlsx";
      }

      const response = await api.get(url, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed:", err);
    } finally {
      setLoading((prev) => ({ ...prev, [type]: false }));
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-white">
      {/* Header */}
      <div className="flex justify-between items-end border-b border-white/10 pb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Reports & Analytics</h1>
          <p className="text-gray-400">
            Download business summaries and inventory data
          </p>
        </div>
        <div className="flex gap-4">
          <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all text-sm">
            <Filter className="w-4 h-4" />
            Advanced Filters
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Inventory Report */}
        <ReportCard
          icon={Package}
          title="Full Inventory Report"
          desc="Current stock levels for all products as of today."
          format="EXCEL"
          onDownload={() => downloadReport("inventory")}
          loading={loading["inventory"]}
        />

        {/* Ledger Report */}
        <ReportCard
          icon={TrendingUp}
          title="Overall Ledger"
          desc="Summary of all billed and received payments."
          format="PDF"
          onDownload={() => downloadReport("ledger")}
          loading={loading["ledger"]}
        />

        {/* Debtor List */}
        <ReportCard
          icon={Clock}
          title="Aging Debtors"
          desc="Detailed list of all customers with outstanding balance."
          format="EXCEL"
          onDownload={() => downloadReport("aging")}
          loading={loading["aging"]}
        />
      </div>

      {/* Recent Invoices Section */}
      <div className="bg-[#0A0A0A] border border-white/5 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-white/5 flex justify-between items-center">
          <h2 className="text-xl font-bold">Recent Invoice Exports</h2>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search invoice ID..."
              className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-indigo-500/50 w-64"
            />
          </div>
        </div>
        <div className="p-0">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-white/[0.02] text-gray-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-medium">Invoice ID</th>
                <th className="px-6 py-4 font-medium">Customer</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <InvoiceRow
                id="INV-001"
                customer="Sharma General Store"
                date="2024-05-12"
                onPdf={() => downloadReport("invoice-pdf", "INV-001")}
                onExcel={() => downloadReport("invoice-excel", "INV-001")}
              />
              <InvoiceRow
                id="INV-002"
                customer="Rahul Sweets"
                date="2024-05-11"
                onPdf={() => downloadReport("invoice-pdf", "INV-002")}
              />
              <InvoiceRow
                id="INV-003"
                customer="Amit Traders"
                date="2024-05-10"
                onPdf={() => downloadReport("invoice-pdf", "INV-003")}
              />
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ReportCard({
  icon: Icon,
  title,
  desc,
  format,
  onDownload,
  loading,
  tag,
  disabled,
}) {
  return (
    <div
      className={`p-6 bg-[#0A0A0A] border border-white/5 rounded-2xl hover:border-white/20 transition-all group ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <div className="flex justify-between items-start mb-6">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
          <Icon className="w-6 h-6" />
        </div>
        {tag ? (
          <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {tag}
          </span>
        ) : (
          <span className="text-[10px] px-2 py-1 rounded-full bg-white/5 text-gray-400 border border-white/10 font-bold tracking-widest">
            {format}
          </span>
        )}
      </div>
      <h3 className="text-lg font-bold mb-2 group-hover:text-indigo-400 transition-colors">
        {title}
      </h3>
      <p className="text-sm text-gray-400 mb-6">{desc}</p>

      {!disabled && (
        <button
          onClick={onDownload}
          disabled={loading}
          className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center gap-2 text-sm font-medium transition-all"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <Download className="w-4 h-4" />
          )}
          {loading ? "Preparing..." : `Download ${format}`}
        </button>
      )}
    </div>
  );
}

function InvoiceRow({ id, customer, date, onPdf, onExcel }) {
  return (
    <tr className="hover:bg-white/[0.01] transition-colors">
      <td className="px-6 py-4 text-sm font-medium">{id}</td>
      <td className="px-6 py-4 text-sm text-gray-400">{customer}</td>
      <td className="px-6 py-4 text-sm text-gray-500">{date}</td>
      <td className="px-6 py-4 text-right space-x-2">
        <button
          onClick={onPdf}
          className="p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500/20 transition-all title='Download PDF'"
        >
          <FileText className="w-4 h-4" />
        </button>
        <button
          onClick={onExcel}
          className="p-2 bg-green-500/10 text-green-500 rounded-lg hover:bg-green-500/20 transition-all title='Download Excel'"
        >
          <FileSpreadsheet className="w-4 h-4" />
        </button>
      </td>
    </tr>
  );
}
