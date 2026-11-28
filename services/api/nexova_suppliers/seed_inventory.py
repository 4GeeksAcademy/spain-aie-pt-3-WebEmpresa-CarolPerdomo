"""Seed the minimum inventory dataset without duplicating existing rows."""

from sqlmodel import Session, select

from .config import load_project_env
from .database import SuppliersDB
from .inventory_database import get_inventory_engine, initialize_inventory_database
from .inventory_models import Asset, AssetEntry, AssetExit


ASSETS = [
    {"name": 'Portátil 14" Business', "sku": "NXV-IT-001", "category": "hardware", "office": "Valencia"},
    {"name": 'Portátil 14" Business', "sku": "NXV-IT-002", "category": "hardware", "office": "Miami"},
    {"name": "Ratón ergonómico", "sku": "NXV-PER-001", "category": "peripherals", "office": "Valencia"},
    {"name": "Hub USB-C", "sku": "NXV-PER-002", "category": "peripherals", "office": "Miami"},
    {"name": "Resma de papel A4", "sku": "NXV-OFF-001", "category": "office_supplies", "office": "Valencia"},
    {"name": "Cuaderno de formación en liderazgo", "sku": "NXV-TRN-001", "category": "training_materials", "office": "Valencia"},
]

ENTRIES = [
    ("NXV-IT-001", 10, "TechDistrib Valencia S.L.", "Valencia"),
    ("NXV-IT-001", 5, "TechDistrib Valencia S.L.", "Valencia"),
    ("NXV-PER-002", 8, "Office Depot Miami", "Miami"),
    ("NXV-OFF-001", 12, "Office Depot Valencia", "Valencia"),
]

EXITS = [
    ("NXV-IT-001", 2, "allocation", "Empleado de prueba", "Valencia"),
    ("NXV-PER-002", 1, "allocation", "Empleado de prueba", "Miami"),
    ("NXV-OFF-001", 3, "consumption", None, "Valencia"),
]


def seed_inventory() -> None:
    load_project_env()
    if not initialize_inventory_database():
        raise RuntimeError("Set DATABASE_URL to the Supabase transaction-pooler URI before seeding inventory.")

    auth_db = SuppliersDB()
    try:
        users = auth_db.get_all_users()
        if not users:
            raise RuntimeError("Register an API user before seeding orders so each one can reference a TinyDB UUID.")
        user_uuid = auth_db.get_or_create_user_uuid(users[0]["id"])

        with Session(get_inventory_engine()) as session:
            assets_by_sku: dict[str, Asset] = {}
            for asset_data in ASSETS:
                asset = session.exec(select(Asset).where(Asset.sku == asset_data["sku"])).first()
                if asset is None:
                    asset = Asset(**asset_data)
                    session.add(asset)
                    session.flush()
                assets_by_sku[asset_data["sku"]] = asset

            for sku, quantity, supplier, office in ENTRIES:
                asset = assets_by_sku[sku]
                existing = session.exec(
                    select(AssetEntry).where(
                        AssetEntry.asset_id == asset.id,
                        AssetEntry.quantity == quantity,
                        AssetEntry.supplier == supplier,
                        AssetEntry.office == office,
                    )
                ).first()
                if existing is None:
                    session.add(AssetEntry(
                        asset_id=asset.id,
                        quantity=quantity,
                        supplier=supplier,
                        office=office,
                        user_uuid=user_uuid,
                    ))

            for sku, quantity, exit_type, assigned_to, office in EXITS:
                asset = assets_by_sku[sku]
                existing = session.exec(
                    select(AssetExit).where(
                        AssetExit.asset_id == asset.id,
                        AssetExit.quantity == quantity,
                        AssetExit.exit_type == exit_type,
                        AssetExit.assigned_to == assigned_to,
                        AssetExit.office == office,
                    )
                ).first()
                if existing is None:
                    session.add(AssetExit(
                        asset_id=asset.id,
                        quantity=quantity,
                        exit_type=exit_type,
                        assigned_to=assigned_to,
                        office=office,
                        user_uuid=user_uuid,
                    ))
            session.commit()
    finally:
        auth_db.close()


if __name__ == "__main__":
    seed_inventory()
    print("Inventory seed completed.")
