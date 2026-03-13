from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal

class UserCompanyResponse(BaseModel):
    company_id: str
    company_name: str
    role: str
    quotaparte: Decimal
    is_active: bool

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str]
    avatar_url: Optional[str]
    companies: List[UserCompanyResponse]

    class Config:
        from_attributes = True

class UserCompanyCreate(BaseModel):
    user_email: EmailStr
    role: str = 'viewer'
    quotaparte: Decimal = Decimal('0.0')

class UserCompanyUpdate(BaseModel):
    role: Optional[str] = None
    quotaparte: Optional[Decimal] = None
    is_active: Optional[bool] = None
