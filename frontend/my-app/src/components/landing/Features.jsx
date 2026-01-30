import FeatureCard from "./FeatureCard";

export default function Features() {
  const features = [
    {
      icon: "chat",
      title: "Chat Your Way to Invoices",
      subtitle: "Voice → Draft → Confirm → Send",
      items: [
        "Voice to text",
        "Auto-drafting",
        "One-tap approval",
        "Instant WhatsApp",
      ],
    },
    {
      icon: "mobile",
      title: "Chase Payments on WhatsApp",
      subtitle: "Automated reminders, real-time confirmation",
      items: [
        "Smart reminders",
        "Status tracking",
        "Payment links",
        "Receipt delivery",
      ],
    },
    {
      icon: "zap",
      title: "Run Your Business, Your Way",
      subtitle: "Offline-friendly, multilingual, India-first",
      items: ["Offline mode", "Multi-language", "GST-ready", "Local payments"],
    },
  ];

  return (
    <section className="py-20 lg:py-32 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Why Bharat Biz-Agent?
          </h2>
          <p className="text-gray-400 text-lg">
            Designed from the ground up for Indian small businesses
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, idx) => (
            <FeatureCard
              key={idx}
              icon={feature.icon}
              title={feature.title}
              subtitle={feature.subtitle}
              features={feature.items}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
