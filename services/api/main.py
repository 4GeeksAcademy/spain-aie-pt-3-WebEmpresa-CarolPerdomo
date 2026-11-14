from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.suppliers import router as suppliers_router
from models import ProductCategory, SupplierStatus
from database import seed_suppliers

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


# Include suppliers router
app.include_router(suppliers_router)


@app.get("/suppliers/categories/list", response_model=list, tags=["Reference"])
async def get_categories():
    """Get list of valid product categories"""
    return [category.value for category in ProductCategory]


@app.get("/suppliers/status/list", response_model=list, tags=["Reference"])
async def get_statuses():
    """Get list of valid supplier statuses"""
    return [status.value for status in SupplierStatus]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
