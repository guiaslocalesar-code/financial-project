import enum

class FiscalCondition(str, enum.Enum):
    RI = "RI"
    MONOTRIBUTO = "MONOTRIBUTO"
    EXENTO = "EXENTO"
    CONSUMIDOR_FINAL = "CONSUMIDOR_FINAL"

class ServiceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

class InvoiceType(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    EMITTED = "EMITTED"
    CANCELLED = "CANCELLED"

class AppliesTo(str, enum.Enum):
    BUDGETED = "BUDGETED"
    UNBUDGETED = "UNBUDGETED"
    BOTH = "BOTH"

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
    BUDGETED = "BUDGETED"
    UNBUDGETED = "UNBUDGETED"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    TRANSFER = "TRANSFER"
    CHECK = "CHECK"
    CARD = "CARD"
    OTHER = "OTHER"
