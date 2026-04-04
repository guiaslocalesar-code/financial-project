'use client'

import { Bars3Icon, BellIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'
import { useAuthContext } from '@/context/AuthContext'

interface HeaderProps {
    onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
    const { user, logout } = useAuthContext()

    return (
        <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white/80 backdrop-blur-lg px-4 sm:gap-x-6 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
                onClick={onMenuClick}
            >
                <Bars3Icon className="h-6 w-6" />
            </button>

            {/* Separator */}
            <div className="h-6 w-px bg-gray-200 lg:hidden" />

            {/* Right side */}
            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6 justify-end">
                <div className="flex items-center gap-x-4 lg:gap-x-6">
                    {/* Notifications (placeholder) */}
                    <button className="relative -m-2.5 p-2.5 text-gray-400 hover:text-gray-500 transition-colors">
                        <BellIcon className="h-5 w-5" />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
                    </button>

                    {/* Separator */}
                    <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" />

                    {/* User info + logout */}
                    <div className="flex items-center gap-3">
                        {user?.picture ? (
                            <img src={user.picture} alt="" className="h-8 w-8 rounded-full bg-gray-50 ring-2 ring-white shadow-sm" />
                        ) : (
                            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                                {user?.name?.substring(0, 2).toUpperCase() || '?'}
                            </div>
                        )}
                        <div className="hidden sm:flex sm:flex-col">
                            <span className="text-sm font-semibold text-gray-900">{user?.name}</span>
                        </div>
                        <button
                            onClick={logout}
                            className="ml-2 p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                            title="Cerrar sesión"
                        >
                            <ArrowRightOnRectangleIcon className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    )
}
