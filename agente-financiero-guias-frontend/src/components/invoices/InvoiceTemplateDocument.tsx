'use client'

/**
 * InvoiceTemplateDocument — Documento A4 de Factura
 *
 * Adaptación directa del doc.html original a JSX.
 * Recibe InvoicePreviewData como prop y renderiza el comprobante completo.
 *
 * REGLAS DE DISEÑO:
 * - CSS aislado con prefijo .inv-doc-* para no contaminar el dashboard.
 * - La sección de ítems es dinámica (no posicionamiento absoluto).
 * - El resto del layout preserva la estructura fija del original.
 * - Pensado para ser capturado por html2canvas / window.print para PDF.
 */

import type { InvoicePreviewData, InvoiceItemComputed } from '@/types/invoices'

interface InvoiceTemplateDocumentProps {
    data: InvoicePreviewData
}

// ── Helpers ─────────────────────────────────────────────────────────────────

const formatCurrency = (val: number, currency: string = 'ARS') =>
    val.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const formatDate = (dateStr: string | null | undefined): string => {
    if (!dateStr) return '—'
    try {
        const [year, month, day] = dateStr.split('-').map(Number)
        return `${String(day).padStart(2, '0')}/${String(month).padStart(2, '0')}/${year}`
    } catch {
        return dateStr
    }
}

const INVOICE_TYPE_LABELS: Record<string, string> = {
    A: 'FACTURA A',
    B: 'FACTURA B',
    C: 'FACTURA C',
}

const FISCAL_LABELS: Record<string, string> = {
    RI: 'IVA Responsable Inscripto',
    MONOTRIBUTO: 'Monotributo',
    EXENTO: 'IVA Exento',
    CONSUMIDOR_FINAL: 'Consumidor Final',
}

// ── Componente Principal ────────────────────────────────────────────────────

