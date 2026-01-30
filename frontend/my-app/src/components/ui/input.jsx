import * as React from "react";
import { cn } from "@/lib/utils";

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-12 w-full rounded-xl border border-[#2D2D3A] bg-[#0A0A12] px-3 py-2 text-sm ring-offset-[#0B0c15] file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#7047EB] focus-visible:border-[#7047EB]/50 disabled:cursor-not-allowed disabled:opacity-50 text-white placeholder:text-[#52525b] transition-all",
        className,
      )}
      ref={ref}
      {...props}
    />
  );
});
Input.displayName = "Input";

export { Input };
