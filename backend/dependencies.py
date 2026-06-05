from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import JWT_SECRET, JWT_ALGORITHM, SUPABASE_KEY
from services.supabase_client import supabase
import httpx
import os

bearer = HTTPBearer(auto_error=False)

# Demo users fallback
_DEMO_USERS = {
    "demo-user-001":  {"id": "demo-user-001",  "email": "user@demo.com",  "role": "user"},
    "demo-admin-001": {"id": "demo-admin-001", "email": "admin@demo.com", "role": "admin"},
}


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = creds.credentials
    user_id = None
    
    print(f"[DEBUG] Received token: {token[:50]}...")  # Debug log
    print(f"[DEBUG] Supabase client exists: {supabase is not None}")
    
    # Try to verify with Supabase Auth API (for OAuth tokens)
    if supabase:
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            print(f"[DEBUG] Supabase URL: {supabase_url}")
            print(f"[DEBUG] Trying Supabase Auth validation...")
            
            # Make request to Supabase Auth API to validate token
            with httpx.Client() as client:
                response = client.get(
                    f"{supabase_url}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": supabase_key
                    },
                    timeout=5.0
                )
            
            print(f"[DEBUG] Supabase Auth response status: {response.status_code}")
            print(f"[DEBUG] Supabase Auth response body: {response.text[:200]}")
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("id")
                
                print(f"[DEBUG] Got user_id from Supabase: {user_id}")
                
                if user_id:
                    # Fetch user from database with role
                    try:
                        print(f"[DEBUG] Querying database for user_id: {user_id}")
                        res = supabase.table("users").select("*").eq("id", user_id).execute()
                        print(f"[DEBUG] Query result count: {len(res.data) if res.data else 0}")
                        print(f"[DEBUG] Query result data: {res.data}")
                        
                        if res.data and len(res.data) > 0:
                            user = res.data[0]
                            print(f"[DEBUG] Found user in database: {user['email']}, role: {user['role']}")
                            return user
                        else:
                            print(f"[DEBUG] User not found in database, will try creating...")
                            # User doesn't exist, create them
                            new_user = {
                                "id": user_id,
                                "email": user_data.get("email"),
                                "role": "user"
                            }
                            insert_res = supabase.table("users").insert(new_user).execute()
                            print(f"[DEBUG] Insert result: {insert_res.data}")
                            if insert_res.data and len(insert_res.data) > 0:
                                print(f"[DEBUG] Successfully created user in database")
                                return insert_res.data[0]
                    except Exception as db_error:
                        print(f"[DEBUG] Database error: {type(db_error).__name__}: {str(db_error)}")
                        raise
        except Exception as e:
            print(f"[DEBUG] Supabase validation exception: {type(e).__name__}: {str(e)}")
            # Not a Supabase token, try custom JWT
            pass
    else:
        print(f"[DEBUG] Supabase client is None, skipping Supabase validation")
    
    # Try our custom JWT (for email/password login)
    print(f"[DEBUG] Trying custom JWT validation...")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"[DEBUG] Got user_id from custom JWT: {user_id}")
        
        # Try Supabase database
        if supabase:
            try:
                res = supabase.table("users").select("*").eq("id", user_id).single().execute()
                if res.data:
                    print(f"[DEBUG] Found user in database: {res.data['email']}, role: {res.data['role']}")
                    return res.data
            except Exception:
                pass
    except JWTError as e:
        print(f"[DEBUG] Custom JWT validation error: {str(e)}")
        pass
    
    # Demo fallback
    if user_id:
        user = _DEMO_USERS.get(user_id)
        if user:
            print(f"[DEBUG] Using demo user: {user['email']}")
            return user
    
    print(f"[DEBUG] All validation methods failed!")
    raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_admin_user(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
