# Nexova Backoffice

Internal dashboard for the Nexova monorepo. It surfaces company and departmental facts from the business context; values are reference data, not a live connection to company systems. Login, registration and profile screens use the API in `services/api`.

## Authentication

- Open `/login` to sign in or `/register` to create an account. Public registration uses `POST /auth/register`; optional name, phone and address are saved to the new profile with `PUT /profiles/me`.
- The JWT is held in `localStorage`. Protected screens validate it through `GET /users/me`; API requests go through Next route handlers with a Bearer token.
- A `401` clears the token and sends the user to `/login`. `/`, `/suppliers` and `/account/profile` require a valid session.
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
