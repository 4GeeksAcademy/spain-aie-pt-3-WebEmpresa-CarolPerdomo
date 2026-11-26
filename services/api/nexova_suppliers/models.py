from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime
from nexova_shared.incident_csv import (
    INCIDENT_BRANCHES,
    INCIDENT_CATEGORIES,
    INCIDENT_ORIGINS,
    INCIDENT_STATUSES,
    validate_incident_field,
)

# ============ Auth Models ============

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=8)

class AdminUserCreate(UserCreate):
    role: RoleEnum = RoleEnum.USER

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    created_at: datetime

class UserUpdate(BaseModel):
    """Fields editable on a user account; profile details stay on Profile."""
    model_config = ConfigDict(extra="forbid")

    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None

class ProfileCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(..., min_length=32, max_length=200)
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

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
    categories: List[CategoryEnum] = Field(..., min_length=1)
    monthly_rate: float = Field(..., gt=0)
    currency: CurrencyEnum
    status: StatusEnum
    contract_renewal_date: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('contract_renewal_date')
    @classmethod
    def validate_date_format(cls, value):
        if value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise ValueError('contract_renewal_date debe estar en formato YYYY-MM-DD')
        return value

    @model_validator(mode="after")
    def validate_currency_country(self):
        if self.country == CountryEnum.SPAIN and self.currency != CurrencyEnum.EUR:
            raise ValueError('Spain debe usar EUR')
        if self.country == CountryEnum.USA and self.currency != CurrencyEnum.USD:
            raise ValueError('USA debe usar USD')
        return self

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: Optional[datetime] = None

class SupplierUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monthly_rate: Optional[float] = Field(None, gt=0)
    status: Optional[StatusEnum] = None


# ============ Incident Management Models ============

class IncidentStatusEnum(str, Enum):
    OPEN = INCIDENT_STATUSES[0]
    IN_PROGRESS = INCIDENT_STATUSES[1]
    RESOLVED = INCIDENT_STATUSES[2]
    DISCARDED = INCIDENT_STATUSES[3]


class IncidentOriginEnum(str, Enum):
    CUSTOMER = INCIDENT_ORIGINS[0]
    BRANCH = INCIDENT_ORIGINS[1]
    INTERNAL = INCIDENT_ORIGINS[2]


class IncidentBranchEnum(str, Enum):
    CENTRAL = INCIDENT_BRANCHES[0]
    VALENCIA_OPERATIONS = INCIDENT_BRANCHES[1]
    MIAMI_OFFICE = INCIDENT_BRANCHES[2]
    REMOTE = INCIDENT_BRANCHES[3]


class IncidentCategoryEnum(str, Enum):
    TECHNICAL_FAILURE = INCIDENT_CATEGORIES[0]
    PROCESS_ERROR = INCIDENT_CATEGORIES[1]
    CLIENT_COMPLAINT = INCIDENT_CATEGORIES[2]
    CANDIDATE_ISSUE = INCIDENT_CATEGORIES[3]
    STAFF_ISSUE = INCIDENT_CATEGORIES[4]
    SLA_BREACH = INCIDENT_CATEGORIES[5]
    DATA_QUALITY = INCIDENT_CATEGORIES[6]
    OTHER = INCIDENT_CATEGORIES[7]


class IncidentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1)
    category: IncidentCategoryEnum
    status: IncidentStatusEnum
    origin: IncidentOriginEnum
    branch: IncidentBranchEnum

    @field_validator("title")
    @classmethod
    def require_title(cls, value):
        message = validate_incident_field("title", value)
        if message:
            raise ValueError(message)
        return value

    @field_validator("description")
    @classmethod
    def require_description(cls, value):
        message = validate_incident_field("description", value)
        if message:
            raise ValueError(message)
        return value


class Incident(IncidentCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class IncidentStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: IncidentStatusEnum
