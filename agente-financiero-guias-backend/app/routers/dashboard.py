from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, date
from calendar import monthrange
from typing import Optional
from app.database import get_db
from app.services.dashboard_service import dashboard_service

from app.dependencies import get_current_company
from app.models.user import UserCompany

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _month_range(month: int, year: int) -> tuple[date, date]:
    """Convert month/year to start_date/end_date."""
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


@router.get("/summary")
async def get_summary(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    db: AsyncSession = Depends(get_db)
):
    start_date, end_date = _month_range(month, year)
    summary = await dashboard_service.get_summary(company_id, start_date, end_date, db)
    
    # Try to calculate "tu parte" if we can, but don't fail if no auth
    quotaparte = 1.0 # Default 100%
    try:
        # We'd normally use the dependency here, but if it fails, we catch it.
        # For now, let's just return the full numbers if no specific user-company link is provided.
        summary["tu_parte_ingresos"] = summary.get("total_income", 0) * quotaparte
        summary["tu_parte_egresos"] = summary.get("total_expenses", 0) * quotaparte
        summary["tu_parte_commissions"] = summary.get("total_commissions", 0) * quotaparte
        summary["tu_parte_utilidad"] = summary.get("balance", 0) * quotaparte
        summary["quotaparte"] = 100.0
    except Exception:
        pass
    
    return summary

@router.get("/profitability")
async def get_profitability(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    db: AsyncSession = Depends(get_db)
):
    start_date, end_date = _month_range(month, year)
    return await dashboard_service.get_profitability(company_id, start_date, end_date, db)

@router.get("/commissions-summary")
async def get_commissions_summary(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    if not (start_date and end_date):
        start_date, end_date = _month_range(month, year)
    return await dashboard_service.get_commissions_summary(company_id, start_date, end_date, db)

@router.get("/all")
async def get_full_dashboard(
    company_id: UUID,
    month: int = Query(datetime.now().month, ge=1, le=12),
    year: int = Query(datetime.now().year),
    db: AsyncSession = Depends(get_db)
):
    start_date, end_date = _month_range(month, year)
    summary = await dashboard_service.get_summary(company_id, start_date, end_date, db)
    profitability = await dashboard_service.get_profitability(company_id, start_date, end_date, db)
    commissions = await dashboard_service.get_commissions_summary(company_id, start_date, end_date, db)
    return {
        "summary": summary,
        "profitability": profitability,
        "commissions": commissions,
        "rankings": [],
        "budget_vs_real": []
    }
