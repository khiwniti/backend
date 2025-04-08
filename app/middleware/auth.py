from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import os
from dotenv import load_dotenv
from ..logging.config import logging_config

load_dotenv()

logger = logging_config.get_logger(__name__)

class AuthMiddleware:
    def __init__(self):
        self.security = HTTPBearer()
    
    async def __call__(self, request: Request):
        """Verify Firebase authentication token"""
        try:
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token = credentials.credentials
            decoded_token = auth.verify_id_token(token)
            
            # Add user info to request state
            request.state.user = {
                "id": decoded_token["uid"],
                "email": decoded_token["email"],
                "name": decoded_token.get("name"),
                "role": decoded_token.get("role", "user")
            }
            
            return request
        except Exception as e:
            logger.error("Authentication error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Create a singleton instance
auth_middleware = AuthMiddleware() 