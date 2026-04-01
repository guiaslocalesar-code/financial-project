import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import IncomeBudgetStatus

class IncomeBudget(Base):
    __tablename__ = "income_budgets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)
    budgeted_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    requires_invoice: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    iva_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=True)
    iva_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=True)
    actual_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[IncomeBudgetStatus] = mapped_column(SQLEnum(IncomeBudgetStatus), default=IncomeBudgetStatus.PENDING, nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="income_budgets")
    client = relationship("Client", back_populates="income_budgets")
    service = relationship("Service", back_populates="income_budgets")
    transaction = relationship("Transaction", foreign_keys=[transaction_id], post_update=True)
