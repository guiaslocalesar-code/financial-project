from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import ServiceStatus

class ClientServiceBase(BaseModel):
    client_id: str
    service_id: str
    monthly_fee: float
    currency: str = "ARS"
    start_date: date
    end_date: date | None = None
    status: ServiceStatus = ServiceStatus.ACTIVE

class ClientServiceCreate(ClientServiceBase):
    pass

class ClientServiceUpdate(BaseModel):
    monthly_fee: float | None = None
    status: ServiceStatus | None = None
    end_date: date | None = None

class ClientServiceResponse(ClientServiceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
