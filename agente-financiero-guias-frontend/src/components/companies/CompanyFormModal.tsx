'use client'

import { Fragment, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, PencilSquareIcon } from '@heroicons/react/24/outline'
import { useForm, Controller } from 'react-hook-form'
import { ImageUpload } from '../common/ImageUpload'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { clsx } from 'clsx'
import { z } from 'zod'
import { api } from '@/services/api'
import type { Company } from '@/types'
import { useMutation, useQueryClient } from '@tanstack/react-query'

const companySchema = z.object({
    name: z.string().min(1, 'El nombre es requerido'),
    cuit: z.string().min(11, 'El CUIT debe tener al menos 11 caracteres'),
    fiscal_condition: z.enum(['RI', 'MONOTRIBUTO', 'EXENTO', 'CONSUMIDOR_FINAL']),
    address: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().email('Email inválido').or(z.literal('')).optional(),
    afip_point_of_sale: z.number().int().min(1, 'Punto de venta inválido').optional().or(z.nan()),
    imagen: z.string().url('URL inválida').or(z.literal('')).optional(),
    is_active: z.boolean(),
})

type CompanyFormData = z.infer<typeof companySchema>

interface CompanyFormModalProps {
    isOpen: boolean
    onClose: () => void
    company?: Company | null
}

