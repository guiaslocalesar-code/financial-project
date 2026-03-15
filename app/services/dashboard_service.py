from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from app.models.transaction import Transaction
from app.models.invoice_item import InvoiceItem
from app.models.expense_budget import ExpenseBudget
from app.models.service import Service
from app.models.commission import Commission
from app.utils.enums import TransactionType, BudgetStatus, CommissionStatus

class DashboardService:
    async def get_summary(self, company_id: UUID, month: int, year: int, db: AsyncSession):
        # Total Income
        income_res = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.INCOME,
                func.extract('month', Transaction.transaction_date) == month,
                func.extract('year', Transaction.transaction_date) == year
            )
        )
        total_income = income_res.scalar() or 0.0

        # Total Expenses
        expense_res = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.EXPENSE,
                func.extract('month', Transaction.transaction_date) == month,
                func.extract('year', Transaction.transaction_date) == year
            )
        )
        total_expenses = expense_res.scalar() or 0.0

        # Pending to Pay
        pending_res = await db.execute(
            select(func.sum(ExpenseBudget.budgeted_amount))
            .where(
                ExpenseBudget.company_id == company_id,
                ExpenseBudget.status == BudgetStatus.PENDING,
                ExpenseBudget.period_month == month,
                ExpenseBudget.period_year == year
            )
        )
        pending_to_pay = pending_res.scalar() or 0.0

        # Total Commissions pending
        comm_pending_res = await db.execute(
            select(func.sum(Commission.commission_amount))
            .where(
                Commission.company_id == company_id,
                Commission.status == CommissionStatus.PENDING,
                func.extract('month', Commission.created_at) == month,
                func.extract('year', Commission.created_at) == year
            )
        )
        total_commissions_pending = float(comm_pending_res.scalar() or 0.0)

        # Total Commissions paid
        comm_paid_res = await db.execute(
            select(func.sum(Commission.commission_amount))
            .where(
                Commission.company_id == company_id,
                Commission.status == CommissionStatus.PAID,
                func.extract('month', Commission.created_at) == month,
                func.extract('year', Commission.created_at) == year
            )
        )
        total_commissions_paid = float(comm_paid_res.scalar() or 0.0)

        total_commissions = total_commissions_pending + total_commissions_paid

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_commissions_pending": total_commissions_pending,
            "total_commissions_paid": total_commissions_paid,
            "total_commissions": total_commissions,
            "net_income_after_commissions": total_income - total_commissions,
            "balance": total_income - total_expenses - total_commissions,
            "pending_to_pay": pending_to_pay
        }

    async def get_profitability(self, company_id: UUID, db: AsyncSession):
        # Simplified profitability by service
        # 1. Income by service
        income_query = select(InvoiceItem.service_id, func.sum(InvoiceItem.subtotal).label("income")) \
            .group_by(InvoiceItem.service_id)
        
        income_data = await db.execute(income_query)
        income_map = {row.service_id: float(row.income) for row in income_data if row.service_id}

        # 2. Expense by service
        expense_query = select(Transaction.service_id, func.sum(Transaction.amount).label("expense")) \
            .where(Transaction.type == TransactionType.EXPENSE) \
            .group_by(Transaction.service_id)
        
        expense_data = await db.execute(expense_query)
        expense_map = {row.service_id: float(row.expense) for row in expense_data if row.service_id}

        # 3. Combine
        all_service_ids = set(income_map.keys()).union(set(expense_map.keys()))
        profitability = []
        for sid in all_service_ids:
            service_res = await db.execute(select(Service.name).where(Service.id == sid))
            name = service_res.scalar() or "Unknown"
            income = income_map.get(sid, 0.0)
            expense = expense_map.get(sid, 0.0)
            profitability.append({
                "service_name": name,
                "income": income,
                "expenses": expense,
                "margin": income - expense
            })
        
        return profitability

dashboard_service = DashboardService()
