from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token
from app.database.supabase_client import supabase
from app.models.schemas import UserProfileResponse

router = APIRouter()
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    payload = verify_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Session expired."
        )

    return payload.get("sub")


@router.get("/user-profile", response_model=UserProfileResponse)
def get_user_profile(
    user_id: str = Depends(get_current_user_id)
):
    try:
        res = (
            supabase.table("users")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not res.data:
            raise HTTPException(
                status_code=404,
                detail="User not registered."
            )

        return res.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Profile fetch failed: {str(e)}"
        )


@router.get("/usage")
def get_usage_metrics(
    user_id: str = Depends(get_current_user_id)
):
    try:
        res = (
            supabase.table("users")
            .select("query_count")
            .eq("user_id", user_id)
            .execute()
        )

        if not res.data:
            raise HTTPException(
                status_code=404,
                detail="User entry missing."
            )

        count = res.data[0].get("query_count", 0)

        return {
            "current_query_count": count,
            "max_free_limit": 20,
            "remaining_queries": max(0, 20 - count)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Usage fetch failed: {str(e)}"
        )
