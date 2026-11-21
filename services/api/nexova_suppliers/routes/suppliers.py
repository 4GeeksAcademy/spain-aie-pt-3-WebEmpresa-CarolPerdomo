"""
Supplier management routes for Nexova API.
Protected routes for supplier operations (create, read, update, delete).
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from ..models import SupplierCreate, StatusEnum
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
    try:
        created = db.create_supplier(supplier)
        return created
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("", response_model=List[dict])
def list_suppliers(
    country: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Lista todos los proveedores con filtros opcionales.
    
    **Protegido:** Requiere token JWT válido.
    """
    return db.get_all_suppliers(country=country, category=category)

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
    update: dict,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Actualiza la tarifa de un proveedor.
    
    **Protegido:** Requiere token JWT válido.
    """
    if 'monthly_rate' not in update or update['monthly_rate'] <= 0:
        raise HTTPException(status_code=422, detail="Tarifa debe ser mayor a 0")
    
    result = db.update_rate(supplier_id, update['monthly_rate'])
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.patch("/{supplier_id}/status", response_model=dict)
def update_status(
    supplier_id: int,
    update: dict,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Actualiza el estado de un proveedor.
    
    **Protegido:** Requiere token JWT válido.
    """
    if 'status' not in update or update['status'] not in ['active', 'suspended']:
        raise HTTPException(status_code=422, detail="Estado inválido. Debe ser 'active' o 'suspended'")
    
    result = db.update_status(supplier_id, update['status'])
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
