from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
import uuid

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS
from services.supabase_client import supabase

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


class AuthBody(BaseModel):
    email: EmailStr
    password: str


def make_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/signup")
async def signup(body: AuthBody):
    email = body.email.lower()
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # Sign up with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": body.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        
        user_id = auth_response.user.id
        
        # The trigger will auto-create the user profile
        # Wait a moment and fetch the profile
        import time
        time.sleep(0.5)
        
        res = supabase.table("users").select("*").eq("id", user_id).single().execute()
        user = res.data
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user profile")

        token = make_token(user_id)
        return {
            "access_token": token,
            "user": {"id": user["id"], "email": user["email"], "role": user["role"]}
        }
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=400, detail=f"Signup failed: {error_msg}")


@router.post("/login")
async def login(body: AuthBody):
    email = body.email.lower()

    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": body.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id = auth_response.user.id
        
        # Get user profile
        res = supabase.table("users").select("*").eq("id", user_id).single().execute()
        user = res.data
        
        if not user:
            raise HTTPException(status_code=401, detail="User profile not found")

        token = make_token(user_id)
        return {
            "access_token": token,
            "user": {"id": user["id"], "email": user["email"], "role": user["role"]}
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "credentials" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=400, detail=f"Login failed: {error_msg}")


@router.get("/me")
async def get_me(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    """Get current user info from token"""
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        # Verify with Supabase
        auth_response = supabase.auth.get_user(creds.credentials)
        if not auth_response or not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = auth_response.user.id
        
        # Fetch user profile with role from database
        res = supabase.table("users").select("*").eq("id", user_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "id": res.data["id"],
            "email": res.data["email"],
            "role": res.data["role"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

