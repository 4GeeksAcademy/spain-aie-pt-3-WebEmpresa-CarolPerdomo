from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import SuppliersDB
from .routes import suppliers
from .routes.suppliers import set_db

# Crear aplicación FastAPI
app = FastAPI(
    title="Nexova Suppliers API",
    description="Lightweight Storage API para Directorio de Proveedores",
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

# Registrar rutas
app.include_router(suppliers.router)

@app.on_event("shutdown")
def shutdown_event():
    db.close()

@app.get("/", tags=["health"])
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Nexova Suppliers API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
