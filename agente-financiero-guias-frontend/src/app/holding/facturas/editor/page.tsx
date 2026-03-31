'use client'

/**
 * /holding/facturas/editor — Creación de nueva factura
 *
 * En esta fase muestra el split view con datos mock.
 * Se conectará en fase 3 al formulario reactivo real.
 */

import { InvoiceEditorLayout } from '@/components/invoices/InvoiceEditorLayout'
import { InvoiceEditorForm } from '@/components/invoices/InvoiceEditorForm'
import { useInvoiceEditor } from '@/hooks/useInvoiceEditor'
import { useHoldingContext } from '@/context/HoldingContext'
import { ArrowLeftIcon, DocumentTextIcon, CheckIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function InvoiceEditorPage() {
    const { selectedCompany } = useHoldingContext()
    const router = useRouter()

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
        setValue,
        isSubmitting,
        isValid
    } = useInvoiceEditor({
        onSuccess: () => {
            router.push('/holding/facturas')
        }
    })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <DocumentTextIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para crear una factura, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <form onSubmit={onSubmit}>
            <InvoiceEditorLayout previewData={previewData}>
                {/* ── Header ── */}
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100 sticky top-0 bg-white z-10">
                    <Link
                        href="/holding/facturas"
                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                        title="Volver al listado"
                    >
                        <ArrowLeftIcon className="w-5 h-5 text-gray-500" />
                    </Link>
                    <div className="flex-1">
                        <h1 className="text-xl font-bold text-gray-900">Nueva Factura</h1>
                        <p className="text-sm text-gray-500">{selectedCompany.name}</p>
                    </div>
                </div>

                {/* ── Form Content ── */}
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
                />

                {/* ── Toolbar Inferior (Sticky en el panel izquierdo) ── */}
                <div className="fixed bottom-0 left-0 w-full lg:w-[480px] xl:w-[520px] bg-white/80 backdrop-blur-md border-t border-gray-100 p-4 flex items-center justify-between z-20">
                    <div className="flex items-center gap-2">
                        {isValid ? (
                            <span className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100">
                                <CheckIcon className="w-3 h-3" /> LISTO PARA EMITIR
                            </span>
                        ) : (
                            <span className="flex items-center gap-1.5 text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-full border border-amber-100">
                                PENDIENTE DE DATOS
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        <Link 
                            href="/holding/facturas"
                            className="px-4 py-2 text-sm font-semibold text-gray-500 hover:text-gray-700"
                        >
                            Cancelar
                        </Link>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="btn-primary py-2 px-6 shadow-blue-500/20"
                        >
                            <CloudArrowUpIcon className="w-4 h-4" />
                            {isSubmitting ? 'Guardando...' : 'Guardar Borrador'}
                        </button>
                    </div>
                </div>
            </InvoiceEditorLayout>
        </form>
    )
}
