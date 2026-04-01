/**
 * Commission Module Types
 */

export type CommissionRecipientType = 'supplier' | 'employee' | 'partner';
export type CommissionStatus = 'pending' | 'paid' | 'cancelled';
export type PaymentMethodType = 'transfer' | 'cash' | 'card' | 'check';

export interface CommissionRecipient {
    id: string;
    company_id: string;
    type: CommissionRecipientType;
    name: string;
    cuit: string;
    email: string;
    // Extended fields for summary/list
    total_commissions?: number;
    total_pending?: number;
    commission_count?: number;
    is_active?: boolean;
    created_at?: string;
}

export interface CommissionRule {
    id: string;
    company_id: string;
    recipient_id: string;
    client_id: string | null; // null = todos los clientes
    service_id: string | null; // null = todos los servicios
    percentage: number;
    // Relations (for display)
    recipient_name?: string;
    client_name?: string;
    service_name?: string;
}

export interface Commission {
    id: string;
    // Backend fields
    transaction_id?: string;
    recipient_id: string;
    amount?: number;             // from backend 'commission_amount' column
    status: string;              // PENDING | PAID (uppercase from backend)
    created_at: string;
    updated_at?: string;
    // Enriched fields (joined by backend)
    recipient_name?: string;
    client_name?: string;
    client_logo?: string;
    service_name?: string;
    transaction_description?: string;
    transaction_date?: string;
    // Legacy/frontend-only fields
    company_id?: string;
    base_amount?: number;
    commission_amount?: number;
    payment_date?: string;
    payment_method?: string;
    actual_amount?: number;
    payment_method_id?: string;
}

export interface TopRecipient {
    id: string;
    name: string;
    total_earned: number;
}

export interface CommissionDashboardSummary {
    // Backend returns English field names
    total_pending: number;
    total_paid: number;
    recipient_count: number;
    top_recipients: TopRecipient[];
    // Legacy aliases (in case old API still used)
    total_pendiente?: number;
    total_pagado?: number;
}

export interface RecipientSummary extends CommissionRecipient {
    stats: {
        total_earned: number;
        total_pending: number;
        performance_pct: number; // cumplimiento
        commission_history: Commission[];
    }
}

export interface CreateCommissionRecipient {
    company_id: string;
    type: CommissionRecipientType;
    name: string;
    cuit: string;
    email: string;
}

export interface CreateCommissionRule {
    company_id: string;
    recipient_id: string;
    client_id: string | null;
    service_id: string | null;
    percentage: number;
}

export interface PayCommissionPayload {
    payment_method: PaymentMethodType;
    payment_date: string;
    actual_amount?: number;
    payment_method_id?: string;
}
