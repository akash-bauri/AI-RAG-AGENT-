from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import verify_token
from app.api import auth, chat, questions, user
from app.rag.ingest import build_and_seed_vector_database

# --- Lifespan Event Handler (Replaces deprecated @app.on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ON STARTUP
    print(f"🚀 {settings.PROJECT_NAME} Started Successfully")
    yield
    # You can add shutdown logic here if needed (e.g., closing DB connections)
    print(f"🛑 {settings.PROJECT_NAME} Shutting Down")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

security = HTTPBearer()

# --- CORS Configuration ---
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
)

# --- Dependency Security Layer ---
def verify_admin_privileges(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = verify_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature credentials."
        )

    email = payload.get("email", "")

    if not email.endswith("@appnabank.com"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative role required."
        )

    return payload

# --- Route Inclusions ---
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["AI Hybrid RAG Core Engine"])
app.include_router(questions.router, prefix=settings.API_V1_STR, tags=["Question Bank Module"])
app.include_router(user.router, prefix=settings.API_V1_STR, tags=["User Module"])

# --- System Endpoints ---
@app.get("/")
def root():
    return {
        "message": "Welcome to APPNA BANK AI",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

@app.post("/api/v1/admin/reindex")
def trigger_system_reindexing_routine(
    admin_user=Depends(verify_admin_privileges)
):
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reindexing disabled in production."
        )

    try:
        build_and_seed_vector_database()
        return {
            "status": "success",
            "message": "Vector database synchronized successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}"
        )
