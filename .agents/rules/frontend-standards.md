---
trigger: always_on
description: Enforces Next.js App Router, TypeScript, Tailwind CSS, accessibility, and localization standards for apps/web.
---

# Frontend Coding Standards (`apps/web`)

1. **Architecture & Organization**:
   - Use Next.js App Router (`src/app/`) for routing and layout composition.
   - Organize domain logic into feature modules under `src/features/<feature-name>/` (`components/`, `api/`, `schemas/`, `types/`).
   - Keep reusable UI primitives in `src/components/ui/`.
2. **Type Safety & Validation**:
   - Enable TypeScript `strict: true`. Avoid `any`; use explicit interfaces or Zod-inferred types (`z.infer<typeof Schema>`).
   - Validate external API responses and user form inputs using Zod.
   - Use TanStack Query for client-side asynchronous data fetching, caching, and loading/error state management.
3. **Language & Accessibility**:
   - Write all source code, component names, variables, and comments in **English**.
   - Present user-facing UI labels, helper text, and explanations in clear, accessible **Bahasa Indonesia**.
   - Use semantic HTML (`main`, `section`, `article`, `nav`, `button`), explicit ARIA labels where needed, and high-contrast status indicators.
4. **Security**:
   - Only expose non-sensitive configuration prefixed with `NEXT_PUBLIC_`.
   - Sanitize or safely render any dynamic text as plain text nodes (never use `dangerouslySetInnerHTML` with untrusted content).
