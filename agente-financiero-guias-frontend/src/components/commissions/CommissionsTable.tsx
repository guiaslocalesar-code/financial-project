'use client'

import { 
    ClockIcon, 
    CheckCircleIcon, 
    BanknotesIcon,
    ArrowRightIcon,
    PencilSquareIcon
} from '@heroicons/react/24/outline'
import { Commission } from '@/types/commissions'
import { clsx } from 'clsx'

interface Props {
    commissions: Commission[]
    isLoading: boolean
    onPay?: (commission: Commission) => void
    isHistory?: boolean
}

export function CommissionsTable({ commissions, isLoading, onPay, isHistory }: Props) {
    if (isLoading) {
        return (
            <div className="p-12 flex justify-center">
                <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
            </div>
        )
    }

    if (commissions.length === 0) {
        return (
            <div className="text-center py-20 px-4">
                <div className={clsx(
                    "mx-auto h-16 w-16 rounded-2xl flex items-center justify-center mb-4 shadow-sm border border-gray-100",
                    isHistory ? "bg-gray-50 text-gray-300" : "bg-blue-50 text-blue-300"
                )}>
                    {isHistory ? <ClockIcon className="w-8 h-8" /> : <BanknotesIcon className="w-8 h-8" />}
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                    {isHistory ? 'Sin historial' : 'Sin comisiones pendientes'}
                </h3>
                <p className="mt-1 text-sm text-gray-500 max-w-xs mx-auto">
                    {isHistory 
                        ? 'Todavía no se han registrado liquidaciones completadas.' 
                        : 'No hay liquidaciones pendientes para cobrar en este momento.'}
                </p>
            </div>
        )
    }

    return (
        <div className="overflow-x-auto">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Beneficiario</th>
                        <th>Contexto (Cliente / Servicio)</th>
                        <th className="text-right">Base Imponible</th>
                        <th className="text-right">%</th>
                        <th className="text-right">Comisión</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                        <th className="text-right pr-6">Acción</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {commissions.map((comm) => {
                        // Backend returns 'amount' for commission_amount, base_amount may not exist
                        const commissionAmount = comm.commission_amount ?? comm.amount ?? 0
                        const baseAmount = comm.base_amount ?? 0
                        const percentage = baseAmount > 0 
                            ? (commissionAmount / baseAmount) * 100 
                            : 0;
                        const displayDate = comm.transaction_date || comm.created_at

                        return (
                            <tr key={comm.id} className="hover:bg-gray-50/50 transition-colors group">
                                <td className="py-4">
                                    <div className="flex flex-col">
                                        <span className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
                                            {comm.recipient_name || '—'}
                                        </span>
                                        <span className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">ID: {comm.id.slice(0, 8)}</span>
                                    </div>
                                </td>
                                <td>
                                    <div className="flex flex-col text-sm">
                                        <span className="text-gray-700 font-medium">{comm.client_name || comm.transaction_description || '—'}</span>
                                        <span className="text-gray-400 text-xs italic">{comm.service_name || ''}</span>
                                    </div>
                                </td>
                                <td className="text-right font-mono text-gray-600">
                                    ${baseAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
                                </td>
                                <td className="text-right font-medium text-blue-600">
                                    {percentage.toFixed(1)}%
                                </td>
                                <td className="text-right font-bold text-gray-900 whitespace-nowrap">
                                    ${commissionAmount.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
                                </td>
                                <td>
                                    <div className="flex flex-col text-xs text-gray-500">
                                        <span>{displayDate ? new Date(displayDate).toLocaleDateString('es-AR') : '—'}</span>
                                        {comm.payment_date && (
                                            <span className="text-emerald-600 font-medium">Pago: {new Date(comm.payment_date).toLocaleDateString('es-AR')}</span>
                                        )}
                                    </div>
                                </td>
                                <td>
                                    <span className={clsx(
                                        "badge inline-flex items-center gap-1.5",
                                        comm.status?.toUpperCase() === 'PENDING' ? "badge-warning" : "badge-success"
                                    )}>
                                        {comm.status?.toUpperCase() === 'PENDING' ? (
                                            <ClockIcon className="w-3 h-3" />
                                        ) : (
                                            <CheckCircleIcon className="w-3 h-3" />
                                        )}
                                        {comm.status?.toUpperCase() === 'PENDING' ? 'Pendiente' : 'Pagada'}
                                    </span>
                                </td>
                                <td className="text-right pr-6">
                                    {!isHistory && onPay && comm.status?.toUpperCase() === 'PENDING' && (
                                        <button
                                            onClick={() => onPay(comm)}
                                            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-all shadow-sm active:scale-95"
                                        >
                                            Pagar Comisión
                                            <ArrowRightIcon className="w-3 h-3" />
                                        </button>
                                    )}
                                    {isHistory && (
                                        <span className="text-xs text-gray-400 italic">Liquidada</span>
                                    )}
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </div>
    )
}
