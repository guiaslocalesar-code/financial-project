import uuid
from datetime import datetime
from sqlalchemy import Numeric, String, ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"), nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1.0)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    iva_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=21.0)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    service = relationship("Service", back_populates="invoice_items")
