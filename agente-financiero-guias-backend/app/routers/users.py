from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.user import UserCompanyResponse, UserCompanyUpdate, UserCompanyCreate, UserCompanyInvite

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

@router.post("/companies/{company_id}", response_model=UserCompanyResponse)
async def invite_user_to_company(
    company_id: UUID, 
    invite_data: UserCompanyInvite,
    db: AsyncSession = Depends(get_db)
):
    """
    Invita a un usuario (por email) a un negocio. Si el usuario no existe en la BD global de Supabase, falla.
    Si ya posee acceso al negocio, lanza error 400.
    """
    # 1. Check if user exists by email
    user_res = await db.execute(select(User).where(User.email == invite_data.email))
    user = user_res.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="El usuario no se ha registrado en el sistema web. Primero debe iniciar sesión.")
    
    # 2. Check if already linked to this company
    link_res = await db.execute(
        select(UserCompany)
        .where(UserCompany.user_id == user.id, UserCompany.company_id == company_id)
    )
    existing_link = link_res.scalar_one_or_none()
    
    if existing_link:
        if existing_link.is_active:
            raise HTTPException(status_code=400, detail="El usuario ya pertenece a esta empresa")
        else:
            # Re-activate user
            existing_link.is_active = True
            existing_link.role = invite_data.role
            existing_link.permissions = invite_data.permissions
            existing_link.quotaparte = invite_data.quotaparte
            await db.commit()
            await db.refresh(existing_link)
            # Re-fetch with joined user
            rel_res = await db.execute(select(UserCompany).options(joinedload(UserCompany.user)).where(UserCompany.id == existing_link.id))
            return rel_res.scalar_one()

    # 3. Create new link
    new_uc = UserCompany(
        user_id=user.id,
        company_id=company_id,
        role=invite_data.role,
        permissions=invite_data.permissions,
        quotaparte=invite_data.quotaparte
    )
    db.add(new_uc)
    await db.commit()
    await db.refresh(new_uc)
    
    # Re-fetch with user joined
    rel_res = await db.execute(select(UserCompany).options(joinedload(UserCompany.user)).where(UserCompany.id == new_uc.id))
    return rel_res.scalar_one()


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
