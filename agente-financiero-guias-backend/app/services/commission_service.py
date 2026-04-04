import uuid
from datetime import date
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.commission import Commission, CommissionRecipient, CommissionRule
from app.models.transaction import Transaction
from app.utils.enums import TransactionType, PaymentMethod, CommissionStatus
from app.schemas.commission import CommissionPay

class CommissionService:
    async def generate_commissions(self, company_id: uuid.UUID, db: AsyncSession):
        """
        Generates commissions based on INCOME transactions and active rules.
        Skips transactions that already have a commission.
        """
        # 1. Get all INCOME transactions for this company that don't have a commission yet
        # We check the commissions table to see which transaction_ids are already there
        existing_comm_subquery = select(Commission.transaction_id)
        
        query = select(Transaction).where(
            and_(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.INCOME,
                not_(Transaction.id.in_(existing_comm_subquery))
            )
        )
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        if not transactions:
            return 0

        # 2. Get all active rules for this company
        rules_query = select(CommissionRule).join(
            CommissionRecipient, CommissionRule.recipient_id == CommissionRecipient.id
        ).where(
            CommissionRecipient.company_id == company_id
        )
        rules_result = await db.execute(rules_query)
        rules = rules_result.scalars().all()
        
        if not rules:
            return 0

        commissions_created = 0
        
        for tx in transactions:
            for rule in rules:
                # Logic: Match by service_id (specific) or client_id (less specific) or global (if both null)
                match = False
                
                if rule.service_id and tx.service_id:
                    if str(rule.service_id) == str(tx.service_id):
                        match = True
                elif rule.client_id and tx.client_id:
                    if str(rule.client_id) == str(tx.client_id):
                        match = True
                elif not rule.service_id and not rule.client_id:
                    # Global rule for this recipient
                    match = True
                
                if match:
                    # Calculate amount
                    comm_amount = (float(tx.amount) * float(rule.percentage)) / 100
                    
                    new_comm = Commission(
                        transaction_id=tx.id,
                        recipient_id=rule.recipient_id,
                        amount=comm_amount,
                        status=CommissionStatus.PENDING
                    )
                    db.add(new_comm)
                    commissions_created += 1
        
        await db.commit()
        return commissions_created

    async def pay_commission(self, commission_id: uuid.UUID, payload: CommissionPay, db: AsyncSession):
        """
        Pays a commission by creating an EXPENSE transaction and updating status.
        """
        # 1. Get commission with recipient info
        query = select(Commission).options(joinedload(Commission.recipient)).where(Commission.id == commission_id)
        result = await db.execute(query)
        commission = result.scalar_one_or_none()
        
        if not commission:
            raise Exception("Commission not found")
        
        if commission.status == CommissionStatus.PAID:
            raise Exception("Commission already paid")

        # 2. Create the Expense Transaction
        # We use actual_amount if provided, otherwise the original commission amount
        final_amount = payload.actual_amount if payload.actual_amount is not None else float(commission.amount)
        
        payment_tx = Transaction(
            company_id=commission.recipient.company_id,
            type=TransactionType.EXPENSE,
            amount=final_amount,
            payment_method=PaymentMethod(payload.payment_method.upper()),
            payment_method_id=payload.payment_method_id if payload.payment_method_id else None,
            description=f"Liquidación Comisión: {commission.recipient.name}",
            transaction_date=payload.payment_date or date.today(),
            is_budgeted=False
        )
        
        db.add(payment_tx)
        await db.flush() # Get payment_tx.id

        # 3. Update Commission
        commission.status = CommissionStatus.PAID
        commission.payment_transaction_id = payment_tx.id
        
        await db.commit()

        # Re-fetch with eager loading for all required UI fields
        reload_query = (
            select(Commission)
            .options(
                joinedload(Commission.recipient),
                joinedload(Commission.transaction).joinedload(Transaction.client),
                joinedload(Commission.transaction).joinedload(Transaction.service)
            )
            .where(Commission.id == commission_id)
        )
        reload_result = await db.execute(reload_query)
        commission = reload_result.scalar_one()
        return commission

    async def bulk_pay_commissions(self, payload: BulkPayPayload, db: AsyncSession):
        """
        Pays multiple commissions in a batch.
        """
        results = []
        for commission_id in payload.commission_ids:
            try:
                # Reuse the single payment logic but localized to a sub-transaction if needed
                # For now, we manually do the logic to avoid multiple commits inside the loop
                # for better performance and session control.
                
                query = select(Commission).options(joinedload(Commission.recipient)).where(Commission.id == commission_id)
                res = await db.execute(query)
                comm = res.scalar_one_or_none()
                
                if not comm or comm.status == CommissionStatus.PAID:
                    results.append({"id": str(commission_id), "status": "skipped"})
                    continue

                payment_tx = Transaction(
                    company_id=comm.recipient.company_id,
                    type=TransactionType.EXPENSE,
                    amount=float(comm.amount),
                    payment_method=PaymentMethod(payload.payment_method.upper()),
                    payment_method_id=payload.payment_method_id if payload.payment_method_id else None,
                    description=f"Liquidación Comisión: {comm.recipient.name}",
                    transaction_date=payload.payment_date or date.today(),
                    is_budgeted=False
                )
                db.add(payment_tx)
                await db.flush()

                comm.status = CommissionStatus.PAID
                comm.payment_transaction_id = payment_tx.id
                results.append({"id": str(commission_id), "status": "paid"})
                
            except Exception as e:
                results.append({"id": str(commission_id), "status": "error", "error": str(e)})

        await db.commit()
        return results

commission_service = CommissionService()
