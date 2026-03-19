/**
 * API Client — Holding Financial Portal
 * Dual-backend Axios client with cookie-based auth
 *
 * Auth API  → Node.js (api.guiaslocales.com.ar)
 * Finance API → Python FastAPI
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios'

// In browser use relative paths (Next.js proxy handles routing)
const API_BASE_URL = typeof window !== 'undefined' ? '' : (process.env.NEXT_PUBLIC_AUTH_API_URL || '')
const FINANCE_BASE_URL = typeof window !== 'undefined' ? '' : (process.env.NEXT_PUBLIC_FINANCE_API_URL || '')

// ─── Auth API Client (Node.js) ──────────────────────────────────────────────

export const authClient: AxiosInstance = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
    timeout: 30000,
})

// Token-refresh interceptor
authClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as typeof error.config & { _retry?: boolean }

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true
            try {
                await axios.post(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true })
                return authClient(originalRequest)
            } catch {
                if (typeof window !== 'undefined') window.location.href = '/login'
                return Promise.reject(error)
            }
        }
        return Promise.reject(error)
    }
)

// ─── Finance API Client (Python / FastAPI) ──────────────────────────────────

export const financeClient: AxiosInstance = axios.create({
    baseURL: `${FINANCE_BASE_URL}/finance-api`,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
    timeout: 30000,
})

// ─── API Namespaces ─────────────────────────────────────────────────────────

export const api = {
    // ── Auth (Node.js) ──────────────────────────────────────────────────────
    auth: {
        me: () => axios.get(`${API_BASE_URL}/auth/me`, { withCredentials: true }),
        logout: () => axios.post(`${API_BASE_URL}/auth/logout`, {}, { withCredentials: true }),
        refresh: () => axios.post(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true }),
    },

    // ── Admin / RBAC (Node.js) ──────────────────────────────────────────────
    admin: {
        listBrands: () => authClient.get('/admin/brands'),
        listUsers: (params?: { status?: string }) => authClient.get('/admin/users', { params }),
        getUserBrands: (email: string) => authClient.get(`/admin/users/${encodeURIComponent(email)}/brands`),
    },

    // ── Finance: Companies ──────────────────────────────────────────────────
    companies: {
        list: () => financeClient.get('/companies/'),
        get: (id: string) => financeClient.get(`/companies/${id}/`),
        create: (data: any) => financeClient.post('/companies/', data),
        update: (id: string, data: any) => financeClient.put(`/companies/${id}/`, data),
    },

    // ── Finance: Clients ────────────────────────────────────────────────────
    clients: {
        list: (companyId: string) => financeClient.get('/clients/', { params: { company_id: companyId } }),
        get: (id: string) => financeClient.get(`/clients/${id}/`),
        create: (data: any) => financeClient.post('/clients/', data),
        update: (id: string, data: any) => financeClient.put(`/clients/${id}/`, data),
    },

    // ── Finance: Services ───────────────────────────────────────────────────
    services: {
        list: (companyId: string) => financeClient.get('/services/', { params: { company_id: companyId } }),
        create: (data: any) => financeClient.post('/services/', data),
        update: (id: string, data: any) => financeClient.put(`/services/${id}/`, data),
    },

    // ── Finance: Invoices ───────────────────────────────────────────────────
    invoices: {
        list: (companyId: string) => financeClient.get('/invoices/', { params: { company_id: companyId } }),
        create: (data: any) => financeClient.post('/invoices/', data),
        update: (id: string, data: any) => financeClient.put(`/invoices/${id}/`, data),
        emit: (invoiceId: string) => financeClient.post(`/invoices/${invoiceId}/emit/`),
    },

    // ── Finance: Dashboard ──────────────────────────────────────────────────
    dashboard: {
        all: (companyId: string, month?: number, year?: number) => financeClient.get('/dashboard/all/', {
            params: { company_id: companyId, month, year }
        }),
        summary: (companyId: string, month?: number, year?: number) => financeClient.get('/dashboard/summary/', { 
            params: { company_id: companyId, month, year } 
        }),
        profitability: (companyId: string, month?: number, year?: number) => financeClient.get('/dashboard/profitability/', { 
            params: { company_id: companyId, month, year } 
        }),
    },

    // ── Finance: Budgets ────────────────────────────────────────────────────
    budgets: {
        list: (companyId: string, params?: { month?: number; year?: number }) =>
            financeClient.get('/budgets/', { params: { company_id: companyId, ...params } }),
        create: (data: any) => financeClient.post('/budgets/', data),
        pay: (budgetId: string) => financeClient.post(`/budgets/${budgetId}/pay/`),
    },

    incomeBudgets: {
        list: (companyId: string, params?: { month?: number; year?: number }) =>
            financeClient.get('/income-budgets/', { params: { company_id: companyId, ...params } }),
        create: (data: any) => financeClient.post('/income-budgets/', data),
        collect: (budgetId: string) => financeClient.post(`/income-budgets/${budgetId}/collect/`),
    },

    expenses: {
        listTypes: (companyId: string) => financeClient.get('/expenses/types/', { params: { company_id: companyId } }),
        createType: (data: any) => financeClient.post('/expenses/types/', data),
        listCategories: (companyId: string, typeId?: string) => 
            financeClient.get('/expenses/categories/', { params: { company_id: companyId, expense_type_id: typeId } }),
        createCategory: (data: any) => financeClient.post('/expenses/categories/', data),
    },

    transactions: {
        list: (companyId: string) => financeClient.get('/transactions/', { params: { company_id: companyId } }),
        get: (id: string) => financeClient.get(`/transactions/${id}/`),
    },

    clientServices: {
        list: (clientId: string) => financeClient.get(`/client-services/${clientId}/`),
        assign: (clientId: string, data: any) => financeClient.post(`/client-services/${clientId}/`, data),
    }
}

export const AUTH_URL = API_BASE_URL
