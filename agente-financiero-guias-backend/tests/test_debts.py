import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from decimal import Decimal
import uuid

# Reemplazar con el ID que obtuvimos
COMPANY_ID = "aeb56588-5e15-4ce2-b24b-065ebf842c44"

@pytest.mark.asyncio
async def test_crear_deuda_sin_interes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "payment_method_id": "pm_efectivo",
            "description": "Prueba deuda sin interes",
            "original_amount": 30000,
            "installments": 3,
            "interest_type": "none",
            "interest_rate": 0,
            "first_due_date": "2026-04-10"
        }
        response = await ac.post(f"/api/v1/debts?company_id={COMPANY_ID}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["original_amount"] == "30000.00"
        assert data["total_amount"] == "30000.00"
        assert len(data["installments_detail"]) == 3
        # Verificar cuotas = original/3
        for installment in data["installments_detail"]:
            assert installment["amount"] == "10000.00"

@pytest.mark.asyncio
async def test_crear_deuda_con_interes_fijo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "payment_method_id": "pm_credito",
            "description": "Compra equipo camara",
            "original_amount": 60000,
            "installments": 6,
            "interest_type": "fixed_rate",
            "interest_rate": 8.00,
            "first_due_date": "2026-04-15"
        }
        response = await ac.post(f"/api/v1/debts?company_id={COMPANY_ID}", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Interés fijo: 60000 * 0.08 * 6 = 28800
        # Total: 88800
        # Cuot: 88800 / 6 = 14800
        assert data["interest_total"] == "28800.00"
        assert data["total_amount"] == "88800.00"
        assert data["installment_amount"] == "14800.00"
        assert len(data["installments_detail"]) == 6
        assert data["installments_detail"][0]["interest_amount"] == "4800.00"
        assert data["installments_detail"][0]["capital_amount"] == "10000.00"

@pytest.mark.asyncio
async def test_pagar_cuota():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Crear deuda
        payload = {
            "payment_method_id": "pm_debito",
            "description": "Deuda para pagar",
            "original_amount": 10000,
            "installments": 2,
            "interest_type": "none",
            "interest_rate": 0,
            "first_due_date": "2026-04-01"
        }
        resp_create = await ac.post(f"/api/v1/debts?company_id={COMPANY_ID}", json=payload)
        debt = resp_create.json()
        installment_id = debt["installments_detail"][0]["id"]

        # 2. Pagar 1 cuota
        resp_pay = await ac.patch(f"/api/v1/debt-installments/{installment_id}/pay")
        assert resp_pay.status_code == 200
        assert resp_pay.json()["debt_status"] == 'partial'

        # 3. Pagar la segunda
        installment_id_2 = debt["installments_detail"][1]["id"]
        resp_pay_2 = await ac.patch(f"/api/v1/debt-installments/{installment_id_2}/pay")
        assert resp_pay_2.status_code == 200
        assert resp_pay_2.json()["debt_status"] == 'paid'

@pytest.mark.asyncio
async def test_proyeccion_cashflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/dashboard/cashflow-projection?company_id={COMPANY_ID}&months=6")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6
        # Verificar que aparezcan meses futuros
        assert "2026-04" in [d["mes"] for d in data]

@pytest.mark.asyncio
async def test_resumen_deuda():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/dashboard/debt-summary?company_id={COMPANY_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "deuda_total_activa" in data
        assert "proximas_cuotas" in data
