import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import FiscalCondition

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cuit_cuil_dni: Mapped[str] = mapped_column(String(20), nullable=False)
    fiscal_condition: Mapped[FiscalCondition] = mapped_column(SQLEnum(FiscalCondition), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    province: Mapped[str] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="clients")
    services = relationship("ClientService", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    transactions = relationship("Transaction", back_populates="client")
