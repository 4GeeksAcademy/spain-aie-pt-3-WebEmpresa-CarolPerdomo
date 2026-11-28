"""Validated API schemas for inventory requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InventoryCategory(str, Enum):
    HARDWARE = "hardware"
    PERIPHERALS = "peripherals"
    OFFICE_SUPPLIES = "office_supplies"
    TRAINING_MATERIALS = "training_materials"


class Office(str, Enum):
    VALENCIA = "Valencia"
    MIAMI = "Miami"


class ExitType(str, Enum):
    ALLOCATION = "allocation"
    CONSUMPTION = "consumption"


class AssetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    sku: str = Field(min_length=1, max_length=40)
    category: InventoryCategory
    office: Office


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    category: InventoryCategory
    office: Office
    current_stock: int


class AssetEntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    supplier: str = Field(min_length=1, max_length=160)
    office: Office


class AssetEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    quantity: int
    supplier: str
    office: Office
    created_at: datetime
    user_uuid: UUID


class AssetExitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    exit_type: ExitType
    assigned_to: Optional[str] = Field(default=None, max_length=160)
    office: Office

    @model_validator(mode="after")
    def validate_assignee(self):
        if self.exit_type == ExitType.ALLOCATION and not (self.assigned_to or "").strip():
            raise ValueError("assigned_to is required when exit_type is allocation")
        if self.exit_type == ExitType.CONSUMPTION and self.assigned_to is not None:
            raise ValueError("assigned_to must be null when exit_type is consumption")
        return self


class AssetExitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    quantity: int
    exit_type: ExitType
    assigned_to: Optional[str]
    office: Office
    created_at: datetime
    user_uuid: UUID


class InventoryOrderRead(BaseModel):
    id: int
    order_type: Literal["inbound", "outbound"]
    asset_id: int
    asset_name: str
    sku: str
    quantity: int
    supplier: Optional[str] = None
    exit_type: Optional[ExitType] = None
    assigned_to: Optional[str] = None
    office: Office
    created_at: datetime
    user_uuid: UUID
