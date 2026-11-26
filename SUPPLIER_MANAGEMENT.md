# Supplier Management System

Complete supplier management system for Nexova Solutions with FastAPI backend, TinyDB persistence, and React frontend.

## 📋 Overview

This system provides:

- ✅ **Backend REST API** — FastAPI with Pydantic validation
- ✅ **Database** — TinyDB for lightweight JSON persistence
- ✅ **Frontend** — React component for backoffice dashboard
- ✅ **Full CRUD operations** — Create, read, update, delete suppliers
- ✅ **Advanced filtering** — Filter by country and product category
- ✅ **Rate management** — Update daily rates with automatic timestamps
- ✅ **Status tracking** — Active/inactive supplier management

## 🏗️ Architecture

```
services/supplier_management/    # Backend API
├── main.py                       # FastAPI application
├── models.py                     # Pydantic data models
├── db.py                         # TinyDB interface & queries
├── seed.py                       # Initial data seeder
├── pyproject.toml                # Python dependencies
└── db.json                       # TinyDB database (auto-created)

uis/backoffice/                  # Frontend (Next.js)
├── app/suppliers/               # Suppliers page route
│   └── page.tsx
├── components/
│   ├── sidebar.tsx              # Navigation (updated)
│   └── supplier-directory.tsx   # Main supplier component
└── package.json
```

## 🚀 Quick Start

### Backend Setup

```bash
cd services/supplier_management

# Install dependencies
uv sync

# Run seeder (loads initial suppliers)
uv run seed

# Start API server
uv run main
```

The API will be available at `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd uis/backoffice

# Install dependencies
npm install

# Create .env.local (if needed)
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

The backoffice will be available at `http://localhost:3001`
Navigate to `/suppliers` to access the Supplier Directory

## 📊 Domain Configuration

### Valid Statuses
- `active` — Supplier is operational
- `inactive` — Supplier is suspended

### Valid Categories
- `Software`
- `Hardware`
- `Services`
- `papeleria`
- `cafeteria`

### Valid Country
- `spain` (default)

### Rate Field
- `daily_rate` — Supplier daily rate (positive number, €)

## 🔌 API Endpoints

### Create Supplier
```http
POST /suppliers
Content-Type: application/json

{
  "name": "TechSolutions",
  "country": "spain",
  "categories": ["Software", "Services"],
  "daily_rate": 500.00,
  "status": "active"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "TechSolutions",
  "country": "spain",
  "categories": ["Software", "Services"],
  "daily_rate": 500.0,
  "status": "active",
  "updated_at": "2024-11-14T14:43:03.308000"
}
```

### List Suppliers
```http
GET /suppliers
GET /suppliers?country=spain
GET /suppliers?category=Software
GET /suppliers?country=spain&category=Services
```

### Get Supplier Details
```http
GET /suppliers/{id}
```

### Update Daily Rate
```http
PATCH /suppliers/{id}/rate
Content-Type: application/json

{
  "daily_rate": 550.00
}
```

### Update Status
```http
PATCH /suppliers/{id}/status
Content-Type: application/json

{
  "status": "inactive"
}
```

### Delete Supplier
```http
DELETE /suppliers/{id}
```

### Reference Data
```http
GET /suppliers/categories/list
GET /suppliers/status/list
```

## 🗄️ Database Schema

TinyDB stores suppliers as JSON documents:

```json
{
  "id": 1,
  "name": "TechSolutions España",
  "country": "spain",
  "categories": ["Software", "Services"],
  "daily_rate": 450.5,
  "status": "active",
  "updated_at": "2024-11-14T14:43:03.308000"
}
```

Each document gets an auto-incremented `id` (from TinyDB `doc_id`).

## 📝 Validation Rules

### Supplier Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `name` | string | ✅ | Non-empty, text |
| `country` | string | ❌ | Default: "spain" |
| `categories` | array | ✅ | Min 1, valid category values |
| `daily_rate` | number | ✅ | Must be > 0 |
| `status` | enum | ❌ | "active" or "inactive" |

