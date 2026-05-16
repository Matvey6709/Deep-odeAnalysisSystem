from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db


router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=schemas.DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(data: schemas.DeviceCreate, db: Session = Depends(get_db)):
    if data.user_id is not None and not crud.get_user(db, data.user_id):
        raise HTTPException(status_code=404, detail="user not found")
    return crud.create_device(db, data)


@router.get("", response_model=list[schemas.DeviceOut])
def list_devices(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.list_devices(db, user_id=user_id)


@router.get("/{device_id}", response_model=schemas.DeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = crud.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    return device


@router.post(
    "/{device_id}/statistics",
    response_model=schemas.StatisticOut,
    status_code=status.HTTP_201_CREATED,
)
def add_statistic(device_id: int, data: schemas.StatisticIn, db: Session = Depends(get_db)):
    if not crud.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="device not found")
    return crud.add_statistic(db, device_id, data)


@router.get("/{device_id}/statistics", response_model=list[schemas.StatisticOut])
def get_statistics(
    device_id: int,
    start: Optional[datetime] = Query(None, description="ISO datetime (inclusive)"),
    end: Optional[datetime] = Query(None, description="ISO datetime (inclusive)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    if not crud.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="device not found")
    return crud.list_statistics(db, device_id, start=start, end=end, limit=limit)
