from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import (
    companies, clients, services, client_services, 
    expenses, budgets, transactions, 
    dashboard, income_budgets, debts,
    auth, users, commissions,
    upload, payment_methods
)
try:
    from afip_integration.routers import invoices as afip_invoices
    _has_afip = True
except ImportError:
    _has_afip = False

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
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass  # static dir may not exist in container

# Include routers
app.include_router(companies.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(services.router, prefix="/api/v1")
app.include_router(client_services.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(income_budgets.router, prefix="/api/v1")
if _has_afip:
    app.include_router(afip_invoices.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(debts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(commissions.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(payment_methods.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Marketing Agency Financial API is running", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
