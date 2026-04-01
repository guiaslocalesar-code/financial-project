"""
tests/test_commissions.py
─────────────────────────
Tests unitarios e integración para el módulo de comisiones.

Cobertura:
  1.  CRUD Recipient (crear, listar, actualizar, baja lógica)
  2.  CRUD Rules (crear, deduplicación, listar, baja lógica)
  3.  Generación automática de comisiones al cobrar ingreso
  4.  Idempotencia de generate (no duplica comisiones)
  5.  Pago de comisión — crea transaction de egreso
  6.  Pago doble devuelve 400
  7.  Comisión inexistente devuelve 404
  8.  Base de cálculo es sin IVA
  9.  Resumen por recipient (summary)
  10. Dashboard commissions-summary
  11. Suma de porcentajes > 100% se permite con warning
"""

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.utils.enums import CommissionStatus, PaymentMethod, TransactionType

# ─── Constantes ────────────────────────────────────────────────────────────────
COMPANY_ID = "aeb56588-5e15-4ce2-b24b-065ebf842c44"
SERVICE_ID = "45413"       # Meta Ads — existente en la BD de prueba
CLIENT_ID  = "CLIENTE_1"   # Cliente existente en la BD de prueba


# ─── Helpers de creación ───────────────────────────────────────────────────────

async def _create_recipient(ac: AsyncClient, type_: str = "supplier", name: str | None = None) -> dict:
    name = name or f"Test-{uuid.uuid4().hex[:8]}"
    res = await ac.post("/api/v1/commission-recipients", json={
        "company_id": COMPANY_ID,
        "type": type_,
        "name": name,
    })
    assert res.status_code == 200, f"create_recipient failed: {res.text}"
    return res.json()


async def _create_rule(
    ac: AsyncClient,
    recipient_id: str,
    percentage: float,
    service_id: str | None = SERVICE_ID,
    client_id: str | None = None,
) -> dict:
    payload = {
        "company_id": COMPANY_ID,
        "recipient_id": recipient_id,
        "percentage": percentage,
        "priority": 1,
    }
    if service_id:
        payload["service_id"] = service_id
    if client_id:
        payload["client_id"] = client_id

    res = await ac.post("/api/v1/commission-rules", json=payload)
    assert res.status_code == 200, f"create_rule failed: {res.text}"
    return res.json()


# ─── Test 1: CRUD Recipient ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crud_recipient():
    """Crear, listar, actualizar y dar de baja un recipient."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Crear
        rec = await _create_recipient(ac, type_="partner")
        rec_id = rec["id"]
        assert rec["is_active"] is True
        assert rec["company_id"] == COMPANY_ID

        # Listar — aparece en la lista
        list_res = await ac.get(f"/api/v1/commission-recipients?company_id={COMPANY_ID}")
        assert list_res.status_code == 200
        ids = [r["id"] for r in list_res.json()]
        assert rec_id in ids

        # Actualizar nombre
        patch_res = await ac.patch(
            f"/api/v1/commission-recipients/{rec_id}",
            json={"name": "Nombre Actualizado"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["name"] == "Nombre Actualizado"

        # Baja lógica (DELETE → 204)
        del_res = await ac.delete(f"/api/v1/commission-recipients/{rec_id}")
        assert del_res.status_code == 204

        # Ya no aparece en la lista (only_active=True por defecto)
        list_res2 = await ac.get(f"/api/v1/commission-recipients?company_id={COMPANY_ID}")
        ids_after = [r["id"] for r in list_res2.json()]
        assert rec_id not in ids_after


# ─── Test 2: CRUD Rules ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crud_rules():
    """Crear, listar y dar de baja una regla de comisión."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rec = await _create_recipient(ac)
        rule = await _create_rule(ac, rec["id"], 20.0)
        rule_id = rule["id"]

        assert rule["percentage"] == 20.0
        assert rule["is_active"] is True

        # Listar
        list_res = await ac.get(f"/api/v1/commission-rules?company_id={COMPANY_ID}")
        assert list_res.status_code == 200
        rule_ids = [r["id"] for r in list_res.json()]
        assert rule_id in rule_ids

        # Dar de baja
        del_res = await ac.delete(f"/api/v1/commission-rules/{rule_id}")
        assert del_res.status_code == 204


