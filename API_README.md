# Nexova API - Authentication & User Management

Complete JWT-based authentication system with user and profile management using FastAPI and TinyDB.

## Features

- ✅ JWT token-based authentication (stateless)
- ✅ User registration with email and password hashing (bcrypt)
- ✅ Role-based access control (admin, manager, user)
- ✅ User profile management (one-to-one relationship)
- ✅ Protected endpoints with bearer token validation
- ✅ Password hashing with `passlib[bcrypt]`
- ✅ TinyDB for persistent storage (no external database required)
- ✅ Automatic API documentation (Swagger UI)

## Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: TinyDB (JSON-based)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (via passlib)
- **Validation**: Pydantic

## Setup

### Prerequisites

- Python 3.14+
- uv package manager (already installed)

### Installation

All dependencies are already installed. If you need to reinstall:

```bash
uv add fastapi uvicorn python-multipart tinydb pydantic python-dotenv \
    python-jose[cryptography] passlib[bcrypt] pydantic-settings
```

### Configuration

Create a `.env` file in the project root:

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=./data/db.json

# Server
API_PORT=8000
API_HOST=0.0.0.0
```

> ⚠️ **IMPORTANT**: Change the `SECRET_KEY` in production to a cryptographically secure random string.

## Running the API

### Using the startup script

```bash
./start_server.sh
```

### Using uvicorn directly

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Using uv run

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

#### `POST /auth/login`
Authenticate with email and password, receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `GET /auth/me`
Get the authenticated user's profile (requires Bearer token).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "email": "user@example.com",
  "role": "user",
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St"
  }
}
```

### Users

#### `POST /users`
Register a new user (public endpoint).

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "securePassword123",
  "name": "John Doe",
  "phone": "+1234567890",
  "address": "123 Main St"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "is_active": true,
  "role": "user",
  "created_at": "2024-01-01T00:00:00",
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St"
  }
}
```

#### `GET /users`
List all users (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

#### `GET /users/{user_id}`
Get a specific user (requires authentication).

Regular users can only view their own profile; admins can view any user.

#### `PUT /users/{user_id}`
Update user credentials (email and/or role).

Only admins can change roles. Users can update their own email.

**Request:**
```json
{
  "email": "newemail@example.com",
  "role": "manager"
}
```

#### `DELETE /users/{user_id}`
Delete a user and their profile (requires authentication).

Users can delete their own account; admins can delete any user.

### Profiles

#### `GET /profiles/me`
Get the authenticated user's profile (requires Bearer token).

#### `PUT /profiles/me`
Update the authenticated user's profile.

**Request:**
```json
{
  "name": "Jane Doe",
  "phone": "+0987654321",
  "address": "456 Oak Ave"
}
```

## Authentication Flow

### 1. Register

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

Response includes `access_token`.

### 3. Use Token

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

## Database Structure

### Users Table
- `id`: UUID (primary key)
- `email`: String (unique)
- `hashed_password`: String (bcrypt hash)
- `is_active`: Boolean
- `role`: Enum (admin, manager, user)
- `created_at`: ISO timestamp

### Profiles Table
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users)
- `name`: String
- `phone`: String (optional)
- `address`: String (optional)

## Security Considerations

- **Passwords**: Never stored in plain text. Always hashed with bcrypt.
- **Tokens**: JWT tokens are stateless and validated using the SECRET_KEY.
- **Secrets**: Never commit `.env` file with real secrets. Use `.env.example` for reference.
- **HTTPS**: In production, always use HTTPS for API communication.
- **CORS**: Currently allows all origins. Restrict in production.

## Testing

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" and enter your token
3. Try endpoints directly from the UI

### Using cURL

```bash
# Register
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","name":"Test User"}'

# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Use token
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## Error Responses

### 400 Bad Request
- Email already registered
- Invalid email format
- Password too short

### 401 Unauthorized
- Missing or invalid token
- Expired token
- Invalid credentials
- User account inactive

### 403 Forbidden
- User does not have permission to access resource
- Only admins can perform this action

### 404 Not Found
- User or profile not found

## Development

### Project Structure

```
services/
├── core/
│   ├── config.py       # Configuration and environment variables
│   ├── database.py     # TinyDB wrapper and operations
│   ├── models.py       # Pydantic schemas
│   └── security.py     # JWT and password utilities
├── auth/
│   ├── dependencies.py # Token validation dependency
│   └── routes.py       # Login and /auth/me endpoints
├── users/
│   └── routes.py       # User CRUD endpoints
└── profiles/
    └── routes.py       # Profile endpoints
main.py                 # FastAPI app factory
start_server.sh         # Server startup script
```

### Adding More Protected Endpoints

To protect an endpoint, add the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from services.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['email']}"}
```

### Extending Roles

To add role-specific logic:

```python
from services.auth.dependencies import get_current_admin_user

@router.delete("/admin-only")
async def admin_only(current_user: dict = Depends(get_current_admin_user)):
    # Only admins can reach this endpoint
    return {"message": "Admin action performed"}
```

## Performance Notes

- TinyDB stores data in JSON format for simplicity
- For production systems with high concurrency, consider migrating to PostgreSQL
- Token validation is performed on every protected request
- Database queries are not indexed; consider optimization for large datasets

## Future Enhancements

- [ ] Email verification
- [ ] Password reset flow
- [ ] Two-factor authentication
- [ ] Audit logging
- [ ] Rate limiting
- [ ] Database migration to PostgreSQL
- [ ] Redis caching for tokens
- [ ] Refresh token rotation
