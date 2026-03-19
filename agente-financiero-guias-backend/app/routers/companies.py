from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=list[CompanyResponse])
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return companies

@router.post("", response_model=CompanyResponse)
async def create_company(company_in: CompanyCreate, db: AsyncSession = Depends(get_db)):
    # Check if CUIT already exists
    result = await db.execute(select(Company).where(Company.cuit == company_in.cuit))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Company with this CUIT already exists")
    
    company = Company(**company_in.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: UUID, company_in: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    await db.commit()
    await db.refresh(company)
    return company
