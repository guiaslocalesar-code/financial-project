import uuid
from datetime import datetime
from sqlalchemy import Numeric, Boolean, DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.utils.enums import CompanyRole

class UserCompany(Base):
    __tablename__ = "user_companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    role: Mapped[CompanyRole] = mapped_column(SQLEnum(CompanyRole, native_enum=False, length=50), default=CompanyRole.USER)
    
    # Lista JSON de permisos granulares exactos
    permissions = mapped_column(JSONB, nullable=True)
    
    quotaparte: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_companies")
    company = relationship("Company", back_populates="user_companies")
