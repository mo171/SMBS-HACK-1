import React from "react";
import {
  FileText,
  MessageSquare,
  FileJson,
  Users,
  Calendar,
  Zap,
  MoreHorizontal,
} from "lucide-react";

const WorkflowCanvas = () => {
  return (
    <section className="relative w-full py-20 px-4 flex justify-center items-center overflow-hidden">
      {/* Glow effect behind the container */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-primary/5 blur-[100px] rounded-full pointer-events-none" />

      {/* Browser Window Container */}
      <div className="relative w-full max-w-5xl bg-black/20 backdrop-blur-xl border border-white/5 rounded-xl shadow-2xl overflow-hidden z-10 box-border">
        {/* Window Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/5">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
            <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
            <div className="w-3 h-3 rounded-full bg-[#28c840]" />
          </div>
          <div className="text-xs font-mono text-white/20">
            bharat_workflow.canvas
          </div>
          <div className="w-10" /> {/* Spacer for centering */}
        </div>

        {/* Canvas Area */}
        <div className="p-8 md:p-12 grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {/* Removed Background Dots Grid */}

          {/* Card 1: Invoice Generator (Active) */}
          <div className="group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-[#8b5cf6] to-[#d946ef] rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
            <div className="relative bg-[#0B0D15] h-full p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-[#8b5cf6] shadow-[0_0_30px_rgba(139,92,246,0.3)]">
              <div className="w-12 h-12 rounded-lg bg-[#8b5cf6]/20 flex items-center justify-center text-[#8b5cf6] group-hover:scale-110 transition-transform shadow-[0_0_20px_rgba(139,92,246,0.4)]">
                <FileText size={24} />
              </div>
              <h3 className="text-white font-medium tracking-wide text-sm">
                Invoice Generator
              </h3>
            </div>
          </div>

          {/* Card 2: Payment Chaser */}
          <div className="bg-[#05060A]/80 backdrop-blur-sm p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-white/5 hover:border-[#8b5cf6]/50 transition-all cursor-default group relative overflow-hidden">
            <div className="absolute inset-0 bg-[#8b5cf6]/5 pointer-events-none" />
            <div className="relative z-10 w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center text-white/20 group-hover:text-white/40 transition-colors">
              <MessageSquare size={24} />
            </div>
            <h3 className="relative z-10 text-white/30 font-medium tracking-wide text-sm group-hover:text-white/50 transition-colors">
              Payment Chaser
            </h3>
          </div>

          {/* Card 3: Document Builder */}
          <div className="bg-[#05060A]/80 backdrop-blur-sm p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-white/5 hover:border-[#8b5cf6]/50 transition-all cursor-default group relative overflow-hidden">
            <div className="absolute inset-0 bg-[#8b5cf6]/5 pointer-events-none" />
            <div className="relative z-10 w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center text-primary/40 group-hover:text-primary/60 transition-colors">
              <FileJson size={24} />
            </div>
            <h3 className="relative z-10 text-white/30 font-medium tracking-wide text-sm group-hover:text-white/50 transition-colors">
              Document Builder
            </h3>
          </div>

          {/* Card 4: Customer Intel */}
          <div className="bg-[#05060A]/80 backdrop-blur-sm p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-white/5 hover:border-[#8b5cf6]/50 transition-all cursor-default group relative overflow-hidden">
            <div className="absolute inset-0 bg-[#8b5cf6]/5 pointer-events-none" />
            <div className="relative z-10 w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center text-white/20 group-hover:text-white/40 transition-colors">
              <Users size={24} />
            </div>
            <h3 className="relative z-10 text-white/30 font-medium tracking-wide text-sm group-hover:text-white/50 transition-colors">
              Customer Intel
            </h3>
          </div>

          {/* Card 5: Payment Scheduler */}
          <div className="bg-[#05060A]/80 backdrop-blur-sm p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-white/5 hover:border-[#8b5cf6]/50 transition-all cursor-default group relative overflow-hidden">
            <div className="absolute inset-0 bg-[#8b5cf6]/5 pointer-events-none" />
            <div className="relative z-10 w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center text-primary/40 group-hover:text-primary/60 transition-colors">
              <Calendar size={24} />
            </div>
            <h3 className="relative z-10 text-white/30 font-medium tracking-wide text-sm group-hover:text-white/50 transition-colors">
              Payment Scheduler
            </h3>
          </div>

          {/* Card 6: Workflow Trigger */}
          <div className="bg-[#05060A]/80 backdrop-blur-sm p-6 rounded-xl flex flex-col items-center justify-center gap-4 border border-white/5 hover:border-[#8b5cf6]/50 transition-all cursor-default group relative overflow-hidden">
            <div className="absolute inset-0 bg-[#8b5cf6]/5 pointer-events-none" />
            <div className="relative z-10 w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center text-accent/40 group-hover:text-accent/60 transition-colors">
              <Zap size={24} />
            </div>
            <h3 className="relative z-10 text-white/30 font-medium tracking-wide text-sm group-hover:text-white/50 transition-colors">
              Workflow Trigger
            </h3>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WorkflowCanvas;
