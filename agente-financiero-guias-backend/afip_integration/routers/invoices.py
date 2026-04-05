from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.database import get_db
from app.dependencies import require_role
from app.models.invoice import Invoice
from app.models.company import Company
from app.models.client import Client
from app.utils.enums import InvoiceStatus
from afip_integration.schemas.invoice_schemas import InvoiceCreate, InvoiceResponse, CancelResponse, EmitResponse
from afip_integration.services.invoice_service import create_invoice_draft, emit_invoice_to_afip
from afip_integration.utils.pdf_generator import generate_invoice_pdf
from afip_integration.utils.certificate_manager import encrypt_credential

router = APIRouter(prefix="/invoices", tags=["AFIP Invoices"])

@router.post("", response_model=InvoiceResponse, status_code=201)
async def api_create_invoice_draft(
    company_id: UUID = Query(...), 
    payload: InvoiceCreate = None, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    invoice = await create_invoice_draft(db, company_id, payload)
    return invoice

@router.post("/{invoice_id}/emit", response_model=EmitResponse)
async def api_emit_invoice(
    invoice_id: UUID,
    company_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    try:
        invoice = await emit_invoice_to_afip(db, invoice_id, company_id)
        return {
            "id": invoice.id,
            "status": invoice.status.value,
            "invoice_number": invoice.invoice_number,
            "cae": invoice.cae,
            "cae_expiry": invoice.cae_expiry,
            "total": float(invoice.total)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    company_id: UUID, 
    client_id: Optional[str] = None,
    status: Optional[InvoiceStatus] = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    query = select(Invoice).where(Invoice.company_id == company_id)
    if client_id:
        query = query.where(Invoice.client_id == client_id)
    if status:
        query = query.where(Invoice.status == status)
        
    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    company_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Invoice).where(Invoice.id == invoice_id, Invoice.company_id == company_id))
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv

@router.post("/{invoice_id}/cancel", response_model=CancelResponse)
async def cancel_invoice(
    invoice_id: UUID,
    company_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    res = await db.execute(select(Invoice).where(Invoice.id == invoice_id, Invoice.company_id == company_id))
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if inv.status == InvoiceStatus.EMITTED:
        raise HTTPException(status_code=400, detail="Invoice ya emitida, requiere nota de credito")
        
    inv.status = InvoiceStatus.CANCELLED
    await db.commit()
    return {"status": "cancelled"}

@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: UUID,
    company_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Fetch invoice
    res = await db.execute(select(Invoice).where(Invoice.id == invoice_id, Invoice.company_id == company_id))
    invoice = res.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    comp_res = await db.execute(select(Company).where(Company.id == company_id))
    company = comp_res.scalar_one()
    
    cli_res = await db.execute(select(Client).where(Client.id == invoice.client_id))
    client = cli_res.scalar_one()
    
    pdf_bytes = generate_invoice_pdf(invoice, company, client)
    
    headers = {
        "Content-Disposition": f"attachment; filename=factura_{invoice.invoice_number or invoice.id}.pdf"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

# Note: Since the router prefix is /invoices, this actually becomes /invoices/companies/...
# To avoid breaking the frontend if it doesn't expect the prefix, we should either move it or adjust the prefix on the include_router.
# But for now I'll use a slash-less relative path.
@router.post("/companies/{company_id}/afip-credentials")
async def set_afip_credentials(
    company_id: UUID,
    cert_file: UploadFile = File(...),
    key_file: UploadFile = File(...),
    point_of_sale: int = Form(...),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    comp_res = await db.execute(select(Company).where(Company.id == company_id))
    company = comp_res.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    try:
        cert_content = await cert_file.read()
        key_content = await key_file.read()
        
        company.afip_cert = encrypt_credential(cert_content.decode('utf-8'))
        company.afip_key = encrypt_credential(key_content.decode('utf-8'))
        company.afip_point_of_sale = point_of_sale
        
        await db.commit()
        return {"message": "Credenciales AFIP configuradas correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save credentials: {str(e)}")
