"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ExpandableCardProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  /** Content shown in the collapsed card */
  preview?: React.ReactNode;
  className?: string;
  classNameExpanded?: string;
}

export function ExpandableCard({
  title,
  description,
  children,
  preview,
  className,
  classNameExpanded,
}: ExpandableCardProps) {
  const [active, setActive] = React.useState(false);
  const cardRef = React.useRef<HTMLDivElement>(null);
  const id = React.useId();

  React.useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setActive(false);
    };
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (cardRef.current && !cardRef.current.contains(event.target as Node)) {
        setActive(false);
      }
    };

    if (active) {
      window.addEventListener("keydown", onKeyDown);
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("touchstart", handleClickOutside);
      // Prevent body scroll while expanded
      document.body.style.overflow = "hidden";
    }

    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
      document.body.style.overflow = "";
    };
  }, [active]);

  return (
    <>
      {/* Backdrop */}
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-10 bg-white/60 backdrop-blur-md"
          />
        )}
      </AnimatePresence>

      {/* Expanded overlay */}
      <AnimatePresence>
        {active && (
          <div className="fixed inset-0 z-[100] grid place-items-center p-4 sm:p-8">
            <motion.div
              layoutId={`card-${title}-${id}`}
              ref={cardRef}
              className={cn(
                "w-full max-w-[850px] max-h-[85vh] flex flex-col overflow-auto [scrollbar-width:none] [-ms-overflow-style:none] [-webkit-overflow-scrolling:touch]",
                "rounded-2xl border border-border/80 bg-white shadow-[0_24px_80px_rgba(0,0,0,0.08)]",
                classNameExpanded,
              )}
            >
              {/* Header */}
              <div className="flex items-start justify-between border-b border-border/60 p-6">
                <div>
                  {description && (
                    <motion.p
                      layoutId={`desc-${title}-${id}`}
                      className="text-xs uppercase tracking-widest text-muted-foreground"
                    >
                      {description}
                    </motion.p>
                  )}
                  <motion.h3
                    layoutId={`title-${title}-${id}`}
                    className="font-body-mix text-xl font-semibold tracking-tight"
                  >
                    {title}
                  </motion.h3>
                </div>
                <motion.button
                  aria-label="Close card"
                  layoutId={`btn-${title}-${id}`}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border/80 text-muted-foreground transition-colors hover:border-foreground hover:text-foreground focus:outline-none"
                  onClick={() => setActive(false)}
                >
                  <motion.div
                    animate={{ rotate: active ? 45 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M5 12h14" />
                      <path d="M12 5v14" />
                    </svg>
                  </motion.div>
                </motion.button>
              </div>

              {/* Expanded body */}
              <motion.div
                layout
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 p-6 text-sm leading-relaxed text-muted-foreground"
              >
                {children}
              </motion.div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Collapsed card — hover lift */}
      <motion.div
        role="button"
        tabIndex={0}
        aria-labelledby={`card-title-${id}`}
        layoutId={`card-${title}-${id}`}
        onClick={() => setActive(true)}
        onKeyDown={(e) => { if (e.key === "Enter") setActive(true); }}
        className={cn(
          "group cursor-pointer rounded-2xl border border-border/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm",
          "transition-all duration-200 ease-out hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)]",
          className,
        )}
      >
        {/* Card header */}
        <div className="flex items-start justify-between">
          <div>
            {description && (
              <motion.p
                layoutId={`desc-${title}-${id}`}
                className="text-xs uppercase tracking-widest text-muted-foreground"
              >
                {description}
              </motion.p>
            )}
            <motion.h3
              layoutId={`title-${title}-${id}`}
              className="font-body-mix text-sm font-semibold tracking-tight"
            >
              {title}
            </motion.h3>
          </div>
          <motion.button
            aria-label="Expand"
            layoutId={`btn-${title}-${id}`}
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-border/80 text-muted-foreground/50 transition-colors group-hover:border-foreground/30 group-hover:text-foreground/60"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="M12 5v14" />
            </svg>
          </motion.button>
        </div>

        {/* Preview content */}
        {preview && <div className="mt-3">{preview}</div>}

        {/* Click hint */}
        <p className="mt-3 text-center text-[10px] tracking-wide text-muted-foreground/40 transition-colors group-hover:text-muted-foreground/70">
          click for more info
        </p>
      </motion.div>
    </>
  );
}
