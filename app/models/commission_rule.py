import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, ForeignKey, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CommissionRule(Base):
    __tablename__ = "commission_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("commission_recipients.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(50), nullable=True)
    service_id: Mapped[str] = mapped_column(String(50), nullable=True)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Relationships
    company = relationship("Company")
    recipient = relationship("CommissionRecipient", back_populates="commission_rules")
    commissions = relationship("Commission", back_populates="rule")

    __table_args__ = (
        UniqueConstraint("company_id", "recipient_id", "client_id", "service_id", name="uq_commission_rule"),
        Index("idx_commission_rules_company", "company_id", "is_active"),
    )
