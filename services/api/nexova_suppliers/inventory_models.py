"""SQLModel tables for inventory data stored in Supabase PostgreSQL."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class Asset(SQLModel, table=True):
    __tablename__ = "inventory_assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=160)
    sku: str = Field(sa_column=Column(String(40), unique=True, index=True, nullable=False))
    category: str = Field(max_length=40, index=True)
    office: str = Field(max_length=40, index=True)


class AssetEntry(SQLModel, table=True):
    __tablename__ = "inventory_asset_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="inventory_assets.id", index=True)
    quantity: int = Field(gt=0)
    supplier: str = Field(min_length=1, max_length=160)
    office: str = Field(max_length=40, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    user_uuid: str = Field(sa_column=Column(String(36), nullable=False, index=True))


class AssetExit(SQLModel, table=True):
    __tablename__ = "inventory_asset_exits"

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="inventory_assets.id", index=True)
    quantity: int = Field(gt=0)
    exit_type: str = Field(max_length=20, index=True)
    assigned_to: Optional[str] = Field(default=None, max_length=160)
    office: str = Field(max_length=40, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    user_uuid: str = Field(sa_column=Column(String(36), nullable=False, index=True))
