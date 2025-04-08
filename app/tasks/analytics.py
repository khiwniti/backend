from app.celery.config import celery_app
from app.database.config import get_db
from app.database.models import AnalyticsData, Restaurant
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any

@celery_app.task(name="app.tasks.analytics.process_analytics")
def process_analytics(restaurant_id: str, metric_type: str, value: float, timestamp: datetime, metadata: Dict[str, Any] = None):
    """Process and store analytics data"""
    db = next(get_db())
    try:
        analytics = AnalyticsData(
            id=str(uuid.uuid4()),
            restaurant_id=restaurant_id,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            metadata=metadata
        )
        db.add(analytics)
        db.commit()
        return {"success": True, "id": analytics.id}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@celery_app.task(name="app.tasks.analytics.generate_daily_report")
def generate_daily_report(restaurant_id: str):
    """Generate daily analytics report"""
    db = next(get_db())
    try:
        # Get data for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        analytics = db.query(AnalyticsData).filter(
            AnalyticsData.restaurant_id == restaurant_id,
            AnalyticsData.timestamp >= start_time,
            AnalyticsData.timestamp <= end_time
        ).all()
        
        if not analytics:
            return {"success": False, "message": "No data available"}
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'metric_type': a.metric_type,
            'value': a.value,
            'timestamp': a.timestamp
        } for a in analytics])
        
        # Calculate statistics
        stats = {}
        for metric in df['metric_type'].unique():
            metric_data = df[df['metric_type'] == metric]
            stats[metric] = {
                'mean': metric_data['value'].mean(),
                'median': metric_data['value'].median(),
                'std': metric_data['value'].std(),
                'min': metric_data['value'].min(),
                'max': metric_data['value'].max(),
                'trend': calculate_trend(metric_data['value'])
            }
        
        return {
            "success": True,
            "restaurant_id": restaurant_id,
            "timeframe": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "statistics": stats
        }
    except Exception as e:
        raise e
    finally:
        db.close()

@celery_app.task(name="app.tasks.analytics.calculate_trends")
def calculate_trends(restaurant_id: str, metric_type: str, window: int = 7):
    """Calculate trends for a specific metric"""
    db = next(get_db())
    try:
        # Get data for the specified window
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=window)
        
        analytics = db.query(AnalyticsData).filter(
            AnalyticsData.restaurant_id == restaurant_id,
            AnalyticsData.metric_type == metric_type,
            AnalyticsData.timestamp >= start_time,
            AnalyticsData.timestamp <= end_time
        ).order_by(AnalyticsData.timestamp).all()
        
        if not analytics:
            return {"success": False, "message": "No data available"}
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'value': a.value,
            'timestamp': a.timestamp
        } for a in analytics])
        
        # Calculate moving average
        df['moving_avg'] = df['value'].rolling(window=3).mean()
        
        # Calculate trend
        x = np.arange(len(df))
        y = df['value'].values
        trend = np.polyfit(x, y, 1)[0]
        
        return {
            "success": True,
            "restaurant_id": restaurant_id,
            "metric_type": metric_type,
            "window": window,
            "trend": trend,
            "data": df.to_dict(orient='records')
        }
    except Exception as e:
        raise e
    finally:
        db.close()

def calculate_trend(values: List[float]) -> str:
    """Calculate trend direction based on values"""
    if len(values) < 2:
        return "stable"
    
    x = np.arange(len(values))
    y = np.array(values)
    slope = np.polyfit(x, y, 1)[0]
    
    if slope > 0.1:
        return "up"
    elif slope < -0.1:
        return "down"
    else:
        return "stable" 