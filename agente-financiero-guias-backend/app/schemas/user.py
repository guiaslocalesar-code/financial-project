from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any
from app.utils.enums import CompanyRole

class UserBase(BaseModel):
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    google_id: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    google_id: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCompanyBase(BaseModel):
    role: CompanyRole = CompanyRole.USER
    permissions: Optional[List[str]] = None
    quotaparte: Optional[float] = None
    is_active: bool = True

class UserCompanyCreate(UserCompanyBase):
    user_id: UUID
    company_id: UUID

class UserCompanyInvite(BaseModel):
    email: EmailStr
    role: CompanyRole = CompanyRole.USER
    permissions: Optional[List[str]] = None
    quotaparte: Optional[float] = None


class UserCompanyUpdate(BaseModel):
    role: Optional[CompanyRole] = None
    permissions: Optional[List[str]] = None
    quotaparte: Optional[float] = None
    is_active: Optional[bool] = None

class UserCompanyResponse(UserCompanyBase):
    id: UUID
    user_id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
