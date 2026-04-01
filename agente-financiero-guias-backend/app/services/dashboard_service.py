from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from app.models.transaction import Transaction
from app.models.invoice_item import InvoiceItem
from app.models.expense_budget import ExpenseBudget
from app.models.service import Service
from app.utils.enums import TransactionType, BudgetStatus

class DashboardService:
    async def get_summary(self, company_id: UUID, start_date: date, end_date: date, db: AsyncSession):
        total_income = 0.0
        total_expenses = 0.0
        total_commissions = 0.0
        pending_to_pay = 0.0

        # Total Income
        try:
            income_res = await db.execute(
                select(func.sum(Transaction.amount))
                .where(
                    Transaction.company_id == company_id,
                    Transaction.type == TransactionType.INCOME,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
            total_income = float(income_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying income: {e}")

        # Total Expenses
        try:
            expense_res = await db.execute(
                select(func.sum(Transaction.amount))
                .where(
                    Transaction.company_id == company_id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
            total_expenses = float(expense_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying expenses: {e}")

        # Commissions (added to Total Expenses)
        try:
            from app.models.commission import Commission, CommissionRecipient
            from app.utils.enums import CommissionStatus
            
            comm_res = await db.execute(
                select(func.sum(Commission.amount))
                .select_from(Commission)
                .join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)
                .where(
                    CommissionRecipient.company_id == company_id,
                    Commission.status == CommissionStatus.PAID,
                    func.cast(Commission.updated_at, date) >= start_date,
                    func.cast(Commission.updated_at, date) <= end_date
                )
            )
            total_commissions = float(comm_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying commissions: {e}")
        
        total_expenses += total_commissions

        # Pending to Pay
        try:
            pending_res = await db.execute(
                select(func.sum(ExpenseBudget.budgeted_amount))
                .where(
                    ExpenseBudget.company_id == company_id,
                    ExpenseBudget.status == BudgetStatus.PENDING,
                    ExpenseBudget.period_year * 12 + ExpenseBudget.period_month >= start_date.year * 12 + start_date.month,
                    ExpenseBudget.period_year * 12 + ExpenseBudget.period_month <= end_date.year * 12 + end_date.month
                )
            )
            pending_to_pay = float(pending_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying pending: {e}")

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
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

    async def get_commissions_summary(self, company_id: UUID, db: AsyncSession):
        from app.models.commission import Commission, CommissionRecipient
        from app.utils.enums import CommissionStatus

        total_pending = 0.0
        total_paid = 0.0
        recipient_count = 0
        top_recipients = []

        try:
            pending_res = await db.execute(
                select(func.sum(Commission.amount))
                .select_from(Commission)
                .join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)
                .where(
                    CommissionRecipient.company_id == company_id,
                    Commission.status == CommissionStatus.PENDING
                )
            )
            total_pending = float(pending_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying pending commissions: {e}")

        try:
            paid_res = await db.execute(
                select(func.sum(Commission.amount))
                .select_from(Commission)
                .join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)
                .where(
                    CommissionRecipient.company_id == company_id,
                    Commission.status == CommissionStatus.PAID
                )
            )
            total_paid = float(paid_res.scalar() or 0.0)
        except Exception as e:
            print(f"Error querying paid commissions: {e}")

        try:
            recip_res = await db.execute(
                select(func.count(CommissionRecipient.id))
                .select_from(CommissionRecipient)
                .where(CommissionRecipient.company_id == company_id)
            )
            recipient_count = int(recip_res.scalar() or 0)
        except Exception as e:
            print(f"Error querying recipient count: {e}")

        try:
            top_res = await db.execute(
                select(
                    CommissionRecipient.id,
                    CommissionRecipient.name,
                    func.sum(Commission.amount).label('total_earned')
                )
                .select_from(CommissionRecipient)
                .join(Commission, Commission.recipient_id == CommissionRecipient.id)
                .where(CommissionRecipient.company_id == company_id)
                .group_by(CommissionRecipient.id, CommissionRecipient.name)
                .order_by(func.sum(Commission.amount).desc())
                .limit(5)
            )
            top_recipients = [
                {"id": str(row.id), "name": row.name, "total_earned": float(row.total_earned)}
                for row in top_res
            ]
        except Exception as e:
            print(f"Error querying top recipients: {e}")

        return {
            "total_pending": total_pending,
            "total_paid": total_paid,
            "recipient_count": recipient_count,
            "top_recipients": top_recipients
        }

dashboard_service = DashboardService()
