"""
Data Migration Script: Google Sheets → PostgreSQL

This script fetches data from the existing Google Sheets API and migrates it
to the PostgreSQL database.

Usage:
    python scripts/migrate_data.py

Requirements:
    - Backend must be running or database must be accessible
    - Google Sheets API must be reachable
"""

import asyncio
import httpx
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, engine
from models import News, Service, Product, Testimonial, Portfolio, Base


# Google Sheets API Configuration
GOOGLE_SHEETS_BASE_URL = "https://script.google.com/macros/s/AKfycbxnf_4q6fwLvPM1bnNWKKAGwgUdigMEwbLnilce511dnWJIGt7Gvqkrpoly098oZxPBhA/exec"
SHEETS = ["news", "service", "product", "beforeafter", "recommendation"]


async def fetch_sheet_data(sheet_name: str) -> list:
    """Fetch data from Google Sheets API."""
    print(f"📥 Fetching {sheet_name} data from Google Sheets...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{GOOGLE_SHEETS_BASE_URL}?sheet={sheet_name}")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Fetched {len(data)} records from {sheet_name}")
            return data
        except Exception as e:
            print(f"❌ Error fetching {sheet_name}: {e}")
            return []


async def migrate_news(db: AsyncSession, data: list) -> int:
    """Migrate news data to News table."""
    print("\n📰 Migrating News...")
    
    count = 0
    for idx, item in enumerate(data):
        try:
            # Parse date - handle different formats
            date_str = item.get("date", "")
            try:
                news_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                try:
                    news_date = datetime.strptime(date_str, "%Y/%m/%d").date()
                except:
                    print(f"⚠️  Invalid date format for news #{idx}: {date_str}, using today")
                    news_date = date.today()
            
            news = News(
                title=item.get("title", "Untitled"),
                content=item.get("content", ""),
                cover_image=item.get("image_url") or item.get("cover_image"),
                category=item.get("category", "General"),
                date=news_date,
                sort_order=idx
            )
            db.add(news)
            count += 1
        except Exception as e:
            print(f"❌ Error migrating news item #{idx}: {e}")
    
    await db.commit()
    print(f"✅ Migrated {count} news items")
    return count


async def migrate_services(db: AsyncSession, data: list) -> int:
    """Migrate service data to Service table."""
    print("\n💆 Migrating Services...")
    
    count = 0
    for idx, item in enumerate(data):
        try:
            # Parse price - handle different formats
            price_str = str(item.get("price", "0")).replace(",", "").replace("$", "").replace("NT", "").strip()
            try:
                price = int(float(price_str))
            except:
                print(f"⚠️  Invalid price for service #{idx}: {price_str}, using 0")
                price = 0
            
            # Parse duration
            duration_str = str(item.get("duration", "60")).replace("分", "").replace("min", "").strip()
            try:
                duration = int(duration_str)
            except:
                print(f"⚠️  Invalid duration for service #{idx}: {duration_str}, using 60")
                duration = 60
            
            service = Service(
                name=item.get("name", "Unnamed Service"),
                description=item.get("description", ""),
                price=price,
                duration_min=duration,
                category=item.get("category", "General"),
                image_url=item.get("image_url"),
                is_active=item.get("is_active", True) if isinstance(item.get("is_active"), bool) else True,
                sort_order=idx
            )
            db.add(service)
            count += 1
        except Exception as e:
            print(f"❌ Error migrating service item #{idx}: {e}")
    
    await db.commit()
    print(f"✅ Migrated {count} services")
    return count


async def migrate_products(db: AsyncSession, data: list) -> int:
    """Migrate product data to Product table."""
    print("\n🛍️  Migrating Products...")
    
    count = 0
    for idx, item in enumerate(data):
        try:
            # Parse price
            price_str = str(item.get("price", "0")).replace(",", "").replace("$", "").replace("NT", "").strip()
            try:
                price = int(float(price_str))
            except:
                print(f"⚠️  Invalid price for product #{idx}: {price_str}, using 0")
                price = 0
            
            product = Product(
                name=item.get("name", "Unnamed Product"),
                description=item.get("description", ""),
                price=price,
                spec=item.get("spec") or item.get("specification"),
                image_url=item.get("image_url"),
                is_stock=item.get("is_stock", True) if isinstance(item.get("is_stock"), bool) else True,
                sort_order=idx
            )
            db.add(product)
            count += 1
        except Exception as e:
            print(f"❌ Error migrating product item #{idx}: {e}")
    
    await db.commit()
    print(f"✅ Migrated {count} products")
    return count


