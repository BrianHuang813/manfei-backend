from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import date as date_type

from database import get_db
from models import User, Service, WorkLog
from schemas import (
    ServiceResponse,
    WorkLogCreate,
    WorkLogResponse,
    MessageResponse
)
from auth import require_staff_or_admin, get_current_user

router = APIRouter(dependencies=[Depends(require_staff_or_admin)])


@router.get("/menu", response_model=List[ServiceResponse])
async def get_staff_menu(db: AsyncSession = Depends(get_db)):
    """Get list of active services for staff task selection."""
    result = await db.execute(
        select(Service)
        .where(Service.is_active == True)
        .order_by(Service.category, Service.name)
    )
    return result.scalars().all()


@router.post("/logs", response_model=WorkLogResponse, status_code=status.HTTP_201_CREATED)
async def create_work_log(
    log: WorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a work log entry. Date must be today."""
    # Validate date is today
    today = date_type.today()
    if log.date != today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can only log work for today ({today}). Provided date: {log.date}"
        )
    
    # Validate service exists if service_id is provided
    if log.service_id:
        result = await db.execute(select(Service).where(Service.id == log.service_id))
        service = result.scalar_one_or_none()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
    
    # Create work log
    db_log = WorkLog(
        user_id=current_user.id,
        date=log.date,
        service_id=log.service_id,
        custom_task_name=log.custom_task_name,
        hours=log.hours
    )
    
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    
    # Enrich response with service name if applicable
    log_dict = {
        "id": db_log.id,
        "user_id": db_log.user_id,
        "date": db_log.date,
        "service_id": db_log.service_id,
        "custom_task_name": db_log.custom_task_name,
        "hours": db_log.hours,
        "created_at": db_log.created_at,
        "updated_at": db_log.updated_at,
        "user_display_name": current_user.display_name,
        "service_name": None
    }
    
    if db_log.service_id:
        result = await db.execute(select(Service).where(Service.id == db_log.service_id))
        service = result.scalar_one_or_none()
        if service:
            log_dict["service_name"] = service.name
    
    return log_dict


@router.get("/logs/my", response_model=List[WorkLogResponse])
async def get_my_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get work logs for the current user for today."""
    today = date_type.today()
    
    result = await db.execute(
        select(WorkLog)
        .where(WorkLog.user_id == current_user.id)
        .where(WorkLog.date == today)
        .order_by(WorkLog.created_at.desc())
    )
    work_logs = result.scalars().all()
    
    # Enrich with service names
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
            "user_display_name": current_user.display_name,
            "service_name": None
        }
        
        if log.service_id:
            service_result = await db.execute(select(Service).where(Service.id == log.service_id))
            service = service_result.scalar_one_or_none()
            if service:
                log_dict["service_name"] = service.name
        
        enriched_logs.append(log_dict)
    
    return enriched_logs
