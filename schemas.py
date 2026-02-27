import uuid as _uuid

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from models import UserRole, MemberTier


# ==================== Base Schemas ====================

class BaseSchema(BaseModel):
    """Base schema with common fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    sort_order: int

    class Config:
        from_attributes = True


# ==================== User Schemas ====================

class UserBase(BaseModel):
    display_name: str
    role: UserRole = UserRole.customer
    is_active: bool = True


class UserCreate(UserBase):
    line_user_id: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    """Schema for updating user role only."""
    role: UserRole


class UserStatusUpdate(BaseModel):
    """Schema for updating user active status only."""
    is_active: bool


class UserAdminResponse(BaseModel):
    """Schema for admin user listing (excludes sensitive data)."""
    id: _uuid.UUID
    line_user_id: str
    display_name: str
    role: UserRole
    tier: MemberTier
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: _uuid.UUID
    line_user_id: str
    display_name: str
    role: UserRole
    tier: MemberTier
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== News Schemas ====================

class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    cover_image: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., max_length=100)
    date: date
    is_active: bool = True


class NewsCreate(NewsBase):
    sort_order: int = 0


class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    date: Optional[date] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class NewsResponse(BaseSchema, NewsBase):
    pass


# ==================== Service Schemas ====================

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    duration_min: int = Field(..., gt=0)
    category: str = Field(..., max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    sort_order: int = 0


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    duration_min: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ServiceResponse(BaseSchema, ServiceBase):
    pass


# ==================== Product Schemas ====================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    spec: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    is_stock: bool = True


class ProductCreate(ProductBase):
    sort_order: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    spec: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    is_stock: Optional[bool] = None
    sort_order: Optional[int] = None


class ProductResponse(BaseSchema, ProductBase):
    pass


# ==================== Testimonial Schemas ====================

class TestimonialBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class TestimonialCreate(TestimonialBase):
    sort_order: int = 0


class TestimonialUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class TestimonialResponse(BaseSchema, TestimonialBase):
    pass


# ==================== Portfolio Schemas ====================

class PortfolioBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: str = Field(..., max_length=500)
    category: str = Field(..., max_length=100)
    service_id: Optional[int] = None
    is_active: bool = True
    display_order: int = 0


class PortfolioCreate(PortfolioBase):
    sort_order: int = 0


class PortfolioUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    service_id: Optional[int] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    sort_order: Optional[int] = None


class PortfolioResponse(BaseSchema, PortfolioBase):
    service_name: Optional[str] = None


# ==================== WorkLog Schemas ====================

class WorkLogBase(BaseModel):
    date: date
    service_id: Optional[int] = None
    custom_task_name: Optional[str] = Field(None, max_length=255)
    hours: float = Field(..., gt=0)

    @validator('custom_task_name')
    def validate_task(cls, v, values):
        """Ensure either service_id or custom_task_name is provided, but not both."""
        service_id = values.get('service_id')
        if service_id and v:
            raise ValueError('Cannot specify both service_id and custom_task_name')
        if not service_id and not v:
            raise ValueError('Must specify either service_id or custom_task_name')
        return v


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    date: Optional[date] = None
    service_id: Optional[int] = None
    custom_task_name: Optional[str] = Field(None, max_length=255)
    hours: Optional[float] = Field(None, gt=0)


class WorkLogResponse(BaseModel):
    id: int
    user_id: _uuid.UUID
    date: date
    service_id: Optional[int]
    custom_task_name: Optional[str]
    hours: float
    created_at: datetime
    updated_at: datetime
    
    # Optional nested data
    user_display_name: Optional[str] = None
    service_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== Auth Schemas ====================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[_uuid.UUID] = None
    role: Optional[UserRole] = None


class LINELoginRequest(BaseModel):
    code: str
    state: str


# ==================== Utility Schemas ====================

class SortOrderUpdate(BaseModel):
    id: int
    sort_order: int


class BatchSortOrderUpdate(BaseModel):
    items: list[SortOrderUpdate]


class MessageResponse(BaseModel):
    message: str


# ==================== Transaction Schemas ====================

class TransactionCreate(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=255)
    amount: int = Field(..., ge=0)


class TransactionResponse(BaseModel):
    id: _uuid.UUID
    user_id: _uuid.UUID
    service_name: str
    amount: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Member / Customer Schemas ====================

class MemberTierUpdate(BaseModel):
    """Schema for updating a customer's member tier."""
    tier: MemberTier


class CustomerSummaryResponse(BaseModel):
    """Schema for admin customer listing with aggregated stats."""
    id: _uuid.UUID
    line_user_id: str
    display_name: str
    role: UserRole
    tier: MemberTier
    is_active: bool
    created_at: datetime
    transaction_count: int = 0
    total_spent: int = 0

    class Config:
        from_attributes = True


class CustomerDetailResponse(BaseModel):
    """Schema for single customer detail with transactions."""
    id: _uuid.UUID
    line_user_id: str
    display_name: str
    role: UserRole
    tier: MemberTier
    is_active: bool
    created_at: datetime
    updated_at: datetime
    transaction_count: int = 0
    total_spent: int = 0
    transactions: list[TransactionResponse] = []

    class Config:
        from_attributes = True
