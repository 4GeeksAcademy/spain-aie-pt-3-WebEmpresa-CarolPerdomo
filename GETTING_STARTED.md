# Getting Started with Nexova API

## Prerequisites

- Python 3.14+
- `uv` package manager (already installed in this environment)
- Git

## First-Time Setup

### 1. Install All Dependencies

Dependencies are already installed, but if you need to reinstall:

```bash
uv sync
```

This will install all packages from `pyproject.toml`.

### 2. Create Environment File (Optional)

The API works with default values, but you can customize:

```bash
# Copy example (note: may be blocked by content policy)
cp .env.example .env

# Or create your own:
cat > .env << 'ENVFILE'
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=./data/db.json
API_PORT=8000
API_HOST=0.0.0.0
ENVFILE
```

### 3. Start the Server

**Option 1: Using the provided script**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Option 2: Using uv directly**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Using Python directly**
```bash
# Activate the virtual environment if needed
source .venv/bin/activate

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server output should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Quick Test

Once the server is running, try these in another terminal:

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Register a User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "name": "Test User"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

Look for `"access_token"` in the response.

### 4. Access Protected Endpoint
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/auth/me
```

## Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can:
- See all available endpoints
- Try endpoints directly from the browser
- View request/response schemas
- Test with different parameters

## Running Tests

```bash
# Make test script executable
chmod +x test_api.sh

# Run all tests
./test_api.sh
```

## Project Structure

```
.
├── main.py                    # FastAPI application
├── services/
│   ├── core/                  # Core utilities
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # TinyDB wrapper
│   │   ├── models.py          # Pydantic schemas
│   │   └── security.py        # JWT & password utilities
│   ├── auth/                  # Authentication
│   │   ├── routes.py          # Login & /auth/me endpoints
│   │   └── dependencies.py    # Token validation
│   ├── users/                 # User management
│   │   └── routes.py          # User CRUD endpoints
│   └── profiles/              # Profile management
│       └── routes.py          # Profile endpoints
├── data/
│   └── db.json               # Local database
├── start_server.sh            # Server startup script
├── test_api.sh                # Test script
├── API_README.md              # Complete API docs
├── AUTH_IMPLEMENTATION.md     # Implementation guide
└── PROTECTING_ENDPOINTS.md    # How to protect endpoints
```

## Database

- **Type**: TinyDB (JSON-based)
- **Location**: `./data/db.json` (created automatically)
- **Content**: Users and Profiles tables
- **Persistence**: Data persists between server restarts

## Environment Variables

All optional (have sensible defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev-secret | JWT signing key (change in production!) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration in minutes |
| `DATABASE_URL` | ./data/db.json | Database file location |
| `API_PORT` | 8000 | Server port |
| `API_HOST` | 0.0.0.0 | Server host |

## Common Issues

### 1. Port Already in Use

```
ERROR: [Errno 98] Address already in use
```

Change the port:
```bash
uv run uvicorn main:app --port 8001
```

### 2. Module Not Found

```
ModuleNotFoundError: No module named 'fastapi'
```

Reinstall dependencies:
```bash
uv sync
```

### 3. Permission Denied on .sh Files

```bash
chmod +x start_server.sh test_api.sh
```

### 4. Token Expired

Tokens expire after 30 minutes. Login again to get a new one.

## Security Notes

⚠️ **Development Only**: The default `SECRET_KEY` is insecure. For production:

1. Generate a secure key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set it in your production `.env`:
   ```
   SECRET_KEY=your-generated-secure-key
   ```

3. Never commit `.env` with real secrets to git!

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the docs**: Check `API_README.md` for detailed endpoint info
3. **Create admin user**: Add an admin user to test role-based features
4. **Protect endpoints**: Use `PROTECTING_ENDPOINTS.md` as a guide
5. **Deploy**: Set up production environment when ready

## Support

- **API Documentation**: `API_README.md`
- **Implementation Guide**: `AUTH_IMPLEMENTATION.md`
- **Endpoint Protection**: `PROTECTING_ENDPOINTS.md`
- **Project Status**: `memory-bank/progress.md`
- **Business Requirements**: `CONTEXT.md`
- **Interactive Docs**: http://localhost:8000/docs

## Commands Cheat Sheet

```bash
# Start server
./start_server.sh
# OR
uv run uvicorn main:app --port 8000 --reload

# Run tests
./test_api.sh

# Register user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123","name":"Test"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123"}'

# Access protected endpoint with token
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/auth/me

# View interactive docs
open http://localhost:8000/docs
```

You're all set! 🚀
