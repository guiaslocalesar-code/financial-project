'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { PlusIcon, ClipboardDocumentListIcon, EllipsisVerticalIcon, BanknotesIcon, ChevronLeftIcon, ChevronRightIcon, ArrowPathIcon, ArrowPathRoundedSquareIcon } from '@heroicons/react/24/outline'
import { Menu, Transition, Tab } from '@headlessui/react'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { IncomeBudget, ExpenseBudget, ExpenseType, ExpenseCategory } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { IncomeBudgetModal } from '@/components/budgets/IncomeBudgetModal'
import { ExpenseBudgetModal } from '@/components/budgets/ExpenseBudgetModal'
import { CollectIncomeModal } from '@/components/budgets/CollectIncomeModal'
import { useQueryClient } from '@tanstack/react-query'
import type { IncomeBudget as IncomeBudgetType } from '@/types'

export default function PresupuestosPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [isIncomeModalOpen, setIsIncomeModalOpen] = useState(false)
    const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false)
    const [collectBudget, setCollectBudget] = useState<IncomeBudgetType | null>(null)
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
    const [toastMsg, setToastMsg] = useState<{title: string, type: 'success'|'info'|'error'} | null>(null)

    const generateMutation = useMutation({
        mutationFn: async () => {
            if (!selectedCompany) return null;
            const res = await api.incomeBudgets.generate(selectedCompany.id, selectedMonth, selectedYear);
            return res.data;
        },
        onSuccess: (data: any) => {
            if (data) {
                setToastMsg({ title: data.message, type: data.budgets_created > 0 ? 'success' : 'info' });
                setTimeout(() => setToastMsg(null), 5000);
                queryClient.invalidateQueries({ queryKey: ['incomeBudgets'] });
            }
        },
        onError: (err: any) => {
            setToastMsg({ title: err.response?.data?.detail || err.message || 'Error generando presupuestos', type: 'error' });
            setTimeout(() => setToastMsg(null), 5000);
        }
    })

    const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    const prevMonth = () => {
        if (selectedMonth === 1) { setSelectedMonth(12); setSelectedYear(y => y - 1) }
        else setSelectedMonth(m => m - 1)
    }
    const nextMonth = () => {
        if (selectedMonth === 12) { setSelectedMonth(1); setSelectedYear(y => y + 1) }
        else setSelectedMonth(m => m + 1)
    }

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

    const { data: expenseTypes } = useQuery({
        queryKey: ['expenseTypes', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listTypes(selectedCompany.id)
            return (res.data.data || res.data || []) as ExpenseType[]
        },
        enabled: !!selectedCompany,
    })

    const { data: expenseCategories } = useQuery({
        queryKey: ['expenseCategories', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listCategories(selectedCompany.id)
            return (res.data.data || res.data || []) as ExpenseCategory[]
        },
        enabled: !!selectedCompany,
    })


    const { data: incomeBudgets, isLoading: isLoadingIncomes, error: incomeError } = useQuery({
        queryKey: ['incomeBudgets', selectedCompany?.id, selectedMonth, selectedYear],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.incomeBudgets.list(selectedCompany.id, {
                month: selectedMonth,
                year: selectedYear
            })
            const budgets = (res.data.data || res.data || []) as IncomeBudget[]
            
            const clientMap = new Map((clients || []).map(c => [c.id, c.name]))
            const serviceMap = new Map((services || []).map(s => [s.id, s.name]))

            return budgets.map(b => ({
                ...b,
                client: { name: clientMap.get(b.client_id) || b.client_name || '—' },
                service: { name: serviceMap.get(b.service_id) || b.service_name || '—' }
            }))
        },
        enabled: !!selectedCompany && !!clients && !!services,
    })

    const { data: expenseBudgets, isLoading: isLoadingExpenses, error: expenseError } = useQuery({
        queryKey: ['expenseBudgets', selectedCompany?.id, selectedMonth, selectedYear],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.budgets.list(selectedCompany.id, {
                month: selectedMonth,
                year: selectedYear
            })
            const budgets = (res.data.data || res.data || []) as ExpenseBudget[]
            
            const typeMap = new Map((expenseTypes || []).map(t => [t.id, t.name]))
            const categoryMap = new Map((expenseCategories || []).map(c => [c.id, c.name]))

            return budgets.map(b => ({
                ...b,
                expense_type: { name: typeMap.get(b.expense_type_id) || b.expense_type_name || '—' },
                expense_category: { name: categoryMap.get(b.expense_category_id) || b.category_name || '—' }
            }))
        },
        enabled: !!selectedCompany && !!expenseTypes && !!expenseCategories,
    })

    const handleCollect = (budget: IncomeBudgetType) => {
        setCollectBudget(budget)
    }

    const handlePay = async (budgetId: string) => {
        try {
            await api.budgets.pay(budgetId)
            queryClient.invalidateQueries({ queryKey: ['expenseBudgets'] })
        } catch (err) {
            console.error('Error paying expense:', err)
        }
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <ClipboardDocumentListIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver proyecciones, primero debés seleccionar una empresa.</p>
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
                        Presupuestos
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Proyecciones de ingresos y egresos de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <div className="flex flex-wrap gap-2 items-center">
                    {/* Month/Year Navigator */}
                    <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-xl px-1 py-1 shadow-sm">
                        <button onClick={prevMonth} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
                            <ChevronLeftIcon className="w-4 h-4" />
                        </button>
                        <span className="px-2 text-sm font-bold text-gray-700 min-w-[140px] text-center">
                            {MONTH_NAMES[selectedMonth - 1]} {selectedYear}
                        </span>
                        <button onClick={nextMonth} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
                            <ChevronRightIcon className="w-4 h-4" />
                        </button>
                    </div>
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

            <Tab.Group>
                <div className="border-b border-gray-200">
                    <Tab.List className="flex gap-8 -mb-px">
                        {['Ingresos', 'Egresos'].map((tab) => (
                            <Tab
                                key={tab}
                                className={({ selected }) =>
                                    clsx(
                                        'pb-4 text-sm font-semibold border-b-2 transition-all outline-none',
                                        selected
                                            ? 'border-emerald-600 text-emerald-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700'
                                    )
                                }
                            >
                                {tab}
                            </Tab>
                        ))}
                    </Tab.List>
                </div>

                <Tab.Panels className="mt-4">
                    {/* Panel 1: Ingresos */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="flex justify-between items-center mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Ingresos Proyectados</h3>
                                <p className="text-sm text-gray-500">Abonos mensuales para {MONTH_NAMES[selectedMonth - 1]} {selectedYear}</p>
                            </div>
                            <button
                                onClick={() => generateMutation.mutate()}
                                disabled={generateMutation.isPending}
                                className="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 text-white rounded-xl font-semibold shadow-sm hover:bg-emerald-700 transition-all disabled:opacity-50"
                            >
                                {generateMutation.isPending ? (
                                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                                ) : (
                                    <ArrowPathRoundedSquareIcon className="w-5 h-5" />
                                )}
                                Generar Automáticamente
                            </button>
                        </div>
                        <div className="glass-card overflow-hidden">
                            {isLoadingIncomes ? (
                                <div className="p-12 flex justify-center">
                                    <div className="w-8 h-8 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
                                </div>
                            ) : incomeError ? (
                                <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                                    Error al cargar los presupuestos de ingresos.
                                </div>
                            ) : !incomeBudgets || incomeBudgets.length === 0 ? (
                                <div className="text-center py-16 px-4">
                                    <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-300" />
                                    <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay ingresos presupuestados</h3>
                                    <p className="mt-1 text-sm text-gray-500">Aún no se han cargado proyecciones para este período.</p>
                                    <div className="mt-6 flex flex-wrap justify-center gap-2">
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
                                            {incomeBudgets.map((income) => (
                                                <tr key={income.id}>
                                                    <td>
                                                        <div className="font-medium text-gray-900">{income.description}</div>
                                                        <div className="text-xs text-gray-500">{income.client?.name || 'Sin cliente'}</div>
                                                    </td>
                                                    <td>
                                                        <div className="text-sm text-gray-600">{income.service?.name || 'Sin servicio'}</div>
                                                        {income.is_recurring && (
                                                            <div className="text-[10px] text-blue-500 uppercase font-bold tracking-tight">Recurrente</div>
                                                        )}
                                                        {income.requires_invoice ? (
                                                            <div className="text-[10px] text-indigo-600 uppercase font-bold tracking-tight">🧾 En Blanco</div>
                                                        ) : (
                                                            <div className="text-[10px] text-gray-400 uppercase font-bold tracking-tight">Sin Factura</div>
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
                                                                                        onClick={() => handleCollect(income as IncomeBudgetType)}
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
                    </Tab.Panel>

                    {/* Panel 2: Egresos */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="glass-card overflow-hidden">
                            {isLoadingExpenses ? (
                                <div className="p-12 flex justify-center">
                                    <div className="w-8 h-8 border-4 border-rose-200 border-t-rose-600 rounded-full animate-spin" />
                                </div>
                            ) : expenseError ? (
                                <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                                    Error al cargar los presupuestos de egresos.
                                </div>
                            ) : !expenseBudgets || expenseBudgets.length === 0 ? (
                                <div className="text-center py-16 px-4">
                                    <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-300" />
                                    <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay egresos presupuestados</h3>
                                    <p className="mt-1 text-sm text-gray-500">Aún no se han cargado proyecciones de gasto para este período.</p>
                                    <div className="mt-6 flex flex-wrap justify-center gap-2">
                                        <button 
                                            onClick={() => setIsExpenseModalOpen(true)}
                                            className="btn-primary bg-rose-600 hover:bg-rose-700"
                                        >
                                            <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                            Nuevo Gasto
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Descripción</th>
                                                <th>Categoría</th>
                                                <th>Fecha Planificada</th>
                                                <th>Monto</th>
                                                <th>Estado</th>
                                                <th className="text-right">Acciones</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {expenseBudgets.map((expense) => (
                                                <tr key={expense.id}>
                                                    <td>
                                                        <div className="font-medium text-gray-900">{expense.description}</div>
                                                        {expense.is_recurring && (
                                                            <div className="text-[10px] text-blue-500 uppercase font-bold tracking-tight">Recurrente</div>
                                                        )}
                                                    </td>
                                                    <td>
                                                        <div className="text-sm font-semibold text-gray-800">{expense.expense_type?.name || 'Tipo desconocido'}</div>
                                                        <div className="text-xs text-gray-500">{expense.expense_category?.name || 'Sin categoría'}</div>
                                                    </td>
                                                    <td className="text-sm text-gray-600">
                                                        {format(new Date(expense.planned_date), "dd 'de' MMMM", { locale: es })}
                                                    </td>
                                                    <td className="font-semibold text-rose-700">
                                                        ${expense.budgeted_amount.toLocaleString('es-AR')}
                                                    </td>
                                                    <td>
                                                        <span className={clsx(
                                                            expense.status === 'PAID' ? 'badge-success' : 
                                                            expense.status === 'PENDING' ? 'badge-warning' : 'badge-neutral'
                                                        )}>
                                                            {expense.status === 'PAID' ? 'Pagado' : 
                                                             expense.status === 'PENDING' ? 'Pendiente' : 'Cancelado'}
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
                                                                        {expense.status === 'PENDING' && (
                                                                            <Menu.Item>
                                                                                {({ active }) => (
                                                                                    <button
                                                                                        onClick={() => handlePay(expense.id)}
                                                                                        className={clsx(
                                                                                            active ? 'bg-rose-50 text-rose-700' : 'text-gray-700',
                                                                                            'group flex w-full items-center px-4 py-2 text-sm transition-colors'
                                                                                        )}
                                                                                    >
                                                                                        <BanknotesIcon className="mr-3 h-4 w-4 text-gray-400 group-hover:text-rose-500" />
                                                                                        Marcar Pagado
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
                    </Tab.Panel>
                </Tab.Panels>
            </Tab.Group>

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

            <CollectIncomeModal
                isOpen={!!collectBudget}
                onClose={() => setCollectBudget(null)}
                budget={collectBudget}
                companyId={selectedCompany.id}
            />

            {/* Custom Toast */}
            {toastMsg && (
                <div className={`fixed bottom-4 right-4 z-50 p-4 rounded-xl shadow-lg border text-sm font-semibold animate-fade-in-up transition-all ${
                    toastMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' :
                    toastMsg.type === 'error' ? 'bg-rose-50 text-rose-800 border-rose-200' :
                    'bg-blue-50 text-blue-800 border-blue-200'
                }`}>
                    {toastMsg.title}
                </div>
            )}
        </div>
    )
}
