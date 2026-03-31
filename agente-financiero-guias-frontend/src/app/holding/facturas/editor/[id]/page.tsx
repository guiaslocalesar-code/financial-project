'use client'

/**
 * /holding/facturas/editor/[id] — Edición de factura existente
 *
 * Carga la factura desde el backend por ID y renderiza el split view.
 * Sincronizado en tiempo real con el preview a través del hook useInvoiceEditor.
 */

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { InvoiceEditorLayout } from '@/components/invoices/InvoiceEditorLayout'
import { InvoiceEditorForm } from '@/components/invoices/InvoiceEditorForm'
import { useInvoiceEditor } from '@/hooks/useInvoiceEditor'
import { useHoldingContext } from '@/context/HoldingContext'
import { api } from '@/services/api'
import { 
    ArrowLeftIcon, 
    DocumentTextIcon, 
    CloudArrowUpIcon, 
    CheckIcon,
    ArrowDownTrayIcon,
    EnvelopeIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import type { Invoice } from '@/types'

export default function InvoiceEditorByIdPage() {
    const params = useParams()
    const router = useRouter()
    const invoiceId = params.id as string
    const { selectedCompany } = useHoldingContext()

    // 1. Fetch initial invoice data
    const { data: invoiceRaw, isLoading: loadingInvoice } = useQuery({
        queryKey: ['invoice', invoiceId],
        queryFn: async () => {
            if (!selectedCompany || !invoiceId) return null
            const res = await api.invoices.list(selectedCompany.id)
            const list = Array.isArray(res.data) ? res.data : (res.data.data || []) as Invoice[]
            return list.find(inv => inv.id === invoiceId) || null
        },
        enabled: !!selectedCompany && !!invoiceId,
    })

    // 2. Setup hook with initial data
    const {
        register,
        control,
        errors,
        fields,
        append,
        remove,
        previewData,
        clients,
        services,
        onSubmit,
        onEmit,
        setValue,
        isSubmitting,
        isValid
    } = useInvoiceEditor({
        initialData: invoiceRaw,
        onSuccess: () => {
            router.push('/holding/facturas')
        }
    })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <DocumentTextIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
            </div>
        )
    }

    if (loadingInvoice) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
            </div>
        )
    }

    const isReadOnly = invoiceRaw?.status === 'EMITTED' || invoiceRaw?.status === 'CANCELLED'

    return (
        <form onSubmit={onSubmit}>
            <InvoiceEditorLayout previewData={previewData}>
                {/* ── Header ── */}
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100 sticky top-0 bg-white z-10 print:hidden">
                    <Link
                        href="/holding/facturas"
                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                        title="Volver al listado"
                    >
                        <ArrowLeftIcon className="w-5 h-5 text-gray-500" />
                    </Link>
                    <div className="flex-1">
                        <h1 className="text-xl font-bold text-gray-900">
                            {previewData.invoice_number
                                ? `Factura ${previewData.invoice_type} - ${previewData.invoice_number}`
                                : 'Borrador de Factura'}
                        </h1>
                        <p className="text-sm text-gray-500">{selectedCompany.name}</p>
                    </div>
                    {isReadOnly && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/50">
                            <CheckIcon className="w-3 h-3 mr-1" /> Emitida
                        </span>
                    )}
                </div>

                {/* ── Form Content ── */}
                <div className="print:hidden">
                    <InvoiceEditorForm
                        register={register}
                        control={control}
                        errors={errors}
                        fields={fields}
                        append={append}
                        remove={remove}
                        clients={clients}
                        services={services}
                        setValue={setValue}
                        isReadOnly={isReadOnly}
                    />
                </div>

                {/* ── Toolbar Inferior ── */}
                <div className="fixed bottom-0 left-0 w-full lg:w-[480px] xl:w-[520px] bg-white/80 backdrop-blur-md border-t border-gray-100 p-4 flex items-center justify-between z-20 print:hidden">
                    <div className="flex items-center gap-2">
                        {isReadOnly ? (
                            <button
                                type="button"
                                onClick={() => window.print()}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
                            >
                                <ArrowDownTrayIcon className="w-3.5 h-3.5 text-gray-500" /> 
                                PDF
                            </button>
                        ) : (
                            isValid ? (
                                <span className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100">
                                    <CheckIcon className="w-3 h-3" /> LISTO
                                </span>
                            ) : (
                                <span className="flex items-center gap-1.5 text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-full border border-amber-100">
                                    PENDIENTE
                                </span>
                            )
                        )}
                        <button
                            type="button"
                            onClick={() => alert('Próximamente: Integración con SendGrid/Resend')}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
                        >
                            <EnvelopeIcon className="w-3.5 h-3.5 text-gray-500" />
                            Email
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        {!isReadOnly && (
                            <>
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-all focus:ring-2 focus:ring-gray-200 outline-none disabled:opacity-50"
                                >
                                    {isSubmitting ? '...' : 'Guardar'}
                                </button>
                                
                                <button
                                    type="button"
                                    onClick={() => {
                                        if (confirm('¿Estás seguro de emitir esta factura ante AFIP? Esta acción es irreversible.')) {
                                            onEmit();
                                        }
                                    }}
                                    disabled={isSubmitting || !isValid}
                                    className="btn-primary py-2 px-4 shadow-blue-500/20 disabled:scale-100 disabled:opacity-50"
                                >
                                    <CloudArrowUpIcon className="w-4 h-4" />
                                    Emitir (AFIP)
                                </button>
                            </>
                        )}
                        {isReadOnly && (
                             <Link 
                                href="/holding/facturas"
                                className="inline-flex items-center justify-center gap-2 px-5 py-2 rounded-xl text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-all focus:ring-2 focus:ring-gray-200 outline-none"
                            >
                                Cerrar
                            </Link>
                        )}
                    </div>
                </div>
            </InvoiceEditorLayout>
        </form>
    )
}
