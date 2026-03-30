from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.user import UserCompanyResponse, UserCompanyUpdate, UserCompanyCreate, UserCompanyInvite
import traceback

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
    Invita a un usuario (por email) a un negocio.
    Si el usuario existe en Supabase Auth pero nunca inició sesión en el portal,
    se crea automáticamente su registro en public.users y se lo vincula a la empresa.
    """
    try:
        # 1. Check in public.users first
        user_res = await db.execute(select(User).where(User.email == invite_data.email))
        user = user_res.scalar_one_or_none()

        if not user:
            # 2. Look up in auth.users (Supabase's internal table)
            auth_res = await db.execute(
                text("SELECT id, email, raw_user_meta_data FROM auth.users WHERE email = :email LIMIT 1"),
                {"email": invite_data.email}
            )
            auth_row = auth_res.fetchone()

            if not auth_row:
                raise HTTPException(
                    status_code=404,
                    detail=f"El email '{invite_data.email}' no está registrado en Supabase. El usuario debe crear una cuenta primero."
                )

            # 3. Auto-provision into public.users
            auth_id = auth_row[0]
            auth_email = auth_row[1]
            meta = auth_row[2] or {}
            display_name = meta.get("full_name") or meta.get("name") or auth_email.split("@")[0]

            user = User(
                id=auth_id,
                email=auth_email,
                name=display_name,
                is_active=True
            )
            db.add(user)
            await db.flush()  # persist without committing yet

        # 4. Check if already linked to this company
        link_res = await db.execute(
            select(UserCompany)
            .where(UserCompany.user_id == user.id, UserCompany.company_id == company_id)
        )
        existing_link = link_res.scalar_one_or_none()

        if existing_link:
            if existing_link.is_active:
                raise HTTPException(status_code=400, detail="El usuario ya pertenece a esta empresa")
            else:
                # Re-activate
                existing_link.is_active = True
                existing_link.role = invite_data.role
                existing_link.permissions = invite_data.permissions
                existing_link.quotaparte = invite_data.quotaparte
                await db.commit()
                rel_res = await db.execute(select(UserCompany).options(joinedload(UserCompany.user)).where(UserCompany.id == existing_link.id))
                return rel_res.scalar_one()

        # 5. Create new company link
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

        rel_res = await db.execute(select(UserCompany).options(joinedload(UserCompany.user)).where(UserCompany.id == new_uc.id))
        return rel_res.scalar_one()

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=400, detail=error_msg)



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
