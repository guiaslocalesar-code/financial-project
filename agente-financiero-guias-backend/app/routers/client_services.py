from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from app.database import get_db
from app.models.client_service import ClientService
from app.schemas.client_service import ClientServiceCreate, ClientServiceResponse, ClientServiceUpdate

router = APIRouter(prefix="/client-services", tags=["Client Services"])

# Local schema for this endpoint to include service data
from pydantic import BaseModel

class ServiceShort(BaseModel):
    id: str
    name: str

class ClientServiceWithService(ClientServiceResponse):
    service: ServiceShort | None = None

@router.get("/{client_id}", response_model=list[ClientServiceWithService])
async def get_client_services(client_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClientService)
        .options(joinedload(ClientService.service))
        .where(ClientService.client_id == client_id)
    )
    return result.scalars().all()

from datetime import date
from app.utils.enums import ServiceStatus

class ClientServiceAssign(BaseModel):
    service_id: str
    monthly_fee: float
    currency: str = "ARS"
    start_date: date

@router.post("/{client_id}", response_model=ClientServiceResponse)
async def assign_service(client_id: str, service_in: ClientServiceAssign, db: AsyncSession = Depends(get_db)):
    cs = ClientService(
        client_id=client_id,
        **service_in.model_dump()
    )
    db.add(cs)
    await db.commit()
    await db.refresh(cs)
    return cs

@router.put("/item/{id}", response_model=ClientServiceResponse)
async def update_service(id: UUID, service_in: ClientServiceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClientService).where(ClientService.id == id))
    cs = result.scalar_one_or_none()
    if not cs:
        raise HTTPException(status_code=404, detail="Client service not found")
    
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cs, field, value)
        
    await db.commit()
    await db.refresh(cs)
    return cs

@router.delete("/item/{id}")
async def delete_service(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClientService).where(ClientService.id == id))
    cs = result.scalar_one_or_none()
    if not cs:
        raise HTTPException(status_code=404, detail="Client service not found")
        
    await db.delete(cs)
    await db.commit()
    return {"message": "Service deleted"}

