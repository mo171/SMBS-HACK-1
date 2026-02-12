"use client";

import useSWR from "swr";
import { api } from "@/lib/axios";
import { useAuth } from "@/store/authStore";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import {
  FileText,
  CheckCircle2,
  AlertCircle,
  Package,
  Mic,
  PlusSquare,
  MessageCircle,
  BarChart,
  FileCheck2,
  Wallet,
  ArrowRight,
  TrendingUp,
  User,
} from "lucide-react";

// Fetcher for SWR
const fetcher = (url) => api.get(url).then((res) => res.data);

export default function DashboardPage() {
  const { user } = useAuth();
  const {
    data: statsRes,
    error,
    isLoading,
  } = useSWR("/api/dashboard/stats", fetcher, {
    refreshInterval: 10000, // Refresh every 10s
  });

  const stats = statsRes?.data || {
    financials: { total_billed: 0, total_paid: 0, balance_due: 0 },
    debtors_count: 0,
    debtors: [],
    engagement: [],
  };

  const displayName =
    user?.user_metadata?.full_name ||
    user?.user_metadata?.username ||
    user?.email?.split("@")[0] ||
    "User";

  if (error)
    return (
      <div className="p-8 text-red-400">Failed to load dashboard data</div>
    );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-white">
      {/* Header Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#1e1b4b] to-[#0f172a] p-8 border border-white/5">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">
            Welcome Back, {displayName}!
          </h1>
          <p className="text-gray-400">
            You're all set. Let's run your business smarter today.
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ">
        <StatsCard
          icon={FileText}
          color="blue"
          label="Total Billed"
          value={`₹${stats.financials.total_billed.toLocaleString()}`}
          subValue="Lifetime billing"
          loading={isLoading}
        />
        <StatsCard
          icon={CheckCircle2}
          color="green"
          label="Total Paid"
          value={`₹${stats.financials.total_paid.toLocaleString()}`}
          subValue={`${stats.financials.total_billed > 0 ? ((stats.financials.total_paid / stats.financials.total_billed) * 100).toFixed(0) : 0}% of total`}
          loading={isLoading}
        />
        <StatsCard
          icon={AlertCircle}
          color="red"
          label="Balance Due"
          value={`₹${stats.financials.balance_due.toLocaleString()}`}
          subValue={`${stats.debtors_count} pending debtors`}
          loading={isLoading}
        />
        <StatsCard
          icon={Package}
          color="orange"
          label="Inventory Status"
          value="Healthy"
          subValue="All items in stock"
          loading={isLoading}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-[#0A0A0A] border border-white/5 rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              Social Engagement
            </h2>
            <div className="flex gap-4 text-xs">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#5865F2]"></div>{" "}
                WhatsApp
              </span>
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#E4405F]"></div>{" "}
                Instagram
              </span>
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#0085FF]"></div>{" "}
                Bluesky
              </span>
            </div>
          </div>

          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.engagement}>
                <defs>
                  <linearGradient id="colorWA" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#5865F2" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#5865F2" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis
                  dataKey="date"
                  stroke="#555"
                  fontSize={12}
                  tickFormatter={(str) => {
                    const d = new Date(str);
                    return d.toLocaleDateString([], { weekday: "short" });
                  }}
                />
                <YAxis stroke="#555" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0A0A0A",
                    border: "1px solid #333",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ fontSize: "12px" }}
                />
                <Area
                  type="monotone"
                  dataKey="whatsapp"
                  stroke="#5865F2"
                  fillOpacity={1}
                  fill="url(#colorWA)"
                />
                <Area
                  type="monotone"
                  dataKey="instagram"
                  stroke="#E4405F"
                  fillOpacity={0.1}
                  fill="#E4405F"
                />
                <Area
                  type="monotone"
                  dataKey="bluesky"
                  stroke="#0085FF"
                  fillOpacity={0.1}
                  fill="#0085FF"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Stats Summary */}
        <div className="bg-[#0A0A0A] border border-white/5 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-6">Platform Distribution</h2>
          <div className="space-y-4">
            <PlatformProgress label="WhatsApp" value={70} color="#5865F2" />
            <PlatformProgress label="Instagram" value={45} color="#E4405F" />
            <PlatformProgress label="Bluesky" value={30} color="#0085FF" />
            <PlatformProgress label="Pixelfed" value={10} color="#952fef" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4">
            {/* Record Action - Large */}
            <div className="p-6 rounded-2xl bg-[#5865F2]/10 border border-[#5865F2]/20 hover:bg-[#5865F2]/20 transition-all cursor-pointer group">
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded-full bg-[#5865F2]/20 flex items-center justify-center text-[#5865F2]">
                  <Mic className="w-5 h-5" />
                </div>
              </div>
              <h3 className="font-semibold text-lg mb-1 group-hover:text-[#5865F2] transition-colors">
                Record an Action
              </h3>
              <p className="text-sm text-gray-400">Use voice command</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <ActionSmallCard
                icon={PlusSquare}
                label="Invoice"
                onClick={() => {}}
              />
              <ActionSmallCard
                icon={BarChart}
                label="Reports"
                onClick={() => (window.location.href = "/reports")}
              />
            </div>
          </div>
        </div>

        {/* Pending Debtors */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold">Pending Debtors</h2>
          <div className="bg-[#0A0A0A] border border-white/5 rounded-2xl p-6 h-[260px] overflow-y-auto custom-scrollbar">
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-12 bg-white/5 animate-pulse rounded-xl"
                  />
                ))}
              </div>
            ) : stats.debtors.length > 0 ? (
              <div className="space-y-3">
                {stats.debtors.map((debtor, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center text-red-500 text-xs font-bold border border-red-500/20">
                        {debtor.full_name?.charAt(0) || (
                          <User className="w-3 h-3" />
                        )}
                      </div>
                      <span className="text-sm font-medium">
                        {debtor.full_name}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-red-400">
                      ₹{debtor.total_debt.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center py-8">
                <CheckCircle2 className="w-10 h-10 text-green-500/20 mb-2" />
                <p className="text-gray-500 text-sm">No pending debtors.</p>
              </div>
            )}
          </div>
        </div>

        {/* Business Activity */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold">Business Activity</h2>
          <div className="bg-white/5 border border-white/5 rounded-2xl p-6 space-y-6 h-[260px]">
            <ActivityItem
              icon={FileText}
              title="Ledger Synced"
              desc={`Current Balance: ₹${stats.financials.balance_due.toLocaleString()}`}
              time="Just now"
              color="text-blue-400"
              bg="bg-blue-400/10"
            />
            <ActivityItem
              icon={TrendingUp}
              title="Social Flux"
              desc={`${stats.engagement.reduce((acc, curr) => acc + (curr.whatsapp || 0) + (curr.instagram || 0) + (curr.bluesky || 0), 0)} interactions`}
              time="Last 7 days"
              color="text-indigo-400"
              bg="bg-indigo-400/10"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatsCard({ icon: Icon, color, label, value, subValue, loading }) {
  const colors = {
    blue: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    green: "bg-green-500/10 text-green-500 border-green-500/20",
    red: "bg-red-500/10 text-red-500 border-red-500/20",
    orange: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  };

  return (
    <div className="bg-[#0A0A0A] border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors">
      <div
        className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${colors[color]} border`}
      >
        <Icon className="w-5 h-5" />
      </div>
      <h3 className="text-gray-400 text-sm font-medium mb-1">{label}</h3>
      {loading ? (
        <div className="h-8 w-24 bg-white/5 animate-pulse rounded"></div>
      ) : (
        <div className="text-2xl font-bold mb-1">{value}</div>
      )}
      <div className="text-xs text-gray-500">{subValue}</div>
    </div>
  );
}

function ActionSmallCard({ icon: Icon, label, onClick }) {
  return (
    <div
      onClick={onClick}
      className="p-4 rounded-xl bg-[#0A0A0A] border border-white/5 hover:border-white/20 transition-all cursor-pointer group flex flex-col items-center justify-center gap-2"
    >
      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-gray-400 group-hover:text-white transition-colors">
        <Icon className="w-4 h-4" />
      </div>
      <span className="text-xs font-semibold group-hover:text-white transition-colors">
        {label}
      </span>
    </div>
  );
}

function PlatformProgress({ label, value, color }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="font-medium">{value}%</span>
      </div>
      <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

function ActivityItem({ icon: Icon, title, desc, time, color, bg }) {
  return (
    <div className="flex gap-4">
      <div
        className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center ${bg} ${color}`}
      >
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <h4 className="font-medium text-sm">{title}</h4>
        <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
        <p className="text-xs text-gray-600 mt-1">{time}</p>
      </div>
    </div>
  );
}

function ModuleCard({ icon: Icon, title, desc, tag }) {
  return (
    <div className="bg-[#0A0A0A] border border-white/5 rounded-2xl p-5 hover:border-white/20 transition-colors cursor-pointer group">
      <div className="w-10 h-10 rounded-xl bg-orange-500/10 text-orange-500 flex items-center justify-center mb-4">
        <Icon className="w-5 h-5" />
      </div>
      <h4 className="font-semibold mb-1">{title}</h4>
      <p className="text-xs text-gray-400 mb-4">{desc}</p>
      <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/20">
        {tag}
      </span>
    </div>
  );
}
