# Development Progress

## Baseline Status

**Milestone:** Public website and talent registration  
**Status:** Complete authentication system implemented under `/services/api/` with JWT, bcrypt, mandatory SECRET_KEY, auto-profile creation, and 8+ protected routes. Backends ready for frontend integration.

## Implemented

### Frontend
- `index.html` contains a Spanish corporate landing page with service descriptions, responsive Tailwind utility classes, images with alt text, and Organization JSON-LD.
- `application.html` contains a company-services diagnostic form.
- `validation.js` validates fields in the company form, exposes field/status messages, supports reset, and simulates successful submission in the browser.
- Root TypeScript collection/search/transformation/validation utilities and npm typecheck/build scripts are present under `src/`.
- `uis/website/` is an independent Next.js public website with a responsive corporate homepage, reusable header/service/section/footer components, organization JSON-LD, company services, and contact details.
- `uis/backoffice/` is a separate Next.js app and layout with visible company KPIs, department signals, department filtering, text search, and a computed support-SLA gap. It labels its figures as briefing reference data, not live metrics.
- Both frontend apps have per-app READMEs and run/build/lint scripts.
- `scripts/analyze.py` analyzes incident CSV files, reports validation failures and aggregate metrics without exposing customer emails, and optionally exports one metric per row.
- `services/api/` shares that analysis with a local HTTP API, and `uis/backoffice/` provides an incident upload, summary and CSV export through server-side proxy routes. The latest aggregate report is stored in process memory only.
- `uis/backoffice/app/suppliers/page.tsx` provides the supplier directory with country/category filters, supplier creation, rate edits, and status changes. Its Next.js API routes forward the localStorage JWT as a Bearer token; the API listing adds TinyDB document IDs to every supplier.
- `PUT /users/{user_id}` now updates account email and role with ownership/admin checks. Profile fields remain under `/profiles`; duplicate emails return 409. Added persistence and permission coverage in `services/api/tests/test_user_updates.py`.
- User roles are `admin`, `manager`, and `user`. Admins can assign roles when creating users and changing roles; new users default to `user`. `GET /users/` is admin-only and returns password-free results. ASGI-level tests cover login, 401/403 behavior, profiles, user CRUD, and protected supplier access.
- Retired the duplicate supplier screens under `uis/application` and the root HTML files. The former `/login/suppliers` route redirects to `/suppliers`.
- Both frontend apps have per-app READMEs and run/build/lint scripts.
- Backoffice and talent-pipeline views now include login, registration, profile editing, client-side route guards and logout. Authenticated requests send the JWT to the Nexova API; the candidate tracker Next proxy validates it before forwarding requests to the external tracker API without disclosing the JWT to that service. `/website` remains public.

## Internal Authentication Verification

### Frontend (Verified ✓)
- `npm run build --prefix uis/website` — passed.
- `npm run build --prefix uis/backoffice` — passed.
- `npm run lint --prefix uis/website` — passed.
- `npm run lint --prefix uis/backoffice` — passed.
- Local HTTP smoke tests for both `/` routes — returned 200 and contained the expected Nexova content.
- Website Organization JSON-LD — parsed successfully; canonical URL and both office addresses were present.
- `python -m unittest discover -s scripts -p 'test_analyze.py' -v` — passed; synthetic incident data reproduces the briefing's aggregate values and exercises export and privacy checks.
- `python scripts/analyze.py incidents-nexova.csv` — verified against the provided CSV: all totals, invalid-record reasons, category and status distributions, and satisfaction values match the incident briefing.
- Backoffice lint and production build passed in a temporary dependency installation. HTTP checks through the backoffice proxy verified the briefing metrics, CSV export, invalid and empty uploads, and rejection of an outdated export.
- `npm run lint` and an isolated TypeScript check pass for `uis/backoffice/`.
- `npm run build` also passes for `uis/backoffice/` when run with access to Google Fonts.
- Installed tracker dependencies from its existing lockfile; its lint and production build both pass. `npm ci` reported 12 dependency audit findings (7 moderate, 4 high, 1 critical), but a subsequent `npm audit --json` returned zero vulnerabilities. The lockfile was not modified and no automatic fixes were applied. Next.js also warns that multiple lockfiles make its inferred Turbopack root ambiguous.