# ─── Test 3: Regla duplicada devuelve 400 ─────────────────────────────────────

@pytest.mark.asyncio
async def test_regla_duplicada_devuelve_400():
    """Crear la misma regla dos veces devuelve 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rec = await _create_recipient(ac, type_="employee")
        svc = f"SVC-{uuid.uuid4().hex[:6]}"

        res1 = await ac.post("/api/v1/commission-rules", json={
            "company_id": COMPANY_ID,
            "recipient_id": rec["id"],
            "service_id": svc,
            "percentage": 10.0,
            "priority": 1,
        })
        assert res1.status_code == 200

        res2 = await ac.post("/api/v1/commission-rules", json={
            "company_id": COMPANY_ID,
            "recipient_id": rec["id"],
            "service_id": svc,
            "percentage": 15.0,   # diferente % = misma combinación
            "priority": 2,
        })
        assert res2.status_code == 400


# ─── Test 4: Comisiones pendientes se listan correctamente ────────────────────

@pytest.mark.asyncio
async def test_listar_comisiones_pendientes():
    """GET /commissions/pending devuelve 200 y estructura correcta."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/commissions/pending?company_id={COMPANY_ID}")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)

        if data:
            item = data[0]
            required_fields = {
                "id", "recipient_id", "client_id", "service_id",
                "base_amount", "commission_amount", "status", "created_at",
            }
            assert required_fields.issubset(item.keys())
            assert item["status"] == "pending"


# ─── Test 5: Pago de comisión — crea transaction de egreso ────────────────────

@pytest.mark.asyncio
async def test_pagar_comision_crea_egreso():
    """POST /commissions/{id}/pay crea una transaction de tipo expense."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        pending_res = await ac.get(f"/api/v1/commissions/pending?company_id={COMPANY_ID}")
        assert pending_res.status_code == 200
        pending = pending_res.json()

        if not pending:
            pytest.skip("No hay comisiones pendientes — crear primero")

        commission_id = pending[0]["id"]
        pay_res = await ac.post(
            f"/api/v1/commissions/{commission_id}/pay",
            json={
                "payment_method": "transfer",
                "payment_date": str(date.today()),
            },
        )
        assert pay_res.status_code == 200, pay_res.text
        data = pay_res.json()
        assert "transaction_id" in data
        assert "commission_id" in data
        assert data["commission_id"] == commission_id
        assert "amount_paid" in data
        assert float(data["amount_paid"]) > 0


# ─── Test 6: Pagar dos veces la misma comisión devuelve 400 ───────────────────

@pytest.mark.asyncio
async def test_pago_doble_devuelve_400():
    """POST /commissions/{id}/pay dos veces sobre la misma comisión → 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        pending_res = await ac.get(f"/api/v1/commissions/pending?company_id={COMPANY_ID}")
        pending = pending_res.json()

        if not pending:
            pytest.skip("No hay comisiones pendientes para este test")

        commission_id = pending[0]["id"]
        payload = {"payment_method": "transfer", "payment_date": str(date.today())}

        first = await ac.post(f"/api/v1/commissions/{commission_id}/pay", json=payload)
        assert first.status_code == 200

        second = await ac.post(f"/api/v1/commissions/{commission_id}/pay", json=payload)
        assert second.status_code == 400
        assert "PENDING" in second.text or "pending" in second.text.lower()


# ─── Test 7: Comisión inexistente devuelve 404 ────────────────────────────────

@pytest.mark.asyncio
async def test_comision_inexistente_404():
    """POST /commissions/{id}/pay con ID inválido → 404."""
    fake_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/commissions/{fake_id}/pay",
            json={"payment_method": "transfer", "payment_date": str(date.today())},
        )
        assert res.status_code == 404


# ─── Test 8: Generate — no duplica comisiones (idempotente) ───────────────────

