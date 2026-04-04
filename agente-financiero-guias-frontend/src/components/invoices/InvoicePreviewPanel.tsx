'use client'

/**
 * InvoicePreviewPanel — Panel derecho del Split View
 *
 * Contiene el "sandbox" gris donde se muestra el documento A4 centrado
 * con controles de zoom. Aísla visualmente el template del resto del dashboard.
 */

import { forwardRef } from 'react'
import {
    InvoiceTemplateDocument,
    MOCK_INVOICE_PREVIEW,
} from '@/components/invoices/InvoiceTemplateDocument'
import type { InvoicePreviewData } from '@/types/invoices'
import {
    MagnifyingGlassPlusIcon,
    MagnifyingGlassMinusIcon,
} from '@heroicons/react/24/outline'
import { useState } from 'react'

interface InvoicePreviewPanelProps {
    data: InvoicePreviewData
}

const ZOOM_LEVELS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
const DEFAULT_ZOOM_INDEX = 2 // 0.7

export const InvoicePreviewPanel = forwardRef<HTMLDivElement, InvoicePreviewPanelProps>(
    function InvoicePreviewPanel({ data }, ref) {
        const [zoomIndex, setZoomIndex] = useState(DEFAULT_ZOOM_INDEX)
        const zoom = ZOOM_LEVELS[zoomIndex]

        const zoomIn = () => setZoomIndex((prev) => Math.min(prev + 1, ZOOM_LEVELS.length - 1))
        const zoomOut = () => setZoomIndex((prev) => Math.max(prev - 1, 0))

        return (
            <div className="flex flex-col h-full bg-gray-100 border-l border-gray-200 print:bg-white print:border-none print:h-auto print:block">
                {/* Zoom controls */}
                <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-50 shrink-0 print:hidden">
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Vista previa
                    </span>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={zoomOut}
                            disabled={zoomIndex === 0}
                             type="button"
                            className="p-1 rounded hover:bg-gray-200 disabled:opacity-30 transition-colors"
                            title="Reducir"
                        >
                            <MagnifyingGlassMinusIcon className="w-4 h-4 text-gray-600" />
                        </button>
                        <span className="text-xs font-mono text-gray-600 min-w-[3rem] text-center">
                            {Math.round(zoom * 100)}%
                        </span>
                        <button
                            onClick={zoomIn}
                            disabled={zoomIndex === ZOOM_LEVELS.length - 1}
                             type="button"
                            className="p-1 rounded hover:bg-gray-200 disabled:opacity-30 transition-colors"
                            title="Ampliar"
                        >
                            <MagnifyingGlassPlusIcon className="w-4 h-4 text-gray-600" />
                        </button>
                    </div>
                </div>

                {/* Document sandbox */}
                <div className="flex-1 overflow-auto p-6 flex justify-center print:p-0 print:overflow-visible print:block">
                    <div
                        ref={ref}
                        className="print:!transform-none print:!m-0"
                        style={{
                            transform: `scale(${zoom})`,
                            transformOrigin: 'top center',
                        }}
                    >
                        <div
                            className="shadow-2xl print:shadow-none"
                            style={{ borderRadius: '2px' }}
                        >
                            <InvoiceTemplateDocument data={data} />
                        </div>
                    </div>
                </div>
            </div>
        )
    }
)
