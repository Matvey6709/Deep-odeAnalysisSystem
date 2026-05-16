from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(name=data.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.get(models.User, user_id)


def list_users(db: Session) -> list[models.User]:
    return list(db.scalars(select(models.User).order_by(models.User.id)))


def create_device(db: Session, data: schemas.DeviceCreate) -> models.Device:
    device = models.Device(name=data.name, user_id=data.user_id)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_device(db: Session, device_id: int) -> Optional[models.Device]:
    return db.get(models.Device, device_id)


def list_devices(db: Session, user_id: Optional[int] = None) -> list[models.Device]:
    stmt = select(models.Device).order_by(models.Device.id)
    if user_id is not None:
        stmt = stmt.where(models.Device.user_id == user_id)
    return list(db.scalars(stmt))


def add_statistic(db: Session, device_id: int, data: schemas.StatisticIn) -> models.Statistic:
    stat = models.Statistic(device_id=device_id, x=data.x, y=data.y, z=data.z)
    db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat


def list_statistics(
    db: Session,
    device_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100,
) -> list[models.Statistic]:
    stmt = select(models.Statistic).where(models.Statistic.device_id == device_id)
    if start is not None:
        stmt = stmt.where(models.Statistic.created_at >= start)
    if end is not None:
        stmt = stmt.where(models.Statistic.created_at <= end)
    stmt = stmt.order_by(models.Statistic.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
