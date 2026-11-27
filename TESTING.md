# Testing

## FastAPI

From the repository root, install the project and development dependencies once, then run the unit suite:

```bash
uv sync
uv run pytest
```

The root pytest configuration discovers `services/api/tests`, adds the API and shared Python packages to the import path, and excludes the separately marked ASGI checks from the unit run. To run those routed-request checks separately:

```bash
uv run pytest -m integration
```

The endpoint unit modules, `services/api/tests/test_auth_endpoints.py` and `services/api/tests/test_users_profiles.py`, call route functions and helpers directly. They cover successful inputs, boundary cases, and failures without asserting HTTP serialization or framework internals. User/profile coverage can be checked from the root with:

```bash
uv run python services/api/run_coverage.py services/api/tests/test_users_profiles.py --cov=nexova_suppliers.routes.users --cov=nexova_suppliers.routes.profiles --cov-report=term-missing --cov-fail-under=60
```

Authentication logic coverage can be checked from the root with:

```bash
uv run python services/api/run_coverage.py services/api/tests/test_auth_endpoints.py --cov=nexova_suppliers.auth --cov=nexova_suppliers.dependencies --cov=nexova_suppliers.routes.auth --cov-report=term-missing --cov-fail-under=70
```

`services/api/run_coverage.py` preloads the compiled `bcrypt` extension before pytest-cov starts. This workaround is needed by the installed bcrypt wheel on the current CPython 3.15 Windows environment. It only affects coverage runs; the standard test command remains `uv run pytest`.

The AI-assisted edge case in this suite is horizontal access control: an authenticated user must be rejected when trying to read, update, or delete another user's account/profile, while the owner can access their own resource. This is covered in `services/api/tests/test_users_profiles.py`.

ASGI behavior checks in `services/api/tests/test_auth_http.py` and `services/api/tests/test_incidents.py` are marked `integration`; they are not included in the unit run by default.

## Backoffice utilities (Jest)

From `uis/backoffice/`, install that app's dependencies and run its tests independently:

```bash
npm install
npm run test:coverage -- --runInBand
```

Tests live in `uis/backoffice/__tests__/`. The current suite tests token read/write/removal and authenticated fetch behavior, including storage errors, unauthorized responses, and network failures. It measures coverage for the Backoffice auth utility.