export function CompanyFormModal({ isOpen, onClose, company }: CompanyFormModalProps) {
    const queryClient = useQueryClient()
    const isEditing = !!company
    const [isViewMode, setIsViewMode] = useState(true)

    const {
        register,
        handleSubmit,
        reset,
        control,
        setValue,
        formState: { errors, isSubmitting },
    } = useForm<CompanyFormData>({
        resolver: zodResolver(companySchema),
        defaultValues: {
            name: '',
            cuit: '',
            fiscal_condition: 'RI',
            imagen: '',
            is_active: true,
        },
    })

    useEffect(() => {
        if (company && isOpen) {
            setIsViewMode(true)
            reset({
                name: company.name,
                cuit: company.cuit,
                fiscal_condition: company.fiscal_condition,
                address: company.address || '',
                phone: company.phone || '',
                email: company.email || '',
                afip_point_of_sale: company.afip_point_of_sale || undefined,
                imagen: company.imagen || '',
                is_active: company.is_active,
            })
        } else if (!company && isOpen) {
            setIsViewMode(false)
            reset({
                name: '',
                cuit: '',
                fiscal_condition: 'RI',
                address: '',
                phone: '',
                email: '',
                afip_point_of_sale: undefined,
                imagen: '',
                is_active: true,
            })
        }
    }, [company, isOpen, reset])

    const mutation = useMutation({
        mutationFn: (data: CompanyFormData) => {
            // Strip NaN from point of sale
            if (Number.isNaN(data.afip_point_of_sale)) {
                delete data.afip_point_of_sale
            }
            if (isEditing && company) {
                return api.companies.update(company.id, data)
            }
            return api.companies.create(data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['companies'] })
            onClose()
        },
        onError: (error: any) => {
            console.error('Error saving company:', error.response?.data || error.message)
            alert('Error al guardar la empresa. Por favor revise los datos.')
        }
    })

    const onSubmit = (data: CompanyFormData) => {
        mutation.mutate(data)
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
                    <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity" />
                </Transition.Child>

                <div className="fixed inset-0 z-10 overflow-y-auto">
                    <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                            enterTo="opacity-100 translate-y-0 sm:scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        >
                            <Dialog.Panel className="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-2xl border border-gray-100">
                                <div className="absolute right-0 top-0 pr-4 pt-4 flex items-center gap-2">
                                    {isEditing && isViewMode && (
                                        <button
                                            type="button"
                                            onClick={() => setIsViewMode(false)}
                                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-1.5 text-sm font-semibold"
                                        >
                                            <PencilSquareIcon className="w-5 h-5" />
                                            <span>Editar</span>
                                        </button>
                                    )}
                                    <button
                                        type="button"
                                        className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                        onClick={onClose}
                                    >
                                        <span className="sr-only">Cerrar</span>
                                        <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                                    </button>
                                </div>
                                
                                <form onSubmit={handleSubmit(onSubmit)}>
                                    <div className="px-6 pb-6 pt-5 sm:p-8 sm:pb-6">
                                        <Dialog.Title as="h3" className="text-xl font-semibold leading-6 text-gray-900 mb-6">
                                            {isEditing ? (isViewMode ? 'Detalles de la Empresa' : 'Editar Empresa') : 'Nueva Empresa'}
                                        </Dialog.Title>
                                        
                                        {isViewMode && company ? (
                                            <div className="space-y-8 animate-fade-in">
                                                {/* Hero Logo Section */}
                                                <div className="flex flex-col items-center">
                                                    <div className="w-full max-w-md h-32 rounded-2xl border-2 border-white shadow-sm overflow-hidden bg-white shrink-0 flex items-center justify-center p-4">
                                                        {company.imagen ? (
                                                            <img 
                                                                src={company.imagen} 
                                                                alt={company.name} 
                                                                className="w-full h-full object-contain" 
                                                            />
                                                        ) : (
                                                            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-3xl font-bold">
                                                                {company.name.substring(0, 2).toUpperCase()}
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="mt-4 text-center">
                                                        <h2 className="text-2xl font-bold text-gray-900">{company.name}</h2>
                                                        <div className="mt-1 flex items-center justify-center gap-2">
                                                            <span className="text-sm font-mono text-gray-500">CUIT: {company.cuit}</span>
                                                            <span className={clsx(
                                                                "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset",
                                                                company.is_active 
                                                                    ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20" 
                                                                    : "bg-gray-50 text-gray-600 ring-gray-500/10"
                                                            )}>
                                                                {company.is_active ? 'Activa' : 'Inactiva'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-8 border-t border-gray-100 pt-8">
                                                    <div>
                                                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Información Fiscal</h4>
                                                        <div className="space-y-3">
                                                            <div>
                                                                <p className="text-xs text-gray-500 mb-0.5">Condición Frente al IVA</p>
                                                                <p className="text-sm font-medium text-gray-900">
                                                                    {company.fiscal_condition === 'RI' ? 'Responsable Inscripto' : 
                                                                     company.fiscal_condition === 'MONOTRIBUTO' ? 'Monotributo' : 
                                                                     company.fiscal_condition === 'EXENTO' ? 'Exento' : company.fiscal_condition}
                                                                </p>
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500 mb-0.5">Punto de Venta</p>
                                                                <p className="text-sm font-medium text-gray-900">{company.afip_point_of_sale || '—'}</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Contacto</h4>
                                                        <div className="space-y-3">
                                                            <div>
                                                                <p className="text-xs text-gray-500 mb-0.5">Email</p>
                                                                <p className="text-sm font-medium text-gray-900 break-all">{company.email || '—'}</p>
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500 mb-0.5">Teléfono</p>
                                                                <p className="text-sm font-medium text-gray-900">{company.phone || '—'}</p>
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500 mb-0.5">Dirección</p>
                                                                <p className="text-sm font-medium text-gray-900">{company.address || '—'}</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 gap-y-5 gap-x-4 sm:grid-cols-2">
                                                <div className="sm:col-span-2">
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Razón Social
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('name')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                        placeholder="Ej: Guías Locales SRL"
                                                    />
                                                    {errors.name && <p className="mt-1 text-xs text-rose-500">{errors.name.message}</p>}
                                                </div>

                                                <div className="sm:col-span-2">
                                                    <Controller
                                                        control={control}
                                                        name="imagen"
                                                        render={({ field }) => (
                                                            <ImageUpload
                                                                value={field.value}
                                                                onChange={field.onChange}
                                                                label="Imagen / Logo de la Empresa"
                                                            />
                                                        )}
                                                    />
                                                    {errors.imagen && <p className="mt-1 text-xs text-rose-500">{errors.imagen.message}</p>}
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        CUIT
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('cuit')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                        placeholder="30-12345678-9"
                                                    />
                                                    {errors.cuit && <p className="mt-1 text-xs text-rose-500">{errors.cuit.message}</p>}
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Condición Frente al IVA
                                                    </label>
                                                    <select
                                                        {...register('fiscal_condition')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    >
                                                        <option value="RI">Responsable Inscripto</option>
                                                        <option value="MONOTRIBUTO">Monotributo</option>
                                                        <option value="EXENTO">Exento</option>
                                                    </select>
                                                    {errors.fiscal_condition && <p className="mt-1 text-xs text-rose-500">{errors.fiscal_condition.message}</p>}
                                                </div>

                                                <div className="sm:col-span-2">
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Punto de Venta AFIP
                                                    </label>
                                                    <input
                                                        type="number"
                                                        {...register('afip_point_of_sale', { valueAsNumber: true })}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                        placeholder="Ej: 4"
                                                    />
                                                </div>

                                                <div className="sm:col-span-2 mt-2 pt-4 border-t border-gray-100">
                                                    <h4 className="text-sm font-semibold text-gray-900 mb-4">Información de Contacto</h4>
                                                </div>

                                                <div className="sm:col-span-2">
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Dirección
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('address')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Email
                                                    </label>
                                                    <input
                                                        type="email"
                                                        {...register('email')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Teléfono
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('phone')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>
                                                
                                                <div className="sm:col-span-2 mt-4 flex items-center">
                                                    <input
                                                        id="is_active"
                                                        type="checkbox"
                                                        {...register('is_active')}
                                                        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                                                    />
                                                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                                                        Empresa Activa
                                                    </label>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    <div className="bg-gray-50 px-4 py-4 sm:flex sm:flex-row-reverse sm:px-6 rounded-b-2xl border-t border-gray-100">
                                        {isViewMode ? (
                                            <button
                                                type="button"
                                                className="inline-flex w-full justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:w-auto transition-colors"
                                                onClick={onClose}
                                            >
                                                Cerrar
                                            </button>
                                        ) : (
                                            <>
                                                <button
                                                    type="submit"
                                                    disabled={isSubmitting || mutation.isPending}
                                                    className="inline-flex w-full justify-center rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
                                                >
                                                    {(isSubmitting || mutation.isPending) ? 'Guardando...' : 'Guardar Empresa'}
                                                </button>
                                                <button
                                                    type="button"
                                                    className="mt-3 inline-flex w-full justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
                                                    onClick={() => isEditing ? setIsViewMode(true) : onClose()}
                                                >
                                                    {isEditing ? 'Volver' : 'Cancelar'}
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </form>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition.Root>
    )
}
