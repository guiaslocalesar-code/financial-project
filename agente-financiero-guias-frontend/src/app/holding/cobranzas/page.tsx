'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowUpCircleIcon, MagnifyingGlassIcon, CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon, BanknotesIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Transaction } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { format, startOfMonth, endOfMonth, isWithinInterval, addMonths, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'

export default function CobranzasPage() {
    const { selectedCompany } = useHoldingContext()
    const [search, setSearch] = useState('')
    const [currentDate, setCurrentDate] = useState(new Date())

    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(currentDate)

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

    const { data: allTransactions, isLoading: isLoadingTx, error } = useQuery({
        queryKey: ['transactions', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.transactions.list(selectedCompany.id)
            const txs = (Array.isArray(res.data) ? res.data : res.data.data || []) as Transaction[]
            
            // Enrich with client and service objects
            const enriched = txs.map(tx => ({
                ...tx,
                client: tx.client_id ? { name: clientMap.get(tx.client_id) || '—' } : undefined,
                service: tx.service_id ? { name: serviceMap.get(tx.service_id) || '—' } : undefined
            }))

            if (enriched.length > 0) {
                console.log('[Cobranzas]', { amount: enriched[0].amount, client: enriched[0].client?.name })
            }

            return enriched
        },
        enabled: !!selectedCompany && !!clients && !!services,
    })

    // Only INCOME, filtered by month and search
    const filtered = useMemo(() => {
        if (!allTransactions) return []
        return allTransactions.filter((tx) => {
            if (tx.type !== 'INCOME') return false
            const txDate = new Date(tx.transaction_date)
            if (!isWithinInterval(txDate, { start: monthStart, end: monthEnd })) return false
            if (search) {
                const q = search.toLowerCase()
                const clientName = tx.client?.name || ''
                const serviceName = tx.service?.name || ''
                return (
                    tx.description?.toLowerCase().includes(q) ||
                    tx.payment_method?.toLowerCase().includes(q) ||
                    clientName.toLowerCase().includes(q) ||
                    serviceName.toLowerCase().includes(q)
                )
            }
            return true
        })
    }, [allTransactions, search, monthStart, monthEnd, clientMap, serviceMap])

    const totalIncome = useMemo(() => filtered.reduce((sum, tx) => sum + Number(tx.amount), 0), [filtered])

    const goToPrevMonth = () => setCurrentDate(subMonths(currentDate, 1))
    const goToNextMonth = () => setCurrentDate(addMonths(currentDate, 1))
    const goToCurrentMonth = () => setCurrentDate(new Date())
    const monthLabel = format(currentDate, "MMMM yyyy", { locale: es })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <BanknotesIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver las cobranzas, primero debés seleccionar una empresa.</p>
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
                        <BanknotesIcon className="w-7 h-7 text-emerald-600" />
                        Cobranzas
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Ingresos cobrados de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                {/* Month Selector */}
                <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-2 py-1.5 shadow-sm">
                    <button onClick={goToPrevMonth} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                        <ChevronLeftIcon className="w-4 h-4 text-gray-500" />
                    </button>
                    <button onClick={goToCurrentMonth} className="flex items-center gap-2 px-3 py-1 hover:bg-gray-50 rounded-lg transition-colors">
                        <CalendarDaysIcon className="w-4 h-4 text-emerald-500" />
                        <span className="text-sm font-semibold text-gray-700 capitalize min-w-[130px] text-center">{monthLabel}</span>
                    </button>
                    <button onClick={goToNextMonth} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                        <ChevronRightIcon className="w-4 h-4 text-gray-500" />
                    </button>
                </div>
            </div>

            {/* Summary */}
            <div className="glass-card p-6 flex items-center justify-between">
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Total Cobrado del Mes</p>
                    <p className="text-3xl font-black text-emerald-600 mt-1">+${totalIncome.toLocaleString('es-AR')}</p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-gray-400">{filtered.length} cobro{filtered.length !== 1 ? 's' : ''}</p>
                </div>
            </div>

            {/* Table */}
            <div className="glass-card overflow-hidden">
                <div className="px-6 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <h3 className="font-bold text-gray-900">Cobros Registrados</h3>
                    <div className="relative w-64">
                        <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                            placeholder="Buscar cobros..."
                            className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all" />
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">Error al cargar las cobranzas.</div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <BanknotesIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay cobros</h3>
                        <p className="mt-1 text-sm text-gray-500">No se registraron ingresos en <span className="capitalize">{monthLabel}</span>.</p>
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
                                            <td className="text-sm font-medium text-gray-500">
                                                {format(new Date(tx.transaction_date), "dd/MM/yyyy")}
                                            </td>
                                            <td>
                                                <div className="flex items-center gap-3">
                                                    <ArrowUpCircleIcon className="w-7 h-7 text-emerald-500 shrink-0" />
                                                    <div className="font-medium text-gray-900">{tx.description || '—'}</div>
                                                </div>
                                            </td>
                                             <td>
                                                {tx.client?.name ? (
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center text-[10px] font-bold">
                                                            {tx.client.name.substring(0, 2).toUpperCase()}
                                                        </div>
                                                        <span className="text-sm text-gray-700">{tx.client.name}</span>
                                                    </div>
                                                ) : <span className="text-sm text-gray-400">—</span>}
                                            </td>
                                            <td>
                                                {tx.service?.name ? (
                                                    <span className="text-[11px] font-semibold px-2 py-1 rounded-full bg-violet-50 text-violet-700">
                                                        {tx.service.name}
                                                    </span>
                                                ) : <span className="text-sm text-gray-400">—</span>}
                                            </td>
                                            <td className="text-sm text-gray-600">{tx.payment_method || '—'}</td>
                                            <td className="text-right font-bold text-lg text-emerald-600">
                                                +${Number(tx.amount).toLocaleString('es-AR')}
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
