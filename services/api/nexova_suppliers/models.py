from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

# ============ Auth Models ============

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class AdminUserCreate(UserCreate):
    role: RoleEnum = RoleEnum.USER

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ============ Suppliers Models ============

class CountryEnum(str, Enum):
    SPAIN = "Spain"
    USA = "USA"

class CurrencyEnum(str, Enum):
    EUR = "EUR"
    USD = "USD"

class StatusEnum(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class CategoryEnum(str, Enum):
    JOB_BOARDS = "job_boards"
    ATS_SOFTWARE = "ats_software"
    ASSESSMENT_TOOLS = "assessment_tools"
    TRAINING_PLATFORMS = "training_platforms"
    PAYROLL_AND_HR = "payroll_and_hr_software"
    VIDEO_INTERVIEW = "video_interview"
    BACKGROUND_CHECK = "background_check"
    OFFICE_AND_FACILITIES = "office_and_facilities"
    IT_AND_SOFTWARE = "it_and_software_licenses"

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1)
    country: CountryEnum
    categories: List[CategoryEnum] = Field(..., min_items=1)
    monthly_rate: float = Field(..., gt=0)
    currency: CurrencyEnum
    status: StatusEnum
    contract_renewal_date: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

    @validator('contract_renewal_date')
    def validate_date_format(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('contract_renewal_date debe estar en formato YYYY-MM-DD')
        return v

    @validator('currency')
    def validate_currency_country(cls, v, values):
        if 'country' in values:
            country = values['country']
            if country == CountryEnum.SPAIN and v != CurrencyEnum.EUR:
                raise ValueError('Spain debe usar EUR')
            if country == CountryEnum.USA and v != CurrencyEnum.USD:
                raise ValueError('USA debe usar USD')
        return v

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SupplierUpdate(BaseModel):
    monthly_rate: Optional[float] = Field(None, gt=0)
    status: Optional[StatusEnum] = None

    class Config:
        from_attributes = True
