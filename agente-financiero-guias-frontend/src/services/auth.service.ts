/**
 * Auth Service — Holding Financial Portal
 * Reuses cutguias backend OAuth flow
 */

import { api, AUTH_URL } from './api'
import type { User } from '@/types'

const getApiBaseUrl = () => {
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
        return 'https://api.guiaslocales.com.ar'
    }
    return process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:4000'
}

/** Redirect to Google OAuth login */
export function getLoginUrl(): string {
    const redirectUrl = typeof window !== 'undefined' ? `${window.location.origin}/holding` : '';
    return `${getApiBaseUrl()}/auth/google${redirectUrl ? `?redirect_to=${encodeURIComponent(redirectUrl)}` : ''}`
}

/** Logout and redirect to login page */
export async function logout(): Promise<void> {
    try {
        await api.auth.logout()
    } catch (error) {
        console.error('Logout error:', error)
    } finally {
        if (typeof window !== 'undefined') {
            window.location.href = '/login'
        }
    }
}

/** Refresh access token */
export async function refreshToken(): Promise<boolean> {
    try {
        await api.auth.refresh()
        return true
    } catch {
        return false
    }
}

/** Get current authenticated user */
export async function getCurrentUser(): Promise<User | null> {
    try {
        const response = await api.auth.me()
        return response.data as User
    } catch {
        return null
    }
}

/** Check authentication status */
export async function checkAuth(): Promise<{ authenticated: boolean; user: User | null }> {
    try {
        const user = await getCurrentUser()
        return { authenticated: user !== null, user }
    } catch {
        return { authenticated: false, user: null }
    }
}
