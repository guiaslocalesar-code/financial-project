import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import CommissionStatus

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
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=True) # Optional in some schemas
    transaction_id: Mapped[uuid.UUID] = mapped_column("income_transaction_id", ForeignKey("transactions.id"), nullable=False)
    commission_rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_rules.id"), nullable=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_recipients.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"), nullable=True)
    
    base_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    amount: Mapped[float] = mapped_column("commission_amount", Numeric(12, 2), nullable=False)
    
    status: Mapped[CommissionStatus] = mapped_column(SQLEnum(CommissionStatus, name="commissionstatus", create_type=False), default=CommissionStatus.PENDING)
    payment_transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    transaction = relationship("Transaction", foreign_keys=[transaction_id])
    payment_transaction = relationship("Transaction", foreign_keys=[payment_transaction_id])
    recipient = relationship("CommissionRecipient", back_populates="commissions")
    client = relationship("Client")
    service = relationship("Service")
    rule = relationship("CommissionRule")

