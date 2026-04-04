'use client'

/**
 * Auth Context Provider — Holding Financial Portal
 * Manages authentication state with cutguias backend OAuth
 */

import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
    ReactNode,
} from 'react'
import type { User } from '@/types'
import * as authService from '@/services/auth.service'

interface AuthContextType {
    user: User | null
    isLoading: boolean
    isAuthenticated: boolean
    error: string | null
    login: () => void
    logout: () => Promise<void>
    refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const checkAuth = useCallback(async () => {
        try {
            setIsLoading(true)
            setError(null)

            // Bypass auth for local testing
            if (process.env.NODE_ENV === 'development') {
                setUser({
                    id: 'dev-user-123',
                    email: 'demo@guiaslocales.com.ar',
                    name: 'Demo Local',
                    picture: 'https://ui-avatars.com/api/?name=Demo',
                    roles: ['admin']
                } as User)
                return
            }

            const result = await authService.checkAuth()
            setUser(result.user)
        } catch {
            setUser(null)
            setError('Error al verificar la autenticación')
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => { checkAuth() }, [checkAuth])

    const login = useCallback(() => {
        window.location.href = authService.getLoginUrl()
    }, [])

    const logout = useCallback(async () => {
        try {
            await authService.logout()
        } catch {
            // noop
        } finally {
            setUser(null)
        }
    }, [])

    const refreshUser = useCallback(async () => {
        const userData = await authService.getCurrentUser()
        setUser(userData)
    }, [])

    return (
        <AuthContext.Provider value={{
            user, isLoading, isAuthenticated: !!user, error, login, logout, refreshUser
        }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuthContext() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuthContext must be used within an AuthProvider')
    }
    return context
}
