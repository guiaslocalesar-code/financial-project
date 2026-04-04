'use client'

import { useMemo, useEffect } from 'react'
import { useForm, useFieldArray, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useHoldingContext } from '@/context/HoldingContext'
import type { 
    InvoiceFormValues, 
    InvoicePreviewData, 
    InvoiceItemComputed, 
    InvoiceComputedTotals,
    InvoiceItemDraft 
} from '@/types/invoices'
import type { Client, Service, Invoice } from '@/types'

// ── Validation Schema ───────────────────────────────────────────────────────

const invoiceItemSchema = z.object({
    service_id: z.string().uuid('Debes seleccionar un servicio').optional().or(z.literal('')),
    description: z.string().min(1, 'La descripción es requerida'),
    quantity: z.number().min(0.01, 'Min > 0'),
    unit_price: z.number().min(0, 'Precio inválido'),
    iva_rate: z.number(),
})

const invoiceSchema = z.object({
    client_id: z.string().optional().default(''),
    
    // Campos de cliente (manual overrides)
    client_name: z.string().min(1, 'La razón social es requerida'),
    client_cuit: z.string().min(1, 'El CUIT/CUIL/DNI es requerido'),
    client_fiscal_condition: z.string().min(1, 'La condición de IVA es requerida'),
    client_address: z.string().default(''),

    invoice_type: z.enum(['A', 'B', 'C']),
    point_of_sale: z.number().min(1),
    issue_date: z.string().min(1, 'La fecha es requerida'),
    due_date: z.string().min(1, 'El vencimiento es requerido'),
    currency: z.string(),
    notes: z.string(),
    items: z.array(invoiceItemSchema).min(1, 'Debes agregar al menos un ítem'),
})

// ── Hook ────────────────────────────────────────────────────────────────────

interface UseInvoiceEditorProps {
    initialData?: Invoice | null
    onSuccess?: (invoice: Invoice) => void
}

