from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    companies, clients, services, client_services, 
    expenses, budgets, invoices, transactions, 
    dashboard, income_budgets, debts
)

app = FastAPI(
    title="Marketing Agency Financial API",
    description="Backend for managing agency finances, client invoicing (AFIP), and profitability.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(debts.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Marketing Agency Financial API is running", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
