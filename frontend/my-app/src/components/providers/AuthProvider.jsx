"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";

export function AuthProvider({ children }) {
  const initializeAuth = useAuthStore((state) => state.initializeAuth);

  useEffect(() => {
    // Initialize auth listener on mount
    const cleanup = initializeAuth();
    return () => {
      // Cleanup subscription on unmount if needed
      // The store's initializeAuth returns a cleanup function
      if (cleanup && typeof cleanup === "function") cleanup();
    };
  }, [initializeAuth]);

  return <>{children}</>;
}
