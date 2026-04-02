import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class CommissionRecipient(Base):
    __tablename__ = "commission_recipients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="commission_recipients")
    rules = relationship("CommissionRule", back_populates="recipient", cascade="all, delete-orphan")
    commissions = relationship("Commission", back_populates="recipient")

class CommissionRule(Base):
    __tablename__ = "commission_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_recipients.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"), nullable=True)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    recipient = relationship("CommissionRecipient", back_populates="rules")
    client = relationship("Client")
    service = relationship("Service")

class Commission(Base):
    __tablename__ = "commissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column("income_transaction_id", ForeignKey("transactions.id"), nullable=False)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_recipients.id"), nullable=False)
    amount: Mapped[float] = mapped_column("commission_amount", Numeric(12, 2), nullable=False)
    base_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)  # Neto del ingreso
    commission_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True) # % aplicado
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    transaction = relationship("Transaction")
    recipient = relationship("CommissionRecipient", back_populates="commissions")