async def migrate_testimonials(db: AsyncSession, data: list) -> int:
    """Migrate recommendation data to Testimonial table."""
    print("\n⭐ Migrating Testimonials...")
    
    count = 0
    for idx, item in enumerate(data):
        try:
            # Parse rating
            rating_str = str(item.get("rating", "5"))
            try:
                rating = int(float(rating_str))
                rating = max(1, min(5, rating))  # Clamp between 1-5
            except:
                print(f"⚠️  Invalid rating for testimonial #{idx}: {rating_str}, using 5")
                rating = 5
            
            testimonial = Testimonial(
                customer_name=item.get("customer_name") or item.get("name", "Anonymous"),
                content=item.get("content", ""),
                rating=rating,
                avatar_url=item.get("avatar_url"),
                sort_order=idx
            )
            db.add(testimonial)
            count += 1
        except Exception as e:
            print(f"❌ Error migrating testimonial item #{idx}: {e}")
    
    await db.commit()
    print(f"✅ Migrated {count} testimonials")
    return count


async def migrate_portfolio(db: AsyncSession, data: list) -> int:
    """Migrate beforeafter data to Portfolio table."""
    print("\n🖼️  Migrating Portfolio (Before/After)...")
    
    count = 0
    for idx, item in enumerate(data):
        try:
            portfolio = Portfolio(
                title=item.get("title", "Untitled"),
                description=item.get("description", ""),
                image_url=item.get("image_url", ""),
                category=item.get("category", "General"),
                sort_order=idx
            )
            db.add(portfolio)
            count += 1
        except Exception as e:
            print(f"❌ Error migrating portfolio item #{idx}: {e}")
    
    await db.commit()
    print(f"✅ Migrated {count} portfolio items")
    return count


async def clear_existing_data(db: AsyncSession):
    """Clear existing content data (optional - use with caution!)."""
    print("\n🗑️  Clearing existing content data...")
    
    try:
        # Delete all content (preserve users and work logs)
        await db.execute("DELETE FROM portfolio")
        await db.execute("DELETE FROM testimonials")
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM services")
        await db.execute("DELETE FROM news")
        await db.commit()
        print("✅ Existing content cleared")
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        await db.rollback()


async def main():
    """Main migration function."""
    print("=" * 60)
    print("🚀 Google Sheets → PostgreSQL Migration")
    print("=" * 60)
    
    # Create tables if they don't exist
    print("\n📦 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables ready")
    
    # Fetch all data from Google Sheets
    print("\n📥 Fetching data from Google Sheets...")
    data_dict = {}
    for sheet in SHEETS:
        data = await fetch_sheet_data(sheet)
        data_dict[sheet] = data
    
    # Ask user if they want to clear existing data
    print("\n⚠️  Do you want to clear existing content data before migration?")
    print("   This will DELETE all News, Services, Products, Testimonials, and Portfolio items.")
    print("   (Work logs and users will be preserved)")
    response = input("   Type 'yes' to confirm: ").strip().lower()
    
    async with AsyncSessionLocal() as db:
        if response == 'yes':
            await clear_existing_data(db)
        else:
            print("   Skipping data clearing. New data will be added to existing content.")
        
        # Migrate each content type
        total_migrated = 0
        
        if data_dict.get("news"):
            total_migrated += await migrate_news(db, data_dict["news"])
        
        if data_dict.get("service"):
            total_migrated += await migrate_services(db, data_dict["service"])
        
        if data_dict.get("product"):
            total_migrated += await migrate_products(db, data_dict["product"])
        
        if data_dict.get("recommendation"):
            total_migrated += await migrate_testimonials(db, data_dict["recommendation"])
        
        if data_dict.get("beforeafter"):
            total_migrated += await migrate_portfolio(db, data_dict["beforeafter"])
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Migration completed! Total records migrated: {total_migrated}")
    print("=" * 60)
    print("\n📊 Migration Summary:")
    print(f"   News: {len(data_dict.get('news', []))} items")
    print(f"   Services: {len(data_dict.get('service', []))} items")
    print(f"   Products: {len(data_dict.get('product', []))} items")
    print(f"   Testimonials: {len(data_dict.get('recommendation', []))} items")
    print(f"   Portfolio: {len(data_dict.get('beforeafter', []))} items")
    print("\n💡 Next steps:")
    print("   1. Verify data in your database")
    print("   2. Create an admin user if not already done")
    print("   3. Start the backend server: uvicorn main:app --reload")
    print("   4. Test the API endpoints")


if __name__ == "__main__":
    asyncio.run(main())
