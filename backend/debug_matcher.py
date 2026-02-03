import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/app/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


async def test_matcher(input_name):
    print(f"\n--- Testing Input: '{input_name}' ---")

    # 1. Try exact/partial match
    print("1. Trying ilike %name%...")
    res = (
        supabase.table("products")
        .select("name, base_price")
        .ilike("name", f"%{input_name}%")
        .execute()
    )
    if res.data:
        print("MATCHED METHOD 1:", res.data[0])
        return

    # 2. Fallback fuzzy (words)
    print("2. Trying fuzzy split...")
    words = input_name.split()
    if len(words) > 1:
        or_filter = ",".join([f"name.ilike.%{word}%" for word in words])
        print(f"Filter: {or_filter}")
        res = (
            supabase.table("products")
            .select("name, base_price")
            .or_(or_filter)
            .execute()
        )
        if res.data:
            print("MATCHED METHOD 2:", res.data[0])
        else:
            print("NO MATCH (Method 2)")
    else:
        print("Skipping Method 2 (Single Word)")


if __name__ == "__main__":
    # Test cases likely to fail
    asyncio.run(test_matcher("PVC Pipe"))
    asyncio.run(test_matcher("pvc pipes"))
    asyncio.run(test_matcher("PVC pipe"))
    asyncio.run(test_matcher("3 PVC Pipes"))
