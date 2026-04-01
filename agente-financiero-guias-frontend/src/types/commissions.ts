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
    company_id: string;
    recipient_id: string;
    recipient_name: string;
    client_id: string;
    client_name: string;
    service_id: string;
    service_name: string;
    base_amount: number;
    commission_amount: number;
    status: CommissionStatus;
    created_at: string;
    payment_date?: string;
    payment_method?: PaymentMethodType;
    actual_amount?: number;
    payment_method_id?: string;
}

export interface TopRecipient {
    recipient_id: string;
    name: string;
    total_amount: number;
    count: number;
}

export interface CommissionDashboardSummary {
    total_pendiente: number;
    total_pagado: number;
    top_recipients: TopRecipient[];
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
