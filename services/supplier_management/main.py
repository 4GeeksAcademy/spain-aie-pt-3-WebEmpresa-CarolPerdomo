from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional, List
from models import (
    Supplier, SupplierCreate, SupplierRateUpdate, SupplierStatusUpdate,
    SupplierStatus, ProductCategory
)
from db import (
    list_suppliers, get_supplier, create_supplier, update_supplier_rate,
    update_supplier_status, delete_supplier, seed_suppliers
)

app = FastAPI(
    title="Supplier Management API",
    description="API for managing company suppliers",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    seed_suppliers()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"message": "Supplier Management API is running", "status": "ok"}


@app.post("/suppliers", response_model=dict, status_code=201, tags=["Suppliers"])
async def create_new_supplier(supplier: SupplierCreate):
    """
    Register a new supplier.
    
    Returns the created supplier with its ID assigned by TinyDB.
    Rejects invalid entries with 422.
    """
    try:
        # Convert Pydantic model to dict
        supplier_dict = {
            "name": supplier.name,
            "country": supplier.country,
            "categories": [cat.value for cat in supplier.categories],
            "daily_rate": supplier.daily_rate,
            "status": supplier.status.value,
            "updated_at": datetime.now().isoformat()
        }

        # Create supplier in database
        created = create_supplier(supplier_dict)

        return {
            "id": created.doc_id,
            **created
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/suppliers", response_model=List[dict], tags=["Suppliers"])
async def list_all_suppliers(
    country: Optional[str] = Query(None, description="Filter by country"),
    category: Optional[str] = Query(None, description="Filter by product category")
):
    """
    List all suppliers with optional filtering.
    
    Query parameters:
    - country: Filter by country (case-insensitive)
    - category: Filter by product category
    """
    suppliers = list_suppliers(country=country, category=category)

    # Format response with doc_id as 'id'
    return [
        {
            "id": supplier.doc_id,
            **{k: v for k, v in supplier.items() if k != "doc_id"}
        }
        for supplier in suppliers
    ]


@app.get("/suppliers/{supplier_id}", response_model=dict, tags=["Suppliers"])
async def get_supplier_details(supplier_id: int):
    """
    Get supplier details by ID.
    
    Returns 404 if supplier does not exist.
    """
    supplier = get_supplier(supplier_id)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {
        "id": supplier.doc_id,
        **{k: v for k, v in supplier.items() if k != "doc_id"}
    }


@app.patch("/suppliers/{supplier_id}/rate", response_model=dict, tags=["Suppliers"])
async def update_rate(supplier_id: int, rate_update: SupplierRateUpdate):
    """
    Update supplier daily rate.
    
    Automatically registers updated_at with the current timestamp.
    Does not accept rates equal to or less than zero.
    """
    if rate_update.daily_rate <= 0:
        raise HTTPException(status_code=422, detail="daily_rate must be greater than zero")

    supplier = update_supplier_rate(supplier_id, rate_update.daily_rate)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {
        "id": supplier.doc_id,
        **{k: v for k, v in supplier.items() if k != "doc_id"}
    }


@app.patch("/suppliers/{supplier_id}/status", response_model=dict, tags=["Suppliers"])
async def update_status(supplier_id: int, status_update: SupplierStatusUpdate):
    """
    Update supplier status (active or inactive).
    
    Only accepts valid status values defined in the domain.
    """
    supplier = update_supplier_status(supplier_id, status_update.status.value)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {
        "id": supplier.doc_id,
        **{k: v for k, v in supplier.items() if k != "doc_id"}
    }


@app.delete("/suppliers/{supplier_id}", status_code=204, tags=["Suppliers"])
async def remove_supplier(supplier_id: int):
    """
    Delete a supplier from the directory.
    
    Returns 404 if the ID does not exist.
    """
    if not delete_supplier(supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")

    return None


@app.get("/suppliers/categories/list", response_model=List[str], tags=["Reference"])
async def get_categories():
    """Get list of valid product categories"""
    return [category.value for category in ProductCategory]


@app.get("/suppliers/status/list", response_model=List[str], tags=["Reference"])
async def get_statuses():
    """Get list of valid supplier statuses"""
    return [status.value for status in SupplierStatus]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
