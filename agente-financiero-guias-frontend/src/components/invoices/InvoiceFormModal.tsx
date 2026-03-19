'use client'

import { Fragment, useEffect, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/services/api'
import type { Invoice, Client } from '@/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useHoldingContext } from '@/context/HoldingContext'

const invoiceItemSchema = z.object({
    service_id: z.string().uuid('Debes seleccionar un servicio').optional().or(z.literal('')),
    description: z.string().min(1, 'La descripción es requerida'),
    quantity: z.number().min(0.01, 'Min > 0'),
    unit_price: z.number().min(0, 'Precio inválido'),
    iva_rate: z.number(),
})

const invoiceSchema = z.object({
    client_id: z.string().uuid('Debes seleccionar un cliente'),
    invoice_type: z.enum(['A', 'B', 'C']),
    due_date: z.string().min(1, 'El vencimiento es requerido'),
    currency: z.string(),
    notes: z.string().optional(),
    items: z.array(invoiceItemSchema).min(1, 'Debes agregar al menos un ítem'),
})

type InvoiceFormData = z.infer<typeof invoiceSchema>

interface InvoiceFormModalProps {
    isOpen: boolean
    onClose: () => void
}

export function InvoiceFormModal({ isOpen, onClose }: InvoiceFormModalProps) {
    const queryClient = useQueryClient()
    const { selectedCompany } = useHoldingContext()

    // Fetch clients for the dropdown
    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || res.data.clients || []) as Client[]
        },
        enabled: isOpen && !!selectedCompany,
    })

    // Fetch services for the items catalog
    const { data: services } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || [])
        },
        enabled: isOpen && !!selectedCompany,
    })

    const {
        register,
        control,
        handleSubmit,
        reset,
        watch,
        setValue,
        formState: { errors, isSubmitting },
    } = useForm<InvoiceFormData>({
        resolver: zodResolver(invoiceSchema),
        defaultValues: {
            invoice_type: 'C',
            currency: 'ARS',
            due_date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            items: [{ service_id: '', description: '', quantity: 1, unit_price: 0, iva_rate: 21 }],
        },
    })

    const { fields, append, remove } = useFieldArray({
        control,
        name: 'items',
    })

    const watchItems = watch('items')
    const [subtotal, setSubtotal] = useState(0)
    const [totalIva, setTotalIva] = useState(0)
    const [total, setTotal] = useState(0)

    useEffect(() => {
        let currentSubtotal = 0
        let currentIva = 0

        watchItems?.forEach((item: any) => {
            const itemSubtotal = (item.quantity || 0) * (item.unit_price || 0)
            const itemIva = itemSubtotal * ((item.iva_rate || 0) / 100)
            currentSubtotal += itemSubtotal
            currentIva += itemIva
        })

        setSubtotal(currentSubtotal)
        setTotalIva(currentIva)
        setTotal(currentSubtotal + currentIva)
    }, [watchItems])

    useEffect(() => {
        if (isOpen) {
            reset({
                invoice_type: 'C',
                currency: 'ARS',
                due_date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                items: [{ description: '', quantity: 1, unit_price: 0, iva_rate: 21 }],
            })
        }
    }, [isOpen, reset])

    const mutation = useMutation({
        mutationFn: (data: InvoiceFormData) => {
            if (!selectedCompany) throw new Error('No company selected')
            return api.invoices.create({
                ...data,
                company_id: selectedCompany.id,
            })
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['invoices', selectedCompany?.id] })
            onClose()
        },
        onError: (error: any) => {
            console.error('Error creating invoice:', error.response?.data || error.message)
        }
    })

    const onSubmit = (data: InvoiceFormData) => {
        mutation.mutate(data)
    }

    if (!selectedCompany) return null

    return (
        <Transition.Root show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={onClose}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto w-full">
                    <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 w-full max-w-4xl border border-gray-100 flex flex-col max-h-[90vh]">
                                <div className="absolute right-0 top-0 pr-4 pt-4 z-10">
                                    <button
                                        type="button"
                                        className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                                        onClick={onClose}
                                    >
                                        <XMarkIcon className="h-6 w-6" />
                                    </button>
                                </div>
                                
                                <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col flex-1 overflow-hidden">
                                    <div className="px-6 py-5 border-b border-gray-100 shrink-0">
                                        <Dialog.Title as="h3" className="text-xl font-semibold leading-6 text-gray-900">
                                            Nueva Factura (Borrador)
                                        </Dialog.Title>
                                        <p className="mt-1 text-sm text-gray-500">
                                            Creá un nuevo borrador. Podrás emitirla (AFIP) más adelante.
                                        </p>
                                    </div>
                                    
                                    <div className="flex-1 overflow-y-auto px-6 py-6">
                                        <div className="grid grid-cols-1 gap-y-6 gap-x-6 sm:grid-cols-6">
                                            {/* Client */}
                                            <div className="col-span-1 sm:col-span-3">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">Cliente</label>
                                                <select
                                                    {...register('client_id')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                >
                                                    <option value="">Seleccione un cliente...</option>
                                                    {clients?.map(client => (
                                                        <option key={client.id} value={client.id}>{client.name} ({client.cuit_cuil_dni})</option>
                                                    ))}
                                                </select>
                                                {errors.client_id && <p className="mt-1 text-xs text-rose-500">{errors.client_id.message}</p>}
                                            </div>

                                            {/* Invoice Type */}
                                            <div className="col-span-1 sm:col-span-1">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">Tipo</label>
                                                <select
                                                    {...register('invoice_type')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                >
                                                    <option value="A">A</option>
                                                    <option value="B">B</option>
                                                    <option value="C">C</option>
                                                </select>
                                            </div>

                                            {/* Due Date */}
                                            <div className="col-span-1 sm:col-span-2">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">Vencimiento</label>
                                                <input
                                                    type="date"
                                                    {...register('due_date')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                />
                                            </div>

                                            {/* Items */}
                                            <div className="col-span-1 sm:col-span-6 mt-4">
                                                <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
                                                    <h4 className="text-sm font-semibold text-gray-900">Detalle de la Factura</h4>
                                                    <button
                                                        type="button"
                                                        onClick={() => append({ description: '', quantity: 1, unit_price: 0, iva_rate: 21, service_id: '' })}
                                                        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium"
                                                    >
                                                        <PlusIcon className="w-4 h-4 mr-1" /> Agregar Ítem
                                                    </button>
                                                </div>

                                                <div className="space-y-3">
                                                    {fields.map((field, index) => (
                                                        <div key={field.id} className="flex gap-3 items-start bg-gray-50/50 p-3 rounded-xl border border-gray-100">
                                                            <div className="flex-1">
                                                                <select
                                                                    {...register(`items.${index}.service_id` as const)}
                                                                    onChange={(e) => {
                                                                        const svcId = e.target.value;
                                                                        const svc = services?.find((s: any) => s.id === svcId);
                                                                        if (svc) {
                                                                            setValue(`items.${index}.description` as const, svc.name);
                                                                        }
                                                                        register(`items.${index}.service_id`).onChange(e);
                                                                    }}
                                                                    className="block w-full rounded-lg border-0 py-2 px-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                                                                >
                                                                    <option value="">Seleccione un servicio...</option>
                                                                    {services?.map((svc: any) => (
                                                                        <option key={svc.id} value={svc.id}>{svc.name}</option>
                                                                    ))}
                                                                </select>
                                                                <input type="hidden" {...register(`items.${index}.description` as const)} />
                                                                {errors.items?.[index]?.service_id && <p className="mt-1 text-xs text-rose-500">{errors.items[index]?.service_id?.message}</p>}
                                                            </div>
                                                            <div className="w-24">
                                                                <input
                                                                    type="number"
                                                                    step="0.01"
                                                                    placeholder="Cant."
                                                                    {...register(`items.${index}.quantity` as const, { valueAsNumber: true })}
                                                                    className="block w-full rounded-lg border-0 py-2 px-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                                                                />
                                                            </div>
                                                            <div className="w-32">
                                                                <input
                                                                    type="number"
                                                                    step="0.01"
                                                                    placeholder="$ Precio Unit."
                                                                    {...register(`items.${index}.unit_price` as const, { valueAsNumber: true })}
                                                                    className="block w-full rounded-lg border-0 py-2 px-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                                                                />
                                                            </div>
                                                            <div className="w-20">
                                                                <select
                                                                    {...register(`items.${index}.iva_rate` as const, { valueAsNumber: true })}
                                                                    className="block w-full rounded-lg border-0 py-2 px-2 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                                                                >
                                                                    <option value={21}>21%</option>
                                                                    <option value={10.5}>10.5%</option>
                                                                    <option value={27}>27%</option>
                                                                    <option value={0}>0%</option>
                                                                </select>
                                                            </div>
                                                            <button
                                                                type="button"
                                                                onClick={() => remove(index)}
                                                                disabled={fields.length === 1}
                                                                className="mt-1.5 p-1 text-gray-400 hover:text-rose-500 disabled:opacity-30 disabled:hover:text-gray-400"
                                                            >
                                                                <TrashIcon className="w-5 h-5" />
                                                            </button>
                                                        </div>
                                                    ))}
                                                </div>
                                                {errors.items?.root && <p className="mt-2 text-sm text-rose-500">{errors.items.root.message}</p>}
                                            </div>

                                            {/* Notes */}
                                            <div className="col-span-1 sm:col-span-6">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">Notas Adicionales</label>
                                                <textarea
                                                    {...register('notes')}
                                                    rows={2}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    placeholder="Observaciones internas (no se imprimen en AFIP)"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Footer / Totals */}
                                    <div className="bg-gray-50 px-6 py-4 flex flex-col sm:flex-row items-center justify-between rounded-b-2xl border-t border-gray-100 shrink-0 gap-4">
                                        <div className="flex items-center gap-6 text-sm">
                                            <div>
                                                <span className="text-gray-500">Subtotal: </span>
                                                <span className="font-medium text-gray-900">${subtotal.toLocaleString('es-AR', {minimumFractionDigits: 2})}</span>
                                            </div>
                                            <div>
                                                <span className="text-gray-500">IVA: </span>
                                                <span className="font-medium text-gray-900">${totalIva.toLocaleString('es-AR', {minimumFractionDigits: 2})}</span>
                                            </div>
                                            <div className="text-base">
                                                <span className="text-gray-700 font-semibold">Total: </span>
                                                <span className="font-bold text-blue-600">${total.toLocaleString('es-AR', {minimumFractionDigits: 2})}</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 w-full sm:w-auto">
                                            <button
                                                type="button"
                                                className="w-full sm:w-auto inline-flex justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-colors"
                                                onClick={onClose}
                                            >
                                                Cancelar
                                            </button>
                                            <button
                                                type="submit"
                                                disabled={isSubmitting || mutation.isPending}
                                                className="w-full sm:w-auto inline-flex justify-center rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 disabled:opacity-50 transition-colors"
                                            >
                                                {(isSubmitting || mutation.isPending) ? 'Guardando...' : 'Crear Borrador'}
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
