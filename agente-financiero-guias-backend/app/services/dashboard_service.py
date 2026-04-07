from datetime import date as py_date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Date
from uuid import UUID
from app.models.transaction import Transaction
from app.models.invoice_item import InvoiceItem
from app.models.expense_budget import ExpenseBudget
from app.models.service import Service
from app.models.commission import Commission
from app.models.commission_recipient import CommissionRecipient
from app.utils.enums import TransactionType, BudgetStatus, CommissionStatus

class DashboardService:
    async def get_summary(self, company_id: UUID, start_date: py_date, end_date: py_date, db: AsyncSession):
        """
        Returns a financial summary for a date range.
        Note: The frontend might still send month/year, 
        so the caller should convert them to first/last day of month.
        """
        # Total Income
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

        # Total Expenses (Direct transactions)
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

        # Pending to Pay (Budgeted expenses not yet paid)
        # We look for budgets whose period falls within the range
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

        # Commissions Summary
        comm_summary = await self.get_commissions_summary(company_id, start_date, end_date, db)
        
        balance = total_income - total_expenses - comm_summary["total_paid"]

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_commissions_pending": comm_summary["total_pendiente"],
            "total_commissions_paid": comm_summary["total_pagado"],
            "total_commissions": comm_summary["total_pendiente"] + comm_summary["total_pagado"],
            "balance": balance,
            "pending_to_pay": pending_to_pay,
            "commissions_summary": comm_summary
        }

    async def get_profitability(self, company_id: UUID, start_date: py_date, end_date: py_date, db: AsyncSession):
        # 1. Income by service (joining invoices)
        from app.models.invoice import Invoice
        income_query = select(InvoiceItem.service_id, func.sum(InvoiceItem.subtotal).label("income")) \
            .join(Invoice, InvoiceItem.invoice_id == Invoice.id) \
            .where(
                Invoice.company_id == company_id,
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date
            ) \
            .group_by(InvoiceItem.service_id)
        
        income_data = await db.execute(income_query)
        income_map = {row.service_id: float(row.income) for row in income_data if row.service_id}

        # 2. Expense by service
        expense_query = select(Transaction.service_id, func.sum(Transaction.amount).label("expense")) \
            .where(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ) \
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

    async def get_commissions_summary(self, company_id: UUID, start_date: py_date, end_date: py_date, db: AsyncSession):
        total_pending = 0.0
        total_paid = 0.0
        recipient_count = 0
        top_recipients = []

        # Pending
        pending_res = await db.execute(
            select(func.sum(Commission.commission_amount))
            .where(
                Commission.company_id == company_id,
                Commission.status == CommissionStatus.PENDING,
                func.cast(Commission.created_at, Date) >= start_date,
                func.cast(Commission.created_at, Date) <= end_date
            )
        )
        total_pending = float(pending_res.scalar() or 0.0)

        # Paid
        paid_res = await db.execute(
            select(func.sum(Commission.commission_amount))
            .where(
                Commission.company_id == company_id,
                Commission.status == CommissionStatus.PAID,
                # For PAID, we might want to filter by update_at or transaction date
                func.cast(Commission.created_at, Date) >= start_date,
                func.cast(Commission.created_at, Date) <= end_date
            )
        )
        total_paid = float(paid_res.scalar() or 0.0)

        # Recipients
        recip_cnt_res = await db.execute(
            select(func.count(CommissionRecipient.id))
            .where(CommissionRecipient.company_id == company_id)
        )
        recipient_count = int(recip_cnt_res.scalar() or 0)

        # Top Recipients
        top_res = await db.execute(
            select(
                CommissionRecipient.id,
                CommissionRecipient.name,
                func.sum(Commission.commission_amount).label('total_earned')
            )
            .join(Commission, Commission.recipient_id == CommissionRecipient.id)
            .where(CommissionRecipient.company_id == company_id)
            .group_by(CommissionRecipient.id, CommissionRecipient.name)
            .order_by(func.sum(Commission.commission_amount).desc())
            .limit(5)
        )
        top_recipients = [
            {"id": str(row.id), "name": row.name, "total_earned": float(row.total_earned)}
            for row in top_res
        ]

        return {
            "total_pendiente": total_pending,
            "total_pagado": total_paid,
            "recipient_count": recipient_count,
            "top_recipients": top_recipients
        }

dashboard_service = DashboardService()
