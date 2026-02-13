import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def debug_workflows():
    print("🔍 Fetching recent workflows...")

    response = (
        supabase.table("workflow_blueprints")
        .select("*")
        .order("created_at", desc=True)
        .limit(3)
        .execute()
    )

    if not response.data:
        print("❌ No workflows found.")
        return

    for wf in response.data:
        print(f"\n🆔 Workflow ID: {wf['id']}")
        print(f"Name: {wf['name']}")
        print(f"Nodes count: {len(wf.get('nodes', []))}")

        nodes = wf.get("nodes", [])
        if nodes:
            print("First 2 Nodes:")
            for i, node in enumerate(nodes[:2]):
                print(
                    f"  [{i}] ID: {node.get('id')} | Type: {node.get('type')} | Pos: {node.get('position')}"
                )
                # Check data keys
                print(f"      Data: {node.get('data', {}).keys()}")
        else:
            print("  ⚠️ Nodes array is empty/null!")


if __name__ == "__main__":
    asyncio.run(debug_workflows())
