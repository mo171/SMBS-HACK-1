"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import {
  MessageSquare,
  Bot,
  Zap,
  CreditCard,
  ShieldAlert,
  Repeat,
  Copy,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import { toast } from "react-hot-toast";

export default function IntegrationsPage() {
  const [whatsappConnected, setWhatsappConnected] = useState(true);
  const [sandboxMode, setSandboxMode] = useState(true);

  // Feature flags / Skills state
  const [skills, setSkills] = useState({
    autoInvoice: true,
    paymentReminders: false,
    fraudDetection: false,
    smartRouting: false,
  });

  const toggleSkill = (key) => {
    setSkills((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-white min-h-screen">
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Integrations
        </h1>
        <p className="text-gray-400 mt-2">
          Activate your co-pilot and connect external services
        </p>
      </div>

      {/* WhatsApp Integration Card */}
      <Card className="bg-[#0A0A12] border-[#1E1E2D] p-6 overflow-hidden relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-green400/5 to-transparent pointer-events-none" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8 relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-green-500/10 flex items-center justify-center border border-green-500/20">
              <MessageSquare className="w-7 h-7 text-green-500" />
            </div>
            <div>
              <h2 className="text-xl font-semibold flex items-center gap-2">
                WhatsApp Integration
                {whatsappConnected && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-500 font-medium border border-green-500/20">
                    Active
                  </span>
                )}
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Connect WhatsApp to automate messaging and payments
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-[#11121A] p-2 pr-4 rounded-full border border-white/5">
            <div
              className={`w-3 h-3 rounded-full ${whatsappConnected ? "bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" : "bg-gray-500"}`}
            />
            <span className="text-sm font-medium text-gray-300">
              {whatsappConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>

        <div className="space-y-6 relative z-10">
          {/* Main Toggle */}
          <div className="flex items-center justify-between p-4 rounded-2xl bg-[#11121A] border border-white/5">
            <div>
              <h3 className="font-medium text-white">
                Enable WhatsApp Connection
              </h3>
              <p className="text-sm text-gray-400">
                Connect to Twilio Sandbox for testing or production
              </p>
            </div>
            <Switch
              checked={whatsappConnected}
              onCheckedChange={setWhatsappConnected}
              className="data-[state=checked]:bg-green-500"
            />
          </div>

          <p className="text-xs text-gray-500 font-mono">
            {/* Last synced: {new Date().toLocaleString()} */}
            {/* this synced data will come from backend jo state change me useeffect call hoga */}
            Last synced: 30/01/2026 15:23:45
          </p>
        </div>
      </Card>

      {/* Twilio Configuration */}
      {whatsappConnected && (
        <Card className="bg-[#0A0A12] border-[#1E1E2D] p-6 relative">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#5865F2] to-purple-600 opacity-50" />

          <div className="mb-6">
            <h2 className="text-xl font-semibold">
              Twilio Sandbox Configuration
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Configure your Twilio settings to enable message routing
            </p>
          </div>

          <div className="space-y-6">
            {/* Join Code */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                WhatsApp Sandbox Join Code
              </label>
              <p className="text-xs text-gray-500 mb-2">
                Use this code to join the Twilio WhatsApp Sandbox. Send this
                message to activate.
              </p>
              <div className="flex gap-2">
                <div className="flex-1 bg-[#11121A] border border-white/10 rounded-xl px-4 py-3 font-mono text-sm text-gray-300 flex items-center">
                  join material-red
                </div>
                <button
                  onClick={() => copyToClipboard("join glass-simple")}
                  className="p-3 bg-[#1E1E2D] hover:bg-[#2A2A3C] text-white rounded-xl border border-white/5 transition-colors"
                >
                  <Copy className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Webhook URL */}
            {/* <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-300">
                  Webhook URL
                </label>
                <button className="text-xs text-[#5865F2] hover:text-[#4752C4]">
                  Show Production Credentials
                </button>
              </div>
              <p className="text-xs text-gray-500 mb-2">
                Copy this URL and paste it into your Twilio Console under
                Messaging {">"} Settings {">"} Webhooks
              </p>
              <div className="flex gap-2">
                <div className="flex-1 bg-[#11121A] border border-white/10 rounded-xl px-4 py-3 font-mono text-sm text-gray-300 flex items-center overflow-x-auto">
                  <span className="whitespace-nowrap">
                    https://api.bharatbizagent.com/webhooks/twilio/message
                  </span>
                </div>
                <button
                  onClick={() =>
                    copyToClipboard(
                      "https://api.bharatbizagent.com/webhooks/twilio/message",
                    )
                  }
                  className="p-3 bg-[#1E1E2D] hover:bg-[#2A2A3C] text-white rounded-xl border border-white/5 transition-colors"
                >
                  <Copy className="w-5 h-5" />
                </button>
              </div>
            </div> */}
          </div>
        </Card>
      )}

      {/* AI Skills */}
      <div>
        <div className="mb-6">
          <h2 className="text-xl font-semibold">AI Skills</h2>
          <p className="text-gray-400 text-sm mt-1">
            Enable or disable specific features for your co-pilot
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: Auto Invoice */}
          <SkillCard
            icon={Zap}
            color="text-purple-400"
            bg="bg-purple-900/10"
            borderColor="border-purple-500/20"
            title="Auto-Invoice Creation"
            description="Automatically create invoices from voice commands and chat"
            enabled={skills.autoInvoice}
            onToggle={() => toggleSkill("autoInvoice")}
          />

          {/* Card 2: Payment Reminders */}
          <SkillCard
            icon={MessageSquare}
            color="text-blue-400"
            bg="bg-blue-900/10"
            borderColor="border-blue-500/20"
            title="Payment Reminders"
            description="Send automatic payment reminders via WhatsApp on schedule"
            enabled={skills.paymentReminders}
            onToggle={() => toggleSkill("paymentReminders")}
          />

          {/* Card 3: Fraud Detection */}
          <SkillCard
            icon={ShieldAlert}
            color="text-red-400"
            bg="bg-red-900/10"
            borderColor="border-red-500/20"
            title="Fraud Detection"
            description="AI-powered fraud detection for transactions"
            enabled={skills.fraudDetection}
            onToggle={() => toggleSkill("fraudDetection")}
          />

          {/* Card 4: Smart Routing */}
          <SkillCard
            icon={Repeat}
            color="text-indigo-400"
            bg="bg-indigo-900/10"
            borderColor="border-indigo-500/20"
            title="Smart Payment Routing"
            description="Automatically route payments to optimal channels"
            enabled={skills.smartRouting}
            onToggle={() => toggleSkill("smartRouting")}
          />
        </div>
      </div>

      {/* Coming Soon */}
      <div className="bg-gradient-to-r from-[#1E1E2D] to-[#11121A] rounded-3xl p-8 text-center border border-white/5 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-white/5 to-transparent pointer-events-none" />
        <h3 className="text-xl font-semibold text-white relative z-10">
          More Integrations Coming Soon
        </h3>
        <p className="text-gray-400 mt-2 relative z-10">
          We're working on Stripe, Razorpay, Google Workspace, and more
          integrations
        </p>
        <button className="mt-6 px-6 py-3 bg-[#5865F2] hover:bg-[#4752C4] text-white rounded-xl font-medium transition-colors relative z-10">
          Request an Integration
        </button>
      </div>
    </div>
  );
}

function SkillCard({
  icon: Icon,
  color,
  bg,
  borderColor,
  title,
  description,
  enabled,
  onToggle,
}) {
  return (
    <div
      className={`p-5 rounded-3xl border transition-all duration-300 ${enabled ? "bg-[#151520] border-[#5865F2]/30 shadow-lg shadow-[#5865F2]/5" : "bg-[#0A0A12] border-[#1E1E2D] opacity-80"}`}
    >
      <div className="flex justify-between items-start">
        <div
          className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center border ${borderColor}`}
        >
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <Switch
          checked={enabled}
          onCheckedChange={onToggle}
          className="data-[state=checked]:bg-[#5865F2]"
        />
      </div>

      <div className="mt-4">
        <h3 className="font-medium text-white text-lg">{title}</h3>
        <p className="text-sm text-gray-400 mt-1 leading-relaxed">
          {description}
        </p>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span
          className={`text-xs font-medium ${enabled ? "text-green-400" : "text-gray-600"}`}
        >
          {enabled ? "✓ Enabled" : "Disabled"}
        </span>
      </div>
    </div>
  );
}
