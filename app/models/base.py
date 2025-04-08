from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: str = "user"
    created_at: datetime
    updated_at: datetime

class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisine_type: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

class AnalyticsData(BaseModel):
    id: str
    restaurant_id: str
    metric_type: str
    value: float
    timestamp: datetime
    metadata: Optional[dict] = None

class Competitor(BaseModel):
    id: str
    name: str
    location: str
    cuisine_type: str
    metrics: Optional[dict] = None
    created_at: datetime
    updated_at: datetime 