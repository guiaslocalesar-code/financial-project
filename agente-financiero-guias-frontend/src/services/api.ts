/**
 * API Client — Holding Financial Portal
 * Dual-backend Axios client with cookie-based auth
 *
 * Auth API  → Node.js (api.guiaslocales.com.ar)
 * Finance API → Python FastAPI
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios'
import { PayCommissionPayload } from '@/types/commissions'

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
        list: () => financeClient.get('/companies'),
        get: (id: string) => financeClient.get(`/companies/${id}`),
        create: (data: any) => financeClient.post('/companies', data),
        update: (id: string, data: any) => financeClient.put(`/companies/${id}`, data),
        updateLogo: (id: string, file: File) => {
            const formData = new FormData()
            formData.append('file', file)
            return financeClient.post(`/companies/${id}/logo`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
        },
    },

    // ── Finance: Clients ────────────────────────────────────────────────────
    clients: {
        list: (companyId: string) => financeClient.get('/clients', { params: { company_id: companyId } }),
        get: (id: string) => financeClient.get(`/clients/${id}`),
        create: (data: any) => financeClient.post('/clients', data),
        update: (id: string, data: any) => financeClient.put(`/clients/${id}`, data),
    },

    // ── Finance: Services ───────────────────────────────────────────────────
    services: {
        list: (companyId: string) => financeClient.get('/services', { params: { company_id: companyId } }),
        create: (data: any) => financeClient.post('/services', data),
        update: (id: string, data: any) => financeClient.put(`/services/${id}`, data),
    },

    // ── Finance: Invoices ───────────────────────────────────────────────────
    invoices: {
        list: (companyId: string) => financeClient.get('/invoices', { params: { company_id: companyId } }),
        create: (data: any) => financeClient.post('/invoices', data),
        update: (id: string, data: any) => financeClient.put(`/invoices/${id}`, data),
        emit: (invoiceId: string) => financeClient.post(`/invoices/${invoiceId}/emit`),
    },

    // ── Finance: Dashboard ──────────────────────────────────────────────────
    dashboard: {
        all: (companyId: string, startDate?: string, endDate?: string) => financeClient.get('/dashboard/all', {
            params: { company_id: companyId, start_date: startDate, end_date: endDate }
        }),
        summary: (companyId: string, startDate?: string, endDate?: string) => financeClient.get('/dashboard/summary', { 
            params: { company_id: companyId, start_date: startDate, end_date: endDate } 
        }),
        profitability: (companyId: string, startDate?: string, endDate?: string) => financeClient.get('/dashboard/profitability', { 
            params: { company_id: companyId, start_date: startDate, end_date: endDate } 
        }),
    },

    // ── Finance: Budgets ────────────────────────────────────────────────────
    budgets: {
        list: (companyId: string, params?: { month?: number; year?: number }) =>
            financeClient.get('/budgets', { params: { company_id: companyId, ...params } }),
        create: (data: any) => financeClient.post('/budgets', data),
        pay: (budgetId: string) => financeClient.post(`/budgets/${budgetId}/pay`),
    },

    incomeBudgets: {
        list: (companyId: string, params?: { month?: number; year?: number }) =>
            financeClient.get('/income-budgets', { params: { company_id: companyId, ...params } }),
        create: (data: any) => financeClient.post('/income-budgets', data),
        collect: (budgetId: string) => financeClient.post(`/income-budgets/${budgetId}/collect`),
    },

    expenses: {
        listTypes: (companyId: string) => financeClient.get('/expenses/types', { params: { company_id: companyId } }),
        createType: (data: any) => financeClient.post('/expenses/types', data),
        listCategories: (companyId: string, typeId?: string) => 
            financeClient.get('/expenses/categories', { params: { company_id: companyId, expense_type_id: typeId } }),
        createCategory: (data: any) => financeClient.post('/expenses/categories', data),
    },

    transactions: {
        list: (companyId: string) => financeClient.get('/transactions', { params: { company_id: companyId } }),
        get: (id: string) => financeClient.get(`/transactions/${id}`),
    },

    clientServices: {
        list: (clientId: string) => financeClient.get(`/client-services/${clientId}`),
        assign: (clientId: string, data: any) => financeClient.post(`/client-services/${clientId}`, data),
        update: (id: string, data: any) => financeClient.put(`/client-services/item/${id}`, data),
        remove: (id: string) => financeClient.delete(`/client-services/item/${id}`),
    },
    paymentMethods: {
        list: (companyId: string) => financeClient.get('/payment-methods', { params: { company_id: companyId } }),
        create: (data: any) => financeClient.post('/payment-methods', data),
        update: (id: string, data: any) => financeClient.put(`/payment-methods/${id}`, data),
        delete: (id: string) => financeClient.delete(`/payment-methods/${id}`),
    },
    debts: {
        list: (companyId: string, status?: string) => 
            financeClient.get('/debts', { params: { company_id: companyId, status } }),
        get: (id: string) => financeClient.get(`/debts/${id}`),
        create: (data: any) => financeClient.post('/debts', data),
        listInstallments: (debtId: string) => financeClient.get(`/debts/${debtId}/installments`),
        createInstallment: (debtId: string, data: any) => financeClient.post(`/debts/${debtId}/installments`, data),
    },
    commissions: {
        // Summary & Stats
        getSummary: (companyId: string, startDate?: string, endDate?: string) => 
            financeClient.get('/dashboard/commissions-summary', { params: { company_id: companyId, start_date: startDate, end_date: endDate } }),
        getRecipientSummary: (recipientId: string) => financeClient.get(`/commissions/recipient/${recipientId}/summary`),

        // Comisiones
        list: (params: { company_id: string; status?: string; recipient_id?: string }) => 
            financeClient.get('/commissions', { params }),
        pay: (commissionId: string, data: PayCommissionPayload) => 
            financeClient.post(`/commissions/${commissionId}/pay`, data),
        generate: (companyId: string) => 
            financeClient.post('/commissions/generate', null, { params: { company_id: companyId } }),

        // CRUD Destinatarios
        listRecipients: (companyId: string) => financeClient.get('/commissions/recipients', { params: { company_id: companyId } }),
        createRecipient: (data: any) => financeClient.post('/commissions/recipients', data),
        updateRecipient: (id: string, data: any) => financeClient.patch(`/commissions/recipients/${id}`, data),
        deleteRecipient: (id: string) => financeClient.delete(`/commissions/recipients/${id}`),

        // CRUD Reglas
        listRules: (companyId: string) => financeClient.get('/commissions/rules', { params: { company_id: companyId } }),
        createRule: (data: any) => financeClient.post('/commissions/rules', data),
        updateRule: (id: string, data: any) => financeClient.patch(`/commissions/rules/${id}`, data),
        deleteRule: (id: string) => financeClient.delete(`/commissions/rules/${id}`),
    },

    // ── Finance: User Roles & Permissions ─────────────────────────────────
    users: {
        listFromCompany: (companyId: string) => financeClient.get(`/users/companies/${companyId}`),
        inviteUser: (companyId: string, data: { email: string, role: string, permissions: string[] | null }) => 
            financeClient.post(`/users/companies/${companyId}`, data),
        updateRole: (userCompanyId: string, data: { role?: string, permissions?: string[] | null, is_active?: boolean }) => 
            financeClient.put(`/users/user-companies/${userCompanyId}`, data),
        removeUser: (userCompanyId: string) => financeClient.delete(`/users/user-companies/${userCompanyId}`),
    }
}

export const AUTH_URL = API_BASE_URL
