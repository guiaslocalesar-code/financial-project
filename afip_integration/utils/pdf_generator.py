import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid

def generate_invoice_pdf(invoice, company, client) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"FACTURA {invoice.invoice_type}")
    
    # Company info
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Empresa: {company.name}")
    c.drawString(50, height - 100, f"CUIT: {company.cuit}")
    c.drawString(50, height - 120, f"Condición Frente al IVA: {company.fiscal_condition.value}")
    
    # Client info
    c.drawString(300, height - 80, f"Cliente: {client.name}")
    c.drawString(300, height - 100, f"CUIT/DNI: {client.cuit_cuil_dni}")
    c.drawString(300, height - 120, f"Condición IVA: {client.fiscal_condition.value}")
    
    # Invoice numbers
    c.drawString(50, height - 160, f"Punto de Venta: {invoice.point_of_sale:04d}")
    c.drawString(50, height - 180, f"Comprobante Nro: {invoice.invoice_number or 'Borrador'}")
    c.drawString(300, height - 160, f"Fecha de Emisión: {invoice.issue_date}")
    
    # Line
    c.line(50, height - 200, width - 50, height - 200)
    
    # Items (Mockup list)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 220, "Descripción")
    c.drawString(300, height - 220, "Cant.")
    c.drawString(350, height - 220, "Precio U.")
    c.drawString(450, height - 220, "Subtotal")
    
    c.setFont("Helvetica", 10)
    y = height - 240
    for item in invoice.items:
        c.drawString(50, y, str(item.description)[:40])
        c.drawString(300, y, str(item.quantity))
        c.drawString(350, y, f"${item.unit_price:,.2f}")
        c.drawString(450, y, f"${item.subtotal:,.2f}")
        y -= 20
        
    # Totals
    c.line(50, y - 10, width - 50, y - 10)
    y -= 30
    c.drawString(350, y, f"Subtotal: ${invoice.subtotal:,.2f}")
    y -= 20
    if invoice.iva_amount is not None and invoice.iva_amount > 0:
        c.drawString(350, y, f"IVA ({invoice.iva_rate}%): ${invoice.iva_amount:,.2f}")
    else:
        c.drawString(350, y, "IVA: $0.00")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, f"Total: ${invoice.total:,.2f}")
    
    # AFIP Footers
    if invoice.cae:
        c.setFont("Helvetica", 10)
        y -= 50
        c.drawString(50, y, f"CAE Nro: {invoice.cae}")
        c.drawString(50, y - 20, f"Fecha Vto. CAE: {invoice.cae_expiry}")
        
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
