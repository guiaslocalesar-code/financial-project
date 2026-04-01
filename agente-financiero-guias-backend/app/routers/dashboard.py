from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, date
import calendar
from app.database import get_db
from app.services.dashboard_service import dashboard_service
from app.schemas.dashboard import DashboardData

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_summary(
    company_id: UUID,
    start_date: date = Query(default_factory=lambda: date.today().replace(day=1)),
    end_date: date = Query(default_factory=lambda: date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])),
    db: AsyncSession = Depends(get_db)
):
    summary = await dashboard_service.get_summary(company_id, start_date, end_date, db)
    return summary

from app.schemas.commission import CommissionsSummary
from fastapi import HTTPException
import traceback

@router.get("/commissions-summary")
async def get_commissions_summary(
    company_id: UUID, 
    start_date: date = Query(default_factory=lambda: date.today().replace(day=1)),
    end_date: date = Query(default_factory=lambda: date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])),
    db: AsyncSession = Depends(get_db)
):
    try:
        summary = await dashboard_service.get_commissions_summary(company_id, start_date, end_date, db)
        return summary
    except Exception as e:
        # Log full traceback to Cloud Run logs
        print(f"ERROR in commissions-summary: {e}")
        traceback.print_exc()
        # Return zeros instead of crashing - frontend handles gracefully
        return {
            "total_pending": 0.0,
            "total_paid": 0.0,
            "recipient_count": 0,
            "top_recipients": []
        }

@router.get("/profitability")
async def get_profitability(
    company_id: UUID, 
    start_date: date = Query(default_factory=lambda: date.today().replace(day=1)),
    end_date: date = Query(default_factory=lambda: date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])),
    db: AsyncSession = Depends(get_db)
):
    profitability = await dashboard_service.get_profitability(company_id, start_date, end_date, db)
    return profitability

@router.get("/all")
async def get_full_dashboard(
    company_id: UUID,
    start_date: date = Query(default_factory=lambda: date.today().replace(day=1)),
    end_date: date = Query(default_factory=lambda: date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])),
    db: AsyncSession = Depends(get_db)
):
    summary = await dashboard_service.get_summary(company_id, start_date, end_date, db)
    profitability = await dashboard_service.get_profitability(company_id, start_date, end_date, db)
    # Could add rankings and budget-vs-real here too
    return {
        "summary": summary,
        "profitability": profitability,
        "rankings": [],
        "budget_vs_real": []
    }
