import uuid
import enum

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Date, DateTime, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    admin = "admin"
    staff = "staff"
    customer = "customer"


class MemberTier(str, enum.Enum):
    """Member tier enumeration for loyalty levels."""
    regular = "regular"
    vip = "vip"


class BaseModel(Base):
    """Abstract base model with common fields."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False, index=True)
    # SOFT DELETE: audit trail — NULL means active, timestamp means deleted
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    # SECURITY: Use UUID instead of auto-incrementing integers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    line_user_id = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.customer, nullable=False, index=True)
    tier = Column(SQLEnum(MemberTier), default=MemberTier.regular, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    # TIMEZONE: Always use timezone-aware datetimes in Postgres
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # SOFT DELETE: audit trail
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    work_logs = relationship("WorkLog", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class News(BaseModel):
    """News/Latest News model for CMS."""
    __tablename__ = "news"
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # HTML from React-Quill
    cover_image = Column(String(500), nullable=True)  # Cloudinary URL
    category = Column(String(100), nullable=False, index=True)  # e.g., "Promotion", "Announcement"
    date = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True, server_default="true")


class Service(BaseModel):
    """Service model for menu items and staff tasks."""
    __tablename__ = "services"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in smallest currency unit (e.g., cents)
    duration_min = Column(Integer, nullable=False)  # Duration in minutes
    category = Column(String(100), nullable=False, index=True)  # e.g., "Body", "Face"
    image_url = Column(String(500), nullable=True)  # Cloudinary URL
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    work_logs = relationship("WorkLog", back_populates="service")


class Product(BaseModel):
    """Product model for retail items."""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in smallest currency unit
    spec = Column(String(255), nullable=True)  # e.g., "500ml"
    category = Column(String(100), nullable=True, index=True)  # Product category
    image_url = Column(String(500), nullable=True)  # Cloudinary URL
    is_stock = Column(Boolean, default=True, nullable=False, index=True)


class Testimonial(BaseModel):
    """Testimonial/Recommendation model."""
    __tablename__ = "testimonials"
    
    customer_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    avatar_url = Column(String(500), nullable=True)  # Cloudinary URL, optional
    is_active = Column(Boolean, default=True, nullable=False, index=True, server_default="true")
    
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )


class Portfolio(BaseModel):
    """Portfolio model for showcasing work."""
    __tablename__ = "portfolio"
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=False)  # Cloudinary URL (single image)
    category = Column(String(100), nullable=False, index=True)  # e.g., "Acne", "Anti-aging"
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True, server_default="true")
    display_order = Column(Integer, default=0, nullable=False, server_default="0")
    
    # Relationships
    service = relationship("Service")


class WorkLog(Base):
    """Work log model for staff time tracking."""
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    custom_task_name = Column(String(255), nullable=True)
    hours = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # SOFT DELETE: audit trail
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="work_logs")
    service = relationship("Service", back_populates="work_logs")

    __table_args__ = (
        CheckConstraint(
            '(service_id IS NOT NULL AND custom_task_name IS NULL) OR (service_id IS NULL AND custom_task_name IS NOT NULL)',
            name='check_task_type'
        ),
        CheckConstraint('hours > 0', name='check_positive_hours'),
    )


class SiteSetting(Base):
    """Key-value store for site settings (contact info, SEO, etc.)."""
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # SOFT DELETE: audit trail
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Transaction(Base):
    """Transaction model for member purchase / service history."""
    __tablename__ = "transactions"

    # SECURITY: Use UUID instead of auto-incrementing integers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    # TIMEZONE: Always use timezone-aware datetimes
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # SOFT DELETE: timestamp-based
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
