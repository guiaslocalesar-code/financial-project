# 📊 DATABASE SCHEMA — Agente Financiero Guías
> **Base de datos:** PostgreSQL 15 | **ORM:** SQLAlchemy 2.0 | **Cloud:** Cloud SQL GCP (`southamerica-east1`)

---

## 📌 Convenciones Globales

| Convención | Detalle |
|---|---|
| **PK** | Todos los IDs son `UUID` generado server-side (`uuid4`). Nunca se acepta ID del cliente. |
| **Monetario** | Todos los campos de dinero son `NUMERIC(12,2)`. |
| **Timestamps** | Toda tabla tiene `created_at` y `updated_at` con auto-update. |
| **Baja lógica** | Los registros NO se eliminan físicamente. Se usa `is_active = false`. |
| **Multi-empresa** | Cada entidad tiene `company_id` como discriminador para soportar múltiples empresas. |

---

## 🏢 TABLA 1: `companies`
**Propósito:** Entidad raíz del sistema. Representa cada empresa o agencia que usa la plataforma. Permite multi-empresa desde el día 1.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
<<<<<<< HEAD
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `name` | VARCHAR(255) | ❌ | — | Razón social de la empresa |
| `cuit` | VARCHAR(13) | ❌ | — | CUIT único de la empresa |
| `fiscal_condition` | ENUM | ❌ | — | Condición fiscal: `RI`, `monotributo`, `exento` |
| `afip_cert` | TEXT | ✅ | NULL | Certificado AFIP (encriptado con Fernet) |
| `afip_key` | TEXT | ✅ | NULL | Clave privada AFIP (encriptada) |
| `afip_point_of_sale` | INTEGER | ✅ | NULL | Número de punto de venta habilitado en AFIP |
| `imagen` | TEXT | ✅ | NULL | URL de la imagen/logo de la empresa |
=======
|--| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `name` | VARCHAR(255) | ❌ | — | Razón social de la empresa |
| `cuit` | VARCHAR(13) | ❌ | — | CUIT único de la empresa |
| `fiscal_condition` | ENUM | ❌ | — | Condición fiscal: `RI`, `monotributo`, `exento` |
| `imagen` | TEXT | ✅ | NULL | URL Logo de la empresa |
| `afip_cert` | TEXT | ✅ | NULL | Certificado AFIP (encriptado con Fernet) |
| `afip_key` | TEXT | ✅ | NULL | Clave privada AFIP (encriptada) |
| `afip_point_of_sale` | INTEGER | ✅ | NULL | Número de punto de venta habilitado en AFIP |
>>>>>>> financial-project/main
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **1 Company → N Clients** (`clients.company_id`)
- **1 Company → N Services** (`services.company_id`)
- **1 Company → N Invoices** (`invoices.company_id`)
- **1 Company → N ExpenseTypes** (`expense_types.company_id`)
- **1 Company → N ExpenseCategories** (`expense_categories.company_id`)
- **1 Company → N ExpenseBudgets** (`expense_budgets.company_id`)
- **1 Company → N IncomeBudgets** (`income_budgets.company_id`)
- **1 Company → N Transactions** (`transactions.company_id`)
<<<<<<< HEAD
- **1 Company → N PaymentMethods** (`payment_methods.company_id`)
- **1 Company → N Debts** (`debts.company_id`)
- **1 Company → N UserCompanies** (`user_companies.company_id`)
- **1 Company → N CommissionRecipients** (`commission_recipients.company_id`)
- **1 Company → N CommissionRules** (`commission_rules.company_id`)
- **1 Company → N Commissions** (`commissions.company_id`)
=======
>>>>>>> financial-project/main

---

## 👤 TABLA 2: `clients`
**Propósito:** Clientes de la agencia con todos los datos fiscales necesarios para emitir comprobantes AFIP (Facturas tipo A, B o C). El tipo de factura se determina automáticamente cruzando la condición fiscal de la empresa emisora y del cliente receptor.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
<<<<<<< HEAD
| `id` | VARCHAR(50) | ❌ | — | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(255) | ❌ | — | Razón social o nombre del cliente |
| `customer_name` | VARCHAR(255) | ✅ | NULL | Nombre completo del cliente (ej: "Juan García") |
| `customer_alias` | VARCHAR(100) | ✅ | NULL | Nombre corto o apodo (ej: "Juancho") |
=======
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(255) | ❌ | — | Razón social o nombre del cliente |
| `customer_name` | VARCHAR(255) | ✅ | — | Nombre de fantasía (opcional) |
| `customer_alias` | VARCHAR(100) | ✅ | — | Alias interno |
>>>>>>> financial-project/main
| `cuit_cuil_dni` | VARCHAR(20) | ❌ | — | Documento fiscal (CUIT, CUIL o DNI validado) |
| `fiscal_condition` | ENUM | ❌ | — | Condición: `RI`, `monotributo`, `consumidor_final`, `exento` |
| `email` | VARCHAR(255) | ✅ | NULL | Email de contacto |
| `phone` | VARCHAR(50) | ✅ | NULL | Teléfono |
| `address` | TEXT | ✅ | NULL | Dirección fiscal |
| `city` | VARCHAR(100) | ✅ | NULL | Ciudad |
| `province` | VARCHAR(100) | ✅ | NULL | Provincia |
| `zip_code` | VARCHAR(10) | ✅ | NULL | Código postal |
<<<<<<< HEAD
| `imagen` | TEXT | ✅ | NULL | URL de la imagen/logo del cliente (AppSheet) |
=======
| `imagen` | TEXT | ✅ | NULL | URL Logo del cliente |
>>>>>>> financial-project/main
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N Clients → 1 Company** (`company_id` FK)
- **1 Client → N ClientServices** (`client_services.client_id`)
- **1 Client → N Invoices** (`invoices.client_id`)
- **1 Client → N IncomeBudgets** (`income_budgets.client_id`)
- **1 Client → N Transactions** (`transactions.client_id`) — solo en ingresos

