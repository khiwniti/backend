from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path

# Create router
router = APIRouter(prefix="/workflows", tags=["workflows"])

# Define paths for storing predefined workflows
WORKFLOWS_DIR = Path("data/workflows")
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Predefined workflow categories
WORKFLOW_CATEGORIES = [
    "market_research",
    "competitor_analysis",
    "customer_insights",
    "location_analysis",
    "menu_optimization",
    "foot_traffic_analysis"
]

@router.get("/")
async def get_workflow_categories():
    """Get all workflow categories"""
    return {"categories": WORKFLOW_CATEGORIES}

@router.get("/templates")
async def get_workflow_templates():
    """Get all predefined workflow templates"""
    templates = []
    for category in WORKFLOW_CATEGORIES:
        category_dir = WORKFLOWS_DIR / category
        if category_dir.exists():
            for template_file in category_dir.glob("*.json"):
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                    templates.append({
                        "id": template_file.stem,
                        "name": template_data.get("name", template_file.stem),
                        "category": category,
                        "description": template_data.get("description", ""),
                        "tags": template_data.get("tags", [])
                    })
    
    return {"templates": templates}

@router.get("/templates/{category}")
async def get_category_templates(category: str):
    """Get workflow templates for a specific category"""
    if category not in WORKFLOW_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category} not found"
        )
    
    category_dir = WORKFLOWS_DIR / category
    if not category_dir.exists():
        return {"templates": []}
    
    templates = []
    for template_file in category_dir.glob("*.json"):
        with open(template_file, "r") as f:
            template_data = json.load(f)
            templates.append({
                "id": template_file.stem,
                "name": template_data.get("name", template_file.stem),
                "category": category,
                "description": template_data.get("description", ""),
                "tags": template_data.get("tags", [])
            })
    
    return {"templates": templates}

@router.get("/templates/{category}/{template_id}")
async def get_template(category: str, template_id: str):
    """Get a specific workflow template"""
    if category not in WORKFLOW_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category} not found"
        )
    
    template_path = WORKFLOWS_DIR / category / f"{template_id}.json"
    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found in category {category}"
        )
    
    with open(template_path, "r") as f:
        template_data = json.load(f)
    
    return template_data

@router.post("/templates/{category}")
async def create_template(category: str, template_data: Dict[str, Any]):
    """Create a new workflow template"""
    if category not in WORKFLOW_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category} not found"
        )
    
    # Ensure category directory exists
    category_dir = WORKFLOWS_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    template_id = template_data.get("id", None)
    if not template_id:
        # Generate a unique ID if not provided
        import uuid
        template_id = str(uuid.uuid4())
        template_data["id"] = template_id
    
    template_path = category_dir / f"{template_id}.json"
    
    # Add timestamps and category
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    template_data["created_at"] = now
    template_data["updated_at"] = now
    template_data["category"] = category
    
    with open(template_path, "w") as f:
        json.dump(template_data, f, indent=2)
    
    return {"id": template_id, "category": category, "message": "Template created successfully"}

@router.post("/run/{category}/{template_id}")
async def run_workflow_template(category: str, template_id: str, inputs: Dict[str, Any]):
    """Run a specific workflow template with the provided inputs"""
    if category not in WORKFLOW_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category} not found"
        )
    
    template_path = WORKFLOWS_DIR / category / f"{template_id}.json"
    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found in category {category}"
        )
    
    try:
        # Load the template
        with open(template_path, "r") as f:
            template_data = json.load(f)
        
        # Import langflow components for running the workflow
        from langflow.processing.process import process_graph_cached
        
        # Process and run the workflow
        result = process_graph_cached(template_data, inputs)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running workflow: {str(e)}"
        )
