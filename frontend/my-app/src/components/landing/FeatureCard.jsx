import { MessageSquare, Smartphone, Zap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const icons = {
  chat: MessageSquare,
  mobile: Smartphone,
  zap: Zap,
};

export default function FeatureCard({ icon, title, subtitle, features }) {
  const Icon = icons[icon] || MessageSquare;

  return (
    <Card className="hover:border-[#7047EB]/50 transition-all duration-300 group hover:shadow-[0_0_40px_rgba(112,71,235,0.1)] h-full flex flex-col p-2">
      <CardHeader className="pb-4">
        {/* Icon Box */}
        <div className="w-14 h-14 bg-[#7047EB] rounded-2xl flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(112,71,235,0.3)] group-hover:scale-110 transition-transform duration-300">
          <Icon className="w-7 h-7 text-white" strokeWidth={2} />
        </div>

        <CardTitle className="text-2xl font-bold mb-3 text-white">
          {title}
        </CardTitle>
        <p className="text-[#9496A1] text-base border-b border-[#1E1E2D] pb-6 leading-relaxed">
          {subtitle}
        </p>
      </CardHeader>

      <CardContent className="mt-auto">
        <ul className="space-y-4">
          {features.map((feature, idx) => (
            <li
              key={idx}
              className="flex items-center gap-3 text-[15px] text-[#C4C5CD] group-hover:text-white transition-colors"
            >
              <span className="w-2 h-2 rounded-full bg-[#7047EB] shadow-[0_0_8px_#7047EB]" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
