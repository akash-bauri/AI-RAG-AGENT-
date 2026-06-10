from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.security import verify_token
from app.api import auth, chat, questions, user
from app.rag.ingest import build_and_seed_vector_database

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", docs_url="/docs")
security = HTTPBearer()

# Strict security origin mappings
ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "http://localhost:5173", 
    "http://localhost",      
]

# --- ⭐ Improvement: Hardened CORS Methods & Headers ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
)

def verify_admin_privileges(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Protects administration paths from unauthenticated internet requests.
    """
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature credentials.")
    
    email = payload.get("email", "")
    if not email.endswith("@appnabank.com"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Administrative role permission verification required."
        )
        
    # --- ⚠️ Fixed Issue #1: Added Missing Return ---
    return payload

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["AI Hybrid RAG Core Engine"])
app.include_router(questions.router, prefix=settings.API_V1_STR, tags=["Question Bank Module"])
app.include_router(user.router, prefix=settings.API_V1_STR, tags=["User Account Profiles & Ledger Usage Trackers"])

@app.get("/health", tags=["System Diagnostics"])
def health_check():
    return {"status": "healthy", "system": settings.PROJECT_NAME}

@app.post("/api/v1/admin/reindex", tags=["Administrative Control Panel"])
def trigger_system_reindexing_routine(admin_user=Depends(verify_admin_privileges)):
    # --- ⚠️ Fixed Issue #2: Graceful Production Block ---
    if settings.ENVIRONMENT == "production":
        return {
            "status": "blocked",
            "message": "Manual reindex or automated migration script required in production."
        }

    try:
        build_and_seed_vector_database()
        return {"status": "success", "message": "Vector database collections synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing pipeline failed: {str(e)}")
