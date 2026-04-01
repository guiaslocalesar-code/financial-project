'use client'

import { 
    BanknotesIcon, 
    CheckBadgeIcon, 
    ClockIcon, 
    UserGroupIcon 
} from '@heroicons/react/24/outline'
import { CommissionDashboardSummary } from '@/types/commissions'
import { clsx } from 'clsx'

interface Props {
    summary: CommissionDashboardSummary | null | undefined
    isLoading: boolean
}

export function CommissionsSummaryWidget({ summary, isLoading }: Props) {
    const stats = [
        {
            name: 'Total Pendiente',
            value: summary?.total_pending != null 
                ? `$${summary.total_pending.toLocaleString('es-AR')}` 
                : (summary?.total_pendiente != null ? `$${summary.total_pendiente.toLocaleString('es-AR')}` : '$0'),
            icon: ClockIcon,
            color: 'text-amber-600',
            bgColor: 'bg-amber-50',
            borderColor: 'border-amber-100',
            gradient: 'from-amber-50 to-white'
        },
        {
            name: 'Total Pagado',
            value: summary?.total_paid != null 
                ? `$${summary.total_paid.toLocaleString('es-AR')}` 
                : (summary?.total_pagado != null ? `$${summary.total_pagado.toLocaleString('es-AR')}` : '$0'),
            icon: CheckBadgeIcon,
            color: 'text-emerald-600',
            bgColor: 'bg-emerald-50',
            borderColor: 'border-emerald-100',
            gradient: 'from-emerald-50 to-white'
        },
        {
            name: 'Cobradores Activos',
            value: summary?.recipient_count ?? summary?.top_recipients?.length ?? 0,
            icon: UserGroupIcon,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-100',
            gradient: 'from-blue-50 to-white'
        }
    ]

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.map((stat) => (
                <div 
                    key={stat.name}
                    className={clsx(
                        "relative overflow-hidden glass-card p-6 border transition-all duration-300 hover:shadow-lg group",
                        stat.borderColor
                    )}
                >
                    {/* Background Gradient */}
                    <div className={clsx("absolute inset-0 bg-gradient-to-br opacity-40 -z-10", stat.gradient)} />
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500 mb-1">{stat.name}</p>
                            {isLoading ? (
                                <div className="h-8 w-24 bg-gray-200 animate-pulse rounded-lg" />
                            ) : (
                                <h3 className="text-2xl font-bold text-gray-900 tracking-tight">
                                    {stat.value}
                                </h3>
                            )}
                        </div>
                        <div className={clsx(
                            "p-3 rounded-2xl transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-sm",
                            stat.bgColor,
                            stat.color
                        )}>
                            <stat.icon className="w-6 h-6" />
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
