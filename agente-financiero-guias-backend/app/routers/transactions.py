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

    try:
        comm_query = (
            select(Commission, CommissionRecipient)
            .join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)
            .where(
                CommissionRecipient.company_id == company_id,
                Commission.status == CommissionStatus.PAID
            )
        )
        comm_result = await db.execute(comm_query)
        rows = comm_result.all()
        
        for row in rows:
            c = row[0]
            r = row[1]
            
            # Map values explicitly to a dictionary for Pydantic to pick it up easily
            pseudo_tx = {
                "id": f"comm_{c.id}",
                "company_id": company_id,
                "client_id": None,
                "invoice_id": None,
                "budget_id": None,
                "service_id": None,
                "expense_type_id": None,
                "expense_category_id": None,
                "payment_method_id": None,
                "type": TransactionType.EXPENSE,
                "is_budgeted": False,
                "expense_origin": None,
                "amount": float(c.amount),
                "currency": "ARS",
                "exchange_rate": 1.0,
                "payment_method": None,
                "description": f"Pago de comisión a {r.name}",
                "transaction_date": c.updated_at.date() if c.updated_at else c.created_at.date(),
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            transactions.append(pseudo_tx)

        # Re-sort by date descending
        def get_date(x):
            if isinstance(x, dict):
                return x["transaction_date"]
            return x.transaction_date

        transactions.sort(key=get_date, reverse=True)
    except Exception as e:
        print(f"Error merging commissions: {e}")

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
