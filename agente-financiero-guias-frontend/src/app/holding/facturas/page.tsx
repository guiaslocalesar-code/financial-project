'use client'

import { Fragment, useState, useMemo } from 'react'
import { Tab } from '@headlessui/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
    PlusIcon,
    DocumentTextIcon,
    ExclamationTriangleIcon,
    ClockIcon,
    CheckCircleIcon,
    ArrowPathIcon,
    ArrowPathRoundedSquareIcon,
    SparklesIcon,
    EyeIcon,
    PencilSquareIcon,
    CalendarDaysIcon,
    ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Invoice, Client, ClientService } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { generateInvoiceBatch } from '@/services/invoices'
import Link from 'next/link'
import { format, startOfMonth, endOfMonth, isWithinInterval, parseISO } from 'date-fns'
import { exportToCSV, exportToXML } from '@/utils/export'

const getOverdueDays = (dueDateStr: string, status: string): number => {
    if (status !== 'EMITTED') return 0
    if (!dueDateStr) return 0

    // Convert current time and due date to midnight to compare days accurately
    const now = new Date()
    now.setHours(0,0,0,0)

    // dueDate is usually YYYY-MM-DD from backend
    const [year, month, day] = dueDateStr.split('-').map(Number)
    const due = new Date(year, month - 1, day)
    due.setHours(0,0,0,0)

    const diffTime = now.getTime() - due.getTime()
    if (diffTime <= 0) return 0

    return Math.floor(diffTime / (1000 * 3600 * 24))
}

const getOverdueStatus = (days: number, status: string) => {
    if (status === 'DRAFT') return { label: 'Borrador', class: 'badge-neutral', icon: DocumentTextIcon }
    if (status === 'CANCELLED') return { label: 'Anulada', class: 'badge-neutral', icon: DocumentTextIcon }
    if (days > 7) return { label: `${days} días vencida`, class: 'badge-danger', icon: ExclamationTriangleIcon }
    if (days > 0) return { label: `${days} días vencida`, class: 'badge-warning', icon: ClockIcon }
    return { label: 'Al día', class: 'badge-success', icon: CheckCircleIcon }
}

