from datetime import datetime
from typing import Optional

from app import analytics
from app.celery_app import celery_app
from app.database import SessionLocal


def _parse(dt: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(dt) if dt else None


@celery_app.task(name="analytics.device")
def device_analytics_task(
    device_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> dict:
    db = SessionLocal()
    try:
        return analytics.device_analytics(db, device_id, _parse(start), _parse(end))
    finally:
        db.close()


@celery_app.task(name="analytics.user")
def user_analytics_task(
    user_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> dict:
    db = SessionLocal()
    try:
        return analytics.user_analytics(db, user_id, _parse(start), _parse(end))
    finally:
        db.close()
