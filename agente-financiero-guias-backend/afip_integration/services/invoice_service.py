from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.company import Company
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.utils.enums import InvoiceStatus
from afip_integration.utils.invoice_type_resolver import resolve_invoice_type
from afip_integration.schemas.invoice_schemas import InvoiceCreate
from afip_integration.services.afip_auth import get_access_ticket
from afip_integration.services.afip_wsfe import get_last_invoice_number, authorize_invoice

def calculate_amounts(items: list, iva_rate: float, iva_aplica: bool) -> dict:
    subtotal = sum(item.quantity * item.unit_price for item in items)
    iva_amount = subtotal * (iva_rate / 100) if iva_aplica else 0.0
    total = subtotal + iva_amount
    return {
        "subtotal": subtotal,
        "iva_amount": iva_amount,
        "total": total
    }

async def create_invoice_draft(db: AsyncSession, company_id: UUID, payload: InvoiceCreate) -> Invoice:
    # 1. Obtener company y client
    comp_res = await db.execute(select(Company).where(Company.id == company_id))
    company = comp_res.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    cli_res = await db.execute(select(Client).where(Client.id == payload.client_id, Client.company_id == company_id))
    client = cli_res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Obtener tipo de factura
    resolution = resolve_invoice_type(company.fiscal_condition, client.fiscal_condition)
    
    # 3. Calcular montos
    amounts = calculate_amounts(payload.items, payload.iva_rate, resolution["iva_aplica"])

    # 4. Insertar Invoice Draft
    # Assuming afip_point_of_sale is configured, otherwise fallback to 1 as drafting doesn't strictly need it to succeed unless we validate.
    pto_vta = company.afip_point_of_sale or 1

    invoice = Invoice(
        company_id=company_id,
        client_id=client.id,
        invoice_type=resolution["invoice_type"],
        point_of_sale=pto_vta,
        issue_date=date.today(),
        due_date=payload.due_date,
        subtotal=amounts["subtotal"],
        iva_rate=payload.iva_rate,
        iva_amount=amounts["iva_amount"],
        total=amounts["total"],
        currency=payload.currency,
        exchange_rate=payload.exchange_rate,
        status=InvoiceStatus.DRAFT,
        notes=payload.notes
    )
    db.add(invoice)
    await db.flush() # Get invoice.id

    # 5. Insert Invoice Items
    for item_in in payload.items:
        item_subtotal = item_in.quantity * item_in.unit_price
        # Using item_in.iva_rate just for storage, general total uses global invoice iva_rate.
        item = InvoiceItem(
            invoice_id=invoice.id,
            service_id=item_in.service_id,
            description=item_in.description,
            quantity=item_in.quantity,
            unit_price=item_in.unit_price,
            iva_rate=item_in.iva_rate,
            subtotal=item_subtotal,
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(invoice)
    return invoice

async def emit_invoice_to_afip(db: AsyncSession, invoice_id: UUID, company_id: UUID) -> Invoice:
    # 1. Obtener invoice de DB
    inv_res = await db.execute(select(Invoice).where(Invoice.id == invoice_id, Invoice.company_id == company_id))
    invoice = inv_res.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if invoice.status != InvoiceStatus.DRAFT:
        if invoice.status == InvoiceStatus.EMITTED:
            raise HTTPException(status_code=400, detail="Invoice already emitted")
        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Invoice is cancelled")

    # 2. Obtener company
    comp_res = await db.execute(select(Company).where(Company.id == company_id))
    company = comp_res.scalar_one()

    # 3. VERIFICAR certificados y punto de venta
    if not company.afip_cert or not company.afip_key or not company.afip_point_of_sale:
        raise HTTPException(status_code=400, detail="Configurar certificados AFIP primero")
        
    # Obtener Client document
    cli_res = await db.execute(select(Client).where(Client.id == invoice.client_id))
    client = cli_res.scalar_one()

    # 4. Obtener TA
    ta = await get_access_ticket(company_id, db)

    # Re-calculate resolution to get cbte_tipo
    resolution = resolve_invoice_type(company.fiscal_condition, client.fiscal_condition)
    
    # 5. Obtener próximo número
    next_number = get_last_invoice_number(ta, company.afip_point_of_sale, resolution["cbte_tipo"])
    
    cuit_client = client.cuit_cuil_dni.replace("-", "").strip()
    doc_tipo = 80 if len(cuit_client) == 11 else 96 # 80=CUIT, 96=DNI

    # 6. Construir invoice_data
    invoice_data = {
        "cbte_tipo": resolution["cbte_tipo"],
        "point_of_sale": company.afip_point_of_sale,
        "client_doc_tipo": doc_tipo,
        "client_doc_nro": cuit_client,
        "cbte_desde": next_number,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "total": invoice.total,
        "subtotal": invoice.subtotal,
        "iva_amount": invoice.iva_amount,
        "iva_aplica": resolution["iva_aplica"],
        "iva_rate": invoice.iva_rate,
        "exchange_rate": invoice.exchange_rate
    }

    # 7. Autorizar Factura en AFIP
    # Note: If this fails with a Timeout or AFIP down, exceptions stop execution leaving invoice in draft
    resultado = authorize_invoice(ta, invoice_data)
    
    # 8. Modificar DB
    invoice.status = InvoiceStatus.EMITTED
    invoice.cae = resultado["cae"]
    
    # afip typically returns YYYYMMDD
    raw_venc = resultado["cae_expiry"]
    if raw_venc and len(raw_venc) == 8:
        try:
            year, month, day = int(raw_venc[0:4]), int(raw_venc[4:6]), int(raw_venc[6:8])
            invoice.cae_expiry = date(year, month, day)
        except ValueError:
            pass
            
    invoice.invoice_number = resultado["invoice_number"]
    invoice.afip_raw_response = resultado["raw_response"]
    
    await db.commit()
    await db.refresh(invoice)
    return invoice
