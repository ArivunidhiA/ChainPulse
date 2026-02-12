"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";

type BackgroundProps = {
  children?: React.ReactNode;
  className?: string;
};

export const Component = ({ children, className }: BackgroundProps) => {
  const [count, setCount] = useState(0);
  void count;
  void setCount;

  return (
    <div className={cn("min-h-screen w-full relative bg-white", className)}>
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle at center, #FFF991 0%, transparent 70%)
          `,
          opacity: 0.6,
          mixBlendMode: "multiply",
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};
