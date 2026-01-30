"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useAuthActions } from "@/store/authStore";
import {
  LayoutDashboard,
  MessageSquare,
  Workflow,
  BarChart3,
  Settings,
  HelpCircle,
  LogOut,
  ChevronLeft,
  ChevronRight,
  MessageCircle,
  Zap,
} from "lucide-react";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: MessageSquare, label: "Workflow Chat", href: "/chat" },
  { icon: Workflow, label: "Workflows", href: "/workflows" },
  { icon: Zap, label: "Integrations", href: "/integrations" },
];

export function Sidebar({ isCollapsed, toggleSidebar }) {
  const pathname = usePathname();
  const router = useRouter();
  const { signOut } = useAuthActions();

  const handleLogout = async () => {
    await signOut();
    router.push("/");
  };

  return (
    <aside
      className={`min-h-screen bg-black border-r border-white/10 flex flex-col fixed left-0 top-0 bottom-0 z-50 transition-all duration-300 ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Logo Area */}
      <div
        className={`h-20 flex items-center ${isCollapsed ? "justify-center" : "justify-between px-6"}`}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center flex-shrink-0">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          {!isCollapsed && (
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 whitespace-nowrap">
              Bharat Biz
            </span>
          )}
        </div>

        {/* Toggle Button - Only show here if not collapsed, otherwise it might be better at the bottom or top center? 
            Design-wise, putting it in the header is standard or on the border. 
            Let's put it on the right side if open.
        */}
      </div>

      {/* Collapse Trigger - Floating on the border or inside */}
      <button
        onClick={toggleSidebar}
        className={`absolute -right-3 top-9 w-6 h-6 bg-[#5865F2] rounded-full text-white flex items-center justify-center hover:bg-[#4752C4] transition-all shadow-lg z-50 ${isCollapsed ? "rotate-180 translate-x-1" : ""}`}
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto overflow-x-hidden">
        {sidebarItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative ${
                isActive
                  ? "bg-[#5865F2] text-white shadow-lg shadow-indigo-500/20"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              } ${isCollapsed ? "justify-center" : ""}`}
              title={isCollapsed ? item.label : ""}
            >
              {/* Active Indicator for collapsed state */}
              {isActive && isCollapsed && (
                <div className="absolute left-0 w-1 h-8 bg-white rounded-r-full" />
              )}

              <Icon
                className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-white" : "text-gray-500 group-hover:text-white"}`}
              />

              {!isCollapsed && (
                <span className="font-medium text-sm whitespace-nowrap trancate">
                  {item.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-white/5">
        <button
          onClick={handleLogout}
          className={`flex items-center gap-3 px-3 py-3 w-full rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium ${isCollapsed ? "justify-center" : ""}`}
          title={isCollapsed ? "Logout" : ""}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
