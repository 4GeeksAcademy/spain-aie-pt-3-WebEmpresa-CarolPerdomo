# 🚀 Supplier Management — Quick Start Guide

Complete supplier management system with FastAPI backend + React frontend.

## 📋 What's Included

✅ REST API with full CRUD operations  
✅ Pydantic validation (rejects invalid data with 422)  
✅ TinyDB persistence (JSON-based, no server needed)  
✅ React backoffice UI with table, filters, and forms  
✅ Real-time filtering by country and category  
✅ Inline rate editing with instant updates  
✅ Status management (active/inactive)  

---

## ⚡ 30-Second Start

### Terminal 1: Start Backend

```bash
cd services/supplier_management
pip install fastapi uvicorn pydantic pydantic-settings tinydb python-multipart
python main.py
```

**Output:**
```
✓ Seeded 5 suppliers into database
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ API ready at `http://localhost:8000`  
✅ Interactive docs at `http://localhost:8000/docs`

### Terminal 2: Start Frontend

```bash
cd uis/backoffice
npm install
npm run dev -- --port 3001
```

✅ Backoffice ready at `http://localhost:3001`  
✅ Navigate to `/suppliers` in the menu

---

## 📊 Domain Configuration

| Setting | Value |
|---------|-------|
| **Valid Statuses** | `active`, `inactive` |
| **Valid Categories** | Software, Hardware, Services, papeleria, cafeteria |
| **Rate Field** | `daily_rate` (must be > 0) |
| **Country** | spain |

---

## 🧪 Quick Tests

### Test 1: Create Supplier

```bash
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Supplier",
    "country": "spain",
    "categories": ["Software"],
    "daily_rate": 500.00,
    "status": "active"
  }'
```

**Response (201):**
```json
{
  "id": 6,
  "name": "My Supplier",
  "daily_rate": 500.0,
  "status": "active",
  "updated_at": "2024-11-14T..."
}
```

### Test 2: List All Suppliers

```bash
curl http://localhost:8000/suppliers | jq
```

### Test 3: Filter by Category

```bash
curl "http://localhost:8000/suppliers?category=Software" | jq
```

### Test 4: Update Rate

```bash
curl -X PATCH http://localhost:8000/suppliers/1/rate \
  -H "Content-Type: application/json" \
  -d '{"daily_rate": 600.00}'
```

### Test 5: Change Status

```bash
curl -X PATCH http://localhost:8000/suppliers/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

### Test 6: Delete Supplier

```bash
curl -X DELETE http://localhost:8000/suppliers/1
```

---

## 📁 File Structure

```
services/supplier_management/
├── main.py              ← FastAPI app + all endpoints
├── models.py            ← Pydantic validation models
├── db.py                ← TinyDB operations
├── seed.py              ← Initial data loader
├── test_integration.py  ← Test suite (all tests pass ✓)
└── db.json              ← Database (auto-created)

