from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr


class SupplierStatus(str, Enum):
    """Valid supplier status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ProductCategory(str, Enum):
    """Valid product categories"""
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    SERVICES = "Services"
    PAPELERIA = "papeleria"
    CAFETERIA = "cafeteria"


class SupplierBase(BaseModel):
    """Base supplier model with common fields"""
    name: str = Field(..., min_length=1, description="Supplier name")
    country: str = Field(default="spain", description="Supplier country")
    categories: List[ProductCategory] = Field(..., min_items=1, description="Product categories")
    status: SupplierStatus = Field(default=SupplierStatus.ACTIVE, description="Supplier status")

    @field_validator("categories", mode="before")
    @classmethod
    def validate_categories(cls, v):
        if isinstance(v, str):
            v = [v]
        if not isinstance(v, list):
            raise ValueError("categories must be a list")
        return [
            ProductCategory(cat) if isinstance(cat, str) and not isinstance(cat, ProductCategory)
            else cat
            for cat in v
        ]


class SupplierCreate(SupplierBase):
    """Input model for creating a supplier (client sends this)"""
    daily_rate: float = Field(..., gt=0, description="Daily rate - must be positive")

    @field_validator("daily_rate")
    @classmethod
    def validate_rate(cls, v):
        if v <= 0:
            raise ValueError("daily_rate must be greater than zero")
        return v


class Supplier(SupplierBase):
    """Response model with system-generated fields"""
    id: int = Field(..., description="TinyDB auto-generated ID")
    daily_rate: float = Field(..., gt=0, description="Daily rate")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class SupplierRateUpdate(BaseModel):
    """Model for updating supplier daily rate"""
    daily_rate: float = Field(..., gt=0, description="New daily rate - must be positive")

    @field_validator("daily_rate")
    @classmethod
    def validate_rate(cls, v):
        if v <= 0:
            raise ValueError("daily_rate must be greater than zero")
        return v


class SupplierStatusUpdate(BaseModel):
    """Model for updating supplier status"""
    status: SupplierStatus = Field(..., description="New status: active or inactive")
