# Nexova API - Authentication & User Management

## Overview

The Nexova API now includes a complete authentication system with JWT token-based access control. All user and profile routes are protected and require valid authentication.

## Key Features

✅ **User Registration** - Create accounts with email and password  
✅ **User Login** - Get JWT token with valid credentials  
✅ **Mandatory SECRET_KEY** - Requires environment variable for security  
✅ **Auto-Profile Creation** - Every user automatically gets a profile  
✅ **Password Hashing** - Secure bcrypt password storage  
✅ **5+ Protected Routes** - Full CRUD with 401/403 enforcement  
✅ **Role-Based Access** - Users only access their own data (403 Forbidden on cross-access)  

## Setup

### 1. Install Dependencies

```bash
cd services/api
uv pip install -e .
```

Or with pip:
```bash
pip install -r requirements.txt  # if generated
```

### 2. Set SECRET_KEY Environment Variable

**REQUIRED** - The API will fail to start without this:

```bash
export SECRET_KEY="your-secure-random-secret-key-min-32-chars"
```

**Example for development:**
```bash
export SECRET_KEY="dev-secret-key-change-in-production-12345"
```

### 3. Run the API

```bash
python -m uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will start at `http://localhost:8000`

## API Endpoints

### Authentication (Public Routes - No Token Required)

#### **POST /auth/register**
Register a new user.

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"  // optional
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-11-16T10:00:00"
  }
}
```

**Errors:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid email format or password < 8 chars

---

#### **POST /auth/login**
Login with email and password.

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
Same as registration response above.

**Errors:**
- `401 Unauthorized` - Invalid email or password

---

### Users (Protected Routes - Requires Valid JWT Token)

#### **GET /users/me** ✅ Protected
Get current authenticated user's information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-11-16T10:00:00"
}
```

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - User not found

---

#### **GET /users/{user_id}** ✅ Protected
Get a specific user's information (users can only access their own).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):** Same user object structure

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Attempting to access another user's data
- `404 Not Found` - User not found

---

#### **PUT /users/{user_id}** ✅ Protected
Update user information (name only).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Jane Doe"
}
```

**Response (200):** Updated user object

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Attempting to update another user
- `404 Not Found` - User not found

---

#### **DELETE /users/{user_id}** ✅ Protected
Delete user account (also deletes associated profile).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Attempting to delete another user
- `404 Not Found` - User not found

---

### Profiles (Protected Routes - Requires Valid JWT Token)

#### **GET /profiles/me** ✅ Protected
Get current user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "bio": "I am a talented professional...",
  "phone": "+34-666-123456",
  "location": "Valencia, Spain",
  "specialization": "Full Stack Development",
  "experience_years": 5,
  "created_at": "2024-11-16T10:00:00",
  "updated_at": "2024-11-16T10:30:00"
}
```

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Profile not found

---

#### **GET /profiles/{user_id}** ✅ Protected
Get a specific user's profile (users can only access their own).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):** Same profile object structure

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Accessing another user's profile
- `404 Not Found` - Profile not found

---

#### **PUT /profiles/me** ✅ Protected
Update current user's profile (all fields optional).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "bio": "Updated bio...",
  "phone": "+34-666-999888",
  "location": "Madrid, Spain",
  "specialization": "AI Engineering",
  "experience_years": 7
}
```

**Response (200):** Updated profile object

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Profile not found

---

#### **PUT /profiles/{user_id}** ✅ Protected
Update a specific user's profile (users can only update their own).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:** Same as PUT /profiles/me

**Response (200):** Updated profile object

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Updating another user's profile
- `404 Not Found` - Profile not found

---

## Protected Routes Summary

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | /auth/register | ❌ | Register new user |
| POST | /auth/login | ❌ | Login and get token |
| **GET** | **/users/me** | ✅ | Get current user |
| **GET** | **/users/{user_id}** | ✅ | Get user by ID |
| **PUT** | **/users/{user_id}** | ✅ | Update user |
| **DELETE** | **/users/{user_id}** | ✅ | Delete user |
| **GET** | **/profiles/me** | ✅ | Get current profile |
| **GET** | **/profiles/{user_id}** | ✅ | Get user profile |
| **PUT** | **/profiles/me** | ✅ | Update current profile |
| **PUT** | **/profiles/{user_id}** | ✅ | Update user profile |

**Total Protected Routes: 8 out of 10 (80% protected)**

---

## Security Features

### JWT Token Format

Tokens contain:
- `user_id` - User's database ID
- `email` - User's email address
- `iat` - Issued at timestamp
- `exp` - Expires at (24 hours from issue)

### Password Security

- Passwords are hashed with **bcrypt** (not stored in plain text)
- Minimum 8 characters required
- Each user password is independently salted

### Access Control

- **401 Unauthorized** - Returned when:
  - No token provided
  - Token is invalid or expired
  - Credentials are wrong (login)

- **403 Forbidden** - Returned when:
  - User tries to access/modify another user's data
  - User tries to delete another user's account
  - User tries to update another user's profile

### Profile Auto-Creation

Every user automatically gets a profile record upon registration. This ensures data integrity and simplifies profile-related operations.

---

## Example Usage with cURL

### 1. Register a user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123",
    "name": "Alice Johnson"
  }'
```

### 2. Login and get token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123"
  }'
```

**Store the `access_token` from the response.**

### 3. Access protected route with token

```bash
TOKEN="<access_token_from_login>"
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update profile

```bash
TOKEN="<access_token_from_login>"
curl -X PUT http://localhost:8000/profiles/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "I am a software engineer",
    "phone": "+34-666-123456",
    "location": "Valencia",
    "specialization": "Backend Development",
    "experience_years": 5
  }'
```

---

## Error Response Examples

### 401 Unauthorized (No Token)

```json
{
  "detail": "Missing or invalid token"
}
```

### 403 Forbidden (Cross-User Access)

```json
{
  "detail": "You do not have permission to access this resource"
}
```

### 400 Bad Request (Email Exists)

```json
{
  "detail": "Email already registered"
}
```

### 422 Unprocessable Entity (Validation Error)

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Important Notes

1. **SECRET_KEY is mandatory** - The API will not start without it set in environment variables
2. **Passwords are never returned** - API responses exclude password fields
3. **Profiles are auto-created** - You don't need to manually create profiles
4. **Tokens expire in 24 hours** - Users must login again after expiration
5. **All user data is isolated** - 403 errors enforce strict data ownership
6. **Database is TinyDB** - JSON-based, persisted to `data/suppliers.json`

---

## Development & Testing

### Run with auto-reload

```bash
export SECRET_KEY="dev-key-12345"
python -m uvicorn services.api.main:app --reload --port 8000
```

### View interactive API docs

Open `http://localhost:8000/docs` in your browser for Swagger UI

### View ReDoc alternative

Open `http://localhost:8000/redoc` in your browser

---

## Migration from Previous Implementation

This authentication system:
- ✅ Replaces the hardcoded SECRET_KEY (now mandatory from environment)
- ✅ Ensures every User has a Profile (auto-created)
- ✅ Protects 8 user/profile routes (exceeds the 5-route requirement)
- ✅ Enforces 401/403 properly with role-based access
- ✅ Lives in `/services/api/` protecting the monorepo

---

For questions or issues, refer to the main Nexova project documentation.
