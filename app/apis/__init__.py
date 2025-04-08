# Import all API routers
from fastapi import APIRouter

# Create main router
router = APIRouter()

# Import sub-routers
from .langflow import router as langflow_router
from .workflows import router as workflows_router
from .data import router as data_router
from .users import router as users_router

# Include sub-routers
router.include_router(langflow_router)
router.include_router(workflows_router)
router.include_router(data_router)
router.include_router(users_router)