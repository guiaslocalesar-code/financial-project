from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import get_db
from app.routers import companies, clients, services, client_services, expenses, budgets, invoices, transactions, dashboard, income_budgets, upload, payment_methods, debts, commissions

app = FastAPI(
    title="Marketing Agency Financial API",
    description="Backend for managing agency finances, client invoicing (AFIP), and profitability.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redirect_slashes=False,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(companies.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(services.router, prefix="/api/v1")
app.include_router(client_services.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(income_budgets.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(payment_methods.router, prefix="/api/v1")
app.include_router(debts.router, prefix="/api/v1")
app.include_router(commissions.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Marketing Agency Financial API is running", "status": "ok"}

@app.get("/health/db")
async def db_health(migrate: bool = False, db = Depends(get_db)):
    try:
        from sqlalchemy import text
        if migrate:
            print("🚀 Starting manual migration from health endpoint...")
            # 1. Update 'companies' table
            await db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS afip_point_of_sale INTEGER"))
            await db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
            await db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            await db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            
            # 2. Create 'payment_methods' table
            await db.execute(text("""
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
            await db.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_method_id UUID REFERENCES payment_methods(id)"))
            
            # 4. Create 'debts' and 'debt_installments'
            await db.execute(text("""
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
            await db.execute(text("""
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
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS commission_recipients (
                    id UUID PRIMARY KEY,
                    company_id UUID NOT NULL REFERENCES companies(id),
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS commission_rules (
                    id UUID PRIMARY KEY,
                    recipient_id UUID NOT NULL REFERENCES commission_recipients(id) ON DELETE CASCADE,
                    client_id UUID REFERENCES clients(id),
                    service_id UUID REFERENCES services(id),
                    percentage NUMERIC(5, 2) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await db.execute(text("""
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
            
            await db.commit()
            return {"status": "ok", "message": "Migration completed successfully"}
            
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/inspect/db")
async def db_inspect(table_name: str, db = Depends(get_db)):
    try:
        from sqlalchemy import text
        res = await db.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"))
        return {"table": table_name, "columns": [{"name": row[0], "type": row[1]} for row in res]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
