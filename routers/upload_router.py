"""
Upload router for image uploads via Cloudinary.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from auth import require_admin
from utils.cloudinary import upload_image


router = APIRouter(dependencies=[Depends(require_admin)])


class UploadResponse(BaseModel):
    url: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image to Cloudinary.
    Returns the secure URL of the uploaded image.
    Requires admin authentication.
    """
    url = await upload_image(file)
    return {"url": url}
