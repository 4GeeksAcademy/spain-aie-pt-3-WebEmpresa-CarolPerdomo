from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..models import SupplierCreate, StatusEnum
from ..database import SuppliersDB

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

# Instancia global de BD (se inicializa en main.py)
db_instance = None

def set_db(db: SuppliersDB):
    global db_instance
    db_instance = db

@router.post("", response_model=dict, status_code=201)
def create_supplier(supplier: SupplierCreate):
    """Registra un proveedor nuevo"""
    try:
        created = db_instance.create_supplier(supplier)
        return created
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("", response_model=List[dict])
def list_suppliers(
    country: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Lista todos los proveedores con filtros opcionales"""
    return db_instance.get_all_suppliers(country=country, category=category)

@router.get("/{supplier_id}", response_model=dict)
def get_supplier(supplier_id: int):
    """Obtiene un proveedor por ID"""
    supplier = db_instance.get_supplier_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier

@router.patch("/{supplier_id}/rate", response_model=dict)
def update_rate(supplier_id: int, update: dict):
    """Actualiza la tarifa de un proveedor"""
    if 'monthly_rate' not in update or update['monthly_rate'] <= 0:
        raise HTTPException(status_code=422, detail="Tarifa debe ser mayor a 0")
    
    result = db_instance.update_rate(supplier_id, update['monthly_rate'])
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.patch("/{supplier_id}/status", response_model=dict)
def update_status(supplier_id: int, update: dict):
    """Actualiza el estado de un proveedor"""
    if 'status' not in update or update['status'] not in ['active', 'suspended']:
        raise HTTPException(status_code=422, detail="Estado inválido. Debe ser 'active' o 'suspended'")
    
    result = db_instance.update_status(supplier_id, update['status'])
    if not result:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result

@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int):
    """Elimina un proveedor"""
    if not db_instance.delete_supplier(supplier_id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
