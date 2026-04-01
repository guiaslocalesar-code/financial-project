import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, DateTime, Boolean, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import TransactionType, ExpenseOrigin, PaymentMethod

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    budget_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_budgets.id"), nullable=True)
    income_budget_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("income_budgets.id"), nullable=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"), nullable=True)
    expense_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_types.id"), nullable=True)
    expense_category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_categories.id"), nullable=True)
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    is_budgeted: Mapped[bool] = mapped_column(Boolean, default=False)
    expense_origin: Mapped[ExpenseOrigin] = mapped_column(SQLEnum(ExpenseOrigin), nullable=True)
    requires_invoice: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    iva_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=True)
    iva_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ARS")
    exchange_rate: Mapped[float] = mapped_column(Numeric(10, 4), default=1.0)
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=True)
    payment_method_id: Mapped[str] = mapped_column(ForeignKey("payment_methods.id"), nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, default=func.current_date(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="transactions")
    client = relationship("Client", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")
    budget = relationship("ExpenseBudget", foreign_keys=[budget_id])
    income_budget = relationship("IncomeBudget", foreign_keys=[income_budget_id])
    service = relationship("Service", back_populates="transactions")
    expense_type = relationship("ExpenseType", back_populates="transactions")
    category = relationship("ExpenseCategory", back_populates="transactions")
    payment_method_detail = relationship("PaymentMethod")
