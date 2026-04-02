/** Shared types for the Holding Financial Portal */

export interface Brand {
    id: string
    name: string
    logoUrl?: string
    services?: any[]
}

export interface User {
    email: string
    name?: string
    picture?: string
    isSuperAdmin?: boolean
    globalRole?: string
    brands?: Brand[]
    aiPermissions?: any
}

// ── Finance Types ───────────────────────────────────────────────────────────

export interface Company {
    id: string
    name: string
    cuit: string
    fiscal_condition: 'RI' | 'MONOTRIBUTO' | 'EXENTO' | 'CONSUMIDOR_FINAL'
    address?: string
    phone?: string
    email?: string
    afip_point_of_sale?: number
    imagen?: string
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface Client {
    id: string
    company_id: string
    name: string
    cuit_cuil_dni: string
    fiscal_condition: string
    email?: string
    phone?: string
    address?: string
    city?: string
    province?: string
    zip_code?: string
    imagen?: string
    is_active: boolean
    requires_invoice?: boolean
    created_at: string
}

export interface Invoice {
    id: string
    company_id: string
    client_id: string
    invoice_type: 'A' | 'B' | 'C'
    invoice_number?: string
    point_of_sale?: number
    cae?: string
    cae_expiry?: string
    issue_date: string
    due_date?: string
    subtotal: number
    iva_rate: number
    iva_amount: number
    total: number
    currency: string
    status: 'DRAFT' | 'EMITTED' | 'CANCELLED'
    notes?: string
    created_at: string
    // Computed frontend fields
    client_name?: string;
    overdue_days?: number;
    client?: { 
        name: string;
        cuit_cuil_dni: string;
        fiscal_condition: string;
        address?: string;
    };
    items?: {
        id: string;
        service_id?: string;
        description: string;
        quantity: number;
        unit_price: number;
        iva_rate: number;
        subtotal: number;
    }[];
}

export interface Transaction {
    id: string
    company_id: string
    client_id?: string
    invoice_id?: string
    budget_id?: string
    income_budget_id?: string
    service_id?: string
    expense_type_id?: string
    expense_category_id?: string
    type: 'INCOME' | 'EXPENSE'
    is_budgeted?: boolean
    expense_origin?: string
    amount: number
    currency: string
    requires_invoice?: boolean
    iva_rate?: number
    iva_amount?: number
    exchange_rate?: number
    payment_method?: string
    description?: string
    transaction_date: string
    created_at: string
    updated_at?: string
    // Related objects (transformed)
    client?: { name: string }
    service?: { name: string }
    expense_type?: { name: string }
    expense_category?: { name: string }
}

export interface DashboardSummary {
    summary: {
        total_income: number;
        total_expenses: number;
        balance: number;
        pending_to_pay: number;
    };
    profitability: any[];
    rankings: any[];
    budget_vs_real: any[];
}

export interface ExpenseBudget {
    id: string;
    company_id: string;
    expense_type_id: string;
    expense_category_id: string;
    description: string;
    budgeted_amount: number;
    actual_amount?: number;
    planned_date: string;
    period_month: number;
    period_year: number;
    is_recurring: boolean;
    status: 'PENDING' | 'PAID' | 'CANCELLED';
    transaction_id?: string;
    created_at: string;
    // Relationships
    expense_type_name?: string;
    category_name?: string;
    expense_type?: { name: string };
    expense_category?: { name: string };
}

export interface IncomeBudget {
    id: string;
    company_id: string;
    client_id: string;
    service_id: string;
    description: string;
    amount: number;
    requires_invoice?: boolean;
    iva_rate?: number;
    iva_amount?: number;
    planned_date: string;
    period_month: number;
    period_year: number;
    is_recurring: boolean;
    status: 'PENDING' | 'COLLECTED' | 'CANCELLED';
    transaction_id?: string;
    created_at: string;
    // Relationships
    client_name?: string;
    service_name?: string;
    client?: { name: string };
    service?: { name: string };
}

export interface Service {
    id: string;
    company_id: string;
    name: string;
    description?: string;
    icon?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ClientService {
    id: string;
    client_id: string;
    service_id: string;
    monthly_fee: number;
    currency: string;
    start_date: string;
    end_date?: string;
    status: 'ACTIVE' | 'PAUSED' | 'CANCELLED';
    created_at: string;
    updated_at: string;
    // Relationships
    service_name?: string;
    client_name?: string;
    service?: { name: string; id: string };
    client?: { name: string };
}

export interface ExpenseType {
    id: string;
    company_id: string;
    name: string;
    applies_to: 'BUDGETED' | 'UNBUDGETED' | 'BOTH';
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ExpenseCategory {
    id: string;
    company_id: string;
    expense_type_id: string;
    name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    // Relationships
    expense_type_name?: string;
}

