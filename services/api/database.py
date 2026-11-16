from tinydb import TinyDB, Query
from pathlib import Path
from datetime import datetime
from .models import Supplier, SupplierCreate, CategoryEnum, StatusEnum

DB_PATH = Path("data") / "suppliers.json"
DB_PATH.parent.mkdir(exist_ok=True)

class SuppliersDB:
    def __init__(self, db_path=DB_PATH):
        self.db = TinyDB(str(db_path))
        self.suppliers_table = self.db.table('suppliers')

    def create_supplier(self, supplier_data: SupplierCreate) -> dict:
        new_supplier = supplier_data.model_dump()
        new_supplier['updated_at'] = datetime.now().isoformat()
        doc_id = self.suppliers_table.insert(new_supplier)
        new_supplier['id'] = doc_id
        return new_supplier

    def get_all_suppliers(self, country: str = None, category: str = None) -> list:
        results = self.suppliers_table.all()
        
        if country:
            results = [s for s in results if s.get('country') == country]
        
        if category:
            results = [s for s in results if category in s.get('categories', [])]
        
        return results

    def get_supplier_by_id(self, supplier_id: int) -> dict:
        return self.suppliers_table.get(doc_id=supplier_id)

    def update_rate(self, supplier_id: int, new_rate: float) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update({'monthly_rate': new_rate, 'updated_at': datetime.now().isoformat()}, doc_ids=[supplier_id])
        return self.get_supplier_by_id(supplier_id)

    def update_status(self, supplier_id: int, new_status: str) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update({'status': new_status}, doc_ids=[supplier_id])
        return self.get_supplier_by_id(supplier_id)

    def delete_supplier(self, supplier_id: int) -> bool:
        return bool(self.suppliers_table.remove(doc_ids=[supplier_id]))

    def close(self):
        self.db.close()
