from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from ..models.base import BaseResponse
from ..apis.auth import get_current_user
from ..langflow.service import langflow_service

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

@router.post("/analyze-restaurant", response_model=BaseResponse)
async def analyze_restaurant(
    restaurant_id: str,
    timeframe: str,
    metrics: List[str],
    current_user: User = Depends(get_current_user)
):
    try:
        result = await langflow_service.run_flow(
            "restaurant_analysis",
            {
                "restaurant_id": restaurant_id,
                "timeframe": timeframe,
                "metrics": metrics
            }
        )
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/analyze-competitors", response_model=BaseResponse)
async def analyze_competitors(
    restaurant_id: str,
    competitor_ids: List[str],
    timeframe: str,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await langflow_service.run_flow(
            "competitor_analysis",
            {
                "restaurant_id": restaurant_id,
                "competitor_ids": competitor_ids,
                "timeframe": timeframe
            }
        )
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/optimize-menu", response_model=BaseResponse)
async def optimize_menu(
    restaurant_id: str,
    menu_items: List[Dict[str, Any]],
    sales_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    try:
        result = await langflow_service.run_flow(
            "menu_optimization",
            {
                "restaurant_id": restaurant_id,
                "menu_items": menu_items,
                "sales_data": sales_data
            }
        )
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/flows", response_model=BaseResponse)
async def get_available_flows(current_user: User = Depends(get_current_user)):
    try:
        flows = langflow_service.flows
        return BaseResponse(data={"flows": flows})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 