from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
import tempfile
import shutil
import uuid
from datetime import datetime

# Create router
router = APIRouter(prefix="/langflow", tags=["langflow"])

# For Cloudflare deployment, we'll use KV instead of local file system
# This is a fallback for local development
FLOWS_DIR = Path("data/flows")
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Helper function to determine if we're running in Cloudflare
def is_cloudflare_environment():
    return (os.environ.get("CF_PAGES") is not None or
            os.environ.get("WORKERS_RS_VERSION") is not None or
            os.environ.get("CLOUDFLARE_DEPLOYMENT", "false").lower() == "true")

# Helper functions for KV storage
async def kv_get(key: str, namespace="FLOW_KV"):
    # In Cloudflare environment, use KV
    if is_cloudflare_environment():
        from fastapi import Request
        request = Request.get_current()
        kv = getattr(request.app.state, namespace, None)
        if kv:
            return await kv.get(key, type="json")
    # Fallback to local file
    flow_path = FLOWS_DIR / f"{key}.json"
    if flow_path.exists():
        with open(flow_path, "r") as f:
            return json.load(f)
    return None

async def kv_put(key: str, value: Any, namespace="FLOW_KV"):
    # In Cloudflare environment, use KV
    if is_cloudflare_environment():
        from fastapi import Request
        request = Request.get_current()
        kv = getattr(request.app.state, namespace, None)
        if kv:
            await kv.put(key, json.dumps(value))
            return True
    # Fallback to local file
    flow_path = FLOWS_DIR / f"{key}.json"
    with open(flow_path, "w") as f:
        json.dump(value, f, indent=2)
    return True

async def kv_delete(key: str, namespace="FLOW_KV"):
    # In Cloudflare environment, use KV
    if is_cloudflare_environment():
        from fastapi import Request
        request = Request.get_current()
        kv = getattr(request.app.state, namespace, None)
        if kv:
            await kv.delete(key)
            return True
    # Fallback to local file
    flow_path = FLOWS_DIR / f"{key}.json"
    if flow_path.exists():
        flow_path.unlink()
    return True

async def kv_list(namespace="FLOW_KV"):
    # In Cloudflare environment, use KV
    if is_cloudflare_environment():
        from fastapi import Request
        request = Request.get_current()
        kv = getattr(request.app.state, namespace, None)
        if kv:
            return await kv.list()
    # Fallback to local file
    return [f.stem for f in FLOWS_DIR.glob("*.json")]

@router.get("/")
async def get_langflow_status():
    """Check if Langflow is available"""
    try:
        # This is a simple check to see if langflow is installed
        import langflow
        return {"status": "ok", "version": langflow.__version__}
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Langflow is not installed"
        )

@router.get("/flows")
async def list_flows():
    """List all available flows"""
    flows = []
    flow_ids = await kv_list()

    for flow_id in flow_ids:
        flow_data = await kv_get(flow_id)
        if flow_data:
            flows.append({
                "id": flow_id,
                "name": flow_data.get("name", flow_id),
                "description": flow_data.get("description", ""),
                "created_at": flow_data.get("created_at", ""),
                "updated_at": flow_data.get("updated_at", "")
            })
    return {"flows": flows}

@router.get("/flows/{flow_id}")
async def get_flow(flow_id: str):
    """Get a specific flow by ID"""
    flow_data = await kv_get(flow_id)
    if not flow_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with ID {flow_id} not found"
        )

    return flow_data

@router.post("/flows")
async def create_flow(flow_data: Dict[str, Any]):
    """Create a new flow"""
    flow_id = flow_data.get("id", None)
    if not flow_id:
        # Generate a unique ID if not provided
        flow_id = str(uuid.uuid4())
        flow_data["id"] = flow_id

    # Add timestamps
    now = datetime.now(datetime.timezone.utc).isoformat()
    flow_data["created_at"] = now
    flow_data["updated_at"] = now

    # Store in KV
    await kv_put(flow_id, flow_data)

    return {"id": flow_id, "message": "Flow created successfully"}

@router.put("/flows/{flow_id}")
async def update_flow(flow_id: str, flow_data: Dict[str, Any]):
    """Update an existing flow"""
    # Check if flow exists
    existing_flow = await kv_get(flow_id)
    if not existing_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with ID {flow_id} not found"
        )

    # Update timestamp
    flow_data["updated_at"] = datetime.now(datetime.timezone.utc).isoformat()

    # Preserve creation timestamp if not in the update data
    if "created_at" not in flow_data and "created_at" in existing_flow:
        flow_data["created_at"] = existing_flow["created_at"]

    # Store in KV
    await kv_put(flow_id, flow_data)

    return {"id": flow_id, "message": "Flow updated successfully"}

@router.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str):
    """Delete a flow"""
    # Check if flow exists
    existing_flow = await kv_get(flow_id)
    if not existing_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with ID {flow_id} not found"
        )

    # Delete from KV
    await kv_delete(flow_id)
    return {"id": flow_id, "message": "Flow deleted successfully"}

@router.post("/flows/{flow_id}/run")
async def run_flow(flow_id: str, inputs: Dict[str, Any]):
    """Run a specific flow with the provided inputs"""
    # Get flow from KV
    flow_data = await kv_get(flow_id)
    if not flow_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with ID {flow_id} not found"
        )

    try:
        # In Cloudflare environment, we need to handle this differently
        if is_cloudflare_environment():
            # Use a simplified flow execution for Cloudflare
            # This is a placeholder - you'll need to implement a simplified version
            # that works in Cloudflare's environment
            from app.langflow.service import langflow_service
            result = await langflow_service.run_flow(flow_id, inputs)
            return result
        else:
            # Standard execution for non-Cloudflare environments
            try:
                from langflow.processing.process import process_graph_cached
                result = process_graph_cached(flow_data, inputs)
                return result
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Langflow processing not available in this environment"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running flow: {str(e)}"
        )

@router.post("/flows/import")
async def import_flow(flow_data: Dict[str, Any]):
    """Import a flow from Langflow"""
    try:
        # Generate a unique ID
        flow_id = str(uuid.uuid4())

        # Add timestamps
        now = datetime.now(datetime.timezone.utc).isoformat()
        flow_data["created_at"] = now
        flow_data["updated_at"] = now

        # Save the flow to KV
        await kv_put(flow_id, flow_data)

        return {"id": flow_id, "message": "Flow imported successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing flow: {str(e)}"
        )

@router.get("/components")
async def list_components():
    """List all available Langflow components"""
    try:
        # Try to import langflow components
        try:
            from langflow.interface.types import get_type_list
            components = get_type_list()
        except ImportError:
            # Fallback to a basic set of components if running in Cloudflare
            if is_cloudflare_environment():
                components = [
                    {"name": "LLMChain", "type": "chain"},
                    {"name": "PromptTemplate", "type": "prompt"},
                    {"name": "Ollama", "type": "llm"},
                    {"name": "ConversationChain", "type": "chain"},
                    {"name": "ConversationBufferMemory", "type": "memory"}
                ]
            else:
                raise

        return {"components": components}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing components: {str(e)}"
        )
