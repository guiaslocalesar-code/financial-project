from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta

def calcular_deuda(
    original_amount: Decimal,
    installments: int,
    interest_rate: Decimal,  # % mensual, ej: 8.00
    interest_type: str,      # 'none' o 'fixed_rate'
    first_due_date: date
) -> dict:
    
    if interest_type == 'none' or interest_rate == 0:
        interest_total = Decimal('0')
        total_amount = original_amount
    elif interest_type == 'fixed_rate':
        # Interés fijo: capital × tasa% × cuotas
        interest_total = (original_amount 
                         * (interest_rate / 100) 
                         * installments).quantize(Decimal('0.01'), ROUND_HALF_UP)
        total_amount = original_amount + interest_total
    else:
        # Por defecto si el tipo no es reconocido
        interest_total = Decimal('0')
        total_amount = original_amount

    installment_amount = (total_amount / installments).quantize(
        Decimal('0.01'), ROUND_HALF_UP
    )
    capital_por_cuota = (original_amount / installments).quantize(
        Decimal('0.01'), ROUND_HALF_UP
    )
    interes_por_cuota = (interest_total / installments).quantize(
        Decimal('0.01'), ROUND_HALF_UP
    )

    # Generar lista de cuotas
    cuotas = []
    for i in range(installments):
        cuotas.append({
            "installment_number": i + 1,
            "due_date": first_due_date + relativedelta(months=i),
            "amount": installment_amount,
            "capital_amount": capital_por_cuota,
            "interest_amount": interes_por_cuota
        })

    return {
        "original_amount":    original_amount,
        "interest_type":      interest_type,
        "interest_rate":      interest_rate,
        "interest_total":     interest_total,
        "total_amount":       total_amount,
        "installments":       installments,
        "installment_amount": installment_amount,
        "cuotas":             cuotas
    }
