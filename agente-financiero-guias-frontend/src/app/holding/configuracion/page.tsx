'use client'

import Link from 'next/link'
import {
    UserGroupIcon,
    AdjustmentsHorizontalIcon,
    CreditCardIcon,
    ShieldCheckIcon,
    ArrowRightIcon,
} from '@heroicons/react/24/outline'

const sections = [
    {
        href: '/holding/configuracion/usuarios',
        icon: UserGroupIcon,
        title: 'Usuarios y Accesos',
        description: 'Administrá quién tiene acceso a cada empresa y qué permisos tiene dentro del sistema.',
        color: 'indigo',
    },
    {
        href: '/holding/configuracion/gastos',
        icon: AdjustmentsHorizontalIcon,
        title: 'Config. Gastos',
        description: 'Configurá los tipos y categorías de gastos que se usan al registrar egresos.',
        color: 'amber',
    },
    {
        href: '/holding/configuracion/metodos-pago',
        icon: CreditCardIcon,
        title: 'Métodos de Pago',
        description: 'Gestioná cuentas bancarias, cajas y medios de pago disponibles en el holding.',
        color: 'emerald',
    },
]

const colorMap: Record<string, { bg: string; icon: string; badge: string }> = {
    indigo: {
        bg: 'bg-indigo-50 group-hover:bg-indigo-100',
        icon: 'text-indigo-600',
        badge: 'bg-indigo-600',
    },
    amber: {
        bg: 'bg-amber-50 group-hover:bg-amber-100',
        icon: 'text-amber-600',
        badge: 'bg-amber-600',
    },
    emerald: {
        bg: 'bg-emerald-50 group-hover:bg-emerald-100',
        icon: 'text-emerald-600',
        badge: 'bg-emerald-600',
    },
}

export default function ConfiguracionPage() {
    return (
        <div className="space-y-8 max-w-4xl mx-auto animate-fade-in-up">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <ShieldCheckIcon className="w-7 h-7 text-gray-500" />
                    Configuración
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                    Administrá las configuraciones globales del holding financiero.
                </p>
            </div>

            {/* Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {sections.map((section) => {
                    const colors = colorMap[section.color]
                    return (
                        <Link
                            key={section.href}
                            href={section.href}
                            className="group relative flex flex-col gap-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-200"
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${colors.bg}`}>
                                <section.icon className={`w-6 h-6 ${colors.icon}`} />
                            </div>

                            <div className="flex-1">
                                <h2 className="text-base font-semibold text-gray-900 group-hover:text-gray-700">
                                    {section.title}
                                </h2>
                                <p className="mt-1 text-sm text-gray-500 leading-relaxed">
                                    {section.description}
                                </p>
                            </div>

                            <div className="flex items-center gap-1.5 text-sm font-medium text-gray-400 group-hover:text-gray-600 transition-colors">
                                Ir a la sección
                                <ArrowRightIcon className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                            </div>
                        </Link>
                    )
                })}
            </div>
        </div>
    )
}
