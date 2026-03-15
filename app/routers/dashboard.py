from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.services.dashboard_service import dashboard_service
from app.schemas.dashboard import DashboardData

from app.dependencies import get_current_company
from app.models.user import UserCompany

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_summary(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    db: AsyncSession = Depends(get_db),
    user_company: UserCompany = Depends(get_current_company)
):
    summary = await dashboard_service.get_summary(company_id, month, year, db)
    
    # Calcular "tu parte"
    quotaparte = float(user_company.quotaparte) / 100.0
    
    summary["tu_parte_ingresos"] = summary.get("total_income", 0) * quotaparte
    summary["tu_parte_egresos"] = summary.get("total_expenses", 0) * quotaparte
    summary["tu_parte_commissions"] = summary.get("total_commissions", 0) * quotaparte
    summary["tu_parte_utilidad"] = summary.get("balance", 0) * quotaparte
    summary["quotaparte"] = float(user_company.quotaparte)
    
    return summary

@router.get("/profitability")
async def get_profitability(company_id: UUID, db: AsyncSession = Depends(get_db)):
    profitability = await dashboard_service.get_profitability(company_id, db)
    return profitability

@router.get("/all")
async def get_full_dashboard(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    db: AsyncSession = Depends(get_db)
):
    summary = await dashboard_service.get_summary(company_id, month, year, db)
    profitability = await dashboard_service.get_profitability(company_id, db)
    # Could add rankings and budget-vs-real here too
    return {
        "summary": summary,
        "profitability": profitability,
        "rankings": [],
        "budget_vs_real": []
    }
