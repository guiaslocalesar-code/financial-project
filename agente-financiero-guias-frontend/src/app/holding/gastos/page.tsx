'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowDownCircleIcon, MagnifyingGlassIcon, CalendarDaysIcon, CalculatorIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Transaction, ExpenseType, ExpenseCategory } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { format, startOfMonth, endOfMonth, isWithinInterval, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { exportToCSV, exportToXML } from '@/utils/export'

export default function GastosPage() {
    const { selectedCompany } = useHoldingContext()
    const [search, setSearch] = useState('')
    const [startDate, setStartDate] = useState(format(startOfMonth(new Date()), 'yyyy-MM-dd'))
    const [endDate, setEndDate] = useState(format(endOfMonth(new Date()), 'yyyy-MM-dd'))
    const [showExportMenu, setShowExportMenu] = useState(false)

    const rangeStart = parseISO(startDate)
    const rangeEnd = parseISO(endDate)

    // Fetch expense types for name mapping
    const { data: expenseTypes } = useQuery({
        queryKey: ['expenseTypes', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listTypes(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as ExpenseType[]
        },
        enabled: !!selectedCompany,
    })

    // Fetch expense categories for name mapping
    const { data: expenseCategories } = useQuery({
        queryKey: ['expenseCategories', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listCategories(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as ExpenseCategory[]
        },
        enabled: !!selectedCompany,
    })

    // Name maps
    const typeMap = useMemo(() => new Map((expenseTypes || []).map(t => [t.id, t.name])), [expenseTypes])
    const catMap = useMemo(() => new Map((expenseCategories || []).map(c => [c.id, c.name])), [expenseCategories])

    // Fetch transactions
    const { data: allTransactions, isLoading, error } = useQuery({
        queryKey: ['transactions', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.transactions.list(selectedCompany.id)
            const txs = (Array.isArray(res.data) ? res.data : res.data.data || []) as Transaction[]
            
            // Enrich with expense type and category objects
            const enriched = txs.map(tx => ({
                ...tx,
                expense_type: tx.expense_type_id ? { name: typeMap.get(tx.expense_type_id) || '—' } : undefined,
                expense_category: tx.expense_category_id ? { name: catMap.get(tx.expense_category_id) || '—' } : undefined
            }))

            return enriched
        },
        enabled: !!selectedCompany && !!expenseTypes && !!expenseCategories,
    })

    // Only EXPENSE, filtered by date range and search
    const filtered = useMemo(() => {
        if (!allTransactions) return []
        return allTransactions.filter((tx) => {
            if (tx.type !== 'EXPENSE') return false
            const txDate = new Date(tx.transaction_date)
            if (!isWithinInterval(txDate, { start: rangeStart, end: rangeEnd })) return false
            if (search) {
                const q = search.toLowerCase()
                const typeName = tx.expense_type?.name || ''
                const catName = tx.expense_category?.name || ''
                return (
                    tx.description?.toLowerCase().includes(q) ||
                    tx.payment_method?.toLowerCase().includes(q) ||
                    typeName.toLowerCase().includes(q) ||
                    catName.toLowerCase().includes(q)
                )
            }
            return true
        })
    }, [allTransactions, search, rangeStart, rangeEnd])

    const totalExpenses = useMemo(() => filtered.reduce((sum, tx) => sum + Number(tx.amount), 0), [filtered])

    const handleExport = (fmt: 'csv' | 'xml') => {
        const columnMap = {
            transaction_date: 'Fecha',
            description: 'Concepto',
            _type: 'Tipo de Gasto',
            _category: 'Categoría',
            payment_method: 'Método de Pago',
            amount: 'Monto',
        }
        const rows = filtered.map(tx => ({
            transaction_date: format(new Date(tx.transaction_date), 'dd/MM/yyyy'),
            description: tx.description || '',
            _type: tx.expense_type?.name || '',
            _category: tx.expense_category?.name || '',
            payment_method: tx.payment_method || '',
            amount: Number(tx.amount),
        }))
        const filename = `Gastos_${startDate}_${endDate}`
        if (fmt === 'csv') exportToCSV(rows, filename, columnMap)
        else exportToXML(rows, filename, 'Gastos', 'Gasto', columnMap)
        setShowExportMenu(false)
    }

    // Month quick select helpers
    const setMonth = (offset: number) => {
        const d = new Date()
        d.setMonth(d.getMonth() + offset)
        setStartDate(format(startOfMonth(d), 'yyyy-MM-dd'))
        setEndDate(format(endOfMonth(d), 'yyyy-MM-dd'))
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <CalculatorIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los gastos, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <CalculatorIcon className="w-7 h-7 text-rose-600" />
                        Gastos y Egresos
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Egresos pagados de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                {/* Date Range Selector + Quick Month Buttons */}
                <div className="flex flex-wrap items-center gap-2">
                    <div className="flex items-center gap-1 bg-gray-50 rounded-lg px-1 py-1 text-xs">
                        <button onClick={() => setMonth(0)} className="px-2 py-1 rounded-md hover:bg-white hover:shadow-sm transition-all font-semibold text-gray-600">
                            Este Mes
                        </button>
                        <button onClick={() => setMonth(-1)} className="px-2 py-1 rounded-md hover:bg-white hover:shadow-sm transition-all font-semibold text-gray-600">
                            Mes Anterior
                        </button>
                    </div>
                    <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2 shadow-sm">
                        <CalendarDaysIcon className="w-4 h-4 text-rose-500" />
                        <span className="text-xs font-bold text-gray-400 uppercase">Desde</span>
                        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-sm font-semibold text-gray-700 outline-none bg-transparent cursor-pointer" />
                        <span className="text-gray-300">|</span>
                        <span className="text-xs font-bold text-gray-400 uppercase">Hasta</span>
                        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-sm font-semibold text-gray-700 outline-none bg-transparent cursor-pointer" />
                    </div>
                </div>
            </div>

            {/* Summary */}
            <div className="glass-card p-6 flex items-center justify-between">
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Total Egresos</p>
                    <p className="text-3xl font-black text-rose-600 mt-1">-${totalExpenses.toLocaleString('es-AR')}</p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-gray-400">{filtered.length} egreso{filtered.length !== 1 ? 's' : ''}</p>
                </div>
            </div>

            {/* Table */}
            <div className="glass-card relative">
                <div className="px-6 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <h3 className="font-bold text-gray-900">Egresos Registrados</h3>
                    <div className="flex items-center gap-3">
                        <div className="relative w-64">
                            <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                                placeholder="Buscar egresos..."
                                className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-none transition-all" />
                        </div>
                        {/* Export Button */}
                        <div className="relative">
                            <button 
                                onClick={() => setShowExportMenu(!showExportMenu)}
                                disabled={filtered.length === 0}
                                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
                                <ArrowDownTrayIcon className="w-4 h-4" />
                                Exportar
                            </button>
                            {showExportMenu && (
                                <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-20 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
                                    <button onClick={() => handleExport('csv')} className="block w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 font-medium transition-colors">
                                        📊 Descargar CSV
                                    </button>
                                    <button onClick={() => handleExport('xml')} className="block w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 font-medium transition-colors border-t border-gray-100">
                                        📄 Descargar XML
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-rose-200 border-t-rose-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">Error al cargar los gastos.</div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <CalculatorIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay egresos</h3>
                        <p className="mt-1 text-sm text-gray-500">No se registraron gastos en el rango seleccionado.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Concepto</th>
                                    <th>Tipo de Gasto</th>
                                    <th>Categoría</th>
                                    <th>Método</th>
                                    <th className="text-right">Monto</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((tx) => {
                                    return (
                                        <tr key={tx.id}>
                                            <td className="text-sm font-medium text-gray-500">
                                                {format(new Date(tx.transaction_date), "dd/MM/yyyy")}
                                            </td>
                                            <td>
                                                <div className="flex items-center gap-3">
                                                    <ArrowDownCircleIcon className="w-7 h-7 text-rose-500 shrink-0" />
                                                    <div className="font-medium text-gray-900">{tx.description || '—'}</div>
                                                </div>
                                            </td>
                                             <td>
                                                {tx.expense_type?.name ? (
                                                    <span className="text-[11px] font-semibold px-2 py-1 rounded-full bg-amber-50 text-amber-700">
                                                        {tx.expense_type.name}
                                                    </span>
                                                ) : (
                                                    <span className="text-sm text-gray-400">—</span>
                                                )}
                                            </td>
                                            <td>
                                                {tx.expense_category?.name ? (
                                                    <span className="text-[11px] font-semibold px-2 py-1 rounded-full bg-orange-50 text-orange-700">
                                                        {tx.expense_category.name}
                                                    </span>
                                                ) : (
                                                    <span className="text-sm text-gray-400">—</span>
                                                )}
                                            </td>
                                            <td className="text-sm text-gray-600">{tx.payment_method || '—'}</td>
                                            <td className="text-right font-bold text-lg text-rose-600">
                                                -${Number(tx.amount).toLocaleString('es-AR')}
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
