from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token
from app.database.supabase_client import supabase
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
from app.services.voice_service import voice_service
from typing import Optional

router = APIRouter()
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access verification failed.")
    return payload["sub"]

def enforce_usage_and_update(user_id: str) -> bool:
    """
    Calls the atomic Postgres RPC to handle limits safely without race conditions.
    """
    try:
        rpc_res = supabase.rpc("increment_user_query_count", {"target_user_id": user_id, "max_limit": 20}).execute()
        if not rpc_res.data:
            raise HTTPException(status_code=500, detail="Could not calculate usage limit markers.")
        
        state = rpc_res.data
        if not state.get("success"):
            raise HTTPException(status_code=404, detail=state.get("error", "Database tracking error."))
            
        return state.get("limit_reached", False)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database state sync error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
def handle_text_chat(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    limit_reached = enforce_usage_and_update(user_id)
    if limit_reached:
        return ChatResponse(
            answer="Your free limit has been reached. Recharge ₹10 to continue.",
            source_type="system",
            source_name="Billing Engine",
            detected_language="en",
            free_limit_reached=True
        )

    profile_context = {"age": payload.age, "monthly_income": payload.monthly_income, "goal": payload.goal}
    rag_result = rag_pipeline.process_query(payload.question, profile_data=profile_context)

    supabase.table("chat_history").insert({
        "user_id": user_id, "question": payload.question, "answer": rag_result["answer"],
        "source_type": rag_result["source_type"], "source_name": rag_result["source_name"]
    }).execute()

    return ChatResponse(
        answer=rag_result["answer"], source_type=rag_result["source_type"],
        source_name=rag_result["source_name"], detected_language=rag_result["detected_language"],
        free_limit_reached=False
    )

@router.post("/voice-chat")
async def handle_voice_chat(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    monthly_income: Optional[float] = Form(None),
    goal: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    limit_reached = enforce_usage_and_update(user_id)
    if limit_reached:
        return {
            "recognized_text": "",
            "answer": "Your free limit has been reached. Recharge ₹10 to continue.",
            "source_type": "system", "source_name": "Billing Engine",
            "detected_language": "en", "free_limit_reached": True
        }

    recognized_text = await voice_service.speech_to_text(file)
    profile_context = {"age": age, "monthly_income": monthly_income, "goal": goal}
    rag_result = rag_pipeline.process_query(recognized_text, profile_data=profile_context)

    supabase.table("chat_history").insert({
        "user_id": user_id, "question": recognized_text, "answer": rag_result["answer"],
        "source_type": rag_result["source_type"], "source_name": rag_result["source_name"]
    }).execute()

    return {
        "recognized_text": recognized_text, "answer": rag_result["answer"],
        "source_type": rag_result["source_type"], "source_name": rag_result["source_name"],
        "detected_language": rag_result["detected_language"], "free_limit_reached": False
    }
