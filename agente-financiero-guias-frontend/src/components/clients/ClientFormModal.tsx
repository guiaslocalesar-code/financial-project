'use client'

import { Fragment, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { ImageUpload } from '../common/ImageUpload'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/services/api'
import type { Client } from '@/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useHoldingContext } from '@/context/HoldingContext'
import { PlusIcon, TrashIcon, CalendarIcon, PencilSquareIcon, BriefcaseIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'
import { ClientService } from '@/types'
import { clsx } from 'clsx'

const clientSchema = z.object({
    id: z.string().optional(),
    name: z.string().min(1, 'El nombre/razón social es requerido'),
    cuit_cuil_dni: z.string().min(8, 'Debe tener al menos 8 caracteres'),
    fiscal_condition: z.enum(['RI', 'MONOTRIBUTO', 'EXENTO', 'CONSUMIDOR_FINAL']),
    address: z.string().optional(),
    city: z.string().optional(),
    province: z.string().optional(),
    zip_code: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().email('Email inválido').or(z.literal('')).optional(),
    imagen: z.string().url('URL inválida').or(z.literal('')).optional(),
    is_active: z.boolean(),
    services: z.array(z.object({
        id: z.string().optional(),
        service_id: z.string().min(1, 'El servicio es requerido'),
        monthly_fee: z.coerce.number().min(0, 'El monto debe ser positivo'),
        currency: z.enum(['ARS', 'USD']),
        start_date: z.string().min(1, 'La fecha de inicio es requerida'),
    })).optional(),
})

type ClientFormData = z.infer<typeof clientSchema>

interface ClientFormModalProps {
    isOpen: boolean
    onClose: () => void
    client?: Client | null
}

export function ClientFormModal({ isOpen, onClose, client }: ClientFormModalProps) {
    const queryClient = useQueryClient()
    const { selectedCompany } = useHoldingContext()
    const [isViewMode, setIsViewMode] = useState(true)
    const isEditing = !!client

    const {
        register,
        handleSubmit,
        reset,
        control,
        formState: { errors, isSubmitting },
    } = useForm<any>({
        resolver: zodResolver(clientSchema),
        defaultValues: {
            id: '',
            name: '',
            cuit_cuil_dni: '',
            fiscal_condition: 'CONSUMIDOR_FINAL',
            imagen: '',
            is_active: true,
            services: []
        },
    })

    const { fields, append, remove } = useFieldArray({
        control,
        name: 'services',
    })

    const servicesErrors = errors.services as any

    // Fetch available services
    const { data: availableServices } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as any[]
        },
        enabled: !!selectedCompany && isOpen,
    })

    // Fetch assigned services for the client (for Detail View)
    const { data: clientServices, isLoading: isLoadingCS } = useQuery({
        queryKey: ['clientServices', client?.id],
        queryFn: async () => {
            if (!client?.id) return []
            const res = await api.clientServices.list(client.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as ClientService[]
        },
        enabled: !!client?.id && isOpen,
    })

    useEffect(() => {
        if (client && isOpen) {
            reset({
                id: client.id,
                name: client.name,
                cuit_cuil_dni: client.cuit_cuil_dni,
                fiscal_condition: client.fiscal_condition as any,
                address: client.address || '',
                phone: client.phone || '',
                email: client.email || '',
                imagen: client.imagen || '',
                is_active: client.is_active,
            })
            setIsViewMode(true)
        } else if (!client && isOpen) {
            reset({
                id: '',
                name: '',
                cuit_cuil_dni: '',
                fiscal_condition: 'CONSUMIDOR_FINAL',
                address: '',
                phone: '',
                email: '',
                imagen: '',
                is_active: true,
                services: []
            })
            setIsViewMode(false)
        }
    }, [client, isOpen, reset])

    useEffect(() => {
        if (client && isOpen && !isViewMode && clientServices) {
            const mappedServices = clientServices.map(cs => ({
                id: cs.id,
                service_id: cs.service_id,
                monthly_fee: cs.monthly_fee,
                currency: cs.currency || 'ARS',
                start_date: String(cs.start_date).split('T')[0]
            }))
            reset((formValues: any) => ({ ...formValues, services: mappedServices }))
        }
    }, [client, isOpen, isViewMode, clientServices, reset])

    const mutation = useMutation({
        mutationFn: (data: ClientFormData) => {
            if (!selectedCompany) throw new Error('No company selected')
            // Remove services from payload before sending to Client API
            const { services, ...clientData } = data
            
            // Sanitize payload
            const payload = { 
                ...clientData, 
                company_id: selectedCompany.id,
                id: data.id?.trim() || undefined,
                cuit_cuil_dni: String(data.cuit_cuil_dni).replace('.0', '').trim(),
                address: data.address?.trim() || null,
                email: data.email?.trim() || null,
                imagen: data.imagen?.trim() || null,
                phone: data.phone?.trim() || null,
                city: (data as any).city?.trim() || null,
                province: (data as any).province?.trim() || null,
                zip_code: (data as any).zip_code?.trim() || null,
            }
            
            if (isEditing && client) {
                console.log('Payload enviado:', JSON.stringify(payload))
                return api.clients.update(client.id, payload)
            }
            console.log('Payload enviado:', JSON.stringify(payload))
            return api.clients.create(payload)
        },
        onSuccess: async (response, variables) => {
            const createdClient = response.data.data || response.data
            const clientId = createdClient.id || (isEditing && client?.id)

            const submittedServiceIds = (variables.services || []).map(s => s.id).filter(Boolean)
            const originalServiceIds = (clientServices || []).map(cs => cs.id)
            
            // Find deleted services
            const deletedServiceIds = originalServiceIds.filter(id => !submittedServiceIds.includes(id))
            
            // Execute deletions
            for (const id of deletedServiceIds) {
                try {
                    await api.clientServices.remove(id)
                } catch (err) {
                    console.error(`Error deleting service ${id}:`, err)
                }
            }

            // Assign or update services
            if (variables.services && variables.services.length > 0) {
                for (const service of variables.services) {
                    try {
                        if (service.id) {
                            await api.clientServices.update(service.id, {
                                service_id: service.service_id,
                                monthly_fee: service.monthly_fee,
                                currency: service.currency,
                                start_date: service.start_date
                            })
                        } else {
                            await api.clientServices.assign(clientId, {
                                service_id: service.service_id,
                                monthly_fee: service.monthly_fee,
                                currency: service.currency,
                                start_date: service.start_date
                            })
                        }
                    } catch (err) {
                        console.error(`Error saving service ${service.service_id}:`, err)
                        alert(`Error al guardar un servicio.`)
                    }
                }
            }

            queryClient.invalidateQueries({ queryKey: ['clients', selectedCompany?.id] })
            onClose()
        },
        onError: (error: any) => {
            console.error('Error saving client:', error.response?.data || error.message)
            alert('Error al guardar el cliente. Por favor revise los datos.')
        }
    })

    const onSubmit = (data: any) => {
        mutation.mutate(data)
    }

    if (!selectedCompany) return null

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
                                            {isEditing ? (isViewMode ? 'Detalles del Cliente' : 'Editar Cliente') : 'Nuevo Cliente'}
                                        </Dialog.Title>
                                        
                                        {isViewMode && client ? (
                                            <div className="space-y-6">
                                                {/* Detail View */}
                                                <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-3 gap-x-6">
                                                    <div className="sm:col-span-3 flex flex-col items-center gap-4 p-8 rounded-[2.5rem] bg-gray-50/50 border border-gray-100 shadow-inner">
                                                        <div className="w-full max-w-lg h-56 rounded-3xl border-4 border-white shadow-xl overflow-hidden bg-white shrink-0 flex items-center justify-center group transition-all hover:shadow-2xl">
                                                            {client.imagen ? (
                                                                <img src={client.imagen} alt={client.name} className="w-full h-full object-cover transition-transform group-hover:scale-105" />
                                                            ) : (
                                                                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-5xl font-black">
                                                                    {client.name.substring(0, 2).toUpperCase()}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>

                                                    <div className="sm:col-span-1 space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-center">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID / Referencia</p>
                                                        <p className="text-sm font-black text-gray-900 leading-tight break-all">{client.id}</p>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-center">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Nombre / Razón Social</p>
                                                        <p className="text-sm font-black text-gray-900 leading-tight">{client.name}</p>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-center">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Identificación</p>
                                                        <p className="text-sm font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100 inline-block font-mono self-start">
                                                            {String(client.cuit_cuil_dni).replace('.0', '')}
                                                        </p>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-center">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Estado</p>
                                                        <div>
                                                            <span className={clsx(
                                                                "inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider shadow-sm",
                                                                client.is_active ? "bg-emerald-500 text-white" : "bg-gray-400 text-white"
                                                            )}>
                                                                {client.is_active ? 'Activo' : 'Inactivo'}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Condición Fiscal</p>
                                                        <p className="text-sm font-bold text-gray-900">
                                                            {client.fiscal_condition === 'CONSUMIDOR_FINAL' ? 'Consumidor Final' : 
                                                             client.fiscal_condition === 'RI' ? 'Responsable Inscripto' : 
                                                             client.fiscal_condition === 'MONOTRIBUTO' ? 'Monotributo' : client.fiscal_condition}
                                                        </p>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Email</p>
                                                        <p className="text-sm font-bold text-gray-900 break-all">{client.email || '—'}</p>
                                                    </div>

                                                    <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Teléfono</p>
                                                        <p className="text-sm font-bold text-gray-900">{client.phone || '—'}</p>
                                                    </div>

                                                    <div className="sm:col-span-3 space-y-1 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Dirección completa</p>
                                                        <p className="text-sm font-bold text-gray-900">
                                                            {client.address || ''} {client.city ? ` - ${client.city}` : ''} 
                                                            {client.province ? `, ${client.province}` : ''}
                                                            {!client.address && !client.city && !client.province && '—'}
                                                        </p>
                                                    </div>
                                                </div>

                                                <div className="pt-6 border-t border-gray-100">
                                                    <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                                                        <BriefcaseIcon className="w-5 h-5 text-teal-600" />
                                                        Servicios Contratados
                                                    </h4>
                                                    {isLoadingCS ? (
                                                        <div className="flex justify-center py-4">
                                                            <div className="w-6 h-6 border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                                                        </div>
                                                    ) : !clientServices || clientServices.length === 0 ? (
                                                        <div className="p-4 rounded-xl border-2 border-dashed border-gray-100 text-center">
                                                            <p className="text-xs text-gray-400 italic">No tiene servicios asignados.</p>
                                                        </div>
                                                    ) : (
                                                        <div className="space-y-2">
                                                            {clientServices.map((cs) => (
                                                                <div key={cs.id} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 border border-gray-100">
                                                                    <div>
                                                                        <p className="text-sm font-semibold text-gray-900">{cs.service?.name || cs.service_id}</p>
                                                                        <p className="text-[10px] text-gray-500">Desde: {new Date(cs.start_date).toLocaleDateString()}</p>
                                                                    </div>
                                                                    <div className="text-right">
                                                                        <p className="text-sm font-bold text-teal-700">${cs.monthly_fee.toLocaleString('es-AR')}</p>
                                                                        <p className="text-[10px] text-gray-400">{cs.currency}</p>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 gap-y-5 gap-x-4 sm:grid-cols-2">
                                            
                                            <div className="sm:col-span-2">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    ID del Cliente (Opcional)
                                                </label>
                                                <input
                                                    type="text"
                                                    {...register('id')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    placeholder="Ej: CLI-001 (se autogenera si se deja vacío)"
                                                />
                                                {errors.id && <p className="mt-1 text-xs text-rose-500">{(errors.id as any).message}</p>}
                                            </div>

                                            <div className="sm:col-span-2">
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Nombre / Razón Social
                                                </label>
                                                <input
                                                    type="text"
                                                    {...register('name')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    placeholder="Ej: Juan Pérez"
                                                />
                                                {errors.name && <p className="mt-1 text-xs text-rose-500">{(errors.name as any).message}</p>}
                                            </div>

                                            <div className="sm:col-span-2">
                                                <Controller
                                                    control={control}
                                                    name="imagen"
                                                    render={({ field }) => (
                                                        <ImageUpload
                                                            value={field.value}
                                                            onChange={field.onChange}
                                                            label="Imagen / Logo del Cliente"
                                                        />
                                                    )}
                                                />
                                                {errors.imagen && <p className="mt-1 text-xs text-rose-500">{(errors.imagen as any).message}</p>}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    CUIT / CUIL / DNI
                                                </label>
                                                <input
                                                    type="text"
                                                    {...register('cuit_cuil_dni')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    placeholder="20-12345678-9"
                                                />
                                                {errors.cuit_cuil_dni && <p className="mt-1 text-xs text-rose-500">{(errors.cuit_cuil_dni as any).message}</p>}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Condición Fiscal
                                                </label>
                                                <select
                                                    {...register('fiscal_condition')}
                                                    className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                >
                                                    <option value="CONSUMIDOR_FINAL">Consumidor Final</option>
                                                    <option value="MONOTRIBUTO">Monotributo</option>
                                                    <option value="RI">Responsable Inscripto</option>
                                                    <option value="EXENTO">Exento</option>
                                                </select>
                                                {errors.fiscal_condition && <p className="mt-1 text-xs text-rose-500">{(errors.fiscal_condition as any).message}</p>}
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

                                            <div className="sm:col-span-2 grid grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Ciudad
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('city')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Provincia
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('province')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                                    />
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium leading-6 text-gray-900">
                                                    Código Postal
                                                </label>
                                                <input
                                                    type="text"
                                                    {...register('zip_code')}
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
                                                {errors.email && <p className="mt-1 text-xs text-rose-500">{(errors.email as any).message}</p>}
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
                                                    id="is_active_client"
                                                    type="checkbox"
                                                    {...register('is_active')}
                                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                                                />
                                                <label htmlFor="is_active_client" className="ml-2 block text-sm text-gray-900">
                                                    Cliente Activo
                                                </label>
                                            </div>

                                            {/* Services Section */}
                                            <div className="sm:col-span-2 mt-6 pt-6 border-t border-gray-100">
                                                <div className="flex items-center justify-between mb-4">
                                                    <h4 className="text-sm font-semibold text-gray-900">Servicios contratados</h4>
                                                        <button
                                                            type="button"
                                                            onClick={() => append({ service_id: '', monthly_fee: 0, currency: 'ARS', start_date: new Date().toISOString().split('T')[0] })}
                                                            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700"
                                                        >
                                                            <PlusIcon className="w-4 h-4" />
                                                            Agregar servicio
                                                        </button>
                                                    </div>

                                                    <div className="space-y-4">
                                                        {fields.map((field, index) => (
                                                            <div key={field.id} className="relative p-4 rounded-xl bg-gray-50 border border-gray-100 group">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => remove(index)}
                                                                    className="absolute top-2 right-2 p-1 text-gray-400 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                                >
                                                                    <TrashIcon className="w-4 h-4" />
                                                                </button>
                                                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                                    <div>
                                                                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
                                                                            Servicio
                                                                        </label>
                                                                        <select
                                                                            {...register(`services.${index}.service_id` as const)}
                                                                            className="block w-full rounded-lg border-gray-300 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                                                                        >
                                                                            <option value="">Seleccionar...</option>
                                                                            {availableServices?.map(s => (
                                                                                <option key={s.id} value={s.id}>{s.name}</option>
                                                                            ))}
                                                                        </select>
                                                                        {servicesErrors?.[index]?.service_id && (
                                                                            <p className="mt-1 text-[10px] text-rose-500">{servicesErrors[index]?.service_id?.message}</p>
                                                                        )}
                                                                    </div>
                                                                    <div>
                                                                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
                                                                            Fecha Inicio
                                                                        </label>
                                                                        <input
                                                                            type="date"
                                                                            {...register(`services.${index}.start_date` as const)}
                                                                            className="block w-full rounded-lg border-gray-300 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                                                                        />
                                                                        {servicesErrors?.[index]?.start_date && (
                                                                            <p className="mt-1 text-[10px] text-rose-500">{servicesErrors[index]?.start_date?.message}</p>
                                                                        )}
                                                                    </div>
                                                                    <div>
                                                                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
                                                                            Abono Mensual
                                                                        </label>
                                                                        <div className="relative">
                                                                            <input
                                                                                type="number"
                                                                                step="0.01"
                                                                                {...register(`services.${index}.monthly_fee` as const)}
                                                                                className="block w-full rounded-lg border-gray-300 py-2 pr-16 text-sm focus:ring-blue-500 focus:border-blue-500"
                                                                                placeholder="0.00"
                                                                            />
                                                                            <div className="absolute inset-y-0 right-0 flex items-center">
                                                                                <select
                                                                                    {...register(`services.${index}.currency` as const)}
                                                                                    className="h-full rounded-r-lg border-transparent bg-transparent py-0 pl-2 pr-7 text-gray-500 text-xs focus:ring-0 focus:border-transparent"
                                                                                >
                                                                                    <option>ARS</option>
                                                                                    <option>USD</option>
                                                                                </select>
                                                                            </div>
                                                                        </div>
                                                                        {servicesErrors?.[index]?.monthly_fee && (
                                                                            <p className="mt-1 text-[10px] text-rose-500">{servicesErrors[index]?.monthly_fee?.message}</p>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    {fields.length === 0 && (
                                                        <div className="text-center py-6 px-4 border-2 border-dashed border-gray-100 rounded-xl">
                                                            <p className="text-xs text-gray-400 italic">No se han asignado servicios al cliente.</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            </div>
                                        )}
                                    </div>
                                    <div className="bg-gray-50 px-4 py-4 sm:flex sm:flex-row-reverse sm:px-6 rounded-b-2xl border-t border-gray-100">
                                        {!isViewMode ? (
                                            <>
                                                <button
                                                    type="submit"
                                                    disabled={isSubmitting || mutation.isPending}
                                                    className="inline-flex w-full justify-center rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
                                                >
                                                    {(isSubmitting || mutation.isPending) ? 'Guardando...' : 'Guardar Cliente'}
                                                </button>
                                                <button
                                                    type="button"
                                                    className="mt-3 inline-flex w-full justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
                                                    onClick={isEditing ? () => setIsViewMode(true) : onClose}
                                                >
                                                    {isEditing ? 'Volver' : 'Cancelar'}
                                                </button>
                                            </>
                                        ) : (
                                            <button
                                                type="button"
                                                className="inline-flex w-full justify-center rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:w-auto transition-colors"
                                                onClick={onClose}
                                            >
                                                Cerrar
                                            </button>
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
