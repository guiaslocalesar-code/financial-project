'use client'

import { useState } from 'react'
import { Tab } from '@headlessui/react'
import { 
    BanknotesIcon, 
    ArrowPathRoundedSquareIcon,
    UsersIcon,
    AdjustmentsHorizontalIcon,
    ArchiveBoxIcon,
    FunnelIcon,
    ChevronLeftIcon,
    ChevronRightIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { useHoldingContext } from '@/context/HoldingContext'
import { useCommissions } from '@/hooks/useCommissions'
import { CommissionsSummaryWidget } from '@/components/commissions/CommissionsSummaryWidget'
import { CommissionsTable } from '@/components/commissions/CommissionsTable'
import { CommissionPayModal } from '@/components/commissions/CommissionPayModal'
import { CommissionRecipientsTab } from '@/components/commissions/CommissionRecipientsTab'
import { CommissionRulesTab } from '@/components/commissions/CommissionRulesTab'
import { Commission } from '@/types/commissions'

const tabs = [
    { name: 'Pendientes', icon: BanknotesIcon },
    { name: 'Historial', icon: ArchiveBoxIcon },
    { name: 'Destinatarios', icon: UsersIcon },
    { name: 'Reglas', icon: AdjustmentsHorizontalIcon }
]

const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

export default function CommissionsPage() {
    const { selectedCompany } = useHoldingContext()
    const { 
        summary, 
        isLoadingSummary, 
        commissionsQuery, 
        generateMutation,
        recipients,
        selectedMonth,
        setSelectedMonth,
        selectedYear,
        setSelectedYear
    } = useCommissions(selectedCompany?.id)

    const [selectedRecipientId, setSelectedRecipientId] = useState<string>('')
    const [isPayModalOpen, setIsPayModalOpen] = useState(false)
    const [selectedCommission, setSelectedCommission] = useState<Commission | null>(null)
    const [selectedIds, setSelectedIds] = useState<string[]>([])
    const [isBulkMode, setIsBulkMode] = useState(false)

    // Queries para las tablas
    const pendingQuery = commissionsQuery('pending', selectedRecipientId)
    const historyQuery = commissionsQuery('paid', selectedRecipientId)

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <BanknotesIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para gestionar comisiones, primero debés seleccionar una empresa del Holding.</p>
            </div>
        )
    }

    const prevMonth = () => {
        if (selectedMonth === 1) { setSelectedMonth(12); setSelectedYear(y => y - 1) }
        else setSelectedMonth(m => m - 1)
        setSelectedIds([])
    }
    const nextMonth = () => {
        if (selectedMonth === 12) { setSelectedMonth(1); setSelectedYear(y => y + 1) }
        else setSelectedMonth(m => m + 1)
        setSelectedIds([])
    }

    const handlePay = (commission: Commission) => {
        setSelectedCommission(commission)
        setIsBulkMode(false)
        setIsPayModalOpen(true)
    }

    const handleBulkPay = () => {
        setIsBulkMode(true)
        setIsPayModalOpen(true)
    }

    const toggleSelect = (id: string) => {
        setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id])
    }

    const toggleAll = (ids: string[]) => {
        if (selectedIds.length === ids.length) setSelectedIds([])
        else setSelectedIds(ids)
    }

    const selectedCommissions = (pendingQuery.data || []).filter((c: Commission) => selectedIds.includes(c.id))
    const bulkTotal = selectedCommissions.reduce((sum: number, c: Commission) => sum + (c.commission_amount ?? c.amount ?? 0), 0)

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            <CommissionPayModal
                isOpen={isPayModalOpen}
                onClose={() => {
                    setIsPayModalOpen(false)
                    setSelectedCommission(null)
                    setSelectedIds([])
                }}
                commission={isBulkMode ? null : selectedCommission}
                bulkCommissions={isBulkMode ? selectedCommissions : []}
                companyId={selectedCompany.id}
            />

            {/* ── Header ── */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight flex items-center gap-3">
                        <div className="p-2 bg-blue-600 rounded-xl shadow-lg shadow-blue-200">
                            <BanknotesIcon className="w-8 h-8 text-white" />
                        </div>
                        Gestión de Comisiones
                    </h1>
                    <p className="mt-2 text-sm text-gray-500">
                        Liquidación de comisiones acumuladas para <span className="font-semibold text-gray-900">{selectedCompany.name}</span>.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-4 bg-white p-2 rounded-2xl shadow-sm border border-gray-100">
                    {/* Period Selector */}
                    <div className="flex items-center gap-3 px-3 py-1 bg-gray-50 rounded-xl border border-gray-200">
                        <button onClick={prevMonth} className="p-1.5 hover:bg-white rounded-lg transition-all text-gray-500 hover:text-blue-600 shadow-sm border border-transparent hover:border-gray-100"><ChevronLeftIcon className="w-4 h-4" /></button>
                        <div className="text-center min-w-[120px]">
                            <span className="block text-[10px] uppercase tracking-widest text-gray-400 font-bold leading-none">Periodo</span>
                            <span className="text-sm font-extrabold text-gray-900">{MONTH_NAMES[selectedMonth - 1]} {selectedYear}</span>
                        </div>
                        <button onClick={nextMonth} className="p-1.5 hover:bg-white rounded-lg transition-all text-gray-500 hover:text-blue-600 shadow-sm border border-transparent hover:border-gray-100"><ChevronRightIcon className="w-4 h-4" /></button>
                    </div>

                    <div className="h-8 w-px bg-gray-200 mx-1 hidden sm:block"></div>

                    <button
                        onClick={() => generateMutation.mutate()}
                        disabled={generateMutation.isPending}
                        className="btn-secondary group flex items-center gap-2 border-none shadow-none hover:bg-blue-50"
                    >
                        <ArrowPathRoundedSquareIcon className={clsx("w-5 h-5 text-blue-600", generateMutation.isPending && "animate-spin")} />
                        <span className="text-gray-700 font-bold text-xs uppercase tracking-wider">{generateMutation.isPending ? 'Generando...' : 'Recalcular'}</span>
                    </button>
                    
                    {selectedIds.length > 0 && (
                        <button
                            onClick={handleBulkPay}
                            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-xl shadow-lg shadow-emerald-200 hover:bg-emerald-700 transition-all animate-scale-in"
                        >
                            <BanknotesIcon className="w-5 h-5" />
                            <div className="text-left leading-none">
                                <span className="block text-[9px] uppercase tracking-widest opacity-80 font-bold">Liquidar Selección ({selectedIds.length})</span>
                                <span className="text-sm font-extrabold">${bulkTotal.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                            </div>
                        </button>
                    )}
                </div>
            </div>

            {/* ── Dashboard Summary ── */}
            <CommissionsSummaryWidget summary={summary} isLoading={isLoadingSummary} />

            {/* ── Main Content Tabs ── */}
            <Tab.Group>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-200 gap-4">
                    <Tab.List className="flex gap-8 -mb-px">
                        {tabs.map((tab) => (
                            <Tab
                                key={tab.name}
                                className={({ selected }) =>
                                    clsx(
                                        'pb-4 text-sm font-semibold border-b-2 transition-all outline-none flex items-center gap-2',
                                        selected
                                            ? 'border-blue-600 text-blue-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    )
                                }
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.name}
                            </Tab>
                        ))}
                    </Tab.List>

                    {/* Quick Filter shared for Pending/History */}
                    <div className="pb-3 flex items-center gap-2">
                        <div className="relative">
                            <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <select
                                value={selectedRecipientId}
                                onChange={(e) => {
                                    setSelectedRecipientId(e.target.value)
                                    setSelectedIds([])
                                }}
                                className="pl-9 pr-8 py-1.5 text-xs font-medium bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all appearance-none cursor-pointer hover:bg-gray-50"
                            >
                                <option value="">Todos los destinatarios</option>
                                {recipients.map((r: any) => (
                                    <option key={r.id} value={r.id}>{r.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                <Tab.Panels className="mt-6">
                    {/* 1: Pendientes */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="glass-card overflow-hidden">
                            <CommissionsTable 
                                commissions={pendingQuery.data || []} 
                                isLoading={pendingQuery.isLoading} 
                                onPay={handlePay}
                                isHistory={false}
                                selectedIds={selectedIds}
                                onToggleSelect={toggleSelect}
                                onToggleAll={toggleAll}
                            />
                        </div>
                    </Tab.Panel>

                    {/* 2: Historial */}
                    <Tab.Panel className="focus:outline-none">
                        <div className="glass-card overflow-hidden">
                            <CommissionsTable 
                                commissions={historyQuery.data || []} 
                                isLoading={historyQuery.isLoading} 
                                isHistory={true}
                            />
                        </div>
                    </Tab.Panel>

                    {/* 3: Destinatarios */}
                    <Tab.Panel className="focus:outline-none">
                        <CommissionRecipientsTab companyId={selectedCompany.id} />
                    </Tab.Panel>

                    {/* 4: Reglas */}
                    <Tab.Panel className="focus:outline-none">
                        <CommissionRulesTab companyId={selectedCompany.id} />
                    </Tab.Panel>
                </Tab.Panels>
            </Tab.Group>
        </div>
    )
}
