import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import FiscalCondition

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cuit: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    fiscal_condition: Mapped[FiscalCondition] = mapped_column(SQLEnum(FiscalCondition, name="fiscalcondition"), nullable=False)
    afip_cert: Mapped[str] = mapped_column(Text, nullable=True)
    afip_key: Mapped[str] = mapped_column(Text, nullable=True)
    afip_point_of_sale: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    imagen: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    clients = relationship("Client", back_populates="company")
    services = relationship("Service", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    expense_types = relationship("ExpenseType", back_populates="company")
    expense_categories = relationship("ExpenseCategory", back_populates="company")
    expense_budgets = relationship("ExpenseBudget", back_populates="company")
    income_budgets = relationship("IncomeBudget", back_populates="company")
    transactions = relationship("Transaction", back_populates="company")
    payment_methods = relationship("PaymentMethod", back_populates="company")
    debts = relationship("Debt", back_populates="company")
    commission_recipients = relationship("CommissionRecipient", back_populates="company")
    user_companies = relationship("UserCompany", back_populates="company")
