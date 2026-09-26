# Development Progress

## Baseline Status

**Milestone:** Public website and talent registration  
**Status:** The public-site and backoffice Next.js apps are initialized and build/lint clean. The candidate-registration requirements are still incomplete.

## Implemented

- `index.html` contains a Spanish corporate landing page with service descriptions, responsive Tailwind utility classes, images with alt text, and Organization JSON-LD.
- `application.html` contains a company-services diagnostic form.
- `validation.js` validates fields in the company form, exposes field/status messages, supports reset, and simulates successful submission in the browser.
- Root TypeScript collection/search/transformation/validation utilities and npm typecheck/build scripts are present under `src/`.
- `uis/website/` is an independent Next.js public website with a responsive corporate homepage, reusable header/service/section/footer components, organization JSON-LD, company services, and contact details.
- `uis/backoffice/` is a separate Next.js app and layout with visible company KPIs, department signals, department filtering, text search, and a computed support-SLA gap. It labels its figures as briefing reference data, not live metrics.
- Both frontend apps have per-app READMEs and run/build/lint scripts. No backend service was introduced; future APIs belong under `/services`.

## Verification

- `npm run build --prefix uis/website` — passed.
- `npm run build --prefix uis/backoffice` — passed.
- `npm run lint --prefix uis/website` — passed.
- `npm run lint --prefix uis/backoffice` — passed.
- Local HTTP smoke tests for both `/` routes — returned 200 and contained the expected Nexova content.
- Website Organization JSON-LD — parsed successfully; canonical URL and both office addresses were present.

## Known Gaps Against the Current Context

- The form collects company and service-request details; it does not collect the required candidate profile fields from `CONTEXT.md`.
- The original root landing page CTA leads to that company-services form. The new `uis/website/` has a separate talent contact anchor, but currently uses email rather than a structured candidate form.
- The current simulated success copy and validation rules belong to the company inquiry flow, not the candidate flow.
- The original root landing page JSON-LD has a placeholder URL (`https://example.com`). The new `uis/website/` includes the Nexova organization fields from the context.
- Backoffice metrics are static briefing facts; there is no API or live data connection.
- A public deployment and PageSpeed Insights result have not been verified. Do not claim the performance acceptance threshold is met.

## Next Steps

1. Add a structured candidate-registration route to `uis/website/` with every field, option, required flag, validation rule/message, success state, and reset behavior from `CONTEXT.md`; retain a separate company-services contact path.
2. Check semantic structure, keyboard access, focus/error/status announcements, and responsive layouts at mobile, tablet, and desktop widths for both new apps.
3. Decide whether and when to connect the backoffice to a backend; if implemented, place the service under `/services` and replace static reference values only with verified API data.
4. After a public deployment exists, measure PageSpeed Insights and record the result. A public deployment and performance score are not yet verified.

## Update Policy

Update this file after completing a meaningful implementation or verification step. Record only verified outcomes; keep unfinished or externally dependent checks explicitly marked as pending.
