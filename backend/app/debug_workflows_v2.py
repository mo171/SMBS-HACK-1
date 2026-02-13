import asyncio
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def debug_workflows():
    print("🔍 Fetching workflows...")
    response = (
        supabase.table("workflow_blueprints")
        .select("*")
        .order("created_at", desc=True)
        .limit(2)
        .execute()
    )

    if not response.data:
        print("❌ No workflows found.")
        return

    for wf in response.data:
        print(f"\n🆔 ID: {wf['id']}")
        print(f"Name: {wf['name']}")

        nodes = wf.get("nodes")
        print(f"Nodes Type: {type(nodes)}")

        if isinstance(nodes, list):
            print(f"Count: {len(nodes)}")
            for i, node in enumerate(nodes[:2]):
                print(f"  Node {i}:")
                print(f"    ID: {node.get('id')}")
                print(f"    Type: {node.get('type')}")
                print(f"    Position: {node.get('position')}")
                # print(f"    Full: {json.dumps(node)}")
        else:
            print(f"  ⚠️ Nodes is not a list: {nodes}")


if __name__ == "__main__":
    asyncio.run(debug_workflows())
