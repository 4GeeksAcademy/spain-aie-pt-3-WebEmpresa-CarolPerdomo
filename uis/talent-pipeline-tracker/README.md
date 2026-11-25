This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Authentication and configuration

- All candidate pipeline and profile views require a valid Nexova API session. `/login` and `/register` are public.
- Registration uses `POST /auth/register`, then logs in and saves optional name, phone and address through `PUT /profiles/me`.
- The JWT is kept in `localStorage`; protected requests carry `Authorization: Bearer <token>`. A 401 removes the token and returns to `/login`.
- Password recovery is available at `/forgot-password` and `/reset-password`; signed-in users can update their password at `/account/change-password`.
- `API_URL` points to the Nexova FastAPI server (default `http://127.0.0.1:8000`). `TRACKER_API_URL` points to the candidate service (default `https://playground.4geeks.com/tracker/api/v1`). The server proxy validates the JWT with Nexova before forwarding candidate requests and does not send the JWT to the external tracker.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
