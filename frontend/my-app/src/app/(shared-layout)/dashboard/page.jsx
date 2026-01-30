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
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-white">
      {/* Header Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#1e1b4b] to-[#0f172a] p-8 border border-white/5">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">Welcome Back, Rajesh!</h1>
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
          label="Invoices This Month"
          value="24"
          subValue="₹5,42,000"
        />
        <StatsCard
          icon={CheckCircle2}
          color="green"
          label="Paid Invoices"
          value="18"
          subValue="75% of total"
        />
        <StatsCard
          icon={AlertCircle}
          color="red"
          label="Overdue Invoices"
          value="₹1,35,000"
          subValue="6 pending invoices"
        />
        <StatsCard
          icon={Package}
          color="orange"
          label="Inventory Alerts"
          value="3"
          subValue="Low stock items"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions - Spans 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-bold">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <p className="text-sm text-gray-400">Use voice</p>
            </div>

            {/* Create Invoice */}
            <ActionCard
              icon={PlusSquare}
              label="Create Invoice"
              sub="Manual entry"
            />

            {/* Send WhatsApp */}
            <ActionCard
              icon={MessageCircle}
              label="Send WhatsApp"
              sub="Quick message"
            />

            {/* View Reports */}
            <ActionCard icon={BarChart} label="View Reports" sub="Analytics" />
          </div>

          {/* Bottom Record Bar */}
          <div className="mt-8 relative p-1 rounded-2xl bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent">
            <div className="w-full bg-[#5865F2] hover:bg-[#4752C4] transition-colors rounded-xl p-4 flex items-center justify-center gap-3 cursor-pointer shadow-lg shadow-indigo-500/20">
              <Mic className="w-5 h-5" />
              <span className="font-semibold">Tap to Record an Action</span>
            </div>
          </div>

          {/* Available Modules Grid (from second image) */}
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-6">Available Modules</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <ModuleCard
                icon={FileCheck2}
                title="Visual Assets"
                desc="Create visuals for campaigns"
                tag="Creative"
              />
              <ModuleCard
                icon={FileCheck2}
                title="Video Creator"
                desc="Generate video content"
                tag="Creative"
              />
              <ModuleCard
                icon={FileCheck2}
                title="Copy Writer"
                desc="AI-powered marketing copy"
                tag="Creative"
              />
            </div>
          </div>
        </div>

        {/* Recent Activity - Spans 1 column */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold">Recent Activity</h2>
          <div className="bg-white/5 border border-white/5 rounded-2xl p-6 space-y-6">
            <ActivityItem
              icon={FileText}
              title="Invoice INV-0024 created"
              desc="For Acme Corp - ₹50,000"
              time="2 hours ago"
              color="text-blue-400"
              bg="bg-blue-400/10"
            />
            <ActivityItem
              icon={CheckCircle2}
              title="Payment received"
              desc="INV-0021 - ₹75,000"
              time="4 hours ago"
              color="text-green-400"
              bg="bg-green-400/10"
            />
            <ActivityItem
              icon={Package}
              title="Inventory updated"
              desc="50 units of Product A"
              time="1 day ago"
              color="text-indigo-400"
              bg="bg-indigo-400/10"
            />
            <ActivityItem
              icon={Wallet}
              title="Workflow executed"
              desc="Payment reminder sent to 5 clients"
              time="2 days ago"
              color="text-purple-400"
              bg="bg-purple-400/10"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatsCard({ icon: Icon, color, label, value, subValue }) {
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
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-xs text-gray-500">{subValue}</div>
    </div>
  );
}

function ActionCard({ icon: Icon, label, sub }) {
  return (
    <div className="p-6 rounded-2xl bg-[#0A0A0A] border border-white/5 hover:border-white/20 transition-all cursor-pointer group">
      <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-gray-400 mb-4 group-hover:text-white transition-colors">
        <Icon className="w-5 h-5" />
      </div>
      <h3 className="font-semibold text-lg mb-1 group-hover:text-white transition-colors">
        {label}
      </h3>
      <p className="text-sm text-gray-400">{sub}</p>
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
