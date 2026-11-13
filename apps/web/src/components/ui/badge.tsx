import React from "react";

type BadgeVariant = "neutral" | "success" | "danger" | "warning" | "info";

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  neutral: "bg-slate-100 text-slate-800 border-slate-300",
  success: "bg-emerald-50 text-emerald-900 border-emerald-300",
  danger: "bg-rose-50 text-rose-900 border-rose-300",
  warning: "bg-amber-50 text-amber-900 border-amber-300",
  info: "bg-teal-50 text-teal-900 border-teal-300",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export function Badge({
  children,
  variant = "neutral",
  className = "",
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-semibold ${VARIANT_CLASSES[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
