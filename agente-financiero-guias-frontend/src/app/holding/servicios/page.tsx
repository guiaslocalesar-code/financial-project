'use client'

import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { 
    PlusIcon, 
    WrenchScrewdriverIcon,
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
    SparklesIcon
} from '@heroicons/react/24/outline'
import { Fragment } from 'react'
import { clsx } from 'clsx'
import { api } from '@/services/api'
import type { Service } from '@/types'
import { useHoldingContext } from '@/context/HoldingContext'
import { ServiceFormModal } from '@/components/services/ServiceFormModal'

const ICON_MAP: Record<string, any> = {
    google: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.07-3.71 1.07-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.11c-.22-.66-.35-1.39-.35-2.11s.13-1.45.35-2.11V7.05H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.95l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.05l3.66 2.84c.87-2.6 3.3-4.51 6.16-4.51z"/>
            </svg>
        ), 
        color: '', 
        bg: 'bg-white' 
    },
    meta: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#0668E1" d="M15.42 5.92c-1.35 0-2.3.82-2.3 2.5v1.48h2.3l-.3 2.15h-2v5.95H10.8V12.05h-1.6v-2.15h1.6V8.12c0-2.2 1.25-3.4 3.2-3.4.95 0 1.8.07 2.05.1v2.1h-1.63z" />
            </svg>
        ),
        color: '',
        bg: 'bg-[#0668E1]/5' 
    },
    instagram: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <radialGradient id="ig-grad-page" cx="24.5%" cy="92%" r="130%" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#fdf497"/>
                    <stop offset="5%" stopColor="#fdf497"/>
                    <stop offset="45%" stopColor="#fd5949"/>
                    <stop offset="60%" stopColor="#d6249f"/>
                    <stop offset="90%" stopColor="#285AEB"/>
                </radialGradient>
                <path fill="url(#ig-grad-page)" d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.42a4.8 4.8 0 0 1 1.78 1.16c.49.49.88 1.05 1.16 1.78.17.42.36 1.05.42 2.22.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.06 1.17-.25 1.8-.42 2.23a4.8 4.8 0 0 1-1.16 1.78 4.8 4.8 0 0 1-1.78 1.16c-.42.17-1.05.36-2.22.42-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.42a4.8 4.8 0 0 1-1.78-1.16 4.8 4.8 0 0 1-1.16-1.78c-.17-.42-.36-1.05-.42-2.22-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.06-1.17.25-1.8.42-2.23a4.8 4.8 0 0 1 1.16-1.78 4.8 4.8 0 0 1 1.78-1.16c.42-.17 1.05-.36 2.22-.42 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.77.13 4.9.33 4.14.63a7 7 0 0 0-2.52 1.64A7 7 0 0 0 .63 4.14C.33 4.9.13 5.77.07 7.05 0 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.28.26 2.15.56 2.91a7 7 0 0 0 1.64 2.52 7 7 0 0 0 2.52 1.64c.76.3 1.63.5 2.91.56 1.28.06 1.69.07 4.95.07s3.67-.01 4.95-.07c1.28-.06 2.15-.26 2.91-.56a7 7 0 0 0 2.52-1.64 7 7 0 0 0 1.64-2.52c.3-.76.5-1.63.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.28-.26-2.15-.56-2.91a7 7 0 0 0-1.64-2.52A7 7 0 0 0 19.86.63c-.76-.3-1.63-.5-2.91-.56C15.67.01 15.26 0 12 0z"/>
                <path fill="url(#ig-grad-page)" d="M12 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32m0 10.16a4 4 0 1 1 0-8 4 4 0 0 1 0 8m6.4-10a1.44 1.44 0 1 1-2.88 0 1.44 1.44 0 0 1 2.88 0"/>
            </svg>
        ),
        color: '',
        bg: 'bg-white' 
    },
    tiktok: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#000000" d="M12.53 0c.26 0 .5.01.75.03v5.04c-.11-.01-.23-.02-.34-.02-2.18 0-3.95 1.77-3.95 3.95v11.05c0 2.18-1.77 3.95-3.95 3.95-2.18 0-3.95-1.77-3.95-3.95s1.77-3.95 3.95-3.95c.57 0 1.11.12 1.6.34v-5.2c-.52-.1-1.05-.15-1.6-.15C2.29 11.09 0 13.38 0 16.2c0 2.82 2.29 5.11 5.11 5.11 2.82 0 5.11-2.29 5.11-5.11V8.66c1.65 1.15 3.65 1.83 5.81 1.83V5.45c-1.39 0-2.67-.47-3.7-1.25V0h.2z" />
            </svg>
        ),
        color: '',
        bg: 'bg-white' 
    },
    linkedin: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#0077B5" d="M19 0h-14c-2.76 0-5 2.24-5 5v14c0 2.76 2.24 5 5 5h14c2.76 0 5-2.24 5-5v-14c0-2.76-2.24-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.27c-.97 0-1.75-.78-1.75-1.75s.78-1.75 1.75-1.75 1.75.78 1.75 1.75-.78 1.75-1.75 1.75zm13.5 12.27h-3v-5.6c0-1.34-.03-3.06-1.86-3.06-1.87 0-2.15 1.46-2.15 2.96v5.7h-3v-11h2.88v1.5h.04c.4-.76 1.38-1.56 2.85-1.56 3.04 0 3.6 2 3.6 4.6v6.46z" />
            </svg>
        ),
        color: '',
        bg: 'bg-[#0077B5]/5' 
    },
    youtube: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#FF0000" d="M23.5 6.1s-.2-1.6-.9-2.3c-.9-1-1.9-1-2.4-1.1C16.8 2.5 12 2.5 12 2.5s-4.8 0-8.2.2c-.5.1-1.5.1-2.4 1.1-.7.7-.9 2.3-.9 2.3S.3 8.1.3 10c0 1.9.2 3.9.2 3.9s.2 1.6.9 2.3c.9 1 2.1.9 2.6 1 2 .2 8 .2 8 .2s4.8 0 8.2-.2c.5-.1 1.5-.1 2.4-1.1.7-.7.9-2.3.9-2.3s.2-2 .2-3.9c-.1-1.9-.3-3.9-.3-3.9zM9.5 14.2V7.4l6.3 3.4-6.3 3.4z" />
            </svg>
        ),
        color: '',
        bg: 'bg-red-50' 
    },
    whatsapp: { 
        icon: (props: any) => (
            <svg viewBox="0 0 24 24" {...props}>
                <path fill="#25D366" d="M12.03 0C5.39 0 0 5.39 0 12.03c0 2.11.55 4.17 1.6 5.96L0 24l6.19-1.62c1.72 1.05 3.82 1.6 5.8 1.6 6.64 0 12.03-5.39 12.03-12.03S18.66 0 12.03 0zm5.95 17.02c-.25.7-.85 1.25-1.55 1.55-.4.2-1 .4-2.5-.2-1.5-.6-2.5-1.5-3.5-2.5s-1.9-2-2.5-3.5c-.6-1.5-.4-2.1-.2-2.5.3-.7.88-1.3 1.55-1.55.25-.1.55-.1.85.1l1 2 .5 1.5c.1.3 0 .6-.2.9l-1 1c-.1.1-.2.3-.1.5.1.2.3.4.5.6 1.2 1.2 2.4 2.4 3.6 3.6.2.2.4.4.6.5.2.1.4 0 .5-.1l1-1c.3-.2.6-.3.9-.2l1.5.5 2 1.c.2.3.2.6.1.85z" />
            </svg>
        ),
        color: '',
        bg: 'bg-emerald-50' 
    },
    photo: { icon: PhotoIcon, color: 'text-amber-500', bg: 'bg-amber-50' },
    video: { icon: VideoCameraIcon, color: 'text-rose-600', bg: 'bg-rose-50' },
    data: { icon: ChartBarIcon, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    web: { icon: WindowIcon, color: 'text-cyan-600', bg: 'bg-cyan-50' },
    dev: { icon: CommandLineIcon, color: 'text-gray-700', bg: 'bg-gray-100' },
    shop: { icon: ShoppingCartIcon, color: 'text-orange-600', bg: 'bg-orange-50' },
    ads: { icon: MegaphoneIcon, color: 'text-red-500', bg: 'bg-red-50' },
    social: { icon: ChatBubbleLeftRightIcon, color: 'text-violet-600', bg: 'bg-violet-50' },
    tech: { icon: WrenchScrewdriverIcon, color: 'text-slate-600', bg: 'bg-slate-100' },
    extra: { icon: SparklesIcon, color: 'text-purple-600', bg: 'bg-purple-50' },
}

