"""
Cloudinary integration utilities.
Handles image upload to Cloudinary CDN.
"""

import asyncio
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from config import settings


def init_cloudinary():
    """Initialize Cloudinary configuration from environment variables."""
    if not settings.CLOUDINARY_CLOUD_NAME:
        print("⚠️  Cloudinary not configured (CLOUDINARY_CLOUD_NAME is empty). Image upload will be disabled.")
        return

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    print(f"☁️  Cloudinary configured: {settings.CLOUDINARY_CLOUD_NAME}")


async def upload_image(file: UploadFile) -> str:
    """
    Upload an image file to Cloudinary.
    Uses asyncio.to_thread to avoid blocking the event loop.

    Args:
        file: FastAPI UploadFile object.

    Returns:
        The secure URL of the uploaded image.

    Raises:
        HTTPException: If Cloudinary is not configured or upload fails.
    """
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(
            status_code=503,
            detail="圖片上傳服務未設定，請聯繫管理員設定 Cloudinary。",
        )

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支援的圖片格式。允許的格式：JPEG, PNG, WebP, GIF",
        )

    # Read file content
    content = await file.read()

    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="圖片大小不可超過 10MB",
        )

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            content,
            folder="manfei",
            resource_type="image",
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ],
        )
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"圖片上傳失敗：{str(e)}",
        )
