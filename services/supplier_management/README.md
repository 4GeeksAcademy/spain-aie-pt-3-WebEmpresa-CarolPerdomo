# Supplier Management API

A FastAPI-based REST API for managing company suppliers with Pydantic validation and TinyDB persistence.

## Features

- ✅ Supplier CRUD operations (Create, Read, Update, Delete)
- ✅ Pydantic models with strict validation
- ✅ TinyDB persistence
- ✅ Filtering by country and product category
- ✅ Rate updates with automatic timestamp tracking
- ✅ Status management (active/inactive)
- ✅ CORS enabled for frontend integration

## Tech Stack

- **FastAPI** — Modern async Python web framework
- **Pydantic** — Data validation
- **TinyDB** — Lightweight JSON database
- **UV** — Python package manager (Python 3.9+)

## Installation

```bash
# Install dependencies
uv sync

# Or if you prefer pip
pip install -r requirements.txt
```

## Running the Server

```bash
# Run with uvicorn (development)
uv run main

# Or manually
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

## Database Seeding

Seed the initial suppliers:

```bash
uv run seed
```

This loads 5 initial suppliers from the BRIEFING. If the database already has data, it skips insertion to prevent duplicates.

## API Endpoints

### Suppliers

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/suppliers` | Create a new supplier |
| **GET** | `/suppliers` | List all suppliers (supports filtering) |
| **GET** | `/suppliers/{id}` | Get supplier details by ID |
| **PATCH** | `/suppliers/{id}/rate` | Update daily rate |
| **PATCH** | `/suppliers/{id}/status` | Update status (active/inactive) |
| **DELETE** | `/suppliers/{id}` | Delete supplier |

### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/suppliers/categories/list` | List valid product categories |
| **GET** | `/suppliers/status/list` | List valid statuses |

## Query Parameters

### List Suppliers

```bash
# All suppliers
GET /suppliers

# Filter by country
GET /suppliers?country=spain

# Filter by category
GET /suppliers?category=Software

# Combine filters
GET /suppliers?country=spain&category=Services
```

## Request/Response Examples

### Create Supplier

```bash
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech",
    "country": "spain",
    "categories": ["Software", "Services"],
    "daily_rate": 500.00,
    "status": "active"
  }'
```

**Response (201):**
```json
{
  "id": 1,
  "name": "CloudTech",
  "country": "spain",
  "categories": ["Software", "Services"],
  "daily_rate": 500.0,
  "status": "active",
  "updated_at": "2024-11-14T14:43:03.308000"
}
```

### Update Rate

```bash
curl -X PATCH http://localhost:8000/suppliers/1/rate \
  -H "Content-Type: application/json" \
  -d '{"daily_rate": 550.00}'
```

### Update Status

```bash
curl -X PATCH http://localhost:8000/suppliers/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

### List with Filters

```bash
curl http://localhost:8000/suppliers?country=spain&category=Hardware
```

## Validation Rules

### Supplier Fields

- **name**: Required, non-empty string
- **country**: String (default: "spain")
- **categories**: List of valid categories (at least 1 required)
- **daily_rate**: Positive number (> 0)
- **status**: "active" or "inactive"

### Valid Categories

- Software
- Hardware
- Services
- papeleria
- cafeteria

### Valid Statuses

- active
- inactive

## Error Responses

### 404 Not Found

```json
{
  "detail": "Supplier not found"
}
```

### 422 Unprocessable Entity (Validation Error)

```json
{
  "detail": "daily_rate must be greater than zero"
}
```

## Database Schema

TinyDB stores suppliers as JSON documents:

```json
{
  "name": "TechSolutions España",
  "country": "spain",
  "categories": ["Software", "Services"],
  "daily_rate": 450.5,
  "status": "active",
  "updated_at": "2024-11-14T14:43:03.308000"
}
```

Each document gets an auto-incremented `doc_id` (returned as `id` in responses).

## Development

```bash
# Run tests
uv run pytest

# Run with auto-reload
uv run uvicorn main:app --reload

# Format code
uv run black .

# Type checking
uv run mypy main.py
```

## Environment Variables

Create a `.env` file if needed:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_PATH=./db.json
```

## License

Internal use only — Nexova Solutions
