from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.database.supabase_client import supabase
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
from app.services.voice_service import voice_service

router = APIRouter()

# --------------------------------------------------
# TEMP TEST USER
# --------------------------------------------------
TEST_USER_ID = "test-user"


@router.post("/chat", response_model=ChatResponse)
def handle_text_chat(payload: ChatRequest):

    user_id = TEST_USER_ID

    try:
        profile_context = {
            "age": payload.age,
            "monthly_income": payload.monthly_income,
            "goal": payload.goal
        }

        rag_result = rag_pipeline.process_query(
            payload.question,
            profile_data=profile_context
        )

        try:
            supabase.table("chat_history").insert({
                "user_id": user_id,
                "question": payload.question,
                "answer": rag_result["answer"],
                "source_type": rag_result["source_type"],
                "source_name": rag_result["source_name"]
            }).execute()

        except Exception as db_error:
            print(f"Chat history save failed: {db_error}")

        return ChatResponse(
            answer=rag_result["answer"],
            source_type=rag_result["source_type"],
            source_name=rag_result["source_name"],
            detected_language=rag_result["detected_language"],
            free_limit_reached=False
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/voice-chat")
async def handle_voice_chat(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    monthly_income: Optional[float] = Form(None),
    goal: Optional[str] = Form(None)
):

    user_id = TEST_USER_ID

    try:
        recognized_text = await voice_service.speech_to_text(file)

        profile_context = {
            "age": age,
            "monthly_income": monthly_income,
            "goal": goal
        }

        rag_result = rag_pipeline.process_query(
            recognized_text,
            profile_data=profile_context
        )

        try:
            supabase.table("chat_history").insert({
                "user_id": user_id,
                "question": recognized_text,
                "answer": rag_result["answer"],
                "source_type": rag_result["source_type"],
                "source_name": rag_result["source_name"]
            }).execute()

        except Exception as db_error:
            print(f"Voice chat history save failed: {db_error}")

        return {
            "recognized_text": recognized_text,
            "answer": rag_result["answer"],
            "source_type": rag_result["source_type"],
            "source_name": rag_result["source_name"],
            "detected_language": rag_result["detected_language"],
            "free_limit_reached": False
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice chat processing failed: {str(e)}"
        )
