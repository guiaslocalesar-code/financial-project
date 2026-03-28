from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.user import UserCompanyResponse, UserCompanyUpdate, UserCompanyCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/companies/{company_id}", response_model=List[UserCompanyResponse])
async def list_company_users(company_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Lista todos los usuarios (y sus permisos) que tienen acceso a una empresa específica.
    """
    query = (
        select(UserCompany)
        .options(joinedload(UserCompany.user))
        .where(UserCompany.company_id == company_id, UserCompany.is_active == True)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/user-companies/{user_company_id}", response_model=UserCompanyResponse)
async def update_company_user(
    user_company_id: UUID, 
    update_data: UserCompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Edita rol y permisos granulares en formato JSON para un usuario específico en un negocio.
    """
    result = await db.execute(
        select(UserCompany)
        .options(joinedload(UserCompany.user))
        .where(UserCompany.id == user_company_id)
    )
    uc = result.scalar_one_or_none()
    if not uc:
        raise HTTPException(status_code=404, detail="Relación Usuario-Empresa no encontrada")
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(uc, key, value)
        
    await db.commit()
    await db.refresh(uc)
    return uc

@router.delete("/user-companies/{user_company_id}")
async def remove_company_user(user_company_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Desvincula lógicamente (baja) a un usuario de un negocio.
    """
    result = await db.execute(select(UserCompany).where(UserCompany.id == user_company_id))
    uc = result.scalar_one_or_none()
    if not uc:
        raise HTTPException(status_code=404, detail="Relación Usuario-Empresa no encontrada")
        
    uc.is_active = False
    await db.commit()
    return {"status": "ok", "message": "User removed from company successfully"}
