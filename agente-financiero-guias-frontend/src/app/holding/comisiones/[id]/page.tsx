'use client'

import { useParams, useRouter } from 'next/navigation'
import { 
    ArrowLeftIcon, 
    UserIcon, 
    EnvelopeIcon, 
    IdentificationIcon,
    BriefcaseIcon,
    CurrencyDollarIcon,
    ChartPieIcon,
    CheckBadgeIcon,
    ClockIcon
} from '@heroicons/react/24/outline'
import { useRecipientSummary, useCommissions } from '@/hooks/useCommissions'
import { useHoldingContext } from '@/context/HoldingContext'
import { CommissionsTable } from '@/components/commissions/CommissionsTable'
import { clsx } from 'clsx'

export default function RecipientDetailPage() {
    const params = useParams()
    const router = useRouter()
    const { selectedCompany } = useHoldingContext()
    const recipientId = params.id as string

    const { data: summary, isLoading: isLoadingSummary } = useRecipientSummary(recipientId)
    const { commissionsQuery } = useCommissions(selectedCompany?.id)
    
    // Obtenemos todas las comisiones de este destinatario (mezcla de pendientes y pagadas)
    const { data: commissions = [], isLoading: isLoadingComms } = commissionsQuery(undefined, recipientId)

    if (isLoadingSummary) {
        return (
            <div className="p-12 flex justify-center items-center min-h-[400px]">
                <div className="w-10 h-10 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin" />
            </div>
        )
    }

    if (!summary) {
        return (
            <div className="p-12 text-center">
                <p className="text-gray-500">No se encontró información del destinatario.</p>
                <button onClick={() => router.back()} className="mt-4 btn-secondary">Volver</button>
            </div>
        )
    }

    const stats = [
        {
            label: 'Total Acumulado',
            value: `$${(summary.stats?.total_earned || 0).toLocaleString('es-AR')}`,
            icon: CurrencyDollarIcon,
            color: 'text-blue-600',
            bg: 'bg-blue-50'
        },
        {
            label: 'Pendiente de Pago',
            value: `$${(summary.stats?.total_pending || 0).toLocaleString('es-AR')}`,
            icon: ClockIcon,
            color: 'text-amber-600',
            bg: 'bg-amber-50'
        },
        {
            label: 'Cumplimiento',
            value: `${(summary.stats?.performance_pct || 0).toFixed(1)}%`,
            icon: ChartPieIcon,
            color: 'text-emerald-600',
            bg: 'bg-emerald-50'
        }
    ]

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in-up">
            {/* ── Breadcrumbs & Action ── */}
            <div className="flex items-center gap-4">
                <button 
                    onClick={() => router.back()}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors group"
                >
                    <ArrowLeftIcon className="w-5 h-5 text-gray-500 group-hover:text-gray-900" />
                </button>
                <div className="flex items-center gap-2 text-sm text-gray-400 font-medium">
                    <span>Comisiones</span>
                    <span>/</span>
                    <span className="text-gray-900">Perfil de Destinatario</span>
                </div>
            </div>

            {/* ── Profile Header ── */}
            <div className="glass-card p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full -mr-32 -mt-32 opacity-50 -z-10" />
                
                <div className="flex flex-col md:flex-row gap-8 items-start">
                    <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-xl shadow-blue-100 flex-shrink-0">
                        <UserIcon className="w-12 h-12" />
                    </div>
                    
                    <div className="flex-1 space-y-4">
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-3xl font-black text-gray-900">{summary.name}</h1>
                                <span className={clsx(
                                    "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border",
                                    summary.type === 'partner' ? "bg-purple-50 text-purple-700 border-purple-100" :
                                    summary.type === 'employee' ? "bg-blue-50 text-blue-700 border-blue-100" :
                                    "bg-gray-50 text-gray-700 border-gray-100"
                                )}>
                                    {summary.type === 'partner' ? 'Socio' : summary.type === 'employee' ? 'Empleado' : 'Proveedor'}
                                </span>
                            </div>
                            <div className="mt-3 flex flex-wrap gap-6 text-sm font-medium text-gray-500">
                                <div className="flex items-center gap-2">
                                    <IdentificationIcon className="w-4 h-4" />
                                    {summary.cuit}
                                </div>
                                <div className="flex items-center gap-2">
                                    <EnvelopeIcon className="w-4 h-4" />
                                    {summary.email}
                                </div>
                                <div className="flex items-center gap-2">
                                    <BriefcaseIcon className="w-4 h-4" />
                                    {selectedCompany?.name}
                                </div>
                            </div>
                        </div>

                        {/* Quick Stats Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                            {stats.map((stat) => (
                                <div key={stat.label} className="flex items-center gap-4">
                                    <div className={clsx("p-2 rounded-xl shadow-sm", stat.bg, stat.color)}>
                                        <stat.icon className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider leading-tight">{stat.label}</p>
                                        <p className="text-lg font-black text-gray-900 leading-tight">{stat.value}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Commissions History ── */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <CheckBadgeIcon className="w-6 h-6 text-emerald-600" />
                        Historial de Liquidaciones
                    </h2>
                    <div className="text-sm font-medium text-gray-400">
                        Mostrando {commissions.length} registros
                    </div>
                </div>

                <div className="glass-card overflow-hidden">
                    <CommissionsTable 
                        commissions={commissions} 
                        isLoading={isLoadingComms}
                        isHistory={false} // Permitimos pagar desde aquí si están pendientes, o solo ver si están pagadas
                    />
                </div>
            </div>
        </div>
    )
}
