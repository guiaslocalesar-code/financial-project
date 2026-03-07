from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.company import Company
from app.models.client import Client
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.services.afip_service import afip_service
from app.utils.enums import InvoiceStatus

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=InvoiceResponse)
async def create_invoice_draft(invoice_in: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    # Calculate totals
    subtotal = sum(item.unit_price * item.quantity for item in invoice_in.items)
    iva_rate = 21.0 # Default
    iva_amount = subtotal * (iva_rate / 100)
    total = subtotal + iva_amount

    invoice = Invoice(
        **invoice_in.model_dump(exclude={"items"}),
        subtotal=subtotal,
        iva_rate=iva_rate,
        iva_amount=iva_amount,
        total=total,
        status=InvoiceStatus.DRAFT
    )
    db.add(invoice)
    await db.flush() # Get invoice ID

    for item_in in invoice_in.items:
        item_subtotal = item_in.unit_price * item_in.quantity
        item = InvoiceItem(
            **item_in.model_dump(),
            invoice_id=invoice.id,
            subtotal=item_subtotal
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(invoice)
    return invoice

@router.post("/{invoice_id}/emit")
async def emit_invoice(invoice_id: UUID, db: AsyncSession = Depends(get_db)):
    # 1. Fetch invoice and relations
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status == InvoiceStatus.EMITTED:
        raise HTTPException(status_code=400, detail="Invoice already emitted")

    # 2. Fetch company and client data
    comp_res = await db.execute(select(Company).where(Company.id == invoice.company_id))
    company = comp_res.scalar_one()
    
    cli_res = await db.execute(select(Client).where(Client.id == invoice.client_id))
    client = cli_res.scalar_one()

    # 3. Call AFIP Service
    afip_response = await afip_service.emit_invoice(
        company_data={"cuit": company.cuit, "point_of_sale": company.afip_point_of_sale},
        invoice_data={"invoice_type": invoice.invoice_type, "client_cuit": client.cuit_cuil_dni},
        items=[] # Simplified for now
    )

    if afip_response["status"] == "success":
        invoice.invoice_number = afip_response["invoice_number"]
        invoice.cae = afip_response["cae"]
        invoice.cae_expiry = afip_response["cae_expiry"]
        invoice.afip_raw_response = afip_response["raw_response"]
        invoice.status = InvoiceStatus.EMITTED
        await db.commit()
        return {"message": "Invoice emitted successfully", "cae": invoice.cae, "number": invoice.invoice_number}
    else:
        raise HTTPException(status_code=500, detail=f"AFIP Error: {afip_response.get('error')}")

@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.company_id == company_id))
    return result.scalars().all()
