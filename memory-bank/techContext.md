# Technical Context

## Verified Repository Setup

- The repository root contains a static Spanish website in `index.html`, a separate form page in `application.html`, and browser-side validation in `validation.js`.
- The root pages load Tailwind CSS from its CDN and use utility classes. There is no root frontend framework or bundler configured.
- The root `package.json` defines TypeScript 5.9 as a development dependency and the scripts `typecheck`, `build`, and `render:console`. There are no root runtime dependencies or workspace runner.
- `tsconfig.json` targets ES2020 with ESNext modules and strict type checking. The included TypeScript utilities live in `src/`; they are separate from the root HTML application.
- `packages/shared/` contains shared TypeScript type-package metadata but has no scripts.
- `uis/talent-pipeline-tracker/` is a separate Next.js application with its own package configuration. Do not assume it is the framework or runtime for the root website.
- `uis/website/` and `uis/backoffice/` are independent Next.js 16.3.4 App Router applications using React 19.2.8, TypeScript, Tailwind CSS 4, and ESLint. Each has its own `package.json`, lockfile, `app/` route/layout, and README. Their Next config pins the Turbopack root to that app directory because the monorepo contains multiple lockfiles.
- `uis/website/app/page.tsx` renders the Nexova public site using reusable components. `uis/backoffice/app/page.tsx` renders an internal executive dashboard; its company and department figures are static reference data from the briefing, not a live data connection.
- The current form is client-side only: submission is simulated in JavaScript; no backend persistence or email delivery is configured.
- No backend was added for these frontends. Any future API or integration service belongs under `/services`.

## Established Constraints

- Use semantic HTML5 and keep a logical heading hierarchy with one `h1` per page.
- The website and form are mobile-first and must work across small, medium, and large viewports.
- Use Tailwind utility classes for UI styling; do not add custom CSS when Tailwind can express the design.
- Use vanilla JavaScript for the root form behavior unless the project scope is explicitly changed.
- Associate every form control with a label, use suitable input types, provide accessible focus and error states, and announce dynamic status/errors appropriately.
- Include descriptive `alt` text for meaningful images and valid Schema.org organization metadata on the landing page.
- Spanish is the current base language. English or other locales are enhancements, not a reason to leave the base-language experience incomplete.
- Do not collect or commit real candidate personal data, credentials, or secrets. The current submit behavior is a simulation until an explicitly approved backend exists.

## Current Architecture Gaps

The checked-in root website currently presents a B2B company-services inquiry flow. The current milestone context instead requires a candidate job-seeker registration flow. The website's JSON-LD also currently uses a placeholder URL. See `progress.md` for the verified baseline and next steps.

## Useful Commands

- `npm run typecheck` — type-check the root TypeScript utilities.
- `npm run build` — compile the root TypeScript project to `dist/`.
- `npm run render:console` — run the example TypeScript utility report.
- `npx serve .` — serve the static root website locally, as documented in `README.md`.
- `npm run dev` from `uis/website/` — run the public Next.js site on port 3000.
- `npm run dev -- --port 3001` from `uis/backoffice/` — run the internal dashboard on port 3001.

No root test or lint script is currently configured. Do not report PageSpeed results unless a public URL has actually been tested.