### Lógica de tipo de factura
| Empresa | Cliente | Tipo de Factura |
|---|---|---|
| `RI` | `RI` | **Factura A** |
| `RI` | `consumidor_final` o `monotributo` | **Factura B** |
| `monotributo` | cualquiera | **Factura C** |

=======
>>>>>>> financial-project/main
---

## 🛠️ TABLA 3: `services`
**Propósito:** Catálogo de servicios que la agencia ofrece. Debe existir el servicio aquí antes de asignarlo a un cliente. Permite vincular los ítems de facturas y transacciones a un servicio específico para calcular la rentabilidad por servicio.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
<<<<<<< HEAD
| `id` | VARCHAR(50) | ❌ | — | Primary Key |
=======
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
>>>>>>> financial-project/main
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre del servicio (ej: "Manejo de Redes", "Google Ads") |
| `description` | TEXT | ✅ | NULL | Descripción detallada del servicio |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N Services → 1 Company** (`company_id` FK)
- **1 Service → N ClientServices** (`client_services.service_id`)
- **1 Service → N InvoiceItems** (`invoice_items.service_id`)
- **1 Service → N IncomeBudgets** (`income_budgets.service_id`)
- **1 Service → N Transactions** (`transactions.service_id`)

=======
>>>>>>> financial-project/main
---

## 🔗 TABLA 4: `client_services`
**Propósito:** Relación Muchos-a-Muchos entre clientes y servicios. Registra el precio acordado con cada cliente por cada servicio contratado. Es la fuente de verdad del precio por cliente.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
<<<<<<< HEAD
| `client_id` | VARCHAR(50) | ❌ | — | FK → `clients.id` |
| `service_id` | VARCHAR(50) | ❌ | — | FK → `services.id` |
=======
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
| `service_id` | UUID | ❌ | — | FK → `services.id` |
>>>>>>> financial-project/main
| `monthly_fee` | NUMERIC(12,2) | ❌ | — | Precio mensual acordado con este cliente |
| `currency` | VARCHAR(3) | ❌ | `ARS` | Moneda del precio |
| `start_date` | DATE | ❌ | — | Fecha de inicio del contrato |
| `end_date` | DATE | ✅ | NULL | Fecha de fin (NULL = sigue activo) |
| `status` | ENUM | ❌ | `active` | Estado: `active`, `paused`, `cancelled` |
<<<<<<< HEAD
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Constraints
- `UNIQUE(client_id, service_id)` — No se puede asignar el mismo servicio dos veces al mismo cliente.

### Relaciones
- **N ClientServices → 1 Client** (`client_id` FK)
- **N ClientServices → 1 Service** (`service_id` FK)

=======
| `created_at" | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

>>>>>>> financial-project/main
---

## 🧾 TABLA 5: `invoices`
**Propósito:** Comprobantes emitidos a través de AFIP. Cada registro representa una factura electrónica. Puede estar en estado `draft` (borrador) antes de ser enviada a AFIP. Al emitirse, recibe el **CAE** (Código de Autorización Electrónica).

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
<<<<<<< HEAD
| `client_id` | VARCHAR(50) | ❌ | — | FK → `clients.id` |
=======
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
>>>>>>> financial-project/main
| `invoice_type` | ENUM | ❌ | — | Tipo: `A`, `B`, `C` |
| `invoice_number` | VARCHAR(20) | ✅ | NULL | Número generado por AFIP (ej: `0001-00000001`) |
| `point_of_sale` | INTEGER | ❌ | — | Punto de venta habilitado |
| `cae` | VARCHAR(20) | ✅ | NULL | Código de Autorización Electrónica (AFIP) |
| `cae_expiry` | DATE | ✅ | NULL | Vencimiento del CAE |
| `issue_date` | DATE | ❌ | `current_date` | Fecha de emisión |
| `due_date` | DATE | ✅ | NULL | Fecha de vencimiento de pago |
| `subtotal` | NUMERIC(12,2) | ❌ | — | Subtotal antes de IVA |
| `iva_rate` | NUMERIC(5,2) | ❌ | `21` | Alícuota de IVA: 0, 10.5, 21, 27 |
| `iva_amount` | NUMERIC(12,2) | ✅ | NULL | Monto de IVA calculado |
| `total` | NUMERIC(12,2) | ❌ | — | Total final (subtotal + IVA) |
| `currency` | VARCHAR(3) | ❌ | `ARS` | Moneda |
| `exchange_rate` | NUMERIC(10,4) | ❌ | `1` | Tipo de cambio (para USD) |
| `status` | ENUM | ❌ | `draft` | Estado: `draft`, `emitted`, `cancelled` |
| `afip_raw_response` | JSONB | ✅ | NULL | Respuesta completa de AFIP (para debugging) |
| `notes` | TEXT | ✅ | NULL | Notas internas |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N Invoices → 1 Company** (`company_id` FK)
- **N Invoices → 1 Client** (`client_id` FK)
- **1 Invoice → N InvoiceItems** (`invoice_items.invoice_id`)
- **1 Invoice → N Transactions** (`transactions.invoice_id`)

### Flujo de estados
```
draft → [POST /invoices/{id}/emit] → emitted
draft → cancelled
emitted → cancelled
```

=======
>>>>>>> financial-project/main
---

## 📝 TABLA 6: `invoice_items`
**Propósito:** Líneas de detalle de cada factura (el desglose del "qué se cobró"). Vinculadas opcionalmente a un `service_id` para habilitar el cálculo de rentabilidad por servicio en el dashboard.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
<<<<<<< HEAD
| `invoice_id` | UUID | ❌ | — | FK → `invoices.id` |
| `service_id` | VARCHAR(50) | ✅ | NULL | FK → `services.id` (opcional, para métricas) |
=======
| `invoice_id" | UUID | ❌ | — | FK → `invoices.id` |
| `service_id` | UUID | ✅ | NULL | FK → `services.id` (opcional, para métricas) |
>>>>>>> financial-project/main
| `description` | TEXT | ❌ | — | Descripción del ítem (ej: "Manejo Redes Enero 2025") |
| `quantity` | NUMERIC(10,2) | ❌ | `1` | Cantidad |
| `unit_price` | NUMERIC(12,2) | ❌ | — | Precio unitario |
| `iva_rate` | NUMERIC(5,2) | ❌ | `21` | Alícuota IVA del ítem |
| `subtotal` | NUMERIC(12,2) | ❌ | — | `quantity × unit_price` (calculado) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

