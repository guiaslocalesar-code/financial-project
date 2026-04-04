from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_company, require_role
from app.models.user import User, UserCompany
from app.schemas.user import UserCompanyCreate, UserCompanyUpdate, UserCompanyResponse
from typing import List

router = APIRouter(prefix="/companies/{company_id}/users", tags=["Gestión de Usuarios"])

@router.get("/", response_model=List[UserCompanyResponse])
async def list_company_users(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    # Fetch user_companies for this company
    result = await db.execute(
        select(UserCompany, User.name, User.email)
        .join(User, UserCompany.user_id == User.id)
        .where(UserCompany.company_id == company_id, UserCompany.is_active == True)
    )
    rows = result.all()
    
    return [
        UserCompanyResponse(
            company_id=str(row.UserCompany.company_id),
            company_name="", # Could fetch name if needed
            role=row.UserCompany.role,
            quotaparte=row.UserCompany.quotaparte,
            is_active=row.UserCompany.is_active
        )
        for row in rows
    ]

@router.post("/", response_model=UserCompanyResponse)
async def add_user_to_company(
    company_id: UUID,
    user_in: UserCompanyCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner"]))
):
    # 1. Buscar si el usuario ya existe
    res_user = await db.execute(select(User).where(User.email == user_in.user_email))
    user = res_user.scalar_one_or_none()
    
    if not user:
        # Si no existe, lo creamos como placeholder (o podríamos invitarlo)
        # En este sistema, asumimos que el primer login con Google lo creará formalmente.
        # Por ahora creamos un registro básico.
        user = User(
            email=str(user_in.user_email),
            permissions={"status": "pending"}, # Placeholder instead of google_id
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # 2. Verificar si ya está en la empresa
    res_uc = await db.execute(
        select(UserCompany).where(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company_id
        )
    )
    user_company = res_uc.scalar_one_or_none()
    
    if user_company:
        if user_company.is_active:
            raise HTTPException(status_code=400, detail="El usuario ya pertenece a esta empresa")
        else:
            # Reactivar
            user_company.is_active = True
            user_company.role = user_in.role
            user_company.quotaparte = user_in.quotaparte
    else:
        user_company = UserCompany(
            user_id=user.id,
            company_id=company_id,
            role=user_in.role,
            quotaparte=user_in.quotaparte
        )
        db.add(user_company)
    
    await db.commit()
    await db.refresh(user_company)
    
    return UserCompanyResponse(
        company_id=str(user_company.company_id),
        company_name="",
        role=user_company.role,
        quotaparte=user_company.quotaparte,
        is_active=user_company.is_active
    )

@router.patch("/{user_company_id}", response_model=UserCompanyResponse)
async def update_company_user(
    company_id: UUID,
    user_company_id: UUID,
    user_in: UserCompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner"]))
):
    result = await db.execute(
        select(UserCompany).where(
            UserCompany.id == user_company_id,
            UserCompany.company_id == company_id
        )
    )
    user_company = result.scalar_one_or_none()
    
    if not user_company:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en la empresa")
    
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_company, field, value)
    
    await db.commit()
    await db.refresh(user_company)
    
    return UserCompanyResponse(
        company_id=str(user_company.company_id),
        company_name="",
        role=user_company.role,
        quotaparte=user_company.quotaparte,
        is_active=user_company.is_active
    )

@router.delete("/{user_company_id}")
async def remove_company_user(
    company_id: UUID,
    user_company_id: UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner"]))
):
    result = await db.execute(
        select(UserCompany).where(
            UserCompany.id == user_company_id,
            UserCompany.company_id == company_id
        )
    )
    user_company = result.scalar_one_or_none()
    
    if not user_company:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en la empresa")
    
    # Soft delete
    user_company.is_active = False
    await db.commit()
    
    return {"message": "Usuario removido exitosamente"}
