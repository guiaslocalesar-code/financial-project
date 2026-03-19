"""
Asegura que todos los tipos ENUM existan en Supabase antes de la migración.
"""
import asyncio
import os
from sqlalchemy import create_engine, text

TARGET_URL = "postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

ENUMS = {
    'recipienttype': "('INDIVIDUAL', 'AGENCY', 'OTHER')",
    'commissionstatus': "('PENDING', 'PAID', 'CANCELLED')",
    'transactiontype': "('INCOME', 'EXPENSE')",
    'expenseorigin': "('BUDGETED', 'AD_HOC')",
    'paymentmethod': "('CASH', 'TRANSFER', 'CREDIT_CARD', 'DEBIT_CARD', 'CHECK', 'OTHER')",
    'servicestatus': "('ACTIVE', 'INACTIVE', 'SUSPENDED')",
    'fiscalcondition': "('RESPONSABLE_INSCRIPTO', 'MONOTRIBUTISTA', 'EXENTO', 'CONSUMIDOR_FINAL')",
    'budgetstatus': "('PENDING', 'PAID', 'CANCELLED')",
    'incomebudgetstatus': "('PENDING', 'COLLECTED', 'CANCELLED')"
}

def setup_enums():
    engine = create_engine(TARGET_URL)
    with engine.connect() as conn:
        for name, values in ENUMS.items():
            print(f"Checking enum: {name}...", end=" ")
            try:
                # Verificar si ya existe
                res = conn.execute(text(f"SELECT 1 FROM pg_type WHERE typname = '{name}'"))
                if not res.scalar():
                    print(f"Creating...", end=" ")
                    conn.execute(text(f"CREATE TYPE {name} AS ENUM {values}"))
                    conn.commit()
                    print("✅")
                else:
                    print("exists.")
            except Exception as e:
                print(f"Error: {e}")
                conn.rollback()

if __name__ == "__main__":
    setup_enums()
