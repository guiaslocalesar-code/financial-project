from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.expense_type import ExpenseType
from app.models.expense_category import ExpenseCategory
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.utils.enums import AppliesTo

router = APIRouter(prefix="/expenses", tags=["Expenses Configuration"])

# Internal schemas for simplicity or can be moved to app/schemas/
class ExpenseTypeCreate(BaseModel):
    company_id: UUID
    name: str
    applies_to: str = "BOTH"

class ExpenseCategoryCreate(BaseModel):
    company_id: UUID
    expense_type_id: UUID
    name: str

class ExpenseTypeResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    applies_to: AppliesTo
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExpenseCategoryResponse(BaseModel):
    id: UUID
    company_id: UUID
    expense_type_id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

@router.post("/types", response_model=ExpenseTypeResponse)
async def create_expense_type(type_in: ExpenseTypeCreate, db: AsyncSession = Depends(get_db)):
    expense_type = ExpenseType(**type_in.model_dump())
    db.add(expense_type)
    await db.commit()
    await db.refresh(expense_type)
    return expense_type

@router.get("/types", response_model=list[ExpenseTypeResponse])
async def list_expense_types(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company_id, ExpenseType.is_active == True))
    return result.scalars().all()

@router.post("/categories", response_model=ExpenseCategoryResponse)
async def create_expense_category(cat_in: ExpenseCategoryCreate, db: AsyncSession = Depends(get_db)):
    category = ExpenseCategory(**cat_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.get("/categories", response_model=list[ExpenseCategoryResponse])
async def list_expense_categories(company_id: UUID, expense_type_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    query = select(ExpenseCategory).where(ExpenseCategory.company_id == company_id, ExpenseCategory.is_active == True)
    if expense_type_id:
        query = query.where(ExpenseCategory.expense_type_id == expense_type_id)
    result = await db.execute(query)
    return result.scalars().all()
