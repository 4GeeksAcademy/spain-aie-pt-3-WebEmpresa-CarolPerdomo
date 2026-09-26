# Nexova Backoffice

Internal executive dashboard starter for the Nexova monorepo. It surfaces company and departmental facts from the business context; values are reference data, not a live connection to company systems.

## Run locally

```bash
npm install
npm run dev -- --port 3001
```

Open <http://localhost:3001>. Production checks:

```bash
npm run lint
npm run build
```

This frontend has no backend. Any future API or integration service belongs under the monorepo's `/services` directory.
