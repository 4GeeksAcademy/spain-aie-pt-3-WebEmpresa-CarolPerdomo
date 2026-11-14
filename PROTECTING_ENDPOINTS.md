# Adding Authentication to Existing Endpoints

This guide explains how to protect existing endpoints in the Nexova API with the `get_current_user` dependency.

## Quick Start

To add authentication to any endpoint:

### Step 1: Import the Dependency

```python
from fastapi import APIRouter, Depends
from services.auth.dependencies import get_current_user

router = APIRouter()
```

### Step 2: Add `get_current_user` to Your Endpoint

```python
@router.get("/protected-endpoint")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['email']}"}
```

### Step 3: The Dependency Automatically:
- Extracts the Bearer token from `Authorization` header
- Validates the JWT signature and expiration
- Retrieves the user from the database
- Returns a 401 error if the token is missing, invalid, or expired
- Passes the user dict to your endpoint

## Available User Properties

The `current_user` dict contains:

```python
{
    "id": "uuid-string",
    "email": "user@example.com",
    "is_active": True,
    "role": "user",  # or "admin", "manager"
    "created_at": "2024-01-01T00:00:00",
    "hashed_password": "bcrypt_hash"  # (never leak this!)
}
```

## Common Patterns

### 1. Simple Protection (Any Authenticated User)

```python
@router.get("/candidates")
async def list_candidates(current_user: dict = Depends(get_current_user)):
    # Any authenticated user can access this
    return {"candidates": [...]}
```

### 2. Admin-Only Endpoint

```python
from services.auth.dependencies import get_current_admin_user

@router.delete("/candidates/{id}")
async def delete_candidate(
    id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    # Only admins can access this
    return {"deleted": id}
```

### 3. User-Specific Resource (Own Data Only)

```python
@router.get("/candidates/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Fetch candidate
    candidate = db.get_candidate(candidate_id)
    
    # Check permissions: user can only view their own, admins can view any
    if candidate["user_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    
    return candidate
```

### 4. Role-Based Access

```python
@router.post("/reports/export")
async def export_report(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers+ can export")
    
    return {"report": [...]}
```

### 5. Multiple Dependencies

```python
from fastapi import Query

@router.get("/search")
async def search(
    query: str = Query(...),
    current_user: dict = Depends(get_current_user),  # Authentication
    skip: int = Query(0),
    limit: int = Query(10)
):
    # Use current_user and other parameters
    results = db.search(query, skip, limit, user_id=current_user["id"])
    return results
```

## Error Responses

The dependency automatically returns appropriate HTTP errors:

### 401 Unauthorized (Missing or Invalid Token)

```bash
curl http://localhost:8000/protected
# Response: {"detail": "Not authenticated"}

curl -H "Authorization: Bearer invalid" http://localhost:8000/protected
# Response: {"detail": "Invalid or expired token"}
```

### 403 Forbidden (Admin-Only Endpoint)

```bash
curl -H "Authorization: Bearer user_token" http://localhost:8000/admin-only
# Response: {"detail": "You do not have permission"}
```

## Example: Protecting Candidate Endpoints

### Before (No Auth)

```python
@router.get("/candidates")
async def list_candidates():
    return db.get_all_candidates()
```

### After (Protected)

```python
@router.get("/candidates")
async def list_candidates(current_user: dict = Depends(get_current_user)):
    # Only authenticated users can list candidates
    return db.get_all_candidates()
```

### After (Admin Only)

```python
@router.get("/candidates")
async def list_candidates(current_user: dict = Depends(get_current_admin_user)):
    # Only admins can list all candidates
    return db.get_all_candidates()
```

### After (Filtered by User)

```python
@router.get("/candidates")
async def list_candidates(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        # Admins see all candidates
        return db.get_all_candidates()
    else:
        # Regular users see only their own candidates
        return db.get_candidates_by_user(current_user["id"])
```

## Testing Protected Endpoints

### Using cURL

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/candidates
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click the "Authorize" button
3. Enter: `Bearer <your_token>`
4. Click "Try it out" on any protected endpoint

## Best Practices

1. **Always include `current_user` parameter** for any endpoint that needs authentication
2. **Use specific dependencies**: `get_current_user` for any user, `get_current_admin_user` for admins
3. **Check permissions explicitly** when filtering by user ID
4. **Don't expose sensitive data**: Never return `hashed_password` in responses
5. **Log access**: Consider logging who accessed what resources
6. **Test error cases**: Ensure 401/403 responses work correctly

## Common Mistakes

### ❌ Wrong: Forgetting the Dependency

```python
@router.get("/protected")
async def endpoint():  # No authentication!
    return {"data": "secret"}
```

### ✅ Right: Adding the Dependency

```python
@router.get("/protected")
async def endpoint(current_user: dict = Depends(get_current_user)):
    return {"data": f"secret for {current_user['email']}"}
```

### ❌ Wrong: Not Checking Permissions

```python
@router.delete("/candidates/{id}")
async def delete(id: str, current_user: dict = Depends(get_current_user)):
    return db.delete_candidate(id)  # Anyone can delete any candidate!
```

### ✅ Right: Checking Permissions

```python
@router.delete("/candidates/{id}")
async def delete(id: str, current_user: dict = Depends(get_current_user)):
    candidate = db.get_candidate(id)
    if candidate["user_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return db.delete_candidate(id)
```

## Summary

Protecting endpoints with authentication is simple:

1. Add `from services.auth.dependencies import get_current_user`
2. Add `current_user: dict = Depends(get_current_user)` parameter
3. Use `current_user` to check permissions or pass info to your business logic

The authentication system handles all the complex JWT validation automatically!
