from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from urllib.parse import quote
import secrets

from database import get_db
from models import User, UserRole
from schemas import Token, UserResponse
from config import settings
from auth import (
    create_access_token,
    create_refresh_token,
    exchange_line_code_for_token,
    get_line_user_profile,
    get_current_user,
    verify_refresh_token
)

router = APIRouter()

# Store state tokens temporarily (in production, use Redis)
state_store = {}


@router.get("/line")
async def line_login_redirect():
    """Redirect to LINE Login page."""
    state = secrets.token_urlsafe(32)
    state_store[state] = True  # Store state for verification
    
    redirect_uri = f"{settings.BACKEND_URL}/api/auth/callback"
    
    line_auth_url = (
        f"{settings.LINE_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={settings.LINE_CHANNEL_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope=profile%20openid"
    )
    
    return RedirectResponse(url=line_auth_url)


@router.get("/callback")
async def line_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle LINE OAuth callback."""
    # Verify state
    if state not in state_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Remove used state
    del state_store[state]
    
    # Exchange code for access token
    redirect_uri = f"{settings.BACKEND_URL}/api/auth/callback"
    token_data = await exchange_line_code_for_token(code, redirect_uri)
    line_access_token = token_data.get("access_token")
    
    if not line_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to obtain LINE access token"
        )
    
    # Get LINE user profile
    line_profile = await get_line_user_profile(line_access_token)
    line_user_id = line_profile.get("userId")
    display_name = line_profile.get("displayName", "Unknown User")
    
    # Find or create user
    result = await db.execute(select(User).where(User.line_user_id == line_user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user with customer role by default
        user = User(
            line_user_id=line_user_id,
            display_name=display_name,
            role=UserRole.customer,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update display name if changed
        if user.display_name != display_name:
            user.display_name = display_name
            await db.commit()
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate JWT tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    # Redirect to frontend with tokens and role (URL-encode to be safe)
    frontend_redirect = (
        f"{settings.FRONTEND_URL}/auth/callback"
        f"?access_token={quote(access_token, safe='')}"
        f"&refresh_token={quote(refresh_token, safe='')}"
        f"&role={quote(user.role.value, safe='')}"
    )
    
    return RedirectResponse(url=frontend_redirect, status_code=302)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token and get user_id
        payload = verify_refresh_token(refresh_token)
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Convert sub from string to int (JWT spec requires sub to be a string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in refresh token"
            )
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (client should remove tokens)."""
    return {"message": "Logged out successfully"}
