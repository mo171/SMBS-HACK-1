import { create } from "zustand";
import { supabase } from "@/lib/supabase";

export const useProfileStore = create((set, get) => ({
  profile: null,
  loading: false,
  error: null,

  fetchProfile: async (userId) => {
    set({ loading: true, error: null });
    try {
      let query = supabase.from("profiles").select("*");

      if (userId) {
        query = query.eq("id", userId);
      } else {
        // Fallback to first profile if no ID provided (useful for development/testing)
        query = query.limit(1);
      }

      const { data, error } = await query.single();

      if (error) {
        if (error.code === "PGRST116") {
          // No record found, not necessarily an error if we need to create one
          set({ profile: null });
        } else {
          throw error;
        }
      } else {
        set({ profile: data });
      }
    } catch (error) {
      console.error("Error fetching profile:", error.message);
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },

  updateProfile: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const { data, error } = await supabase
        .from("profiles")
        .upsert({ id, ...updates })
        .select()
        .single();

      if (error) throw error;
      set({ profile: data });
      return data;
    } catch (error) {
      console.error("Error updating profile:", error.message);
      set({ error: error.message });
      throw error;
    } finally {
      set({ loading: false });
    }
  },
}));

export const useProfile = () => {
  const { profile, loading, error } = useProfileStore();
  return { profile, loading, error };
};

export const useProfileActions = () => {
  const { fetchProfile, updateProfile } = useProfileStore();
  return { fetchProfile, updateProfile };
};
