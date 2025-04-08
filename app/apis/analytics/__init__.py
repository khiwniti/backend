from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.base import Restaurant, AnalyticsData, BaseResponse
from ..apis.auth import get_current_user
import pandas as pd
import numpy as np

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Mock data for demonstration - Replace with actual database queries
MOCK_RESTAURANTS = {
    "1": Restaurant(
        id="1",
        name="Sample Restaurant",
        location="New York",
        cuisine_type="Italian",
        owner_id="user1",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
}

MOCK_ANALYTICS = {
    "1": [
        AnalyticsData(
            id="1",
            restaurant_id="1",
            metric_type="foot_traffic",
            value=150.0,
            timestamp=datetime.now() - timedelta(days=i),
            metadata={"source": "sensor"}
        ) for i in range(30)
    ]
}

@router.get("/restaurants", response_model=BaseResponse)
async def get_restaurants(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        data={"restaurants": list(MOCK_RESTAURANTS.values())}
    )

@router.get("/restaurants/{restaurant_id}", response_model=BaseResponse)
async def get_restaurant(restaurant_id: str, current_user: User = Depends(get_current_user)):
    if restaurant_id not in MOCK_RESTAURANTS:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return BaseResponse(
        data={"restaurant": MOCK_RESTAURANTS[restaurant_id]}
    )

@router.get("/metrics/{restaurant_id}", response_model=BaseResponse)
async def get_metrics(
    restaurant_id: str,
    metric_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    if restaurant_id not in MOCK_ANALYTICS:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    metrics = MOCK_ANALYTICS[restaurant_id]
    
    if metric_type:
        metrics = [m for m in metrics if m.metric_type == metric_type]
    
    if start_date:
        metrics = [m for m in metrics if m.timestamp >= start_date]
    
    if end_date:
        metrics = [m for m in metrics if m.timestamp <= end_date]
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame([m.dict() for m in metrics])
    
    # Calculate basic statistics
    stats = {
        "mean": df["value"].mean(),
        "median": df["value"].median(),
        "std": df["value"].std(),
        "min": df["value"].min(),
        "max": df["value"].max()
    }
    
    return BaseResponse(
        data={
            "metrics": metrics,
            "statistics": stats
        }
    )

@router.get("/trends/{restaurant_id}", response_model=BaseResponse)
async def get_trends(
    restaurant_id: str,
    metric_type: str,
    window: int = 7,
    current_user: User = Depends(get_current_user)
):
    if restaurant_id not in MOCK_ANALYTICS:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    metrics = [m for m in MOCK_ANALYTICS[restaurant_id] if m.metric_type == metric_type]
    df = pd.DataFrame([m.dict() for m in metrics])
    
    # Calculate moving average
    df["moving_avg"] = df["value"].rolling(window=window).mean()
    
    # Calculate trend
    df["trend"] = np.polyfit(range(len(df)), df["value"], 1)[0]
    
    return BaseResponse(
        data={
            "trends": df.to_dict(orient="records")
        }
    ) 