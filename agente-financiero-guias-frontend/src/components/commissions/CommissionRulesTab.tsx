'use client'

import { useState, Fragment } from 'react'
import { 
    PlusIcon, 
    PencilSquareIcon, 
    TrashIcon, 
    AdjustmentsHorizontalIcon,
    UserIcon,
    Square3Stack3DIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline'
import { useCommissions } from '@/hooks/useCommissions'
import { CommissionRule } from '@/types/commissions'
import { Dialog, Transition } from '@headlessui/react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { clsx } from 'clsx'

const ruleSchema = z.object({
    recipient_id: z.string().min(1, 'El destinatario es requerido'),
    client_id: z.string().nullable(),
    service_id: z.string().nullable(),
    percentage: z.number().min(0.1, 'Mínimo 0.1%').max(100, 'Máximo 100%'),
})

type FormData = z.infer<typeof ruleSchema>

export function CommissionRulesTab({ companyId }: { companyId: string }) {
    const { 
        rules, 
        isLoadingRules, 
        recipients,
        createRule, 
        updateRule, 
        deleteRule 
    } = useCommissions(companyId)

    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingRule, setEditingRule] = useState<CommissionRule | null>(null)
    const [serverError, setServerError] = useState<string | null>(null)

    // Necesitamos clientes y servicios para el modal
    const { data: clients = [] } = useQuery({
        queryKey: ['clients', companyId],
        queryFn: async () => {
            const res = await api.clients.list(companyId)
            return res.data
        },
        enabled: isModalOpen
    })

    const { data: services = [] } = useQuery({
        queryKey: ['services', companyId],
        queryFn: async () => {
            const res = await api.services.list(companyId)
            return res.data
        },
        enabled: isModalOpen
    })

    const {
        register,
        handleSubmit,
        reset,
        watch,
        formState: { errors }
    } = useForm<FormData>({
        resolver: zodResolver(ruleSchema)
    })

    const handleOpenModal = (rule?: CommissionRule) => {
        setServerError(null)
        if (rule) {
            setEditingRule(rule)
            reset({
                recipient_id: rule.recipient_id,
                client_id: rule.client_id,
                service_id: rule.service_id,
                percentage: rule.percentage
            })
        } else {
            setEditingRule(null)
            reset({
                recipient_id: '',
                client_id: null,
                service_id: null,
                percentage: 10
            })
        }
        setIsModalOpen(true)
    }

    const onSubmit = (data: FormData) => {
        setServerError(null)
        const payload = { ...data, company_id: companyId }

        const mutation = editingRule ? updateRule : createRule
        const mutationParams = editingRule ? { id: editingRule.id, data: payload } : payload

        mutation.mutate(mutationParams as any, {
            onSuccess: () => setIsModalOpen(false),
            onError: (error: any) => {
                if (error.response?.status === 400) {
                    setServerError("Ya existe una regla para esta combinación de destinatario, cliente y servicio. Editá la regla existente.")
                } else {
                    setServerError("Error al guardar la regla. Por favor reintentá.")
                }
            }
        })
    }

    const handleDelete = (id: string) => {
        if (confirm('¿Estás seguro de eliminar esta regla?')) {
            deleteRule.mutate(id)
        }
    }

    if (isLoadingRules) {
        return <div className="p-12 text-center animate-pulse">Cargando reglas...</div>
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-900">Configuración de Reglas</h3>
                <button
                    onClick={() => handleOpenModal()}
                    className="btn-primary"
                >
                    <PlusIcon className="w-5 h-5 mr-2" />
                    Nueva Regla
                </button>
            </div>

            <div className="glass-card overflow-hidden">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>Destinatario</th>
                            <th>Aplica a Cliente</th>
                            <th>Aplica a Servicio</th>
                            <th className="text-right">% Comisión</th>
                            <th className="text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {rules.map((rule: any) => (
                            <tr key={rule.id} className="hover:bg-gray-50/50 group">
                                <td className="py-4">
                                    <div className="flex items-center gap-2">
                                        <div className="p-1.5 bg-blue-50 text-blue-600 rounded-md">
                                            <UserIcon className="w-4 h-4" />
                                        </div>
                                        <span className="font-semibold text-gray-900">{rule.recipient_name}</span>
                                    </div>
                                </td>
                                <td>
                                    <span className={clsx(
                                        "text-sm font-medium",
                                        rule.client_id ? "text-gray-700" : "text-blue-600 italic font-bold"
                                    )}>
                                        {rule.client_name || 'Todos los clientes'}
                                    </span>
                                </td>
                                <td>
                                    <span className={clsx(
                                        "text-sm font-medium",
                                        rule.service_id ? "text-gray-700" : "text-emerald-600 italic font-bold"
                                    )}>
                                        {rule.service_name || 'Todos los servicios'}
                                    </span>
                                </td>
                                <td className="text-right font-black text-blue-700">
                                    {rule.percentage}%
                                </td>
                                <td className="text-right">
                                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity pr-4">
                                        <button
                                            onClick={() => handleOpenModal(rule)}
                                            className="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                                            title="Editar"
                                        >
                                            <PencilSquareIcon className="w-5 h-5" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(rule.id)}
                                            className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                                            title="Eliminar"
                                        >
                                            <TrashIcon className="w-5 h-5" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Modal CRUD Reglas */}
            <Transition.Root show={isModalOpen} as={Fragment}>
                <Dialog as="div" className="relative z-50" onClose={setIsModalOpen}>
                    <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0">
                        <div className="fixed inset-0 bg-gray-900/60 transition-opacity backdrop-blur-sm" />
                    </Transition.Child>
                    <div className="fixed inset-0 z-10 overflow-y-auto">
                        <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                            <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enterTo="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leaveFrom="opacity-100 translate-y-0 sm:scale-100" leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                                <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white px-4 pb-4 pt-5 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-md sm:p-6">
                                    <Dialog.Title as="h3" className="text-xl font-bold leading-6 text-gray-900 flex items-center gap-2 mb-6">
                                        <AdjustmentsHorizontalIcon className="w-6 h-6 text-blue-600" />
                                        {editingRule ? 'Editar Regla' : 'Nueva Regla'}
                                    </Dialog.Title>

                                    {serverError && (
                                        <div className="mb-4 p-3 bg-red-50 border border-red-100 rounded-lg flex gap-2 text-rose-700 text-xs">
                                            <ExclamationCircleIcon className="w-4 h-4 flex-shrink-0" />
                                            {serverError}
                                        </div>
                                    )}

                                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">Destinatario</label>
                                            <select {...register('recipient_id')} className="input-field" disabled={!!editingRule}>
                                                <option value="">Seleccionar beneficiario</option>
                                                {recipients.map((r: any) => <option key={r.id} value={r.id}>{r.name}</option>)}
                                            </select>
                                            {errors.recipient_id && <p className="text-xs text-red-500 mt-1">{errors.recipient_id.message}</p>}
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-semibold text-gray-700 mb-1">Cliente</label>
                                                <select 
                                                    {...register('client_id')} 
                                                    className="input-field"
                                                    onChange={(e) => reset({ ...watch(), client_id: e.target.value || null })}
                                                >
                                                    <option value="">Todos los clientes</option>
                                                    {clients.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-semibold text-gray-700 mb-1">Servicio</label>
                                                <select 
                                                    {...register('service_id')} 
                                                    className="input-field"
                                                    onChange={(e) => reset({ ...watch(), service_id: e.target.value || null })}
                                                >
                                                    <option value="">Todos los servicios</option>
                                                    {services.map((s: any) => <option key={s.id} value={s.id}>{s.name}</option>)}
                                                </select>
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">Porcentaje de Comisión</label>
                                            <div className="relative">
                                                <input 
                                                    type="number" 
                                                    step="0.1" 
                                                    {...register('percentage', { valueAsNumber: true })} 
                                                    className="input-field pr-8 font-mono" 
                                                />
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">%</span>
                                            </div>
                                            {errors.percentage && <p className="text-xs text-red-500 mt-1">{errors.percentage.message}</p>}
                                        </div>

                                        <div className="mt-8 flex gap-3">
                                            <button type="submit" className="btn-primary flex-1">
                                                {editingRule ? 'Guardar Cambios' : 'Crear Regla'}
                                            </button>
                                            <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">
                                                Cancelar
                                            </button>
                                        </div>
                                    </form>
                                </Dialog.Panel>
                            </Transition.Child>
                        </div>
                    </div>
                </Dialog>
            </Transition.Root>
        </div>
    )
}
