from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import func

class AfipToken(Base):
    __tablename__ = "afip_tokens"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), primary_key=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    sign: Mapped[str] = mapped_column(Text, nullable=False)
    cuit: Mapped[str] = mapped_column(String(20), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
