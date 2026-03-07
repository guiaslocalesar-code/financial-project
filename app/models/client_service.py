import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.utils.enums import ServiceStatus

class ClientService(Base):
    __tablename__ = "client_services"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"), nullable=False)
    monthly_fee: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ARS")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[ServiceStatus] = mapped_column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="services")
    service = relationship("Service", back_populates="client_services")

    __table_args__ = (
        UniqueConstraint('client_id', 'service_id', name='_client_service_uc'),
    )
