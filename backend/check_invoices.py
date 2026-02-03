import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv("c:/movin/programing/3_projects/SMBS-HACK-1/backend/app/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- INVOICES TABLE ---")
try:
    res = supabase.table("invoices").select("*").limit(1).execute()
    if res.data:
        print("Columns:", res.data[0].keys())
    else:
        print("No invoices found or table empty.")
except Exception as e:
    print(f"Error: {e}")
