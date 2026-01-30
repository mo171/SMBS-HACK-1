import Link from "next/link";
import { MessageSquare, Twitter, Linkedin, Github, Mail } from "lucide-react";

export default function Footer() {
  const links = {
    product: ["Features", "Pricing", "Roadmap"],
    company: ["About", "Blog", "Careers"],
    legal: ["Privacy", "Terms", "Support"],
  };

  return (
    <footer className="border-t border-white/5 bg-[#0B0c15] pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-16">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="bg-[#6366f1] p-1.5 rounded-lg">
                <MessageSquare className="w-5 h-5 text-white fill-white" />
              </div>
              <span className="text-lg font-semibold tracking-tight">
                Bharat Biz
              </span>
            </Link>
            <p className="text-gray-400 text-sm max-w-xs">
              AI co-pilot for Indian businesses
            </p>
          </div>

          {/* Links Columns */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="font-semibold mb-4 capitalize">{category}</h4>
              <ul className="space-y-3">
                {items.map((item) => (
                  <li key={item}>
                    <Link
                      href="#"
                      className="text-gray-400 hover:text-white text-sm transition-colors"
                    >
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-500 text-sm">
            © 2026 Bharat Biz-Agent. All rights reserved. Built for India.
          </p>
          <div className="flex items-center gap-6 text-gray-400">
            <Mail className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
            <Twitter className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
            <Linkedin className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
            <Github className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
          </div>
        </div>
      </div>
    </footer>
  );
}
