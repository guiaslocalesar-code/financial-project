"""
Informe Completo Financiero - Marzo 2026
Fuente: Supabase REST API (usa HTTPS, sin necesidad de conexión TCP a Cloud SQL)
"""
import requests
import json
from decimal import Decimal
from scripts.migrar_supabase_rest import SUPABASE_URL, supabase_headers

def get(url, params=""):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{url}{params}", headers={
        **supabase_headers(False),
        "Prefer": "count=exact",
        "Range": "0-9999",
    })
    if r.status_code not in (200, 206):
        raise Exception(f"Error {r.status_code}: {r.text}")
    return r.json()

def run():
    # ─── INGRESOS Marzo 2026 ─────────────────────────────────────
    ingresos_raw = get(
        "transactions",
        "?type=eq.INCOME&transaction_date=gte.2026-03-01&transaction_date=lte.2026-03-31"
        "&select=id,transaction_date,amount,description&order=transaction_date"
    )
    
    # ─── income_budgets para cruzar cliente/servicio ─────────────
    budgets_raw = get(
        "income_budgets",
        "?period_year=eq.2026&period_month=eq.3"
        "&select=id,transaction_id,client_id,service_id"
    )
    budget_by_tx = {b["transaction_id"]: b for b in budgets_raw}

    # ─── clients lookup ─────────────────────────────────────────
    clients_raw = get("clients", "?select=id,name")
    clients = {c["id"]: c["name"] for c in clients_raw}

    # ─── services lookup ─────────────────────────────────────────
    services_raw = get("services", "?select=id,name")
    services = {str(s["id"]): s["name"] for s in services_raw}

    # ─── EGRESOS Marzo 2026 ─────────────────────────────────────
    egresos_raw = get(
        "transactions",
        "?type=eq.EXPENSE&transaction_date=gte.2026-03-01&transaction_date=lte.2026-03-31"
        "&select=id,transaction_date,amount,description,expense_type_id&order=transaction_date"
    )

    # ─── expense_types para nombre de categoría ─────────────────
    expense_types_raw = get("expense_types", "?select=id,name")
    etypes = {e["id"]: e["name"] for e in expense_types_raw}

    # ─── COMISIONES Marzo 2026 ───────────────────────────────────
    # Traer comisiones cuyos income_transaction_id estén en los ingresos de marzo
    tx_ids_ing = [t["id"] for t in ingresos_raw]
    # Las comisiones se cruzan via income_transaction_id
    comis_raw = get(
        "commissions",
        "?select=id,income_transaction_id,client_id,service_id,base_amount,commission_amount,status,recipient_id"
    )
    comis_marzo = [c for c in comis_raw if c["income_transaction_id"] in tx_ids_ing]

    # ─── recipients ─────────────────────────────────────────────
    recip_raw = get("commission_recipients", "?select=id,name")
    recip = {r["id"]: r["name"] for r in recip_raw}

    # ─── CÁLCULOS ────────────────────────────────────────────────
    total_ingresos   = sum(float(t["amount"]) for t in ingresos_raw)
    total_egresos    = sum(float(t["amount"]) for t in egresos_raw)
    total_comisiones = sum(float(c["commission_amount"]) for c in comis_marzo)
    resultado_neto   = total_ingresos - total_egresos - total_comisiones

    # ─── EGRESOS AGRUPADOS ───────────────────────────────────────
    from collections import defaultdict
    egr_agrup = defaultdict(lambda: {"total": 0.0, "ops": 0})
    for e in egresos_raw:
        cat = etypes.get(e["expense_type_id"], "Sin categoría")
        egr_agrup[cat]["total"] += float(e["amount"])
        egr_agrup[cat]["ops"]   += 1
    egr_agrup_sorted = sorted(egr_agrup.items(), key=lambda x: -x[1]["total"])

    # ─── GENERAR MARKDOWN ────────────────────────────────────────
    L = []
    L.append("# 📊 Informe Financiero Completo — Marzo 2026")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## 🔢 Resumen Ejecutivo")
    L.append("")
    L.append("| Concepto                          | Importe           |")
    L.append("|-----------------------------------|-------------------|")
    L.append(f"| 💰 Total Ingresos                 | $ {total_ingresos:>16,.2f} |")
    L.append(f"| 📤 Total Egresos                  | $ {total_egresos:>16,.2f} |")
    L.append(f"| 🤝 Total Comisiones (Guias 2.0)   | $ {total_comisiones:>16,.2f} |")
    L.append(f"| **📈 Resultado Neto**              | **$ {resultado_neto:>14,.2f}** |")
    L.append("")

    # ─── INGRESOS ────────────────────────────────────────────────
    L.append("---")
    L.append(f"## 💰 Ingresos ({len(ingresos_raw)} operaciones)")
    L.append("")
    # Mapear tx_id -> (client_id, service_id) via commissions
    comis_by_tx = {}
    for c in comis_marzo:
        comis_by_tx[c["income_transaction_id"]] = {
            "client_id": c["client_id"],
            "service_id": c["service_id"],
        }

    L.append("| Fecha      | Cliente                  | Servicio                   | Importe          |")
    L.append("|------------|--------------------------|----------------------------|------------------|")
    for t in ingresos_raw:
        info     = comis_by_tx.get(t["id"], {})
        cliente  = clients.get(info.get("client_id"), info.get("client_id") or "N/D")
        servicio = services.get(str(info.get("service_id","")), info.get("service_id") or "N/D")
        L.append(f"| {t['transaction_date']} | {str(cliente):<24} | {str(servicio):<26} | $ {float(t['amount']):>15,.2f} |")
    L.append(f"|            | | | **$ {total_ingresos:>15,.2f}** |")
    L.append("")

    # ─── EGRESOS AGRUPADOS ───────────────────────────────────────
    L.append("---")
    L.append(f"## 📤 Egresos por Categoría ({len(egresos_raw)} operaciones)")
    L.append("")
    L.append("| Categoría                                | Operaciones | Total             |")
    L.append("|------------------------------------------|-------------|-------------------|")
    for cat, v in egr_agrup_sorted:
        L.append(f"| {cat:<40} | {v['ops']:>11} | $ {v['total']:>16,.2f} |")
    L.append(f"|                                          |             | **$ {total_egresos:>14,.2f}** |")
    L.append("")

    # ─── EGRESOS DETALLE ─────────────────────────────────────────
    L.append("### Detalle de Egresos")
    L.append("")
    L.append("| Fecha      | Categoría                     | Descripción                     | Importe          |")
    L.append("|------------|-------------------------------|---------------------------------|------------------|")
    for e in egresos_raw:
        cat  = etypes.get(e["expense_type_id"], "Sin categoría")
        desc = (e.get("description") or "")[:31]
        L.append(f"| {e['transaction_date']} | {cat:<29} | {desc:<31} | $ {float(e['amount']):>15,.2f} |")
    L.append("")

    # ─── COMISIONES DETALLE ──────────────────────────────────────
    L.append("---")
    L.append(f"## 🤝 Comisiones — Guias 2.0 ({len(comis_marzo)} operaciones)")
    L.append("")
    L.append("| Cliente                  | Servicio                 | Base              | %     | Comisión          |")
    L.append("|--------------------------|--------------------------|-------------------|-------|-------------------|")
    for c in sorted(comis_marzo, key=lambda x: x["service_id"]):
        base      = float(c["base_amount"])
        com       = float(c["commission_amount"])
        pct       = round(com / base * 100, 2) if base else 0
        cli_name  = clients.get(c["client_id"], c["client_id"])
        srv_name  = services.get(str(c["service_id"]), c["service_id"])
        L.append(f"| {str(cli_name):<24} | {str(srv_name):<24} | $ {base:>16,.2f} | {pct:>5}% | $ {com:>16,.2f} |")
    L.append(f"|                          |                          |                   |       | **$ {total_comisiones:>14,.2f}** |")
    L.append("")
    L.append("---")
    L.append("")
    L.append("> Informe generado el 26/03/2026 · Fuente: Supabase · Todos los valores en ARS")

    report = "\n".join(L)
    print(report)
    with open("informe_completo_marzo_2026.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ Informe guardado en: informe_completo_marzo_2026.md")

if __name__ == "__main__":
    run()
