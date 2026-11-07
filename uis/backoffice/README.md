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

## Incident analysis

Start the Python API from the repository root in a separate terminal:

```bash
python services/api/server.py 8000
```

Open `/incidencias` in the backoffice to upload a CSV and download the latest aggregate report. Next.js forwards requests to `http://127.0.0.1:8000` by default; set `INCIDENTS_API_URL` on the Next.js server if the API runs at another address. See [the API documentation](../../services/api/README.md) for the upload limit, in-memory result lifetime, and security limitations. Protect access to the backoffice: neither it nor the API currently implements authentication.
