# Nexova API

Complete REST API for Nexova Solutions with **authentication**, **user management**, and **supplier directory**.

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based access control
- 👤 **User Management** - Full CRUD with password hashing (bcrypt)
- 📋 **User Profiles** - Auto-created for every user, with detailed personal info
- 🏢 **Supplier Directory** - Complete supplier management system
- ⚡ **FastAPI** - Modern, fast, automatic API documentation
- 🛡️ **Role-Based Access** - 403 Forbidden on cross-user access, 401 on missing auth
- 📚 **Interactive Docs** - Swagger UI at `/docs`, ReDoc at `/redoc`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd services/api
pip install PyJWT bcrypt pydantic[email] fastapi uvicorn tinydb python-multipart
```

### 2. Set SECRET_KEY Environment Variable

**REQUIRED** - The API will not start without this:

```bash
export SECRET_KEY="your-secure-random-secret-key-min-32-chars"
```

### 3. Run the Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or use the provided script:

```bash
bash run.sh
```

The API will be available at: **http://localhost:8000**

## 📚 API Documentation

- **Swagger UI** (Interactive): http://localhost:8000/docs
- **ReDoc** (Alternative): http://localhost:8000/redoc
- **Full API Guide**: See [README_AUTH.md](./README_AUTH.md)

## 🔑 Protected Routes (8 Total)

### Users
- `GET /users/me` - Get current user
- `GET /users/{user_id}` - Get specific user (own data only)
- `PUT /users/{user_id}` - Update user (own data only)
- `DELETE /users/{user_id}` - Delete user (own data only)

### Profiles
- `GET /profiles/me` - Get current profile
- `GET /profiles/{user_id}` - Get user profile (own only)
- `PUT /profiles/me` - Update current profile
- `PUT /profiles/{user_id}` - Update user profile (own only)

## 🔓 Public Routes (No Auth Required)

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and get JWT token

### Suppliers (Full CRUD)
- `GET /suppliers` - List all suppliers
- `POST /suppliers` - Create supplier (requires auth)
- `GET /suppliers/{id}` - Get supplier details
- `PATCH /suppliers/{id}/rate` - Update supplier rate (requires auth)
- `PATCH /suppliers/{id}/status` - Update supplier status (requires auth)
- `DELETE /suppliers/{id}` - Delete supplier (requires auth)

## 🧪 Testing

Run the authentication test suite:

```bash
export SECRET_KEY="test-secret-key-12345-min-32-chars-requirement"
python test_auth.py
```

Expected output:
```
✅ PASS: SECRET_KEY mandatory
✅ PASS: Protected routes (5+)
✅ PASS: User-Profile auto-creation
✅ PASS: FastAPI app initialization

Total: 4/4 tests passed
```

## 📋 Example Flow

### 1. Register a new user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "name": "John Doe"
  }'
```

**Response:**
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

### 2. Access protected route with token

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Update your profile

```bash
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

## 🔒 Security Highlights

| Feature | Implementation |
|---------|-----------------|
| **Secret Key** | Mandatory environment variable (raises ValueError if missing) |
| **Passwords** | Hashed with bcrypt, never stored in plain text |
| **Tokens** | JWT with 24-hour expiration |
| **Access Control** | 401 Unauthorized for missing/invalid tokens |
| **Data Ownership** | 403 Forbidden when accessing another user's data |
| **Profile Creation** | Auto-created for every user (no missing profiles) |

## 📁 Project Structure

```
services/api/
├── main.py                # FastAPI application entry point
├── auth.py               # JWT and password management
├── models.py             # Pydantic data models (User, Profile, etc)
├── database.py           # TinyDB operations
├── dependencies.py       # FastAPI dependency functions
├── routes/
│   ├── auth.py          # /auth routes (register, login)
│   ├── users.py         # /users routes (CRUD)
│   ├── profiles.py      # /profiles routes (CRUD)
│   └── suppliers.py     # /suppliers routes (CRUD)
├── pyproject.toml        # Project configuration
├── README_AUTH.md        # Detailed authentication guide
├── test_auth.py         # Test suite
└── run.sh               # Quick start script
```

## 🌍 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ Yes | Secret key for JWT signing (min 32 chars recommended) |

**Example .env file:**
```bash
export SECRET_KEY="production-secret-key-change-regularly-12345"
```

## 🔧 Configuration

Edit values in [auth.py](./auth.py):
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime (default: 1440 = 24 hours)

## 💾 Database

Uses **TinyDB** for data persistence:
- File: `data/suppliers.json`
- Tables: `suppliers`, `users`, `profiles`
- Format: JSON for easy inspection/debugging

## 🚨 Error Responses

### 401 Unauthorized
```json
{
  "detail": "Missing or invalid token"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to access this resource"
}
```

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 422 Unprocessable Entity
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

## 📖 Additional Resources

- [Full Authentication Guide](./README_AUTH.md) - Detailed endpoint documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT Introduction](https://jwt.io/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt)

## 🤝 Contributing

When adding new protected routes:

1. Add the route to the appropriate file in `routes/`
2. Use `Depends(get_current_user)` to require authentication
3. Use `Depends(verify_owns_resource)` to restrict to resource owner
4. Document the endpoint in [README_AUTH.md](./README_AUTH.md)

## 📄 License

Part of Nexova Solutions projects. See root LICENSE file.

---

**Questions?** Check the [detailed API documentation](./README_AUTH.md) or the interactive docs at http://localhost:8000/docs


## API actualizada - Noviembre 2026

### Modelos de datos

Los datos de autenticación se almacenan en `User`:
- `id`
- `email`
- `password` (hash)
- `role`
- `created_at`

Los datos personales y profesionales se almacenan en `Profile`:
- `id`
- `user_id`
- `name`
- `phone`
- `address`
- `specialization`
- `experience_years`
- `created_at`
- `updated_at`

Cada usuario recibe automáticamente un perfil al crearse.

### Autenticación y usuarios

- `POST /auth/register`: registro público con email y contraseña. El rol inicial es `user`.
- `POST /auth/login`: autenticación y obtención de token JWT.
- `POST /users/`: creación de usuarios por administradores autenticados. Solo un administrador puede asignar roles elevados.
- `GET /users/me`: consulta del usuario autenticado.

### Perfiles

Los perfiles utilizan los campos `name`, `phone`, `address`, `specialization` y `experience_years`. La modificación del perfil requiere autenticación.

### Configuración JWT

- `SECRET_KEY`: obligatoria.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: duración del token en minutos. Valor predeterminado: `1440` (24 horas).

### Pruebas

Última ejecución registrada: `4 passed`. Se registraron 15 warnings de pytest, pendientes de revisión.
