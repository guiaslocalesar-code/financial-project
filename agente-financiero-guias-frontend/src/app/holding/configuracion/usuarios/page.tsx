'use client'

import { useState, useEffect } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import UserFormModal from '@/components/users/UserFormModal'
import { toast } from 'react-hot-toast'
import { clsx } from 'clsx'

const getRoleBadge = (role: string) => {
    switch (role) {
        case 'admin':
            return <span className="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-700/10">Administrador</span>
        case 'owner':
            return <span className="inline-flex items-center rounded-md bg-rose-50 px-2 py-1 text-xs font-medium text-rose-700 ring-1 ring-inset ring-rose-700/10">Dueño</span>
        case 'accountant':
            return <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">Contador</span>
        default:
            return <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-700 ring-1 ring-inset ring-gray-700/10">Usuario Base</span>
    }
}

export default function UsuariosPage() {
    const { selectedCompany } = useHoldingContext()
    const [users, setUsers] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [modalOpen, setModalOpen] = useState(false)
    const [editingUser, setEditingUser] = useState<any | null>(null)

    const fetchUsers = async () => {
        if (!selectedCompany) return
        setLoading(true)
        try {
            const { data } = await api.users.listFromCompany(selectedCompany.id)
            setUsers(data)
        } catch (error) {
            console.error('Error fetching users:', error)
            toast.error('No se pudieron cargar los usuarios')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (selectedCompany) {
            fetchUsers()
        }
    }, [selectedCompany])

    const handleDelete = async (id: string) => {
        if (!confirm('¿Estás seguro de que quieres remover a este usuario de la empresa?')) return
        try {
            await api.users.removeUser(id)
            toast.success('Usuario removido')
            fetchUsers()
        } catch (error) {
            console.error(error)
            toast.error('Error al remover usuario')
        }
    }

    if (!selectedCompany) {
        return (
            <div className="p-6 max-w-7xl mx-auto">
                <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
                    <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-300" />
                    <h3 className="mt-2 text-sm font-semibold text-gray-900">Seleccioná una empresa</h3>
                    <p className="mt-1 text-sm text-gray-500">Para ver y administrar usuarios, primero seleccioná una empresa arriba.</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex justify-between items-center bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ShieldCheckIcon className="w-6 h-6 text-indigo-600" />
                        Usuarios y Accesos
                    </h1>
                    <p className="text-gray-500 mt-2">Configurá quién tiene acceso y qué permisos tiene dentro de tu negocio.</p>
                </div>
                <button
                    onClick={() => {
                        setEditingUser(null)
                        setModalOpen(true)
                    }}
                    className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-500 transition-colors shadow-sm"
                >
                    <PlusIcon className="w-5 h-5" />
                    Invitar Usuario
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : users.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
                    <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-300" />
                    <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay usuarios adicionales</h3>
                    <p className="mt-1 text-sm text-gray-500">Parece que eres el único con acceso a este negocio.</p>
                </div>
            ) : (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50/50">
                            <tr>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Usuario</th>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Rol General</th>
                                <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Super Permisos JSON</th>
                                <th scope="col" className="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Cuotaparte</th>
                                <th scope="col" className="relative px-6 py-4"><span className="sr-only">Acciones</span></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 bg-white">
                            {users.map((uc) => (
                                <tr key={uc.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="whitespace-nowrap px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            {uc.user?.avatar_url ? (
                                                <img src={uc.user.avatar_url} alt="" className="h-10 w-10 rounded-full bg-gray-50 ring-2 ring-white shadow-sm" />
                                            ) : (
                                                <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-700 ring-2 ring-white shadow-sm">
                                                    {uc.user?.name?.substring(0, 2).toUpperCase() || '?'}
                                                </div>
                                            )}
                                            <div>
                                                <div className="font-semibold text-gray-900">{uc.user?.name}</div>
                                                <div className="text-sm text-gray-500">{uc.user?.email}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4">
                                        {getRoleBadge(uc.role)}
                                    </td>
                                    <td className="px-6 py-4">
                                        {uc.permissions && uc.permissions.length > 0 ? (
                                            <div className="flex flex-wrap gap-1 max-w-xs">
                                                {uc.permissions.map((p: string) => (
                                                    <span key={p} className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                                                        {p}
                                                    </span>
                                                ))}
                                            </div>
                                        ) : (
                                            <span className="text-sm text-gray-400 italic">Predefinidos</span>
                                        )}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-center">
                                        {uc.quotaparte ? (
                                            <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                                                {uc.quotaparte}%
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">-</span>
                                        )}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                                        <div className="flex items-center justify-end gap-2">
                                            <button
                                                onClick={() => {
                                                    setEditingUser(uc)
                                                    setModalOpen(true)
                                                }}
                                                className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                                title="Editar permisos"
                                            >
                                                <PencilIcon className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(uc.id)}
                                                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                title="Remover"
                                            >
                                                <TrashIcon className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <UserFormModal 
                isOpen={modalOpen}
                onClose={() => {
                    setModalOpen(false)
                    setEditingUser(null)
                }}
                companyId={selectedCompany?.id || null}
                onSuccess={fetchUsers}
                editData={editingUser}
            />
        </div>
    )
}