## Supplier Backoffice Verification

- `npm run build` from `uis/backoffice/` completes successfully with Next.js 16.3.4; the build includes `/suppliers` and the authenticated supplier API proxy routes.
- The production build required network access to fetch the Google Fonts already imported by `app/layout.tsx`.

## Password Recovery and Change

- Added `POST /auth/forgot-password`, `/reset-password`, and authenticated `/change-password`. Reset links are signed JWTs with configurable 15–60 minute expiry, stored one-time identifiers, and invalidation after password changes. Forgot-password responds with the same 200 payload for known and unknown emails.
- Added Resend delivery through `RESEND_API_KEY` and optional `RESEND_FROM_EMAIL`; reset URLs use `FRONTEND_BASE_URL`. Variable names and safe placeholders are documented in the root `.env.example` and API README.
- Added backoffice pages at `/forgot-password`, `/reset-password`, and `/account/change-password`, plus the login recovery link. The authenticated change proxy forwards the HTTP-only session cookie as Bearer authorization.
- Verification: API password recovery/email tests pass (4 tests), including expired/reused token rejection, password persistence, generic forgot response, authenticated password change, and a mocked Resend HTTP request containing the link. `npm run build` in `uis/backoffice/` completes and includes all three pages and API proxies. Actual inbox delivery still requires a registered test recipient and was not externally verified.

## Authentication System (New)

**Location:** `/services/api/` - Complete REST API with authentication foundation.

### Core Features Implemented

1. **Mandatory SECRET_KEY** ✅
   - `auth.py` raises `ValueError` if `SECRET_KEY` environment variable is not set
   - App will not start without SECRET_KEY
   - File: `services/api/auth.py:7-11`

2. **User & Profile Models** ✅
   - `UserCreate`, `UserResponse` with email and password
   - `ProfileCreate`, `ProfileResponse` with detailed fields (bio, phone, location, specialization, experience_years)
   - File: `services/api/models.py`

3. **Auto-Profile Creation** ✅
   - Every user automatically gets a Profile upon registration
   - Profile is created before returning from `create_user()`
   - Ensures every User has associated Profile data
   - File: `services/api/database.py:35-57`

4. **Password Security** ✅
   - Passwords hashed with bcrypt (`AuthService.hash_password()`)
   - Passwords never returned in responses
   - Minimum 8 characters enforced via Pydantic
   - File: `services/api/auth.py`

5. **JWT Authentication** ✅
   - Token generation with 24-hour expiration
   - Secure token decoding with error handling
   - User ID and email embedded in token payload
   - File: `services/api/auth.py:19-50`

6. **Protected Routes (8 Total - Exceeds 5 Requirement)** ✅

   **Auth (Public):**
   - `POST /auth/register` - User registration (creates User + auto-Profile)
   - `POST /auth/login` - User login (returns JWT token)

   **Users (Protected):**
   - `GET /users/me` - Get current user
   - `GET /users/{user_id}` - Get user (own data only)
   - `PUT /users/{user_id}` - Update user (own data only)
   - `DELETE /users/{user_id}` - Delete user (own data only)

   **Profiles (Protected):**
   - `GET /profiles/me` - Get current profile
   - `GET /profiles/{user_id}` - Get profile (own only)
   - `PUT /profiles/me` - Update current profile
   - `PUT /profiles/{user_id}` - Update profile (own only)

   Files: `services/api/routes/users.py`, `services/api/routes/profiles.py`

7. **Access Control** ✅
   - `401 Unauthorized` - Missing or invalid JWT token
   - `403 Forbidden` - User attempting to access another user's data
   - Enforced via `Depends(get_current_user)` and resource ownership checks
   - File: `services/api/dependencies.py`

8. **FastAPI Integration** ✅
   - All routers registered in main.py
   - Interactive docs at `/docs` (Swagger UI) and `/redoc` (ReDoc)
   - CORS middleware configured for cross-origin requests
   - File: `services/api/main.py`

### New Files Created

