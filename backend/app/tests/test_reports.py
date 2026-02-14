import httpx
import asyncio


async def verify_reports():
    base_url = "http://localhost:8000"

    print("--- Verifying Overall Ledger PDF ---")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{base_url}/export/overall-ledger")
            if response.status_code == 200:
                print(
                    f"✅ Success: Overall Ledger PDF received. Content-Type: {response.headers.get('content-type')}"
                )
                print(f"   Size: {len(response.content)} bytes")
            else:
                print(
                    f"❌ Error: Overall Ledger PDF failed with status {response.status_code}"
                )
                print(f"   Detail: {response.text}")
        except Exception as e:
            import traceback

            print(f"❌ Exception verifying ledger: {e}")
            traceback.print_exc()

    print("\n--- Verifying Aging Debtors Excel ---")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{base_url}/export/aging-debtors")
            if response.status_code == 200:
                print(
                    f"✅ Success: Aging Debtors Excel received. Content-Type: {response.headers.get('content-type')}"
                )
                print(f"   Size: {len(response.content)} bytes")
            else:
                print(
                    f"❌ Error: Aging Debtors Excel failed with status {response.status_code}"
                )
                print(f"   Detail: {response.text}")
        except Exception as e:
            import traceback

            print(f"❌ Exception verifying aging debtors: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify_reports())
