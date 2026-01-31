"use client";

import { useState, useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { useProfile, useProfileActions } from "@/store/profileStore";
import { useAuthStore } from "@/store/authStore";
import {
  Building2,
  User,
  Hash,
  Briefcase,
  Globe,
  MessageCircle,
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  Check,
  Loader2,
  CheckCircle2,
  Send,
} from "lucide-react";
import { toast } from "sonner";

const industryOptions = [
  { label: "Retail", value: "retail" },
  { label: "Manufacturing", value: "manufacturing" },
  { label: "Services", value: "services" },
  { label: "Other", value: "other" },
];

const languageOptions = [
  { label: "English", value: "English" },
  { label: "हिंदी", value: "Hindi" },
  { label: "मराठी", value: "Marathi" },
  { label: "தமிழ்", value: "Tamil" },
];

function CustomSelect({ value, onChange, options, placeholder }) {
  const [isOpen, setIsOpen] = useState(false);
  const selectedOption = options.find((opt) => opt.value === value);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-[#5865F2] transition-all flex items-center justify-between group"
      >
        <span className={selectedOption ? "text-white" : "text-gray-400"}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 right-0 mt-2 bg-[#0A0A0A] border border-white/10 rounded-2xl overflow-hidden z-20 shadow-2xl animate-in fade-in zoom-in duration-200">
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left flex items-center justify-between transition-colors ${
                  value === option.value
                    ? "bg-[#5865F2] text-white"
                    : "text-gray-300 hover:bg-white/5"
                }`}
              >
                <span className="text-sm font-medium">{option.label}</span>
                {value === option.value && <Check className="w-4 h-4" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function ProfilePage() {
  const [step, setStep] = useState(1);
  const { profile, loading } = useProfile();
  const { fetchProfile, updateProfile } = useProfileActions();
  const { user } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm({
    defaultValues: {
      business_name: "",
      owner_name: "",
      gst_number: "",
      industry: "",
      preferred_language: "English",
      whatsapp_number: "",
    },
  });

  useEffect(() => {
    // Fetch profile on mount
    fetchProfile(user?.id);
  }, [user?.id, fetchProfile]);

  useEffect(() => {
    if (profile) {
      reset({
        business_name: profile.business_name || "",
        owner_name: profile.owner_name || "",
        gst_number: profile.gst_number || "",
        industry: profile.industry || "",
        preferred_language: profile.preferred_language || "English",
        whatsapp_number: profile.whatsapp_number || "",
      });
    }
  }, [profile, reset]);

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      // If we have a profile ID, use it, otherwise let it generate a new one (or use user.id if linked)
      const profileId = profile?.id || user?.id || crypto.randomUUID();
      await updateProfile(profileId, data);
      toast.success("Profile updated successfully!");
      if (step < 2) setStep(step + 1);
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 2));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center gap-4 mb-8">
      {[1, 2].map((i) => (
        <div key={i} className="flex items-center">
          <div
            className={`w-36 h-1 rounded-full transition-all duration-300 ${
              step >= i ? "bg-[#5865F2]" : "bg-white/10"
            }`}
          />
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#11121A] text-white p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">Bharat Biz-Agent</span>
          </div>
          <h1 className="text-4xl font-bold mb-2">
            Let's Set Up Your Business
          </h1>
          <p className="text-gray-400">Step {step} of 2</p>
        </div>

        {renderStepIndicator()}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="bg-[#1A1B23] border border-white/5 rounded-3xl p-8 shadow-2xl">
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold mb-1">
                    Business Information
                  </h2>
                  <p className="text-sm text-gray-400 mb-6">
                    Tell us about your business
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      Business Name
                    </label>
                    <div className="relative">
                      <input
                        {...register("business_name", {
                          required: "Business name is required",
                        })}
                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-[#5865F2] transition-all"
                        placeholder="Your business name"
                      />
                    </div>
                    {errors.business_name && (
                      <p className="text-red-500 text-xs">
                        {errors.business_name.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      Owner Name
                    </label>
                    <div className="relative">
                      <input
                        {...register("owner_name", {
                          required: "Owner name is required",
                        })}
                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-[#5865F2] transition-all"
                        placeholder="Your full name"
                      />
                    </div>
                    {errors.owner_name && (
                      <p className="text-red-500 text-xs">
                        {errors.owner_name.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      GST Number (Optional)
                    </label>
                    <div className="relative">
                      <input
                        {...register("gst_number")}
                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-[#5865F2] transition-all"
                        placeholder="15-character GST number"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      Industry
                    </label>
                    <Controller
                      name="industry"
                      control={control}
                      render={({ field }) => (
                        <CustomSelect
                          value={field.value}
                          onChange={field.onChange}
                          options={industryOptions}
                          placeholder="Select your industry"
                        />
                      )}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      Preferred Language
                    </label>
                    <Controller
                      name="preferred_language"
                      control={control}
                      render={({ field }) => (
                        <CustomSelect
                          value={field.value}
                          onChange={field.onChange}
                          options={languageOptions}
                          placeholder="Select language"
                        />
                      )}
                    />
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold mb-1">
                    WhatsApp Configuration
                  </h2>
                  <p className="text-sm text-gray-400 mb-6">
                    Connect your WhatsApp for invoices & reminders
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">
                      WhatsApp Number
                    </label>
                    <div className="flex gap-2">
                      <div className="bg-black/40 border border-white/10 rounded-xl px-3 py-3 text-gray-500 text-sm flex items-center">
                        +91
                      </div>
                      <input
                        {...register("whatsapp_number", {
                          required: "WhatsApp number is required",
                          pattern: {
                            value: /^[0-9]{10}$/,
                            message:
                              "Invalid WhatsApp number (10 digits expected)",
                          },
                        })}
                        className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-[#5865F2] transition-all"
                        placeholder="10-digit number"
                      />
                    </div>
                    {errors.whatsapp_number && (
                      <p className="text-red-500 text-xs">
                        {errors.whatsapp_number.message}
                      </p>
                    )}
                  </div>

                  <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/10 text-sm text-gray-400">
                    We'll send invoices & payment reminders on WhatsApp. You can
                    manage these anytime in Settings.
                  </div>

                  <button
                    type="button"
                    className="w-full py-3 border border-white/10 rounded-xl hover:bg-white/5 transition-all flex items-center justify-center gap-2 text-sm font-medium"
                  >
                    Send Test Message
                  </button>

                  <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/10 text-sm text-green-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Test message sent to your WhatsApp
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-4">
            {step > 1 && (
              <button
                type="button"
                onClick={prevStep}
                className="flex-1 py-4 bg-white/5 border border-white/10 rounded-xl font-semibold hover:bg-white/10 transition-all flex items-center justify-center gap-2"
              >
                <ChevronLeft className="w-5 h-5" />
                Back
              </button>
            )}
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-[2] py-4 bg-[#5865F2] rounded-xl font-semibold hover:bg-[#4752C4] transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  {step === 2 ? "Final Submit" : "Next"}
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
