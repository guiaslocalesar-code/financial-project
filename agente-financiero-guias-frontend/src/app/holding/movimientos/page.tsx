'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowsRightLeftIcon, ArrowUpCircleIcon, ArrowDownCircleIcon, MagnifyingGlassIcon, CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Transaction } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { format, startOfMonth, endOfMonth, isWithinInterval, addMonths, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'

type TabKey = 'ALL' | 'INCOME' | 'EXPENSE'

const TABS: { key: TabKey; label: string }[] = [
    { key: 'ALL', label: 'Todos' },
    { key: 'INCOME', label: 'Ingresos' },
    { key: 'EXPENSE', label: 'Egresos' },
]

export default function MovimientosPage() {
    const { selectedCompany } = useHoldingContext()
    const [activeTab, setActiveTab] = useState<TabKey>('ALL')
    const [search, setSearch] = useState('')
    const [currentDate, setCurrentDate] = useState(new Date())

    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(currentDate)

    const { data: allTransactions, isLoading: isLoadingTx, error } = useQuery({
        queryKey: ['transactions', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.transactions.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as Transaction[]
        },
        enabled: !!selectedCompany,
    })

    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as any[]
        },
        enabled: !!selectedCompany,
    })

    const { data: services } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as any[]
        },
        enabled: !!selectedCompany,
    })

    const clientMap = useMemo(() => new Map((clients || []).map(c => [c.id, c.name])), [clients])
    const serviceMap = useMemo(() => new Map((services || []).map(s => [s.id, s.name])), [services])

    const filtered = useMemo(() => {
        if (!allTransactions) return []
        return allTransactions.filter((tx) => {
            const txDate = new Date(tx.transaction_date)
            if (!isWithinInterval(txDate, { start: monthStart, end: monthEnd })) return false
            if (activeTab !== 'ALL' && tx.type !== activeTab) return false
            if (search) {
                const q = search.toLowerCase()
                const clientName = tx.client_id ? (clientMap.get(tx.client_id) || '') : ''
                const serviceName = tx.service_id ? (serviceMap.get(tx.service_id) || '') : ''
                return (
                    tx.description?.toLowerCase().includes(q) ||
                    tx.payment_method?.toLowerCase().includes(q) ||
                    clientName.toLowerCase().includes(q) ||
                    serviceName.toLowerCase().includes(q)
                )
            }
            return true
        })
    }, [allTransactions, activeTab, search, monthStart, monthEnd, clientMap, serviceMap])

    const monthSummary = useMemo(() => {
        if (!allTransactions) return { income: 0, expenses: 0, balance: 0 }
        let income = 0, expenses = 0
        allTransactions.forEach((tx) => {
            const txDate = new Date(tx.transaction_date)
            if (isWithinInterval(txDate, { start: monthStart, end: monthEnd })) {
                if (tx.type === 'INCOME') income += Number(tx.amount)
                else expenses += Number(tx.amount)
            }
        })
        return { income, expenses, balance: income - expenses }
    }, [allTransactions, monthStart, monthEnd])

    const countForTab = (tab: TabKey) => {
        if (!allTransactions) return 0
        return allTransactions.filter((tx) => {
            const txDate = new Date(tx.transaction_date)
            if (!isWithinInterval(txDate, { start: monthStart, end: monthEnd })) return false
            return tab === 'ALL' || tx.type === tab
        }).length
    }

    const goToPrevMonth = () => setCurrentDate(subMonths(currentDate, 1))
    const goToNextMonth = () => setCurrentDate(addMonths(currentDate, 1))
    const goToCurrentMonth = () => setCurrentDate(new Date())
    const monthLabel = format(currentDate, "MMMM yyyy", { locale: es })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <ArrowsRightLeftIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los movimientos, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    const isLoading = isLoadingTx || !clients || !services

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ArrowsRightLeftIcon className="w-7 h-7 text-indigo-600" />
                        Movimientos
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Historial completo de ingresos y egresos de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-2 py-1.5 shadow-sm">
                    <button onClick={goToPrevMonth} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                        <ChevronLeftIcon className="w-4 h-4 text-gray-500" />
                    </button>
                    <button onClick={goToCurrentMonth} className="flex items-center gap-2 px-3 py-1 hover:bg-gray-50 rounded-lg transition-colors">
                        <CalendarDaysIcon className="w-4 h-4 text-indigo-500" />
                        <span className="text-sm font-semibold text-gray-700 capitalize min-w-[130px] text-center">{monthLabel}</span>
                    </button>
                    <button onClick={goToNextMonth} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                        <ChevronRightIcon className="w-4 h-4 text-gray-500" />
                    </button>
                </div>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="glass-card p-6">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Ingresos del Mes</p>
                    <p className="text-2xl font-black text-emerald-600 mt-1">+${monthSummary.income.toLocaleString('es-AR')}</p>
                </div>
                <div className="glass-card p-6">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Egresos del Mes</p>
                    <p className="text-2xl font-black text-rose-600 mt-1">-${monthSummary.expenses.toLocaleString('es-AR')}</p>
                </div>
                <div className="glass-card p-6">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Saldo del Mes</p>
                    <p className={clsx("text-2xl font-black mt-1", monthSummary.balance >= 0 ? "text-blue-600" : "text-rose-600")}>
                        ${monthSummary.balance.toLocaleString('es-AR')}
                    </p>
                </div>
            </div>

            {/* Tabs + Table */}
            <div className="glass-card overflow-hidden">
                <div className="px-6 py-3 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-gray-50/50">
                    <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
                        {TABS.map((tab) => (
                            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                                className={clsx('px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2',
                                    activeTab === tab.key ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700')}>
                                {tab.label}
                                <span className={clsx('text-[10px] font-bold px-1.5 py-0.5 rounded-full',
                                    activeTab === tab.key ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-200 text-gray-500')}>
                                    {countForTab(tab.key)}
                                </span>
                            </button>
                        ))}
                    </div>
                    <div className="relative w-full sm:w-64">
                        <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                            placeholder="Buscar..."
                            className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" />
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-12 flex justify-center"><div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" /></div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">Error al cargar movimientos.</div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <ArrowsRightLeftIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay movimientos</h3>
                        <p className="mt-1 text-sm text-gray-500">No se encontraron registros en <span className="capitalize">{monthLabel}</span>.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Concepto</th>
                                    <th>Cliente</th>
                                    <th>Servicio</th>
                                    <th>Tipo</th>
                                    <th>Método</th>
                                    <th className="text-right">Monto</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((tx) => {
                                    const clientName = tx.client_id ? clientMap.get(tx.client_id) : null
                                    const serviceName = tx.service_id ? serviceMap.get(tx.service_id) : null

                                    return (
                                        <tr key={tx.id}>
                                            <td className="text-sm font-medium text-gray-500">{format(new Date(tx.transaction_date), "dd/MM/yyyy")}</td>
                                            <td>
                                                <div className="flex items-center gap-3">
                                                    {tx.type === 'INCOME'
                                                        ? <ArrowUpCircleIcon className="w-7 h-7 text-emerald-500 shrink-0" />
                                                        : <ArrowDownCircleIcon className="w-7 h-7 text-rose-500 shrink-0" />}
                                                    <div className="font-medium text-gray-900">{tx.description || '—'}</div>
                                                </div>
                                            </td>
                                            <td>
                                                {clientName ? (
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center text-[10px] font-bold">
                                                            {clientName.substring(0, 2).toUpperCase()}
                                                        </div>
                                                        <span className="text-sm text-gray-700">{clientName}</span>
                                                    </div>
                                                ) : <span className="text-sm text-gray-400">—</span>}
                                            </td>
                                            <td>
                                                {serviceName ? (
                                                    <span className="text-[11px] font-semibold px-2 py-1 rounded-full bg-violet-50 text-violet-700">
                                                        {serviceName}
                                                    </span>
                                                ) : <span className="text-sm text-gray-400">—</span>}
                                            </td>
                                            <td>
                                                <span className={clsx('text-[10px] font-bold uppercase px-2 py-1 rounded-full',
                                                    tx.type === 'INCOME' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700')}>
                                                    {tx.type === 'INCOME' ? 'Ingreso' : 'Egreso'}
                                                </span>
                                            </td>
                                            <td className="text-sm text-gray-600">{tx.payment_method || '—'}</td>
                                            <td className={clsx("text-right font-bold text-lg", tx.type === 'INCOME' ? "text-emerald-600" : "text-rose-600")}>
                                                {tx.type === 'INCOME' ? '+' : '-'}${Number(tx.amount).toLocaleString('es-AR')}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
