import os
from supabase import create_client
from dotenv import load_dotenv

# Load env from the backend/app/.env
load_dotenv("c:/movin/programing/3_projects/SMBS-HACK-1/backend/app/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- CUSTOMERS TABLE ---")
try:
    res = supabase.table("customers").select("*").limit(1).execute()
    if res.data:
        print("Columns:", res.data[0].keys())
    else:
        print("No customers found or table empty.")
except Exception as e:
    print(f"Error: {e}")
