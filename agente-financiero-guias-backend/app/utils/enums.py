import enum

class CompanyRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    OWNER = "owner"
    ACCOUNTANT = "accountant"

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
class PaymentMethodType(str, enum.Enum):
    BANK = "BANK"
    CASH = "CASH"
    CARD = "CARD"
    OTHER = "OTHER"

class DebtStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class InterestType(str, enum.Enum):
    FIXED = "FIXED"
    VARIABLE = "VARIABLE"

class CommissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
