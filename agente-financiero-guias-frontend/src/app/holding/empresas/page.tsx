'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlusIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Company } from '@/types'
import { CompanyFormModal } from '@/components/companies/CompanyFormModal'
import { useHoldingContext } from '@/context/HoldingContext'

export default function EmpresasPage() {
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingCompany, setEditingCompany] = useState<Company | null>(null)
    const { setCompanies } = useHoldingContext()

    const { data, isLoading, error } = useQuery({
        queryKey: ['companies'],
        queryFn: async () => {
            const res = await api.companies.list()
            const companiesList = Array.isArray(res.data) ? res.data : (res.data.data || res.data.companies || [])
            setCompanies(companiesList) // Update global context whenever list refreshes
            return companiesList as Company[]
        }
    })

    const handleCreate = () => {
        setEditingCompany(null)
        setIsModalOpen(true)
    }

    const handleEdit = (company: Company) => {
        setEditingCompany(company)
        setIsModalOpen(true)
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <BuildingOfficeIcon className="w-7 h-7 text-blue-600" />
                        Empresas
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Gestioná las unidades de negocio del holding.
                    </p>
                </div>
                <button
                    onClick={handleCreate}
                    className="btn-primary"
                >
                    <PlusIcon className="w-5 h-5" />
                    Nueva Empresa
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
                        Error al cargar las empresas. Conecte el backend.
                    </div>
                ) : !data || data.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay empresas</h3>
                        <p className="mt-1 text-sm text-gray-500">Comenzá creando la primera unidad de negocio.</p>
                        <div className="mt-6">
                            <button onClick={handleCreate} className="btn-primary">
                                <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                                Nueva Empresa
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Empresa</th>
                                    <th>CUIT</th>
                                    <th>Condición Fiscal</th>
                                    <th>Punto Venta</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.map((company) => (
                                    <tr 
                                        key={company.id}
                                        onClick={() => handleEdit(company)}
                                        className="cursor-pointer hover:bg-gray-50/80 transition-all duration-200 group border-b border-gray-100 last:border-0"
                                    >
                                        <td>
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-sm border-2 border-white">
                                                    {company.name.substring(0, 2).toUpperCase()}
                                                </div>
                                                <div className="font-bold text-gray-900 transition-colors group-hover:text-blue-600">{company.name}</div>
                                            </div>
                                        </td>
                                        <td className="text-sm text-gray-600 font-mono">{company.cuit}</td>
                                        <td className="text-sm text-gray-600">
                                            {company.fiscal_condition === 'RI' ? 'Resp. Inscripto' : 
                                             company.fiscal_condition === 'MONOTRIBUTO' ? 'Monotributo' :
                                             company.fiscal_condition === 'EXENTO' ? 'Exento' : company.fiscal_condition}
                                        </td>
                                        <td className="text-sm text-gray-600 font-mono">{company.afip_point_of_sale || '—'}</td>
                                        <td>
                                            <span className={clsx(
                                                "text-xs font-semibold px-2 py-1 rounded-md ring-1 ring-inset",
                                                company.is_active 
                                                    ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20" 
                                                    : "bg-gray-50 text-gray-600 ring-gray-500/10"
                                            )}>
                                                {company.is_active ? 'Activa' : 'Inactiva'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <CompanyFormModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                company={editingCompany}
            />
        </div>
    )
}
