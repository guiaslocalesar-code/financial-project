import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # ej: 'pm_efectivo', 'pm_visa_galicia'
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False) # cash, transfer, credit_card, debit_card, financing
    bank: Mapped[str] = mapped_column(String(100), nullable=True)
    is_credit: Mapped[bool] = mapped_column(Boolean, default=False)
    closing_day: Mapped[int] = mapped_column(Integer, nullable=True)
    due_day: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    company = relationship("Company")