<<<<<<< HEAD
### Relaciones
- **N InvoiceItems → 1 Invoice** (`invoice_id` FK)
- **N InvoiceItems → 1 Service** (`service_id` FK, nullable)

=======
>>>>>>> financial-project/main
---

## 🗂️ TABLA 7: `expense_types`
**Propósito:** Clasificación mayor de egresos. Es una tabla de validación/catálogo. Debe crearse el tipo antes de poder crear categorías o presupuestos. Ejemplo: "Sueldos", "Gastos Operativos", "Impuestos".

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre del tipo (ej: "Sueldos") |
| `applies_to` | ENUM | ❌ | `both` | A qué aplica: `budgeted`, `unbudgeted`, `both` |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N ExpenseTypes → 1 Company** (`company_id` FK)
- **1 ExpenseType → N ExpenseCategories** (`expense_categories.expense_type_id`)
- **1 ExpenseType → N ExpenseBudgets** (`expense_budgets.expense_type_id`)
- **1 ExpenseType → N Transactions** (`transactions.expense_type_id`)

=======
>>>>>>> financial-project/main
---

## 🏷️ TABLA 8: `expense_categories`
**Propósito:** Subcategorías de egresos. Depende de un `expense_type`. Tabla de validación/catálogo. Permite un desglose más fino para reportes. Ejemplo (dentro de "Sueldos"): "Sueldo Junior", "Sueldo Senior", "Monotributo Freelance".

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `expense_type_id` | UUID | ❌ | — | FK → `expense_types.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre de la categoría (ej: "Alquiler oficina") |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
<<<<<<< HEAD
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **N ExpenseCategories → 1 Company** (`company_id` FK)
- **N ExpenseCategories → 1 ExpenseType** (`expense_type_id` FK)
- **1 ExpenseCategory → N ExpenseBudgets** (`expense_budgets.expense_category_id`)
- **1 ExpenseCategory → N Transactions** (`transactions.expense_category_id`)

=======
| `created_at" | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

>>>>>>> financial-project/main
---

## 📅 TABLA 9: `expense_budgets`
**Propósito:** Presupuesto mensual de egresos planificados. El usuario carga los egresos esperados para el mes. Los marcados como `is_recurring = true` se replican automáticamente cada mes al siguiente período. Al confirmarse el pago, se crea automáticamente un registro en `transactions`.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `expense_type_id` | UUID | ❌ | — | FK → `expense_types.id` |
| `expense_category_id` | UUID | ❌ | — | FK → `expense_categories.id` |
<<<<<<< HEAD
=======
| `debt_id` | UUID | ✅ | NULL | FK → `debts.id` (si el gasto es cuota de deuda) |
>>>>>>> financial-project/main
| `description` | TEXT | ❌ | — | Descripción del gasto planificado |
| `budgeted_amount` | NUMERIC(12,2) | ❌ | — | Monto presupuestado originalmente |
| `actual_amount` | NUMERIC(12,2) | ✅ | NULL | Monto real pagado (puede diferir del presupuestado) |
| `planned_date` | DATE | ❌ | — | Fecha en que se debe abonar |
| `period_month` | INTEGER | ❌ | — | Mes del período (1–12) |
| `period_year` | INTEGER | ❌ | — | Año del período |
| `is_recurring` | BOOLEAN | ❌ | `false` | Si `true`, se clona automáticamente cada mes |
| `status` | ENUM | ❌ | `pending` | Estado: `pending`, `paid`, `cancelled` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (se llena al pagar) |
<<<<<<< HEAD
| `debt_id` | UUID | ✅ | NULL | FK → `debts.id` (si el gasto corresponde a una cuota de deuda) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **N ExpenseBudgets → 1 Company** (`company_id` FK)
- **N ExpenseBudgets → 1 ExpenseType** (`expense_type_id` FK)
- **N ExpenseBudgets → 1 ExpenseCategory** (`expense_category_id` FK)
- **N ExpenseBudgets → 1 Debt** (`debt_id` FK, nullable)
- **1 ExpenseBudget → 1 Transaction** (`transaction_id` FK, se llena al pagar — puede ser NULL)

