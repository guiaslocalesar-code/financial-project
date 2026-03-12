from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date
from typing import List, Optional
import uuid

class DebtCreate(BaseModel):
    payment_method_id: str
    description: str
    original_amount: Decimal
    installments: int = 1
    interest_type: str = 'none'   # 'none' o 'fixed_rate'
    interest_rate: Decimal = 0    # % mensual
    first_due_date: date

class DebtInstallmentResponse(BaseModel):
    id: uuid.UUID
    installment_number: int
    due_date: date
    amount: Decimal
    capital_amount: Decimal
    interest_amount: Decimal
    status: str
    transaction_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

class DebtResponse(BaseModel):
    id: uuid.UUID
    description: str
    original_amount: Decimal
    interest_rate: Decimal
    interest_total: Decimal
    total_amount: Decimal
    installments: int
    installment_amount: Decimal
    status: str
    installments_detail: List[DebtInstallmentResponse]

    model_config = ConfigDict(from_attributes=True)

class CashflowProjectionDetail(BaseModel):
    mes: str
    ingresos_esperados: Decimal
    egresos_presupuestados: Decimal
    cuotas_a_pagar: Decimal
    cuotas_capital: Decimal
    cuotas_interes: Decimal
    flujo_neto: Decimal

class DebtSummaryResponse(BaseModel):
    deuda_total_activa: Decimal
    total_pagado: Decimal
    total_pendiente: Decimal
    intereses_pagados: Decimal
    intereses_pendientes: Decimal
    proximas_cuotas: List[DebtInstallmentResponse]

class PaymentMethodResponse(BaseModel):
    id: str
    name: str
    type: str
    bank: Optional[str] = None
    is_credit: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
