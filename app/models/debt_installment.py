import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class DebtInstallment(Base):
    __tablename__ = "debt_installments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    debt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("debts.id", ondelete="CASCADE"), nullable=False)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)           # total cuota
    capital_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)   # parte capital
    interest_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)  # parte interés
    status: Mapped[str] = mapped_column(String(20), default="pending")               # pending, paid
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    debt = relationship("Debt", back_populates="installments_detail")
    transaction = relationship("Transaction")