### Flujo de estados
```
pending → [POST /budgets/{id}/pay] → paid  (crea Transaction automáticamente)
pending → cancelled
```

### Lógica de recurrentes
Todos los registros con `is_recurring = true` al cierre de cada mes generan copias para el período siguiente con `status = pending`, copiando el `budgeted_amount` y avanzando `planned_date` un mes.

=======
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

>>>>>>> financial-project/main
---

## 📅 TABLA 10: `income_budgets`
**Propósito:** Presupuesto mensual de ingresos esperados (cobranza planificada). El usuario carga los cobros esperados mes a mes o usa facturación recurrente. Funciona en paralelo a `expense_budgets`.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
<<<<<<< HEAD
| `client_id` | VARCHAR(50) | ❌ | — | FK → `clients.id` |
| `service_id` | VARCHAR(50) | ❌ | — | FK → `services.id` |
=======
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
| `service_id` | UUID | ❌ | — | FK → `services.id` |
>>>>>>> financial-project/main
| `budgeted_amount` | NUMERIC(12,2) | ❌ | — | Monto original a cobrar |
| `actual_amount` | NUMERIC(12,2) | ✅ | NULL | Monto real cobrado |
| `planned_date` | DATE | ❌ | — | Fecha estimada de cobro |
| `period_month` | INTEGER | ❌ | — | Mes del período |
<<<<<<< HEAD
| `period_year` | INTEGER | ❌ | — | Año del período |
=======
| `period_year" | INTEGER | ❌ | — | Año del período |
>>>>>>> financial-project/main
| `is_recurring` | BOOLEAN | ❌ | `true` | Si `true`, se clona para el próximo mes |
| `status` | ENUM | ❌ | `pending` | Estado: `pending`, `collected`, `cancelled` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (se llena al cobrar) |
| `notes` | TEXT | ✅ | NULL | Notas internas |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N IncomeBudgets → 1 Company** (`company_id` FK)
- **N IncomeBudgets → 1 Client** (`client_id` FK)
- **N IncomeBudgets → 1 Service** (`service_id` FK)
- **1 IncomeBudget → 1 Transaction** (`transaction_id` FK, al cobrar)

### Flujo de estados
```
pending → [POST /income-budgets/{id}/collect] → collected  (crea Transaction automáticamente)
pending → cancelled
```

=======
>>>>>>> financial-project/main
---

## 💰 TABLA 11: `transactions`
**Propósito:** Registro central de todos los movimientos de dinero **reales** (ingresos y egresos efectivamente cobrados/pagados). Es la fuente de verdad para el dashboard, cálculo de rentabilidad, flujo de caja y balance. Cada peso que entró o salió debe estar aquí.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
<<<<<<< HEAD
| `client_id` | VARCHAR(50) | ✅ | NULL | FK → `clients.id` (solo en ingresos) |
| `invoice_id` | UUID | ✅ | NULL | FK → `invoices.id` (si el ingreso viene de una factura) |
| `budget_id` | UUID | ✅ | NULL | FK → `expense_budgets.id` (si el egreso vino del presupuesto) |
| `income_budget_id` | UUID | ✅ | NULL | FK → `income_budgets.id` (si el ingreso vino de cobranza presupuestada) |
| `service_id` | VARCHAR(50) | ✅ | NULL | FK → `services.id` (para métricas de rentabilidad) |
=======
| `client_id` | UUID | ✅ | NULL | FK → `clients.id` (solo en ingresos) |
| `invoice_id` | UUID | ✅ | NULL | FK → `invoices.id` (si el ingreso viene de una factura) |
| `budget_id` | UUID | ✅ | NULL | FK → `expense_budgets.id` (si el egreso vino del presupuesto) |
| `income_budget_id` | UUID | ✅ | NULL | FK → `income_budgets.id` (si el ingreso vino de cobranza presupuestada) |
| `service_id` | UUID | ✅ | NULL | FK → `services.id` (para métricas de rentabilidad) |
>>>>>>> financial-project/main
| `expense_type_id` | UUID | ✅ | NULL | FK → `expense_types.id` (solo en egresos) |
| `expense_category_id` | UUID | ✅ | NULL | FK → `expense_categories.id` (solo en egresos) |
| `type` | ENUM | ❌ | — | Tipo: `income`, `expense` |
| `is_budgeted` | BOOLEAN | ❌ | `false` | Si el egreso fue presupuestado previamente |
| `expense_origin` | ENUM | ✅ | NULL | Origen del egreso: `budgeted`, `unbudgeted` |
| `amount` | NUMERIC(12,2) | ❌ | — | Monto real de la transacción |
| `currency` | VARCHAR(3) | ❌ | `ARS` | Moneda |
| `exchange_rate` | NUMERIC(10,4) | ❌ | `1` | Tipo de cambio |
<<<<<<< HEAD
| `payment_method` | ENUM | ✅ | NULL | Medio de pago (legacy/simple): `cash`, `transfer`, `check`, `card`, `other` |
| `payment_method_id` | VARCHAR(50) | ✅ | NULL | FK → `payment_methods.id` (detalle completo) |
=======
| `payment_method` | ENUM | ✅ | NULL | Método: `cash`, `transfer`, `check`, `card`, `other` (legacy) |
| `payment_method_id` | UUID | ✅ | NULL | FK → `payment_methods.id` (nuevo sistema) |
>>>>>>> financial-project/main
| `description` | TEXT | ✅ | NULL | Descripción del movimiento |
| `transaction_date` | DATE | ❌ | `current_date` | Fecha real del movimiento de dinero |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación del registro |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

<<<<<<< HEAD
### Relaciones
- **N Transactions → 1 Company** (`company_id` FK)
- **N Transactions → 1 Client** (`client_id` FK, nullable)
- **N Transactions → 1 Invoice** (`invoice_id` FK, nullable)
- **N Transactions → 1 ExpenseBudget** (`budget_id` FK, nullable)
- **N Transactions → 1 IncomeBudget** (`income_budget_id` FK, nullable)
- **N Transactions → 1 Service** (`service_id` FK, nullable)
- **N Transactions → 1 ExpenseType** (`expense_type_id` FK, nullable)
- **N Transactions → 1 ExpenseCategory** (`expense_category_id` FK, nullable)
- **N Transactions → 1 PaymentMethod** (`payment_method_id` FK, nullable)
- **1 Transaction → 1 Debt** (`debts.transaction_id`)
- **1 Transaction → 1 DebtInstallment** (`debt_installments.transaction_id`)

---

## 👤 TABLA 12: `users`
**Propósito:** Identidad de los usuarios del sistema. Los usuarios se crean automáticamente en su primer inicio de sesión mediante Google OAuth.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `google_id` | VARCHAR(255) | ❌ | — | ID único provisto por Google |
| `email` | VARCHAR(255) | ❌ | — | Email principal (único) |
| `name` | VARCHAR(255) | ✅ | NULL | Nombre completo |
| `avatar_url` | TEXT | ✅ | NULL | URL de la imagen de perfil |
| `is_active` | BOOLEAN | ❌ | `true` | Estado del usuario |
| `last_login` | TIMESTAMP | ✅ | NULL | Fecha del último acceso |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **1 User → N UserCompanies** (`user_companies.user_id`)

---

## 🏢 TABLA 13: `user_companies`
**Propósito:** Relación entre usuarios y empresas. Define los permisos y la participación accionaria (`quotaparte`) de cada usuario en cada agencia.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `user_id` | UUID | ❌ | — | FK → `users.id` |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `role` | ENUM | ❌ | `viewer` | Rol: `owner`, `admin`, `viewer` |
| `quotaparte` | NUMERIC(5,2) | ❌ | `0` | Porcentaje de participación (0-100%) |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica de la relación |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **N UserCompanies → 1 User** (`user_id` FK)
- **N UserCompanies → 1 Company** (`company_id` FK)

---

## 💳 TABLA 14: `payment_methods`
**Propósito:** Definición de medios de pago disponibles por empresa. Incluye cuentas bancarias (débito) y tarjetas de crédito con su lógica de cierre y vencimiento.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | VARCHAR(50) | ❌ | — | Primary Key (Slug único por empresa) |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre descriptivo (ej: "Galicia 1234") |
| `type` | VARCHAR(20) | ❌ | — | Tipo: `cash`, `transfer`, `credit_card`, `debit_card`, `financing` |
| `bank` | VARCHAR(100) | ✅ | NULL | Entidad bancaria |
| `is_credit` | BOOLEAN | ❌ | `false` | Indica si es tarjeta de crédito |
| `closing_day` | INTEGER | ✅ | NULL | Día de cierre (1-31, solo crédito) |
| `due_day` | INTEGER | ✅ | NULL | Día de vencimiento (1-31, solo crédito) |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

### Relaciones
- **N PaymentMethods → 1 Company** (`company_id` FK)
- **1 PaymentMethod → N Debts** (`debts.payment_method_id`)
- **1 PaymentMethod → N Transactions** (`transactions.payment_method_id`)

---

## 💸 TABLA 15: `debts`
**Propósito:** Gestión de deudas y préstamos (Pasivos). Registra el capital inicial, intereses y la planificación en cuotas. Cada cuota se vincula a `expense_budgets` para el flujo proyectado.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (desembolso inicial) |
| `payment_method_id` | VARCHAR(50) | ✅ | NULL | FK → `payment_methods.id` (donde se paga) |
| `description` | TEXT | ❌ | — | Concepto de la deuda |
| `original_amount` | NUMERIC(12,2) | ❌ | — | Capital solicitado |
| `interest_type` | VARCHAR(20) | ❌ | `none` | Tipo: `none`, `fixed_rate` |
| `interest_rate` | NUMERIC(6,2) | ❌ | `0` | Tasa de interés (TEM) |
| `interest_total` | NUMERIC(12,2) | ❌ | `0` | Interés total calculado al inicio |
| `total_amount` | NUMERIC(12,2) | ❌ | — | Capital + Intereses |
| `installments` | INTEGER | ❌ | `1` | Cantidad de cuotas |
| `installment_amount` | NUMERIC(12,2) | ❌ | — | Valor de cada cuotas |
| `first_due_date` | DATE | ❌ | — | Vencimiento de la primera cuota |
| `status` | VARCHAR(20) | ❌ | `active` | Estado: `active`, `partial`, `paid` |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

### Relaciones
- **N Debts → 1 Company** (`company_id` FK)
- **N Debts → 1 PaymentMethod** (`payment_method_id` FK)
- **N Debts → 1 Transaction** (`transaction_id` FK — desembolso)
- **1 Debt → N DebtInstallments** (`debt_installments.debt_id`)
- **1 Debt → N ExpenseBudgets** (`expense_budgets.debt_id`)

---

## 📈 TABLA 16: `debt_installments`
**Propósito:** Desglose de cada cuota de una deuda. Permite trackear el pago individual, discriminando capital e interés por cuota.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `debt_id` | UUID | ❌ | — | FK → `debts.id` |
| `installment_number` | INTEGER | ❌ | — | Nro de cuota (ej: 1, 2, 3...) |
| `due_date` | DATE | ❌ | — | Fecha de vencimiento |
| `amount` | NUMERIC(12,2) | ❌ | — | Valor total de la cuota |
| `capital_amount` | NUMERIC(12,2) | ❌ | — | Parte de capital |
| `interest_amount` | NUMERIC(12,2) | ❌ | — | Parte de interés |
| `status` | VARCHAR(20) | ❌ | `pending` | Estado: `pending`, `paid` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (pago de la cuota) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

### Relaciones
- **N DebtInstallments → 1 Debt** (`debt_id` FK)
- **N DebtInstallments → 1 Transaction** (`transaction_id` FK — pago)

---

## 🤝 TABLA 17: `commission_recipients`
**Propósito:** Catálogo de quiénes reciben comisiones (proveedores, empleados, socios). Cada recipient puede tener múltiples reglas de comisión por cliente y/o servicio.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|-­­­­--|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `type` | ENUM | ❌ | — | Tipo: `supplier`, `employee`, `partner` |
| `name` | VARCHAR(255) | ❌ | — | Nombre del recipient |
| `cuit` | VARCHAR(20) | ✅ | NULL | CUIT fiscal (opcional) |
| `email` | VARCHAR(255) | ✅ | NULL | Email de contacto |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

### Índices
- `idx_commission_recipients_company` ON `(company_id, is_active)`

### Relaciones
- **N CommissionRecipients → 1 Company** (`company_id` FK)
- **1 CommissionRecipient → N CommissionRules** (`commission_rules.recipient_id`)
- **1 CommissionRecipient → N Commissions** (`commissions.recipient_id`)

---

## 📐 TABLA 18: `commission_rules`
**Propósito:** Reglas de porcentaje de comisión por recipient, filtradas opcionalmente por cliente y/o servicio. Se aplican automáticamente al cobrar un ingreso. Permiten condiciones específicas (ej: sólo para Meta, sólo para un cliente) o genéricas (null = aplica a todos).

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `recipient_id` | UUID | ❌ | — | FK → `commission_recipients.id` |
| `client_id` | VARCHAR(50) | ✅ | NULL | FK → `clients.id` (NULL = aplica a todos) |
| `service_id` | VARCHAR(50) | ✅ | NULL | FK → `services.id` (NULL = aplica a todos) |
| `percentage` | NUMERIC(5,2) | ❌ | — | Porcentaje a aplicar sobre ingreso bruto |
| `priority` | INTEGER | ❌ | `1` | Orden de aplicación (ASC) |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

### Constraints
- `UNIQUE(company_id, recipient_id, client_id, service_id)` — evita reglas duplicadas.
- `CHECK (percentage >= 0 AND percentage <= 100)`

### Índices
- `idx_commission_rules_company` ON `(company_id, is_active)`

### Relaciones
- **N CommissionRules → 1 Company** (`company_id` FK)
- **N CommissionRules → 1 CommissionRecipient** (`recipient_id` FK)
- **1 CommissionRule → N Commissions** (`commissions.commission_rule_id`)

---

## 💸 TABLA 19: `commissions`
**Propósito:** Registro central de todas las comisiones calculadas sobre ingresos reales. Se generan **automáticamente** al cobrar un ingreso (`POST /income-budgets/{id}/collect`). La base de cálculo es siempre el **ingreso bruto** (`transaction.amount`), nunca la utilidad neta. Múltiples comisiones pueden existir por ingreso (suma de varios %).

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `income_transaction_id` | UUID | ❌ | — | FK → `transactions.id` (el ingreso que generó la comisión) |
| `commission_rule_id` | UUID | ✅ | NULL | FK → `commission_rules.id` (regla que originó esta comisión) |
| `recipient_id` | UUID | ❌ | — | FK → `commission_recipients.id` |
| `client_id` | VARCHAR(50) | ❌ | — | ID del cliente del ingreso |
| `service_id` | VARCHAR(50) | ❌ | — | ID del servicio del ingreso |
| `base_amount` | NUMERIC(12,2) | ❌ | — | Ingreso bruto (fuente del cálculo) |
| `commission_amount` | NUMERIC(12,2) | ❌ | — | Monto de la comisión (`base × %`) |
| `status` | ENUM | ❌ | `pending` | Estado: `pending`, `paid`, `cancelled` |
| `payment_transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (egreso generado al pagar) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

