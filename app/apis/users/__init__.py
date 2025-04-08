from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# Create router
router = APIRouter(prefix="/users", tags=["users"])

# Define paths for storing user data
USERS_DIR = Path("data/users")
USERS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/")
async def list_users():
    """List all users"""
    users = []
    for user_file in USERS_DIR.glob("*.json"):
        with open(user_file, "r") as f:
            user_data = json.load(f)
            # Remove sensitive information
            if "password" in user_data:
                del user_data["password"]
            users.append(user_data)
    
    return {"users": users}

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get a specific user by ID"""
    user_path = USERS_DIR / f"{user_id}.json"
    if not user_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    with open(user_path, "r") as f:
        user_data = json.load(f)
    
    # Remove sensitive information
    if "password" in user_data:
        del user_data["password"]
    
    return user_data

@router.post("/")
async def create_user(user_data: Dict[str, Any]):
    """Create a new user"""
    # Validate required fields
    required_fields = ["email", "password", "name"]
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # Check if email already exists
    for user_file in USERS_DIR.glob("*.json"):
        with open(user_file, "r") as f:
            existing_user = json.load(f)
            if existing_user.get("email") == user_data["email"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email {user_data['email']} already exists"
                )
    
    # Generate user ID
    import uuid
    user_id = str(uuid.uuid4())
    user_data["id"] = user_id
    
    # Add timestamps
    now = datetime.utcnow().isoformat()
    user_data["created_at"] = now
    user_data["updated_at"] = now
    
    # Hash password (in a real app, use a proper password hashing library)
    import hashlib
    user_data["password"] = hashlib.sha256(user_data["password"].encode()).hexdigest()
    
    # Save user data
    user_path = USERS_DIR / f"{user_id}.json"
    with open(user_path, "w") as f:
        json.dump(user_data, f, indent=2)
    
    # Remove password from response
    response_data = user_data.copy()
    del response_data["password"]
    
    return response_data

@router.put("/{user_id}")
async def update_user(user_id: str, user_data: Dict[str, Any]):
    """Update an existing user"""
    user_path = USERS_DIR / f"{user_id}.json"
    if not user_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Load existing user data
    with open(user_path, "r") as f:
        existing_user = json.load(f)
    
    # Update fields
    for key, value in user_data.items():
        if key != "id" and key != "created_at":  # Don't allow changing ID or creation date
            existing_user[key] = value
    
    # Update timestamp
    existing_user["updated_at"] = datetime.utcnow().isoformat()
    
    # Hash password if provided
    if "password" in user_data:
        import hashlib
        existing_user["password"] = hashlib.sha256(user_data["password"].encode()).hexdigest()
    
    # Save updated user data
    with open(user_path, "w") as f:
        json.dump(existing_user, f, indent=2)
    
    # Remove password from response
    response_data = existing_user.copy()
    if "password" in response_data:
        del response_data["password"]
    
    return response_data

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    user_path = USERS_DIR / f"{user_id}.json"
    if not user_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user_path.unlink()
    return {"id": user_id, "message": "User deleted successfully"}

@router.post("/login")
async def login(credentials: Dict[str, str]):
    """Login a user"""
    # Validate required fields
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # Hash password for comparison
    import hashlib
    hashed_password = hashlib.sha256(credentials["password"].encode()).hexdigest()
    
    # Find user by email
    for user_file in USERS_DIR.glob("*.json"):
        with open(user_file, "r") as f:
            user_data = json.load(f)
            if user_data.get("email") == credentials["email"]:
                # Check password
                if user_data.get("password") == hashed_password:
                    # Generate token (in a real app, use JWT)
                    token = {
                        "user_id": user_data["id"],
                        "email": user_data["email"],
                        "exp": (datetime.utcnow() + timedelta(days=1)).isoformat()
                    }
                    
                    # Remove password from response
                    response_data = user_data.copy()
                    del response_data["password"]
                    
                    return {
                        "token": token,
                        "user": response_data
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid password"
                    )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with email {credentials['email']} not found"
    )