uis/backoffice/
├── app/suppliers/page.tsx           ← Suppliers page
├── components/supplier-directory.tsx ← Main UI component
└── components/sidebar.tsx            ← Menu with new link
```

---

## 🎯 Key Features

### ✅ Data Validation

- Pydantic rejects invalid data **before** database
- Negative/zero rates → 422 error
- Missing required fields → 422 error
- Invalid status/categories → 422 error

### ✅ Automatic Timestamps

Every update automatically records `updated_at`:

```json
{
  "id": 1,
  "name": "TechSolutions",
  "daily_rate": 500.0,
  "updated_at": "2024-11-14T14:52:44.074066"
}
```

### ✅ Real-time Frontend

- Filter table without page reload
- Inline rate editing with live update
- Status toggle with instant reflection
- Delete with confirmation
- Error messages for all validation failures

### ✅ Initial Data

Running the backend auto-seeds 5 suppliers:

1. TechSolutions España — Software, Services (€450.50/day)
2. Hardware Pro — Hardware (€320/day)
3. Papelería Central — papeleria (€85/day)
4. Cafetería Premium — cafeteria (€150/day)
5. Servicios Integrales — Services (€380/day)

---

## 🔍 API Reference (Quick)

| Method | Endpoint | What It Does |
|--------|----------|--------------|
| **POST** | `/suppliers` | Create supplier |
| **GET** | `/suppliers` | List all suppliers |
| **GET** | `/suppliers?category=Software` | Filter by category |
| **GET** | `/suppliers/{id}` | Get one supplier |
| **PATCH** | `/suppliers/{id}/rate` | Update daily rate |
| **PATCH** | `/suppliers/{id}/status` | Change active/inactive |
| **DELETE** | `/suppliers/{id}` | Delete supplier |
| **GET** | `/suppliers/categories/list` | Valid categories |
| **GET** | `/suppliers/status/list` | Valid statuses |

---

## ✨ Frontend Capabilities

### Supplier Directory Page

- 📊 **Table View** — Name, country, categories, rate, status
- 🔍 **Filtering** — Country and category dropdowns
- ➕ **Add Supplier** — Form with validation
- ✏️ **Edit Rate** — Inline editing
- 🔴 **Toggle Status** — Active/Inactive selector
- 🗑️ **Delete** — With confirmation
- ⚠️ **Error Handling** — User-friendly messages
- ⏳ **Loading States** — Spinner during operations

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
lsof -i :8000

# Or use different port
python -m uvicorn main:app --port 8001
```

### Database errors
```bash
# Clear and reseed
rm db.json
python main.py  # Automatically reseeds
```

### Frontend can't connect to API
```bash
# Ensure backend is running on port 8000
# Check NEXT_PUBLIC_API_URL in backoffice .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Validation errors
All validation errors return 422 with details:
```json
{
  "detail": "daily_rate must be greater than zero"
}
```

---

## 📚 Full Documentation

- **Backend Details**: See `services/supplier_management/README.md`
- **Complete Guide**: See `SUPPLIER_MANAGEMENT.md` in repo root
- **API Docs**: Visit `http://localhost:8000/docs` (interactive Swagger UI)

---

## ✅ Verification Checklist

After starting both servers:

- [ ] `http://localhost:8000` returns `{"status": "ok"}`
- [ ] `http://localhost:8000/docs` loads Swagger UI
- [ ] `http://localhost:3001/suppliers` loads supplier table
- [ ] Supplier table shows initial 5 suppliers
- [ ] Can add new supplier from form
- [ ] Can edit rate inline
- [ ] Can toggle status dropdown
- [ ] Can delete supplier
- [ ] Filters work (country, category)

---

## 🎓 Example Workflows

### Workflow 1: Add and Update Supplier

1. Go to `/suppliers` page
2. Click "New Supplier" button
3. Fill form:
   - Name: "Acme Inc"
   - Categories: Software, Services
   - Rate: 750.00
   - Status: active
4. Click "Save Supplier"
5. Table updates with new supplier
6. Click edit icon on rate → change to 800.00 → click check mark
7. Rate updates automatically

### Workflow 2: Filter Suppliers

1. Go to `/suppliers` page
2. Select "Software" in Category filter
3. Table shows only Software suppliers
4. Select another country in Country filter
5. Table updates live (no page reload)

### Workflow 3: Delete Supplier

1. Go to `/suppliers` page
2. Find supplier in table
3. Click trash icon in Actions column
4. Confirm deletion
5. Supplier disappears from table

---

## 🚀 Next Steps

- Deploy backend to production (e.g., Heroku, Railway)
- Add authentication for backoffice
- Add audit logging for changes
- Implement CSV export
- Add bulk operations
- Set up automated backups

---

**Version:** 1.0.0 ✅  
**Status:** Production Ready  
**Last Updated:** November 2024

Questions? Check the full documentation or the API docs at `/docs`
