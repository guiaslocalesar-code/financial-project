'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PlusIcon, TagIcon, FolderIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { ExpenseType, ExpenseCategory } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'

export default function ConfigGastosPage() {
    const { selectedCompany } = useHoldingContext()
    const queryClient = useQueryClient()

    const [selectedTypeId, setSelectedTypeId] = useState<string | null>(null)

    // ── Forms state ──
    const [showTypeForm, setShowTypeForm] = useState(false)
    const [typeName, setTypeName] = useState('')
    const [typeAppliesTo, setTypeAppliesTo] = useState('BOTH')

    const [showCatForm, setShowCatForm] = useState(false)
    const [catName, setCatName] = useState('')
    const [catTypeId, setCatTypeId] = useState('')

    // ── Queries ──
    const { data: types, isLoading: loadingTypes } = useQuery({
        queryKey: ['expenseTypes', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listTypes(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as ExpenseType[]
        },
        enabled: !!selectedCompany,
    })

    const { data: categories, isLoading: loadingCats } = useQuery({
        queryKey: ['expenseCategories', selectedCompany?.id, selectedTypeId],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.expenses.listCategories(selectedCompany.id, selectedTypeId || undefined)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as ExpenseCategory[]
        },
        enabled: !!selectedCompany,
    })

    // ── Mutations ──
    const createTypeMutation = useMutation({
        mutationFn: (data: any) => api.expenses.createType(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['expenseTypes'] })
            setShowTypeForm(false)
            setTypeName('')
        }
    })

    const createCatMutation = useMutation({
        mutationFn: (data: any) => api.expenses.createCategory(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['expenseCategories'] })
            setShowCatForm(false)
            setCatName('')
        }
    })

    const handleCreateType = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany) return
        createTypeMutation.mutate({ company_id: selectedCompany.id, name: typeName, applies_to: typeAppliesTo.toLowerCase() })
    }

    const handleCreateCat = (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCompany || !catTypeId) return
        createCatMutation.mutate({ company_id: selectedCompany.id, expense_type_id: catTypeId, name: catName })
    }

    // ── Helpers ──
    const appliesToLabel = (v: string) => {
        const map: Record<string, string> = { BUDGETED: 'Presupuestado', UNBUDGETED: 'No presupuestado', BOTH: 'Ambos' }
        return map[v?.toUpperCase()] || v
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <AdjustmentsHorizontalIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para configurar los gastos, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <AdjustmentsHorizontalIcon className="w-7 h-7 text-amber-600" />
                    Configuración de Gastos
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                    Tipos y categorías de egresos de <span className="font-semibold">{selectedCompany.name}</span>.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* ═══ EXPENSE TYPES ═══ */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                            <TagIcon className="w-5 h-5 text-amber-500" />
                            Tipos de Gasto
                        </h2>
                        <button onClick={() => setShowTypeForm(!showTypeForm)} className="text-sm text-amber-600 hover:text-amber-700 font-medium flex items-center gap-1">
                            <PlusIcon className="w-4 h-4" /> Nuevo
                        </button>
                    </div>

                    {showTypeForm && (
                        <form onSubmit={handleCreateType} className="glass-card p-4 space-y-3">
                            <input
                                type="text" placeholder="Nombre del tipo" value={typeName}
                                onChange={(e) => setTypeName(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 outline-none text-sm"
                                required
                            />
                            <select value={typeAppliesTo} onChange={(e) => setTypeAppliesTo(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 outline-none text-sm bg-white">
                                <option value="BOTH">Ambos</option>
                                <option value="BUDGETED">Solo presupuestado</option>
                                <option value="UNBUDGETED">Solo no presupuestado</option>
                            </select>
                            <div className="flex gap-2">
                                <button type="submit" disabled={createTypeMutation.isPending} className="btn-primary bg-amber-600 hover:bg-amber-700 text-sm">
                                    {createTypeMutation.isPending ? 'Guardando...' : 'Crear Tipo'}
                                </button>
                                <button type="button" onClick={() => setShowTypeForm(false)} className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700">Cancelar</button>
                            </div>
                        </form>
                    )}

                    <div className="glass-card overflow-hidden">
                        {loadingTypes ? (
                            <div className="p-8 flex justify-center">
                                <div className="w-6 h-6 border-3 border-amber-200 border-t-amber-600 rounded-full animate-spin" />
                            </div>
                        ) : !types || types.length === 0 ? (
                            <div className="text-center py-10 px-4">
                                <TagIcon className="mx-auto h-10 w-10 text-gray-300" />
                                <p className="mt-2 text-sm text-gray-500">No hay tipos de gasto.</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-100">
                                {types.map((type) => (
                                    <button
                                        key={type.id}
                                        onClick={() => setSelectedTypeId(selectedTypeId === type.id ? null : type.id)}
                                        className={clsx(
                                            'w-full flex items-center justify-between px-4 py-3 text-left transition-colors',
                                            selectedTypeId === type.id ? 'bg-amber-50' : 'hover:bg-gray-50'
                                        )}
                                    >
                                        <div>
                                            <div className="font-medium text-gray-900 text-sm">{type.name}</div>
                                            <div className="text-xs text-gray-400">{appliesToLabel(type.applies_to)}</div>
                                        </div>
                                        <span className={clsx(
                                            type.is_active ? 'badge-success' : 'badge-neutral', 'text-[10px]'
                                        )}>
                                            {type.is_active ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* ═══ EXPENSE CATEGORIES ═══ */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                            <FolderIcon className="w-5 h-5 text-orange-500" />
                            Categorías
                            {selectedTypeId && types && (
                                <span className="text-xs text-gray-400 font-normal">
                                    — {types.find(t => t.id === selectedTypeId)?.name}
                                </span>
                            )}
                        </h2>
                        <button onClick={() => { setShowCatForm(!showCatForm); if (selectedTypeId) setCatTypeId(selectedTypeId) }} className="text-sm text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1">
                            <PlusIcon className="w-4 h-4" /> Nueva
                        </button>
                    </div>

                    {showCatForm && (
                        <form onSubmit={handleCreateCat} className="glass-card p-4 space-y-3">
                            <select value={catTypeId} onChange={(e) => setCatTypeId(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500/20 focus:border-orange-400 outline-none text-sm bg-white"
                                required>
                                <option value="">Seleccionar tipo...</option>
                                {types?.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                            </select>
                            <input
                                type="text" placeholder="Nombre de la categoría" value={catName}
                                onChange={(e) => setCatName(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500/20 focus:border-orange-400 outline-none text-sm"
                                required
                            />
                            <div className="flex gap-2">
                                <button type="submit" disabled={createCatMutation.isPending} className="btn-primary bg-orange-600 hover:bg-orange-700 text-sm">
                                    {createCatMutation.isPending ? 'Guardando...' : 'Crear Categoría'}
                                </button>
                                <button type="button" onClick={() => setShowCatForm(false)} className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700">Cancelar</button>
                            </div>
                        </form>
                    )}

                    <div className="glass-card overflow-hidden">
                        {loadingCats ? (
                            <div className="p-8 flex justify-center">
                                <div className="w-6 h-6 border-3 border-orange-200 border-t-orange-600 rounded-full animate-spin" />
                            </div>
                        ) : !categories || categories.length === 0 ? (
                            <div className="text-center py-10 px-4">
                                <FolderIcon className="mx-auto h-10 w-10 text-gray-300" />
                                <p className="mt-2 text-sm text-gray-500">
                                    {selectedTypeId ? 'No hay categorías para este tipo.' : 'Seleccioná un tipo de gasto para ver sus categorías.'}
                                </p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Categoría</th>
                                            <th>Tipo</th>
                                            <th>Estado</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {categories.map((cat) => {
                                            const parentType = types?.find(t => t.id === cat.expense_type_id)
                                            return (
                                                <tr key={cat.id}>
                                                    <td className="font-medium text-gray-900 text-sm">{cat.name}</td>
                                                    <td className="text-sm text-gray-500">{parentType?.name || '—'}</td>
                                                    <td>
                                                        <span className={clsx(cat.is_active ? 'badge-success' : 'badge-neutral', 'text-[10px]')}>
                                                            {cat.is_active ? 'Activo' : 'Inactivo'}
                                                        </span>
                                                    </td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
