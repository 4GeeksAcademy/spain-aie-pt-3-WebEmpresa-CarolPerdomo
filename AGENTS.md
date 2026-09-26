# Agent Instructions

## Start of Every Session

Before making changes, read these files in order:

1. `memory-bank/projectbrief.md` for the business, project goal, and domain boundary.
2. `memory-bank/techContext.md` for verified stack details and technical constraints.
3. `memory-bank/progress.md` for current implementation status, known gaps, and next steps.
4. `.agents/rules/nexova-development.md` for the always-active repository rule.
5. The applicable `CONTEXT.md`, relevant folder `README.md`, and any closer `AGENTS.md` or applicable instruction files for the files being changed.

Treat the context documents as the source of product requirements and inspect the working tree before editing. Preserve unrelated user changes.

## Required Workflow Before Every Commit

Complete these steps in order before creating each commit:

1. **Inspect scope:** review `git status` and the complete diff; identify existing user changes and exclude unrelated files.
2. **Confirm requirements:** read the applicable context, local instructions, and acceptance criteria; state what the change is intended to satisfy.
3. **Implement and document:** make the smallest scoped change, and update `memory-bank/progress.md` when verified project status or next steps change.
4. **Validate:** run the narrowest relevant tests, type checks, lint/build commands, and any required manual acceptance checks. Resolve relevant failures or record checks that are blocked; do not claim unverified results.
5. **Review staged content:** stage only task-related files; inspect the staged diff for accidental changes, secrets, personal data, generated artifacts, and whitespace errors.
6. **Commit and confirm:** only after steps 1-5 pass, create a descriptive commit and verify the resulting commit and working-tree status. Do not create commits unless the developer has asked for one.

## Changes Requiring Explicit Developer Confirmation

Do not modify these without explicit confirmation from the developer for the specific change:

- Product source-of-truth context: `CONTEXT.md`, `CONTEXT-en.md`, and `CONTEXT-nexova-briefing.es.md`.
- Agent policy and repository-wide instructions: `AGENTS.md`, `.agents/rules/**`, `.github/**`, and other root or directory-level agent instruction files.
- Dependency, build, or compiler configuration: `package.json`, package lockfiles, `tsconfig.json`, and workspace/build configuration.
- Infrastructure and automation with deployment or external side effects: `infra/**`, `workflows/**`, and deployment configuration.
- Raw source datasets and any real candidate, employee, or customer personal data: `data/raw/**` and equivalent files elsewhere.
- Secrets and local environment configuration: `.env*`, credentials, tokens, and private keys. Never expose secret values in output or commits.
- Git internals and generated/dependency directories: `.git/**`, `node_modules/**`, and generated build output such as `dist/**`.

A direct developer request that explicitly names one of these changes counts as confirmation for that requested scope only.
