import os
from dotenv import load_dotenv

load_dotenv()

def verify_env():
    keys = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY"]
    for key in keys:
        val = os.getenv(key)
        print(f"{key}: {'✅ Found' if val else '❌ Missing'}")

if __name__ == "__main__":
    verify_env()