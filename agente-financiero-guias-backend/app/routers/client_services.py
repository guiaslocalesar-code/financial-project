from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from app.database import get_db
from app.models.client_service import ClientService
from app.schemas.client_service import ClientServiceCreate, ClientServiceResponse

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
