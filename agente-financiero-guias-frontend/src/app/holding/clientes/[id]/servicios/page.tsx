'use client'

import { useQuery } from '@tanstack/react-query'
import { LinkIcon, ArrowLeftIcon, WrenchScrewdriverIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { ClientService, Client } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function ClientServiciosPage() {
    const params = useParams()
    const clientId = params.id as string
    const { selectedCompany } = useHoldingContext()

    const { data: client } = useQuery({
        queryKey: ['client', clientId],
        queryFn: async () => {
            const res = await api.clients.get(clientId)
            return res.data as Client
        },
        enabled: !!clientId,
    })

    const { data: services, isLoading, error } = useQuery({
        queryKey: ['clientServices', clientId],
        queryFn: async () => {
            const res = await api.clientServices.list(clientId)
            const list = (Array.isArray(res.data) ? res.data : res.data.data || []) as ClientService[]
            return list
        },
        enabled: !!clientId && !!client && !!selectedCompany,
    })

    const statusLabel = (s: string) => {
        const map: Record<string, string> = { ACTIVE: 'Activo', PAUSED: 'Pausado', CANCELLED: 'Cancelado' }
        return map[s?.toUpperCase()] || s
    }

    const statusBadge = (s: string) => {
        switch (s?.toUpperCase()) {
            case 'ACTIVE': return 'badge-success'
            case 'PAUSED': return 'badge-warning'
            case 'CANCELLED': return 'badge-neutral'
            default: return 'badge-neutral'
        }
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-500">
                <Link href="/holding/clientes" className="hover:text-blue-600 transition-colors flex items-center gap-1">
                    <ArrowLeftIcon className="w-4 h-4" />
                    Clientes
                </Link>
                <span>/</span>
                <span className="text-gray-900 font-medium">{client?.name || 'Cliente'}</span>
                <span>/</span>
                <span className="text-gray-900 font-medium">Servicios</span>
            </div>

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <LinkIcon className="w-7 h-7 text-teal-600" />
                        Servicios de {client?.name || '...'}
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Contratos y fees mensuales asignados a este cliente.
                    </p>
                </div>
            </div>

            {/* Table */}
            <div className="glass-card overflow-hidden">
                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                        Error al cargar los servicios del cliente.
                    </div>
                ) : !services || services.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <WrenchScrewdriverIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">Sin servicios asignados</h3>
                        <p className="mt-1 text-sm text-gray-500">Este cliente aún no tiene servicios contratados.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Servicio</th>
                                    <th>Fee Mensual</th>
                                    <th>Moneda</th>
                                    <th>Inicio</th>
                                    <th>Fin</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {services.map((cs) => (
                                    <tr key={cs.id}>
                                        <td className="font-medium text-gray-900">{cs.service?.name || '—'}</td>
                                        <td className="font-semibold text-teal-700">
                                            ${cs.monthly_fee?.toLocaleString('es-AR')}
                                        </td>
                                        <td className="text-sm text-gray-500">{cs.currency || 'ARS'}</td>
                                        <td className="text-sm text-gray-600">
                                            {cs.start_date ? format(new Date(cs.start_date), "dd/MM/yyyy") : '—'}
                                        </td>
                                        <td className="text-sm text-gray-600">
                                            {cs.end_date ? format(new Date(cs.end_date), "dd/MM/yyyy") : 'Vigente'}
                                        </td>
                                        <td>
                                            <span className={clsx(statusBadge(cs.status), 'text-[10px]')}>
                                                {statusLabel(cs.status)}
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
