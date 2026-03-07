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
    DRAFT = "draft"
    EMITTED = "emitted"
    CANCELLED = "cancelled"

class AppliesTo(str, enum.Enum):
    BUDGETED = "budgeted"
    UNBUDGETED = "unbudgeted"
    BOTH = "both"

class BudgetStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class ExpenseOrigin(str, enum.Enum):
    BUDGETED = "budgeted"
    UNBUDGETED = "unbudgeted"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CHECK = "check"
    CARD = "card"
    OTHER = "other"
