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
|--| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `name` | VARCHAR(255) | ❌ | — | Razón social de la empresa |
| `cuit` | VARCHAR(13) | ❌ | — | CUIT único de la empresa |
| `fiscal_condition` | ENUM | ❌ | — | Condición fiscal: `RI`, `monotributo`, `exento` |
| `imagen` | TEXT | ✅ | NULL | URL Logo de la empresa |
| `afip_cert` | TEXT | ✅ | NULL | Certificado AFIP (encriptado con Fernet) |
| `afip_key` | TEXT | ✅ | NULL | Clave privada AFIP (encriptada) |
| `afip_point_of_sale` | INTEGER | ✅ | NULL | Número de punto de venta habilitado en AFIP |
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

---

## 👤 TABLA 2: `clients`
**Propósito:** Clientes de la agencia con todos los datos fiscales necesarios para emitir comprobantes AFIP (Facturas tipo A, B o C). El tipo de factura se determina automáticamente cruzando la condición fiscal de la empresa emisora y del cliente receptor.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(255) | ❌ | — | Razón social o nombre del cliente |
| `customer_name` | VARCHAR(255) | ✅ | — | Nombre de fantasía (opcional) |
| `customer_alias` | VARCHAR(100) | ✅ | — | Alias interno |
| `cuit_cuil_dni` | VARCHAR(20) | ❌ | — | Documento fiscal (CUIT, CUIL o DNI validado) |
| `fiscal_condition` | ENUM | ❌ | — | Condición: `RI`, `monotributo`, `consumidor_final`, `exento` |
| `email` | VARCHAR(255) | ✅ | NULL | Email de contacto |
| `phone` | VARCHAR(50) | ✅ | NULL | Teléfono |
| `address` | TEXT | ✅ | NULL | Dirección fiscal |
| `city` | VARCHAR(100) | ✅ | NULL | Ciudad |
| `province` | VARCHAR(100) | ✅ | NULL | Provincia |
| `zip_code` | VARCHAR(10) | ✅ | NULL | Código postal |
| `imagen` | TEXT | ✅ | NULL | URL Logo del cliente |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

---

## 🛠️ TABLA 3: `services`
**Propósito:** Catálogo de servicios que la agencia ofrece. Debe existir el servicio aquí antes de asignarlo a un cliente. Permite vincular los ítems de facturas y transacciones a un servicio específico para calcular la rentabilidad por servicio.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `name` | VARCHAR(100) | ❌ | — | Nombre del servicio (ej: "Manejo de Redes", "Google Ads") |
| `description` | TEXT | ✅ | NULL | Descripción detallada del servicio |
| `is_active` | BOOLEAN | ❌ | `true` | Baja lógica |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

---

## 🔗 TABLA 4: `client_services`
**Propósito:** Relación Muchos-a-Muchos entre clientes y servicios. Registra el precio acordado con cada cliente por cada servicio contratado. Es la fuente de verdad del precio por cliente.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
| `service_id` | UUID | ❌ | — | FK → `services.id` |
| `monthly_fee` | NUMERIC(12,2) | ❌ | — | Precio mensual acordado con este cliente |
| `currency` | VARCHAR(3) | ❌ | `ARS` | Moneda del precio |
| `start_date` | DATE | ❌ | — | Fecha de inicio del contrato |
| `end_date` | DATE | ✅ | NULL | Fecha de fin (NULL = sigue activo) |
| `status` | ENUM | ❌ | `active` | Estado: `active`, `paused`, `cancelled` |
| `created_at" | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

---

## 🧾 TABLA 5: `invoices`
**Propósito:** Comprobantes emitidos a través de AFIP. Cada registro representa una factura electrónica. Puede estar en estado `draft` (borrador) antes de ser enviada a AFIP. Al emitirse, recibe el **CAE** (Código de Autorización Electrónica).

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
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

---

## 📝 TABLA 6: `invoice_items`
**Propósito:** Líneas de detalle de cada factura (el desglose del "qué se cobró"). Vinculadas opcionalmente a un `service_id` para habilitar el cálculo de rentabilidad por servicio en el dashboard.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `invoice_id" | UUID | ❌ | — | FK → `invoices.id` |
| `service_id` | UUID | ✅ | NULL | FK → `services.id` (opcional, para métricas) |
| `description` | TEXT | ❌ | — | Descripción del ítem (ej: "Manejo Redes Enero 2025") |
| `quantity` | NUMERIC(10,2) | ❌ | `1` | Cantidad |
| `unit_price` | NUMERIC(12,2) | ❌ | — | Precio unitario |
| `iva_rate` | NUMERIC(5,2) | ❌ | `21` | Alícuota IVA del ítem |
| `subtotal` | NUMERIC(12,2) | ❌ | — | `quantity × unit_price` (calculado) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |

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
| `created_at" | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

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
| `debt_id` | UUID | ✅ | NULL | FK → `debts.id` (si el gasto es cuota de deuda) |
| `description` | TEXT | ❌ | — | Descripción del gasto planificado |
| `budgeted_amount` | NUMERIC(12,2) | ❌ | — | Monto presupuestado originalmente |
| `actual_amount` | NUMERIC(12,2) | ✅ | NULL | Monto real pagado (puede diferir del presupuestado) |
| `planned_date` | DATE | ❌ | — | Fecha en que se debe abonar |
| `period_month` | INTEGER | ❌ | — | Mes del período (1–12) |
| `period_year` | INTEGER | ❌ | — | Año del período |
| `is_recurring` | BOOLEAN | ❌ | `false` | Si `true`, se clona automáticamente cada mes |
| `status` | ENUM | ❌ | `pending` | Estado: `pending`, `paid`, `cancelled` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (se llena al pagar) |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

---

## 📅 TABLA 10: `income_budgets`
**Propósito:** Presupuesto mensual de ingresos esperados (cobranza planificada). El usuario carga los cobros esperados mes a mes o usa facturación recurrente. Funciona en paralelo a `expense_budgets`.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `client_id` | UUID | ❌ | — | FK → `clients.id` |
| `service_id` | UUID | ❌ | — | FK → `services.id` |
| `budgeted_amount` | NUMERIC(12,2) | ❌ | — | Monto original a cobrar |
| `actual_amount` | NUMERIC(12,2) | ✅ | NULL | Monto real cobrado |
| `planned_date` | DATE | ❌ | — | Fecha estimada de cobro |
| `period_month` | INTEGER | ❌ | — | Mes del período |
| `period_year" | INTEGER | ❌ | — | Año del período |
| `is_recurring` | BOOLEAN | ❌ | `true` | Si `true`, se clona para el próximo mes |
| `status` | ENUM | ❌ | `pending` | Estado: `pending`, `collected`, `cancelled` |
| `transaction_id` | UUID | ✅ | NULL | FK → `transactions.id` (se llena al cobrar) |
| `notes` | TEXT | ✅ | NULL | Notas internas |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