export default function FacturasPage() {
    const queryClient = useQueryClient()
    const { selectedCompany } = useHoldingContext()
    const [startDate, setStartDate] = useState(format(startOfMonth(new Date()), 'yyyy-MM-dd'))
    const [endDate, setEndDate] = useState(format(endOfMonth(new Date()), 'yyyy-MM-dd'))
    const [showExportMenu, setShowExportMenu] = useState(false)

    // Used for recurring invoices batch generation (current month focus)
    const now = new Date()
    const currentMonth = now.getMonth() + 1
    const currentYear = now.getFullYear()

    const rangeStart = parseISO(startDate)
    const rangeEnd = parseISO(endDate)

    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || res.data.clients || []) as Client[]
        },
        enabled: !!selectedCompany,
    })

    const { data: invoices, isLoading: isLoadingInvoices, error } = useQuery({
        queryKey: ['invoices', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.invoices.list(selectedCompany.id)
            const list = Array.isArray(res.data) ? res.data : (res.data.data || res.data.invoices || []) as Invoice[]

            if (list.length > 0) {
                console.log('[Facturas]', { total: list[0].total, client: list[0].client?.name, cae: list[0].cae ?? 'Pendiente' })
            }

            return list
        },
        enabled: !!selectedCompany,
    })

    // Fetch all client services for recurring tab
    const { data: recurringContracts, isLoading: isLoadingRecurring } = useQuery({
        queryKey: ['recurring-contracts', selectedCompany?.id, clients?.length],
        queryFn: async () => {
            if (!selectedCompany || !clients || clients.length === 0) return []

            // Parallel fetch for all clients (following "no backend changes" rule)
            const allPromises = clients.map(client => api.clientServices.list(client.id))
            const results = await Promise.all(allPromises)

            const allContracts: ClientService[] = []
            results.forEach((res, index) => {
                const clientContracts = Array.isArray(res.data) ? res.data : (res.data.data || [])
                clientContracts.forEach((c: any) => {
                    allContracts.push({
                        ...c,
                        client_name: clients[index].name,
                        client: clients[index]
                    })
                })
            })

            return allContracts
        },
        enabled: !!selectedCompany && !!clients,
    })

    const emitMutation = useMutation({
        mutationFn: (invoiceId: string) => api.invoices.emit(invoiceId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['invoices', selectedCompany?.id] })
        },
        onError: (err: any) => {
            console.error('Emit error:', err.response?.data || err.message)
            alert(`Error al emitir factura en AFIP: ${err.response?.data?.detail || err.message}`)
        }
    })

    const batchMutation = useMutation({
        mutationFn: async () => {
            if (!selectedCompany || !recurringContracts || !invoices) return
            
            const activeContracts = recurringContracts.filter(c => c.status === 'ACTIVE')
            return generateInvoiceBatch(
                activeContracts,
                selectedCompany.id,
                invoices,
                currentMonth,
                currentYear
            )
        },
        onSuccess: (res) => {
            console.log('[Batch] Generación completada', res);
            queryClient.invalidateQueries({ queryKey: ['invoices', selectedCompany?.id] })
        }
    })

    const enrichedInvoices = useMemo(() => {
        if (!invoices || !clients) return []
        const clientMap = new Map((clients || []).map(c => [c.id, c.name]))
        return invoices
            .filter(inv => {
                const invDate = new Date(inv.issue_date)
                return isWithinInterval(invDate, { start: rangeStart, end: rangeEnd })
            })
            .map(inv => ({
                ...inv,
                client_name: clientMap.get(inv.client_id) || 'Cliente Desconocido',
                overdue_days: getOverdueDays(inv.due_date || inv.issue_date, inv.status)
            }))
    }, [invoices, clients, rangeStart, rangeEnd])

    const handleExport = (fmt: 'csv' | 'xml') => {
        const columnMap = {
            invoice_number: 'Nº Comprobante',
            client_name: 'Cliente',
            issue_date: 'Fecha Emisión',
            due_date: 'Vencimiento',
            total: 'Total',
            status: 'Estado',
            cae: 'CAE'
        }
        const rows = enrichedInvoices.map(inv => ({
            invoice_number: inv.invoice_number || 'Borrador',
            client_name: inv.client_name,
            issue_date: format(new Date(inv.issue_date), 'dd/MM/yyyy'),
            due_date: inv.due_date ? format(new Date(inv.due_date), 'dd/MM/yyyy') : '—',
            total: Number(inv.total),
            status: inv.status,
            cae: inv.cae || '—'
        }))
        const filename = `Facturas_${startDate}_${endDate}`
        if (fmt === 'csv') exportToCSV(rows, filename, columnMap)
        else exportToXML(rows, filename, 'Facturas', 'Factura', columnMap)
        setShowExportMenu(false)
    }

    const setMonthRange = (offset: number) => {
        const d = new Date()
        d.setMonth(d.getMonth() + offset)
        setStartDate(format(startOfMonth(d), 'yyyy-MM-dd'))
        setEndDate(format(endOfMonth(d), 'yyyy-MM-dd'))
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <DocumentTextIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para gestionar facturas, primero debés seleccionar una empresa del Holding.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <DocumentTextIcon className="w-7 h-7 text-blue-600" />
                        Facturación
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Gestión de comprobantes y contratos recurrentes de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <div className="flex flex-wrap gap-3">
                    <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2 shadow-sm order-2 sm:order-1">
                        <CalendarDaysIcon className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-bold text-gray-400 uppercase">Desde</span>
                        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-sm font-semibold text-gray-700 outline-none bg-transparent cursor-pointer" />
                        <span className="text-gray-300">|</span>
                        <span className="text-xs font-bold text-gray-400 uppercase">Hasta</span>
                        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-sm font-semibold text-gray-700 outline-none bg-transparent cursor-pointer" />
                    </div>
                    
                    <div className="flex items-center gap-2 order-3 sm:order-2">
                        <div className="relative">
                            <button 
                                onClick={() => setShowExportMenu(!showExportMenu)}
                                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
                                <ArrowDownTrayIcon className="w-4 h-4" />
                                Exportar
                            </button>
                            {showExportMenu && (
                                <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-20 overflow-hidden min-w-[140px]">
                                    <button onClick={() => handleExport('csv')} className="block w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 font-medium transition-colors">
                                        📊 CSV
                                    </button>
                                    <button onClick={() => handleExport('xml')} className="block w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 font-medium transition-colors border-t border-gray-100">
                                        📄 XML
                                    </button>
                                </div>
                            )}
                        </div>
                        <Link
                            href="/holding/facturas/editor"
                            className="btn-primary"
                        >
                            <PlusIcon className="w-5 h-5" />
                            Nueva
                        </Link>
                    </div>
                </div>
            </div>

            <Tab.Group>
                <div className="border-b border-gray-200">
                    <Tab.List className="flex gap-8 -mb-px">
                        {['Facturas', 'Recurrentes'].map((tab) => (
                            <Tab
                                key={tab}
                                className={({ selected }) =>
                                    clsx(
                                        'pb-4 text-sm font-semibold border-b-2 transition-all outline-none',
                                        selected
                                            ? 'border-blue-600 text-blue-600'
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
                    {/* Tab 1: Facturas */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="glass-card overflow-hidden">
                            {isLoadingInvoices ? (
                                <div className="p-12 flex justify-center">
                                    <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                                </div>
                            ) : error ? (
                                <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                                    Error al cargar las facturas.
                                </div>
                            ) : enrichedInvoices.length === 0 ? (
                                <div className="text-center py-16 px-4">
                                    <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-300" />
                                    <h3 className="mt-2 text-sm font-semibold text-gray-900">Sin facturas</h3>
                                    <p className="mt-1 text-sm text-gray-500">Todavía no has creado facturas para este negocio.</p>
                                    <div className="mt-6">
                                        <Link href="/holding/facturas/editor" className="btn-primary">
                                            <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                            Crear Primera Factura
                                        </Link>
                                    </div>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Nº Comprobante</th>
                                                <th>Cliente</th>
                                                <th>Fechas</th>
                                                <th className="text-right">Importe Total</th>
                                                <th>Estado</th>
                                                <th className="text-right">Acción</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {enrichedInvoices
                                                .sort((a,b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                                                .map((inv) => {
                                                    const statusInfo = getOverdueStatus(inv.overdue_days || 0, inv.status)
                                                    return (
                                                        <tr key={inv.id}>
                                                            <td>
                                                                <div className="font-mono text-sm font-semibold text-gray-900">
                                                                    {inv.invoice_number || <span className="text-gray-400 font-sans italic">Borrador ({inv.invoice_type})</span>}
                                                                </div>
                                                                {inv.cae && <div className="text-xs text-gray-500 mt-0.5">CAE: {inv.cae}</div>}
                                                            </td>
                                                            <td className="font-medium text-gray-800">{inv.client_name}</td>
                                                            <td>
                                                                <div className="text-sm text-gray-900">
                                                                    Creación: {new Date(inv.created_at).toLocaleDateString('es-AR')}
                                                                </div>
                                                                <div className="text-xs text-gray-500">
                                                                    Vto: {inv.due_date ? new Date(inv.due_date).toLocaleDateString('es-AR') : '—'}
                                                                </div>
                                                            </td>
                                                            <td className="text-right font-bold text-gray-900 whitespace-nowrap">
                                                                ${Number(inv.total).toLocaleString('es-AR', {minimumFractionDigits: 2})}
                                                            </td>
                                                            <td>
                                                                <span className={statusInfo.class}>
                                                                    <statusInfo.icon className="w-3.5 h-3.5" />
                                                                    {statusInfo.label}
                                                                </span>
                                                            </td>
                                                            <td className="text-right">
                                                                <div className="flex items-center justify-end gap-2">
                                                                    <Link
                                                                        href={`/holding/facturas/editor/${inv.id}`}
                                                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
                                                                    >
                                                                        {inv.status === 'DRAFT' ? (
                                                                            <><PencilSquareIcon className="w-3.5 h-3.5" /> Editar</>
                                                                        ) : (
                                                                            <><EyeIcon className="w-3.5 h-3.5" /> Ver</>
                                                                        )}
                                                                    </Link>
                                                                    {inv.status === 'DRAFT' && (
                                                                        <button
                                                                            onClick={() => emitMutation.mutate(inv.id)}
                                                                            disabled={emitMutation.isPending && emitMutation.variables === inv.id}
                                                                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200"
                                                                        >
                                                                            {(emitMutation.isPending && emitMutation.variables === inv.id) ? (
                                                                                <ArrowPathIcon className="w-4 h-4 animate-spin" />
                                                                            ) : (
                                                                                'Emitir (AFIP)'
                                                                            )}
                                                                        </button>
                                                                    )}
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    )
                                                })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </Tab.Panel>

                    {/* Tab 2: Recurrentes */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="flex justify-between items-center mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Contratos Mensuales</h3>
                                <p className="text-sm text-gray-500">Próximo período: {currentMonth}/{currentYear}</p>
                            </div>
                            <button
                                onClick={() => batchMutation.mutate()}
                                disabled={batchMutation.isPending || !recurringContracts?.length}
                                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl font-semibold shadow-sm hover:bg-blue-700 transition-all disabled:opacity-50"
                            >
                                {batchMutation.isPending ? (
                                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                                ) : (
                                    <ArrowPathRoundedSquareIcon className="w-5 h-5" />
                                )}
                                Generar Facturas del Mes
                            </button>
                        </div>

                        <div className="glass-card overflow-hidden">
                            {isLoadingRecurring ? (
                                <div className="p-12 flex justify-center">
                                    <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                                </div>
                            ) : !recurringContracts || recurringContracts.length === 0 ? (
                                <div className="text-center py-16 px-4">
                                    <ArrowPathRoundedSquareIcon className="mx-auto h-12 w-12 text-gray-300" />
                                    <h3 className="mt-2 text-sm font-semibold text-gray-900">Sin contratos</h3>
                                    <p className="mt-1 text-sm text-gray-500">No hay servicios recurrentes activos en tus clientes.</p>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Cliente</th>
                                                <th>Servicio</th>
                                                <th className="text-right">Monto Mensual</th>
                                                <th>Estado</th>
                                                <th>Auto-Factura</th>
                                                <th className="text-right">Estado Borrador</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {recurringContracts.map((contract) => {
                                                const hasDraft = enrichedInvoices.some(inv => {
                                                    const invDate = new Date(inv.issue_date)
                                                    return inv.client_id === contract.client_id &&
                                                           (invDate.getMonth() + 1) === currentMonth &&
                                                           invDate.getFullYear() === currentYear &&
                                                            inv.items?.some((it: any) => it.service_id === contract.service_id)
                                                })

                                                return (
                                                    <tr key={contract.id}>
                                                        <td className="font-medium text-gray-900">{contract.client_name}</td>
                                                        <td className="text-gray-700">{contract.service?.name || contract.service_name}</td>
                                                        <td className="text-right font-bold text-gray-800">
                                                            ${contract.monthly_fee.toLocaleString('es-AR')} {contract.currency}
                                                        </td>
                                                        <td>
                                                            <span className={clsx(
                                                                'badge',
                                                                contract.status === 'ACTIVE' ? 'badge-success' :
                                                                contract.status === 'PAUSED' ? 'badge-warning' : 'badge-neutral'
                                                            )}>
                                                                {contract.status === 'ACTIVE' ? 'Activo' :
                                                                 contract.status === 'PAUSED' ? 'Pausado' : 'Cancelado'}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <div className="flex items-center gap-2">
                                                                <input
                                                                    type="checkbox"
                                                                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                                    defaultChecked={contract.status === 'ACTIVE'}
                                                                />
                                                                <span className="text-xs text-gray-500 italic">Si</span>
                                                            </div>
                                                        </td>
                                                        <td className="text-right">
                                                            {hasDraft ? (
                                                                <span className="badge badge-success bg-emerald-50 text-emerald-700 border-emerald-100 gap-1.5">
                                                                    <CheckCircleIcon className="w-3.5 h-3.5" />
                                                                    Borrador generado
                                                                </span>
                                                            ) : (
                                                                <span className="text-xs text-gray-400 italic">Pendiente</span>
                                                            )}
                                                        </td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </Tab.Panel>
                </Tab.Panels>
            </Tab.Group>

        </div>
    )
}