export function InvoiceTemplateDocument({ data }: InvoiceTemplateDocumentProps) {
    const {
        invoice_type,
        invoice_number,
        point_of_sale,
        issue_date,
        due_date,
        currency,
        status,
        cae,
        cae_expiry,
        items,
        totals,
        company,
        client,
        notes,
    } = data

    // Formatear número de comprobante
    const formattedNumber = invoice_number
        ? `${String(point_of_sale || 1).padStart(5, '0')}-${invoice_number.padStart(8, '0')}`
        : 'BORRADOR'

    return (
        <>
            {/* Estilos aislados — prefijo inv-doc para no contaminar el dashboard */}
            <style jsx>{`
                .inv-doc-page {
                    width: 909px;
                    min-height: 1286px;
                    background: #fff;
                    color: #000;
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 11px;
                    line-height: 1.4;
                    position: relative;
                    box-sizing: border-box;
                    padding: 12mm 15mm 20mm 15mm;
                    display: flex;
                    flex-direction: column;
                    margin: 0 auto;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }

                /* ── Header con tipo de comprobante ── */
                .inv-doc-header {
                    display: grid;
                    grid-template-columns: 1fr auto 1fr;
                    gap: 0;
                    border: 1.5px solid #000;
                    margin-bottom: 6mm;
                }
                .inv-doc-header-left {
                    padding: 4mm;
                    border-right: 1.5px solid #000;
                    display: flex;
                    gap: 4mm;
                }
                .inv-doc-logo {
                    width: 80px;
                    height: 80px;
                    object-fit: contain;
                }
                .inv-doc-header-type {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding: 3mm 5mm;
                    border-right: 1.5px solid #000;
                    min-width: 22mm;
                }
                .inv-doc-header-type-letter {
                    font-size: 36px;
                    font-weight: bold;
                    line-height: 1;
                }
                .inv-doc-header-type-code {
                    font-size: 7px;
                    color: #333;
                    margin-top: 1mm;
                    text-align: center;
                }
                .inv-doc-header-right {
                    padding: 4mm;
                }

                .inv-doc-company-name {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 2mm;
                }
                .inv-doc-company-detail {
                    font-size: 9px;
                    color: #333;
                    line-height: 1.6;
                }

                .inv-doc-title {
                    font-size: 13px;
                    font-weight: bold;
                    margin-bottom: 1mm;
                }
                .inv-doc-number {
                    font-size: 15px;
                    font-weight: bold;
                    margin-bottom: 2mm;
                }
                .inv-doc-meta {
                    font-size: 9px;
                    color: #333;
                    line-height: 1.6;
                }

                /* ── Datos del cliente ── */
                .inv-doc-client-section {
                    border: 1px solid #ccc;
                    padding: 3mm 4mm;
                    margin-bottom: 6mm;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1mm 4mm;
                    font-size: 10px;
                }
                .inv-doc-client-section .label {
                    font-weight: bold;
                    color: #333;
                }
                .inv-doc-client-full {
                    grid-column: 1 / -1;
                }

                /* ── Tabla de ítems (DINÁMICO) ── */
                .inv-doc-items-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 6mm;
                    font-size: 10px;
                }
                .inv-doc-items-table thead th {
                    background: #f5f5f5;
                    border: 1px solid #ccc;
                    padding: 2mm 3mm;
                    text-align: left;
                    font-weight: bold;
                    font-size: 9px;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }
                .inv-doc-items-table thead th.right {
                    text-align: right;
                }
                .inv-doc-items-table tbody td {
                    border: 1px solid #ddd;
                    padding: 2mm 3mm;
                    vertical-align: top;
                }
                .inv-doc-items-table tbody td.right {
                    text-align: right;
                    font-variant-numeric: tabular-nums;
                }
                .inv-doc-items-table tbody tr:nth-child(even) {
                    background: #fafafa;
                }

                /* ── Totales ── */
                .inv-doc-totals {
                    display: flex;
                    justify-content: flex-end;
                    margin-bottom: 6mm;
                }
                .inv-doc-totals-box {
                    width: 65mm;
                    border: 1px solid #ccc;
                }
                .inv-doc-totals-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 1.5mm 3mm;
                    font-size: 10px;
                    border-bottom: 1px solid #eee;
                }
                .inv-doc-totals-row:last-child {
                    border-bottom: none;
                }
                .inv-doc-totals-row.total {
                    font-weight: bold;
                    font-size: 12px;
                    background: #f5f5f5;
                }

                /* ── Observaciones ── */
                .inv-doc-notes {
                    font-size: 9px;
                    color: #555;
                    border-top: 1px solid #eee;
                    padding-top: 3mm;
                    margin-bottom: 4mm;
                }

                /* ── CAE / Footer ── */
                .inv-doc-footer {
                    margin-top: auto;
                    border-top: 1.5px solid #000;
                    padding-top: 3mm;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    font-size: 9px;
                }
                .inv-doc-cae {
                    font-size: 10px;
                }
                .inv-doc-cae strong {
                    font-size: 11px;
                }

                /* ── Draft Watermark ── */
                .inv-doc-watermark {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-35deg);
                    font-size: 72px;
                    font-weight: bold;
                    color: rgba(0, 0, 0, 0.04);
                    pointer-events: none;
                    z-index: 1;
                    letter-spacing: 8px;
                    white-space: nowrap;
                }

                /* ── Print-specific ── */
                @media print {
                    .inv-doc-page {
                        margin: 0;
                        box-shadow: none;
                    }
                    .inv-doc-watermark {
                        display: none;
                    }
                }
            `}</style>

            <div className="inv-doc-page" id="invoice-document">
                {/* Watermark for DRAFT status */}
                {status === 'DRAFT' && (
                    <div className="inv-doc-watermark">BORRADOR</div>
                )}

                {/* ═══════════════ HEADER ═══════════════ */}
                <div className="inv-doc-header">
                    {/* Left: Company info */}
                    <div className="inv-doc-header-left">
                        {company.imagen && (
                            <img src={company.imagen} alt="Logo" className="inv-doc-logo" />
                        )}
                        <div>
                            <div className="inv-doc-company-name">
                                {company.name || 'Nombre de la Empresa'}
                            </div>
                            <div className="inv-doc-company-detail">
                                {company.address && <div>{company.address}</div>}
                                {company.phone && <div>Tel: {company.phone}</div>}
                                {company.email && <div>{company.email}</div>}
                                <div>
                                    Condición frente al IVA:{' '}
                                    {FISCAL_LABELS[company.fiscal_condition] || company.fiscal_condition}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Center: Invoice type letter */}
                    <div className="inv-doc-header-type">
                        <div className="inv-doc-header-type-letter">{invoice_type}</div>
                        <div className="inv-doc-header-type-code">
                            COD. {invoice_type === 'A' ? '01' : invoice_type === 'B' ? '06' : '11'}
                        </div>
                    </div>

                    {/* Right: Invoice number and dates */}
                    <div className="inv-doc-header-right">
                        <div className="inv-doc-title">
                            {INVOICE_TYPE_LABELS[invoice_type] || 'FACTURA'}
                        </div>
                        <div className="inv-doc-number">
                            Nº {formattedNumber}
                        </div>
                        <div className="inv-doc-meta">
                            <div>Fecha de Emisión: {formatDate(issue_date)}</div>
                            <div>Fecha de Vto. de Pago: {formatDate(due_date)}</div>
                            <div>CUIT: {company.cuit || '—'}</div>
                            <div>IIBB: {company.cuit || '—'}</div>
                            <div>Inicio de Actividades: —</div>
                        </div>
                    </div>
                </div>

                {/* ═══════════════ DATOS DEL CLIENTE ═══════════════ */}
                <div className="inv-doc-client-section">
                    <div className="inv-doc-client-full">
                        <span className="label">Razón Social: </span>
                        {client.name || 'Nombre del Cliente'}
                    </div>
                    <div>
                        <span className="label">CUIT/CUIL/DNI: </span>
                        {client.cuit_cuil_dni || '—'}
                    </div>
                    <div>
                        <span className="label">Condición IVA: </span>
                        {FISCAL_LABELS[client.fiscal_condition] || client.fiscal_condition || '—'}
                    </div>
                    <div className="inv-doc-client-full">
                        <span className="label">Domicilio: </span>
                        {[client.address, client.city, client.province].filter(Boolean).join(', ') || '—'}
                    </div>
                    <div>
                        <span className="label">Condición de venta: </span>
                        Contado
                    </div>
                </div>

                {/* ═══════════════ TABLA DE ÍTEMS ═══════════════ */}
                <table className="inv-doc-items-table">
                    <thead>
                        <tr>
                            <th style={{ width: '8%' }}>Código</th>
                            <th style={{ width: '42%' }}>Producto / Servicio</th>
                            <th className="right" style={{ width: '10%' }}>Cantidad</th>
                            <th className="right" style={{ width: '8%' }}>Ud. Medida</th>
                            <th className="right" style={{ width: '14%' }}>Precio Unit.</th>
                            <th className="right" style={{ width: '5%' }}>% IVA</th>
                            <th className="right" style={{ width: '13%' }}>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.length === 0 ? (
                            <tr>
                                <td colSpan={7} style={{ textAlign: 'center', padding: '6mm', color: '#aaa' }}>
                                    Agregá ítems a la factura...
                                </td>
                            </tr>
                        ) : (
                            items.map((item: InvoiceItemComputed, idx: number) => (
                                <tr key={idx}>
                                    <td>{item.service_id ? item.service_id.substring(0, 6) : '—'}</td>
                                    <td>{item.description || 'Sin descripción'}</td>
                                    <td className="right">{item.quantity}</td>
                                    <td className="right">unidades</td>
                                    <td className="right">$ {formatCurrency(item.unit_price, currency)}</td>
                                    <td className="right">{item.iva_rate}%</td>
                                    <td className="right">$ {formatCurrency(item._subtotal, currency)}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>

                {/* ═══════════════ TOTALES ═══════════════ */}
                <div className="inv-doc-totals">
                    <div className="inv-doc-totals-box">
                        <div className="inv-doc-totals-row">
                            <span>Subtotal:</span>
                            <span>$ {formatCurrency(totals.subtotal, currency)}</span>
                        </div>
                        {invoice_type !== 'C' && (
                            <div className="inv-doc-totals-row">
                                <span>IVA 21%:</span>
                                <span>$ {formatCurrency(totals.iva, currency)}</span>
                            </div>
                        )}
                        <div className="inv-doc-totals-row total">
                            <span>Total ({currency}):</span>
                            <span>$ {formatCurrency(totals.total, currency)}</span>
                        </div>
                    </div>
                </div>

                {/* ═══════════════ OBSERVACIONES ═══════════════ */}
                {notes && (
                    <div className="inv-doc-notes">
                        <strong>Observaciones:</strong> {notes}
                    </div>
                )}

                {/* ═══════════════ FOOTER / CAE ═══════════════ */}
                <div className="inv-doc-footer">
                    {cae ? (
                        <div className="inv-doc-cae">
                            <strong>CAE Nº: {cae}</strong>
                            <div>Fecha de Vto. de CAE: {formatDate(cae_expiry || null)}</div>
                        </div>
                    ) : (
                        <div className="inv-doc-cae" style={{ color: '#aaa' }}>
                            CAE: Pendiente de emisión
                        </div>
                    )}
                    <div style={{ textAlign: 'right', fontSize: '8px', color: '#999' }}>
                        Comprobante generado electrónicamente
                    </div>
                </div>
            </div>
        </>
    )
}

// ── Datos mock para testeo rápido ───────────────────────────────────────────

export const MOCK_INVOICE_PREVIEW: InvoicePreviewData = {
    invoice_type: 'C',
    invoice_number: null,
    point_of_sale: 1,
    issue_date: '2026-03-31',
    due_date: '2026-04-15',
    currency: 'ARS',
    status: 'DRAFT',
    cae: null,
    cae_expiry: null,
    notes: '',
    items: [
        {
            service_id: 'svc-001',
            description: 'Servicio de Marketing Digital',
            quantity: 1,
            unit_price: 85000,
            iva_rate: 21,
            _subtotal: 85000,
            _iva_amount: 17850,
        },
        {
            service_id: 'svc-002',
            description: 'Gestión de Redes Sociales',
            quantity: 1,
            unit_price: 45000,
            iva_rate: 21,
            _subtotal: 45000,
            _iva_amount: 9450,
        },
    ],
    totals: {
        subtotal: 130000,
        iva: 27300,
        total: 157300,
    },
    company: {
        name: 'Guias Locales S.A.',
        cuit: '30-71234567-0',
        fiscal_condition: 'RI',
        afip_point_of_sale: 1,
        address: 'Av. Corrientes 1234, CABA',
        phone: '(011) 5555-1234',
        email: 'admin@guiaslocales.com.ar',
    },
    client: {
        name: 'Acme Corporation S.R.L.',
        cuit_cuil_dni: '30-98765432-1',
        fiscal_condition: 'RI',
        address: 'Av. Santa Fe 5678',
        city: 'CABA',
        province: 'Buenos Aires',
    },
}
