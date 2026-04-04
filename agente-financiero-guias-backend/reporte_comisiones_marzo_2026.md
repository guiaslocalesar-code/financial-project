# Informe de Comisiones - Marzo 2026

Este informe detalla las comisiones generadas por los cobros realizados en marzo de 2026 y el estado de su liquidación.

## 🛠️ Estructura de Datos (Tablas Cruzadas)
Para este informe se cruzaron las siguientes tablas:
1.  **`commissions`**: Tabla principal que registra el monto de comisión y su estado (PENDING/PAID).
2.  **`commission_recipients`**: Contiene los nombres de los beneficiarios (vendedores/gestores).
3.  **`transactions`**: Se utilizó doblemente:
    *   Primero para filtrar las comisiones según la **fecha del ingreso** que las originó.
    *   Segundo para verificar si existe una **transacción de pago** realizada en el mes.

## 📊 Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Comisiones Generadas (Marzo)** | **$597,120.00** |
| **Comisiones Pagadas en este mes** | **$0.00** |
| **Saldo Pendiente de Liquidación** | **$597,120.00** |

## 👥 Desglose por Beneficiario
Montos generados por las ventas/cobros de Marzo 2026:

| Beneficiario | Comisiones Generadas | Base Imponible (Cobros) | Cant. Operaciones | Pagado (en Marzo) |
|---|---|---|---|---|
| Guias 2.0 | $597,120.00 | $4,253,000.00 | 20 | $0.00 |
