'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { UserGroupIcon, PlusIcon, DocumentTextIcon, BanknotesIcon, CheckCircleIcon, TrashIcon, PencilSquareIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import { formatCurrency } from '@/utils/formatters'

export default function ComisionesPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState<'recipients' | 'rules' | 'commissions'>('recipients')
    const [showRecipientForm, setShowRecipientForm] = useState(false)
    const [showRuleForm, setShowRuleForm] = useState(false)

    // Form states - Recipient
    const [recName, setRecName] = useState('')
    const [recEmail, setRecEmail] = useState('')

    // Form states - Rule
    const [ruleRecipientId, setRuleRecipientId] = useState('')
    const [ruleClientId, setRuleClientId] = useState('')
    const [ruleServiceId, setRuleServiceId] = useState('')
    const [rulePercentage, setRulePercentage] = useState<number | ''>('')
    const [editingRec, setEditingRec] = useState<any>(null)
    const [editingRule, setEditingRule] = useState<any>(null)

    // Data Queries
    const { data: recipients, isLoading: loadingRecs } = useQuery({
        queryKey: ['commissionRecipients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.commissions.listRecipients(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany,
    })

    const { data: rules, isLoading: loadingRules } = useQuery({
        queryKey: ['commissionRules', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.commissions.listRules(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany && activeTab === 'rules',
    })

    const { data: commissions, isLoading: loadingComms } = useQuery({
        queryKey: ['commissions', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.commissions.list(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany && activeTab === 'commissions',
    })

    const { data: clients } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany && showRuleForm,
    })

    const { data: services } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return res.data
        },
        enabled: !!selectedCompany && showRuleForm,
    })

    // Mutations
    const createRecMutation = useMutation({
        mutationFn: (data: any) => api.commissions.createRecipient(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRecipients'] })
            setShowRecipientForm(false)
            setRecName('')
            setRecEmail('')
        }
    })

    const createRuleMutation = useMutation({
        mutationFn: (data: any) => api.commissions.createRule(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRules'] })
            setShowRuleForm(false)
            setRulePercentage('')
        }
    })

    const updateRecMutation = useMutation({
        mutationFn: ({ id, data }: any) => api.commissions.updateRecipient(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRecipients'] })
            setEditingRec(null)
        }
    })

    const deleteRecMutation = useMutation({
        mutationFn: (id: string) => api.commissions.deleteRecipient(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRecipients'] })
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
        }
    })

    const updateRuleMutation = useMutation({
        mutationFn: ({ id, data }: any) => api.commissions.updateRule(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRules'] })
            setEditingRule(null)
        }
    })

    const deleteRuleMutation = useMutation({
        mutationFn: (id: string) => api.commissions.deleteRule(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissionRules'] })
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
                <div className="flex gap-2">
                    {activeTab === 'recipients' && (
                        <button onClick={() => setShowRecipientForm(!showRecipientForm)} className="btn-primary">
                            <PlusIcon className="w-5 h-5" /> Nuevo Colaborador
                        </button>
                    )}
                    {activeTab === 'rules' && (
                        <button onClick={() => setShowRuleForm(!showRuleForm)} className="btn-primary">
                            <PlusIcon className="w-5 h-5" /> Nueva Regla
                        </button>
                    )}
                </div>
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
                            className="glass-card p-6 grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in border-indigo-100">
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
                                <button type="button" onClick={() => setShowRecipientForm(false)} className="px-4 py-2 text-sm text-gray-500 font-medium">Cancelar</button>
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
                            <div className="col-span-full py-20 text-center glass-card border-dashed border-2 border-gray-100">
                                <UserGroupIcon className="mx-auto h-12 w-12 text-gray-200" />
                                <p className="mt-2 text-sm text-gray-400 font-medium">No hay colaboradores registrados.</p>
                            </div>
                        ) : recipients?.map((rec: any) => (
                            <div key={rec.id} className="glass-card p-5 transition-all hover:ring-2 hover:ring-indigo-500/20 group relative">
                                <div className="absolute top-4 right-4 flex gap-1 opacity-10 group-hover:opacity-100 transition-opacity">
                                    <button onClick={() => { setEditingRec(rec); setRecName(rec.name); setRecEmail(rec.email || '') }} 
                                        className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                                        <PencilSquareIcon className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => { if(confirm('¿Eliminar colaborador y sus reglas?')) deleteRecMutation.mutate(rec.id) }} 
                                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                                        <TrashIcon className="w-4 h-4" />
                                    </button>
                                </div>

                                {editingRec?.id === rec.id ? (
                                    <form onSubmit={(e) => { e.preventDefault(); updateRecMutation.mutate({ id: rec.id, data: { name: recName, email: recEmail } }) }} className="space-y-3">
                                        <input type="text" value={recName} onChange={(e) => setRecName(e.target.value)}
                                            className="w-full px-2 py-1 text-sm border rounded outline-none focus:ring-1 focus:ring-indigo-500" />
                                        <input type="email" value={recEmail} onChange={(e) => setRecEmail(e.target.value)}
                                            className="w-full px-2 py-1 text-sm border rounded outline-none focus:ring-1 focus:ring-indigo-500" />
                                        <div className="flex justify-end gap-2">
                                            <button type="button" onClick={() => setEditingRec(null)} className="text-[10px] font-bold text-gray-400 uppercase">Cancelar</button>
                                            <button type="submit" className="text-[10px] font-bold text-indigo-600 uppercase">Guardar</button>
                                        </div>
                                    </form>
                                ) : (
                                    <>
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-lg group-hover:scale-110 transition-transform">
                                                {rec.name.charAt(0)}
                                            </div>
                                            <div className="overflow-hidden">
                                                <h3 className="font-bold text-gray-900 line-clamp-1">{rec.name}</h3>
                                                <p className="text-xs text-gray-500 line-clamp-1">{rec.email || 'Sin email'}</p>
                                            </div>
                                        </div>
                                        <div className="mt-4 flex gap-4 text-[10px] uppercase font-bold tracking-wider text-gray-400">
                                            <div className="flex items-center gap-1"><DocumentTextIcon className="w-3 h-3" /> {rec.rules?.length || 0} Reglas</div>
                                            <div className="flex items-center gap-1 text-emerald-600"><BanknotesIcon className="w-3 h-3" /> {formatCurrency(0)} Pagados</div>
                                        </div>
                                    </>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {activeTab === 'rules' && (
                <div className="space-y-6">
                    {showRuleForm && (
                        <form onSubmit={(e) => { e.preventDefault(); createRuleMutation.mutate({ recipient_id: ruleRecipientId, client_id: ruleClientId || null, service_id: ruleServiceId || null, percentage: Number(rulePercentage) }) }}
                            className="glass-card p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in border-indigo-100">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Colaborador</label>
                                <select value={ruleRecipientId} onChange={(e) => setRuleRecipientId(e.target.value)} required
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                                    <option value="">Seleccionar...</option>
                                    {recipients?.map((r: any) => <option key={r.id} value={r.id}>{r.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Cliente (Opcional)</label>
                                <select value={ruleClientId} onChange={(e) => setRuleClientId(e.target.value)}
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                                    <option value="">Todos los clientes</option>
                                    {clients?.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Servicio (Opcional)</label>
                                <select value={ruleServiceId} onChange={(e) => setRuleServiceId(e.target.value)}
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                                    <option value="">Todos los servicios</option>
                                    {services?.map((s: any) => <option key={s.id} value={s.id}>{s.name || s.nombre}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Comisión (%)</label>
                                <input type="number" value={rulePercentage} onChange={(e) => setRulePercentage(Number(e.target.value))} required
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                            </div>
                            <div className="lg:col-span-4 flex justify-end gap-3 pt-2">
                                <button type="button" onClick={() => setShowRuleForm(false)} className="px-4 py-2 text-sm text-gray-500 font-medium">Cancelar</button>
                                <button type="submit" disabled={createRuleMutation.isPending} className="btn-primary">
                                    {createRuleMutation.isPending ? 'Guardando...' : 'Crear Regla'}
                                </button>
                            </div>
                        </form>
                    )}

                    <div className="overflow-hidden glass-card">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Colaborador</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Aplica a</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Porcentaje</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Creado</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px] text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {loadingRules ? (
                                    Array(3).fill(0).map((_, i) => <tr key={i} className="animate-pulse h-16 bg-white" />)
                                ) : rules?.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-10 text-center text-gray-400 text-sm italic">No hay reglas configuradas.</td>
                                    </tr>
                                ) : rules?.map((rule: any) => (
                                    <tr key={rule.id} className="hover:bg-gray-50/50 transition-colors">
                                        {editingRule?.id === rule.id ? (
                                            <>
                                                <td className="px-6 py-4 font-bold text-gray-900">{rule.recipient_name || rule.recipient_id}</td>
                                                <td className="px-6 py-4">
                                                    <div className="flex flex-col gap-1">
                                                        <select value={ruleClientId} onChange={(e) => setRuleClientId(e.target.value)}
                                                            className="text-xs border rounded p-1 outline-none">
                                                            <option value="">Todos los clientes</option>
                                                            {clients?.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
                                                        </select>
                                                        <select value={ruleServiceId} onChange={(e) => setRuleServiceId(e.target.value)}
                                                            className="text-xs border rounded p-1 outline-none">
                                                            <option value="">Todos los servicios</option>
                                                            {services?.map((s: any) => <option key={s.id} value={s.id}>{s.name || s.nombre}</option>)}
                                                        </select>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <input type="number" value={rulePercentage} onChange={(e) => setRulePercentage(Number(e.target.value))}
                                                        className="w-16 text-xs border rounded p-1 outline-none" />
                                                </td>
                                                <td colSpan={2} className="px-6 py-4 text-right">
                                                    <div className="flex justify-end gap-2">
                                                        <button onClick={() => setEditingRule(null)} className="text-[10px] font-bold text-gray-400 uppercase">Cancel</button>
                                                        <button onClick={() => updateRuleMutation.mutate({ id: rule.id, data: { client_id: ruleClientId || null, service_id: ruleServiceId || null, percentage: Number(rulePercentage) } })} 
                                                            className="text-[10px] font-bold text-indigo-600 uppercase">Save</button>
                                                    </div>
                                                </td>
                                            </>
                                        ) : (
                                            <>
                                                <td className="px-6 py-4 font-bold text-gray-900">{rule.recipient_name || rule.recipient_id}</td>
                                                <td className="px-6 py-4">
                                                    <div className="text-xs font-semibold text-gray-500">
                                                        {rule.client_name ? (
                                                            <span className="flex items-center gap-1">Cliente: <span className="text-emerald-600">{rule.client_name}</span></span>
                                                        ) : null}
                                                        {rule.client_name && rule.service_name ? <span className="mx-1">+</span> : null}
                                                        {rule.service_name ? (
                                                            <span className="flex items-center gap-1">Servicio: <span className="text-indigo-600">{rule.service_name}</span></span>
                                                        ) : null}
                                                        {!rule.client_name && !rule.service_name ? (
                                                            <span className="text-gray-400 italic">Todas las ventas</span>
                                                        ) : null}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 font-black text-indigo-600 text-sm">{rule.percentage}%</td>
                                                <td className="px-6 py-4 text-xs text-gray-400 font-medium">{new Date(rule.created_at).toLocaleDateString()}</td>
                                                <td className="px-6 py-4 text-right">
                                                    <div className="flex justify-end gap-1 opacity-20 hover:opacity-100 transition-opacity">
                                                        <button onClick={() => { setEditingRule(rule); setRulePercentage(rule.percentage); setRuleClientId(rule.client_id || ''); setRuleServiceId(rule.service_id || '') }}
                                                            className="p-1 hover:text-indigo-600 transition-colors"><PencilSquareIcon className="w-4 h-4" /></button>
                                                        <button onClick={() => { if(confirm('¿Eliminar regla?')) deleteRuleMutation.mutate(rule.id) }} 
                                                            className="p-1 hover:text-red-600 transition-colors"><TrashIcon className="w-4 h-4" /></button>
                                                    </div>
                                                </td>
                                            </>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {activeTab === 'commissions' && (
                <div className="space-y-6">
                    <div className="overflow-hidden glass-card">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Fecha</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Colaborador</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Detalle Venta</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Monto</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-[10px]">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {loadingComms ? (
                                    Array(5).fill(0).map((_, i) => <tr key={i} className="animate-pulse h-16 bg-white" />)
                                ) : commissions?.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-10 text-center text-gray-400 text-sm italic">No hay liquidaciones generadas.</td>
                                    </tr>
                                ) : commissions?.map((comm: any) => (
                                    <tr key={comm.id} className="hover:bg-gray-50/50 transition-colors">
                                        <td className="px-6 py-4 text-sm text-gray-500">{new Date(comm.transaction_date || comm.created_at).toLocaleDateString()}</td>
                                        <td className="px-6 py-4">
                                            <div className="font-bold text-gray-900">{comm.recipient_name || comm.recipient_id}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-xs text-gray-500 font-medium">
                                                {comm.client_name ? <span className="block text-emerald-600 font-bold">{comm.client_name}</span> : null}
                                                {comm.service_name ? <span className="block text-indigo-600">{comm.service_name}</span> : null}
                                                {!comm.client_name && !comm.service_name && <span className="text-gray-300 italic">Sin detalle</span>}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 font-black text-gray-900">{formatCurrency(comm.amount)}</td>
                                        <td className="px-6 py-4">
                                            <span className={clsx("badge text-[10px]", 
                                                comm.status === 'PAID' ? "badge-success" : "badge-warning")}>
                                                {comm.status === 'PAID' ? 'PAGADO' : 'PENDIENTE'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}

