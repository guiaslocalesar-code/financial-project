/**
 * Invoice Editor Types
 * Shapes that gobiernan el flujo de creación/edición/preview de facturas.
 * Separados de types/index.ts para mantener el módulo aislado.
 */

// ── Item de factura (línea de detalle) ──────────────────────────────────────

export interface InvoiceItemDraft {
    service_id?: string
    description: string
    quantity: number
    unit_price: number
    iva_rate: number
}

// ── Snapshot de datos de empresa para el preview A4 ─────────────────────────

export interface CompanySnapshot {
    name: string
    cuit: string
    fiscal_condition: string
    afip_point_of_sale?: number
    address?: string
    phone?: string
    email?: string
    imagen?: string // logo URL
}

// ── Snapshot de datos de cliente para el preview A4 ─────────────────────────

export interface ClientSnapshot {
    name: string
    cuit_cuil_dni: string
    fiscal_condition: string
    address?: string
    city?: string
    province?: string
    email?: string
    phone?: string
}

// ── Totales calculados al vuelo ─────────────────────────────────────────────

export interface InvoiceComputedTotals {
    subtotal: number
    iva: number
    total: number
}

// ── Item calculado (con subtotal derivado) ──────────────────────────────────

export interface InvoiceItemComputed extends InvoiceItemDraft {
    _subtotal: number
    _iva_amount: number
}

// ── Contexto completo que el template A4 necesita para renderizar ────────────

export interface InvoicePreviewData {
    // Datos de cabecera
    invoice_type: 'A' | 'B' | 'C'
    invoice_number?: string | null
    point_of_sale?: number
    issue_date: string
    due_date: string
    currency: string
    status: 'DRAFT' | 'EMITTED' | 'CANCELLED'
    notes?: string

    // CAE (solo si EMITTED)
    cae?: string | null
    cae_expiry?: string | null

    // Items calculados
    items: InvoiceItemComputed[]

    // Totales
    totals: InvoiceComputedTotals

    // Snapshots de entidades relacionadas
    company: CompanySnapshot
    client: ClientSnapshot
}

// ── Payload que se envía al backend para crear/editar ───────────────────────

export interface InvoiceCreatePayload {
    company_id: string
    client_id: string
    invoice_type: 'A' | 'B' | 'C'
    point_of_sale: number
    issue_date?: string
    due_date?: string
    currency: string
    exchange_rate?: number
    notes?: string
    items: InvoiceItemDraft[]
}

// ── Datos del formulario (lo que maneja React Hook Form) ────────────────────

export interface InvoiceFormValues {
    client_id: string
    invoice_type: 'A' | 'B' | 'C'
    point_of_sale: number
    issue_date: string
    due_date: string
    currency: string
    notes: string
    items: InvoiceItemDraft[]
}
