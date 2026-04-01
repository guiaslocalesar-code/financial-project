'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
    ChartBarIcon, 
    ArrowTrendingUpIcon, 
    ArrowTrendingDownIcon, 
    CircleStackIcon,
    CalendarIcon,
    ChevronDownIcon
} from '@heroicons/react/24/outline'
import { Listbox, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import { format, startOfMonth, endOfMonth } from 'date-fns'

const MONTHS = [
    { id: 1, name: 'Enero' }, { id: 2, name: 'Febrero' }, { id: 3, name: 'Marzo' },
    { id: 4, name: 'Abril' }, { id: 5, name: 'Mayo' }, { id: 6, name: 'Junio' },
    { id: 7, name: 'Julio' }, { id: 8, name: 'Agosto' }, { id: 9, name: 'Septiembre' },
    { id: 10, name: 'Octubre' }, { id: 11, name: 'Noviembre' }, { id: 12, name: 'Diciembre' },
]

const YEARS = Array.from({ length: 5 }, (_, i) => 2024 + i)

const formatCurrency = (val: number) => 
    val.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })

export default function ReportesPage() {
    const { selectedCompany } = useHoldingContext()
    
    // Default period: Marzo 2026
    const [month, setMonth] = useState(3)
    const [year, setYear] = useState(2026)

    // ── Queries ──
    const { data: summary, isLoading: loadingSummary } = useQuery({
        queryKey: ['dashboard-summary', selectedCompany?.id, month, year],
        queryFn: async () => {
            if (!selectedCompany) return null
            const baseDate = new Date(year, month - 1, 1)
            const startDate = format(startOfMonth(baseDate), 'yyyy-MM-dd')
            const endDate = format(endOfMonth(baseDate), 'yyyy-MM-dd')
            const res = await api.dashboard.summary(selectedCompany.id, startDate, endDate)
            const data = res.data
            
            if (data) {
                console.log('[Reportes - Resumen]', { 
                    ingresos: data.total_income, 
                    egresos: data.total_expenses, 
                    saldo: data.balance 
                })
            }
            return data
        },
        enabled: !!selectedCompany,
    })

    const { data: profitability, isLoading: loadingProfit } = useQuery({
        queryKey: ['dashboard-profitability', selectedCompany?.id, month, year],
        queryFn: async () => {
            if (!selectedCompany) return []
            const baseDate = new Date(year, month - 1, 1)
            const startDate = format(startOfMonth(baseDate), 'yyyy-MM-dd')
            const endDate = format(endOfMonth(baseDate), 'yyyy-MM-dd')
            const res = await api.dashboard.profitability(selectedCompany.id, startDate, endDate)
            const data = Array.isArray(res.data) ? res.data : (res.data.data || [])
            
            if (data && data.length > 0) {
                console.log('[Reportes - Rentabilidad]', { 
                    servicio: data[0].service_name, 
                    ingreso: data[0].income, 
                    margen: data[0].margin 
                })
            }
            return data
        },
        enabled: !!selectedCompany,
    })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <ChartBarIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los reportes financieros, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header + Period Filter */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ChartBarIcon className="w-7 h-7 text-indigo-600" />
                        Reportes Financieros
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Análisis detallado de rendimiento para <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>

                <div className="flex items-center gap-3 bg-white p-1.5 rounded-2xl border border-gray-200 shadow-sm">
                    {/* Month Picker */}
                    <Listbox value={month} onChange={setMonth}>
                        <div className="relative">
                            <Listbox.Button className="relative w-36 px-4 py-2 text-left bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-sm font-semibold text-gray-700 flex items-center justify-between">
                                <span>{MONTHS.find(m => m.id === month)?.name}</span>
                                <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                            </Listbox.Button>
                            <Transition as={Fragment} leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0">
                                <Listbox.Options className="absolute mt-2 max-h-60 w-full overflow-auto rounded-xl bg-white py-1 text-sm shadow-xl ring-1 ring-black/5 focus:outline-none z-50">
                                    {MONTHS.map((m) => (
                                        <Listbox.Option key={m.id} value={m.id} className={({ active }) => clsx('relative cursor-default select-none py-2 px-4', active ? 'bg-indigo-50 text-indigo-900' : 'text-gray-900')}>
                                            {m.name}
                                        </Listbox.Option>
                                    ))}
                                </Listbox.Options>
                            </Transition>
                        </div>
                    </Listbox>

                    {/* Year Picker */}
                    <Listbox value={year} onChange={setYear}>
                        <div className="relative">
                            <Listbox.Button className="relative w-28 px-4 py-2 text-left bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-sm font-semibold text-gray-700 flex items-center justify-between">
                                <span>{year}</span>
                                <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                            </Listbox.Button>
                            <Transition as={Fragment} leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0">
                                <Listbox.Options className="absolute mt-2 max-h-60 w-full overflow-auto rounded-xl bg-white py-1 text-sm shadow-xl ring-1 ring-black/5 focus:outline-none z-50">
                                    {YEARS.map((y) => (
                                        <Listbox.Option key={y} value={y} className={({ active }) => clsx('relative cursor-default select-none py-2 px-4', active ? 'bg-indigo-50 text-indigo-900' : 'text-gray-900')}>
                                            {y}
                                        </Listbox.Option>
                                    ))}
                                </Listbox.Options>
                            </Transition>
                        </div>
                    </Listbox>
                    
                    <div className="p-2 bg-indigo-50 rounded-xl">
                        <CalendarIcon className="w-5 h-5 text-indigo-600" />
                    </div>
                </div>
            </div>

            {/* Section 1: KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="glass-card p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <ArrowTrendingUpIcon className="w-16 h-16 text-emerald-600" />
                    </div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Ingresos Totales</p>
                    <div className="mt-2 flex items-baseline gap-2">
                        <h3 className="text-3xl font-black text-gray-900">
                            {loadingSummary ? '...' : formatCurrency(summary?.total_income || 0)}
                        </h3>
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-xs font-semibold text-emerald-600">Cobrado en {MONTHS.find(m => m.id === month)?.name}</span>
                    </div>
                </div>

                <div className="glass-card p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <ArrowTrendingDownIcon className="w-16 h-16 text-rose-600" />
                    </div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Egresos Totales</p>
                    <div className="mt-2 flex items-baseline gap-2">
                        <h3 className="text-3xl font-black text-gray-900">
                            {loadingSummary ? '...' : formatCurrency(summary?.total_expenses || 0)}
                        </h3>
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-rose-500" />
                        <span className="text-xs font-semibold text-rose-600">Pagado este mes</span>
                    </div>
                </div>

                <div className="glass-card p-6 bg-gradient-to-br from-indigo-600 to-violet-700 text-white relative overflow-hidden group">
                     <div className="absolute top-0 right-0 p-4 opacity-20">
                        <CircleStackIcon className="w-16 h-16 text-white" />
                    </div>
                    <p className="text-xs font-bold text-indigo-100 uppercase tracking-widest">Saldo Neto</p>
                    <div className="mt-2 flex items-baseline gap-2">
                        <h3 className="text-3xl font-black">
                            {loadingSummary ? '...' : formatCurrency(summary?.balance || 0)}
                        </h3>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-indigo-100">
                        <span className="text-xs font-medium">Margen Operativo de {((summary?.balance / (summary?.total_income || 1)) * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            {/* Section 2: Profitability Table */}
            <div className="glass-card overflow-hidden">
                <div className="px-6 py-5 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold text-gray-900">Rentabilidad por Servicio</h3>
                        <p className="text-xs text-gray-500 mt-1 uppercase tracking-tight font-semibold">Desglose de márgenes por unidad de negocio</p>
                    </div>
                </div>

                {loadingProfit ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                    </div>
                ) : !profitability || profitability.length === 0 ? (
                    <div className="text-center py-20 px-8">
                         <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-gray-100">
                            <ChartBarIcon className="w-8 h-8 text-gray-300" />
                        </div>
                        <h4 className="text-sm font-bold text-gray-900">No hay datos de rentabilidad</h4>
                        <p className="mt-1 text-sm text-gray-500 max-w-xs mx-auto">No se registraron transacciones para los servicios en este período.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th className="pl-6">Servicio</th>
                                    <th className="text-right">Ingresos</th>
                                    <th className="text-right">Egresos</th>
                                    <th className="text-right pr-6">Margen</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {profitability.map((item: any, idx: number) => (
                                    <tr key={idx} className="hover:bg-gray-50/80 transition-colors group">
                                        <td className="pl-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-[10px] font-black group-hover:scale-110 transition-transform">
                                                    {item.service_name.substring(0, 2).toUpperCase()}
                                                </div>
                                                <span className="font-bold text-gray-900">{item.service_name}</span>
                                            </div>
                                        </td>
                                        <td className="text-right font-medium text-emerald-600">
                                            {formatCurrency(item.income)}
                                        </td>
                                        <td className="text-right font-medium text-rose-500">
                                            {formatCurrency(item.expenses)}
                                        </td>
                                        <td className="text-right pr-6">
                                            <span className={clsx(
                                                'inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-black',
                                                item.margin >= 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                                            )}>
                                                {formatCurrency(item.margin)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
