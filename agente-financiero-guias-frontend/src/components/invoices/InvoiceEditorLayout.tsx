'use client'

/**
 * InvoiceEditorLayout — Layout Split View para el editor de facturas.
 *
 * Panel izquierdo: formulario/children
 * Panel derecho: preview A4
 *
 * Se adapta dentro del layout existente del Holding (sidebar + header ya están).
 * Solo ocupa el area de `main > children`.
 */

import { useRef, type ReactNode } from 'react'
import { InvoicePreviewPanel } from '@/components/invoices/InvoicePreviewPanel'
import type { InvoicePreviewData } from '@/types/invoices'

interface InvoiceEditorLayoutProps {
    previewData: InvoicePreviewData
    children: ReactNode // The form goes here
}

export function InvoiceEditorLayout({ previewData, children }: InvoiceEditorLayoutProps) {
    const documentRef = useRef<HTMLDivElement>(null)

    return (
        <div
            className="flex flex-col lg:flex-row print:block print:h-auto print:m-0"
            style={{
                /* Fill all available space under the header, accounting for the p-4/p-6/p-8 
                   padding in the holding layout main area */
                height: 'calc(100vh - 80px)',
                margin: '-1rem -1.5rem',  /* Counteract parent padding for full bleed */
            }}
        >
            {/* ── Left: Form panel (scrollable) ── */}
            <div className="w-full lg:w-[480px] xl:w-[520px] shrink-0 overflow-y-auto bg-white border-r border-gray-200 print:hidden">
                <div className="p-6">
                    {children}
                </div>
            </div>

            {/* ── Right: Preview panel (fills remaining) ── */}
            <div className="flex-1 hidden lg:block min-w-0 print:block print:p-0">
                <InvoicePreviewPanel
                    ref={documentRef}
                    data={previewData}
                />
            </div>
        </div>
    )
}
