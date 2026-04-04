'use client'

import { Fragment, useEffect, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { 
    XMarkIcon, 
    PencilSquareIcon,
    GlobeAltIcon,
    MagnifyingGlassIcon,
    CameraIcon,
    PhotoIcon,
    ChartBarIcon,
    MusicalNoteIcon,
    CommandLineIcon,
    WindowIcon,
    MegaphoneIcon,
    ChatBubbleLeftRightIcon,
    ShoppingCartIcon,
    VideoCameraIcon,
    WrenchScrewdriverIcon,
    SparklesIcon
} from '@heroicons/react/24/outline'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/services/api'
import type { Service } from '@/types'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { clsx } from 'clsx'

const serviceSchema = z.object({
    name: z.string().min(1, 'El nombre es requerido'),
    description: z.string().optional(),
    icon: z.string().optional(),
    is_active: z.boolean(),
})

type ServiceFormData = z.infer<typeof serviceSchema>

interface ServiceFormModalProps {
    isOpen: boolean
    onClose: () => void
    service?: Service | null
    companyId: string
}

const ICON_OPTIONS = [
    { 
        id: 'google', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.07-3.71 1.07-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.11c-.22-.66-.35-1.39-.35-2.11s.13-1.45.35-2.11V7.05H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.95l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.05l3.66 2.84c.87-2.6 3.3-4.51 6.16-4.51z"/>
            </svg>
        ), 
        color: '', 
        bg: 'bg-white', 
        label: 'Google' 
    },
    { 
        id: 'meta', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#0668E1" d="M15.42 5.92c-1.35 0-2.3.82-2.3 2.5v1.48h2.3l-.3 2.15h-2v5.95H10.8V12.05h-1.6v-2.15h1.6V8.12c0-2.2 1.25-3.4 3.2-3.4.95 0 1.8.07 2.05.1v2.1h-1.63z" />
            </svg>
        ),
        color: '',
        bg: 'bg-[#0668E1]/5', 
        label: 'Facebook' 
    },
    { 
        id: 'instagram', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <radialGradient id="ig-grad" cx="24.5%" cy="92%" r="130%" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#fdf497"/>
                    <stop offset="5%" stopColor="#fdf497"/>
                    <stop offset="45%" stopColor="#fd5949"/>
                    <stop offset="60%" stopColor="#d6249f"/>
                    <stop offset="90%" stopColor="#285AEB"/>
                </radialGradient>
                <path fill="url(#ig-grad)" d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.42a4.8 4.8 0 0 1 1.78 1.16c.49.49.88 1.05 1.16 1.78.17.42.36 1.05.42 2.22.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.06 1.17-.25 1.8-.42 2.23a4.8 4.8 0 0 1-1.16 1.78 4.8 4.8 0 0 1-1.78 1.16c-.42.17-1.05.36-2.22.42-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.42a4.8 4.8 0 0 1-1.78-1.16 4.8 4.8 0 0 1-1.16-1.78c-.17-.42-.36-1.05-.42-2.22-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.06-1.17.25-1.8.42-2.23a4.8 4.8 0 0 1 1.16-1.78 4.8 4.8 0 0 1 1.78-1.16c.42-.17 1.05-.36 2.22-.42 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.77.13 4.9.33 4.14.63a7 7 0 0 0-2.52 1.64A7 7 0 0 0 .63 4.14C.33 4.9.13 5.77.07 7.05 0 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.28.26 2.15.56 2.91a7 7 0 0 0 1.64 2.52 7 7 0 0 0 2.52 1.64c.76.3 1.63.5 2.91.56 1.28.06 1.69.07 4.95.07s3.67-.01 4.95-.07c1.28-.06 2.15-.26 2.91-.56a7 7 0 0 0 2.52-1.64 7 7 0 0 0 1.64-2.52c.3-.76.5-1.63.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.28-.26-2.15-.56-2.91a7 7 0 0 0-1.64-2.52A7 7 0 0 0 19.86.63c-.76-.3-1.63-.5-2.91-.56C15.67.01 15.26 0 12 0z"/>
                <path fill="url(#ig-grad)" d="M12 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32m0 10.16a4 4 0 1 1 0-8 4 4 0 0 1 0 8m6.4-10a1.44 1.44 0 1 1-2.88 0 1.44 1.44 0 0 1 2.88 0"/>
            </svg>
        ),
        color: '',
        bg: 'bg-white', 
        label: 'Instagram' 
    },
    { 
        id: 'tiktok', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#000000" d="M12.53 0c.26 0 .5.01.75.03v5.04c-.11-.01-.23-.02-.34-.02-2.18 0-3.95 1.77-3.95 3.95v11.05c0 2.18-1.77 3.95-3.95 3.95-2.18 0-3.95-1.77-3.95-3.95s1.77-3.95 3.95-3.95c.57 0 1.11.12 1.6.34v-5.2c-.52-.1-1.05-.15-1.6-.15C2.29 11.09 0 13.38 0 16.2c0 2.82 2.29 5.11 5.11 5.11 2.82 0 5.11-2.29 5.11-5.11V8.66c1.65 1.15 3.65 1.83 5.81 1.83V5.45c-1.39 0-2.67-.47-3.7-1.25V0h.2z" />
            </svg>
        ),
        color: '',
        bg: 'bg-white', 
        label: 'TikTok' 
    },
    { 
        id: 'linkedin', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#0077B5" d="M19 0h-14c-2.76 0-5 2.24-5 5v14c0 2.76 2.24 5 5 5h14c2.76 0 5-2.24 5-5v-14c0-2.76-2.24-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.27c-.97 0-1.75-.78-1.75-1.75s.78-1.75 1.75-1.75 1.75.78 1.75 1.75-.78 1.75-1.75 1.75zm13.5 12.27h-3v-5.6c0-1.34-.03-3.06-1.86-3.06-1.87 0-2.15 1.46-2.15 2.96v5.7h-3v-11h2.88v1.5h.04c.4-.76 1.38-1.56 2.85-1.56 3.04 0 3.6 2 3.6 4.6v6.46z" />
            </svg>
        ),
        color: '',
        bg: 'bg-[#0077B5]/5', 
        label: 'LinkedIn' 
    },
    { 
        id: 'youtube', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#FF0000" d="M23.5 6.1s-.2-1.6-.9-2.3c-.9-1-1.9-1-2.4-1.1C16.8 2.5 12 2.5 12 2.5s-4.8 0-8.2.2c-.5.1-1.5.1-2.4 1.1-.7.7-.9 2.3-.9 2.3S.3 8.1.3 10c0 1.9.2 3.9.2 3.9s.2 1.6.9 2.3c.9 1 2.1.9 2.6 1 2 .2 8 .2 8 .2s4.8 0 8.2-.2c.5-.1 1.5-.1 2.4-1.1.7-.7.9-2.3.9-2.3s.2-2 .2-3.9c-.1-1.9-.3-3.9-.3-3.9zM9.5 14.2V7.4l6.3 3.4-6.3 3.4z" />
            </svg>
        ),
        color: '',
        bg: 'bg-red-50', 
        label: 'YouTube' 
    },
    { 
        id: 'whatsapp', 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#25D366" d="M12.03 0C5.39 0 0 5.39 0 12.03c0 2.11.55 4.17 1.6 5.96L0 24l6.19-1.62c1.72 1.05 3.82 1.6 5.8 1.6 6.64 0 12.03-5.39 12.03-12.03S18.66 0 12.03 0zm5.95 17.02c-.25.7-.85 1.25-1.55 1.55-.4.2-1 .4-2.5-.2-1.5-.6-2.5-1.5-3.5-2.5s-1.9-2-2.5-3.5c-.6-1.5-.4-2.1-.2-2.5.3-.7.88-1.3 1.55-1.55.25-.1.55-.1.85.1l1 2 .5 1.5c.1.3 0 .6-.2.9l-1 1c-.1.1-.2.3-.1.5.1.2.3.4.5.6 1.2 1.2 2.4 2.4 3.6 3.6.2.2.4.4.6.5.2.1.4 0 .5-.1l1-1c.3-.2.6-.3.9-.2l1.5.5 2 1c.2.3.2.6.1.85z" />
            </svg>
        ),
        color: '',
        bg: 'bg-emerald-50', 
        label: 'WhatsApp' 
    },
    { id: 'photo', icon: PhotoIcon, color: 'text-amber-500', bg: 'bg-amber-50', label: 'Fotografía' },
    { id: 'video', icon: VideoCameraIcon, color: 'text-rose-600', bg: 'bg-rose-50', label: 'Video / Reel' },
    { id: 'data', icon: ChartBarIcon, color: 'text-emerald-600', bg: 'bg-emerald-50', label: 'Data / Analytics' },
    { id: 'web', icon: WindowIcon, color: 'text-cyan-600', bg: 'bg-cyan-50', label: 'Web / Landing' },
    { id: 'dev', icon: CommandLineIcon, color: 'text-gray-700', bg: 'bg-gray-100', label: 'Development' },
    { id: 'shop', icon: ShoppingCartIcon, color: 'text-orange-600', bg: 'bg-orange-50', label: 'E-commerce' },
    { id: 'ads', icon: MegaphoneIcon, color: 'text-red-500', bg: 'bg-red-50', label: 'Ads / Marketing' },
    { id: 'social', icon: ChatBubbleLeftRightIcon, color: 'text-violet-600', bg: 'bg-violet-50', label: 'Community' },
    { id: 'tech', icon: WrenchScrewdriverIcon, color: 'text-slate-600', bg: 'bg-slate-100', label: 'Mantenimiento' },
    { id: 'extra', icon: SparklesIcon, color: 'text-purple-600', bg: 'bg-purple-50', label: 'Extra / Otros' },
]