---

## 💰 TABLA 11: `transactions`
**Propósito:** Registro central de todos los movimientos de dinero **reales** (ingresos y egresos efectivamente cobrados/pagados). Es la fuente de verdad para el dashboard, cálculo de rentabilidad, flujo de caja y balance. Cada peso que entró o salió debe estar aquí.

### Columnas

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | ❌ | `uuid4()` | Primary Key |
| `company_id` | UUID | ❌ | — | FK → `companies.id` |
| `client_id` | UUID | ✅ | NULL | FK → `clients.id` (solo en ingresos) |
| `invoice_id` | UUID | ✅ | NULL | FK → `invoices.id` (si el ingreso viene de una factura) |
| `budget_id` | UUID | ✅ | NULL | FK → `expense_budgets.id` (si el egreso vino del presupuesto) |
| `income_budget_id` | UUID | ✅ | NULL | FK → `income_budgets.id` (si el ingreso vino de cobranza presupuestada) |
| `service_id` | UUID | ✅ | NULL | FK → `services.id` (para métricas de rentabilidad) |
| `expense_type_id` | UUID | ✅ | NULL | FK → `expense_types.id` (solo en egresos) |
| `expense_category_id` | UUID | ✅ | NULL | FK → `expense_categories.id` (solo en egresos) |
| `type` | ENUM | ❌ | — | Tipo: `income`, `expense` |
| `is_budgeted` | BOOLEAN | ❌ | `false` | Si el egreso fue presupuestado previamente |
| `expense_origin` | ENUM | ✅ | NULL | Origen del egreso: `budgeted`, `unbudgeted` |
| `amount` | NUMERIC(12,2) | ❌ | — | Monto real de la transacción |
| `currency` | VARCHAR(3) | ❌ | `ARS` | Moneda |
| `exchange_rate` | NUMERIC(10,4) | ❌ | `1` | Tipo de cambio |
| `payment_method` | ENUM | ✅ | NULL | Método: `cash`, `transfer`, `check`, `card`, `other` (legacy) |
| `payment_method_id` | UUID | ✅ | NULL | FK → `payment_methods.id` (nuevo sistema) |
| `description` | TEXT | ✅ | NULL | Descripción del movimiento |
| `transaction_date` | DATE | ❌ | `current_date` | Fecha real del movimiento de dinero |
| `created_at` | TIMESTAMP | ❌ | `now()` | Fecha de creación del registro |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Última actualización |

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
├── clients (N)
│   └── client_services (N) ←→ services (N)
├── services (N)
│   └── invoice_items (N)
├── invoices (N)
│   └── invoice_items (N)
├── expense_types (N)
│   └── expense_categories (N)
│       └── expense_budgets (N)
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
```

---

*Actualizado: 2026-03-16 | Proyecto: `aplicacion-financiera-guias-42` (GCP)*
`clients` |
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

---

*Generado: 2026-03-08 | Proyecto: `aplicacion-financiera-guias-42` (GCP)*
