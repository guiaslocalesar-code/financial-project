import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    payment_method_id: Mapped[str] = mapped_column(ForeignKey("payment_methods.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Montos
    original_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    interest_type: Mapped[str] = mapped_column(String(20), default="none") # none, fixed_rate
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0) # % mensual
    interest_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # original + interés total

    # Cuotas
    installments: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    installment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    first_due_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="active") # active, paid, partial
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company")
    payment_method = relationship("PaymentMethod")
    transaction = relationship("Transaction")
    installments_detail = relationship("DebtInstallment", back_populates="debt", cascade="all, delete-orphan")
