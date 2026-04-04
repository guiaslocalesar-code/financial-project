'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AuthProvider, useAuthContext } from '@/context/AuthContext'
import { HoldingProvider, useHoldingContext } from '@/context/HoldingContext'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { api } from '@/services/api'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 5 * 60 * 1000, // 5 min
        },
    },
})

function HoldingShell({ children }: { children: React.ReactNode }) {
    const { user, isLoading, isAuthenticated } = useAuthContext()
    const { setCompanies } = useHoldingContext()
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const router = useRouter()

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/login')
        }
    }, [isLoading, isAuthenticated, router])

    // Load companies from financial backend
    useEffect(() => {
        if (isAuthenticated) {
            api.companies.list()
                .then(res => {
                    const data = res.data
                    // Handle both array responses and {data: [...]} responses
                    const companiesList = Array.isArray(data) ? data : (data.data || data.companies || [])
                    setCompanies(companiesList)
                })
                .catch(err => {
                    console.error('[Holding] Error loading companies:', err)
                    // Use mock data in dev if backend is unavailable
                    if (process.env.NODE_ENV === 'development') {
                        setCompanies([
                            { id: 'aeb56588-5e15-4ce2-b24b-065ebf842c44', name: 'Guias Locales', cuit: '30-71234567-0', fiscal_condition: 'RI', is_active: true, created_at: '', updated_at: '' },
                            { id: 'f27ddc21-a43f-4a3e-b041-3be2819a515a', name: 'Guias 2.0', cuit: '30-71234568-0', fiscal_condition: 'RI', is_active: true, created_at: '', updated_at: '' },
                        ])
                    }
                })
        }
    }, [isAuthenticated, setCompanies])

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                    <span className="text-sm text-gray-500">Cargando portal...</span>
                </div>
            </div>
        )
    }

    if (!isAuthenticated) return null

    return (
        <div className="min-h-screen flex bg-gray-50">
            <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
            <div className="flex-1 flex flex-col min-w-0">
                <Header onMenuClick={() => setSidebarOpen(true)} />
                <main className="flex-1 overflow-y-auto">
                    <div className="p-4 sm:p-6 lg:p-8">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}

export default function HoldingLayout({ children }: { children: React.ReactNode }) {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <HoldingProvider>
                    <HoldingShell>
                        {children}
                    </HoldingShell>
                </HoldingProvider>
            </AuthProvider>
        </QueryClientProvider>
    )
}
