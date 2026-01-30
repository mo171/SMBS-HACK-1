"use client";

import Link from "next/link";
import {
  MessageSquare,
  ChevronDown,
  LogOut,
  LayoutDashboard,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";

export default function Navbar() {
  const { isAuthenticated, signOut } = useAuthStore();

  return (
    <nav className="fixed top-0 w-full z-50 glass-nav">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="bg-[#7047EB] p-2 rounded-xl shadow-[0_0_15px_rgba(112,71,235,0.4)] transition-all group-hover:scale-105">
              <MessageSquare className="w-6 h-6 text-white fill-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white group-hover:text-[#A888FF] transition-colors">
              Bharat Biz-Agent
            </span>
          </Link>

          {/* Right Actions */}
          <div className="flex items-center gap-6">
            {/* Lang Switcher */}
            <button className="flex items-center gap-1.5 text-sm font-medium text-[#9496A1] hover:text-white transition-colors">
              EN <ChevronDown className="w-4 h-4" />
            </button>

            {isAuthenticated ? (
              <>
                {/* Dashboard Link */}
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-[#E2E8F0] border border-[#2D2D3A] hover:bg-white/5 hover:border-white/20 transition-all"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>

                {/* Logout Button */}
                <button
                  onClick={() => signOut()}
                  className="flex items-center gap-2 bg-[#7047EB] hover:bg-[#5e3bc7] text-white text-sm font-semibold px-6 py-2.5 rounded-lg transition-all shadow-[0_0_20px_rgba(112,71,235,0.3)] hover:shadow-[0_0_25px_rgba(112,71,235,0.5)] active:scale-[0.98]"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </>
            ) : (
              <>
                {/* Login Link */}
                <Link
                  href="/login"
                  className="px-5 py-2.5 rounded-lg text-sm font-medium text-[#E2E8F0] border border-[#2D2D3A] hover:bg-white/5 hover:border-white/20 transition-all"
                >
                  Login
                </Link>

                {/* Get Started Button */}
                <Link
                  href="/signup"
                  className="bg-[#7047EB] hover:bg-[#5e3bc7] text-white text-sm font-semibold px-6 py-2.5 rounded-lg transition-all shadow-[0_0_20px_rgba(112,71,235,0.3)] hover:shadow-[0_0_25px_rgba(112,71,235,0.5)] active:scale-[0.98]"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
