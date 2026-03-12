from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import date, datetime
from typing import List
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from app.database import get_db
from app.models.debt import Debt
from app.models.debt_installment import DebtInstallment
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction
from app.models.income_budget import IncomeBudget
from app.models.expense_budget import ExpenseBudget
from app.schemas.debt import (
    DebtCreate, DebtResponse, DebtSummaryResponse, 
    PaymentMethodResponse, CashflowProjectionDetail, DebtInstallmentResponse
)
from app.services.debt_service import calcular_deuda
from app.utils.enums import TransactionType, BudgetStatus

router = APIRouter(prefix="", tags=["Debts & Payment Methods"])

@router.post("/debts", response_model=DebtResponse)
async def create_debt(
    company_id: UUID,
    debt_in: DebtCreate, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Calcular deuda
    calculation = calcular_deuda(
        original_amount=debt_in.original_amount,
        installments=debt_in.installments,
        interest_rate=debt_in.interest_rate,
        interest_type=debt_in.interest_type,
        first_due_date=debt_in.first_due_date
    )

    # 2. Crear cabecera de deuda
    debt = Debt(
        company_id=company_id,
        payment_method_id=debt_in.payment_method_id,
        description=debt_in.description,
        original_amount=calculation["original_amount"],
        interest_type=calculation["interest_type"],
        interest_rate=calculation["interest_rate"],
        interest_total=calculation["interest_total"],
        total_amount=calculation["total_amount"],
        installments=calculation["installments"],
        installment_amount=calculation["installment_amount"],
        first_due_date=debt_in.first_due_date,
        status="active"
    )
    db.add(debt)
    await db.flush()

    # 3. Crear cuotas
    for c in calculation["cuotas"]:
        installment = DebtInstallment(
            debt_id=debt.id,
            installment_number=c["installment_number"],
            due_date=c["due_date"],
            amount=c["amount"],
            capital_amount=c["capital_amount"],
            interest_amount=c["interest_amount"],
            status="pending"
        )
        db.add(installment)
    
    await db.commit()
    await db.refresh(debt)
    
    # Reload with installments
    result = await db.execute(
        select(Debt).options(selectinload(Debt.installments_detail)).where(Debt.id == debt.id)
    )
    return result.scalar_one()

@router.post("/transactions/{transaction_id}/add-debt", response_model=DebtResponse)
async def add_debt_to_transaction(
    transaction_id: UUID,
    debt_in: DebtCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verificar si existe la transaccion
    res_t = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = res_t.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Calcular deuda
    calculation = calcular_deuda(
        original_amount=debt_in.original_amount,
        installments=debt_in.installments,
        interest_rate=debt_in.interest_rate,
        interest_type=debt_in.interest_type,
        first_due_date=debt_in.first_due_date
    )

    # Crear deuda vinculada
    debt = Debt(
        company_id=transaction.company_id,
        transaction_id=transaction.id,
        payment_method_id=debt_in.payment_method_id,
        description=debt_in.description,
        original_amount=calculation["original_amount"],
        interest_type=calculation["interest_type"],
        interest_rate=calculation["interest_rate"],
        interest_total=calculation["interest_total"],
        total_amount=calculation["total_amount"],
        installments=calculation["installments"],
        installment_amount=calculation["installment_amount"],
        first_due_date=debt_in.first_due_date,
        status="active"
    )
    db.add(debt)
    await db.flush()

    for c in calculation["cuotas"]:
        installment = DebtInstallment(
            debt_id=debt.id,
            installment_number=c["installment_number"],
            due_date=c["due_date"],
            amount=c["amount"],
            capital_amount=c["capital_amount"],
            interest_amount=c["interest_amount"],
            status="pending"
        )
        db.add(installment)
    
    await db.commit()
    await db.refresh(debt)
    
    result = await db.execute(
        select(Debt).options(selectinload(Debt.installments_detail)).where(Debt.id == debt.id)
    )
    return result.scalar_one()

@router.patch("/debt-installments/{installment_id}/pay")
async def pay_debt_installment(
    installment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    res_inst = await db.execute(
        select(DebtInstallment).where(DebtInstallment.id == installment_id)
    )
    installment = res_inst.scalar_one_or_none()
    if not installment:
        raise HTTPException(status_code=404, detail="Installment not found")
    
    if installment.status == 'paid':
        raise HTTPException(status_code=400, detail="Installment already paid")

    # Get debt info
    res_debt = await db.execute(select(Debt).where(Debt.id == installment.debt_id))
    debt = res_debt.scalar_one()

    # 1. Crear transaccion (egreso)
    transaction = Transaction(
        company_id=debt.company_id,
        type=TransactionType.EXPENSE,
        amount=installment.amount,
        payment_method_id=debt.payment_method_id,
        description=f"Pago cuota {installment.installment_number}/{debt.installments} - {debt.description}",
        transaction_date=date.today()
    )
    db.add(transaction)
    await db.flush()

    # 2. Actualizar cuota
    installment.status = 'paid'
    installment.transaction_id = transaction.id
    await db.flush()

    # 3. Actualizar estado de la deuda
    # Contar cuotas pagadas
    res_count = await db.execute(
        select(func.count(DebtInstallment.id))
        .where(DebtInstallment.debt_id == debt.id, DebtInstallment.status == 'paid')
    )
    paid_count = res_count.scalar()

    if paid_count == debt.installments:
        debt.status = 'paid'
    else:
        debt.status = 'partial'

    await db.commit()
    return {"message": "Installment paid", "transaction_id": transaction.id, "debt_status": debt.status}

@router.get("/debts", response_model=List[DebtResponse])
async def list_debts(
    company_id: UUID,
    status: str = 'active',
    db: AsyncSession = Depends(get_db)
):
    query = select(Debt).options(selectinload(Debt.installments_detail)).where(Debt.company_id == company_id)
    if status:
        query = query.where(Debt.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def list_payment_methods(
    company_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.company_id == company_id, PaymentMethod.is_active == True)
    )
    return result.scalars().all()

@router.get("/dashboard/debt-summary", response_model=DebtSummaryResponse)
async def get_debt_summary(
    company_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    # Deuda total activa (suma de total_amount de todas las debts active/partial)
    res_total = await db.execute(
        select(func.sum(Debt.total_amount))
        .where(Debt.company_id == company_id, Debt.status.in_(['active', 'partial']))
    )
    deuda_total_activa = res_total.scalar() or Decimal(0)

    # Total pagado (suma de amount de installments paid)
    res_paid = await db.execute(
        select(func.sum(DebtInstallment.amount))
        .join(Debt)
        .where(Debt.company_id == company_id, DebtInstallment.status == 'paid')
    )
    total_pagado = res_paid.scalar() or Decimal(0)

    # Total pendiente
    total_pendiente = deuda_total_activa - total_pagado

    # Intereses
    res_int_paid = await db.execute(
        select(func.sum(DebtInstallment.interest_amount))
        .join(Debt)
        .where(Debt.company_id == company_id, DebtInstallment.status == 'paid')
    )
    intereses_pagados = res_int_paid.scalar() or Decimal(0)

    res_int_pend = await db.execute(
        select(func.sum(DebtInstallment.interest_amount))
        .join(Debt)
        .where(Debt.company_id == company_id, DebtInstallment.status == 'pending', Debt.status.in_(['active', 'partial']))
    )
    intereses_pendientes = res_int_pend.scalar() or Decimal(0)

    # Proximas 5 cuotas
    res_next = await db.execute(
        select(DebtInstallment)
        .join(Debt)
        .where(Debt.company_id == company_id, DebtInstallment.status == 'pending')
        .order_by(DebtInstallment.due_date.asc())
        .limit(5)
    )
    proximas_cuotas = res_next.scalars().all()

    return {
        "deuda_total_activa": deuda_total_activa,
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
        "intereses_pagados": intereses_pagados,
        "intereses_pendientes": intereses_pendientes,
        "proximas_cuotas": proximas_cuotas
    }

@router.get("/dashboard/cashflow-projection", response_model=List[CashflowProjectionDetail])
async def get_cashflow_projection(
    company_id: UUID,
    months: int = 6,
    db: AsyncSession = Depends(get_db)
):
    projection = []
    base_date = date.today().replace(day=1)

    for i in range(months):
        target_month = base_date + relativedelta(months=i)
        month_str = target_month.strftime("%Y-%m")
        
        # Ingresos esperados (income_budgets pending)
        res_inc = await db.execute(
            select(func.sum(IncomeBudget.budgeted_amount))
            .where(
                IncomeBudget.company_id == company_id,
                IncomeBudget.period_month == target_month.month,
                IncomeBudget.period_year == target_month.year,
                IncomeBudget.status == 'pending'
            )
        )
        ingresos = res_inc.scalar() or Decimal(0)

        # Egresos presupuestados (expense_budgets pending)
        res_exp = await db.execute(
            select(func.sum(ExpenseBudget.budgeted_amount))
            .where(
                ExpenseBudget.company_id == company_id,
                ExpenseBudget.period_month == target_month.month,
                ExpenseBudget.period_year == target_month.year,
                ExpenseBudget.status == BudgetStatus.PENDING
            )
        )
        egresos = res_exp.scalar() or Decimal(0)

        # Cuotas a pagar (debt_installments pending)
        res_debt = await db.execute(
            select(
                func.sum(DebtInstallment.amount),
                func.sum(DebtInstallment.capital_amount),
                func.sum(DebtInstallment.interest_amount)
            )
            .join(Debt)
            .where(
                Debt.company_id == company_id,
                DebtInstallment.status == 'pending',
                func.extract('month', DebtInstallment.due_date) == target_month.month,
                func.extract('year', DebtInstallment.due_date) == target_month.year
            )
        )
        debt_data = res_debt.one()
        cuotas_total = debt_data[0] or Decimal(0)
        cuotas_capital = debt_data[1] or Decimal(0)
        cuotas_interes = debt_data[2] or Decimal(0)

        flujo_neto = ingresos - egresos - cuotas_total

        projection.append({
            "mes": month_str,
            "ingresos_esperados": ingresos,
            "egresos_presupuestados": egresos,
            "cuotas_a_pagar": cuotas_total,
            "cuotas_capital": cuotas_capital,
            "cuotas_interes": cuotas_interes,
            "flujo_neto": flujo_neto
        })

    return projection