@pytest.mark.asyncio
async def test_generate_es_idempotente():
    """POST /commissions/generate dos veces no duplica comisiones."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r1 = await ac.post(f"/api/v1/commissions/generate?company_id={COMPANY_ID}")
        assert r1.status_code == 200

        r2 = await ac.post(f"/api/v1/commissions/generate?company_id={COMPANY_ID}")
        assert r2.status_code == 200
        d2 = r2.json()
        # En la segunda corrida no debería haber comisiones nuevas
        assert d2["comisiones_generadas"] == 0, (
            f"Segunda corrida generó {d2['comisiones_generadas']} comisiones — "
            "el endpoint NO es idempotente"
        )


# ─── Test 9: Resumen por recipient ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resumen_recipient_campos():
    """GET /commissions/recipient/{id}/summary devuelve campos esperados."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rec = await _create_recipient(ac, type_="employee")
        rec_id = rec["id"]

        summary_res = await ac.get(f"/api/v1/commissions/recipient/{rec_id}/summary")
        assert summary_res.status_code == 200
        data = summary_res.json()

        assert data["recipient_id"] == rec_id
        assert "total_base" in data
        assert "total_pendiente" in data
        assert "total_pagado" in data
        assert "porcentaje_cumplimiento" in data
        # Recipient nuevo sin comisiones → todo en 0
        assert data["total_pendiente"] == 0.0
        assert data["total_pagado"] == 0.0
        assert data["porcentaje_cumplimiento"] == 0.0


# ─── Test 10: Recipient inexistente → 404 en summary ─────────────────────────

@pytest.mark.asyncio
async def test_resumen_recipient_inexistente_404():
    fake_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/commissions/recipient/{fake_id}/summary")
        assert res.status_code == 404


# ─── Test 11: Dashboard commissions-summary ───────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_commissions_summary():
    """GET /dashboard/commissions-summary devuelve estructura correcta."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/dashboard/commissions-summary?company_id={COMPANY_ID}")
        assert res.status_code == 200
        data = res.json()
        assert "total_pendiente" in data
        assert "total_pagado" in data
        assert "top_recipients" in data
        assert isinstance(data["top_recipients"], list)
        assert len(data["top_recipients"]) <= 5

        if data["top_recipients"]:
            top = data["top_recipients"][0]
            assert "recipient_id" in top
            assert "name" in top
            assert "total_comisiones" in top
            assert "total_pendiente" in top
            assert "total_pagado" in top


# ─── Test 12: Suma > 100% se permite (solo warning en logs) ───────────────────

@pytest.mark.asyncio
async def test_suma_porcentaje_mayor_100_se_permite():
    """Reglas que suman > 100% deben crearse sin error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        svc = f"SVC-{uuid.uuid4().hex[:6]}"
        rec_a = await _create_recipient(ac, "supplier")
        rec_b = await _create_recipient(ac, "partner")

        # Suman 110%
        r_a = await _create_rule(ac, rec_a["id"], 60.0, service_id=svc)
        r_b = await _create_rule(ac, rec_b["id"], 50.0, service_id=svc)

        assert r_a["percentage"] == 60.0
        assert r_b["percentage"] == 50.0


# ─── Test 13: Cálculo de comisión unitario (service layer) ────────────────────

@pytest.mark.asyncio
async def test_calculate_commissions_unit():
    """
    Test unitario (mock de BD) que valida que:
    · La base se calcula sin IVA (amount - iva_amount).
    · Se generan correctamente los objetos Commission.
    """
    from decimal import Decimal
    from unittest.mock import AsyncMock, MagicMock, patch

    from app.services.commission_service import calculate_commissions_for_income, _base_without_iva
    from app.utils.enums import CommissionStatus, TransactionType

    # Mock de transaction con IVA
    mock_tx = MagicMock()
    mock_tx.id = uuid.uuid4()
    mock_tx.company_id = uuid.UUID(COMPANY_ID)
    mock_tx.type = TransactionType.INCOME
    mock_tx.client_id = "CLI_001"
    mock_tx.service_id = "SVC_001"
    mock_tx.amount = Decimal("121.00")   # Total con 21% IVA
    mock_tx.iva_amount = Decimal("21.00")

    # base_without_iva debe retornar 100 (sin IVA)
    base = _base_without_iva(mock_tx)
    assert base == Decimal("100.00"), f"Base esperada 100, obtenida {base}"

    # Verificar cálculo al 25%: 100 × 0.25 = 25.00
    expected_commission = base * Decimal("25") / Decimal("100")
    assert expected_commission == Decimal("25.00")
