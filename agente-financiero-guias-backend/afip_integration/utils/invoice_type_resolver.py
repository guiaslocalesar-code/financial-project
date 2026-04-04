from app.utils.enums import FiscalCondition

def resolve_invoice_type(company_fiscal: FiscalCondition, client_fiscal: FiscalCondition) -> dict:
    """
    company=RI     + client=RI                         → tipo="A", cbte_tipo=1, iva_aplica=True
    company=RI     + client=monotributo                → tipo="B", cbte_tipo=6, iva_aplica=False
    company=RI     + client=consumidor_final           → tipo="B", cbte_tipo=6, iva_aplica=False
    company=RI     + client=exento                     → tipo="B", cbte_tipo=6, iva_aplica=False
    company=mono   + cualquier client                  → tipo="C", cbte_tipo=11, iva_aplica=False
    """
    if company_fiscal == FiscalCondition.MONOTRIBUTO:
        return {
            "invoice_type": "C",
            "cbte_tipo": 11,
            "iva_aplica": False
        }
    
    if company_fiscal == FiscalCondition.RI:
        if client_fiscal == FiscalCondition.RI:
            return {
                "invoice_type": "A",
                "cbte_tipo": 1,
                "iva_aplica": True
            }
        else:
            # Monotributo, consumidor final, exento
            return {
                "invoice_type": "B",
                "cbte_tipo": 6,
                "iva_aplica": False
            }
            
    # Default fallback just in case, treat as C (Exento could also be C depending on details)
    return {
        "invoice_type": "C",
        "cbte_tipo": 11,
        "iva_aplica": False
    }
