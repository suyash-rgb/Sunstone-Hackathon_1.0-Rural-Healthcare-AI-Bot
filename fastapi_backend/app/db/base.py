import datetime
# Import the specific SQLAlchemy types needed for configuration
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, DateTime, Float

# Define the base class for all declarative models
class Base(DeclarativeBase):
    """
    Base class which provides automated table name
    and is the parent for all ORM models.
    """
    pass

# --- 1. User Model  ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # FIX: MySQL requires explicit length for VARCHAR. Use type_=String(length)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # FIX: Apply length to email field as well
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # CRITICAL: Added hashed_password field, also needs a length
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Note: Use timezone-aware datetime for production
    # Mapped[datetime.datetime] resolves to a database compatible DateTime type
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
    
# --- 2. Appointment Model (Requirement 2: Tele-consultations) ---
# Tracks patient appointment requests

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign Key to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Consultation details
    specialty: Mapped[str] = mapped_column(String(100)) # e.g., 'General', 'Dental'
    schedule_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    
    # Status should be controlled (e.g., PENDING, CONFIRMED, COMPLETED, CANCELLED)
    # Enforce these values in your Pydantic schemas.
    status: Mapped[str] = mapped_column(String(50), default="PENDING") 
    
    notes: Mapped[str] = mapped_column(String(1000), nullable=True) # Patient's description of issue

    # Relationship to parent User
    patient: Mapped["User"] = relationship(back_populates="appointments")

    def __repr__(self) -> str:
        return f"Appointment(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r})"

