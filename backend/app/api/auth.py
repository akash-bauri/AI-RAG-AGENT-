from fastapi import APIRouter, HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.security import create_access_token
from app.database.supabase_client import supabase
from app.models.schemas import GoogleLoginRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def google_login(payload: GoogleLoginRequest):
    try:
        # Verify Google Token
        id_info = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        user_id = id_info.get("sub")
        email = id_info.get("email")
        name = id_info.get("name", "User")

        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Google user ID missing."
            )

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Google email missing."
            )

        # Check existing user
        existing_user = (
            supabase.table("users")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        # Create user if first login
        if not existing_user.data:
            user_data = {
                "user_id": user_id,
                "name": name,
                "email": email,
                "language_preference": "English",
                "query_count": 0
            }

            supabase.table("users").insert(user_data).execute()

        # Create JWT
        token_payload = {
            "sub": user_id,
            "email": email
        }

        access_token = create_access_token(
            data=token_payload
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}"
        )