### Error Responses

**404 Not Found:**
```json
{
  "detail": "Supplier not found"
}
```

**422 Unprocessable Entity (Validation):**
```json
{
  "detail": "daily_rate must be greater than zero"
}
```

## 🎨 Frontend Features

The backoffice Supplier Directory includes:

- **Supplier Directory Table** — View all suppliers with key information
- **Registration Form** — Add new suppliers with validation
- **Filtering** — Filter by country and product category in real-time
- **Rate Management** — Inline editing of daily rates
- **Status Control** — Toggle between active/inactive
- **Delete Action** — Remove suppliers with confirmation
- **Visual Indicators** — Status badges, category tags, loading states
- **Error Handling** — User-friendly error messages

## 🔄 Data Flow

1. **User submits form** in backoffice
2. **Validation** in React component
3. **API request** to FastAPI backend
4. **Pydantic validation** rejects invalid data with 422
5. **Database operation** in TinyDB
6. **Response** with created/updated supplier
7. **Frontend update** — table refreshes with new data
8. **UI feedback** — success message or error display

## 🧪 Testing

### API Testing with curl

```bash
# Create supplier
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech",
    "country": "spain",
    "categories": ["Software"],
    "daily_rate": 400.00,
    "status": "active"
  }'

# List suppliers
curl http://localhost:8000/suppliers

# Get supplier
curl http://localhost:8000/suppliers/1

# Update rate
curl -X PATCH http://localhost:8000/suppliers/1/rate \
  -H "Content-Type: application/json" \
  -d '{"daily_rate": 450.00}'

# Update status
curl -X PATCH http://localhost:8000/suppliers/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'

# Delete supplier
curl -X DELETE http://localhost:8000/suppliers/1
```

### Initial Data

Running `uv run seed` creates these 5 suppliers:

1. **TechSolutions España** — Software, Services (€450.50/day)
2. **Hardware Pro** — Hardware (€320/day)
3. **Papelería Central** — papeleria (€85/day)
4. **Cafetería Premium** — cafeteria (€150/day)
5. **Servicios Integrales** — Services (€380/day)

## 📁 Directory Structure

```
/services/supplier_management/
├── __init__.py
├── main.py                    # FastAPI app + endpoints
├── models.py                  # Pydantic models
├── db.py                      # Database layer
├── seed.py                    # Seeder script
├── pyproject.toml             # Dependencies
├── README.md                  # This file
└── db.json                    # Auto-created TinyDB

/uis/backoffice/
├── app/
│   └── suppliers/
│       └── page.tsx           # Suppliers page
├── components/
│   ├── sidebar.tsx            # Nav with suppliers link
│   └── supplier-directory.tsx # Main UI component
├── package.json
└── README.md
```

## 🔐 Security Notes

- CORS is enabled for all origins (configure for production)
- Input validation at multiple levels (Pydantic + frontend)
- No authentication implemented (add auth middleware for production)
- No rate limiting (add rate limiter for production)
- Database file not committed (in .gitignore)

## 🚧 Future Enhancements

- Authentication & authorization
- Role-based access control (RBAC)
- Audit logging for supplier changes
- Export to CSV/PDF
- Bulk operations
- Advanced search
- API rate limiting
- Database backup automation
- Email notifications on status changes

## 📖 Documentation

- **Backend**: See `services/supplier_management/README.md`
- **API Docs**: Run server and visit `/docs` for interactive Swagger UI
- **Frontend**: Component uses standard React patterns

## 🤝 Contributing

Follow these patterns when extending:

1. **Backend changes** → Update `models.py` and `db.py`, then `main.py`
2. **Frontend changes** → Maintain component separation, use hooks properly
3. **Database changes** → Create migration scripts in seed pattern
4. **Add tests** → Use pytest for backend, testing library for frontend

## 📞 Support

For issues or questions:
- Check API docs at `http://localhost:8000/docs`
- Review backend README: `services/supplier_management/README.md`
- Check validation errors in browser console

---

**Last Updated:** November 2024  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
