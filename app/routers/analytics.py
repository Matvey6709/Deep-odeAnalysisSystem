from datetime import datetime
from typing import Optional

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.celery_app import celery_app
from app.database import get_db
from app.tasks import device_analytics_task, user_analytics_task


router = APIRouter(tags=["analytics"])


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


@router.post(
    "/devices/{device_id}/analytics",
    response_model=schemas.TaskAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_device_analytics(
    device_id: int,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    if not crud.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="device not found")
    async_result = device_analytics_task.delay(device_id, _iso(start), _iso(end))
    return schemas.TaskAccepted(task_id=async_result.id, status_url=f"/tasks/{async_result.id}")


@router.post(
    "/users/{user_id}/analytics",
    response_model=schemas.TaskAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_user_analytics(
    user_id: int,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    if not crud.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="user not found")
    async_result = user_analytics_task.delay(user_id, _iso(start), _iso(end))
    return schemas.TaskAccepted(task_id=async_result.id, status_url=f"/tasks/{async_result.id}")


@router.get("/tasks/{task_id}", response_model=schemas.TaskStatus)
def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    payload = schemas.TaskStatus(task_id=task_id, status=result.status)
    if result.successful():
        payload.result = result.result
    elif result.failed():
        payload.result = {"error": str(result.result)}
    return payload
