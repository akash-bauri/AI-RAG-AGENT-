from supabase import create_client, Client
from app.core.config import settings

print("========== SUPABASE DEBUG ==========")
print("SUPABASE_URL =", repr(settings.SUPABASE_URL))
print("SUPABASE_KEY EXISTS =", bool(settings.SUPABASE_KEY))
print("====================================")

if not settings.SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing")

if not settings.SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing")

try:
    supabase: Client = create_client(
        settings.SUPABASE_URL.strip(),
        settings.SUPABASE_KEY.strip()
    )

    print("✅ Supabase Connected Successfully")

except Exception as e:
    print(f"❌ Supabase Connection Failed: {str(e)}")
    raise
