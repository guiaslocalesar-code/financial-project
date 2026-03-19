from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class ServiceBase(BaseModel):
    company_id: UUID
    name: str = Field(..., max_length=100)
    description: str | None = None
    icon: str | None = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    is_active: bool | None = None

class ServiceResponse(ServiceBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
