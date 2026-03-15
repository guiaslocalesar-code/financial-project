import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.transaction import Transaction
from app.models.commission_rule import CommissionRule
from app.models.commission import Commission
from app.utils.enums import TransactionType, CommissionStatus

logger = logging.getLogger(__name__)


async def calculate_commissions_for_income(db: AsyncSession, income_transaction_id: UUID) -> list[Commission]:
    """
    Calcula y persiste las comisiones para un ingreso dado.
    Busca reglas activas que matcheen por company_id, client_id y/o service_id.
    Comisión = ingreso bruto × (porcentaje / 100)
    Si la suma de porcentajes supera 100 se registra un warning pero se procede igual.
    """
    # 1. Obtener la transaction de ingreso
    tx_result = await db.execute(
        select(Transaction).where(Transaction.id == income_transaction_id)
    )
    transaction = tx_result.scalar_one_or_none()

    if not transaction or transaction.type != TransactionType.INCOME:
        logger.warning(f"Transaction {income_transaction_id} no encontrada o no es de tipo INCOME")
        return []

    if not transaction.client_id or not transaction.service_id:
        logger.info(f"Transaction {income_transaction_id} sin client_id o service_id — omitiendo comisiones")
        return []

    # 2. Buscar reglas activas que apliquen a este ingreso
    rules_result = await db.execute(
        select(CommissionRule)
        .where(
            CommissionRule.company_id == transaction.company_id,
            CommissionRule.is_active == True,
            or_(CommissionRule.client_id == transaction.client_id, CommissionRule.client_id == None),
            or_(CommissionRule.service_id == transaction.service_id, CommissionRule.service_id == None),
        )
        .order_by(CommissionRule.priority.asc())
    )
    rules = rules_result.scalars().all()

    if not rules:
        return []

    # 3. Verificar suma de porcentajes
    total_pct = sum(float(r.percentage) for r in rules)
    if total_pct > 100:
        logger.warning(
            f"Configuración de comisiones excede 100% para transaction {income_transaction_id}. "
            f"Total: {total_pct:.2f}%"
        )

    # 4. Crear comisiones
    created: list[Commission] = []
    base_amount = float(transaction.amount)

    for rule in rules:
        commission_amount = base_amount * (float(rule.percentage) / 100)
        commission = Commission(
            company_id=transaction.company_id,
            income_transaction_id=transaction.id,
            commission_rule_id=rule.id,
            recipient_id=rule.recipient_id,
            client_id=transaction.client_id,
            service_id=transaction.service_id,
            base_amount=base_amount,
            commission_amount=commission_amount,
            status=CommissionStatus.PENDING,
        )
        db.add(commission)
        created.append(commission)

    # No se hace commit aquí — el caller es responsable del commit/flush
    await db.flush()
    logger.info(f"Generadas {len(created)} comisiones para transaction {income_transaction_id}")
    return created
