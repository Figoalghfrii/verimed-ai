import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  as?: "div" | "section" | "article";
  ariaLabelledBy?: string;
}

export function Card({
  children,
  className = "",
  as: Component = "div",
  ariaLabelledBy,
}: CardProps) {
  return (
    <Component
      aria-labelledby={ariaLabelledBy}
      className={`rounded-3xl border border-slate-200/75 bg-white p-6 shadow-bento ${className}`}
    >
      {children}
    </Component>
  );
}
