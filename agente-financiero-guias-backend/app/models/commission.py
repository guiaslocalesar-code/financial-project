import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Enum as SQLEnum, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import CommissionStatus


class Commission(Base):
    __tablename__ = "commissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    income_transaction_id: Mapped[uuid.UUID] = mapped_column("income_transaction_id", ForeignKey("transactions.id"), nullable=False)
    commission_rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_rules.id"), nullable=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_recipients.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(50), nullable=False)
    service_id: Mapped[str] = mapped_column(String(50), nullable=False)
    base_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    commission_amount: Mapped[float] = mapped_column("commission_amount", Numeric(12, 2), nullable=False)
    status: Mapped[CommissionStatus] = mapped_column(
        SQLEnum(CommissionStatus, name="commissionstatus"), default=CommissionStatus.PENDING
    )
    payment_transaction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Relationships
    company = relationship("Company")
    income_transaction = relationship("Transaction", foreign_keys=[income_transaction_id])
    payment_transaction = relationship("Transaction", foreign_keys=[payment_transaction_id])
    rule = relationship("CommissionRule", back_populates="commissions")
    recipient = relationship("CommissionRecipient", back_populates="commissions")

    __table_args__ = (
        Index("idx_commissions_status", "company_id", "status"),
        Index("idx_commissions_income", "income_transaction_id"),
    )
