from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("", response_model=ServiceResponse)
async def create_service(service_in: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(**service_in.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

@router.get("", response_model=list[ServiceResponse])
async def list_services(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.company_id == company_id, Service.is_active == True))
    return result.scalars().all()

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_in: ServiceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/{service_id}")
async def delete_service(service_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = False
    await db.commit()
    return {"message": "Service deactivated successfully"}
