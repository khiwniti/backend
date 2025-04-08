from app.celery.config import celery_app
from app.langflow.service import langflow_service
from typing import Dict, Any, List
import json
import uuid

@celery_app.task(name="app.tasks.ai.run_restaurant_analysis")
def run_restaurant_analysis(restaurant_id: str, timeframe: str, metrics: List[str]) -> Dict[str, Any]:
    """Run restaurant analysis using Langflow"""
    try:
        result = langflow_service.run_flow(
            "restaurant_analysis",
            {
                "restaurant_id": restaurant_id,
                "timeframe": timeframe,
                "metrics": metrics
            }
        )
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@celery_app.task(name="app.tasks.ai.run_competitor_analysis")
def run_competitor_analysis(restaurant_id: str, competitor_ids: List[str], timeframe: str) -> Dict[str, Any]:
    """Run competitor analysis using Langflow"""
    try:
        result = langflow_service.run_flow(
            "competitor_analysis",
            {
                "restaurant_id": restaurant_id,
                "competitor_ids": competitor_ids,
                "timeframe": timeframe
            }
        )
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@celery_app.task(name="app.tasks.ai.run_menu_optimization")
def run_menu_optimization(restaurant_id: str, menu_items: List[Dict[str, Any]], sales_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run menu optimization using Langflow"""
    try:
        result = langflow_service.run_flow(
            "menu_optimization",
            {
                "restaurant_id": restaurant_id,
                "menu_items": menu_items,
                "sales_data": sales_data
            }
        )
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@celery_app.task(name="app.tasks.ai.generate_insights")
def generate_insights(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights from data using Langflow"""
    try:
        # Create a custom flow for insight generation
        flow_config = {
            "name": "insight_generation",
            "description": "Generate insights from data",
            "input_schema": {
                "data": "dict",
                "context": "dict"
            },
            "output_schema": {
                "insights": "list",
                "recommendations": "list",
                "key_findings": "list"
            }
        }
        
        result = langflow_service.run_flow(
            "insight_generation",
            {
                "data": data,
                "context": context
            }
        )
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@celery_app.task(name="app.tasks.ai.predict_trends")
def predict_trends(data: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
    """Predict future trends using Langflow"""
    try:
        # Create a custom flow for trend prediction
        flow_config = {
            "name": "trend_prediction",
            "description": "Predict future trends",
            "input_schema": {
                "data": "dict",
                "timeframe": "str"
            },
            "output_schema": {
                "predictions": "dict",
                "confidence": "float",
                "factors": "list"
            }
        }
        
        result = langflow_service.run_flow(
            "trend_prediction",
            {
                "data": data,
                "timeframe": timeframe
            }
        )
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 