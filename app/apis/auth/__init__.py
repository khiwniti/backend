from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials, initialize_app
import os
from ..models.base import User, BaseResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize Firebase Admin
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
})

initialize_app(cred)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return User(
            id=decoded_token["uid"],
            email=decoded_token["email"],
            name=decoded_token.get("name"),
            created_at=decoded_token.get("iat"),
            updated_at=decoded_token.get("iat")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=BaseResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        data={"user": current_user.dict()}
    )

@router.post("/refresh-token", response_model=BaseResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    try:
        custom_token = auth.create_custom_token(current_user.id)
        return BaseResponse(
            data={"token": custom_token.decode()}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        ) 