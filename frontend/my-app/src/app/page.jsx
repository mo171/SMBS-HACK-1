import WorkflowCanvas from "@/components/landing/WorkflowCanvas";
import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import Footer from "@/components/landing/Footer";
import { ParticleBackground } from "@/components/ui/particle-backgournd";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background to-background">
      {/* Particle background effect */}
      <ParticleBackground />

      {/* Animated background particles */}
      <div className="fixed inset-0 pointer-events-none z-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-primary/3 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent/3 rounded-full blur-3xl animate-pulse delay-700" />
      </div>

      {/* Content */}
      <div className="relative z-20">
        <Navbar />
        <Hero />
        <WorkflowCanvas />
        <Features />
        <Footer />
      </div>
    </main>
  );
}
