'use client'

import { useMemo } from 'react'
import { useHoldingContext } from '@/context/HoldingContext'
import { api } from '@/services/api'
import {
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon,
    ExclamationTriangleIcon,
    ClockIcon,
    CheckCircleIcon,
    CurrencyDollarIcon,
    DocumentTextIcon,
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
} from 'recharts'
import { useQuery } from '@tanstack/react-query'
import type { Transaction, Invoice, Client } from '@/types'
import { format, subMonths, startOfMonth, endOfMonth, isWithinInterval } from 'date-fns'
import { es } from 'date-fns/locale'

// ─── Helpers ─────────────────────────────────────────────────────────────────

const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount)

const getOverdueStatus = (days: number, status: string) => {
    if (status === 'DRAFT') return { label: 'Borrador', class: 'badge-neutral', icon: DocumentTextIcon }
    if (status === 'CANCELLED') return { label: 'Anulada', class: 'badge-neutral', icon: DocumentTextIcon }
    if (days > 7) return { label: `${days} días de atraso`, class: 'badge-danger', icon: ExclamationTriangleIcon }
    if (days > 0) return { label: `${days} días de atraso`, class: 'badge-warning', icon: ClockIcon }
    return { label: 'Al día', class: 'badge-success', icon: CheckCircleIcon }
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function HoldingDashboard() {
    const { selectedCompany } = useHoldingContext()

    // 1. Fetch ALL transactions — the source of truth for KPIs & charts
    const { data: transactions, isLoading: isLoadingTx } = useQuery({
        queryKey: ['transactions', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.transactions.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as Transaction[]
        },
        enabled: !!selectedCompany,
    })

    // 2. Fetch clients to map names
    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as Client[]
        },
        enabled: !!selectedCompany,
    })

    // 3. Fetch services to map names
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

    // 4. Fetch dashboard summary (KPIs)
    const { data: summary, isLoading: isLoadingSummary } = useQuery({
        queryKey: ['dashboard-summary', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return null
            const res = await api.dashboard.summary(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany,
    })

    // 5. Fetch invoices
    const { data: invoices, isLoading: isLoadingInvoices } = useQuery({
        queryKey: ['invoices', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.invoices.list(selectedCompany.id)
            const list = (Array.isArray(res.data) ? res.data : (res.data.data || [])) as Invoice[]
            return list.map(inv => {
                let overdue_days = 0
                if (inv.status === 'EMITTED' && (inv.due_date || inv.issue_date)) {
                    const today = new Date(); today.setHours(0, 0, 0, 0)
                    const [year, month, day] = (inv.due_date || inv.issue_date).split('-').map(Number)
                    const due = new Date(year, month - 1, day); due.setHours(0, 0, 0, 0)
                    const diff = today.getTime() - due.getTime()
                    if (diff > 0) overdue_days = Math.floor(diff / (1000 * 3600 * 24))
                }
                // Enrich with client object for consistent mapping
                return { 
                    ...inv, 
                    client: { name: clientMap.get(inv.client_id) || 'Cliente' },
                    overdue_days 
                }
            }).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        },
        enabled: !!selectedCompany && !!clients,
    })

    // ─── Compute KPIs from real transactions ────────────────────────────────
    // ─── KPIs from Summary Endpoint ─────────────────────────────────────────
    const totalIncome = summary?.total_income || 0
    const totalExpenses = summary?.total_expenses || 0
    const netProfit = summary?.balance || 0
    const profitMargin = totalIncome > 0 ? ((netProfit / totalIncome) * 100).toFixed(1) : '0.0'

    const overdueInvoices = useMemo(
        () => (invoices || []).filter(inv => inv.overdue_days && inv.overdue_days > 0),
        [invoices]
    )
    const pendingInvoices = useMemo(
        () => (invoices || []).filter(inv => inv.status === 'EMITTED'),
        [invoices]
    )

    // ─── Compute chart data (last 6 months) ────────────────────────────────
    const chartData = useMemo(() => {
        const now = new Date()
        const months: { month: string; Ingresos: number; Egresos: number; Ganancia: number }[] = []

        for (let i = 5; i >= 0; i--) {
            const date = subMonths(now, i)
            const mStart = startOfMonth(date)
            const mEnd = endOfMonth(date)
            const label = format(date, 'MMM', { locale: es })

            let income = 0
            let expense = 0

            if (transactions) {
                transactions.forEach((tx) => {
                    const txDate = new Date(tx.transaction_date)
                    if (isWithinInterval(txDate, { start: mStart, end: mEnd })) {
                        if (tx.type === 'INCOME') income += Number(tx.amount)
                        else expense += Number(tx.amount)
                    }
                })
            }

            months.push({
                month: label.charAt(0).toUpperCase() + label.slice(1),
                Ingresos: income,
                Egresos: expense,
                Ganancia: income - expense,
            })
        }

        return months
    }, [transactions])

    const isLoading = isLoadingTx || isLoadingInvoices || !clients || !services

    return (
        <div className="space-y-8 animate-fade-in-up">
            {/* Page Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard Financiero</h1>
                <p className="mt-1 text-sm text-gray-500">
                    {selectedCompany ? (
                        <>Resumen de <span className="font-semibold text-gray-700">{selectedCompany.name}</span></>
                    ) : 'Seleccioná una empresa para ver su resumen.'}
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="metric-card">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-500">Ingresos Totales</span>
                        <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                            <ArrowTrendingUpIcon className="w-5 h-5 text-emerald-600" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalIncome)}</p>
                    <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1">
                        <ArrowTrendingUpIcon className="w-3 h-3" /> ingresos cobrados
                    </p>
                </div>

                <div className="metric-card">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-500">Egresos Totales</span>
                        <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center">
                            <ArrowTrendingDownIcon className="w-5 h-5 text-rose-600" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalExpenses)}</p>
                    <p className="text-xs text-rose-600 mt-1 flex items-center gap-1">
                        <ArrowTrendingDownIcon className="w-3 h-3" /> egresos pagados
                    </p>
                </div>

                <div className="metric-card">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-500">Ganancia Neta</span>
                        <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                            <CurrencyDollarIcon className="w-5 h-5 text-blue-600" />
                        </div>
                    </div>
                    <p className={clsx("text-2xl font-bold", netProfit >= 0 ? "text-gray-900" : "text-rose-600")}>
                        {formatCurrency(netProfit)}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">Margen: {profitMargin}%</p>
                </div>

                <div className="metric-card border-l-4 border-l-rose-400">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-500">Facturas Vencidas</span>
                        <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
                            <ExclamationTriangleIcon className="w-5 h-5 text-amber-600" />
                        </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <p className="text-2xl font-bold text-rose-600">{overdueInvoices.length}</p>
                        <span className="text-sm text-gray-400">de {pendingInvoices.length} pendientes</span>
                    </div>
                    <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                        <ClockIcon className="w-3 h-3" /> Requiere atención
                    </p>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-6">
                    <h3 className="text-base font-semibold text-gray-900 mb-4">Ingresos vs Egresos</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                            <defs>
                                <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#9ca3af' }} />
                            <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                            <Tooltip
                                formatter={(value: number) => formatCurrency(value)}
                                contentStyle={{ background: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontSize: '13px' }}
                            />
                            <Area type="monotone" dataKey="Ingresos" stroke="#10B981" strokeWidth={2.5} fill="url(#incomeGrad)" />
                            <Area type="monotone" dataKey="Egresos" stroke="#F43F5E" strokeWidth={2.5} fill="url(#expenseGrad)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                <div className="glass-card p-6">
                    <h3 className="text-base font-semibold text-gray-900 mb-4">Ganancia Mensual</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                            <defs>
                                <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#3B82F6" />
                                    <stop offset="100%" stopColor="#6366F1" />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#9ca3af' }} />
                            <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                            <Tooltip
                                formatter={(value: number) => formatCurrency(value)}
                                contentStyle={{ background: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontSize: '13px' }}
                            />
                            <Bar dataKey="Ganancia" fill="url(#profitGrad)" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Latest Invoices */}
            <div className="glass-card overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                    <div>
                        <h3 className="text-base font-semibold text-gray-900">Últimas Facturas</h3>
                        <p className="text-xs text-gray-500 mt-0.5">Estado de cobranza y días de atraso</p>
                    </div>
                    {overdueInvoices.length > 0 && (
                        <span className="badge-danger">
                            <ExclamationTriangleIcon className="w-3.5 h-3.5" />
                            {overdueInvoices.length} vencida{overdueInvoices.length > 1 ? 's' : ''}
                        </span>
                    )}
                </div>

                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                    </div>
                ) : !invoices || invoices.length === 0 ? (
                    <div className="text-center py-12 px-4">
                        <DocumentTextIcon className="mx-auto h-10 w-10 text-gray-300" />
                        <p className="mt-2 text-sm text-gray-500">No hay facturas registradas.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Nº Factura</th>
                                    <th>Cliente</th>
                                    <th className="text-right">Monto</th>
                                    <th>Vencimiento</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoices.slice(0, 10).map((inv) => {
                                    const overdueInfo = getOverdueStatus(inv.overdue_days || 0, inv.status)
                                    return (
                                        <tr key={inv.id} className="group">
                                            <td className="font-mono text-xs text-gray-500">
                                                {inv.invoice_number || '—'}
                                            </td>
                                            <td className="font-medium text-gray-900">{inv.client?.name}</td>
                                            <td className="text-right font-semibold text-gray-900 tabular-nums">
                                                {formatCurrency(inv.total)}
                                            </td>
                                            <td className="text-gray-600">
                                                {inv.due_date ? new Date(inv.due_date).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                                            </td>
                                            <td>
                                                <span className={overdueInfo.class}>
                                                    <overdueInfo.icon className="w-3.5 h-3.5" />
                                                    {overdueInfo.label}
                                                </span>
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Latest Transactions */}
            {transactions && transactions.length > 0 && (
                <div className="glass-card overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100">
                        <h3 className="text-base font-semibold text-gray-900">Últimos Movimientos</h3>
                        <p className="text-xs text-gray-500 mt-0.5">Las 10 transacciones más recientes</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Concepto</th>
                                    <th>Cliente</th>
                                    <th>Servicio</th>
                                    <th>Tipo</th>
                                    <th className="text-right">Monto</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.slice(0, 10).map((rawTx) => {
                                    // Map to enriched structure for consistent property access
                                    const tx = {
                                        ...rawTx,
                                        client: rawTx.client_id ? { name: clientMap.get(rawTx.client_id) || '—' } : undefined,
                                        service: rawTx.service_id ? { name: serviceMap.get(rawTx.service_id) || '—' } : undefined
                                    }
                                    
                                    return (
                                        <tr key={tx.id}>
                                            <td className="text-sm text-gray-500">
                                                {new Date(tx.transaction_date).toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })}
                                            </td>
                                            <td className="font-medium text-gray-900">{tx.description || '—'}</td>
                                            <td>
                                                {tx.client?.name ? (
                                                    <span className="text-sm text-gray-700">{tx.client.name}</span>
                                                ) : <span className="text-gray-400">—</span>}
                                            </td>
                                            <td>
                                                {tx.service?.name ? (
                                                    <span className="text-[11px] font-semibold px-2 py-1 rounded-full bg-violet-50 text-violet-700">
                                                        {tx.service.name}
                                                    </span>
                                                ) : <span className="text-gray-400">—</span>}
                                            </td>
                                            <td>
                                                <span className={clsx(
                                                    'text-[10px] font-bold uppercase px-2 py-1 rounded-full',
                                                    tx.type === 'INCOME' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                                                )}>
                                                    {tx.type === 'INCOME' ? 'Ingreso' : 'Egreso'}
                                                </span>
                                            </td>
                                            <td className={clsx(
                                                "text-right font-bold",
                                                tx.type === 'INCOME' ? "text-emerald-600" : "text-rose-600"
                                            )}>
                                                {tx.type === 'INCOME' ? '+' : '-'}{formatCurrency(Number(tx.amount))}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
