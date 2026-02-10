import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.bluesky_tool import BlueskyTool

# Specify the path to .env explicitly
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(dotenv_path=env_path)


async def test_bluesky():
    print("🚀 Testing BlueskyTool...")
    tool = BlueskyTool()

    handle = os.getenv("BLUESKY_HANDLE")
    app_pwd = os.getenv("BLUESKY_APP_PASSWORD")

    if not handle or not app_pwd:
        print("⚠️ BLUESKY_HANDLE or BLUESKY_APP_PASSWORD not found in .env")
        print("Please add them to test the live connection.")
        return

    print(f"DEBUG: Using handle: {handle}")

    # Test Posting
    print("\n--- Task: post_content ---")
    post_params = {
        "text": "Hello from Bharat Biz-Agent! Testing social media integration. 🚀 #AI #Automation"
    }
    print(f"Executing with params: {post_params}")
    result = await tool.execute("post_content", post_params)
    print(f"Result: {result}")

    # Test Notifications
    print("\n--- Task: read_notifications ---")
    notif_params = {}
    print(f"Executing with params: {notif_params}")
    notif_result = await tool.execute("read_notifications", notif_params)
    print(f"Result: {notif_result}")


if __name__ == "__main__":
    asyncio.run(test_bluesky())