export function useInvoiceEditor({ initialData, onSuccess }: UseInvoiceEditorProps = {}) {
    const queryClient = useQueryClient()
    const { selectedCompany } = useHoldingContext()

    // 1. Form Initialization
    const {
        register,
        control,
        handleSubmit,
        reset,
        setValue,
        watch,
        formState: { errors, isSubmitting },
    } = useForm<InvoiceFormValues>({
        resolver: zodResolver(invoiceSchema),
        defaultValues: {
            invoice_type: 'C',
            point_of_sale: selectedCompany?.afip_point_of_sale || 1,
            issue_date: new Date().toISOString().split('T')[0],
            due_date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            currency: 'ARS',
            client_id: '',
            client_name: '',
            client_cuit: '',
            client_fiscal_condition: 'CONSUMIDOR_FINAL',
            client_address: '',
            notes: '',
            items: [
                { service_id: '', description: '', quantity: 1, unit_price: 0, iva_rate: 21 }
            ],
        },
    })

    // Update form when initialData arrives (async fetch)
    useEffect(() => {
        if (initialData) {
            reset({
                invoice_type: initialData.invoice_type,
                point_of_sale: initialData.point_of_sale || selectedCompany?.afip_point_of_sale || 1,
                issue_date: initialData.issue_date,
                due_date: initialData.due_date || initialData.issue_date,
                currency: initialData.currency || 'ARS',
                client_id: initialData.client_id || '',
                client_name: initialData.client?.name || '',
                client_cuit: initialData.client?.cuit_cuil_dni || '',
                client_fiscal_condition: initialData.client?.fiscal_condition || '', 
                client_address: initialData.client?.address || '',
                notes: initialData.notes || '',
                items: initialData.items?.map(it => ({
                    service_id: it.service_id || '',
                    description: it.description,
                    quantity: it.quantity,
                    unit_price: it.unit_price,
                    iva_rate: it.iva_rate
                })) || [{ service_id: '', description: '', quantity: 1, unit_price: 0, iva_rate: 21 }]
            })
        }
    }, [initialData, reset, selectedCompany])

    const { fields, append, remove } = useFieldArray({
        control,
        name: 'items',
    })

    // 2. Data Fetching
    const { data: clients = [] } = useQuery({
        queryKey: ['clients', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.clients.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || res.data.clients || [])) as Client[]
        },
        enabled: !!selectedCompany,
    })

    const { data: services = [] } = useQuery({
        queryKey: ['services', selectedCompany?.id],
        queryFn: async () => {
            if (!selectedCompany) return []
            const res = await api.services.list(selectedCompany.id)
            return (Array.isArray(res.data) ? res.data : (res.data.data || [])) as Service[]
        },
        enabled: !!selectedCompany,
    })

    // 3. Real-time Preview Calculation
    const watchedValues = useWatch<InvoiceFormValues>({ control })

    // Auto-fill client data when client changes
    const currentClientId = watchedValues.client_id
    useEffect(() => {
        if (currentClientId) {
            const client = clients.find(c => c.id === currentClientId)
            if (client) {
                setValue('client_name', client.name)
                setValue('client_cuit', client.cuit_cuil_dni)
                setValue('client_fiscal_condition', client.fiscal_condition)
                setValue('client_address', [client.address, client.city].filter(Boolean).join(', '))
            }
        }
    }, [currentClientId, clients, setValue])

    const previewData = useMemo((): InvoicePreviewData => {
        const items = (watchedValues.items || []) as InvoiceItemDraft[]
        
        // Calculate items with subtotals
        const computedItems: InvoiceItemComputed[] = items.map(it => {
            const subtotal = (it.quantity || 0) * (it.unit_price || 0)
            const ivaAmount = subtotal * ((it.iva_rate || 0) / 100)
            return {
                ...it,
                _subtotal: subtotal,
                _iva_amount: ivaAmount
            }
        })

        // Calculate totals
        const totals: InvoiceComputedTotals = computedItems.reduce((acc, it) => {
            acc.subtotal += it._subtotal
            acc.iva += it._iva_amount
            acc.total += (it._subtotal + it._iva_amount)
            return acc
        }, { subtotal: 0, iva: 0, total: 0 })

        return {
            invoice_type: (watchedValues.invoice_type as any) || 'C',
            invoice_number: initialData?.invoice_number || null,
            point_of_sale: watchedValues.point_of_sale || 1,
            issue_date: watchedValues.issue_date || new Date().toISOString().split('T')[0],
            due_date: watchedValues.due_date || '',
            currency: watchedValues.currency || 'ARS',
            status: initialData?.status || 'DRAFT',
            cae: initialData?.cae || null,
            cae_expiry: initialData?.cae_expiry || null,
            notes: watchedValues.notes || '',
            items: computedItems,
            totals,
            company: {
                name: selectedCompany?.name || '',
                cuit: selectedCompany?.cuit || '',
                fiscal_condition: selectedCompany?.fiscal_condition || 'RI',
                afip_point_of_sale: selectedCompany?.afip_point_of_sale || 1,
                address: selectedCompany?.address,
                phone: selectedCompany?.phone,
                email: selectedCompany?.email,
                imagen: selectedCompany?.imagen
            },
            client: {
                name: watchedValues.client_name || 'Nombre del Cliente',
                cuit_cuil_dni: watchedValues.client_cuit || '—',
                fiscal_condition: watchedValues.client_fiscal_condition || '—',
                address: watchedValues.client_address || '',
                city: '',
                province: '',
                email: '',
                phone: ''
            }
        }
    }, [watchedValues, initialData, selectedCompany, clients])

    // 4. Persistence
    const mutation = useMutation({
        mutationFn: (data: InvoiceFormValues) => {
            if (!selectedCompany) throw new Error('No company selected')
            if (initialData?.id) {
                return api.invoices.update(initialData.id, data)
            }
            return api.invoices.create({
                ...data,
                company_id: selectedCompany.id,
            })
        },
        onSuccess: (res) => {
            const savedInvoice = res.data as Invoice
            queryClient.invalidateQueries({ queryKey: ['invoices', selectedCompany?.id] })
            queryClient.invalidateQueries({ queryKey: ['invoice', savedInvoice.id] })
            if (onSuccess) onSuccess(savedInvoice)
        }
    })

    const emitMutation = useMutation({
        mutationFn: async () => {
            if (!initialData?.id) throw new Error('Invoice not saved yet')
            return api.invoices.emit(initialData.id)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['invoices', selectedCompany?.id] })
            queryClient.invalidateQueries({ queryKey: ['invoice', initialData?.id] })
        }
    })

    const uploadLogoMutation = useMutation({
        mutationFn: async (file: File) => {
            if (!selectedCompany?.id) throw new Error('No company selected')
            return api.companies.updateLogo(selectedCompany.id, file)
        },
        onSuccess: () => {
            // Invalidate company queries to refresh the logo everywhere
            queryClient.invalidateQueries({ queryKey: ['companies'] })
            queryClient.invalidateQueries({ queryKey: ['company', selectedCompany?.id] })
            // If there's a global context query for the selected company, invalidate it too
        }
    })

    const onSubmit = (data: InvoiceFormValues) => {
        mutation.mutate(data)
    }

    return {
        register,
        control,
        errors,
        isSubmitting: isSubmitting || mutation.isPending || emitMutation.isPending || uploadLogoMutation.isPending,
        fields,
        append,
        remove,
        previewData,
        clients,
        services,
        onSubmit: handleSubmit(onSubmit),
        onEmit: () => emitMutation.mutate(),
        onUploadLogo: (file: File) => uploadLogoMutation.mutate(file),
        setValue,
        isValid: Object.keys(errors).length === 0,
        isDirty: Object.keys(errors).length > 0 || !!initialData
    }
}
