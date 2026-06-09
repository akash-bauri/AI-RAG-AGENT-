import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "APPNA BANK AI"
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"
    
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    GOOGLE_CLIENT_ID: str
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    
    CHROMA_DB_DIR: str = "./chroma_db_storage"

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
