'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PlusIcon, BanknotesIcon, CalendarDaysIcon, ChartBarIcon, ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import { formatCurrency } from '@/utils/formatters'

export default function DeudasPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()
    const [showForm, setShowForm] = useState(false)

    // Form state
    const [description, setDescription] = useState('')
    const [amount, setAmount] = useState<number | ''>('')
    const [interestType, setInterestType] = useState('FIXED')
    const [interestRate, setInterestRate] = useState<number | ''>('')
    const [totalAmount, setTotalAmount] = useState<number | ''>('')
    const [installments, setInstallments] = useState<number>(1)

    const { data: debts, isLoading } = useQuery({
        queryKey: ['debts', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.debts.list(selectedCompany.id)
            return Array.isArray(res.data) ? res.data : (res.data.data || [])
        },
        enabled: !!selectedCompany,
    })

    const createMutation = useMutation({
        mutationFn: (data: any) => api.debts.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['debts'] })
            setShowForm(false)
            resetForm()
        }
    })

    const resetForm = () => {
        setDescription('')
        setAmount('')
        setInterestType('FIXED')
        setInterestRate('')
        setTotalAmount('')
        setInstallments(1)
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany) return
        createMutation.mutate({
            company_id: selectedCompany.id,
            description,
            original_amount: Number(amount),
            interest_type: interestType,
            interest_rate: Number(interestRate),
            total_amount: Number(totalAmount),
            installments
        })
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <BanknotesIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para gestionar deudas, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ExclamationTriangleIcon className="w-7 h-7 text-indigo-600" />
                        Pasivos y Deudas
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Administrá préstamos, tarjetas de crédito y otras obligaciones financieras.
                    </p>
                </div>
                <button onClick={() => setShowForm(!showForm)} className="btn-primary">
                    <PlusIcon className="w-5 h-5" /> Nueva Deuda
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleSubmit} className="glass-card p-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 animate-fade-in">
                    <div className="col-span-1 sm:col-span-2 md:col-span-3">
                        <label className="block text-sm font-medium text-gray-700">Descripción</label>
                        <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} required
                            placeholder="Ej: Préstamo Banco Galicia, Cuotas PC" className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Monto Original</label>
                        <div className="relative mt-1">
                            <span className="absolute left-3 top-2 text-gray-400">$</span>
                            <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} required
                                className="w-full pl-7 pr-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Tasa de Interés (%)</label>
                        <input type="number" value={interestRate} onChange={(e) => setInterestRate(Number(e.target.value))}
                            className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Total a Pagar</label>
                        <div className="relative mt-1">
                            <span className="absolute left-3 top-2 text-gray-400">$</span>
                            <input type="number" value={totalAmount} onChange={(e) => setTotalAmount(Number(e.target.value))} required
                                className="w-full pl-7 pr-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Cuotas</label>
                        <input type="number" value={installments} onChange={(e) => setInstallments(Number(e.target.value))} required min={1}
                            className="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                    </div>
                    <div className="col-span-1 sm:col-span-2 md:col-span-3 flex justify-end gap-3 pt-4 border-t border-gray-100">
                        <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 font-medium">Cancelar</button>
                        <button type="submit" disabled={createMutation.isPending} className="btn-primary">
                            {createMutation.isPending ? 'Guardando...' : 'Crear Deuda'}
                        </button>
                    </div>
                </form>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {isLoading ? (
                    Array(4).fill(0).map((_, i) => <div key={i} className="glass-card h-40 animate-pulse" />)
                ) : debts?.length === 0 ? (
                    <div className="col-span-full py-20 text-center glass-card">
                        <BanknotesIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <p className="mt-2 text-sm text-gray-500">No hay deudas registradas.</p>
                    </div>
                ) : debts?.map((debt: any) => (
                    <div key={debt.id} className="glass-card p-6 border-l-4 border-l-indigo-500 transition-all hover:translate-x-1">
                        <div className="flex items-start justify-between">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">{debt.description}</h3>
                                <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                                    <span className="flex items-center gap-1"><CalendarDaysIcon className="w-3 h-3" /> {new Date(debt.created_at).toLocaleDateString()}</span>
                                    <span className={clsx("badge text-[10px]", 
                                        (debt.status === 'PENDING' || debt.status === 'ACTIVE' || debt.status === 'PARTIAL') ? "badge-warning" : "badge-success")}>
                                        {(debt.status === 'PENDING' || debt.status === 'ACTIVE') ? 'Activa' : debt.status === 'PARTIAL' ? 'Parcial' : 'Pagada'}
                                    </span>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-black text-gray-900">{formatCurrency(debt.total_amount)}</div>
                                <div className="text-xs text-gray-500">en {debt.installments} cuotas</div>
                            </div>
                        </div>
                        <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between text-sm">
                            <div className="flex gap-4">
                                <div>
                                    <span className="text-gray-400 block text-[10px] uppercase font-bold tracking-wider">Original</span>
                                    <span className="font-semibold text-gray-700">{formatCurrency(debt.original_amount)}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400 block text-[10px] uppercase font-bold tracking-wider">Tasa</span>
                                    <span className="font-semibold text-gray-700">{debt.interest_rate}%</span>
                                </div>
                            </div>
                            <button className="flex items-center gap-1 text-indigo-600 font-bold hover:underline">
                                Ver Cuotas <ArrowPathIcon className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