### Índices
- `idx_commissions_status` ON `(company_id, status)`
- `idx_commissions_income` ON `(income_transaction_id)`

### Relaciones
- **N Commissions → 1 Company** (`company_id` FK)
- **N Commissions → 1 Transaction** (`income_transaction_id` FK — ingreso origen)
- **N Commissions → 1 CommissionRule** (`commission_rule_id` FK, nullable)
- **N Commissions → 1 CommissionRecipient** (`recipient_id` FK)
- **N Commissions → 1 Transaction** (`payment_transaction_id` FK — pago, nullable)

### Flujo de estados
```
pending → [POST /commissions/{id}/pay] → paid  (crea Transaction expense automáticamente)
pending → cancelled
```

### Reglas de negocio
- **Base = ingreso bruto** (`transaction.amount`), NUNCA utilidad neta
- **Automático**: se calculan en el hook de `POST /income-budgets/{id}/collect`
- **Múltiples por ingreso**: varios recipients pueden comisionar el mismo ingreso
- **Si suma % > 100**: se permite pero se logea un `warning`

---

## 🔄 Diagrama de Relaciones

```
companies (1)
=======
---

## 💳 TABLA 12: `payment_methods`
**Propósito:** Catálogo de cuentas bancarias, cajas o tarjetas desde donde se mueve el dinero.

### Columnas
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre (Ej: "Galicia 1234", "Caja Pesos") |
| `type" | ENUM | ❌ | — | `bank`, `cash`, `card`, `other` |
| `bank` | VARCHAR(100) | ✅ | — | Nombre del banco |
| `is_credit` | BOOLEAN | ❌ | `false` | Si aplica cierre/vencimiento |
| `closing_day` | INTEGER | ✅ | — | Día de cierre (tarjetas) |
| `due_day` | INTEGER | ✅ | — | Día de vencimiento (tarjetas) |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | — |

---

## 📉 TABLA 13: `debts` (Pasivos)
**Propósito:** Registro de deudas a largo plazo o préstamos (ej: Préstamo Banco, Deuda con Socio).

### Columnas
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `transaction_id` | UUID | ✅ | NULL | FK inicial (ingreso por préstamo) |
| `payment_method_id` | UUID | ✅ | NULL | Cuenta destino del préstamo |
| `description` | TEXT | ❌ | — | Concepto |
| `original_amount` | NUMERIC | ❌ | — | Capital inicial |
| `interest_type` | ENUM | ✅ | — | `fixed`, `variable` |
| `interest_rate` | NUMERIC | ✅ | — | TNA/TEM |
| `interest_total` | NUMERIC | ✅ | — | Interés proyectado total |
| `total_amount` | NUMERIC | ❌ | — | Capital + Interés |
| `installments` | INTEGER | ❌ | `1` | Cantidad de cuotas |
| `installment_amount` | NUMERIC | ❌ | — | Valor cuota |
| `first_due_date` | DATE | ❌ | — | Vencimiento 1ra cuota |
| `status` | ENUM | ❌ | `pending` | `pending`, `paid`, `cancelled` |

---

## 👥 TABLA 14: `users` & `user_companies`
**Propósito:** Gestión de usuarios y permisos multi-empresa.

