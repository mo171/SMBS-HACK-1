import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    exit(1)

supabase: Client = create_client(url, key)


async def test_stock():
    print("--- 1. Listing First 5 Products ---")
    try:
        res = supabase.table("products").select("*").limit(5).execute()
        for idx, item in enumerate(res.data):
            print(f"Item {idx}: {item}")
    except Exception as e:
        print(f"Error listing products: {e}")

    print("\n--- 2. Testing Search for 'PVC pipe' ---")
    try:
        product_name = "PVC pipe"
        res = (
            supabase.table("products")
            .select("name, current_stock")
            .ilike("name", f"%{product_name}%")
            .execute()
        )
        print(f"Query for '{product_name}' result: {res.data}")
    except Exception as e:
        print(f"Error searching products: {e}")

    print("\n--- 3. Testing Search for 'PVC' ---")
    try:
        product_name = "PVC"
        res = (
            supabase.table("products")
            .select("name, current_stock")
            .ilike("name", f"%{product_name}%")
            .execute()
        )
        print(f"Query for '{product_name}' result: {res.data}")
    except Exception as e:
        print(f"Error searching products: {e}")

    print("\n--- 4. Testing Intent Parsing ---")
    try:
        from services.intent_service import intent_service

        text = "How much stock do we have of PVC pipe?"
        print(f"Parsing text: '{text}'")
        result = await intent_service.parse_message(text, language="English")
        print(f"Intent Result: {result.intent_type}")
        print(f"Data Base: {result.data}")
        print(f"Raw Response: {result.response_text}")
    except Exception as e:
        print(f"Error parsing intent: {e}")
    print("\n--- 5. Testing Intent Parsing with TYPO 'pcv pipe' ---")
    try:
        text = "How much stock do we have of pcv pipe?"
        print(f"Parsing text: '{text}'")
        result = await intent_service.parse_message(text, language="English")
        print(f"Intent Result: {result.intent_type}")
        print(f"Data Base: {result.data}")
    except Exception as e:
        print(f"Error parsing typo intent: {e}")

    print("\n--- 6. Testing Action Service Fix ('pcv pipe') ---")
    try:
        from services.action_service import action_service

        stock = await action_service.get_stock("pcv pipe")
        print(f"Stock for 'pcv pipe': {stock}")
    except Exception as e:
        print(f"Error calling action service: {e}")


if __name__ == "__main__":
    asyncio.run(test_stock())
