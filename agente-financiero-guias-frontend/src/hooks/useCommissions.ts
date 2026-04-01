import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { 
    PayCommissionPayload, 
    CreateCommissionRecipient, 
    CreateCommissionRule 
} from '@/types/commissions'

export function useCommissions(companyId?: string) {
    const queryClient = useQueryClient()

    // ── Resumen Dashboard ───────────────────────────────────────────────────
    const summaryQuery = useQuery({
        queryKey: ['commissions-summary', companyId],
        queryFn: async () => {
            if (!companyId) return null
            const res = await api.commissions.getSummary(companyId)
            return res.data
        },
        enabled: !!companyId,
    })

    // ── Listado de Comisiones (Pendientes/Pagadas) ─────────────────────────
    const commissionsQuery = (status?: string, recipientId?: string) => useQuery({
        queryKey: ['commissions', companyId, status, recipientId],
        queryFn: async () => {
            if (!companyId) return []
            const res = await api.commissions.list({ 
                company_id: companyId, 
                status, 
                recipient_id: recipientId 
            })
            return res.data
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
    
    // Liquidar (Pagar)
    const payMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: PayCommissionPayload }) => 
            api.commissions.pay(id, data),
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
        generateMutation,
        createRecipient: createRecipientMutation,
        updateRecipient: updateRecipientMutation,
        deleteRecipient: deleteRecipientMutation,
        createRule: createRuleMutation,
        updateRule: updateRuleMutation,
        deleteRule: deleteRuleMutation,
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
