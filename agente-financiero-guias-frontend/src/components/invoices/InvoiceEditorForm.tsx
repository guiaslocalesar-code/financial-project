'use client'

/**
 * InvoiceEditorForm — Formulario del panel izquierdo del Split View
 *
 * Utiliza RHF para capturar datos de cliente, items, fechas y notas.
 * Sincronizado en tiempo real con el preview a través del hook useInvoiceEditor.
 */

import { PlusIcon, TrashIcon, UserIcon, CalendarIcon, ArchiveBoxIcon } from '@heroicons/react/24/outline'
import type { 
    UseFormRegister, 
    Control, 
    FieldErrors, 
    UseFieldArrayAppend, 
    UseFieldArrayRemove,
    FieldArrayWithId,
    UseFormSetValue
} from 'react-hook-form'
import type { InvoiceFormValues } from '@/types/invoices'
import type { Client, Service } from '@/types'

interface InvoiceEditorFormProps {
    register: UseFormRegister<InvoiceFormValues>
    control: Control<InvoiceFormValues>
    errors: FieldErrors<InvoiceFormValues>
    fields: FieldArrayWithId<InvoiceFormValues, 'items'>[]
    append: UseFieldArrayAppend<InvoiceFormValues, 'items'>
    remove: UseFieldArrayRemove
    clients: Client[]
    services: Service[]
    setValue: UseFormSetValue<InvoiceFormValues>
    isReadOnly?: boolean
}

export function InvoiceEditorForm({
    register,
    control,
    errors,
    fields,
    append,
    remove,
    clients,
    services,
    setValue,
    isReadOnly = false,
}: InvoiceEditorFormProps) {

    return (
        <div className="space-y-8 pb-20">
            {/* ── Sección 1: Cliente y Datos de Cabecera ── */}
            <div className="space-y-5">
                <div className="flex items-center gap-2 mb-2 text-blue-600 font-bold text-xs uppercase tracking-widest">
                    <UserIcon className="w-4 h-4" />
                    Información del Cliente
                </div>
                
                <div className="grid grid-cols-1 gap-4">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Cliente</label>
                        <select
                            {...register('client_id')}
                            disabled={isReadOnly}
                            className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500"
                        >
                            <option value="">Seleccionar cliente...</option>
                            {clients.map(c => (
                                <option key={c.id} value={c.id}>{c.name} ({c.cuit_cuil_dni})</option>
                            ))}
                        </select>
                        {errors.client_id && <p className="mt-1 text-xs text-rose-500 font-medium">{errors.client_id.message}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Tipo Factura</label>
                            <select
                                {...register('invoice_type')}
                                disabled={isReadOnly}
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            >
                                <option value="A">Factura A</option>
                                <option value="B">Factura B</option>
                                <option value="C">Factura C</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Punto de Venta</label>
                            <input
                                type="number"
                                {...register('point_of_sale', { valueAsNumber: true })}
                                disabled={isReadOnly}
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Sección 2: Fechas y Moneda ── */}
            <div className="space-y-5">
                <div className="flex items-center gap-2 mb-2 text-blue-600 font-bold text-xs uppercase tracking-widest">
                    <CalendarIcon className="w-4 h-4" />
                    Fechas y Moneda
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Fecha Emisión</label>
                        <input
                            type="date"
                            {...register('issue_date')}
                            disabled={isReadOnly}
                            className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Vencimiento</label>
                        <input
                            type="date"
                            {...register('due_date')}
                            disabled={isReadOnly}
                            className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Moneda</label>
                        <select
                            {...register('currency')}
                            disabled={isReadOnly}
                            className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                        >
                            <option value="ARS">Peso Argentino (ARS)</option>
                            <option value="USD">Dólar Estadounidense (USD)</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* ── Sección 3: Ítems ── */}
            <div className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-blue-600 font-bold text-xs uppercase tracking-widest">
                        <ArchiveBoxIcon className="w-4 h-4" />
                        Detalle de Ítems
                    </div>
                    {!isReadOnly && (
                        <button
                            type="button"
                            onClick={() => append({ service_id: '', description: '', quantity: 1, unit_price: 0, iva_rate: 21 })}
                            className="inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
                        >
                            <PlusIcon className="w-3.5 h-3.5" /> AGREGAR ÍTEM
                        </button>
                    )}
                </div>

                <div className="space-y-4">
                    {fields.map((field, index) => (
                        <div key={field.id} className="relative p-4 rounded-2xl bg-gray-50/50 border border-gray-100 group transition-all hover:bg-white hover:shadow-md">
                            {!isReadOnly && fields.length > 1 && (
                                <button
                                    type="button"
                                    onClick={() => remove(index)}
                                    className="absolute -top-2 -right-2 p-1.5 bg-white border border-gray-200 rounded-full text-gray-400 hover:text-rose-500 shadow-sm transition-all opacity-0 group-hover:opacity-100"
                                >
                                    <TrashIcon className="w-4 h-4" />
                                </button>
                            )}
                            
                            <div className="grid grid-cols-1 gap-3">
                                <div>
                                    <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1">Servicio / Producto</label>
                                    <select
                                        {...register(`items.${index}.service_id` as const)}
                                        disabled={isReadOnly}
                                        onChange={(e) => {
                                            const svcId = e.target.value
                                            const svc = services.find(s => s.id === svcId)
                                            if (svc) {
                                                setValue(`items.${index}.description`, svc.name)
                                            }
                                            register(`items.${index}.service_id`).onChange(e)
                                        }}
                                        className="block w-full rounded-lg border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-transparent"
                                    >
                                        <option value="">Selección manual o catálogo...</option>
                                        {services.map(s => (
                                            <option key={s.id} value={s.id}>{s.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <input
                                    type="text"
                                    placeholder="Descripción del concepto..."
                                    {...register(`items.${index}.description` as const)}
                                    disabled={isReadOnly}
                                    className="block w-full rounded-lg border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-transparent"
                                />
                                
                                <div className="grid grid-cols-3 gap-3">
                                    <div>
                                        <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1">Cant.</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register(`items.${index}.quantity` as const, { valueAsNumber: true })}
                                            disabled={isReadOnly}
                                            className="block w-full rounded-lg border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm py-1.5 disabled:bg-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1">Precio Unit.</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register(`items.${index}.unit_price` as const, { valueAsNumber: true })}
                                            disabled={isReadOnly}
                                            className="block w-full rounded-lg border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm py-1.5 disabled:bg-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1">% IVA</label>
                                        <select
                                            {...register(`items.${index}.iva_rate` as const, { valueAsNumber: true })}
                                            disabled={isReadOnly}
                                            className="block w-full rounded-lg border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm py-1.5 disabled:bg-transparent"
                                        >
                                            <option value={21}>21%</option>
                                            <option value={10.5}>10.5%</option>
                                            <option value={27}>27%</option>
                                            <option value={0}>0%</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Sección 4: Notas ── */}
            <div className="space-y-4">
                <label className="block text-sm font-semibold text-gray-700">Observaciones Internas</label>
                <textarea
                    {...register('notes')}
                    disabled={isReadOnly}
                    rows={3}
                    placeholder="Notas que no se imprimen en AFIP..."
                    className="block w-full rounded-2xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-gray-50"
                />
            </div>
        </div>
    )
}
