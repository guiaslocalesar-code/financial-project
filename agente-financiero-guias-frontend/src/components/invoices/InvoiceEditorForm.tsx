'use client'

/**
 * InvoiceEditorForm — Formulario del panel izquierdo del Split View
 *
 * Utiliza RHF para capturar datos de cliente, items, fechas y notas.
 * Sincronizado en tiempo real con el preview a través del hook useInvoiceEditor.
 */

import { useRef } from 'react'
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
    onUploadLogo?: (file: File) => void
    company?: any
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
    onUploadLogo,
    company,
    isReadOnly = false,
}: InvoiceEditorFormProps) {

    const logoInputRef = useRef<HTMLInputElement>(null)

    return (
        <div className="space-y-8 pb-20">
            {/* ── Sección 0: Empresa Emisora ── */}
            <div className="p-5 rounded-3xl bg-blue-50/20 border border-blue-100 flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-white border border-blue-100 flex items-center justify-center overflow-hidden shadow-sm">
                        {company?.imagen ? (
                            <img src={company.imagen} alt="Logo" className="w-full h-full object-contain" />
                        ) : (
                            <ArchiveBoxIcon className="w-6 h-6 text-blue-200" />
                        )}
                    </div>
                    <div>
                        <div className="text-[10px] font-bold text-blue-500 uppercase tracking-widest mb-0.5">Identidad Corporativa</div>
                        <div className="text-sm font-bold text-slate-700">{company?.name || 'Nombre Empresa'}</div>
                        <p className="text-[10px] text-slate-500">Logo y datos para el comprobante A4.</p>
                    </div>
                </div>
                
                {!isReadOnly && onUploadLogo && (
                    <>
                        <input 
                            type="file" 
                            className="hidden" 
                            ref={logoInputRef}
                            accept="image/*"
                            onChange={(e) => {
                                const file = e.target.files?.[0]
                                if (file) onUploadLogo(file)
                            }}
                        />
                        <button
                            type="button"
                            onClick={() => logoInputRef.current?.click()}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-xl transition-all"
                            title="Cambiar Logo"
                        >
                            <PlusIcon className="w-5 h-5" />
                        </button>
                    </>
                )}
            </div>

            {/* ── Sección 1: Cliente e Información Fiscal ── */}
            <div className="space-y-5">
                <div className="flex items-center gap-2 mb-2 text-blue-600 font-bold text-xs uppercase tracking-widest">
                    <UserIcon className="w-4 h-4" />
                    Información del Cliente
                </div>
                
                <div className="grid grid-cols-1 gap-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="sm:col-span-2">
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Buscar Cliente (Catálogo)</label>
                            <select
                                {...register('client_id')}
                                disabled={isReadOnly}
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500"
                            >
                                <option value="">Carga manual o seleccionar catálogo...</option>
                                {clients.map(c => (
                                    <option key={c.id} value={c.id}>{c.name} ({c.cuit_cuil_dni})</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Razón Social</label>
                            <input
                                type="text"
                                {...register('client_name')}
                                disabled={isReadOnly}
                                placeholder="Nombre completo o empresa"
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            />
                            {errors.client_name && <p className="mt-1 text-xs text-rose-500 font-medium">{errors.client_name.message}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">CUIT / CUIL / DNI</label>
                            <input
                                type="text"
                                {...register('client_cuit')}
                                disabled={isReadOnly}
                                placeholder="00-00000000-0"
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Condición IVA</label>
                            <select
                                {...register('client_fiscal_condition')}
                                disabled={isReadOnly}
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            >
                                <option value="RI">IVA Responsable Inscripto</option>
                                <option value="MONOTRIBUTO">Monotributo</option>
                                <option value="EXENTO">IVA Exento</option>
                                <option value="CONSUMIDOR_FINAL">Consumidor Final</option>
                            </select>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Domicilio</label>
                            <input
                                type="text"
                                {...register('client_address')}
                                disabled={isReadOnly}
                                placeholder="Calle y número..."
                                className="block w-full rounded-xl border-gray-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-50"
                            />
                        </div>

                        <div className="sm:col-span-2 pt-2 border-t border-gray-100"></div>

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
