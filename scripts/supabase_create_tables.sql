
-- debt_installments
CREATE TABLE IF NOT EXISTS public.debt_installments (
    id UUID NOT NULL PRIMARY KEY,
    debt_id UUID NOT NULL REFERENCES public.debts(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    capital_amount NUMERIC(12, 2) NOT NULL,
    interest_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- commission_recipients
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recipienttype') THEN
        CREATE TYPE recipienttype AS ENUM ('SUPPLIER', 'EMPLOYEE', 'PARTNER');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.commission_recipients (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    type recipienttype NOT NULL,
    name VARCHAR(255) NOT NULL,
    cuit VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_commission_recipients_company
    ON public.commission_recipients (company_id, is_active);

-- commission_rules
CREATE TABLE IF NOT EXISTS public.commission_rules (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES public.commission_recipients(id),
    client_id VARCHAR(50),
    service_id VARCHAR(50),
    percentage NUMERIC(5, 2) NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    priority INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_commission_rule UNIQUE (company_id, recipient_id, client_id, service_id)
);
CREATE INDEX IF NOT EXISTS idx_commission_rules_company
    ON public.commission_rules (company_id, is_active);

-- commissions
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'commissionstatus') THEN
        CREATE TYPE commissionstatus AS ENUM ('PENDING', 'PAID', 'CANCELLED');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.commissions (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    income_transaction_id UUID NOT NULL REFERENCES public.transactions(id),
    commission_rule_id UUID REFERENCES public.commission_rules(id),
    recipient_id UUID NOT NULL REFERENCES public.commission_recipients(id),
    client_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(50) NOT NULL,
    base_amount NUMERIC(12, 2) NOT NULL,
    commission_amount NUMERIC(12, 2) NOT NULL,
    status commissionstatus NOT NULL DEFAULT 'PENDING',
    payment_transaction_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_commissions_income ON public.commissions (income_transaction_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON public.commissions (company_id, status);
