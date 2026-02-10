import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.shiprocket_tool import ShiprocketTool

import logging

# Load env variables
# Specify the path to .env explicitly
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_shiprocket():
    print(f"DEBUG: SHIPROCKET_EMAIL: {os.getenv('SHIPROCKET_EMAIL')}")
    password = os.getenv("SHIPROCKET_PASSWORD")
    if password:
        print(f"DEBUG: SHIPROCKET_PASSWORD length: {len(password)}")
        print(f"DEBUG: PWD starts with: {password[0]} and ends with: {password[-1]}")
    else:
        print("DEBUG: SHIPROCKET_PASSWORD not found")

    print("🚀 Testing ShiprocketTool...")
    tool = ShiprocketTool()

    # NOTE: You need SHIPROCKET_EMAIL and SHIPROCKET_PASSWORD in .env
    # If not present, this will show the auth failure message correctly.

    print("\n--- Task: create_order ---")
    params = {
        "customer_name": "Test User",
        "address": "456 Main St",
        "city": "Mumbai",
        "pincode": "400001",
        "state": "Maharashtra",
        "phone": "9867020608",
        "amount": 500,
    }

    print(f"Executing with params: {params}")
    result = await tool.execute("create_order", params)
    print(f"Result: {result}")

    if result.get("status") == "success":
        print("\n--- Task: get_tracking ---")
        # Simulating tracking for the created order if possible
        # Or using a dummy awb
        tracking_params = {"awb": "123456789"}
        print(f"Executing with params: {tracking_params}")
        track_result = await tool.execute("get_tracking", tracking_params)
        print(f"Result: {track_result}")


if __name__ == "__main__":
    asyncio.run(test_shiprocket())
