from fastapi import APIRouter, HTTPException
from app.database.supabase_client import supabase
from typing import List, Dict, Any

router = APIRouter()

@router.get("/question-bank", response_model=List[Dict[str, Any]])
def get_question_bank():
    res = supabase.table("question_bank").select("*").execute()
    return res.data
