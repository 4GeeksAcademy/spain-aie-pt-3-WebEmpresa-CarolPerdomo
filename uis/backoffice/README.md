# Nexova Backoffice

Internal dashboard for the Nexova monorepo. It surfaces company and departmental facts from the business context; values are reference data, not a live connection to company systems. Login, registration and profile screens use the API in `services/api`.

## Authentication

- Open `/login` to sign in or `/register` to create an account. Public registration uses `POST /auth/register`; optional name, phone and address are saved to the new profile with `PUT /profiles/me`.
- The JWT is held in `localStorage`. Protected screens validate it through `GET /users/me`; API requests go through Next route handlers with a Bearer token.
- A `401` clears the token and sends the user to `/login`. `/`, `/suppliers` and `/account/profile` require a valid session.
- Password recovery is available at `/forgot-password` and `/reset-password`; signed-in users can update their password at `/account/change-password`.
- Set `API_URL` for the FastAPI server (defaults to `http://127.0.0.1:8000`). Keep this server-only variable out of client bundles.

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

## Inventory backoffice

The authenticated inventory screens are available at `/backoffice/inventory/products`, `/backoffice/inventory/orders/inbound`, `/backoffice/inventory/orders/outbound` and `/backoffice/inventory/orders`. Inventory API calls are centralized in `lib/inventory.ts` and use the existing Bearer-token helper. Set `NEXT_PUBLIC_INVENTORY_API_URL` in `.env.local` to the running FastAPI origin (for example, `http://localhost:8000`). The product list marks stock of 1-3 units as low and 0 as out of stock; the server remains authoritative when validating an outgoing order.
