from tinydb import TinyDB
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Database path
DB_PATH = Path(__file__).parent / "db.json"


def init_db():
    """Initialize database and ensure it exists"""
    db_path = Path(__file__).parent / "db.json"
    return TinyDB(str(db_path))


def get_db():
    """Get or create database instance"""
    if not hasattr(get_db, "_db"):
        get_db._db = init_db()
    return get_db._db


def clear_db():
    """Clear all records from database (for testing)"""
    db_instance = get_db()
    db_instance.truncate()


def seed_suppliers():
    """Seed initial suppliers from BRIEFING"""
    db_instance = get_db()

    initial_suppliers = [
        {
            "name": "TechSolutions España",
            "country": "spain",
            "categories": ["Software", "Services"],
            "daily_rate": 450.50,
            "status": "active",
            "updated_at": datetime.now().isoformat()
        },
        {
            "name": "Hardware Pro",
            "country": "spain",
            "categories": ["Hardware"],
            "daily_rate": 320.00,
            "status": "active",
            "updated_at": datetime.now().isoformat()
        },
        {
            "name": "Papelería Central",
            "country": "spain",
            "categories": ["papeleria"],
            "daily_rate": 85.00,
            "status": "active",
            "updated_at": datetime.now().isoformat()
        },
        {
            "name": "Cafetería Premium",
            "country": "spain",
            "categories": ["cafeteria"],
            "daily_rate": 150.00,
            "status": "active",
            "updated_at": datetime.now().isoformat()
        },
        {
            "name": "Servicios Integrales",
            "country": "spain",
            "categories": ["Services"],
            "daily_rate": 380.00,
            "status": "active",
            "updated_at": datetime.now().isoformat()
        }
    ]

    # Check if suppliers already exist
    if len(db_instance.all()) > 0:
        print(f"Database already has {len(db_instance.all())} records. Skipping seed.")
        return 0

    # Insert suppliers
    for supplier in initial_suppliers:
        db_instance.insert(supplier)

    print(f"✓ Seeded {len(initial_suppliers)} suppliers into database")
    return len(initial_suppliers)


def list_suppliers(country: Optional[str] = None, category: Optional[str] = None) -> List[dict]:
    """List all suppliers with optional filtering"""
    db_instance = get_db()
    suppliers = db_instance.all()

    # Filter by country if provided
    if country:
        suppliers = [s for s in suppliers if s.get("country", "").lower() == country.lower()]

    # Filter by category if provided
    if category:
        suppliers = [s for s in suppliers if category in s.get("categories", [])]

    return suppliers


def get_supplier(supplier_id: int) -> Optional[dict]:
    """Get supplier by ID"""
    db_instance = get_db()
    supplier = db_instance.get(doc_id=supplier_id)
    return supplier


def create_supplier(supplier_data: dict) -> dict:
    """Create a new supplier"""
    db_instance = get_db()
    supplier_data["updated_at"] = datetime.now().isoformat()
    supplier_id = db_instance.insert(supplier_data)
    return get_supplier(supplier_id)


def update_supplier_rate(supplier_id: int, daily_rate: float) -> Optional[dict]:
    """Update supplier daily rate"""
    db_instance = get_db()
    supplier = get_supplier(supplier_id)
    if not supplier:
        return None

    db_instance.update(
        {"updated_at": datetime.now().isoformat(), "daily_rate": daily_rate},
        doc_ids=[supplier_id]
    )
    return get_supplier(supplier_id)


def update_supplier_status(supplier_id: int, status: str) -> Optional[dict]:
    """Update supplier status"""
    db_instance = get_db()
    supplier = get_supplier(supplier_id)
    if not supplier:
        return None

    db_instance.update(
        {"status": status, "updated_at": datetime.now().isoformat()},
        doc_ids=[supplier_id]
    )
    return get_supplier(supplier_id)


def delete_supplier(supplier_id: int) -> bool:
    """Delete supplier by ID"""
    db_instance = get_db()
    supplier = get_supplier(supplier_id)
    if not supplier:
        return False

    db_instance.remove(doc_ids=[supplier_id])
    return True