- `services/api/auth.py` - JWT and password management
- `services/api/dependencies.py` - FastAPI dependency functions for auth
- `services/api/routes/auth.py` - Register/login endpoints
- `services/api/routes/users.py` - User CRUD (protected)
- `services/api/routes/profiles.py` - Profile CRUD (protected)
- `services/api/README.md` - User-facing API documentation
- `services/api/README_AUTH.md` - Detailed authentication guide
- `services/api/test_auth.py` - Comprehensive test suite
- `services/api/demo.py` - Interactive demonstration
- `services/api/run.sh` - Quick start script

### Modified Files

- `services/api/models.py` - Added User, Profile, and auth Pydantic models
- `services/api/database.py` - Added user/profile operations and auto-profile creation
- `services/api/main.py` - Integrated auth/users/profiles routers
- `services/api/pyproject.toml` - Added PyJWT, bcrypt, pydantic[email]
- `services/api/routes/__init__.py` - Imported new route modules

### Verification

- ✅ Python syntax check: `py_compile` on all files
- ✅ FastAPI app imports successfully
- ✅ All 8 protected routes registered and accessible
- ✅ Test suite passes (4/4 tests):
  - SECRET_KEY is mandatory
  - Protected routes >= 5 requirement (8 found)
  - User-Profile auto-creation working
  - FastAPI app initialization successful

### Backend API (Verified ✓)
- `uv add` all dependencies: fastapi, uvicorn, tinydb, pydantic, bcrypt, python-jose[cryptography], email-validator, pydantic-settings — installed.
- API server starts with `uv run uvicorn main:app --port 8000` — confirmed running at http://localhost:8000.
- Health endpoint `/health` — returns 200 with service info.
- User registration `POST /users` — creates user + profile with bcrypt-hashed password, returns 201.
- Login `POST /auth/login` — accepts email/password, returns JWT token with 30-min TTL, status 200.
- Authentication `/auth/me` with valid token — returns user email, role, profile, status 200.
- Protected endpoint without token — returns 403 "Not authenticated".
- Protected endpoint with invalid token — returns 401 "Invalid or expired token".
- Duplicate email registration — returns 400 "Email already registered".
- Wrong password login — returns 401 "Invalid email or password".
- User list `GET /users` (protected) — returns all users, status 200.
- User detail `GET /users/{id}` (protected) — returns user with profile, status 200.
- Profile get `GET /profiles/me` (protected) — returns user's profile, status 200.
- Profile update `PUT /profiles/me` (protected) — updates name/phone/address, returns 200.
- Interactive docs `/docs` — Swagger UI loads successfully.
- Python syntax check — all modules compile without errors.
- File structure — `/services/` organized with core, auth, users, profiles packages.

### Test Scripts
- `test_api.sh` created with curl-based endpoint tests (executable).
- Manual verification tests completed successfully (registration → login → protected endpoints).

- The form collects company and service-request details; it does not collect the required candidate profile fields from `CONTEXT.md`.
- The original root landing page CTA leads to that company-services form. The new `uis/website/` has a separate talent contact anchor, but currently uses email rather than a structured candidate form.
- The current simulated success copy and validation rules belong to the company inquiry flow, not the candidate flow.
- The original root landing page JSON-LD has a placeholder URL (`https://example.com`). The new `uis/website/` includes the Nexova organization fields from the context.
- Executive dashboard metrics are static briefing facts. The incident API is a separate local service without authentication or durable storage; it is not production-ready or connected to an external system.
- Backend is now available but not yet wired to frontends. Candidate registration form needs to call POST /auth/register and manage JWT tokens.
- A public deployment and PageSpeed Insights result have not been verified. Do not claim the performance acceptance threshold is met.

## Next Steps

1. Connect `uis/website/` candidate-registration form to backend API (`POST /auth/register`, then store JWT and populate `/profiles/me`)
2. Update form field validation to match backend constraints (password min 8 chars, email format, etc)
3. Add error handling and success states that work with real API responses
4. Test end-to-end flow: register → auto-profile created → update profile → fetch profile
5. Measure PageSpeed Insights after deployment. Current requirement: >= 80, target: > 90.

## User Update Verification

