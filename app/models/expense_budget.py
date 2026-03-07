import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Boolean, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import BudgetStatus

class ExpenseBudget(Base):
    __tablename__ = "expense_budgets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    expense_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_types.id"), nullable=False)
    expense_category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expense_categories.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    budgeted_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    actual_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[BudgetStatus] = mapped_column(SQLEnum(BudgetStatus), default=BudgetStatus.PENDING)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="expense_budgets")
    expense_type = relationship("ExpenseType", back_populates="budgets")
    category = relationship("ExpenseCategory", back_populates="budgets")
    transaction = relationship("Transaction", foreign_keys=[transaction_id], back_populates="budget")
