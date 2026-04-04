import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import RecipientType


class CommissionRecipient(Base):
    __tablename__ = "commission_recipients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[RecipientType] = mapped_column(SQLEnum(RecipientType, name="recipienttype"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cuit: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Relationships
    company = relationship("Company")
    commission_rules = relationship("CommissionRule", back_populates="recipient")
    commissions = relationship("Commission", back_populates="recipient")

    __table_args__ = (
        Index("idx_commission_recipients_company", "company_id", "is_active"),
    )
