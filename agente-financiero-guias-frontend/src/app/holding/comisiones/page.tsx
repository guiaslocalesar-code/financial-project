'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { UserGroupIcon, PlusIcon, DocumentTextIcon, BanknotesIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import { formatCurrency } from '@/utils/formatters'

export default function ComisionesPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState<'recipients' | 'rules' | 'commissions'>('recipients')
    const [showRecipientForm, setShowRecipientForm] = useState(false)

    // Form states
    const [recName, setRecName] = useState('')
    const [recEmail, setRecEmail] = useState('')

    const { data: recipients, isLoading: loadingRecs } = useQuery({
        queryKey: ['commissionRecipients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.commissions.listRecipients(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || [])
        },
        enabled: !!selectedCompany,
    })

    const createRecMutation = useMutation({
        mutationFn: (data: any) => api.commissions.createRecipient(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRecipients'] })
            setShowRecipientForm(false)
            setRecName('')
            setRecEmail('')
        }
    })

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <UserGroupIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para gestionar comisiones, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <BanknotesIcon className="w-7 h-7 text-indigo-600" />
                        Comisiones y Referidores
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Gestioná colaboradores externos y reglas de comisión por ventas.
                    </p>
                </div>
                {activeTab === 'recipients' && (
                    <button onClick={() => setShowRecipientForm(!showRecipientForm)} className="btn-primary">
                        <PlusIcon className="w-5 h-5" /> Nuevo Colaborador
                    </button>
                )}
            </div>

            <nav className="flex space-x-4 border-b border-gray-100 pb-px">
                {['recipients', 'rules', 'commissions'].map((tab) => (
                    <button key={tab} 
                        onClick={() => setActiveTab(tab as any)}
                        className={clsx("px-4 py-2 text-sm font-bold transition-all border-b-2",
                        activeTab === tab ? "border-indigo-600 text-indigo-600" : "border-transparent text-gray-400 hover:text-gray-600")}>
                        {tab === 'recipients' ? 'Colaboradores' : tab === 'rules' ? 'Reglas' : 'Liquidaciones'}
                    </button>
                ))}
            </nav>

            {activeTab === 'recipients' && (
                <div className="space-y-6">
                    {showRecipientForm && (
                        <form onSubmit={(e) => { e.preventDefault(); createRecMutation.mutate({ company_id: selectedCompany.id, name: recName, email: recEmail }) }}
                            className="glass-card p-6 grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                                <input type="text" value={recName} onChange={(e) => setRecName(e.target.value)} required
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" value={recEmail} onChange={(e) => setRecEmail(e.target.value)}
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                            </div>
                            <div className="col-span-full flex justify-end gap-3 pt-2">
                                <button type="button" onClick={() => setShowRecipientForm(false)} className="px-4 py-2 text-sm text-gray-500">Cancelar</button>
                                <button type="submit" disabled={createRecMutation.isPending} className="btn-primary">
                                    {createRecMutation.isPending ? 'Guardando...' : 'Crear Colaborador'}
                                </button>
                            </div>
                        </form>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {loadingRecs ? (
                            Array(3).fill(0).map((_, i) => <div key={i} className="glass-card h-32 animate-pulse" />)
                        ) : recipients?.length === 0 ? (
                            <div className="col-span-full py-20 text-center glass-card">
                                <UserGroupIcon className="mx-auto h-12 w-12 text-gray-300" />
                                <p className="mt-2 text-sm text-gray-500">No hay colaboradores registrados.</p>
                            </div>
                        ) : recipients?.map((rec: any) => (
                            <div key={rec.id} className="glass-card p-5 transition-all hover:ring-2 hover:ring-indigo-500/20">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-lg">
                                        {rec.name.charAt(0)}
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-gray-900 line-clamp-1">{rec.name}</h3>
                                        <p className="text-xs text-gray-500 line-clamp-1">{rec.email || 'Sin email'}</p>
                                    </div>
                                </div>
                                <div className="mt-4 flex gap-4 text-[10px] uppercase font-bold tracking-wider text-gray-400">
                                    <div className="flex items-center gap-1"><DocumentTextIcon className="w-3 h-3" /> {rec.rules?.length || 0} Reglas</div>
                                    <div className="flex items-center gap-1 text-emerald-600"><BanknotesIcon className="w-3 h-3" /> {formatCurrency(0)} Pagados</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {activeTab === 'rules' && (
                <div className="glass-card p-20 text-center">
                    <BanknotesIcon className="mx-auto h-12 w-12 text-gray-300" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">Gestión de Reglas</h3>
                    <p className="mt-1 text-sm text-gray-500">Configurá incentivos porcentuales por cliente o servicio.</p>
                    <div className="mt-6">
                        <button className="btn-primary">Próximamente</button>
                    </div>
                </div>
            )}

            {activeTab === 'commissions' && (
                <div className="glass-card p-20 text-center">
                    <CheckCircleIcon className="mx-auto h-12 w-12 text-gray-300" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">Liquidaciones</h3>
                    <p className="mt-1 text-sm text-gray-500">Aquí podrás ver las transacciones generadas por comisiones.</p>
                </div>
            )}
        </div>
    )
}
