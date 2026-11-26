# Nexova API - Implementation Summary

## Overview

A complete JWT-based authentication and user management system has been implemented as a FastAPI backend service. The system enables secure user registration, login, profile management, and role-based access control for the Nexova platform.

## What Was Built

### Core Components

1. **Authentication System**
   - JWT token-based authentication (stateless)
   - 30-minute token expiration (configurable)
   - Bearer token validation on protected endpoints
   - Automatic token invalidation on expiry

2. **User Management**
   - User registration with email and password
   - Password hashing with bcrypt (secure, salted)
   - User profile management (name, phone, address)
   - Role-based access control (admin, manager, user)
   - One-to-one User ↔ Profile relationship

3. **Data Persistence**
   - TinyDB (JSON-based) for local development
   - Automatic database initialization
   - No external dependencies required for testing

4. **API Documentation**
   - Interactive Swagger UI at `/docs`
   - ReDoc at `/redoc`
   - Complete endpoint documentation
   - Try-it-out functionality

## How to Use

### Start the Server

```bash
# Option 1: Using the startup script
./start_server.sh

# Option 2: Using uv directly
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Option 3: Using Python directly (after activating venv)
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Workflow

#### 1. Register a User

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St"
  }'
```

#### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response includes `access_token` (JWT).

#### 3. Use Token to Access Protected Endpoints

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

## API Endpoints

### Public Endpoints
- `POST /users` — User registration
- `POST /auth/login` — Login
- `GET /health` — Health check

### Protected Endpoints (Require Bearer Token)

**Authentication**
- `GET /auth/me` — Get current user info

**Users**
- `GET /users` — List all users
- `GET /users/{id}` — Get specific user
- `PUT /users/{id}` — Update user (email/role)
- `DELETE /users/{id}` — Delete user

**Profiles**
- `GET /profiles/me` — Get own profile
- `PUT /profiles/me` — Update own profile

## Error Handling

| Status | Scenario | Detail |
|--------|----------|--------|
| 400 | Bad Request | Invalid email, duplicate email, password too short |
| 401 | Unauthorized | Missing token, invalid token, expired token, wrong password |
| 403 | Forbidden | Missing auth header, token not provided |
| 404 | Not Found | User/profile not found |
| 422 | Validation Error | Invalid email format, missing required fields |

## Testing

### Run Tests

```bash
# Using the provided test script
./test_api.sh

# Or manually test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d '...'
```

### Test Scenarios Verified

✓ User registration with profile creation  
✓ Login with correct credentials  
✓ Login with wrong credentials (401)  
✓ Protected endpoint without token (401/403)  
✓ Protected endpoint with valid token (200)  
✓ Protected endpoint with invalid token (401)  
✓ Duplicate email registration (400)  
✓ Invalid email format (422)  
✓ List users (protected)  
✓ Get user by ID (protected)  
✓ Update profile (protected)  
✓ Delete user (protected)  

## Project Structure

```
/services
  /core              # Core utilities
    config.py        # Environment configuration
    database.py      # TinyDB wrapper
    models.py        # Pydantic schemas
    security.py      # JWT & password utilities
  /auth              # Authentication
    dependencies.py  # Token validation dependency
    routes.py        # Login & /auth/me endpoints
  /users             # User management
    routes.py        # CRUD endpoints
  /profiles          # Profile management
    routes.py        # Profile endpoints

main.py              # FastAPI application factory
start_server.sh      # Server startup script
test_api.sh          # Test script
API_README.md        # Detailed API documentation
```

## Configuration

Environment variables (set in `.env`):

```env
SECRET_KEY=your-secret-key-here (default: dev-secret)
ACCESS_TOKEN_EXPIRE_MINUTES=30 (default: 30)
DATABASE_URL=./data/db.json (default: ./data/db.json)
API_PORT=8000 (default: 8000)
API_HOST=0.0.0.0 (default: 0.0.0.0)
```

## Dependencies

All dependencies are in `pyproject.toml`:

- **fastapi** — Web framework
- **uvicorn** — ASGI server
- **tinydb** — Local JSON database
- **pydantic** — Data validation
- **python-jose[cryptography]** — JWT handling
- **passlib[bcrypt]** — Password hashing
- **email-validator** — Email validation
- **pydantic-settings** — Configuration management

## Security Features

✓ Passwords hashed with bcrypt (never stored plain-text)  
✓ JWT tokens with expiration  
✓ HTTPBearer token validation  
✓ Role-based access control (admin/manager/user)  
✓ User permission checks (own resources or admin)  
✓ CORS headers for cross-origin requests  
✓ Input validation with Pydantic  
✓ Email format validation  

## Next Steps

1. **Frontend Integration**: Connect candidate registration form to API
2. **Deployment**: Set up production environment with PostgreSQL
3. **Enhanced Features**: 
   - Email verification
   - Password reset flow
   - Refresh token rotation
   - Audit logging
   - Rate limiting
4. **Database Migration**: Migrate from TinyDB to PostgreSQL for production

## Documentation

- [API_README.md](./API_README.md) — Full API documentation with examples
- [memory-bank/progress.md](./memory-bank/progress.md) — Development progress
- Swagger UI: http://localhost:8000/docs

## Support

For issues or questions:

1. Check the server logs: `tail -f /tmp/server.log`
2. Review API_README.md for endpoint details
3. Test endpoints in Swagger UI: http://localhost:8000/docs
4. Verify configuration in `.env`
