from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import SuppliersDB
from .routes import suppliers, auth, users, profiles, incidents, inventory
from .routes.suppliers import set_db as set_suppliers_db
from .dependencies import set_db
from .inventory_database import close_inventory_database, initialize_inventory_database

# Crear aplicación FastAPI
app = FastAPI(
    title="Nexova API",
    description="Complete API for Nexova Solutions with Authentication and Supplier Management",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
db = SuppliersDB()
set_db(db)
set_suppliers_db(db)

# Registrar rutas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(suppliers.router)
app.include_router(incidents.router)
app.include_router(inventory.router)

@app.on_event("startup")
def startup_inventory_database():
    initialize_inventory_database()

@app.on_event("shutdown")
def shutdown_event():
    close_inventory_database()
    db.close()

@app.get("/", tags=["health"])
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Nexova API",
        "version": "1.0.0",
        "docs": "/docs",
        "auth_endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login"
        },
        "protected_routes": {
            "users": ["POST /users/", "GET /users/ (admin)", "GET /users/me", "GET /users/{user_id}", "PUT /users/{user_id}", "DELETE /users/{user_id}"],
            "profiles": ["GET /profiles/me", "GET /profiles/{user_id}", "PUT /profiles/me", "PUT /profiles/{user_id}"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

