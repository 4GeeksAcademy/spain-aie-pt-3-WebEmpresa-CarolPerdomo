# Nexova Development Rule

**Scope: Always active.** Apply this rule to all tasks and files in this repository.

- Use `CONTEXT.md` and `CONTEXT-nexova-briefing.es.md` as the product/domain sources of truth. Do not invent business facts or present planned capabilities as implemented.
- Keep the job-seeker registration journey distinct from company inquiries. The candidate form is for professionals; provide a separate visible contact path for companies seeking Nexova services.
- For the root website, preserve semantic HTML, accessible labels and feedback, mobile-first behavior, and Tailwind utility styling. Use vanilla JavaScript for browser form behavior unless the developer approves a stack change.
- Treat the root static website, TypeScript utilities, and nested applications as separate implementation surfaces; verify which package owns a change before editing configuration.
- Never use real candidate or employee personal data in fixtures, examples, or commits. Do not expose credentials or secrets.
- Keep `memory-bank/progress.md` factual: record completed checks only after running them, and mark external or unavailable checks as pending.
