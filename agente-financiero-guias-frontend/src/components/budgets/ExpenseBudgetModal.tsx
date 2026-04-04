'use client'

import { Fragment, useState, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'

interface Props {
    isOpen: boolean
    onClose: () => void
}

export function ExpenseBudgetModal({ isOpen, onClose }: Props) {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    
    const [typeId, setTypeId] = useState('')
    const [categoryId, setCategoryId] = useState('')
    const [description, setDescription] = useState('')
    const [amount, setAmount] = useState('')
    const [plannedDate, setPlannedDate] = useState(new Date().toISOString().split('T')[0])
    const [isRecurring, setIsRecurring] = useState(false)

    // Fetch expense types
    const { data: expenseTypes } = useQuery({
        queryKey: ['expenseTypes', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listTypes(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as any[]
        },
        enabled: !!selectedCompany && isOpen,
    })

    // Fetch categories when type changes
    const { data: categories } = useQuery({
        queryKey: ['expenseCategories', selectedCompany?.id, typeId],
        queryFn: async () => {
            if (!selectedCompany || !typeId) return []
            const res = await api.expenses.listCategories(selectedCompany.id, typeId)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as any[]
        },
        enabled: !!selectedCompany && !!typeId && isOpen,
    })

    const mutation = useMutation({
        mutationFn: (data: any) => api.budgets.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['budgets'] })
            onClose()
            reset()
        }
    })

    const reset = () => {
        setTypeId('')
        setCategoryId('')
        setDescription('')
        setAmount('')
        setPlannedDate(new Date().toISOString().split('T')[0])
        setIsRecurring(false)
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany) return

        const date = new Date(plannedDate)
        mutation.mutate({
            company_id: selectedCompany.id,
            expense_type_id: typeId,
            expense_category_id: categoryId,
            description,
            budgeted_amount: parseFloat(amount),
            planned_date: plannedDate,
            period_month: date.getMonth() + 1,
            period_year: date.getFullYear(),
            is_recurring: isRecurring,
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
                    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
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
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                                    <button onClick={onClose} className="rounded-md bg-white text-gray-400 hover:text-gray-500">
                                        <XMarkIcon className="h-6 w-6" />
                                    </button>
                                </div>
                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                                        <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                                            Nuevo Gasto Presupuestado
                                        </Dialog.Title>
                                        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Tipo de Gasto</label>
                                                <select
                                                    value={typeId}
                                                    onChange={(e) => {
                                                        setTypeId(e.target.value)
                                                        setCategoryId('')
                                                    }}
                                                    required
                                                    className="mt-1 block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500"
                                                >
                                                    <option value="">Seleccionar tipo</option>
                                                    {expenseTypes?.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Categoría</label>
                                                <select
                                                    value={categoryId}
                                                    onChange={(e) => setCategoryId(e.target.value)}
                                                    required
                                                    disabled={!typeId}
                                                    className="mt-1 block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500 disabled:bg-gray-50 disabled:text-gray-400"
                                                >
                                                    <option value="">{typeId ? 'Seleccionar categoría' : 'Seleccioná primero un tipo'}</option>
                                                    {categories?.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Descripción</label>
                                                <input
                                                    type="text"
                                                    value={description}
                                                    onChange={(e) => setDescription(e.target.value)}
                                                    required
                                                    placeholder="Ej: Alquiler Oficinas"
                                                    className="mt-1 block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Monto</label>
                                                <div className="relative mt-1">
                                                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                                        <span className="text-gray-500 sm:text-sm">$</span>
                                                    </div>
                                                    <input
                                                        type="number"
                                                        value={amount}
                                                        onChange={(e) => setAmount(e.target.value)}
                                                        required
                                                        placeholder="0.00"
                                                        className="block w-full rounded-xl border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Fecha Estimada</label>
                                                <input
                                                    type="date"
                                                    value={plannedDate}
                                                    onChange={(e) => setPlannedDate(e.target.value)}
                                                    required
                                                    className="mt-1 block w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500"
                                                />
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    id="isRecurringExpense"
                                                    checked={isRecurring}
                                                    onChange={(e) => setIsRecurring(e.target.checked)}
                                                    className="h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500"
                                                />
                                                <label htmlFor="isRecurringExpense" className="ml-2 block text-sm text-gray-900">
                                                    Es recurrente
                                                </label>
                                            </div>
                                            <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                                                <button
                                                    type="submit"
                                                    disabled={mutation.isPending}
                                                    className="inline-flex w-full justify-center rounded-xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-500 sm:ml-3 sm:w-auto"
                                                >
                                                    {mutation.isPending ? 'Guardando...' : 'Guardar'}
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={onClose}
                                                    className="mt-3 inline-flex w-full justify-center rounded-xl bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
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