### `users`
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `google_id` | VARCHAR | ✅ | — | ID de Google Auth |
| `email` | VARCHAR | ❌ | — | Email principal |
| `name` | VARCHAR | ❌ | — | Nombre completo |
| `avatar_url` | TEXT | ✅ | — | Imagen perfil |

### `user_companies`
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `user_id` | UUID | ❌ | — | FK → `users.id` |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `role` | ENUM | ❌ | `user` | `admin`, `user`, `owner` |
| `quotaparte` | NUMERIC | ✅ | — | Porcentaje societario (para balances) |

---

## 🤝 TABLAS 15-17: Comisiones
**Propósito:** Gestión de comisiones para referidores, vendedores o colaboradores por cada ingreso.

### `commission_recipients`
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `name` | VARCHAR | ❌ | — | Nombre del colaborador |
| `type` | ENUM | ❌ | — | `fixed`, `percentage` (Legacy?) |

### `commission_rules`
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `recipient_id` | UUID | ❌ | — | FK → `recipients` |
| `client_id` | UUID | ✅ | — | Aplicar solo a este cliente |
| `service_id` | UUID | ✅ | — | Aplicar solo a este servicio |
| `percentage` | NUMERIC | ❌ | — | % a pagar |

### `commissions` (Transacciones de comisión)
| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | PK |
| `income_transaction_id` | UUID | ❌ | — | FK → `transactions` (el ingreso que la origina) |
| `commission_amount` | NUMERIC | ❌ | — | $ calculado |
| `status` | ENUM | ❌ | `pending` | `pending`, `paid` |

---

## 🔄 Diagrama de Relaciones (Actualizado)

