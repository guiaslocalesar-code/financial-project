"""
Informe Completo Financiero - Marzo 2026
Ingresos + Egresos + Comisiones
"""
from scripts.migrar_supabase_rest import connect_src
from datetime import date

FECHA_INICIO = date(2026, 3, 1)
FECHA_FIN    = date(2026, 3, 31)

def run():
    conn = connect_src()
    cur  = conn.cursor()

    # ─── INGRESOS ────────────────────────────────────────────────
    cur.execute("""
        SELECT
            t.transaction_date,
            c.customer_name AS cliente,
            sv.name         AS servicio,
            t.amount        AS importe
        FROM transactions t
        LEFT JOIN income_budgets ib ON ib.transaction_id = t.id
        LEFT JOIN clients c  ON c.id = ib.client_id
        LEFT JOIN services sv ON sv.id::text = ib.service_id::text
        WHERE t.type = 'INCOME'
          AND t.transaction_date BETWEEN %s AND %s
        ORDER BY t.transaction_date, cliente
    """, (FECHA_INICIO, FECHA_FIN))
    ingresos = cur.fetchall()

    # ─── EGRESOS ────────────────────────────────────────────────
    cur.execute("""
        SELECT
            t.transaction_date,
            COALESCE(ec.name, 'Sin categoría') AS categoria,
            t.description,
            t.amount
        FROM transactions t
        LEFT JOIN expense_types ec ON ec.id = t.expense_type_id
        WHERE t.type = 'EXPENSE'
          AND t.transaction_date BETWEEN %s AND %s
        ORDER BY categoria, t.transaction_date
    """, (FECHA_INICIO, FECHA_FIN))
    egresos = cur.fetchall()

    # ─── EGRESOS AGRUPADOS POR CATEGORIA ─────────────────────────
    cur.execute("""
        SELECT
            COALESCE(ec.name, 'Sin categoría') AS categoria,
            SUM(t.amount) AS total,
            COUNT(*) AS operaciones
        FROM transactions t
        LEFT JOIN expense_types ec ON ec.id = t.expense_type_id
        WHERE t.type = 'EXPENSE'
          AND t.transaction_date BETWEEN %s AND %s
        GROUP BY categoria
        ORDER BY total DESC
    """, (FECHA_INICIO, FECHA_FIN))
    egresos_agrupados = cur.fetchall()

    # ─── COMISIONES ──────────────────────────────────────────────
    cur.execute("""
        SELECT
            t.transaction_date,
            cm.client_id           AS cliente_id,
            cm.service_id          AS servicio_id,
            r.name                  AS destinatario,
            cm.base_amount         AS base,
            cm.commission_amount   AS comision,
            ROUND((cm.commission_amount / NULLIF(cm.base_amount,0) * 100)::numeric, 2) AS porcentaje
        FROM commissions cm
        JOIN transactions t ON t.id = cm.income_transaction_id
        JOIN commission_recipients r ON r.id = cm.recipient_id
        WHERE t.transaction_date BETWEEN %s AND %s
        ORDER BY t.transaction_date, r.name
    """, (FECHA_INICIO, FECHA_FIN))
    comisiones = cur.fetchall()

    # ─── TOTALES ─────────────────────────────────────────────────
    total_ingresos   = sum(r[3] for r in ingresos)
    total_egresos    = sum(r[3] for r in egresos)
    total_comisiones = sum(r[5] for r in comisiones)
    resultado_neto   = total_ingresos - total_egresos - total_comisiones

    conn.close()

    # ─── IMPRIMIR MARKDOWN ───────────────────────────────────────
    lines = []
    lines.append("# 📊 Informe Financiero Completo — Marzo 2026")
    lines.append("")
    lines.append("---")
    lines.append("")

    # RESUMEN EJECUTIVO
    lines.append("## 🔢 Resumen Ejecutivo")
    lines.append("")
    lines.append("| Concepto                  | Importe          |")
    lines.append("|---------------------------|------------------|")
    lines.append(f"| 💰 Total Ingresos         | ${total_ingresos:>16,.2f} |")
    lines.append(f"| 📤 Total Egresos           | ${total_egresos:>16,.2f} |")
    lines.append(f"| 🤝 Total Comisiones        | ${total_comisiones:>16,.2f} |")
    lines.append(f"| **📈 Resultado Neto**      | **${resultado_neto:>14,.2f}** |")
    lines.append("")

    # INGRESOS
    lines.append("---")
    lines.append(f"## 💰 Ingresos ({len(ingresos)} operaciones)")
    lines.append("")
    lines.append("| Fecha      | Cliente                        | Servicio              | Importe        |")
    lines.append("|------------|--------------------------------|-----------------------|----------------|")
    for row in ingresos:
        fecha, cliente, servicio, importe = row
        lines.append(f"| {fecha} | {str(cliente or 'N/D'):<30} | {str(servicio or 'N/D'):<21} | ${float(importe):>13,.2f} |")
    lines.append(f"|            |                                | **TOTAL**             | **${float(total_ingresos):>12,.2f}** |")
    lines.append("")

    # EGRESOS AGRUPADOS
    lines.append("---")
    lines.append(f"## 📤 Egresos por Categoría ({len(egresos)} operaciones)")
    lines.append("")
    lines.append("| Categoría                              | Operaciones | Total           |")
    lines.append("|----------------------------------------|-------------|-----------------|")
    for row in egresos_agrupados:
        cat, total, ops = row
        lines.append(f"| {str(cat):<38} | {int(ops):>11} | ${float(total):>14,.2f} |")
    lines.append(f"|                                        |             | **${float(total_egresos):>13,.2f}** |")
    lines.append("")

    # EGRESOS DETALLE
    lines.append("### Detalle de Egresos")
    lines.append("")
    lines.append("| Fecha      | Categoría                     | Descripción                   | Importe        |")
    lines.append("|------------|-------------------------------|-------------------------------|----------------|")
    for row in egresos:
        fecha, cat, desc, importe = row
        lines.append(f"| {fecha} | {str(cat):<29} | {str(desc or '')[:29]:<29} | ${float(importe):>13,.2f} |")
    lines.append("")

    # COMISIONES
    lines.append("---")
    lines.append(f"## 🤝 Comisiones — Guias 2.0 ({len(comisiones)} operaciones)")
    lines.append("")
    lines.append("| Fecha      | Cliente  | Servicio | Destinatario | Base           | %     | Comisión       |")
    lines.append("|------------|----------|----------|--------------|----------------|-------|----------------|")
    for row in comisiones:
        fecha, cli, srv, dest, base, com, pct = row
        lines.append(f"| {fecha} | {str(cli):<8} | {str(srv):<8} | {str(dest):<12} | ${float(base):>13,.2f} | {float(pct):>5}% | ${float(com):>13,.2f} |")
    lines.append(f"|            |          |          |              |                |       | **${float(total_comisiones):>12,.2f}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> Informe generado el 26/03/2026 — Todos los valores en ARS")

    report = "\n".join(lines)
    print(report)
    with open("informe_completo_marzo_2026.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ Informe guardado en: informe_completo_marzo_2026.md")

if __name__ == "__main__":
    run()
