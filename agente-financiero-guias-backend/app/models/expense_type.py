import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import AppliesTo

class ExpenseType(Base):
    __tablename__ = "expense_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    applies_to: Mapped[AppliesTo] = mapped_column(SQLEnum(AppliesTo, name="appliesto"), default=AppliesTo.BOTH)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="expense_types")
    categories = relationship("ExpenseCategory", back_populates="expense_type")
    budgets = relationship("ExpenseBudget", back_populates="expense_type")
    transactions = relationship("Transaction", back_populates="expense_type")
