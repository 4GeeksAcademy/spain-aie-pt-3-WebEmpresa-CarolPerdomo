import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest
os.environ.setdefault("SECRET_KEY", "test-only-inventory-key-longer-than-32-bytes")

from fastapi import HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.inventory_models import Asset, AssetEntry, AssetExit
from nexova_suppliers.inventory_schemas import AssetCreate, AssetEntryCreate, AssetExitCreate, AssetEntryRead, AssetExitRead
from nexova_suppliers.seed_inventory import ASSETS, ENTRIES, EXITS
from nexova_suppliers.routes.inventory import (
    create_asset,
    create_inbound_order,
    create_outbound_order,
    get_asset,
    list_orders,
)


@pytest.fixture
def inventory_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            yield session
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


class FakeAuthDatabase:
    def __init__(self):
        self.user_uuid = str(uuid4())

    def get_or_create_user_uuid(self, user_id):
        assert user_id == 17
        return self.user_uuid


def test_orders_calculate_stock_and_reject_negative_balance(inventory_session):
    session = inventory_session
    auth_db = FakeAuthDatabase()
    user = {"user_id": 17}

    asset = create_asset(
        AssetCreate(name="Portátil de prueba", sku="TEST-IT-001", category="hardware", office="Valencia"),
        session,
        user,
    )
    assert asset.current_stock == 0

    inbound = create_inbound_order(
        AssetEntryCreate(asset_id=asset.id, quantity=5, supplier="Proveedor de prueba", office="Valencia"),
        session,
        user,
        auth_db,
    )
    assert isinstance(inbound, AssetEntryRead)
    assert str(inbound.user_uuid) == auth_db.user_uuid

    outbound = create_outbound_order(
        AssetExitCreate(
            asset_id=asset.id,
            quantity=2,
            exit_type="allocation",
            assigned_to="Empleado de prueba",
            office="Valencia",
        ),
        session,
        user,
        auth_db,
    )
    assert isinstance(outbound, AssetExitRead)
    assert str(outbound.user_uuid) == auth_db.user_uuid
    assert get_asset(asset.id, session, user).current_stock == 3

    with pytest.raises(HTTPException) as error:
        create_outbound_order(
            AssetExitCreate(
                asset_id=asset.id,
                quantity=4,
                exit_type="consumption",
                office="Valencia",
            ),
            session,
            user,
            auth_db,
        )
    assert error.value.status_code == 400
    assert error.value.detail == "Insufficient stock for asset 'Portátil de prueba'. Available: 3, requested: 4."
    assert len(session.exec(select(AssetExit)).all()) == 1

    orders = list_orders(session, user)
    assert len(orders) == 2
    assert all(str(order.user_uuid) == auth_db.user_uuid for order in orders)


def test_order_office_must_match_asset_office(inventory_session):
    session = inventory_session
    auth_db = FakeAuthDatabase()
    user = {"user_id": 17}
    asset = create_asset(
        AssetCreate(name="Hub de prueba", sku="TEST-PER-001", category="peripherals", office="Miami"),
        session,
        user,
    )

    with pytest.raises(HTTPException) as error:
        create_inbound_order(
            AssetEntryCreate(asset_id=asset.id, quantity=2, supplier="Proveedor de prueba", office="Valencia"),
            session,
            user,
            auth_db,
        )
    assert error.value.status_code == 400
    assert session.exec(select(AssetEntry)).all() == []
    assert session.exec(select(Asset).where(Asset.id == asset.id)).one().office == "Miami"


def test_allocation_requires_assignee_and_consumption_forbids_one():
    with pytest.raises(ValueError):
        AssetExitCreate(asset_id=1, quantity=1, exit_type="allocation", office="Valencia")
    with pytest.raises(ValueError):
        AssetExitCreate(
            asset_id=1,
            quantity=1,
            exit_type="consumption",
            assigned_to="Empleado de prueba",
            office="Valencia",
        )


def test_seed_meets_minimum_counts_and_keeps_office_stock_nonnegative():
    assets_by_sku = {asset["sku"]: asset for asset in ASSETS}
    assert len(assets_by_sku) >= 6
    assert len(ENTRIES) >= 4
    assert len(EXITS) >= 3

    stock_by_sku = {sku: 0 for sku in assets_by_sku}
    for sku, quantity, _supplier, office in ENTRIES:
        assert office == assets_by_sku[sku]["office"]
        stock_by_sku[sku] += quantity
    for sku, quantity, exit_type, assigned_to, office in EXITS:
        assert office == assets_by_sku[sku]["office"]
        assert exit_type in {"allocation", "consumption"}
        assert bool(assigned_to) if exit_type == "allocation" else assigned_to is None
        stock_by_sku[sku] -= quantity
        assert stock_by_sku[sku] >= 0


def test_tinydb_user_uuid_is_valid_and_persistent():
    db_path = Path(__file__).resolve().parents[1] / "data" / f"inventory-uuid-test-{uuid4().hex}.json"
    db = SuppliersDB(db_path)
    try:
        user = db.create_user(f"{uuid4().hex}@example.test", "test-password-123")
        user_uuid = db.get_or_create_user_uuid(user["id"])
        UUID(user_uuid)
        db.close()

        reopened = SuppliersDB(db_path)
        try:
            assert reopened.get_or_create_user_uuid(user["id"]) == user_uuid
        finally:
            reopened.close()
    finally:
        db.close()
        db_path.unlink(missing_ok=True)
