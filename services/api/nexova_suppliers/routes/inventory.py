"""Authenticated inventory endpoints backed by the Supabase SQLModel database."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..dependencies import get_current_user, get_db
from ..database import SuppliersDB
from ..inventory_database import get_db as get_inventory_session
from ..inventory_models import Asset, AssetEntry, AssetExit
from ..inventory_schemas import (
    AssetCreate,
    AssetEntryCreate,
    AssetEntryRead,
    AssetExitCreate,
    AssetExitRead,
    AssetRead,
    InventoryOrderRead,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _require_user_uuid(current_user: dict, auth_db: SuppliersDB) -> str:
    user_id = current_user.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authenticated user")
    user_uuid = auth_db.get_or_create_user_uuid(user_id)
    if not user_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user no longer exists")
    return user_uuid


def _stock_for(session: Session, asset_id: int, office: str) -> int:
    inbound = session.exec(
        select(func.coalesce(func.sum(AssetEntry.quantity), 0)).where(
            AssetEntry.asset_id == asset_id,
            AssetEntry.office == office,
        )
    ).one()
    outbound = session.exec(
        select(func.coalesce(func.sum(AssetExit.quantity), 0)).where(
            AssetExit.asset_id == asset_id,
            AssetExit.office == office,
        )
    ).one()
    return int(inbound or 0) - int(outbound or 0)


def _asset_response(session: Session, asset: Asset) -> AssetRead:
    return AssetRead.model_validate({
        **asset.model_dump(),
        "current_stock": _stock_for(session, asset.id, asset.office),
    })


def _require_asset_office(asset: Asset, office: str) -> None:
    if asset.office != office:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order office must match the asset office ({asset.office}).",
        )


@router.get("/products", response_model=list[AssetRead])
def list_assets(
    session: Session = Depends(get_inventory_session),
    _current_user: dict = Depends(get_current_user),
):
    return [_asset_response(session, asset) for asset in session.exec(select(Asset).order_by(Asset.id)).all()]


@router.post("/products", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    session: Session = Depends(get_inventory_session),
    _current_user: dict = Depends(get_current_user),
):
    asset = Asset(**payload.model_dump())
    session.add(asset)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An asset with this SKU already exists") from exc
    session.refresh(asset)
    return _asset_response(session, asset)


@router.get("/products/{asset_id}", response_model=AssetRead)
def get_asset(
    asset_id: int,
    session: Session = Depends(get_inventory_session),
    _current_user: dict = Depends(get_current_user),
):
    asset = session.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return _asset_response(session, asset)


@router.post("/orders/inbound", response_model=AssetEntryRead, status_code=status.HTTP_201_CREATED)
def create_inbound_order(
    payload: AssetEntryCreate,
    session: Session = Depends(get_inventory_session),
    current_user: dict = Depends(get_current_user),
    auth_db: SuppliersDB = Depends(get_db),
):
    asset = session.get(Asset, payload.asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    _require_asset_office(asset, payload.office.value)
    order = AssetEntry(
        **payload.model_dump(),
        created_at=datetime.now(timezone.utc),
        user_uuid=_require_user_uuid(current_user, auth_db),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return AssetEntryRead.model_validate(order)


@router.post("/orders/outbound", response_model=AssetExitRead, status_code=status.HTTP_201_CREATED)
def create_outbound_order(
    payload: AssetExitCreate,
    session: Session = Depends(get_inventory_session),
    current_user: dict = Depends(get_current_user),
    auth_db: SuppliersDB = Depends(get_db),
):
    # Locking the asset row serializes competing withdrawals of the same stock.
    asset = session.exec(select(Asset).where(Asset.id == payload.asset_id).with_for_update()).first()
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    _require_asset_office(asset, payload.office.value)

    available = _stock_for(session, asset.id, payload.office.value)
    if payload.quantity > available:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient stock for asset '{asset.name}'. Available: {available}, "
                f"requested: {payload.quantity}."
            ),
        )

    order = AssetExit(
        **payload.model_dump(),
        created_at=datetime.now(timezone.utc),
        user_uuid=_require_user_uuid(current_user, auth_db),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return AssetExitRead.model_validate(order)


@router.get("/orders", response_model=list[InventoryOrderRead])
def list_orders(
    session: Session = Depends(get_inventory_session),
    _current_user: dict = Depends(get_current_user),
):
    orders: list[InventoryOrderRead] = []
    entries = session.exec(
        select(AssetEntry, Asset).join(Asset, Asset.id == AssetEntry.asset_id)
    ).all()
    for entry, asset in entries:
        orders.append(InventoryOrderRead(
            id=entry.id,
            order_type="inbound",
            asset_id=entry.asset_id,
            asset_name=asset.name,
            sku=asset.sku,
            quantity=entry.quantity,
            supplier=entry.supplier,
            office=entry.office,
            created_at=entry.created_at,
            user_uuid=entry.user_uuid,
        ))

    exits = session.exec(
        select(AssetExit, Asset).join(Asset, Asset.id == AssetExit.asset_id)
    ).all()
    for exit_order, asset in exits:
        orders.append(InventoryOrderRead(
            id=exit_order.id,
            order_type="outbound",
            asset_id=exit_order.asset_id,
            asset_name=asset.name,
            sku=asset.sku,
            quantity=exit_order.quantity,
            exit_type=exit_order.exit_type,
            assigned_to=exit_order.assigned_to,
            office=exit_order.office,
            created_at=exit_order.created_at,
            user_uuid=exit_order.user_uuid,
        ))
    return sorted(orders, key=lambda order: order.created_at, reverse=True)
