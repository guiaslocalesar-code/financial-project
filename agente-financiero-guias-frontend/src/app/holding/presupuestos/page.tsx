'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlusIcon, ClipboardDocumentListIcon, EllipsisVerticalIcon, BanknotesIcon } from '@heroicons/react/24/outline'
import { Menu, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { IncomeBudget } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { IncomeBudgetModal } from '@/components/budgets/IncomeBudgetModal'
import { ExpenseBudgetModal } from '@/components/budgets/ExpenseBudgetModal'
import { useQueryClient } from '@tanstack/react-query'

export default function PresupuestosPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [isIncomeModalOpen, setIsIncomeModalOpen] = useState(false)
    const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false)

    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as any[]
        },
        enabled: !!selectedCompany,
    })

    const { data: services } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as any[]
        },
        enabled: !!selectedCompany,
    })

    const { data, isLoading, error } = useQuery({
        queryKey: ['incomeBudgets', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const now = new Date()
            const res = await api.incomeBudgets.list(selectedCompany.id, {
                month: now.getMonth() + 1,
                year: now.getFullYear()
            })
            const budgets = (res.data.data || res.data || []) as IncomeBudget[]
            
            const clientMap = new Map((clients || []).map(c => [c.id, c.name]))
            const serviceMap = new Map((services || []).map(s => [s.id, s.name]))

            const enriched = budgets.map(b => ({
                ...b,
                client: { name: clientMap.get(b.client_id) || b.client_name || '—' },
                service: { name: serviceMap.get(b.service_id) || b.service_name || '—' }
            }))

            if (enriched.length > 0) {
                console.log('[Presupuestos]', { amount: enriched[0].amount, client: enriched[0].client?.name })
            }

            return enriched
        },
        enabled: !!selectedCompany && !!clients && !!services,
    })

    const handleCollect = async (budgetId: string) => {
        try {
            await api.incomeBudgets.collect(budgetId)
            queryClient.invalidateQueries({ queryKey: ['incomeBudgets'] })
        } catch (err) {
            console.error('Error collecting income:', err)
        }
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <ClipboardDocumentListIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los presupuestos de ingresos, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ClipboardDocumentListIcon className="w-7 h-7 text-emerald-600" />
                        Presupuestos (Ingresos)
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Proyecciones de ingresos y cobranzas de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <div className="flex flex-wrap gap-2">
                    <button 
                        onClick={() => setIsExpenseModalOpen(true)}
                        className="btn-primary bg-rose-600 hover:bg-rose-700 ring-rose-500/30"
                    >
                        <PlusIcon className="w-5 h-5" />
                        Nuevo Gasto
                    </button>
                    <button 
                        onClick={() => setIsIncomeModalOpen(true)}
                        className="btn-primary bg-emerald-600 hover:bg-emerald-700 ring-emerald-500/30"
                    >
                        <PlusIcon className="w-5 h-5" />
                        Nuevo Ingreso
                    </button>
                </div>
            </div>

            {/* List */}
            <div className="glass-card overflow-hidden">
                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                        Error al cargar los presupuestos de ingresos.
                    </div>
                ) : !data || data.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay ingresos presupuestados</h3>
                        <p className="mt-1 text-sm text-gray-500">Aún no se han cargado proyecciones para este período.</p>
                        <div className="mt-6 flex flex-wrap justify-center gap-2">
                            <button 
                                onClick={() => setIsExpenseModalOpen(true)}
                                className="btn-primary bg-rose-600 hover:bg-rose-700"
                            >
                                <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                Nuevo Gasto
                            </button>
                            <button 
                                onClick={() => setIsIncomeModalOpen(true)}
                                className="btn-primary bg-emerald-600 hover:bg-emerald-700"
                            >
                                <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                Nuevo Ingreso
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Descripción / Cliente</th>
                                    <th>Servicio</th>
                                    <th>Fecha Planificada</th>
                                    <th>Monto</th>
                                    <th>Estado</th>
                                    <th className="text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.map((income) => (
                                    <tr key={income.id}>
                                        <td>
                                            <div className="font-medium text-gray-900">{income.description}</div>
                                            <div className="text-xs text-gray-500">{income.client_name || 'Sin cliente'}</div>
                                        </td>
                                        <td>
                                            <div className="text-sm text-gray-600">{income.service_name || 'Sin servicio'}</div>
                                            {income.is_recurring && (
                                                <div className="text-[10px] text-blue-500 uppercase font-bold tracking-tight">Recurrente</div>
                                            )}
                                        </td>
                                        <td className="text-sm text-gray-600">
                                            {format(new Date(income.planned_date), "dd 'de' MMMM", { locale: es })}
                                        </td>
                                        <td className="font-semibold text-emerald-700">
                                            ${income.amount.toLocaleString('es-AR')}
                                        </td>
                                        <td>
                                            <span className={clsx(
                                                income.status === 'COLLECTED' ? 'badge-success' : 
                                                income.status === 'PENDING' ? 'badge-warning' : 'badge-neutral'
                                            )}>
                                                {income.status === 'COLLECTED' ? 'Cobrado' : 
                                                 income.status === 'PENDING' ? 'Pendiente' : 'Cancelado'}
                                            </span>
                                        </td>
                                        <td className="text-right">
                                            <Menu as="div" className="relative inline-block text-left">
                                                <Menu.Button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                                    <EllipsisVerticalIcon className="h-5 w-5" />
                                                </Menu.Button>
                                                <Transition
                                                    as={Fragment}
                                                    enter="transition ease-out duration-100"
                                                    enterFrom="transform opacity-0 scale-95"
                                                    enterTo="transform opacity-100 scale-100"
                                                    leave="transition ease-in duration-75"
                                                    leaveFrom="transform opacity-100 scale-100"
                                                    leaveTo="transform opacity-0 scale-95"
                                                >
                                                    <Menu.Items className="absolute right-0 z-10 mt-2 w-44 origin-top-right rounded-xl bg-white shadow-lg ring-1 ring-black/5 focus:outline-none">
                                                        <div className="py-1">
                                                            {income.status === 'PENDING' && (
                                                                <Menu.Item>
                                                                    {({ active }) => (
                                                                        <button
                                                                            onClick={() => handleCollect(income.id)}
                                                                            className={clsx(
                                                                                active ? 'bg-emerald-50 text-emerald-700' : 'text-gray-700',
                                                                                'group flex w-full items-center px-4 py-2 text-sm transition-colors'
                                                                            )}
                                                                        >
                                                                            <BanknotesIcon className="mr-3 h-4 w-4 text-gray-400 group-hover:text-emerald-500" />
                                                                            Marcar Cobrado
                                                                        </button>
                                                                    )}
                                                                </Menu.Item>
                                                            )}
                                                        </div>
                                                    </Menu.Items>
                                                </Transition>
                                            </Menu>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <IncomeBudgetModal
                isOpen={isIncomeModalOpen}
                onClose={() => setIsIncomeModalOpen(false)}
                clients={clients || []}
                services={services || []}
            />

            <ExpenseBudgetModal
                isOpen={isExpenseModalOpen}
                onClose={() => setIsExpenseModalOpen(false)}
            />
        </div>
    )
}
