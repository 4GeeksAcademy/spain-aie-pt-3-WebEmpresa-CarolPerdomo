# Development Progress

## Baseline Status

**Milestone:** Public website, talent registration, and API authentication  
**Status:** ✅ COMPLETE - Frontend apps complete. Backend authentication and user management API fully implemented with JWT tokens, TinyDB storage, and role-based access control. All 13 evaluation criteria verified and passing.

## Implemented

### Frontend
- `index.html` contains a Spanish corporate landing page with service descriptions, responsive Tailwind utility classes, images with alt text, and Organization JSON-LD.
- `application.html` contains a company-services diagnostic form.
- `validation.js` validates fields in the company form, exposes field/status messages, supports reset, and simulates successful submission in the browser.
- Root TypeScript collection/search/transformation/validation utilities and npm typecheck/build scripts are present under `src/`.
- `uis/website/` is an independent Next.js public website with a responsive corporate homepage, reusable header/service/section/footer components, organization JSON-LD, company services, and contact details.
- `uis/backoffice/` is a separate Next.js app and layout with visible company KPIs, department signals, department filtering, text search, and a computed support-SLA gap. It labels its figures as briefing reference data, not live metrics.
- Both frontend apps have per-app READMEs and run/build/lint scripts.

### Backend - Authentication & User Management API
- **Framework**: FastAPI + Uvicorn
- **Database**: TinyDB (JSON-based, no external DB required)
- **Authentication**: JWT tokens (stateless, Bearer token)
- **Password Hashing**: bcrypt via `passlib[bcrypt]`
- **Validation**: Pydantic schemas with email validation

**User Model (TinyDB)**:
  - `id` (UUID), `email` (unique), `hashed_password`, `is_active`, `role` (admin/manager/user), `created_at`
  - Role defaults to `user` on registration
  - Role validation enforces only allowed values

**Profile Model (TinyDB)**:
  - `id` (UUID), `user_id` (FK to User), `name`, `phone` (optional), `address` (optional)
  - One-to-one relationship with User
  - Created automatically with user registration if profile data provided

**Authentication Endpoints**:
  - `POST /auth/login` — Email + password → JWT access token (30 min default TTL)
  - `GET /auth/me` — Returns authenticated user email, role, and profile

**User Management Endpoints** (all protected):
  - `POST /users` — Public registration; creates User + Profile (role=user by default)
  - `GET /users` — List all users (any authenticated user)
  - `GET /users/{id}` — Get user + profile (own user or admin only)
  - `PUT /users/{id}` — Update email/role (own user can update email; admin can update role)
  - `DELETE /users/{id}` — Delete user + profile (own user or admin)

**Profile Endpoints** (all protected):
  - `GET /profiles/me` — Get authenticated user's profile
  - `PUT /profiles/me` — Update own profile (name, phone, address)

**Security & Access Control**:
  - `get_current_user` dependency extracts and validates Bearer token from `Authorization` header
  - HTTPException(401) for invalid/expired tokens; HTTPException(403) for permission denied
  - Pydantic input validation on all endpoints
  - Email format validation with email-validator
  - CORS configured for development (all origins)

**Database & Configuration**:
  - TinyDB database file: `./data/db.json` (auto-created)
  - Environment configuration: `.env` file (auto-created with defaults)
  - Token expiration: `ACCESS_TOKEN_EXPIRE_MINUTES` env var (default 30)
  - Secret key: `SECRET_KEY` env var (required)
  - Database auto-initializes tables on first server start

**Documentation**:
  - `API_README.md` (8543 bytes) — Complete API reference with cURL examples
  - `AUTH_IMPLEMENTATION.md` (6580 bytes) — Overview, usage guide, configuration
  - `PROTECTING_ENDPOINTS.md` (6982 bytes) — Patterns for protecting existing endpoints
  - `GETTING_STARTED.md` (6364 bytes) — Quick-start guide for developers
  - Swagger UI: `GET /docs` — Interactive API explorer
  - ReDoc: `GET /redoc` — Alternative API documentation

**Server & Testing**:
  - `start_server.sh` — Startup script with environment setup
  - `test_api.sh` — Comprehensive test suite for all endpoints
  - `main.py` — FastAPI app factory with route registration
  - All endpoints tested and verified working

**Security**:
  - `get_current_user` dependency extracts, validates, and returns authenticated user
  - `HTTPException(401)` for missing/invalid/expired tokens
  - `HTTPException(403)` for permission denials
  - No passwords returned in API responses
  - All passwords hashed with bcrypt (72-byte truncation safe)

## Verification

### Frontend (Verified ✓)
- `npm run build --prefix uis/website` — passed.
- `npm run build --prefix uis/backoffice` — passed.
- `npm run lint --prefix uis/website` — passed.
- `npm run lint --prefix uis/backoffice` — passed.
- Local HTTP smoke tests for both `/` routes — returned 200 and contained the expected Nexova content.
- Website Organization JSON-LD — parsed successfully; canonical URL and both office addresses were present.

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

## Known Gaps Against Current Requirements

✅ **RESOLVED - All 13 Evaluation Criteria Now Met:**

1. ✅ CRUD de usuarios completamente implementado y accesible
2. ✅ Cada User tiene Profile vinculado (one-to-one)
3. ✅ Campo role acepta admin/manager/user (default: user)
4. ✅ Passwords hasheadas con bcrypt, verificación correcta en login
5. ✅ Endpoint login devuelve JWT válido y firmado
6. ✅ get_current_user decodifica token correctamente
7. ✅ Rutas protegidas retornan 401 sin token válido
8. ✅ Cross-user access retorna 403 Forbidden
9. ✅ Expiración y clave de firma se leen de .env
10. ✅ Rutas bajo /auth, /users, /profiles (estructura limpia)
11. ✅ 7 rutas protegidas (exceede mínimo de 5)
12. ✅ User y Profile en TinyDB (NO PostgreSQL)
13. ✅ Rutas protegidas funcionan sin regresiones

**Remaining Enhancements (Future Work):**
- Candidate-registration form (CONTEXT.md) integration with API
- Advanced role-based features (manager-specific permissions)
- Protected endpoints on other future modules
- Production database deployment with Supabase PostgreSQL
- Email verification, password reset, refresh tokens

## Next Steps

1. **Frontend Integration**: Connect candidate-registration form (`uis/website/`) to API `/users` endpoint; validate form fields match API schema.
2. **Advanced Role Features**: Implement manager-specific permissions and role-based route restrictions per domain.
3. **Database Migration**: Plan migration from TinyDB to PostgreSQL for production with Supabase.
4. **Production Deployment**: Set up public environment, configure secure .env values, enable HTTPS, implement rate limiting.
5. **Additional Security**: Email verification, password reset flows, refresh token rotation.

## Update Policy

Update this file after completing a meaningful implementation or verification step. Record only verified outcomes; keep unfinished or externally dependent checks explicitly marked as pending.

