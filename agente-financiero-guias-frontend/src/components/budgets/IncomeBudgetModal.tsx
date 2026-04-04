'use client'

import { Fragment, useState, useMemo } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, DocumentTextIcon, ReceiptPercentIcon } from '@heroicons/react/24/outline'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'

const IVA_OPTIONS = [
    { label: 'Sin IVA (0%)', value: 0 },
    { label: 'IVA 10.5%', value: 10.5 },
    { label: 'IVA 21%', value: 21 },
    { label: 'IVA 27%', value: 27 },
]

interface Props {
    isOpen: boolean
    onClose: () => void
    clients: any[]
    services: any[]
}

export function IncomeBudgetModal({ isOpen, onClose, clients, services }: Props) {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()

    const [clientId, setClientId] = useState('')
    const [serviceId, setServiceId] = useState('')
    const [amount, setAmount] = useState('')
    const [plannedDate, setPlannedDate] = useState(new Date().toISOString().split('T')[0])
    const [isRecurring, setIsRecurring] = useState(false)
    const [description, setDescription] = useState('')
    const [requiresInvoice, setRequiresInvoice] = useState(false)
    const [ivaRate, setIvaRate] = useState(21)

    const baseAmount = parseFloat(amount) || 0
    const ivaAmount = requiresInvoice ? +(baseAmount * ivaRate / 100).toFixed(2) : 0
    const totalAmount = +(baseAmount + ivaAmount).toFixed(2)

    const mutation = useMutation({
        mutationFn: (data: any) => api.incomeBudgets.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['incomeBudgets'] })
            onClose()
            reset()
        }
    })

    const reset = () => {
        setClientId('')
        setServiceId('')
        setAmount('')
        setPlannedDate(new Date().toISOString().split('T')[0])
        setIsRecurring(false)
        setDescription('')
        setRequiresInvoice(false)
        setIvaRate(21)
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany) return

        const date = new Date(plannedDate)
        mutation.mutate({
            company_id: selectedCompany.id,
            client_id: clientId,
            service_id: serviceId,
            description: description || `Presupuesto ${date.getMonth() + 1}/${date.getFullYear()}`,
            budgeted_amount: baseAmount,
            planned_date: plannedDate,
            period_month: date.getMonth() + 1,
            period_year: date.getFullYear(),
            is_recurring: isRecurring,
            requires_invoice: requiresInvoice,
            iva_rate: requiresInvoice ? ivaRate : 0,
            iva_amount: requiresInvoice ? ivaAmount : 0,
            status: 'PENDING'
        })
    }

    return (
        <Transition.Root show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={onClose}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
                    leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto">
                    <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300" enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200" leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                                    <button onClick={onClose} className="rounded-md bg-white text-gray-400 hover:text-gray-500 transition-colors">
                                        <XMarkIcon className="h-6 w-6" />
                                    </button>
                                </div>
                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                                        <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 flex items-center gap-2">
                                            <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                                                <DocumentTextIcon className="w-5 h-5" />
                                            </div>
                                            Nuevo Ingreso Presupuestado
                                        </Dialog.Title>

                                        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                                            {/* Cliente y Servicio */}
                                            <div className="grid grid-cols-2 gap-3">
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
                                                    <select value={clientId} onChange={(e) => setClientId(e.target.value)} required
                                                        className="block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-emerald-500">
                                                        <option value="">Seleccionar...</option>
                                                        {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Servicio</label>
                                                    <select value={serviceId} onChange={(e) => setServiceId(e.target.value)} required
                                                        className="block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-emerald-500">
                                                        <option value="">Seleccionar...</option>
                                                        {services.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                                                    </select>
                                                </div>
                                            </div>

                                            {/* Monto */}
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Monto Base (Neto)</label>
                                                <div className="relative">
                                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
                                                    <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} required
                                                        placeholder="0.00" step="0.01"
                                                        className="block w-full rounded-xl border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-emerald-500" />
                                                </div>
                                            </div>

                                            {/* Toggle Factura + IVA */}
                                            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 space-y-3">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <ReceiptPercentIcon className="w-4 h-4 text-blue-500" />
                                                        <span className="text-sm font-semibold text-gray-700">Requiere Factura (En Blanco)</span>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => setRequiresInvoice(!requiresInvoice)}
                                                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${requiresInvoice ? 'bg-blue-600' : 'bg-gray-200'}`}
                                                    >
                                                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${requiresInvoice ? 'translate-x-6' : 'translate-x-1'}`} />
                                                    </button>
                                                </div>

                                                {requiresInvoice && (
                                                    <div className="space-y-3 pt-2 border-t border-gray-200">
                                                        <div>
                                                            <label className="block text-xs font-medium text-gray-500 mb-1">Tasa de IVA</label>
                                                            <select value={ivaRate} onChange={(e) => setIvaRate(parseFloat(e.target.value))}
                                                                className="block w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none">
                                                                {IVA_OPTIONS.map(opt => (
                                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                                ))}
                                                            </select>
                                                        </div>
                                                        {/* Desglose */}
                                                        <div className="rounded-lg bg-white border border-gray-100 divide-y divide-gray-50 text-sm">
                                                            <div className="flex justify-between px-3 py-2">
                                                                <span className="text-gray-500">Subtotal (Neto)</span>
                                                                <span className="font-medium text-gray-900">${baseAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                            </div>
                                                            <div className="flex justify-between px-3 py-2">
                                                                <span className="text-gray-500">IVA ({ivaRate}%)</span>
                                                                <span className="font-medium text-blue-600">+${ivaAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                            </div>
                                                            <div className="flex justify-between px-3 py-2 bg-gray-50 rounded-b-lg">
                                                                <span className="font-bold text-gray-900">Total a Cobrar</span>
                                                                <span className="font-black text-emerald-600">${totalAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Fecha y Recurrente */}
                                            <div className="grid grid-cols-2 gap-3">
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Estimada</label>
                                                    <input type="date" value={plannedDate} onChange={(e) => setPlannedDate(e.target.value)} required
                                                        className="block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none" />
                                                </div>
                                                <div className="flex flex-col justify-end pb-1.5">
                                                    <label className="flex items-center gap-2 cursor-pointer select-none">
                                                        <input type="checkbox" id="isRecurring" checked={isRecurring}
                                                            onChange={(e) => setIsRecurring(e.target.checked)}
                                                            className="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500" />
                                                        <span className="text-sm text-gray-700 font-medium">Es recurrente</span>
                                                    </label>
                                                </div>
                                            </div>

                                            {/* Descripción */}
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Notas (opcional)</label>
                                                <input type="text" value={description} onChange={(e) => setDescription(e.target.value)}
                                                    placeholder="Descripción o referencia..."
                                                    className="block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none" />
                                            </div>

                                            {/* Botones */}
                                            <div className="mt-5 flex flex-col-reverse sm:flex-row sm:justify-end gap-2">
                                                <button type="button" onClick={onClose}
                                                    className="inline-flex justify-center rounded-xl bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all">
                                                    Cancelar
                                                </button>
                                                <button type="submit" disabled={mutation.isPending}
                                                    className="inline-flex justify-center rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 transition-all disabled:opacity-50">
                                                    {mutation.isPending ? 'Guardando...' : 'Guardar Presupuesto'}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
