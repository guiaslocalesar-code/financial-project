# Detalle de Sueldos - Marzo 2026

Este informe detalla la asignación de dinero para salarios en el mes de marzo de 2026, comparando lo planificado contra los pagos realizados.

## ⚙️ Lógica de Cruce de Datos
Para generar este informe, se cruzaron las siguientes tablas de la base de datos:
1.  **`expense_types`**: Se filtró por la categoría `adc92130-eba1-4819-8631-746936317469` (Sueldos).
2.  **`expense_budgets`**: Es el origen de la planificación nominal. Cada fila representa un sueldo devengado para una persona o ítem específico.
3.  **`transactions`**: Muestra los pagos reales. Cada transacción de egreso vinculada a la categoría de Sueldos se restó del monto presupuestado correspondiente para determinar el saldo.

## 📊 Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Presupuesto Total Sueldos** | **$3,904,000.43** |
| **Total Pagado a la Fecha** | **$640,000.00** |
| **Saldos Pendientes** | **$3,264,000.43** |

## 👥 Desglose Nominal
Estado de pago para cada ítem de sueldo presupuestado:

| Descripción | Presupuestado | Pagado | Pendiente | Estado |
|---|---|---|---|---|
| Fernando Rivetti | $800,000.43 | $0.00 | $800,000.43 | pending |
| Leandro Mercado | $250,000.00 | $0.00 | $250,000.00 | pending |
| Johana Zamudio | $250,000.00 | $0.00 | $250,000.00 | pending |
| Leandro Mercado | $250,000.00 | $0.00 | $250,000.00 | pending |
| Leandro Mercado | $250,000.00 | $250,000.00 | $0.00 | paid |
| Johana Zamudio | $250,000.00 | $0.00 | $250,000.00 | pending |
| Leandro Mercado | $250,000.00 | $0.00 | $250,000.00 | pending |
| Johana Zamudio | $250,000.00 | $250,000.00 | $0.00 | paid |
| Johana Zamudio | $250,000.00 | $0.00 | $250,000.00 | pending |
| Facundo Fredes | $140,000.00 | $0.00 | $140,000.00 | pending |
| Facundo Fredes | $140,000.00 | $0.00 | $140,000.00 | pending |
| Facundo Fredes | $140,000.00 | $140,000.00 | $0.00 | paid |
| Facundo Fredes | $140,000.00 | $0.00 | $140,000.00 | pending |
| Romina Mercado | $136,000.00 | $0.00 | $136,000.00 | pending |
| Romina Mercado | $136,000.00 | $0.00 | $136,000.00 | pending |
| Romina Mercado | $136,000.00 | $0.00 | $136,000.00 | pending |
| Romina Mercado | $136,000.00 | $0.00 | $136,000.00 | pending |
