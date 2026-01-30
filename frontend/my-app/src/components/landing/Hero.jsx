import Link from "next/link";
import { Zap, MessageCircle } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden flex flex-col items-center justify-center min-h-[80vh]">
      {/* Central Glow Effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] hero-glow pointer-events-none z-0" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center flex flex-col items-center">
        {/* Badge - Exact match */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#7047EB]/30 bg-[#7047EB]/10 text-[#A888FF] text-sm font-medium mb-10 shadow-[0_0_15px_rgba(112,71,235,0.1)]">
          <Zap className="w-3.5 h-3.5 fill-current" />
          <span className="tracking-wide">
            AI-Powered Workflow Intelligence
          </span>
        </div>

        {/* Headline - Exact match */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-8 text-white drop-shadow-2xl">
          Your AI Co-Pilot <br />
          <span className="text-[#a1a1aa]">for Business</span>
        </h1>

        {/* Subhead - Exact match */}
        <p className="text-xl md:text-2xl text-[#9496A1] max-w-3xl mx-auto mb-12 leading-relaxed font-light">
          Create invoices, chase payments, and run workflows —{" "}
          <br className="hidden md:block" />
          just by talking. Built for Indian businesses, powered by AI.
        </p>

        {/* CTA Buttons - Exact match */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-5 w-full sm:w-auto">
          {/* WhatsApp Button */}
          <Link
            href="/login?method=whatsapp"
            className="group w-full sm:w-auto flex items-center justify-center gap-3 bg-[#7047EB] hover:bg-[#5e3bc7] text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-[0_0_30px_rgba(112,71,235,0.3)] hover:shadow-[0_0_40px_rgba(112,71,235,0.5)] active:scale-[0.98]"
          >
            <MessageCircle className="w-6 h-6 fill-current" />
            Login with WhatsApp
          </Link>

          {/* Email Button */}
          <Link
            href="/login?method=email"
            className="w-full sm:w-auto flex items-center justify-center px-8 py-4 rounded-xl font-medium text-[#E2E8F0] bg-[#0E0E16] border border-[#2D2D3A] hover:border-[#7047EB]/50 hover:bg-[#1A1A24] transition-all text-lg"
          >
            Continue with Email
          </Link>
        </div>
      </div>
    </section>
  );
}
