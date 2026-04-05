from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_company, require_role
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.utils.validators import validate_cuit, validate_dni

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("", response_model=ClientResponse)
async def create_client(
    client_in: ClientCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Verify company access (manual check or just skip for now as frontend doesn't send JWT)

    # Validate CUIT/CUIL/DNI
    doc = client_in.cuit_cuil_dni
    if len(doc) > 10:
        if not validate_cuit(doc):
            raise HTTPException(status_code=400, detail="Invalid CUIT/CUIL format")
    else:
        if not validate_dni(doc):
            raise HTTPException(status_code=400, detail="Invalid DNI format")
            
    client = Client(**client_in.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

@router.get("", response_model=list[ClientResponse])
async def list_clients(
    company_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Client)
        .where(Client.company_id == company_id, Client.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: UUID, client_in: ClientUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    return client

@router.delete("/{client_id}")
async def delete_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.is_active = False
    await db.commit()
    return {"message": "Client deactivated successfully"}
