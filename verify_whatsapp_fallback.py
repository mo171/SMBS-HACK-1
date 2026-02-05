import asyncio
import os
import sys

# Add the backend/app directory to sys.path to import integrations
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "app"))
)

from integrations.whatsapp_tool import WhatsAppTool


async def test_fallbacks():
    print("🚀 Testing WhatsApp Fallbacks...")
    tool = WhatsAppTool()

    # Test 1: Missing phone
    print("\n--- Test 1: Missing phone ---")
    result1 = await tool.send_message(to_phone=None, body="Hello World")
    print(f"Result 1: {result1}")

    # Test 2: Missing body
    print("\n--- Test 2: Missing body ---")
    result2 = await tool.send_message(to_phone="9867020608", body=None)
    print(f"Result 2: {result2}")

    # Test 3: Missing both
    print("\n--- Test 3: Missing both ---")
    result3 = await tool.send_message(to_phone=None, body=None)
    print(f"Result 3: {result3}")


if __name__ == "__main__":
    asyncio.run(test_fallbacks())
