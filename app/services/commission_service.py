"""
commission_service.py
─────────────────────
Lógica de negocio para el módulo de comisiones.

Reglas críticas:
  · La base de cálculo es SIEMPRE el subtotal sin IVA
    (transaction.amount − transaction.iva_amount).
  · Una transaction de ingreso no puede generar dos veces comisiones
    para la misma regla (unicidad guardada por income_transaction_id + commission_rule_id).
  · El pago de comisión crea una Transaction de tipo EXPENSE de forma
    atómica: si falla el commit, el estado de la comisión no cambia.
"""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commission import Commission
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule
from app.models.transaction import Transaction
from app.utils.enums import (
    CommissionStatus,
    ExpenseOrigin,
    PaymentMethod,
    TransactionType,
)

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _base_without_iva(transaction: Transaction) -> Decimal:
    """
    Retorna el subtotal del ingreso SIN IVA.
    Si iva_amount está disponible lo resta del amount total.
    Si no, usa amount directamente (clientes sin factura / monto ya neto).
    """
    total = Decimal(str(transaction.amount))
    iva = Decimal(str(transaction.iva_amount or 0))
    base = total - iva
    # Nunca negativo por redondeo
    return base if base > 0 else total


# ── Generación de comisiones ───────────────────────────────────────────────────

async def calculate_commissions_for_income(
    db: AsyncSession,
    income_transaction_id: UUID,
) -> list[Commission]:
    """
    Calcula y persiste las comisiones para un ingreso dado.

    · Busca reglas activas que matcheen por company_id, client_id y/o service_id.
    · Comisión = (subtotal sin IVA) × (porcentaje / 100)
    · Si la suma de porcentajes supera 100 % se registra un warning pero se procede.
    · Si ya existen comisiones para esta transaction + regla, las omite
      (idempotente — seguro llamar múltiples veces).
    · NO hace commit — el caller es responsable del flush/commit.
    """
    # 1. Obtener la transaction de ingreso
    tx_res = await db.execute(
        select(Transaction).where(Transaction.id == income_transaction_id)
    )
    transaction = tx_res.scalar_one_or_none()

    if not transaction or transaction.type != TransactionType.INCOME:
        logger.warning(
            "Transaction %s no encontrada o no es INCOME — omitiendo comisiones",
            income_transaction_id,
        )
        return []

    if not transaction.client_id or not transaction.service_id:
        logger.info(
            "Transaction %s sin client_id/service_id — omitiendo comisiones",
            income_transaction_id,
        )
        return []

    # 2. Reglas activas que aplican (client_id o servicio match, con NULL = todos)
    rules_res = await db.execute(
        select(CommissionRule)
        .where(
            CommissionRule.company_id == transaction.company_id,
            CommissionRule.is_active == True,  # noqa: E712
            or_(
                CommissionRule.client_id == transaction.client_id,
                CommissionRule.client_id == None,  # noqa: E711
            ),
            or_(
                CommissionRule.service_id == transaction.service_id,
                CommissionRule.service_id == None,  # noqa: E711
            ),
        )
        .order_by(CommissionRule.priority.asc())
    )
    rules = rules_res.scalars().all()

    if not rules:
        return []

    # 3. IDs de reglas que ya tienen comisión para esta transaction (deduplicación)
    existing_res = await db.execute(
        select(Commission.commission_rule_id)
        .where(
            Commission.income_transaction_id == income_transaction_id,
            Commission.commission_rule_id != None,  # noqa: E711
        )
    )
    already_applied: set[UUID] = {row[0] for row in existing_res.all()}

    # 4. Calcular porcentaje total (warning si > 100)
    total_pct = sum(float(r.percentage) for r in rules)
    if total_pct > 100:
        logger.warning(
            "Comisiones superan 100%% para transaction %s (total: %.2f%%)",
            income_transaction_id,
            total_pct,
        )

    # 5. Crear comisiones para las reglas que aún no tienen registro
    base_amount = _base_without_iva(transaction)
    created: list[Commission] = []

    for rule in rules:
        if rule.id in already_applied:
            logger.debug(
                "Regla %s ya aplicada sobre transaction %s — saltando",
                rule.id,
                income_transaction_id,
            )
            continue

        commission_amount = base_amount * Decimal(str(rule.percentage)) / Decimal("100")
        commission = Commission(
            company_id=transaction.company_id,
            income_transaction_id=transaction.id,
            commission_rule_id=rule.id,
            recipient_id=rule.recipient_id,
            client_id=transaction.client_id,
            service_id=transaction.service_id,
            base_amount=float(base_amount),
            commission_amount=float(commission_amount.quantize(Decimal("0.01"))),
            status=CommissionStatus.PENDING,
        )
        db.add(commission)
        created.append(commission)

    await db.flush()
    logger.info(
        "Generadas %d comisiones para transaction %s (base sin IVA: %.2f)",
        len(created),
        income_transaction_id,
        base_amount,
    )
    return created