export default function ServiciosPage() {
    const { selectedCompany } = useHoldingContext()
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingService, setEditingService] = useState<Service | null>(null)

    const { data, isLoading, error } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : res.data.data || []) as Service[]
        },
        enabled: !!selectedCompany,
    })

    const openCreate = () => {
        setEditingService(null)
        setIsModalOpen(true)
    }

    const handleEdit = (service: Service) => {
        setEditingService(service)
        setIsModalOpen(true)
    }

    if (!selectedCompany) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
                <WrenchScrewdriverIcon className="w-16 h-16 text-gray-300 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Seleccioná una empresa</h2>
                <p className="text-gray-500 mt-2">Para ver los servicios, primero debés seleccionar una empresa.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <WrenchScrewdriverIcon className="w-7 h-7 text-violet-600" />
                        Servicios
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Catálogo de servicios de <span className="font-semibold">{selectedCompany.name}</span>.
                    </p>
                </div>
                <button 
                    onClick={openCreate} 
                    className="btn-primary bg-violet-600 hover:bg-violet-700 ring-violet-500/30"
                >
                    <PlusIcon className="w-5 h-5" />
                    Nuevo Servicio
                </button>
            </div>

            {/* Table */}
            <div className="glass-card overflow-hidden">
                {isLoading ? (
                    <div className="p-12 flex justify-center">
                        <div className="w-8 h-8 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="p-12 text-center text-rose-500 bg-rose-50/50">
                        Error al cargar los servicios.
                    </div>
                ) : !data || data.length === 0 ? (
                    <div className="text-center py-16 px-4">
                        <WrenchScrewdriverIcon className="mx-auto h-12 w-12 text-gray-300" />
                        <h3 className="mt-2 text-sm font-semibold text-gray-900">No hay servicios</h3>
                        <p className="mt-1 text-sm text-gray-500">Creá el primer servicio para empezar a asignarlos a clientes.</p>
                        <div className="mt-6">
                            <button onClick={openCreate} className="btn-primary bg-violet-600 hover:bg-violet-700">
                                <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                                Nuevo Servicio
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Servicio</th>
                                    <th>Descripción</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.map((service) => {
                                    const iconData = ICON_MAP[service.icon || 'extra'] || ICON_MAP.extra
                                    const IconComponent = iconData.icon

                                    return (
                                        <tr 
                                            key={service.id}
                                            onClick={() => handleEdit(service)}
                                            className="cursor-pointer hover:bg-gray-50/80 transition-all duration-200 group border-b border-gray-100 last:border-0"
                                        >
                                            <td>
                                                <div className="flex items-center gap-3">
                                                    <div className={clsx(
                                                        "w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm border-2 border-white transition-transform group-hover:scale-110",
                                                        iconData.bg
                                                    )}>
                                                        <IconComponent className={clsx("w-6 h-6", iconData.color)} />
                                                    </div>
                                                    <div>
                                                        <div className="font-bold text-gray-900 transition-colors group-hover:text-violet-600">{service.name}</div>
                                                        <div className="text-[10px] text-gray-400 font-mono uppercase tracking-widest leading-none">ID: {service.id.split('-')[0]}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="text-sm text-gray-600 py-4 max-w-md truncate">{service.description || '—'}</td>
                                            <td>
                                                <span className={clsx(
                                                    "text-xs font-semibold px-2 py-1 rounded-md ring-1 ring-inset",
                                                    service.is_active 
                                                        ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20" 
                                                        : "bg-gray-50 text-gray-600 ring-gray-500/10"
                                                )}>
                                                    {service.is_active ? 'Activo' : 'Inactivo'}
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

            <ServiceFormModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                service={editingService}
                companyId={selectedCompany.id}
            />
        </div>
    )
}
