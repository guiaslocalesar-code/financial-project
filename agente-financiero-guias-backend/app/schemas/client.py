from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from datetime import datetime
from app.utils.enums import FiscalCondition

class ClientBase(BaseModel):
    company_id: UUID
    name: str = Field(..., max_length=255)
    customer_name: str | None = Field(None, max_length=255)
    customer_alias: str | None = Field(None, max_length=100)
    cuit_cuil_dni: str = Field(..., max_length=20)
    fiscal_condition: FiscalCondition
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    province: str | None = Field(None, max_length=100)
    zip_code: str | None = Field(None, max_length=10)
    imagen: str | None = None
    requires_invoice: bool = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    customer_name: str | None = None
    customer_alias: str | None = None
    cuit_cuil_dni: str | None = None
    fiscal_condition: FiscalCondition | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    province: str | None = None
    zip_code: str | None = None
    imagen: str | None = None
    requires_invoice: bool | None = None
    is_active: bool | None = None

class ClientResponse(ClientBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
