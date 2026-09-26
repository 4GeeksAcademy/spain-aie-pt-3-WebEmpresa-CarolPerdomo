---
name: nexova-web-acceptance-audit
description: Audit the Nexova public website and candidate registration flow against the repository's current product and accessibility requirements, without modifying files.
---

# Nexova Web Acceptance Audit

## Objective

Verify whether the Nexova landing page and candidate-registration flow meet the applicable requirements in `CONTEXT.md` and `.github/copilot-instructions.md`, and report evidence-backed pass, fail, or unverified results. This skill audits only; it does not edit files or fix findings.

## Inputs

Required:

- Repository root path.

Optional:

- Website/form files to audit. If omitted, inspect root `index.html`, `application.html`, and `validation.js`.
- A public deployment URL for live responsive checks and PageSpeed Insights. Without a URL, mark public performance as unverified.
- Any relevant test or browser output already produced by the developer.

Use `CONTEXT.md` for exact form fields, choices, messages, and acceptance requirements. Use `.github/copilot-instructions.md` for the project-wide quality bar. If either source is unavailable, report that limitation rather than inventing requirements.

## Procedure

1. Inspect the landing page, form markup, validation behavior, and referenced assets. Do not infer behavior from copy alone.
2. Compare the implementation with the exact product requirements in `CONTEXT.md`.
3. Run only relevant, available checks. For a static root website, serve it with `npx serve .` and verify interactions in a browser when browser access is available. Run `npm run typecheck` only when TypeScript changes or utility behavior are in scope.
4. If a public URL is supplied, inspect mobile, tablet, and desktop layouts and run PageSpeed Insights. Otherwise mark these external checks unverified.
5. Return a concise checklist using **Pass**, **Fail**, or **Unverified** for every criterion, with a file/element/test as evidence. List the highest-priority gaps and the next check or fix. Do not report a check as passing without evidence.

## Acceptance Criteria

### Landing page and domain scope

- The page reflects Nexova's HR/talent services and matches the company facts in the context.
- The page has the required content sections and one logical `h1`; heading levels do not skip incoherently.
- Every meaningful image has contextual `alt` text.
- Organization JSON-LD parses as JSON and includes the required organization name, description, canonical URL, founding date, Valencia and Miami addresses, contact point, languages, and social links.
- Candidate registration is clearly intended for job seekers. Companies seeking services have a separate visible contact path rather than being routed into the candidate form.

### Candidate form

- All required fields appear with their specified HTML types, labels associated by `for`/`id`, required status, and exact option sets from `CONTEXT.md`.
- Validation enforces the specified full-name, email, international phone, country, experience range, sector, English level, availability, optional LinkedIn URL, comment-length, and data-policy rules.
- Invalid fields receive the specified useful error messages; invalid submission is prevented and dynamic errors/status are announced accessibly.
- The comments counter reflects the 500-character limit; successful simulated submission uses the required success message; reset clears values, errors, and status.

### Accessibility, responsiveness, and performance

- All interactive controls are keyboard reachable and have visible focus; labels, errors, and status messages are programmatically associated or announced where needed.
- Layout uses the required mobile-first Tailwind utility approach and remains usable at mobile, tablet, and desktop widths.
- The documented local command `npx serve .` starts the static site and both pages load correctly.
- If a public deployment URL is provided, PageSpeed Insights performance is at least 80. Otherwise report this criterion as **Unverified**, not Pass.

## Output Format

For each criterion, report one status (**Pass**, **Fail**, or **Unverified**) and concise evidence. Finish with the highest-priority findings and any checks that could not be run. Do not make code changes.
