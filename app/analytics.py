"""Aggregate statistics in PostgreSQL (min/max/count/sum/median)."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app import models


AXES = ("x", "y", "z")


def _empty_axis() -> dict:
    return {"min": None, "max": None, "count": 0, "sum": 0.0, "median": None}


def _empty_device(device_id: int) -> dict:
    return {"device_id": device_id, "x": _empty_axis(), "y": _empty_axis(), "z": _empty_axis()}


def _apply_filters(
    stmt: Select,
    start: Optional[datetime],
    end: Optional[datetime],
) -> Select:
    if start is not None:
        stmt = stmt.where(models.Statistic.created_at >= start)
    if end is not None:
        stmt = stmt.where(models.Statistic.created_at <= end)
    return stmt


def _axis_columns():
    cols = []
    for axis in AXES:
        column = getattr(models.Statistic, axis)
        cols.extend([
            func.min(column).label(f"{axis}_min"),
            func.max(column).label(f"{axis}_max"),
            func.count(column).label(f"{axis}_count"),
            func.coalesce(func.sum(column), 0.0).label(f"{axis}_sum"),
            func.percentile_cont(0.5).within_group(column.asc()).label(f"{axis}_median"),
        ])
    return cols


def _row_to_device(device_id: int, row) -> dict:
    if row is None:
        return _empty_device(device_id)
    out = {"device_id": device_id}
    for axis in AXES:
        count = getattr(row, f"{axis}_count") or 0
        if count == 0:
            out[axis] = _empty_axis()
            continue
        out[axis] = {
            "min": getattr(row, f"{axis}_min"),
            "max": getattr(row, f"{axis}_max"),
            "count": int(count),
            "sum": float(getattr(row, f"{axis}_sum") or 0.0),
            "median": float(getattr(row, f"{axis}_median")) if getattr(row, f"{axis}_median") is not None else None,
        }
    return out


def device_analytics(
    db: Session,
    device_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    stmt = select(*_axis_columns()).where(models.Statistic.device_id == device_id)
    stmt = _apply_filters(stmt, start, end)
    row = db.execute(stmt).one_or_none()
    return _row_to_device(device_id, row)


def user_analytics(
    db: Session,
    user_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    device_ids = [
        d_id for d_id in db.scalars(
            select(models.Device.id).where(models.Device.user_id == user_id)
        )
    ]

    per_device = [device_analytics(db, d_id, start, end) for d_id in device_ids]

    agg_stmt = (
        select(*_axis_columns())
        .join(models.Device, models.Device.id == models.Statistic.device_id)
        .where(models.Device.user_id == user_id)
    )
    agg_stmt = _apply_filters(agg_stmt, start, end)
    agg_row = db.execute(agg_stmt).one_or_none()
    aggregated = _row_to_device(0, agg_row)

    return {"user_id": user_id, "aggregated": aggregated, "per_device": per_device}
