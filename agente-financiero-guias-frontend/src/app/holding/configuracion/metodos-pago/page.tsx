'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PlusIcon, BuildingLibraryIcon, CreditCardIcon, BanknotesIcon, AdjustmentsHorizontalIcon, TrashIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'

export default function MetodosPagoPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [showForm, setShowForm] = useState(false)

    // Form state
    const [name, setName] = useState('')
    const [type, setType] = useState('BANK')
    const [bank, setBank] = useState('')
    const [isCredit, setIsCredit] = useState(false)
    const [closingDay, setClosingDay] = useState<number | ''>('')
    const [dueDay, setDueDay] = useState<number | ''>('')

    const { data: methods, isLoading } = useQuery({
        queryKey: ['paymentMethods', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.paymentMethods.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || [])
        },
        enabled: !!selectedCompany,
    })

    const createMutation = useMutation({
        mutationFn: (data: any) => api.paymentMethods.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['paymentMethods'] })
            setShowForm(false)
            resetForm()
        }
    })

    const deleteMutation = useMutation({
        mutationFn: (id: string) => api.paymentMethods.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['paymentMethods'] })
        }
    })

    const resetForm = () => {
        setName('')
        setType('BANK')
        setBank('')
        setIsCredit(false)
        setClosingDay('')
        setDueDay('')
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany) return
        createMutation.mutate({
            company_id: selectedCompany.id,
            name,
            type,
            bank: type === 'BANK' ? bank : null,
            is_credit: isCredit,
            closing_day: isCredit ? closingDay : null,
            due_day: isCredit ? dueDay : null
        })
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <AdjustmentsHorizontalIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para configurar métodos de pago, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <CreditCardIcon className="w-7 h-7 text-indigo-600" />
                        Métodos de Pago
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Configurá tus cuentas bancarias, cajas y tarjetas de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <button onClick={() => setShowForm(!showForm)} className="btn-primary">
                    <PlusIcon className="w-5 h-5" /> Nuevo Método
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleSubmit} className="glass-card p-6 grid grid-cols-1 sm:grid-cols-2 gap-6 animate-fade-in">
                    <div className="col-span-1 sm:col-span-2">
                        <label className="block text-sm font-medium text-gray-700">Nombre del Método</label>
                        <input type="text" value={name} onChange={(e) => setName(e.target.value)} required
                            placeholder="Ej: Galicia 1234, Caja Chica" className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Tipo</label>
                        <select value={type} onChange={(e) => setType(e.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-white">
                            <option value="BANK">Banco / Transferencia</option>
                            <option value="CASH">Efectivo / Caja</option>
                            <option value="CARD">Tarjeta</option>
                            <option value="OTHER">Otro</option>
                        </select>
                    </div>
                    {type === 'BANK' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Nombre del Banco</label>
                            <input type="text" value={bank} onChange={(e) => setBank(e.target.value)} required
                                placeholder="Ej: Galicia" className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                        </div>
                    )}
                    <div className="flex items-center gap-4 py-8">
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" checked={isCredit} onChange={(e) => setIsCredit(e.target.checked)} className="w-4 h-4 text-indigo-600 rounded" />
                            <span className="text-sm font-medium text-gray-700">¿Es tarjeta de crédito?</span>
                        </label>
                    </div>
                    {isCredit && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Día de Cierre</label>
                                <input type="number" value={closingDay} onChange={(e) => setClosingDay(Number(e.target.value))} required min={1} max={31}
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Día de Vencimiento</label>
                                <input type="number" value={dueDay} onChange={(e) => setDueDay(Number(e.target.value))} required min={1} max={31}
                                    className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                            </div>
                        </>
                    )}
                    <div className="col-span-1 sm:col-span-2 flex justify-end gap-3 pt-4">
                        <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 font-medium">Cancelar</button>
                        <button type="submit" disabled={createMutation.isPending} className="btn-primary">
                            {createMutation.isPending ? 'Guardando...' : 'Crear Método'}
                        </button>
                    </div>
                </form>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {isLoading ? (
                    Array(3).fill(0).map((_, i) => <div key={i} className="glass-card h-32 animate-pulse" />)
                ) : methods?.length === 0 ? (
                    <div className="col-span-full py-20 text-center glass-card">
                        <CreditCardIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <p className="mt-2 text-sm text-gray-500">No hay métodos de pago configurados.</p>
                    </div>
                ) : methods?.map((pm: any) => (
                    <div key={pm.id} className="glass-card p-5 relative group overflow-hidden transition-all hover:ring-2 hover:ring-indigo-500/30">
                        <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                                <div className={clsx("p-2 rounded-xl", 
                                    pm.type === 'BANK' ? "bg-blue-50 text-blue-600" :
                                    pm.type === 'CASH' ? "bg-emerald-50 text-emerald-600" :
                                    pm.type === 'CARD' ? "bg-purple-50 text-purple-600" : "bg-gray-50 text-gray-600")}>
                                    {pm.type === 'BANK' ? <BuildingLibraryIcon className="w-6 h-6" /> :
                                     pm.type === 'CASH' ? <BanknotesIcon className="w-6 h-6" /> :
                                     pm.type === 'CARD' ? <CreditCardIcon className="w-6 h-6" /> : <AdjustmentsHorizontalIcon className="w-6 h-6" />}
                                </div>
                                <div className="font-bold text-gray-900">{pm.name}</div>
                            </div>
                            <button onClick={() => deleteMutation.mutate(pm.id)} className="p-1.5 text-gray-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-all opacity-0 group-hover:opacity-100">
                                <TrashIcon className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="mt-4 flex flex-wrap gap-2">
                            {pm.bank && <span className="badge badge-neutral text-[10px]">{pm.bank}</span>}
                            {pm.is_credit && <span className="badge badge-warning text-[10px]">Crédito (Cierre: {pm.closing_day})</span>}
                            <span className={clsx("badge text-[10px]", pm.is_active ? "badge-success" : "badge-neutral")}>
                                {pm.is_active ? 'Activo' : 'Inactivo'}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
