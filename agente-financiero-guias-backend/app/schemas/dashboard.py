from pydantic import BaseModel
from uuid import UUID

class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    pending_to_pay: float

class ProfitabilityByService(BaseModel):
    service_name: str
    income: float
    expenses: float
    margin: float

class ClientRanking(BaseModel):
    client_name: str
    total_income: float

class BudgetVsReal(BaseModel):
    category_name: str
    budgeted: float
    actual: float
    variance: float

class DashboardData(BaseModel):
    summary: DashboardSummary
    profitability: list[ProfitabilityByService]
    rankings: list[ClientRanking]
    budget_vs_real: list[BudgetVsReal]
