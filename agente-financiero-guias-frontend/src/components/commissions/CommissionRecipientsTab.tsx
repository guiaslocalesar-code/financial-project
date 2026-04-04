'use client'

import { useState, Fragment } from 'react'
import { 
    PlusIcon, 
    PencilSquareIcon, 
    TrashIcon, 
    UserIcon,
    EnvelopeIcon,
    IdentificationIcon,
    ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline'
import { useCommissions } from '@/hooks/useCommissions'
import { CommissionRecipient } from '@/types/commissions'
import { Dialog, Transition } from '@headlessui/react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import Link from 'next/link'
import { clsx } from 'clsx'

const recipientSchema = z.object({
    name: z.string().min(3, 'Nombre demasiado corto'),
    type: z.enum(['supplier', 'employee', 'partner']),
    cuit: z.string().min(11, 'CUIT inválido (11 dígitos)').max(13),
    email: z.string().email('Email inválido'),
})

type FormData = z.infer<typeof recipientSchema>

export function CommissionRecipientsTab({ companyId }: { companyId: string }) {
    const { 
        recipients, 
        isLoadingRecipients, 
        createRecipient, 
        updateRecipient, 
        deleteRecipient 
    } = useCommissions(companyId)

    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingRecipient, setEditingRecipient] = useState<CommissionRecipient | null>(null)

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors }
    } = useForm<FormData>({
        resolver: zodResolver(recipientSchema)
    })

    const handleOpenModal = (recipient?: CommissionRecipient) => {
        if (recipient) {
            setEditingRecipient(recipient)
            reset({
                name: recipient.name,
                type: recipient.type,
                cuit: recipient.cuit,
                email: recipient.email
            })
        } else {
            setEditingRecipient(null)
            reset({
                name: '',
                type: 'employee',
                cuit: '',
                email: ''
            })
        }
        setIsModalOpen(true)
    }

    const onSubmit = (data: FormData) => {
        if (editingRecipient) {
            updateRecipient.mutate({ id: editingRecipient.id, data }, {
                onSuccess: () => setIsModalOpen(false)
            })
        } else {
            createRecipient.mutate({ ...data, company_id: companyId }, {
                onSuccess: () => setIsModalOpen(false)
            })
        }
    }

    const handleDelete = (id: string) => {
        if (confirm('¿Estás seguro de eliminar este destinatario?')) {
            deleteRecipient.mutate(id)
        }
    }

    if (isLoadingRecipients) {
        return <div className="p-12 text-center animate-pulse">Cargando destinatarios...</div>
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-900">Destinatarios de Comisiones</h3>
                <button
                    onClick={() => handleOpenModal()}
                    className="btn-primary"
                >
                    <PlusIcon className="w-5 h-5 mr-2" />
                    Nuevo Destinatario
                </button>
            </div>

            <div className="glass-card overflow-hidden">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>Nombre / Datos</th>
                            <th>Tipo</th>
                            <th className="text-right">Total Generado</th>
                            <th className="text-right">Pendiente</th>
                            <th className="text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {recipients.map((r: any) => (
                            <tr key={r.id} className="hover:bg-gray-50/50 group">
                                <td className="py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
                                            <UserIcon className="w-5 h-5" />
                                        </div>
                                        <div className="flex flex-col">
                                            <span className="font-semibold text-gray-900">{r.name}</span>
                                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                                <IdentificationIcon className="w-3 h-3" /> {r.cuit}
                                                <span>•</span>
                                                <EnvelopeIcon className="w-3 h-3" /> {r.email}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span className={clsx(
                                        "badge",
                                        r.type === 'partner' ? "bg-purple-50 text-purple-700 border-purple-100" :
                                        r.type === 'employee' ? "bg-amber-50 text-amber-700 border-amber-100" :
                                        "bg-gray-50 text-gray-700 border-gray-100"
                                    )}>
                                        {r.type === 'partner' ? 'Socio' : r.type === 'employee' ? 'Empleado' : 'Proveedor'}
                                    </span>
                                </td>
                                <td className="text-right font-mono font-medium text-gray-600">
                                    ${(r.total_commissions || 0).toLocaleString('es-AR')}
                                </td>
                                <td className="text-right font-mono font-bold text-blue-700">
                                    ${(r.total_pending || 0).toLocaleString('es-AR')}
                                </td>
                                <td className="text-right">
                                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity pr-4">
                                        <Link
                                            href={`/holding/comisiones/${r.id}`}
                                            className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                            title="Ver detalle"
                                        >
                                            <ArrowTopRightOnSquareIcon className="w-5 h-5" />
                                        </Link>
                                        <button
                                            onClick={() => handleOpenModal(r)}
                                            className="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                                            title="Editar"
                                        >
                                            <PencilSquareIcon className="w-5 h-5" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(r.id)}
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

            {/* Modal CRUD */}
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
                                        {editingRecipient ? 'Editar Destinatario' : 'Nuevo Destinatario'}
                                    </Dialog.Title>
                                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">Nombre Completo</label>
                                            <input type="text" {...register('name')} className="input-field" placeholder="Ej: Juan Pérez" />
                                            {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name.message}</p>}
                                        </div>
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">Tipo</label>
                                            <select {...register('type')} className="input-field">
                                                <option value="employee">Empleado</option>
                                                <option value="partner">Socio / Dueño</option>
                                                <option value="supplier">Proveedor Externo</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">CUIT</label>
                                            <input type="text" {...register('cuit')} className="input-field" placeholder="20-XXXXXXXX-X" />
                                            {errors.cuit && <p className="text-xs text-red-500 mt-1">{errors.cuit.message}</p>}
                                        </div>
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                                            <input type="email" {...register('email')} className="input-field" placeholder="email@ejemplo.com" />
                                            {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
                                        </div>
                                        <div className="mt-8 flex gap-3">
                                            <button type="submit" className="btn-primary flex-1">
                                                {editingRecipient ? 'Guardar Cambios' : 'Crear Destinatario'}
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
