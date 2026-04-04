import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Enum as SQLEnum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import InvoiceType, InvoiceStatus

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    invoice_type: Mapped[InvoiceType] = mapped_column(SQLEnum(InvoiceType), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(20), nullable=True)
    point_of_sale: Mapped[int] = mapped_column(Integer, nullable=False)
    cae: Mapped[str] = mapped_column(String(20), nullable=True)
    cae_expiry: Mapped[date] = mapped_column(Date, nullable=True)
    issue_date: Mapped[date] = mapped_column(Date, default=func.current_date(), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    iva_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=21.0)
    iva_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ARS")
    exchange_rate: Mapped[float] = mapped_column(Numeric(10, 4), default=1.0)
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    afip_raw_response: Mapped[dict] = mapped_column(JSON, nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")
    transactions = relationship("Transaction", back_populates="invoice")
