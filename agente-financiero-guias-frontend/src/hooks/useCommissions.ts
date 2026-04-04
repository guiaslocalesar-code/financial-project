import { useState } from 'react'
import { useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { 
    PayCommissionPayload, 
    CreateCommissionRecipient, 
    CreateCommissionRule,
    Commission
} from '@/types/commissions'
import { startOfMonth, endOfMonth, format } from 'date-fns'

export function useCommissions(companyId?: string) {
    const queryClient = useQueryClient()
    
    // Período seleccionado
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())

    // Sync effect for external triggers (like 400 errors)
    useEffect(() => {
        const handleRefresh = () => {
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
            queryClient.invalidateQueries({ queryKey: ['commissions-summary'] })
        };
        window.addEventListener('refresh-commissions', handleRefresh);
        return () => window.removeEventListener('refresh-commissions', handleRefresh);
    }, [queryClient])

    // Helper para fechas
    const startDate = format(startOfMonth(new Date(selectedYear, selectedMonth - 1)), 'yyyy-MM-dd')
    const endDate = format(endOfMonth(new Date(selectedYear, selectedMonth - 1)), 'yyyy-MM-dd')

    // ── Resumen Dashboard ───────────────────────────────────────────────────
    const summaryQuery = useQuery({
        queryKey: ['commissions-summary', companyId, selectedMonth, selectedYear],
        queryFn: async () => {
            if (!companyId) return null
            const res = await api.commissions.getSummary(companyId, startDate, endDate)
            return res.data
        },
        enabled: !!companyId,
    })

    // ── Listado de Comisiones (Pendientes/Pagadas) ─────────────────────────
    const commissionsQuery = (status?: string, recipientId?: string) => useQuery({
        queryKey: ['commissions', companyId, status, recipientId, selectedMonth, selectedYear],
        queryFn: async () => {
            if (!companyId) return []
            const res = await api.commissions.list({ 
                company_id: companyId, 
                recipient_id: recipientId ? recipientId : undefined,
                month: selectedMonth,
                year: selectedYear
            })
            const allCommissions = res.data;
            if (status) {
                // Backend returns status in UPPERCASE (PENDING, PAID)
                return allCommissions.filter((c: Commission) => 
                    c.status?.toUpperCase() === status.toUpperCase()
                )
            }
            return allCommissions
        },
        enabled: !!companyId,
    })

    // ── Destinatarios ───────────────────────────────────────────────────────
    const recipientsQuery = useQuery({
        queryKey: ['commission-recipients', companyId],
        queryFn: async () => {
            if (!companyId) return []
            const res = await api.commissions.listRecipients(companyId)
            return res.data
        },
        enabled: !!companyId,
    })

    // ── Reglas ─────────────────────────────────────────────────────────────
    const rulesQuery = useQuery({
        queryKey: ['commission-rules', companyId],
        queryFn: async () => {
            if (!companyId) return []
            const res = await api.commissions.listRules(companyId)
            return res.data
        },
        enabled: !!companyId,
    })

    // ── Mutaciones ─────────────────────────────────────────────────────────
    
    // Liquidar (Pagar) individual
    const payMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: PayCommissionPayload }) => 
            api.commissions.pay(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
            queryClient.invalidateQueries({ queryKey: ['commissions-summary'] })
        }
    })

    // Liquidar (Pagar) Masivo
    const bulkPayMutation = useMutation({
        mutationFn: (data: { commission_ids: string[]; payment_method: string; payment_method_id?: string; payment_date?: string }) =>
            api.commissions.bulkPay(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
            queryClient.invalidateQueries({ queryKey: ['commissions-summary'] })
        }
    })

    // Recalcular / Generar
    const generateMutation = useMutation({
        mutationFn: () => {
            if (!companyId) throw new Error('Company ID is required')
            return api.commissions.generate(companyId)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commissions'] })
            queryClient.invalidateQueries({ queryKey: ['commissions-summary'] })
        }
    })

    // CRUD Destinatarios
    const createRecipientMutation = useMutation({
        mutationFn: (data: CreateCommissionRecipient) => api.commissions.createRecipient(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-recipients'] })
        }
    })

    const updateRecipientMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: any }) => api.commissions.updateRecipient(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-recipients'] })
        }
    })

    const deleteRecipientMutation = useMutation({
        mutationFn: (id: string) => api.commissions.deleteRecipient(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-recipients'] })
        }
    })

    // CRUD Reglas
    const createRuleMutation = useMutation({
        mutationFn: (data: CreateCommissionRule) => api.commissions.createRule(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-rules'] })
        }
    })

    const updateRuleMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: any }) => api.commissions.updateRule(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-rules'] })
        }
    })

    const deleteRuleMutation = useMutation({
        mutationFn: (id: string) => api.commissions.deleteRule(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['commission-rules'] })
        }
    })

    return {
        summary: summaryQuery.data,
        isLoadingSummary: summaryQuery.isLoading,
        commissionsQuery,
        recipients: recipientsQuery.data || [],
        isLoadingRecipients: recipientsQuery.isLoading,
        rules: rulesQuery.data || [],
        isLoadingRules: rulesQuery.isLoading,
        payMutation,
        bulkPayMutation,
        generateMutation,
        createRecipient: createRecipientMutation,
        updateRecipient: updateRecipientMutation,
        deleteRecipient: deleteRecipientMutation,
        createRule: createRuleMutation,
        updateRule: updateRuleMutation,
        deleteRule: deleteRuleMutation,
        selectedMonth,
        setSelectedMonth,
        selectedYear,
        setSelectedYear
    }
}

export function useRecipientSummary(recipientId?: string) {
    return useQuery({
        queryKey: ['recipient-summary', recipientId],
        queryFn: async () => {
            if (!recipientId) return null
            const res = await api.commissions.getRecipientSummary(recipientId)
            return res.data
        },
        enabled: !!recipientId,
    })
}
