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


async def check_recent_logs():
    print("🔍 Fetching recent workflow logs...")
    response = (
        supabase.table("workflow_logs")
        .select("*")
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        print("❌ No logs found.")
        return

    log = response.data[0]
    print(f"\n🆔 Run ID: {log['run_id']}")
    print(f"Status: {log['status']}")
    print(f"Workflow ID: {log['workflow_id']}")

    print("\n📦 Trigger Data:")
    print(json.dumps(log.get("trigger_data"), indent=2))

    print("\n📊 Step Results (Node Context):")
    results = log.get("step_results", {})
    for node_id, result in results.items():
        print(f"\n🔵 Node: {node_id}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(check_recent_logs())
