import enum

class FiscalCondition(str, enum.Enum):
    RI = "RI"
    MONOTRIBUTO = "monotributo"
    EXENTO = "exento"
    CONSUMIDOR_FINAL = "consumidor_final"

class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class InvoiceType(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    EMITTED = "EMITTED"
    CANCELLED = "CANCELLED"

class AppliesTo(str, enum.Enum):
    BUDGETED = "budgeted"
    UNBUDGETED = "unbudgeted"
    BOTH = "both"

class BudgetStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class IncomeBudgetStatus(str, enum.Enum):
    PENDING = "PENDING"
    COLLECTED = "COLLECTED"
    CANCELLED = "CANCELLED"

class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class ExpenseOrigin(str, enum.Enum):
    BUDGETED = "budgeted"
    UNBUDGETED = "unbudgeted"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CHECK = "check"
    CARD = "card"
    OTHER = "other"

class RecipientType(str, enum.Enum):
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    PARTNER = "partner"

class CommissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
