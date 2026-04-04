'use client'

import { Fragment, useEffect, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import {
    XMarkIcon,
    BanknotesIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon,
    DocumentTextIcon,
    CalendarIcon,
    BuildingLibraryIcon,
} from '@heroicons/react/24/outline'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { IncomeBudget } from '@/types'

interface Props {
    isOpen: boolean
    onClose: () => void
    budget: IncomeBudget | null
    companyId: string
}

export function CollectIncomeModal({ isOpen, onClose, budget, companyId }: Props) {
    const queryClient = useQueryClient()
    const [paymentMethodId, setPaymentMethodId] = useState('')
    const [transactionDate, setTransactionDate] = useState(new Date().toISOString().split('T')[0])
    const [actualAmount, setActualAmount] = useState('')
    const [afipError, setAfipError] = useState<string | null>(null)

    // Pre-fill actual amount when budget changes
    useEffect(() => {
        if (budget) {
            // If requires_invoice, total = neto + IVA; otherwise just budgeted_amount
            const total = budget.requires_invoice && budget.iva_amount
                ? (budget.amount ?? 0) + (budget.iva_amount ?? 0)
                : (budget.amount ?? 0)
            setActualAmount(total.toFixed(2))
            setAfipError(null)
        }
    }, [budget, isOpen])

    const { data: paymentMethods = [] } = useQuery({
        queryKey: ['payment-methods', companyId],
        queryFn: async () => {
            const res = await api.paymentMethods.list(companyId)
            return res.data || []
        },
        enabled: isOpen && !!companyId,
    })

    const mutation = useMutation({
        mutationFn: (data: any) => api.incomeBudgets.collect(budget!.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['incomeBudgets'] })
            queryClient.invalidateQueries({ queryKey: ['transactions'] })
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
            onClose()
        },
        onError: (error: any) => {
            const detail = error?.response?.data?.detail
            if (error?.response?.status === 400 && detail) {
                setAfipError(detail)
            } else {
                setAfipError('Error al registrar el cobro. Por favor, reintentá.')
            }
        }
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!budget) return
        setAfipError(null)
        mutation.mutate({
            actual_amount_collected: parseFloat(actualAmount),
            payment_method_id: paymentMethodId || undefined,
            transaction_date: transactionDate,
        })
    }

    const ivaAmount = budget?.iva_amount ?? 0
    const baseAmount = budget?.amount ?? 0

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
                            enter="ease-out duration-300" enterFrom="opacity-0 translate-y-4 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200" leaveFrom="opacity-100 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-md sm:p-6">
                                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                                    <button onClick={onClose} className="rounded-md bg-white text-gray-400 hover:text-gray-500 transition-colors">
                                        <XMarkIcon className="h-6 w-6" />
                                    </button>
                                </div>

                                <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 flex items-center gap-2 mb-4">
                                    <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                                        <BanknotesIcon className="w-5 h-5" />
                                    </div>
                                    Registrar Cobro
                                </Dialog.Title>

                                {/* Info del presupuesto */}
                                {budget && (
                                    <div className="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-100 space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-gray-400 uppercase font-bold tracking-wider">Cliente</span>
                                            <span className="text-sm font-semibold text-gray-800">{budget.client?.name || budget.client_name || '—'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-gray-400 uppercase font-bold tracking-wider">Servicio</span>
                                            <span className="text-sm text-gray-700">{budget.service?.name || budget.service_name || '—'}</span>
                                        </div>
                                        {budget.requires_invoice ? (
                                            <>
                                                <div className="border-t border-gray-200 pt-2 space-y-1">
                                                    <div className="flex justify-between text-sm">
                                                        <span className="text-gray-500">Neto</span>
                                                        <span>${baseAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                    </div>
                                                    <div className="flex justify-between text-sm">
                                                        <span className="text-gray-500">IVA ({budget.iva_rate ?? 21}%)</span>
                                                        <span className="text-blue-600">+${ivaAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                    </div>
                                                    <div className="flex justify-between font-bold text-sm pt-1 border-t border-gray-100">
                                                        <span>Total con IVA</span>
                                                        <span className="text-emerald-700">${(baseAmount + ivaAmount).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-1.5 pt-1">
                                                    <DocumentTextIcon className="w-4 h-4 text-blue-500" />
                                                    <span className="text-xs font-semibold text-blue-600">Se generará FACTURA automáticamente</span>
                                                </div>
                                            </>
                                        ) : (
                                            <div className="flex items-center gap-1.5 border-t border-gray-100 pt-2">
                                                <span className="text-xs font-semibold text-gray-500">Operación sin factura (En Negro) — ${baseAmount.toLocaleString('es-AR')}</span>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Error de AFIP */}
                                {afipError && (
                                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl flex gap-3 text-sm text-red-700">
                                        <ExclamationTriangleIcon className="w-5 h-5 shrink-0 text-red-500 mt-0.5" />
                                        <div>
                                            <p className="font-bold">Error al emitir factura AFIP</p>
                                            <p className="mt-0.5">{afipError}</p>
                                        </div>
                                    </div>
                                )}

                                <form onSubmit={handleSubmit} className="space-y-4">
                                    {/* Monto real cobrado */}
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-1">Monto Efectivamente Cobrado</label>
                                        <div className="relative">
                                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
                                            <input
                                                type="number"
                                                step="0.01"
                                                value={actualAmount}
                                                onChange={(e) => setActualAmount(e.target.value)}
                                                required
                                                className="block w-full rounded-xl border border-gray-300 pl-7 pr-3 py-2.5 text-sm font-mono focus:border-emerald-500 focus:outline-none focus:ring-emerald-500"
                                            />
                                        </div>
                                    </div>

                                    {/* Fecha */}
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                                            <CalendarIcon className="w-4 h-4 text-gray-400" />
                                            Fecha del Cobro
                                        </label>
                                        <input
                                            type="date"
                                            value={transactionDate}
                                            onChange={(e) => setTransactionDate(e.target.value)}
                                            required
                                            className="block w-full rounded-xl border border-gray-300 px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none"
                                        />
                                    </div>

                                    {/* Método de pago */}
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                                            <BuildingLibraryIcon className="w-4 h-4 text-gray-400" />
                                            Cuenta / Método de Pago
                                        </label>
                                        <select
                                            value={paymentMethodId}
                                            onChange={(e) => setPaymentMethodId(e.target.value)}
                                            className="block w-full rounded-xl border border-gray-300 px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none"
                                        >
                                            <option value="">Sin cuenta asociada</option>
                                            {(paymentMethods as any[]).map((pm: any) => (
                                                <option key={pm.id} value={pm.id}>
                                                    {pm.name} {pm.bank_name ? `(${pm.bank_name})` : ''}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Botones */}
                                    <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-2">
                                        <button type="button" onClick={onClose}
                                            className="inline-flex justify-center rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all">
                                            Cancelar
                                        </button>
                                        <button type="submit" disabled={mutation.isPending}
                                            className="inline-flex justify-center items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 transition-all disabled:opacity-50">
                                            <CheckCircleIcon className="w-4 h-4" />
                                            {mutation.isPending ? 'Procesando...' : 'Confirmar Cobro'}
                                        </button>
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
