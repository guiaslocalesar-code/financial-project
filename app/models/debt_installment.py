import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class DebtInstallment(Base):
    __tablename__ = "debt_installments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("debts.id"), nullable=False)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    capital_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    interest_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    debt = relationship("Debt", back_populates="debt_installments")
    transaction = relationship("Transaction")