```
companies (1)
├── users (N) via user_companies
>>>>>>> financial-project/main
├── clients (N)
│   └── client_services (N) ←→ services (N)
├── services (N)
│   └── invoice_items (N)
├── invoices (N)
│   └── invoice_items (N)
├── expense_types (N)
│   └── expense_categories (N)
│       └── expense_budgets (N)
<<<<<<< HEAD
│           └── transactions (1) [cuando se paga]
├── income_budgets (N)
│   └── transactions (1) [cuando se cobra]
│       └── commissions (N) [automáticas al cobrar]
├── commission_recipients (N)
│   └── commission_rules (N)
│       └── commissions (N)
├── users (N)
│   └── user_companies (N)
├── payment_methods (N)
│   └── debts (N)
│       └── debt_installments (N)
└── transactions (N)
    ├── → client (nullable)
    ├── → invoice (nullable)
    ├── → expense_budget (nullable)
    ├── → income_budget (nullable)
    ├── → service (nullable)
    ├── → expense_type (nullable)
    ├── → expense_category (nullable)
    ├── → payment_method (required or nullable)
    └── → debt_installments (nullable)
=======
│           ├── debts (cuotas)
│           └── transactions (1) [pago]
├── income_budgets (N)
│   └── transactions (1) [cobro]
├── payment_methods (N)
│   └── transactions (N)
├── debts (N)
│   └── debt_installments (N)
└── transactions (N)
    └── commissions (N)
>>>>>>> financial-project/main
```

---

<<<<<<< HEAD
## 🔗 ENUMs Disponibles

| ENUM | Valores |
|---|---|
| `fiscalcondition` | `RI`, `MONOTRIBUTO`, `EXENTO`, `CONSUMIDOR_FINAL` |
| `servicestatus` | `ACTIVE`, `PAUSED`, `CANCELLED` |
| `invoicetype` | `A`, `B`, `C` |
| `invoicestatus` | `DRAFT`, `EMITTED`, `CANCELLED` |
| `appliesto` | `BUDGETED`, `UNBUDGETED`, `BOTH` |
| `budgetstatus` | `PENDING`, `PAID`, `CANCELLED` |
| `incomebudgetstatus` | `PENDING`, `COLLECTED`, `CANCELLED` |
| `transactiontype` | `INCOME`, `EXPENSE` |
| `expenseorigin` | `BUDGETED`, `UNBUDGETED` |
| `paymentmethodtype` | `cash`, `transfer`, `credit_card`, `debit_card`, `financing` |
| `interesttype` | `none`, `fixed_rate` |
| `debtstatus` | `active`, `partial`, `paid` |
| `installmentstatus` | `pending`, `paid` |
| `userrole` | `OWNER`, `ADMIN`, `VIEWER` |
| `recipienttype` | `supplier`, `employee`, `partner` |
| `commissionstatus` | `pending`, `paid`, `cancelled` |

---

## 🌐 Endpoints principales de la API — `/api/v1`

| Método | Endpoint | Table afectada |
|---|---|---|
| POST | `/companies/` | `companies` |
| GET/PUT | `/companies/{id}` | `companies` |
| POST | `/clients/` | `clients` |
=======
*Actualizado: 2026-03-16 | Proyecto: `aplicacion-financiera-guias-42` (GCP)*
`clients` |
>>>>>>> financial-project/main
| GET | `/clients/` | `clients` |
| POST | `/services/` | `services` |
| POST | `/client-services/{client_id}` | `client_services` |
| POST | `/invoices/` | `invoices`, `invoice_items` |
| POST | `/invoices/{id}/emit` | `invoices` (actualiza `cae`, `status`) |
| POST | `/expenses/types` | `expense_types` |
| POST | `/expenses/categories` | `expense_categories` |
| POST | `/budgets/` | `expense_budgets` |
| POST | `/budgets/{id}/pay` | `expense_budgets`, `transactions` |
| POST | `/income-budgets/` | `income_budgets` |
| POST | `/income-budgets/{id}/collect` | `income_budgets`, `transactions` |
| GET | `/transactions/` | `transactions` |
| GET | `/dashboard/summary` | `transactions`, `expense_budgets` |
| GET | `/dashboard/profitability` | `invoice_items`, `transactions` |
<<<<<<< HEAD
| GET | `/payment-methods/` | `payment_methods` |
| POST | `/debts/` | `debts`, `debt_installments`, `expense_budgets` |
| GET | `/debts/` | `debts` |
| POST | `/auth/google` | `users` (login/registro) |
| GET | `/auth/me` | `users` (perfil actual) |
| GET | `/companies/{id}/users` | `user_companies`, `users` |
| POST | `/companies/{id}/users` | `user_companies` (invitar) |
| PATCH | `/companies/{id}/imagen` | `companies` (subir logo) |
| POST | `/commission-recipients` | `commission_recipients` |
| GET | `/commission-recipients` | `commission_recipients` |
| PATCH | `/commission-recipients/{id}` | `commission_recipients` |
| DELETE | `/commission-recipients/{id}` | `commission_recipients` (baja lógica) |
| POST | `/commission-rules` | `commission_rules` |
| GET | `/commission-rules` | `commission_rules` |
| PATCH | `/commission-rules/{id}` | `commission_rules` |
| DELETE | `/commission-rules/{id}` | `commission_rules` (baja lógica) |
| GET | `/commissions/pending` | `commissions` |
| POST | `/commissions/{id}/pay` | `commissions`, `transactions` |
| POST | `/commissions/generate` | `commissions` (recalcular) |
| GET | `/commissions/recipient/{id}/summary` | `commissions`, `commission_recipients` |
| GET | `/dashboard/commissions-summary` | `commissions`, `commission_recipients` |

---

*Generado: 2026-03-14 | Actualizado: 2026-03-14 (sistema de comisiones) | Proyecto: `aplicacion-financiera-guias-42` (GCP)*
=======

---

*Generado: 2026-03-08 | Proyecto: `aplicacion-financiera-guias-42` (GCP)*
>>>>>>> financial-project/main
