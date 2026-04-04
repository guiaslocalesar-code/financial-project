'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlusIcon, UsersIcon } from '@heroicons/react/24/outline'
import { Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import Link from 'next/link'
import { api } from '@/services/api'
import type { Client } from '@/types'
import { ClientFormModal } from '@/components/clients/ClientFormModal'
import { useHoldingContext } from '@/context/HoldingContext'
import { Switch } from '@headlessui/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/20/solid'

export default function ClientesPage() {
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingClient, setEditingClient] = useState<Client | null>(null)
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [showInactive, setShowInactive] = useState(false)
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

    const { data, isLoading, error } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || res.data.clients || []) as Client[]
        },
        enabled: !!selectedCompany,
    })

    const activeCount = data?.filter(c => c.is_active).length || 0
    const inactiveCount = data?.filter(c => !c.is_active).length || 0
    const filteredClients = data?.filter(c => showInactive ? !c.is_active : c.is_active) ?? []

    const handleCreate = () => {
        setEditingClient(null)
        setIsModalOpen(true)
    }

    const handleEdit = (client: Client) => {
        setEditingClient(client)
        setIsModalOpen(true)
    }

    const mutation = useMutation({
        mutationFn: ({ id, is_active, cuit_cuil_dni }: { id: string; is_active: boolean; cuit_cuil_dni: string }) => 
            api.clients.update(id, { is_active, cuit_cuil_dni }),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['clients', selectedCompany?.id] })
            setToast({
                message: `Cliente ${variables.is_active ? 'activado' : 'desactivado'} correctamente.`,
                type: 'success'
            })
            setTimeout(() => setToast(null), 3000)
        }
    })

    const toggleStatus = (client: Client) => {
        mutation.mutate({ 
            id: client.id, 
            is_active: !client.is_active,
            cuit_cuil_dni: String(client.cuit_cuil_dni).replace('.0', '')
        })
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <UsersIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los clientes, primero debés seleccionar una empresa del Holding operando en el selector superior.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <UsersIcon className="w-7 h-7 text-blue-600" />
                        Clientes
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Directorio de clientes de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <button
                    onClick={handleCreate}
                    className="btn-primary"
                >
                    <PlusIcon className="w-5 h-5" />
                    Nuevo Cliente
                </button>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center gap-1 bg-gray-100/80 p-1 rounded-xl self-start backdrop-blur-sm border border-gray-200">
                <button
                    onClick={() => setShowInactive(false)}
                    className={clsx(
                        'px-4 py-2 text-sm font-semibold rounded-lg transition-all',
                        !showInactive 
                            ? 'bg-white text-blue-600 shadow-sm' 
                            : 'text-gray-500 hover:text-gray-700'
                    )}
                >
                    Activos <span className="ml-1 opacity-60 font-normal">({activeCount})</span>
                </button>
                <button
                    onClick={() => setShowInactive(true)}
                    className={clsx(
                        'px-4 py-2 text-sm font-semibold rounded-lg transition-all',
                        showInactive 
                            ? 'bg-white text-blue-600 shadow-sm' 
                            : 'text-gray-500 hover:text-gray-700'
                    )}
                >
                    Inactivos <span className="ml-1 opacity-60 font-normal">({inactiveCount})</span>
                </button>
            </div>

            {/* List */}
            <div className="glass-card overflow-hidden">
                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                        Error al cargar los clientes.
                    </div>
                ) : !data || data.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <UsersIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">Aún no hay clientes</h3>
                        <p className="mt-1 text-sm text-gray-500">Este negocio todavía no tiene clientes registrados.</p>
                        <div className="mt-6">
                            <button onClick={handleCreate} className="btn-primary">
                                <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                Nuevo Cliente
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Cliente</th>
                                    <th>Identificación</th>
                                    <th>Condición Fiscal</th>
                                    <th>Contacto</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredClients.map((client) => (
                                    <tr 
                                        key={client.id} 
                                        onClick={() => handleEdit(client)}
                                        className={clsx(
                                            "cursor-pointer hover:bg-gray-50/80 transition-all duration-200 group border-b border-gray-100 last:border-0",
                                            !client.is_active && 'bg-gray-50/50 opacity-50'
                                        )}
                                    >
                                        <td>
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl border-2 border-white shadow-sm overflow-hidden bg-white shrink-0">
                                                    {client.imagen ? (
                                                        <img src={client.imagen} alt={client.name} className="w-full h-full object-cover" />
                                                    ) : (
                                                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-xs font-bold">
                                                            {client.name.substring(0, 2).toUpperCase()}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className={clsx(
                                                    "font-bold transition-colors group-hover:text-blue-600",
                                                    client.is_active ? "text-gray-900" : "text-gray-400 italic"
                                                )}>
                                                    {client.name}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="text-sm text-gray-600 font-mono">{String(client.cuit_cuil_dni).replace('.0', '')}</td>
                                        <td className="text-sm text-gray-600">
                                            {client.fiscal_condition === 'CONSUMIDOR_FINAL' ? 'Consumidor Final' : 
                                             client.fiscal_condition === 'RI' ? 'Responsable Inscripto' : 
                                             client.fiscal_condition === 'MONOTRIBUTO' ? 'Monotributo' : client.fiscal_condition}
                                        </td>
                                        <td>
                                            <div className="text-sm text-gray-900">{client.email || '—'}</div>
                                            <div className="text-xs text-gray-500">{client.phone || ''}</div>
                                        </td>
                                        <td>
                                            <div className="flex items-center gap-3">
                                                <Switch
                                                    checked={client.is_active}
                                                    onChange={(e: any) => {
                                                        // Prevent row click when toggling switch
                                                        if (typeof e === 'boolean' || e?.stopPropagation) {
                                                            if (e?.stopPropagation) e.stopPropagation();
                                                            toggleStatus(client);
                                                        }
                                                    }}
                                                    onClick={(e) => e.stopPropagation()}
                                                    className={clsx(
                                                        client.is_active ? 'bg-blue-600' : 'bg-gray-200',
                                                        'relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2'
                                                    )}
                                                >
                                                    <span
                                                        aria-hidden="true"
                                                        className={clsx(
                                                            client.is_active ? 'translate-x-4' : 'translate-x-0',
                                                            'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                                                        )}
                                                    />
                                                </Switch>
                                                <span className={clsx(
                                                    'text-xs font-semibold',
                                                    client.is_active ? 'text-emerald-700' : 'text-gray-500'
                                                )}>
                                                    {client.is_active ? 'Activo' : 'Inactivo'}
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <ClientFormModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                client={editingClient}
            />

            {/* Simple Toast */}
            <Transition
                show={!!toast}
                as={Fragment}
                enter="transform ease-out duration-300 transition"
                enterFrom="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
                enterTo="translate-y-0 opacity-100 sm:translate-x-0"
                leave="transition ease-in duration-100"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
            >
                <div className="pointer-events-none fixed inset-0 z-[100] flex items-end px-4 py-6 sm:items-start sm:p-6">
                    <div className="flex w-full flex-col items-center space-y-4 sm:items-end">
                        <div className="pointer-events-auto w-full max-w-sm overflow-hidden rounded-xl bg-white shadow-2xl ring-1 ring-black ring-opacity-5">
                            <div className="p-4">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        {toast?.type === 'success' ? (
                                            <CheckCircleIcon className="h-6 w-6 text-emerald-500" />
                                        ) : (
                                            <XCircleIcon className="h-6 w-6 text-rose-500" />
                                        )}
                                    </div>
                                    <div className="ml-3 w-0 flex-1 pt-0.5">
                                        <p className="text-sm font-bold text-gray-900">{toast?.message}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Transition>
        </div>
    )
}
