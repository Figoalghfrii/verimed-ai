"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Ringkasan",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        className="h-4 w-4"
      >
        <rect
          x="3"
          y="3"
          width="6"
          height="6"
          rx="1.5"
          stroke="currentColor"
          strokeWidth="1.6"
        />
        <rect
          x="11"
          y="3"
          width="6"
          height="6"
          rx="1.5"
          stroke="currentColor"
          strokeWidth="1.6"
        />
        <rect
          x="3"
          y="11"
          width="6"
          height="6"
          rx="1.5"
          stroke="currentColor"
          strokeWidth="1.6"
        />
        <rect
          x="11"
          y="11"
          width="6"
          height="6"
          rx="1.5"
          stroke="currentColor"
          strokeWidth="1.6"
        />
      </svg>
    ),
  },
  {
    href: "/verify",
    label: "Verifikasi Klaim",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        className="h-4 w-4"
      >
        <path
          d="M10 2.5L4 5v4.5c0 4.1 2.6 7.4 6 8.5 3.4-1.1 6-4.4 6-8.5V5l-6-2.5z"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <path
          d="M7.5 10l1.7 1.7 3.5-3.5"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    href: "/corpus",
    label: "Korpus Bukti",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        className="h-4 w-4"
      >
        <path
          d="M3.5 5.5A2 2 0 015.5 3.5h9a2 2 0 012 2v9a2 2 0 01-2 2h-9a2 2 0 01-2-2v-9z"
          stroke="currentColor"
          strokeWidth="1.6"
        />
        <path
          d="M6.5 7.5h7M6.5 10.5h7M6.5 13.5h4.5"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    href: "/about",
    label: "Metodologi",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        className="h-4 w-4"
      >
        <path
          d="M4 5.5A2.5 2.5 0 016.5 3H16v13H6.5A2.5 2.5 0 004 18V5.5z"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <path
          d="M7.5 7h5M7.5 10h5"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
];

export function TopNavbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-30 bg-canvas/85 backdrop-blur-md print:hidden">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-sm transition group-hover:bg-brand-700">
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              className="h-5 w-5"
            >
              <path
                d="M4 12h3.5l2-5 4 10 2.5-5H20"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className="text-xl font-bold tracking-tight text-slate-900">
            VeriMed
          </span>
        </Link>

        <nav
          aria-label="Navigasi Utama"
          className="flex flex-wrap items-center gap-1 rounded-full border border-slate-200/80 bg-white p-1.5 shadow-pill"
        >
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-600 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-100/80 hover:text-slate-900"
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2.5">
          <Link
            href="/verify"
            aria-label="Mulai periksa klaim kesehatan"
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200/80 bg-white text-slate-600 shadow-pill transition hover:border-brand-200 hover:text-brand-600"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 20 20"
              fill="none"
              className="h-4 w-4"
            >
              <circle
                cx="9"
                cy="9"
                r="5.5"
                stroke="currentColor"
                strokeWidth="1.7"
              />
              <path
                d="M13.5 13.5L17 17"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
              />
            </svg>
          </Link>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-200/80 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-pill">
            <span className="h-2 w-2 rounded-full bg-brand-600" />
            SDG 3 • ID
          </span>
        </div>
      </div>
    </header>
  );
}
