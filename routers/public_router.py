from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from collections import defaultdict

from database import get_db
from models import News, Service, Product, Testimonial, Portfolio
from schemas import (
    NewsResponse,
    ServiceResponse,
    ProductResponse,
    TestimonialResponse,
    PortfolioResponse
)

router = APIRouter()


@router.get("/news", response_model=List[NewsResponse])
async def get_public_news(
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get published news ordered by date (most recent first)."""
    result = await db.execute(
        select(News)
        .where(News.is_active == True)
        .order_by(News.date.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_public_news_detail(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single published news article by ID."""
    result = await db.execute(
        select(News)
        .where(News.id == news_id, News.is_active == True)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.get("/services", response_model=List[ServiceResponse])
async def get_public_services(db: AsyncSession = Depends(get_db)):
    """Get active services ordered by category and sort_order."""
    result = await db.execute(
        select(Service)
        .where(Service.is_active == True)
        .order_by(Service.category, Service.sort_order, Service.name)
    )
    return result.scalars().all()


@router.get("/services/by-category")
async def get_services_by_category(db: AsyncSession = Depends(get_db)):
    """Get active services grouped by category."""
    result = await db.execute(
        select(Service)
        .where(Service.is_active == True)
        .order_by(Service.category, Service.sort_order, Service.name)
    )
    services = result.scalars().all()
    
    # Group by category
    grouped = defaultdict(list)
    for service in services:
        grouped[service.category].append({
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "price": service.price,
            "duration_min": service.duration_min,
            "image_url": service.image_url,
            "sort_order": service.sort_order
        })
    
    return dict(grouped)


@router.get("/products", response_model=List[ProductResponse])
async def get_public_products(db: AsyncSession = Depends(get_db)):
    """Get in-stock products ordered by sort_order."""
    result = await db.execute(
        select(Product)
        .where(Product.is_stock == True)
        .order_by(Product.sort_order, Product.name)
    )
    return result.scalars().all()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_public_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single in-stock product by ID."""
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id, Product.is_stock == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/testimonials", response_model=List[TestimonialResponse])
async def get_public_testimonials(db: AsyncSession = Depends(get_db)):
    """Get active testimonials ordered by sort_order."""
    result = await db.execute(
        select(Testimonial)
        .where(Testimonial.is_active == True)
        .order_by(Testimonial.sort_order)
    )
    return result.scalars().all()


@router.get("/portfolio", response_model=List[PortfolioResponse])
async def get_public_portfolio(db: AsyncSession = Depends(get_db)):
    """Get active portfolio items ordered by sort_order."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.is_active == True)
        .order_by(Portfolio.sort_order)
    )
    return result.scalars().all()


@router.get("/portfolio/by-category")
async def get_portfolio_by_category(db: AsyncSession = Depends(get_db)):
    """Get active portfolio items grouped by category."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.is_active == True)
        .order_by(Portfolio.category, Portfolio.sort_order)
    )
    portfolio_items = result.scalars().all()
    
    # Group by category
    grouped = defaultdict(list)
    for item in portfolio_items:
        grouped[item.category].append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "image_url": item.image_url,
            "sort_order": item.sort_order
        })
    
    return dict(grouped)


@router.get("/settings")
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    """Get public site settings (contact info, social links, etc.)."""
    from models import SiteSetting
    result = await db.execute(select(SiteSetting))
    settings_list = result.scalars().all()
    return {s.key: s.value for s in settings_list}
