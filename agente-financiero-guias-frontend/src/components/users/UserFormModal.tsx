'use client'

import { Fragment, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useForm, Controller } from 'react-hook-form'
import { api } from '@/services/api'
import { toast } from 'react-hot-toast'

interface UserFormModalProps {
    isOpen: boolean
    onClose: () => void
    companyId: string | null
    onSuccess: () => void
    editData: any | null
}

const AVAILABLE_PERMISSIONS = [
    { id: 'dashboard:read', label: 'Ver Dashboard' },
    { id: 'clients:write', label: 'Gestionar Clientes y Servicios' },
    { id: 'invoices:read', label: 'Ver Facturas' },
    { id: 'invoices:write', label: 'Emitir Facturas' },
    { id: 'debts:write', label: 'Gestionar Deudas' },
    { id: 'budgets:write', label: 'Gestionar Presupuestos' },
    { id: 'transactions:write', label: 'Gestionar Movimientos' },
    { id: 'settings:write', label: 'Configuración Administrativa' }
]

export default function UserFormModal({ isOpen, onClose, companyId, onSuccess, editData }: UserFormModalProps) {
    const isEdit = !!editData

    const { register, handleSubmit, control, reset, formState: { errors, isSubmitting } } = useForm({
        defaultValues: {
            email: '',
            role: 'user',
            permissions: [] as string[],
            quotaparte: ''
        }
    })

    useEffect(() => {
        if (isOpen) {
            if (isEdit && editData) {
                reset({
                    email: editData.user?.email || '',
                    role: editData.role || 'user',
                    permissions: editData.permissions || [],
                    quotaparte: editData.quotaparte || ''
                })
            } else {
                reset({ email: '', role: 'user', permissions: [], quotaparte: '' })
            }
        }
    }, [isOpen, editData, reset])

    const onSubmit = async (data: any) => {
        if (!companyId) return

        try {
            const payload = {
                email: data.email,
                role: data.role,
                permissions: data.permissions.length > 0 ? data.permissions : null,
                quotaparte: data.quotaparte ? parseFloat(data.quotaparte) : null
            }

            if (isEdit) {
                delete payload.email // No actualizamos email
                await api.users.updateRole(editData.id, payload)
                toast.success('Permisos actualizados exitosamente')
            } else {
                await api.users.inviteUser(companyId, payload)
                toast.success('Usuario invitado exitosamente')
            }
            onSuccess()
            onClose()
        } catch (error: any) {
            console.error('Error saving user permissions:', error)
            const detail = error.response?.data?.detail 
                ? (typeof error.response.data.detail === 'string' ? error.response.data.detail : 'Error de validación') 
                : 'Ocurrió un error al guardar'
            toast.error(detail)
        }
    }

    return (
        <Transition.Root show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={onClose}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-gray-900/70 backdrop-blur-sm transition-opacity" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto">
                    <div className="flex min-h-full justify-center p-4 text-center items-center sm:p-0">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-xl">
                                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block z-10">
                                    <button
                                        type="button"
                                        className="rounded-full bg-white/10 p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none transition-colors"
                                        onClick={onClose}
                                    >
                                        <XMarkIcon className="h-5 w-5" aria-hidden="true" />
                                    </button>
                                </div>

                                <div className="bg-gradient-to-br from-indigo-50 via-white to-blue-50 px-6 py-8">
                                    <div className="sm:flex sm:items-start">
                                        <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                                            <Dialog.Title as="h3" className="text-xl font-semibold leading-6 text-gray-900 flex items-center gap-2">
                                                {isEdit ? 'Editar Permisos del Usuario' : 'Invitar Miembro'}
                                            </Dialog.Title>
                                            <p className="mt-2 text-sm text-gray-500">
                                                {isEdit 
                                                    ? 'Módulo avanzado para re-asignar los permisos del usuario activo.' 
                                                    : 'Vincular a un empleado o contador existente en el portal web (ingresando su email).'}
                                            </p>
                                        </div>
                                    </div>

                                    <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-5 px-4">
                                        
                                        {!isEdit && (
                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Email del Usuario <span className="text-red-500">*</span>
                                                </label>
                                                <div className="mt-2">
                                                    <input
                                                        type="email"
                                                        disabled={isEdit}
                                                        {...register('email', { required: 'El email es requerido' })}
                                                        className="block w-full rounded-xl border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>
                                            </div>
                                        )}

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Rol General
                                                </label>
                                                <select
                                                    {...register('role')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                                >
                                                    <option value="admin">Administrador Geral</option>
                                                    <option value="owner">Dueño</option>
                                                    <option value="accountant">Contador</option>
                                                    <option value="user">Usuario Básico</option>
                                                </select>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Cuotaparte (%)
                                                </label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('quotaparte')}
                                                    placeholder="Ej: 30.50"
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                                />
                                            </div>
                                        </div>

                                        <div className="border-t border-gray-200 pt-5 mt-5">
                                            <h4 className="text-sm font-medium text-gray-900 mb-4">Permisos Granulares Especiales</h4>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                {AVAILABLE_PERMISSIONS.map((perm) => (
                                                    <label key={perm.id} className="relative flex items-start gap-3 p-3 rounded-xl border border-gray-200 bg-white/50 hover:bg-white cursor-pointer transition-colors shadow-sm">
                                                        <div className="flex h-6 items-center">
                                                            <input
                                                                type="checkbox"
                                                                value={perm.id}
                                                                {...register('permissions')}
                                                                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                                                            />
                                                        </div>
                                                        <div className="text-sm leading-6">
                                                            <span className="font-medium text-gray-900">{perm.label}</span>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                            <p className="mt-3 text-xs text-gray-500">
                                                Si no seleccionás nada, se aplicarán los permisos por defecto de su Rol General.
                                            </p>
                                        </div>

                                        <div className="mt-8 flex items-center justify-end gap-x-3 border-t border-gray-200 pt-6">
                                            <button
                                                type="button"
                                                onClick={onClose}
                                                className="rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                            >
                                                Cancelar
                                            </button>
                                            <button
                                                type="submit"
                                                disabled={isSubmitting}
                                                className="inline-flex justify-center rounded-xl bg-indigo-600 px-8 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                            >
                                                {isSubmitting ? 'Guardando...' : (isEdit ? 'Guardar Cambios' : 'Invitar Usuario')}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
