# Development Progress

## Baseline Status

**Milestone:** Public website and talent registration  
**Status:** Complete authentication system implemented under `/services/api/` with JWT, bcrypt, mandatory SECRET_KEY, auto-profile creation, and 8+ protected routes. Backends ready for frontend integration.

## Implemented

- `index.html` contains a Spanish corporate landing page with service descriptions, responsive Tailwind utility classes, images with alt text, and Organization JSON-LD.
- `application.html` contains a company-services diagnostic form.
- `validation.js` validates fields in the company form, exposes field/status messages, supports reset, and simulates successful submission in the browser.
- Root TypeScript collection/search/transformation/validation utilities and npm typecheck/build scripts are present under `src/`.
- `uis/website/` is an independent Next.js public website with a responsive corporate homepage, reusable header/service/section/footer components, organization JSON-LD, company services, and contact details.
- `uis/backoffice/` is a separate Next.js app and layout with visible company KPIs, department signals, department filtering, text search, and a computed support-SLA gap. It labels its figures as briefing reference data, not live metrics.
- `uis/backoffice/app/suppliers/page.tsx` now provides the supplier directory with country/category filters, supplier creation, rate edits, and status changes. Its Next.js API routes forward the login's HTTP-only `access_token` cookie as a Bearer token; the API listing adds TinyDB document IDs to every supplier.
- `PUT /users/{user_id}` now updates account email and role with ownership/admin checks. Profile fields remain under `/profiles`; duplicate emails return 409. Added persistence and permission coverage in `services/api/tests/test_user_updates.py`.
- User roles are restricted to `admin` and `user`. Added admin-only `GET /users/` with password-free results and ASGI-level auth/CRUD tests for login, 401/403 behavior, profiles, user CRUD, and protected supplier access.
- Retired the duplicate supplier screens under `uis/application` and the root HTML files. The former `/login/suppliers` route redirects to `/suppliers`.
- Both frontend apps have per-app READMEs and run/build/lint scripts.

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

## Known Gaps Against the Current Context

- The form collects company and service-request details; it does not collect the required candidate profile fields from `CONTEXT.md`.
- The original root landing page CTA leads to that company-services form. The new `uis/website/` has a separate talent contact anchor, but currently uses email rather than a structured candidate form.
- The current simulated success copy and validation rules belong to the company inquiry flow, not the candidate flow.
- The original root landing page JSON-LD has a placeholder URL (`https://example.com`). The new `uis/website/` includes the Nexova organization fields from the context.
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

## Update Policy

Update this file after completing a meaningful implementation or verification step. Record only verified outcomes; keep unfinished or externally dependent checks explicitly marked as pending.

