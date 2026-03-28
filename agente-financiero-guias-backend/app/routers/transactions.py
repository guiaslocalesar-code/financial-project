from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=list[TransactionResponse])
async def list_transactions(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.company_id == company_id).order_by(Transaction.transaction_date.desc()))
    transactions = list(result.scalars().all())

    # Fetch PAID commissions for this company to merge them as pseudo-transactions
    from app.models.commission import Commission, CommissionRecipient
    from app.utils.enums import CommissionStatus, TransactionType

    comm_query = (
        select(Commission, CommissionRecipient)
        .join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)
        .where(
            CommissionRecipient.company_id == company_id,
            Commission.status == CommissionStatus.PAID
        )
    )
    comm_result = await db.execute(comm_query)
    
    # Create Pydantic-compatible objects or dicts for the commissions
    class PseudoTransaction:
        def __init__(self, c: Commission, r: CommissionRecipient, comp_id: UUID):
            self.id = c.id
            self.company_id = comp_id
            self.client_id = None
            self.invoice_id = None
            self.budget_id = None
            self.service_id = None
            self.expense_type_id = None
            self.expense_category_id = None
            self.payment_method_id = None
            self.type = TransactionType.EXPENSE
            self.is_budgeted = False
            self.expense_origin = None
            self.amount = float(c.amount)
            self.currency = "ARS"
            self.exchange_rate = 1.0
            self.payment_method = None
            self.description = f"Pago de comisión a {r.name}"
            # Use updated_at as the date of payment
            self.transaction_date = c.updated_at.date() if c.updated_at else c.created_at.date()
            self.created_at = c.created_at
            self.updated_at = c.updated_at

    for comm, rec in comm_result:
        transactions.append(PseudoTransaction(comm, rec, company_id))

    # Re-sort by date descending
    transactions.sort(key=lambda x: x.transaction_date, reverse=True)

    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
