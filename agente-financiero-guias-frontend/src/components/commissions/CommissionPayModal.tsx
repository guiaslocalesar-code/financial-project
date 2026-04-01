'use client'

import { Fragment, useEffect, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { 
    XMarkIcon, 
    BanknotesIcon, 
    CalendarIcon, 
    CreditCardIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Commission, PayCommissionPayload } from '@/types/commissions'
import { useCommissions } from '@/hooks/useCommissions'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { clsx } from 'clsx'

const paySchema = z.object({
    payment_method: z.enum(['transfer', 'cash', 'card', 'check']),
    payment_date: z.string().min(1, 'La fecha es requerida'),
    actual_amount: z.number().min(1, 'El monto debe ser mayor a 0').optional(),
    payment_method_id: z.string().optional()
})

type FormData = z.infer<typeof paySchema>

interface Props {
    isOpen: boolean
    onClose: () => void
    commission: Commission | null
    companyId: string
}

export function CommissionPayModal({ isOpen, onClose, commission, companyId }: Props) {
    const { payMutation } = useCommissions(companyId)
    const [serverError, setServerError] = useState<string | null>(null)

    const { data: paymentMethods = [] } = useQuery({
        queryKey: ['payment-methods', companyId],
        queryFn: async () => {
            const res = await api.paymentMethods.list(companyId)
            return res.data
        },
        enabled: isOpen && !!companyId
    })

    const {
        register,
        handleSubmit,
        reset,
        watch,
        formState: { errors }
    } = useForm<FormData>({
        resolver: zodResolver(paySchema),
        defaultValues: {
            payment_date: new Date().toISOString().split('T')[0],
            payment_method: 'transfer'
        }
    })

    const selectedMethod = watch('payment_method')

    useEffect(() => {
        if (isOpen && commission) {
            reset({
                payment_date: new Date().toISOString().split('T')[0],
                payment_method: 'transfer',
                actual_amount: commission.commission_amount
            })
            setServerError(null)
        }
    }, [isOpen, commission, reset])

    const onSubmit = (data: FormData) => {
        if (!commission) return

        payMutation.mutate({
            id: commission.id,
            data: data as PayCommissionPayload
        }, {
            onSuccess: () => {
                onClose()
            },
            onError: (error: any) => {
                if (error.response?.status === 400) {
                    setServerError("Esta comisión ya fue pagada. Por favor, actualizá la lista.")
                } else {
                    setServerError("Hubo un error al procesar el pago. Reintentá en unos momentos.")
                }
            }
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
                    <div className="fixed inset-0 bg-gray-900/60 transition-opacity backdrop-blur-sm" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto">
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
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                                    <button
                                        type="button"
                                        className="rounded-md bg-white text-gray-400 hover:text-gray-500 transition-colors"
                                        onClick={onClose}
                                    >
                                        <XMarkIcon className="h-6 w-6" />
                                    </button>
                                </div>

                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                                        <Dialog.Title as="h3" className="text-xl font-bold leading-6 text-gray-900 flex items-center gap-2">
                                            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                                                <BanknotesIcon className="w-5 h-5" />
                                            </div>
                                            Liquidar Comisión
                                        </Dialog.Title>

                                        {commission && (
                                            <div className="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-100 grid grid-cols-2 gap-4">
                                                <div>
                                                    <p className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Destinatario</p>
                                                    <p className="text-sm font-semibold text-gray-800">{commission.recipient_name}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Total a Cobrar</p>
                                                    <p className="text-lg font-black text-blue-700">${commission.commission_amount.toLocaleString('es-AR')}</p>
                                                </div>
                                                <div className="col-span-2 pt-2 border-t border-gray-200 mt-1">
                                                    <p className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Contexto</p>
                                                    <p className="text-xs text-gray-600">{commission.client_name} — <span className="italic">{commission.service_name}</span></p>
                                                </div>
                                            </div>
                                        )}

                                        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-5">
                                            {serverError && (
                                                <div className="p-3 bg-red-50 border border-red-100 rounded-lg flex gap-2 text-rose-700 text-sm animate-shake">
                                                    <ExclamationCircleIcon className="w-5 h-5 flex-shrink-0" />
                                                    {serverError}
                                                </div>
                                            )}

                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5 flex items-center gap-2">
                                                        <CreditCardIcon className="w-4 h-4 text-gray-400" />
                                                        Método
                                                    </label>
                                                    <select
                                                        {...register('payment_method')}
                                                        className="input-field"
                                                    >
                                                        <option value="transfer">Transferencia</option>
                                                        <option value="cash">Efectivo</option>
                                                        <option value="card">Tarjeta</option>
                                                        <option value="check">Cheque</option>
                                                    </select>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5 flex items-center gap-2">
                                                        <CalendarIcon className="w-4 h-4 text-gray-400" />
                                                        Fecha
                                                    </label>
                                                    <input
                                                        type="date"
                                                        {...register('payment_date')}
                                                        className="input-field"
                                                    />
                                                </div>
                                            </div>

                                            {(selectedMethod === 'transfer' || selectedMethod === 'card') && (
                                                <div>
                                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5 flex items-center gap-2">
                                                        <BanknotesIcon className="w-4 h-4 text-gray-400" />
                                                        Cuenta / Caja Relacionada
                                                    </label>
                                                    <select
                                                        {...register('payment_method_id')}
                                                        className="input-field"
                                                    >
                                                        <option value="">Seleccionar cuenta (opcional)</option>
                                                        {paymentMethods.map((pm: any) => (
                                                            <option key={pm.id} value={pm.id}>
                                                                {pm.name} ({pm.bank_name || 'Efectivo'})
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            )}

                                            <div>
                                                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Monto a Liquidar (Parcial o Total)</label>
                                                <div className="relative">
                                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
                                                    <input
                                                        type="number"
                                                        step="0.01"
                                                        {...register('actual_amount', { valueAsNumber: true })}
                                                        className="input-field pl-8 font-mono"
                                                    />
                                                </div>
                                                {errors.actual_amount && <p className="text-xs text-red-500 mt-1">{errors.actual_amount.message}</p>}
                                            </div>

                                            <div className="mt-8 flex flex-col sm:flex-row-reverse gap-3">
                                                <button
                                                    type="submit"
                                                    disabled={payMutation.isPending}
                                                    className="inline-flex w-full justify-center rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all active:scale-95 disabled:opacity-50"
                                                >
                                                    {payMutation.isPending ? 'Procesando...' : 'Confirmar Liquidación'}
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={onClose}
                                                    className="inline-flex w-full justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:w-auto transition-all"
                                                >
                                                    Cancelar
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
