# 📘 Marketing Agency Financial API — Documentación del Backend

> **Versión:** 1.0.0  
> **Base URL:** `https://agente-financiero-backend-815637135726.us-east1.run.app`  
> **Docs interactivos:** `/docs`  
> **OpenAPI JSON:** `/openapi.json`  
> **Descripción:** Backend para gestión de finanzas de agencias de marketing, facturación AFIP y análisis de rentabilidad.

---

## 📋 Tabla de Contenidos

1. [Endpoints de Sistema](#-1-endpoints-de-sistema)
2. [Companies (Empresas)](#-2-companies-empresas)
3. [Clients (Clientes)](#-3-clients-clientes)
4. [Services (Servicios)](#-4-services-servicios)
5. [Client Services](#-5-client-services)
6. [Expenses Configuration](#-6-expenses-configuration)
7. [Expense Budgets](#-7-expense-budgets)
8. [Income Budgets](#-8-income-budgets)
9. [Invoices (Facturas AFIP)](#-9-invoices-facturas-afip)
10. [Transactions](#-10-transactions)
11. [Dashboard](#-11-dashboard)
12. [Upload](#-12-upload)
13. [Payment Methods](#-13-payment-methods)
14. [Debts (Deudas)](#-14-debts-deudas)
15. [Commissions (Comisiones)](#-15-commissions-comisiones)
16. [Users (Usuarios y Accesos)](#-16-users-usuarios-y-accesos)
17. [Schemas / Modelos](#-17-schemas--modelos)
18. [Enums](#-18-enums)

---

## 🔧 1. Endpoints de Sistema

### `GET /`
- **Descripción:** Health check raíz.
- **Auth:** No requerida
- **Response:** `200 OK` — objeto vacío

---

### `GET /health/db`
- **Descripción:** Verifica la conexión a la base de datos. Opcional: corre migraciones.
- **Auth:** No requerida
- **Query Params:**

| Param | Tipo | Requerido | Default | Descripción |
|-------|------|-----------|---------|-------------|
| `migrate` | boolean | No | `false` | Si `true`, ejecuta migraciones Alembic |

- **Response:** `200 OK` — objeto libre

---

### `GET /inspect/db`
- **Descripción:** Inspecciona el schema de una tabla de la base de datos.
- **Auth:** No requerida
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `table_name` | string | **Sí** | Nombre de la tabla a inspeccionar |

- **Response:** `200 OK` — objeto libre

---

## 🏢 2. Companies (Empresas)

### `GET /api/v1/companies`
- **Descripción:** Lista todas las empresas.
- **Response:** `array<CompanyResponse>`

---

### `POST /api/v1/companies`
- **Descripción:** Crea una nueva empresa.
- **Request Body:** `CompanyCreate`
- **Response:** `CompanyResponse`

---

### `GET /api/v1/companies/{company_id}`
- **Descripción:** Obtiene una empresa por ID.
- **Path Params:**

| Param | Tipo | Requerido |
|-------|------|-----------|
| `company_id` | uuid | **Sí** |

- **Response:** `CompanyResponse`

---

### `PUT /api/v1/companies/{company_id}`
- **Descripción:** Actualiza los datos de una empresa.
- **Path Params:**

| Param | Tipo | Requerido |
|-------|------|-----------|
| `company_id` | uuid | **Sí** |

- **Request Body:** `CompanyUpdate`
- **Response:** `CompanyResponse`

---

## 👥 3. Clients (Clientes)

### `POST /api/v1/clients`
- **Descripción:** Crea un nuevo cliente.
- **Request Body:** `ClientCreate`
- **Response:** `ClientResponse`

---

### `GET /api/v1/clients`
- **Descripción:** Lista los clientes de una empresa, con filtros opcionales.
- **Query Params:**

| Param | Tipo | Requerido | Default | Descripción |
|-------|------|-----------|---------|-------------|
| `company_id` | string | **Sí** | — | ID de la empresa |
| `is_active` | boolean | No | `null` | Filtrar por estado activo |
| `skip` | integer | No | `0` | Paginación: registros a saltear |
| `limit` | integer | No | `100` | Paginación: máximo de resultados |

- **Response:** `array<ClientResponse>`

---

### `GET /api/v1/clients/{client_id}`
- **Descripción:** Obtiene un cliente por ID.
- **Path Params:** `client_id` (string, requerido)
- **Response:** `ClientResponse`

---

### `PUT /api/v1/clients/{client_id}`
- **Descripción:** Actualiza los datos de un cliente.
- **Path Params:** `client_id` (string, requerido)
- **Request Body:** `ClientUpdate`
- **Response:** `ClientResponse`

---

### `DELETE /api/v1/clients/{client_id}`
- **Descripción:** Elimina (o desactiva) un cliente.
- **Path Params:** `client_id` (string, requerido)
- **Response:** `200 OK` — objeto vacío

---

## 🛠️ 4. Services (Servicios)

### `POST /api/v1/services`
- **Descripción:** Crea un nuevo servicio ofrecido por la agencia.
- **Request Body:** `ServiceCreate`
- **Response:** `ServiceResponse`

---

### `GET /api/v1/services`
- **Descripción:** Lista los servicios de una empresa.
- **Query Params:**

| Param | Tipo | Requerido |
|-------|------|-----------|
| `company_id` | uuid | **Sí** |

- **Response:** `array<ServiceResponse>`

---

### `PUT /api/v1/services/{service_id}`
- **Descripción:** Actualiza un servicio existente.
- **Path Params:** `service_id` (string, requerido)
- **Request Body:** `ServiceUpdate`
- **Response:** `ServiceResponse`

---

### `DELETE /api/v1/services/{service_id}`
- **Descripción:** Elimina un servicio.
- **Path Params:** `service_id` (string, requerido)
- **Response:** `200 OK` — objeto vacío

---

## 🔗 5. Client Services

Gestión de la relación entre Clientes y Servicios (tabla de junction + datos contractuales).

### `GET /api/v1/client-services/{client_id}`
- **Descripción:** Obtiene todos los servicios asignados a un cliente, con info del servicio embebida.
- **Path Params:** `client_id` (string, requerido)
- **Response:** `array<ClientServiceWithService>`

---

### `POST /api/v1/client-services/{client_id}`
- **Descripción:** Asigna un servicio a un cliente con precio mensual y fecha de inicio.
- **Path Params:** `client_id` (string, requerido)
- **Request Body:** `ClientServiceAssign`
- **Response:** `ClientServiceResponse`

---

### `PUT /api/v1/client-services/item/{id}`
- **Descripción:** Actualiza un client-service específico (fee, estado, fecha fin).
- **Path Params:** `id` (uuid, requerido)
- **Request Body:** `ClientServiceUpdate`
- **Response:** `ClientServiceResponse`

---

### `DELETE /api/v1/client-services/item/{id}`
- **Descripción:** Elimina la asignación de un servicio a un cliente.
- **Path Params:** `id` (uuid, requerido)
- **Response:** `200 OK` — objeto vacío

---

## 🗂️ 6. Expenses Configuration

Configuración de los tipos y categorías de gastos. Deben crearse antes de poder registrar presupuestos de gasto.

### `POST /api/v1/expenses/types`
- **Descripción:** Crea un tipo de gasto (ej: "Sueldos", "Marketing").
- **Request Body:** `ExpenseTypeCreate`
- **Response:** `ExpenseTypeResponse`

---

### `GET /api/v1/expenses/types`
- **Descripción:** Lista los tipos de gasto de una empresa.
- **Query Params:** `company_id` (uuid, requerido)
- **Response:** `array<ExpenseTypeResponse>`

---

### `POST /api/v1/expenses/categories`
- **Descripción:** Crea una categoría de gasto asociada a un tipo.
- **Request Body:** `ExpenseCategoryCreate`
- **Response:** `ExpenseCategoryResponse`

---

### `GET /api/v1/expenses/categories`
- **Descripción:** Lista las categorías de gasto de una empresa.
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | ID de la empresa |
| `expense_type_id` | uuid | No | Filtrar por tipo de gasto |

- **Response:** `array<ExpenseCategoryResponse>`

---

## 💸 7. Expense Budgets

Gestión de presupuestos de gastos por período. Al "pagar" un budget se genera automáticamente una Transaction.

### `POST /api/v1/budgets`
- **Descripción:** Crea un presupuesto de gasto.
- **Request Body:** `ExpenseBudgetCreate`
- **Response:** `ExpenseBudgetResponse`

---

### `GET /api/v1/budgets`
- **Descripción:** Lista los presupuestos de gasto con filtros opcionales.
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | ID de la empresa |
| `month` | integer (1-12) | No | Filtrar por mes |
| `year` | integer | No | Filtrar por año |
| `status` | `BudgetStatus` | No | Filtrar por estado (`PENDING`, `PAID`, `CANCELLED`) |

- **Response:** `array<ExpenseBudgetResponse>`

---

### `POST /api/v1/budgets/{budget_id}/pay`
- **Descripción:** Marca un presupuesto de gasto como pagado y crea la transacción correspondiente.
- **Path Params:** `budget_id` (uuid, requerido)
- **Query Params:**

| Param | Tipo | Requerido | Default | Descripción |
|-------|------|-----------|---------|-------------|
| `actual_amount` | number | No | `null` | Monto real pagado (si difiere del presupuestado) |
| `payment_method` | string | No | `"transfer"` | Método de pago utilizado |

- **Response:** `200 OK` — objeto vacío

---

## 💰 8. Income Budgets

Gestión de presupuestos de ingresos (cobranzas planificadas). Al "cobrar" se genera una Transaction.

### `POST /api/v1/income-budgets`
- **Descripción:** Crea un presupuesto de ingreso (cobro planificado de un cliente).
- **Request Body:** `IncomeBudgetCreate`
- **Response:** `IncomeBudgetResponse`

---

### `GET /api/v1/income-budgets`
- **Descripción:** Lista los presupuestos de ingreso con filtros opcionales.
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | ID de la empresa |
| `month` | integer (1-12) | No | Filtrar por mes |
| `year` | integer | No | Filtrar por año |
| `status` | `IncomeBudgetStatus` | No | `PENDING`, `COLLECTED`, `CANCELLED` |

- **Response:** `array<IncomeBudgetResponse>`

---

### `POST /api/v1/income-budgets/{budget_id}/collect`
- **Descripción:** Marca un budget de ingreso como cobrado y genera la transacción.
- **Path Params:** `budget_id` (uuid, requerido)
- **Request Body:** `IncomeBudgetCollect`
- **Response:** `200 OK` — objeto vacío

---

## 🧾 9. Invoices (Facturas AFIP)

Gestión de facturas electrónicas para AFIP (CAE). Flujo: crear borrador → emitir.

### `POST /api/v1/invoices`
- **Descripción:** Crea un borrador de factura (no toca AFIP todavía).
- **Request Body:** `InvoiceCreate`
- **Response:** `InvoiceResponse`

---

### `GET /api/v1/invoices`
- **Descripción:** Lista las facturas de una empresa.
- **Query Params:** `company_id` (uuid, requerido)
- **Response:** `array<InvoiceResponse>`

---

### `POST /api/v1/invoices/{invoice_id}/emit`
- **Descripción:** Emite una factura contra AFIP, obtiene el CAE y fecha de vencimiento.
- **Path Params:** `invoice_id` (uuid, requerido)
- **Response:** `200 OK` — objeto vacío

> ⚠️ **Nota:** La empresa debe tener configurados `afip_cert`, `afip_key` y `afip_point_of_sale`.

---

## 💳 10. Transactions

Registro inmutable de todos los movimientos financieros. Se generan automáticamente al pagar/cobrar un budget o emitir una factura.

### `GET /api/v1/transactions`
- **Descripción:** Lista todas las transacciones de una empresa.
- **Query Params:** `company_id` (uuid, requerido)
- **Response:** `array<TransactionResponse>`

---

### `GET /api/v1/transactions/{transaction_id}`
- **Descripción:** Obtiene el detalle de una transacción específica.
- **Path Params:** `transaction_id` (uuid, requerido)
- **Response:** `TransactionResponse`

---

## 📊 11. Dashboard

Endpoints de reportes financieros y rentabilidad.

### `GET /api/v1/dashboard/summary`
- **Descripción:** Resumen financiero del mes/año indicado (ingresos, gastos, resultado).
- **Query Params:**

| Param | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `month` | integer (1-12) | No | `3` (marzo) |
| `year` | integer | No | `2026` |

- **Response:** `200 OK` — objeto libre (estructura dinámica)

---

### `GET /api/v1/dashboard/profitability`
- **Descripción:** Reporte de rentabilidad por cliente/servicio.
- **Query Params:** `company_id` (uuid, requerido)
- **Response:** `200 OK` — objeto libre

---

### `GET /api/v1/dashboard/all`
- **Descripción:** Dashboard completo: combina summary + profitability en una sola llamada.
- **Query Params:**

| Param | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `month` | integer (1-12) | No | `3` |
| `year` | integer | No | `2026` |

- **Response:** `200 OK` — objeto libre

---

## 📎 12. Upload

### `POST /api/v1/upload`
- **Descripción:** Sube un archivo (imagen, certificado, etc.) y retorna la URL.
- **Content-Type:** `multipart/form-data`
- **Body:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `file` | binary | **Sí** |

- **Response:** `200 OK` — objeto con `additionalProperties: true` (JSON libre con URL)

---

## 💳 13. Payment Methods

Métodos de pago registrados por empresa (bancos, cajas, tarjetas).

### `POST /api/v1/payment-methods`
- **Request Body:** `PaymentMethodCreate`
- **Response:** `PaymentMethodResponse`

---

### `GET /api/v1/payment-methods`
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | ID de la empresa |
| `is_active` | boolean | No | Filtrar por estado activo |

- **Response:** `array<PaymentMethodResponse>`

---

### `GET /api/v1/payment-methods/{pm_id}`
- **Path Params:** `pm_id` (uuid, requerido)
- **Response:** `PaymentMethodResponse`

---

### `PUT /api/v1/payment-methods/{pm_id}`
- **Path Params:** `pm_id` (uuid, requerido)
- **Request Body:** `PaymentMethodUpdate`
- **Response:** `PaymentMethodResponse`

---

### `DELETE /api/v1/payment-methods/{pm_id}`
- **Path Params:** `pm_id` (uuid, requerido)
- **Response:** `200 OK` — objeto vacío

---

## 📉 14. Debts (Deudas)

Gestión de deudas con planes de cuotas e intereses.

### `POST /api/v1/debts`
- **Request Body:** `DebtCreate`
- **Response:** `DebtResponse`

---

### `GET /api/v1/debts`
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | ID de la empresa |
| `status` | string | No | Filtrar por estado (`PENDING`, `PAID`, `CANCELLED`) |

- **Response:** `array<DebtResponse>`

---

### `GET /api/v1/debts/{debt_id}`
- **Path Params:** `debt_id` (string, requerido)
- **Response:** `DebtResponse`

---

### `POST /api/v1/debts/{debt_id}/installments`
- **Descripción:** Crea una cuota para una deuda existente.
- **Path Params:** `debt_id` (string, requerido)
- **Request Body:** `DebtInstallmentCreate`
- **Response:** `DebtInstallmentResponse`

---

### `GET /api/v1/debts/{debt_id}/installments`
- **Descripción:** Lista todas las cuotas de una deuda.
- **Path Params:** `debt_id` (string, requerido)
- **Response:** `array<DebtInstallmentResponse>`

---

## 🤝 15. Commissions (Comisiones)

Sistema de comisiones para socios/vendedores basado en reglas por cliente/servicio.

### `POST /api/v1/commissions/recipients`
- **Descripción:** Crea un destinatario de comisiones (socio, vendedor, etc.).
- **Request Body:** `CommissionRecipientCreate`
- **Response:** `CommissionRecipientResponse` (incluye las reglas asociadas)

---

### `GET /api/v1/commissions/recipients`
- **Descripción:** Lista los destinatarios de comisiones de una empresa.
- **Query Params:** `company_id` (uuid, requerido)
- **Response:** `array<CommissionRecipientResponse>`

---

### `POST /api/v1/commissions/rules`
- **Descripción:** Crea una regla de comisión (% por cliente/servicio para un destinatario).
- **Request Body:** `CommissionRuleCreate`
- **Response:** `CommissionRuleResponse`

---

### `GET /api/v1/commissions`
- **Descripción:** Lista las comisiones generadas (instancias reales por transacción).
- **Query Params:**

| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `recipient_id` | uuid | No | Filtrar por destinatario |

- **Response:** `array<CommissionResponse>`

---

## 👤 16. Users (Usuarios y Accesos)

Control de acceso multi-empresa con roles y permisos granulares. Integrado con Supabase Auth.

### `GET /api/v1/users/companies/{company_id}`
- **Descripción:** Lista todos los usuarios con acceso a una empresa, incluyendo sus permisos.
- **Path Params:** `company_id` (uuid, requerido)
- **Response:** `array<UserCompanyResponse>`

---

### `POST /api/v1/users/companies/{company_id}`
- **Descripción:** Invita a un usuario (por email) a una empresa. El usuario debe existir previamente en Supabase. Si ya tiene acceso, retorna error 400.
- **Path Params:** `company_id` (uuid, requerido)
- **Request Body:** `UserCompanyInvite`
- **Response:** `UserCompanyResponse`

---

### `PUT /api/v1/users/user-companies/{user_company_id}`
- **Descripción:** Edita el rol y permisos granulares de un usuario en una empresa.
- **Path Params:** `user_company_id` (uuid, requerido)
- **Request Body:** `UserCompanyUpdate`
- **Response:** `UserCompanyResponse`

---

### `DELETE /api/v1/users/user-companies/{user_company_id}`
- **Descripción:** Desvincula lógicamente (baja) a un usuario de una empresa (no lo elimina del sistema).
- **Path Params:** `user_company_id` (uuid, requerido)
- **Response:** `200 OK` — objeto vacío

---

## 📦 17. Schemas / Modelos

### CompanyCreate
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string (max 255) | **Sí** | Nombre de la empresa |
| `cuit` | string (max 13) | **Sí** | CUIT sin guiones |
| `fiscal_condition` | `FiscalCondition` | **Sí** | Condición fiscal AFIP |
| `afip_point_of_sale` | integer | No | Punto de venta AFIP |
| `imagen` | string | No | URL de logo |
| `afip_cert` | string | No | Certificado AFIP (base64 o path) |
| `afip_key` | string | No | Clave privada AFIP |

### CompanyResponse
Extiende `CompanyCreate` con: `id` (uuid), `is_active` (bool), `created_at`, `updated_at`.  
> ⚠️ Nota: `afip_cert` y `afip_key` **NO** se retornan en el response por seguridad.

---

### ClientCreate
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `company_id` | uuid | **Sí** | Empresa a la que pertenece |
| `name` | string (max 255) | **Sí** | Nombre del cliente |
| `cuit_cuil_dni` | string (max 20) | **Sí** | Documento fiscal |
| `fiscal_condition` | `FiscalCondition` | **Sí** | Condición fiscal |
| `email` | email | No | — |
| `phone` | string (max 50) | No | — |
| `address` | string | No | — |
| `city` | string (max 100) | No | — |
| `province` | string (max 100) | No | — |
| `zip_code` | string (max 10) | No | — |
| `imagen` | string | No | URL de foto/logo |
| `id` | string (max 50) | No | ID personalizado (si no se provee, se auto-genera) |

### ClientResponse
Extiende `ClientCreate` con: `id` (string), `is_active`, `created_at`, `updated_at`.

### ClientUpdate
Todos los campos opcionales: `id`, `name`, `cuit_cuil_dni`, `fiscal_condition`, `email`, `phone`, `address`, `city`, `province`, `zip_code`, `imagen`, `is_active`.

---

### ServiceCreate
| Campo | Tipo | Requerido |
|-------|------|-----------|
| `company_id` | uuid | **Sí** |
| `name` | string (max 100) | **Sí** |
| `description` | string | No |
| `icon` | string | No |

### ServiceResponse
Extiende `ServiceCreate` con: `id`, `is_active`, `created_at`, `updated_at`.

### ServiceUpdate
Todos opcionales: `name`, `description`, `icon`, `is_active`.

### ServiceShort (embebido en ClientServiceWithService)
| Campo | Tipo |
|-------|------|
| `id` | string |
| `name` | string |

---

### ClientServiceAssign
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `service_id` | string | **Sí** | — |
| `monthly_fee` | number | **Sí** | — |
| `currency` | string | No | `"ARS"` |
| `start_date` | date | **Sí** | — |

### ClientServiceResponse
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | uuid | — |
| `client_id` | string | — |
| `service_id` | string | — |
| `monthly_fee` | number | — |
| `currency` | string | Default: ARS |
| `start_date` | date | — |
| `end_date` | date | Puede ser null |
| `status` | `ServiceStatus` | Default: ACTIVE |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

### ClientServiceWithService
Extiende `ClientServiceResponse` con: `service` (`ServiceShort` o null).

### ClientServiceUpdate
Todos opcionales: `monthly_fee`, `status` (`ServiceStatus`), `end_date`.

---

### ExpenseTypeCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `name` | string | **Sí** | — |
| `applies_to` | string | No | `"BOTH"` |

### ExpenseTypeResponse
Agrega: `id`, `applies_to` (`AppliesTo`), `is_active`, `created_at`, `updated_at`.

### ExpenseCategoryCreate
| Campo | Tipo | Requerido |
|-------|------|-----------|
| `company_id` | uuid | **Sí** |
| `expense_type_id` | uuid | **Sí** |
| `name` | string | **Sí** |

### ExpenseCategoryResponse
Agrega: `id`, `is_active`, `created_at`, `updated_at`.

---

### ExpenseBudgetCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `expense_type_id` | uuid | **Sí** | — |
| `expense_category_id` | uuid | **Sí** | — |
| `description` | string | **Sí** | — |
| `budgeted_amount` | number | **Sí** | — |
| `planned_date` | date | **Sí** | — |
| `period_month` | integer | **Sí** | — |
| `period_year` | integer | **Sí** | — |
| `is_recurring` | boolean | No | `false` |
| `status` | `BudgetStatus` | No | `PENDING` |

### ExpenseBudgetResponse
Agrega: `id`, `actual_amount`, `transaction_id`, `created_at`, `updated_at`.

---

### IncomeBudgetCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `client_id` | string | **Sí** | — |
| `service_id` | string | **Sí** | — |
| `budgeted_amount` | number | **Sí** | — |
| `planned_date` | date | **Sí** | — |
| `period_month` | integer | **Sí** | — |
| `period_year` | integer | **Sí** | — |
| `is_recurring` | boolean | No | `true` |
| `notes` | string | No | — |

### IncomeBudgetResponse
Agrega: `id`, `actual_amount`, `status`, `transaction_id`, `amount`, `description`, `client_name`, `service_name`, `created_at`, `updated_at`.

### IncomeBudgetCollect
| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `actual_amount` | number | null | Monto real cobrado |
| `payment_method` | string | `"transfer"` | Método de cobro |

---

### InvoiceCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `client_id` | string | **Sí** | — |
| `invoice_type` | `InvoiceType` | **Sí** | — |
| `point_of_sale` | integer | **Sí** | — |
| `issue_date` | date | No | — |
| `due_date` | date | No | — |
| `currency` | string | No | `"ARS"` |
| `exchange_rate` | number | No | `1.0` |
| `notes` | string | No | — |
| `items` | `array<InvoiceItemCreate>` | **Sí** | — |

### InvoiceItemCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `description` | string | **Sí** | — |
| `unit_price` | number | **Sí** | — |
| `service_id` | string | No | — |
| `quantity` | number | No | `1.0` |
| `iva_rate` | number | No | `21.0` |

### InvoiceResponse
Agrega: `id`, `invoice_number`, `cae`, `cae_expiry`, `subtotal`, `iva_amount`, `total`, `status` (`InvoiceStatus`), `created_at`, `updated_at`, `items` (array de `InvoiceItemResponse`).

### InvoiceItemResponse
Agrega: `id`, `subtotal`, `created_at`.

---

### TransactionResponse
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | uuid | **Sí** | — |
| `company_id` | uuid | **Sí** | — |
| `type` | `TransactionType` | **Sí** | INCOME o EXPENSE |
| `amount` | number | **Sí** | — |
| `currency` | string | No | Default: ARS |
| `exchange_rate` | number | No | Default: 1.0 |
| `is_budgeted` | boolean | No | False = gasto no presupuestado |
| `expense_origin` | `ExpenseOrigin` | No | BUDGETED o UNBUDGETED |
| `client_id` | string | No | — |
| `invoice_id` | uuid | No | — |
| `budget_id` | uuid | No | — |
| `service_id` | string | No | — |
| `expense_type_id` | uuid | No | — |
| `expense_category_id` | uuid | No | — |
| `payment_method_id` | string | No | — |
| `payment_method` | `PaymentMethod` | No | — |
| `description` | string | No | — |
| `transaction_date` | date | No | — |
| `created_at` | datetime | **Sí** | — |
| `updated_at` | datetime | **Sí** | — |

---

### PaymentMethodCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `name` | string (max 100) | **Sí** | — |
| `type` | `PaymentMethodType` | **Sí** | — |
| `company_id` | uuid | **Sí** | — |
| `bank` | string (max 100) | No | — |
| `is_credit` | boolean | No | `false` |
| `closing_day` | integer (1-31) | No | — |
| `due_day` | integer (1-31) | No | — |

### PaymentMethodResponse
Agrega: `id`, `is_active`, `created_at`, `updated_at`.

---

### DebtCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `company_id` | uuid | **Sí** | — |
| `description` | string | **Sí** | — |
| `original_amount` | number | **Sí** | — |
| `total_amount` | number | **Sí** | — |
| `interest_type` | `InterestType` | No | — |
| `interest_rate` | number | No | — |
| `installments` | integer | No | `1` |

### DebtResponse
Agrega: `id`, `status` (`DebtStatus`), `created_at`, `updated_at`, `debt_installments` (array).

### DebtInstallmentCreate
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `debt_id` | string | **Sí** | — |
| `installment_number` | integer | **Sí** | — |
| `amount` | number | **Sí** | — |
| `due_date` | date | **Sí** | — |
| `status` | `DebtStatus` | No | `PENDING` |

### DebtInstallmentResponse
Agrega: `id`, `transaction_id`, `created_at`, `updated_at`.

---

### CommissionRecipientCreate
| Campo | Tipo | Requerido |
|-------|------|-----------|
| `name` | string (max 255) | **Sí** |
| `company_id` | uuid | **Sí** |
| `email` | string (max 255) | No |

### CommissionRecipientResponse
Agrega: `id`, `created_at`, `rules` (array de `CommissionRuleResponse`).

### CommissionRuleCreate
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `recipient_id` | string | **Sí** | Destinatario de la comisión |
| `percentage` | number | **Sí** | Porcentaje de comisión (ej: 10.0 = 10%) |
| `client_id` | string | No | Aplicar solo a este cliente |
| `service_id` | string | No | Aplicar solo a este servicio |

### CommissionRuleResponse
Agrega: `id`, `created_at`.

### CommissionResponse
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | uuid | — |
| `transaction_id` | uuid | Transacción que originó la comisión |
| `recipient_id` | string | Destinatario |
| `amount` | number | Monto calculado |
| `status` | `CommissionStatus` | PENDING o PAID |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

---

### UserCompanyInvite
| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `email` | email | **Sí** | — |
| `role` | `CompanyRole` | No | `"user"` |
| `permissions` | array<string> | No | — |
| `quotaparte` | number | No | — |

### UserCompanyResponse
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | uuid | ID del vínculo user-company |
| `user_id` | uuid | — |
| `company_id` | uuid | — |
| `role` | `CompanyRole` | — |
| `permissions` | array<string> | Permisos granulares |
| `quotaparte` | number | Porcentaje de participación |
| `is_active` | boolean | — |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |
| `user` | `UserResponse` | Info del usuario (embebida) |

### UserCompanyUpdate
Todos opcionales: `role`, `permissions`, `quotaparte`, `is_active`.

### UserResponse
| Campo | Tipo |
|-------|------|
| `id` | uuid |
| `email` | email |
| `name` | string |
| `avatar_url` | string |
| `is_active` | boolean |
| `google_id` | string |
| `last_login` | datetime |
| `created_at` | datetime |
| `updated_at` | datetime |

---

## 🏷️ 18. Enums

| Enum | Valores |
|------|---------|
| `FiscalCondition` | `RI`, `MONOTRIBUTO`, `EXENTO`, `CONSUMIDOR_FINAL` |
| `BudgetStatus` | `PENDING`, `PAID`, `CANCELLED` |
| `IncomeBudgetStatus` | `PENDING`, `COLLECTED`, `CANCELLED` |
| `ServiceStatus` | `ACTIVE`, `PAUSED`, `CANCELLED` |
| `InvoiceStatus` | `DRAFT`, `EMITTED`, `CANCELLED` |
| `InvoiceType` | `A`, `B`, `C` |
| `TransactionType` | `INCOME`, `EXPENSE` |
| `ExpenseOrigin` | `BUDGETED`, `UNBUDGETED` |
| `AppliesTo` | `BUDGETED`, `UNBUDGETED`, `BOTH` |
| `PaymentMethodType` | `BANK`, `CASH`, `CARD`, `OTHER` |
| `PaymentMethod` | `CASH`, `TRANSFER`, `CHECK`, `CARD`, `OTHER` |
| `CompanyRole` | `admin`, `user`, `owner`, `accountant` |
| `DebtStatus` | `PENDING`, `PAID`, `CANCELLED` |
| `InterestType` | `FIXED`, `VARIABLE` |
| `CommissionStatus` | `PENDING`, `PAID` |

---

## 🔄 Flujos Principales

### Flujo de Ingreso (Cobro de cliente)
```
1. Crear IncomeBudget (POST /income-budgets)
2. Cuando se cobra → POST /income-budgets/{id}/collect
   → Se crea automáticamente una Transaction de tipo INCOME
   → Si hay CommissionRules → se crean CommissionResponse automáticamente
```

### Flujo de Egreso (Pago de gasto)
```
1. Crear ExpenseBudget (POST /budgets)
2. Cuando se paga → POST /budgets/{id}/pay
   → Se crea automáticamente una Transaction de tipo EXPENSE
```

### Flujo de Facturación AFIP
```
1. Configurar empresa con afip_cert + afip_key + afip_point_of_sale
2. Crear borrador → POST /invoices
3. Revisar borrador
4. Emitir → POST /invoices/{id}/emit
   → Obtiene CAE de AFIP
   → Genera Transaction de tipo INCOME automáticamente
```

### Alta de Cliente con Servicios
```
1. POST /clients → crear cliente
2. POST /services → crear servicio (si no existe)
3. POST /client-services/{client_id} → asignar servicio con fee mensual
4. (Opcional) POST /commissions/rules → definir comisión por ese cliente/servicio
```
