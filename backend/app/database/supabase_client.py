from supabase import create_client, Client
from app.core.config import settings

print("========== SUPABASE DEBUG ==========")
print("SUPABASE_URL:", settings.SUPABASE_URL)
print("SUPABASE_KEY EXISTS:", bool(settings.SUPABASE_KEY))
print("====================================")

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)