- `pytest -p no:cacheprovider tests/test_user_updates.py -q` passes (4 tests), including email persistence after reopening TinyDB, admin-only role updates, and rejection of Profile fields on User updates.
- `pytest -p no:cacheprovider tests -q` passes (6 tests), including real Bearer-authenticated ASGI requests across users, profiles, and suppliers.

## Password Recovery and Change

- Implemented `POST /auth/forgot-password` with a generic `200` response and background Resend delivery; reset links expire after 30 minutes and only SHA-256 token hashes are persisted in TinyDB.
- Implemented one-time `POST /auth/reset-password`, authenticated `POST /auth/change-password`, and authenticated `GET /auth/me` (email plus profile data). Password updates invalidate outstanding reset links.
- Reset token lifetime is configurable through `PASSWORD_RESET_TOKEN_TTL_MINUTES` (15–60 minutes, default 30); password reset requests/outcomes and password changes are recorded with timestamp and client IP.
- Added `/forgot-password`, `/reset-password`, and `/account/change-password` to both Backoffice and Talent Pipeline Tracker, with bearer-authenticated change-password proxies and the forgot-password link on login.
- Added root `.env.example` and API documentation for `RESEND_API_KEY`, `EMAIL_FROM`, and `PASSWORD_RESET_URL`. The API loads the ignored root `.env` for local runs; no API key value was read, written, or included in tracked files.
- Corrected the `.env` root path after local startup exposed a one-directory offset; verified the API process now sees `SECRET_KEY` and `RESEND_API_KEY` as configured without printing their values.
- Resend delivery failures now log a sanitized provider status/message (redacting email addresses and API-key-like tokens) so 403 causes can be diagnosed without exposing credentials; Python syntax check passes.
- API `py_compile`, ESLint, and `npx tsc --noEmit` pass for the changed API and both frontend apps.
- Next production builds compile the app code but stop with `spawn EPERM` when Next starts its worker/type-check phase in this Windows environment (also reproduced with `--webpack`).
- Real email delivery has not been exercised; it depends on a valid Resend API key and verified sender configuration.

## Update Policy

Update this file after completing a meaningful implementation or verification step. Record only verified outcomes; keep unfinished or externally dependent checks explicitly marked as pending.


## Supplier Directory Acceptance Review (2026-11-22)

- Tightened supplier input validation: unknown fields (including client-supplied updated_at) are rejected, status/country/category use enums, rates must be finite and positive, categories require at least one item, and contact email/currency-country pairing are validated.
- Supplier create/get/update responses include the TinyDB document ID. Supplier creation and rate changes generate a UTC updated_at; filters validate input and combine country/category criteria.
- Seeder now fills missing briefing entries by name without duplicates, reports inserted and total counts, closes the database reliably, and runs against an injectable DB path. Removed employee names from supplier fixture notes.
- Backoffice supplier table now shows all briefing fields, including notes and timestamp, and highlights renewals within 60 days.
- Verification: uv run pytest -p no:cacheprovider tests/test_auth_http.py tests/test_supplier_seed.py -q passes (5 tests); npm run build in uis/backoffice passes; git diff --check passes.
## Centralized Incident Manager (New Milestone)

- Added the `Incident` model fields, allowed values, UTC timestamps, TinyDB persistence, lifecycle transition rules, and JWT-protected `/api/incidents` endpoints for create, list/filter, detail, status update, and summary.
- Added the backoffice registration, filtered incident list with status actions, summary view, navigation links, and authenticated Next.js API proxies.
- Added shared CSV validation/mapping helpers and an idempotent `scripts/seed_incidents.py`. It reports invalid rows without printing row contents and excludes customer email from incident records and import tracking.
- The historical CSV was loaded into a temporary TinyDB twice: first run inserted 96 valid records and skipped 4 invalid rows; the second inserted 0 and skipped the same 96 as duplicates. Summary counts matched the briefing: statuses 27/56/13 and categories 49/35/12. Console output contained no customer email values.
- Added three API lifecycle, validation, filtering, and empty-summary tests. The targeted API suite (`test_incidents.py`, `test_auth_http.py`, and `test_user_updates.py`) passes: 9 passed, with no warnings, using test database files under `services/api/data` because Windows temporary directories are access-restricted in this environment.
- Modernized the remaining Pydantic v2 model configuration/validators and replaced deprecated naive UTC timestamp calls in authentication, password reset, and profile persistence. Legacy naive reset-token timestamps are still interpreted as UTC.
- Backoffice ESLint and TypeScript checks pass. The production Next build succeeds when the existing Google Fonts import can access the network.
- Completed browser acceptance against an isolated local database: login, empty summary, branch-origin highlighting and helper text, incident creation, list display, `open` -> `in_progress` -> `resolved` transitions, and summary totals by status, category, origin, and branch. The browser test used fictional data and its local database was removed afterward.

