import datetime
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, DateTime, Float

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="patient")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
    
# --- Appointment Model ---
class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    specialty: Mapped[str] = mapped_column(String(100))
    schedule_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="PENDING") 
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)

    patient: Mapped["User"] = relationship("User", back_populates="appointments")

    def __repr__(self) -> str:
        return f"Appointment(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r})"

# Deferred import of models to avoid circular import during model loading
try:
    from app.db.models.health_scheme import (
        HealthScheme, HealthSchemeFAQ, HealthSchemeReference,
        HealthSchemeDocument, HealthSchemeEmbedding
    )
except ImportError:
    pass

try:
    from app.db.models.healthcare_facility import HealthcareFacility
except ImportError:
    pass
