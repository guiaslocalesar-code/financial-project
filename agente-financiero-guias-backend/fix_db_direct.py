import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def add_column_direct():
    # Direct connection string (not pooled)
    # User: postgres
    # Password: GuiasSA2020@
    # Host: db.fumejzkghviszmyfjegg.supabase.co
    # Port: 5432
    # DB: postgres
    
    # URL encoded password: GuiasSA2020%40
    url = "postgresql+asyncpg://postgres:GuiasSA2020%40@db.fumejzkghviszmyfjegg.supabase.co:5432/postgres"
    print(f"Connecting directly to: db.fumejzkghviszmyfjegg.supabase.co")
    
    engine = create_async_engine(url)
    
    try:
        async with engine.begin() as conn:
            print("Adding payment_method_id column to transactions table...")
            await conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_method_id UUID REFERENCES payment_methods(id)"))
            print("Column added successfully or already exists.")
            
            print("Creating payment_methods table if not exists...")
            # I should also ensure payment_methods table exists since I'm here
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
            print("Tables checked/updated.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_column_direct())
