"""
Supplier management routes for Nexova API.
Protected routes for supplier operations (create, read, update, delete).
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from ..models import CategoryEnum, CountryEnum, SupplierCreate, SupplierRateUpdate, SupplierStatusUpdate
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

# Instancia global de BD (se inicializa en main.py)
db_instance = None

def set_db(db: SuppliersDB):
    global db_instance
    db_instance = db

@router.post("", response_model=dict, status_code=201)
def create_supplier(
    supplier: SupplierCreate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Registra un proveedor nuevo.
    
    **Protegido:** Requiere token JWT válido.
    Solo usuarios autenticados pueden crear proveedores.
    """
    return db.create_supplier(supplier)

@router.get("", response_model=List[dict])
def list_suppliers(
    country: Optional[CountryEnum] = Query(None),
    category: Optional[CategoryEnum] = Query(None),
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Lista todos los proveedores con filtros opcionales.
    
    **Protegido:** Requiere token JWT válido.
    """
    return db.get_all_suppliers(
        country=country.value if country else None,
        category=category.value if category else None,
    )

@router.get("/{supplier_id}", response_model=dict)
def get_supplier(
    supplier_id: int,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Obtiene un proveedor por ID.
    
    **Protegido:** Requiere token JWT válido.
    """
    supplier = db.get_supplier_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier

@router.patch("/{supplier_id}/rate", response_model=dict)
def update_rate(
    supplier_id: int,
    update: SupplierRateUpdate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Actualiza la tarifa de un proveedor.
    
    **Protegido:** Requiere token JWT válido.
    """
    result = db.update_rate(supplier_id, update.monthly_rate)
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.patch("/{supplier_id}/status", response_model=dict)
def update_status(
    supplier_id: int,
    update: SupplierStatusUpdate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Actualiza el estado de un proveedor.
    
    **Protegido:** Requiere token JWT válido.
    """
    result = db.update_status(supplier_id, update.status.value)
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: int,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Elimina un proveedor.
    
    **Protegido:** Requiere token JWT válido.
    """
    if not db.delete_supplier(supplier_id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
