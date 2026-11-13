import React from "react";
import { EmergencyGuidance } from "../schemas/verification-schema";

export function EmergencyAlert({ guidance }: { guidance: EmergencyGuidance }) {
  return (
    <section
      role="alert"
      aria-live="assertive"
      className="rounded-3xl border-2 border-rose-500 bg-rose-50 p-6 text-rose-950 shadow-bento sm:p-7"
    >
      <div className="flex items-start gap-4">
        <span
          aria-hidden="true"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-rose-600 text-base font-bold text-white shadow-sm"
        >
          !
        </span>
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-rose-950">
            {guidance.headline}
          </h2>
          <p className="text-sm leading-relaxed text-rose-900">
            {guidance.message}
          </p>
          <div className="rounded-2xl border border-rose-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-rose-800">
              Kontak Darurat Medis Indonesia
            </p>
            <ul className="mt-2 list-disc space-y-1.5 pl-5 text-sm font-semibold text-rose-950">
              {guidance.emergency_contacts.map((contact) => (
                <li key={contact}>{contact}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
