import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migration():
    url = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:GuiasSA2020%40@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    print(f"Connecting to production DB...")
    
    engine = create_async_engine(url)
    
    try:
        async with engine.begin() as conn:
            print("Successfully connected!")
            
            # 1. Update 'companies' table
            print("Updating 'companies' table...")
            await conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS afip_point_of_sale INTEGER"))
            await conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
            await conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            await conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            print("'companies' table updated.")
            
            # 2. Create 'payment_methods' table
            print("Creating 'payment_methods' table...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id UUID PRIMARY KEY,
                    company_id UUID NOT NULL REFERENCES companies(id),
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    bank VARCHAR(100),
                    is_credit BOOLEAN DEFAULT FALSE,
                    closing_day INTEGER,
                    due_day INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 3. Update 'transactions' table
            print("Updating 'transactions' table...")
            await conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_method_id UUID REFERENCES payment_methods(id)"))
            print("'transactions' table updated.")
            
            # 4. Create 'debts' and 'debt_installments'
            print("Creating debt tables...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS debts (
                    id UUID PRIMARY KEY,
                    company_id UUID NOT NULL REFERENCES companies(id),
                    description VARCHAR(255) NOT NULL,
                    original_amount NUMERIC(12, 2) NOT NULL,
                    interest_rate NUMERIC(5, 2) DEFAULT 0,
                    installments INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS debt_installments (
                    id UUID PRIMARY KEY,
                    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
                    number INTEGER NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    due_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    transaction_id UUID REFERENCES transactions(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 5. Create 'commission' tables
            print("Creating commission tables...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS commission_recipients (
                    id UUID PRIMARY KEY,
                    company_id UUID NOT NULL REFERENCES companies(id),
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS commission_rules (
                    id UUID PRIMARY KEY,
                    recipient_id UUID NOT NULL REFERENCES commission_recipients(id) ON DELETE CASCADE,
                    client_id UUID REFERENCES clients(id),
                    service_id UUID REFERENCES services(id),
                    percentage NUMERIC(5, 2) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS commissions (
                    id UUID PRIMARY KEY,
                    transaction_id UUID NOT NULL REFERENCES transactions(id),
                    recipient_id UUID NOT NULL REFERENCES commission_recipients(id),
                    amount NUMERIC(12, 2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    payout_date TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            print("ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
            
    except Exception as e:
        print(f"FAILED during migration: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