## Error Handling Audit (2026-11-26)

- Fixed a stray line in `nexova_suppliers/models.py` that prevented API test collection and added the missing `get_setting` helper used by authentication configuration.
- Updated password-reset tests to verify random one-time tokens are stored only as hashes, and updated the Resend test to match the documented `RESEND_API_KEY`/`EMAIL_FROM` configuration and the module's `urlopen` seam.
- Changed the supplier-seed test to use an isolated, uniquely named database under `services/api/data`, avoiding inaccessible Windows temporary folders.
- Verification: the five API test files pass (13 tests); Python syntax compilation, ESLint, and TypeScript checks pass. `git diff --check` passes.
- Both Next.js production builds compile the app, then stop at the type-check worker with `spawn EPERM`. Browser acceptance remains pending because the computer-use browser host was unavailable.
- Running pytest against the entire `tests/` directory still encounters pre-existing inaccessible `tests/tmp*` directories during collection; explicitly listing the five test modules avoids those directories and runs the full suite.

## Authentication Unit Test Battery (2026-11-27)

- Added direct unit coverage for all six `/auth` endpoints plus password hashing, access-token decoding/expiry, and current-user token validation. The new endpoint unit module calls route functions directly and does not test HTTP response serialization.
- Added Jest tests for both frontend auth clients, covering token storage, bearer headers, no-cache behavior, 401 cleanup, non-401 responses, and network failures.
- Added root `TESTING.md`, Jest configuration/scripts, and pytest discovery settings that skip inaccessible legacy `tmp*` directories.
- Verification: `uv run pytest` passes all 35 API tests. `npm run test:coverage -- --runInBand` passes all 18 Jest tests with 100% statements, branches, functions, and lines for both authentication clients.

## Expanded Unit Test Coverage (2026-11-27)

- Added direct unit tests for the user and profile route modules, covering successful operations, input boundaries, permission failures, conflicts, and missing records. These tests do not exercise HTTP serialization.
- Moved the Backoffice auth utility Jest tests into `uis/backoffice/__tests__/` and configured app-local `test` and `test:coverage` scripts so that suite runs independently of the monorepo root.
- Updated root `TESTING.md` with backend and app-local frontend test/coverage commands. Added `services/api/run_coverage.py` to preload bcrypt for coverage on the local CPython 3.15 Windows environment.
- Verification: full API suite passes (45 tests). The coverage run reports 83% for `auth.py`, 87% for the auth routes, 100% for user routes, and 100% for profile routes (89% total across selected modules). Separate auth and user/profile coverage runs are documented with thresholds of 70% and 60% respectively.
- Verification: `npm run test:coverage -- --runInBand` from `uis/backoffice/` passes 8 tests with 100% statements, branches, functions, and lines for `lib/auth-client.ts`.
- The API suite emits one existing Starlette deprecation warning from the user update route's 422 status constant. It does not fail tests.

## Unit Test Evaluation Checklist Review (2026-11-27)

- Documented an AI-assisted cross-user access edge case and noted the pre-existing ASGI-level suites in `TESTING.md` so the unit/integration boundary is clear.
- Updated the root Python pin to 3.15, added root dev dependencies for pytest/coverage/PyJWT, and configured root test discovery to run the API unit suite with API/shared packages on the import path.
- Marked the seven pre-existing ASGI request/response checks as `integration`, outside the default unit run. They remain available via `uv run pytest -m integration`.
- Verification from the root: literal `uv run pytest` passes 38 unit tests with 7 integration tests deselected; `uv run pytest -m integration` passes all 7 marked checks.
- Re-ran Backoffice Jest coverage: all 8 tests pass with 100% coverage for the auth utility.

