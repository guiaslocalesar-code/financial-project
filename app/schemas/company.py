from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.utils.enums import FiscalCondition

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    cuit: str = Field(..., max_length=13)
    fiscal_condition: FiscalCondition
    afip_point_of_sale: int | None = None

class CompanyCreate(CompanyBase):
    afip_cert: str | None = None
    afip_key: str | None = None

class CompanyUpdate(BaseModel):
    name: str | None = None
    cuit: str | None = None
    fiscal_condition: FiscalCondition | None = None
    afip_cert: str | None = None
    afip_key: str | None = None
    afip_point_of_sale: int | None = None
    is_active: bool | None = None

class CompanyResponse(CompanyBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
