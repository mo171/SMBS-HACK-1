import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/app/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


async def check_schema():
    # Fetch one row to see columns
    # Fetch specific product
    try:
        print("\nSearching for 'Pipe'...")
        res = (
            supabase.table("products")
            .select("name, base_price")
            .ilike("name", "%Pipe%")
            .execute()
        )
        if res.data:
            print("Found pipes:", res.data)
        else:
            print("No 'Pipe' found in products table")

        print("\nSearching for 'PVC'...")
        res = (
            supabase.table("products")
            .select("name, base_price")
            .ilike("name", "%PVC%")
            .execute()
        )
        if res.data:
            print("Found PVC:", res.data)
        else:
            print("No 'PVC' found in products table")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_schema())