# ── Pago de comisión ───────────────────────────────────────────────────────────

async def pay_commission(
    db: AsyncSession,
    commission_id: UUID,
    payment_method: PaymentMethod,
    payment_date: date,
    actual_amount: float | None = None,
    payment_method_id: str | None = None,
    description: str | None = None,
) -> Transaction:
    """
    Paga una comisión pendiente de forma atómica:
      1. Valida que exista y esté en estado PENDING.
      2. Crea una Transaction de tipo EXPENSE (expense_origin = unbudgeted).
      3. Asocia la transaction a la comisión y cambia su estado a PAID.
      4. NO hace commit — el caller es responsable del commit.
         Si falla antes del commit el estado de la comisión nunca cambia.

    Raises:
        ValueError  — comisión no encontrada o ya pagada.
    """
    # 1. Obtener comisión
    comm_res = await db.execute(
        select(Commission).where(Commission.id == commission_id)
    )
    commission = comm_res.scalar_one_or_none()

    if not commission:
        raise ValueError(f"Comisión {commission_id} no encontrada")

    if commission.status != CommissionStatus.PENDING:
        raise ValueError(
            f"La comisión ya está en estado '{commission.status.value}'. "
            "Solo se pueden pagar comisiones PENDING."
        )

    # 2. Obtener nombre del recipient para la descripción
    rec_res = await db.execute(
        select(CommissionRecipient).where(
            CommissionRecipient.id == commission.recipient_id
        )
    )
    recipient = rec_res.scalar_one_or_none()
    recipient_name = recipient.name if recipient else "Desconocido"

    final_amount = actual_amount if actual_amount is not None else float(commission.commission_amount)
    desc = description or f"Pago comisión a {recipient_name} — servicio {commission.service_id}"

    # 3. Crear transaction de egreso (NO budgeted, origen = unbudgeted)
    expense_tx = Transaction(
        company_id=commission.company_id,
        type=TransactionType.EXPENSE,
        is_budgeted=False,
        expense_origin=ExpenseOrigin.UNBUDGETED,
        amount=final_amount,
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        description=desc,
        transaction_date=payment_date,
    )
    db.add(expense_tx)
    await db.flush()  # Obtener el ID antes de asignarlo

    # 4. Actualizar comisión — atómico: si el commit falla esto no persiste
    commission.status = CommissionStatus.PAID
    commission.payment_transaction_id = expense_tx.id

    logger.info(
        "Comisión %s marcada PAID — transaction egreso %s (%.2f %s)",
        commission_id,
        expense_tx.id,
        final_amount,
        payment_method.value,
    )
    return expense_tx


# ── Generación masiva de comisiones faltantes ──────────────────────────────────

async def generate_missing_commissions(
    db: AsyncSession,
    company_id: UUID,
) -> dict:
    """
    Busca todas las transactions de ingreso que todavía NO tienen
    ninguna comisión generada y les aplica las reglas vigentes.

    Retorna: {"transactions_procesadas": N, "comisiones_generadas": M}
    """
    # IDs de ingresos que ya tienen al menos 1 comisión (cualquier estado)
    existing_res = await db.execute(
        select(Commission.income_transaction_id)
        .where(Commission.company_id == company_id)
        .distinct()
    )
    already_with_commissions: set[UUID] = {row[0] for row in existing_res.all()}

    # Ingresos sin ninguna comisión
    stmt = select(Transaction).where(
        Transaction.company_id == company_id,
        Transaction.type == TransactionType.INCOME,
    )
    if already_with_commissions:
        stmt = stmt.where(Transaction.id.notin_(already_with_commissions))

    income_res = await db.execute(stmt)
    incomes = income_res.scalars().all()

    total_generated = 0
    for tx in incomes:
        comms = await calculate_commissions_for_income(db, tx.id)
        total_generated += len(comms)

    # El commit lo hace el router
    logger.info(
        "generate_missing_commissions: %d transactions procesadas, %d comisiones generadas",
        len(incomes),
        total_generated,
    )
    return {
        "transactions_procesadas": len(incomes),
        "comisiones_generadas": total_generated,
    }