export function ServiceFormModal({ isOpen, onClose, service, companyId }: ServiceFormModalProps) {
    const queryClient = useQueryClient()
    const isEditing = !!service
    const [isViewMode, setIsViewMode] = useState(true)

    const {
        register,
        handleSubmit,
        reset,
        watch,
        setValue,
        formState: { errors, isSubmitting },
    } = useForm<ServiceFormData>({
        resolver: zodResolver(serviceSchema),
        defaultValues: {
            name: '',
            description: '',
            icon: 'extra',
            is_active: true,
        },
    })

    const selectedIcon = watch('icon')

    useEffect(() => {
        if (service && isOpen) {
            setIsViewMode(true)
            reset({
                name: service.name,
                description: service.description || '',
                icon: service.icon || 'extra',
                is_active: service.is_active,
            })
        } else if (!service && isOpen) {
            setIsViewMode(false)
            reset({
                name: '',
                description: '',
                icon: 'extra',
                is_active: true,
            })
        }
    }, [service, isOpen, reset])

    const mutation = useMutation({
        mutationFn: (data: ServiceFormData) => {
            if (isEditing && service) {
                return api.services.update(service.id, data)
            }
            return api.services.create({ ...data, company_id: companyId })
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['services'] })
            onClose()
        }
    })

    const onSubmit = (data: ServiceFormData) => {
        mutation.mutate(data)
    }

    const SelectedIconComponent = ICON_OPTIONS.find(i => i.id === (service?.icon || selectedIcon))?.icon || SparklesIcon
    const selectedIconColor = ICON_OPTIONS.find(i => i.id === (service?.icon || selectedIcon))?.color || 'text-purple-600'
    const selectedIconBg = ICON_OPTIONS.find(i => i.id === (service?.icon || selectedIcon))?.bg || 'bg-purple-50'

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
                    <div className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity" />
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
                                        className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
                                        onClick={onClose}
                                    >
                                        <span className="sr-only">Cerrar</span>
                                        <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                                    </button>
                                </div>
                                
                                <form onSubmit={handleSubmit(onSubmit)}>
                                    <div className="px-6 pb-6 pt-5 sm:p-8 sm:pb-6">
                                        <Dialog.Title as="h3" className="text-xl font-semibold leading-6 text-gray-900 mb-6">
                                            {isEditing ? (isViewMode ? 'Detalles del Servicio' : 'Editar Servicio') : 'Nuevo Servicio'}
                                        </Dialog.Title>
                                        
                                        {isViewMode && service ? (
                                            <div className="space-y-8 animate-fade-in">
                                                <div className="flex flex-col items-center">
                                                    <div className={clsx(
                                                        "w-24 h-24 rounded-3xl flex items-center justify-center shadow-sm border-2 border-white",
                                                        selectedIconBg
                                                    )}>
                                                        <SelectedIconComponent className={clsx("w-12 h-12", selectedIconColor)} />
                                                    </div>
                                                    <div className="mt-4 text-center">
                                                        <h2 className="text-2xl font-bold text-gray-900 uppercase tracking-tight">{service.name}</h2>
                                                        <div className="mt-1 flex items-center justify-center gap-2">
                                                            <span className={clsx(
                                                                "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset",
                                                                service.is_active 
                                                                    ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20" 
                                                                    : "bg-gray-50 text-gray-600 ring-gray-500/10"
                                                            )}>
                                                                {service.is_active ? 'Activo' : 'Inactivo'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="border-t border-gray-100 pt-8">
                                                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Descripción del Servicio</h4>
                                                    <p className="text-gray-700 leading-relaxed bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                                                        {service.description || 'Sin descripción adicional.'}
                                                    </p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="space-y-6">
                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Nombre del Servicio
                                                    </label>
                                                    <input
                                                        type="text"
                                                        {...register('name')}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-600 sm:text-sm sm:leading-6"
                                                        placeholder="Ej: Google Ads, Gestión de Redes..."
                                                    />
                                                    {errors.name && <p className="mt-1 text-xs text-rose-500">{errors.name.message}</p>}
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900 mb-3">
                                                        Seleccionar Icono Sugerido
                                                    </label>
                                                    <div className="grid grid-cols-4 sm:grid-cols-7 gap-3">
                                                        {ICON_OPTIONS.map((opt) => (
                                                            <button
                                                                key={opt.id}
                                                                type="button"
                                                                onClick={() => setValue('icon', opt.id)}
                                                                className={clsx(
                                                                    "flex flex-col items-center justify-center p-2 rounded-xl transition-all border-2",
                                                                    selectedIcon === opt.id 
                                                                        ? "border-violet-600 bg-violet-50" 
                                                                        : "border-transparent hover:bg-gray-50 bg-gray-50/50"
                                                                )}
                                                            >
                                                                <opt.icon className={clsx("w-6 h-6", opt.color)} />
                                                                <span className="text-[10px] mt-1 text-gray-500 font-medium truncate w-full text-center">{opt.label}</span>
                                                            </button>
                                                        ))}
                                                    </div>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium leading-6 text-gray-900">
                                                        Descripción
                                                    </label>
                                                    <textarea
                                                        {...register('description')}
                                                        rows={4}
                                                        className="mt-2 block w-full rounded-xl border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-violet-600 sm:text-sm sm:leading-6"
                                                        placeholder="Detallá de qué trata este servicio..."
                                                    />
                                                </div>
                                                
                                                <div className="flex items-center">
                                                    <input
                                                        id="is_active"
                                                        type="checkbox"
                                                        {...register('is_active')}
                                                        className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-600"
                                                    />
                                                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                                                        Servicio Activo
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
                                                    className="inline-flex w-full justify-center rounded-xl bg-violet-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-violet-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
                                                >
                                                    {(isSubmitting || mutation.isPending) ? 'Guardando...' : 'Guardar Servicio'}
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
