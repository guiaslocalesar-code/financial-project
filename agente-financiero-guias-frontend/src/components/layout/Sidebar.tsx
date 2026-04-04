'use client'

import { Fragment } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import { Dialog, Transition } from '@headlessui/react'
import {
    HomeIcon,
    BuildingOffice2Icon,
    UsersIcon,
    UserGroupIcon,
    DocumentTextIcon,
    BanknotesIcon,
    ChartBarIcon,
    CogIcon,
    XMarkIcon,
    ArrowTrendingUpIcon,
    ClipboardDocumentListIcon,
    CalculatorIcon,
    WrenchScrewdriverIcon,
    AdjustmentsHorizontalIcon,
    ArrowsRightLeftIcon,
    CreditCardIcon,
} from '@heroicons/react/24/outline'
import { useAuthContext } from '@/context/AuthContext'
import CompanySelector from './CompanySelector'

const navigation = [
    { name: 'Dashboard', href: '/holding', icon: HomeIcon },
    { name: 'Empresas', href: '/holding/empresas', icon: BuildingOffice2Icon },
    { name: 'Clientes', href: '/holding/clientes', icon: UsersIcon },
    { name: 'Servicios', href: '/holding/servicios', icon: WrenchScrewdriverIcon },
    { name: 'Facturas', href: '/holding/facturas', icon: DocumentTextIcon },
    { name: 'Cobranzas', href: '/holding/cobranzas', icon: BanknotesIcon },
    { name: 'Gastos', href: '/holding/gastos', icon: CalculatorIcon },
    { name: 'Presupuestos', href: '/holding/presupuestos', icon: ClipboardDocumentListIcon },
    { name: 'Movimientos', href: '/holding/movimientos', icon: ArrowsRightLeftIcon },
    { name: 'Deudas', href: '/holding/deudas', icon: CreditCardIcon },
    { name: 'Comisiones', href: '/holding/comisiones', icon: BanknotesIcon },
    { name: 'Reportes', href: '/holding/reportes', icon: ChartBarIcon },
]

const adminNavigation = [
    { name: 'Usuarios y Accesos', href: '/holding/configuracion/usuarios', icon: UserGroupIcon },
    { name: 'Config. Gastos', href: '/holding/configuracion/gastos', icon: AdjustmentsHorizontalIcon },
    { name: 'Métodos de Pago', href: '/holding/configuracion/metodos-pago', icon: CreditCardIcon },
    { name: 'Configuración', href: '/holding/configuracion', icon: CogIcon },
]

interface SidebarProps {
    isOpen?: boolean
    setIsOpen?: (open: boolean) => void
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
    const pathname = usePathname()
    const { user } = useAuthContext()

    const isAdmin = user?.isSuperAdmin === true || user?.globalRole === 'super_admin'

    const SidebarContent = () => (
        <>
            {/* Logo */}
            <div className="flex flex-col items-center justify-center min-h-[80px] p-4 bg-white border-b border-gray-100">
                <Link href="/holding" className="flex items-center gap-3 w-full justify-center">
                    <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                        <ArrowTrendingUpIcon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-lg font-bold text-gray-900 leading-tight">Holding</span>
                        <span className="text-[10px] text-gray-400 uppercase tracking-widest -mt-0.5">Financial</span>
                    </div>
                </Link>
            </div>

            {/* Company Selector */}
            <div className="px-4 py-3 border-b border-gray-100">
                <CompanySelector />
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto bg-white">
                {navigation.map((item) => {
                    const isActive = pathname === item.href ||
                        (item.href !== '/holding' && pathname.startsWith(item.href))
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            onClick={() => setIsOpen && setIsOpen(false)}
                            className={clsx(
                                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'bg-blue-50 text-blue-700 shadow-sm'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            )}
                        >
                            <item.icon className={clsx('w-5 h-5', isActive ? 'text-blue-700' : 'text-gray-400')} />
                            {item.name}
                        </Link>
                    )
                })}

                {/* Admin Section */}
                {isAdmin && (
                    <>
                        <div className="my-4 border-t border-gray-200" />
                        {adminNavigation.map((item) => {
                            const isActive = pathname.startsWith(item.href)
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    onClick={() => setIsOpen && setIsOpen(false)}
                                    className={clsx(
                                        'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                                        isActive
                                            ? 'bg-blue-50 text-blue-700 shadow-sm'
                                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                    )}
                                >
                                    <item.icon className={clsx('w-5 h-5', isActive ? 'text-blue-700' : 'text-gray-400')} />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </>
                )}
            </nav>

            {/* User info at bottom */}
            {user && (
                <div className="p-4 border-t border-gray-100 bg-gray-50/50">
                    <div className="flex items-center gap-3">
                        {user.picture ? (
                            <img src={user.picture} alt={user.name || ''} className="w-8 h-8 rounded-full object-cover ring-2 ring-white shadow-sm" />
                        ) : (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                                {user.name?.substring(0, 2).toUpperCase() || user.email.substring(0, 2).toUpperCase()}
                            </div>
                        )}
                        <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-900 truncate">{user.name || user.email}</p>
                            <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                </div>
            )}
        </>
    )

    return (
        <>
            {/* Mobile Sidebar */}
            <Transition.Root show={isOpen} as={Fragment}>
                <Dialog as="div" className="relative z-50 lg:hidden" onClose={setIsOpen || (() => {})}>
                    <Transition.Child as={Fragment}
                        enter="transition-opacity ease-linear duration-300" enterFrom="opacity-0" enterTo="opacity-100"
                        leave="transition-opacity ease-linear duration-300" leaveFrom="opacity-100" leaveTo="opacity-0"
                    >
                        <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm" />
                    </Transition.Child>

                    <div className="fixed inset-0 flex">
                        <Transition.Child as={Fragment}
                            enter="transition ease-in-out duration-300 transform" enterFrom="-translate-x-full" enterTo="translate-x-0"
                            leave="transition ease-in-out duration-300 transform" leaveFrom="translate-x-0" leaveTo="-translate-x-full"
                        >
                            <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                                <Transition.Child as={Fragment}
                                    enter="ease-in-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
                                    leave="ease-in-out duration-300" leaveFrom="opacity-100" leaveTo="opacity-0"
                                >
                                    <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                                        <button type="button" className="-m-2.5 p-2.5" onClick={() => setIsOpen && setIsOpen(false)}>
                                            <XMarkIcon className="h-6 w-6 text-white" />
                                        </button>
                                    </div>
                                </Transition.Child>
                                <div className="flex grow flex-col overflow-y-auto bg-white ring-1 ring-white/10">
                                    <SidebarContent />
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </Dialog>
            </Transition.Root>

            {/* Desktop Sidebar */}
            <div className="hidden lg:flex lg:flex-col lg:w-64 lg:border-r lg:border-gray-200 bg-white">
                <SidebarContent />
            </div>
        </>
    )
}
