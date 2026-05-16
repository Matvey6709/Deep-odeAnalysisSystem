from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    user_id: Optional[int] = None


class DeviceOut(BaseModel):
    id: int
    name: str
    user_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatisticIn(BaseModel):
    x: float
    y: float
    z: float


class StatisticOut(StatisticIn):
    id: int
    device_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AxisAnalytics(BaseModel):
    min: Optional[float]
    max: Optional[float]
    count: int
    sum: float
    median: Optional[float]


class DeviceAnalytics(BaseModel):
    device_id: int
    x: AxisAnalytics
    y: AxisAnalytics
    z: AxisAnalytics


class UserAnalytics(BaseModel):
    user_id: int
    aggregated: DeviceAnalytics
    per_device: list[DeviceAnalytics]


class TaskAccepted(BaseModel):
    task_id: str
    status_url: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
