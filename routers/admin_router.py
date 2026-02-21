from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from typing import List

from database import get_db
from models import User, UserRole, News, Service, Product, Testimonial, Portfolio, WorkLog
from schemas import (
    NewsCreate, NewsUpdate, NewsResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    TestimonialCreate, TestimonialUpdate, TestimonialResponse,
    PortfolioCreate, PortfolioUpdate, PortfolioResponse,
    WorkLogResponse,
    BatchSortOrderUpdate,
    MessageResponse,
    UserAdminResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from auth import require_admin, get_current_user

router = APIRouter(dependencies=[Depends(require_admin)])


# ==================== News CRUD ====================

@router.get("/news", response_model=List[NewsResponse])
async def list_news(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all news items ordered by sort_order."""
    result = await db.execute(
        select(News)
        .order_by(News.sort_order, News.date.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific news item."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.post("/news", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(news: NewsCreate, db: AsyncSession = Depends(get_db)):
    """Create a new news item."""
    db_news = News(**news.dict())
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news


@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(news_id: int, news: NewsUpdate, db: AsyncSession = Depends(get_db)):
    """Update a news item."""
    result = await db.execute(select(News).where(News.id == news_id))
    db_news = result.scalar_one_or_none()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    
    for key, value in news.dict(exclude_unset=True).items():
        setattr(db_news, key, value)
    
    await db.commit()
    await db.refresh(db_news)
    return db_news


@router.delete("/news/{news_id}", response_model=MessageResponse)
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a news item."""
    result = await db.execute(select(News).where(News.id == news_id))
    db_news = result.scalar_one_or_none()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    
    await db.delete(db_news)
    await db.commit()
    return {"message": "News deleted successfully"}


# ==================== Service CRUD ====================

@router.get("/services", response_model=List[ServiceResponse])
async def list_services(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all services ordered by category and sort_order."""
    result = await db.execute(
        select(Service)
        .order_by(Service.category, Service.sort_order)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service: ServiceCreate, db: AsyncSession = Depends(get_db)):
    """Create a new service."""
    db_service = Service(**service.dict())
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: int, service: ServiceUpdate, db: AsyncSession = Depends(get_db)):
    """Update a service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service.dict(exclude_unset=True).items():
        setattr(db_service, key, value)
    
    await db.commit()
    await db.refresh(db_service)
    return db_service


@router.delete("/services/{service_id}", response_model=MessageResponse)
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    await db.delete(db_service)
    await db.commit()
    return {"message": "Service deleted successfully"}


# ==================== Product CRUD ====================

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all products ordered by sort_order."""
    result = await db.execute(
        select(Product)
        .order_by(Product.sort_order)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product."""
    db_product = Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """Update a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    db_product = result.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    db_product = result.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(db_product)
    await db.commit()
    return {"message": "Product deleted successfully"}


# ==================== Testimonial CRUD ====================

@router.get("/testimonials", response_model=List[TestimonialResponse])
async def list_testimonials(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all testimonials ordered by sort_order."""
    result = await db.execute(
        select(Testimonial)
        .order_by(Testimonial.sort_order)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/testimonials/{testimonial_id}", response_model=TestimonialResponse)
async def get_testimonial(testimonial_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific testimonial."""
    result = await db.execute(select(Testimonial).where(Testimonial.id == testimonial_id))
    testimonial = result.scalar_one_or_none()
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return testimonial


@router.post("/testimonials", response_model=TestimonialResponse, status_code=status.HTTP_201_CREATED)
async def create_testimonial(testimonial: TestimonialCreate, db: AsyncSession = Depends(get_db)):
    """Create a new testimonial."""
    db_testimonial = Testimonial(**testimonial.dict())
    db.add(db_testimonial)
    await db.commit()
    await db.refresh(db_testimonial)
    return db_testimonial


@router.put("/testimonials/{testimonial_id}", response_model=TestimonialResponse)
async def update_testimonial(testimonial_id: int, testimonial: TestimonialUpdate, db: AsyncSession = Depends(get_db)):
    """Update a testimonial."""
    result = await db.execute(select(Testimonial).where(Testimonial.id == testimonial_id))
    db_testimonial = result.scalar_one_or_none()
    if not db_testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    for key, value in testimonial.dict(exclude_unset=True).items():
        setattr(db_testimonial, key, value)
    
    await db.commit()
    await db.refresh(db_testimonial)
    return db_testimonial


@router.delete("/testimonials/{testimonial_id}", response_model=MessageResponse)
async def delete_testimonial(testimonial_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a testimonial."""
    result = await db.execute(select(Testimonial).where(Testimonial.id == testimonial_id))
    db_testimonial = result.scalar_one_or_none()
    if not db_testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    await db.delete(db_testimonial)
    await db.commit()
    return {"message": "Testimonial deleted successfully"}


# ==================== Portfolio CRUD ====================

@router.get("/portfolio", response_model=List[PortfolioResponse])
async def list_portfolio(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all portfolio items ordered by category and sort_order."""
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.service))
        .order_by(Portfolio.display_order, Portfolio.sort_order)
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()
    # Enrich with service_name
    enriched = []
    for item in items:
        data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "image_url": item.image_url,
            "category": item.category,
            "service_id": item.service_id,
            "is_active": item.is_active,
            "display_order": item.display_order,
            "sort_order": item.sort_order,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "service_name": item.service.name if item.service else None,
        }
        enriched.append(data)
    return enriched


@router.get("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific portfolio item."""
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.post("/portfolio", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioCreate, db: AsyncSession = Depends(get_db)):
    """Create a new portfolio item."""
    db_portfolio = Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


@router.put("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(portfolio_id: int, portfolio: PortfolioUpdate, db: AsyncSession = Depends(get_db)):
    """Update a portfolio item."""
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    db_portfolio = result.scalar_one_or_none()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    for key, value in portfolio.dict(exclude_unset=True).items():
        setattr(db_portfolio, key, value)
    
    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


@router.delete("/portfolio/{portfolio_id}", response_model=MessageResponse)
async def delete_portfolio(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a portfolio item."""
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    db_portfolio = result.scalar_one_or_none()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    await db.delete(db_portfolio)
    await db.commit()
    return {"message": "Portfolio deleted successfully"}


# ==================== Batch Sort Order Update ====================

@router.patch("/news/reorder", response_model=MessageResponse)
async def reorder_news(update: BatchSortOrderUpdate, db: AsyncSession = Depends(get_db)):
    """Batch update sort order for news items."""
    for item in update.items:
        result = await db.execute(select(News).where(News.id == item.id))
        news = result.scalar_one_or_none()
        if news:
            news.sort_order = item.sort_order
    
    await db.commit()
    return {"message": "News reordered successfully"}


@router.patch("/services/reorder", response_model=MessageResponse)
async def reorder_services(update: BatchSortOrderUpdate, db: AsyncSession = Depends(get_db)):
    """Batch update sort order for services."""
    for item in update.items:
        result = await db.execute(select(Service).where(Service.id == item.id))
        service = result.scalar_one_or_none()
        if service:
            service.sort_order = item.sort_order
    
    await db.commit()
    return {"message": "Services reordered successfully"}


@router.patch("/products/reorder", response_model=MessageResponse)
async def reorder_products(update: BatchSortOrderUpdate, db: AsyncSession = Depends(get_db)):
    """Batch update sort order for products."""
    for item in update.items:
        result = await db.execute(select(Product).where(Product.id == item.id))
        product = result.scalar_one_or_none()
        if product:
            product.sort_order = item.sort_order
    
    await db.commit()
    return {"message": "Products reordered successfully"}


@router.patch("/testimonials/reorder", response_model=MessageResponse)
async def reorder_testimonials(update: BatchSortOrderUpdate, db: AsyncSession = Depends(get_db)):
    """Batch update sort order for testimonials."""
    for item in update.items:
        result = await db.execute(select(Testimonial).where(Testimonial.id == item.id))
        testimonial = result.scalar_one_or_none()
        if testimonial:
            testimonial.sort_order = item.sort_order
    
    await db.commit()
    return {"message": "Testimonials reordered successfully"}


@router.patch("/portfolio/reorder", response_model=MessageResponse)
async def reorder_portfolio(update: BatchSortOrderUpdate, db: AsyncSession = Depends(get_db)):
    """Batch update sort order for portfolio items."""
    for item in update.items:
        result = await db.execute(select(Portfolio).where(Portfolio.id == item.id))
        portfolio = result.scalar_one_or_none()
        if portfolio:
            portfolio.sort_order = item.sort_order
    
    await db.commit()
    return {"message": "Portfolio reordered successfully"}


# ==================== Staff Work Logs (Admin View) ====================

@router.get("/staff/logs", response_model=List[WorkLogResponse])
async def list_all_work_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    start_date: str = None,
    end_date: str = None
):
    """List all staff work logs with optional filters."""
    query = select(WorkLog).order_by(WorkLog.date.desc(), WorkLog.created_at.desc())
    
    if user_id:
        query = query.where(WorkLog.user_id == user_id)
    if start_date:
        query = query.where(WorkLog.date >= start_date)
    if end_date:
        query = query.where(WorkLog.date <= end_date)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    work_logs = result.scalars().all()
    
    # Enrich with user and service names
    enriched_logs = []
    for log in work_logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "date": log.date,
            "service_id": log.service_id,
            "custom_task_name": log.custom_task_name,
            "hours": log.hours,
            "created_at": log.created_at,
            "updated_at": log.updated_at,
            "user_display_name": None,
            "service_name": None
        }
        
        # Get user display name
        user_result = await db.execute(select(User).where(User.id == log.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            log_dict["user_display_name"] = user.display_name
        
        # Get service name if applicable
        if log.service_id:
            service_result = await db.execute(select(Service).where(Service.id == log.service_id))
            service = service_result.scalar_one_or_none()
            if service:
                log_dict["service_name"] = service.name
        
        enriched_logs.append(log_dict)
    
    return enriched_logs


# ==================== User Management ====================

@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
):
    """List all users for admin management, ordered by created_at descending."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/users/{user_id}/role", response_model=UserAdminResponse)
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user's role. Prevents demoting the last administrator."""
    # Find target user
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="使用者不存在")

    # Suicide protection: prevent last admin from demoting themselves
    if (
        target_user.id == current_user.id
        and payload.role != UserRole.admin
    ):
        admin_count_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.role == UserRole.admin,
                User.is_active == True,
            )
        )
        admin_count = admin_count_result.scalar()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="無法降級最後一位管理員",
            )

    # Also protect demoting ANY admin if they are the last one
    if (
        target_user.role == UserRole.admin
        and payload.role != UserRole.admin
    ):
        admin_count_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.role == UserRole.admin,
                User.is_active == True,
            )
        )
        admin_count = admin_count_result.scalar()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="無法降級最後一位管理員",
            )

    target_user.role = payload.role
    await db.commit()
    await db.refresh(target_user)
    return target_user


@router.patch("/users/{user_id}/status", response_model=UserAdminResponse)
async def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user's active status. Prevents self-ban and banning the last admin."""
    # Find target user
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="使用者不存在")

    # Suicide protection: cannot ban yourself
    if target_user.id == current_user.id and not payload.is_active:
        raise HTTPException(
            status_code=400,
            detail="無法停用自己的帳號",
        )

    # Protect last admin from being deactivated
    if (
        target_user.role == UserRole.admin
        and not payload.is_active
    ):
        admin_count_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.role == UserRole.admin,
                User.is_active == True,
            )
        )
        admin_count = admin_count_result.scalar()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="無法停用最後一位管理員",
            )

    target_user.is_active = payload.is_active
    await db.commit()
    await db.refresh(target_user)
    return target_user
