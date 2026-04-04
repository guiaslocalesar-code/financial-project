import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    original_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    interest_type: Mapped[str] = mapped_column(String(50), nullable=True) # fixed, monthly_base, etc.
    interest_rate: Mapped[float] = mapped_column(Numeric(10, 4), nullable=True)
    interest_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    installments: Mapped[int] = mapped_column(Integer, default=1)
    installment_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    first_due_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.current_date())
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="debts")
    debt_installments = relationship("DebtInstallment", back_populates="debt", cascade="all, delete-orphan")
