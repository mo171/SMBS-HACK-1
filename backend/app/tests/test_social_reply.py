import asyncio
import os
import sys
from dotenv import load_dotenv

from app.integrations.social_logic_tool import SocialLogicTool

# LOAD ENV
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(dotenv_path=env_path)


async def test_social_logic():
    print("🚀 Testing SocialLogicTool (AI Auto-Reply Brain)...")
    tool = SocialLogicTool()

    # 1. Test "Stock Check" Reply
    print("\n--- Task: draft_reply (Context: Stock) ---")
    stock_params = {
        "mention": {
            "platform": "bluesky",
            "author": "customer_joe",
            "text": "Do you have any Red Paint in stock?",
            "uri": "at://abc/123",
            "cid": "cid-789",
        },
        "context_type": "stock",
        "product_name": "Red Paint",
    }
    print(f"Executing with params: {stock_params}")
    result = await tool.execute("draft_reply", stock_params)
    print(f"Result Thought: {result['data']['thought']}")
    print(f"Suggested Reply: {result['data']['suggested_text']}")
    print(f"Reply To URI: {result['data']['reply_to']['parent']['uri']}")

    # 2. Test "Ledger" Reply
    print("\n--- Task: draft_reply (Context: Ledger) ---")
    ledger_params = {
        "mention": {
            "platform": "bluesky",
            "author": "yash_the_debtor",
            "text": "How much do I still owe you for the last order?",
            "uri": "at://def/456",
            "cid": "cid-012",
        },
        "context_type": "ledger",
        "customer_name": "Yash",
    }
    print(f"Executing with params: {ledger_params}")
    result = await tool.execute("draft_reply", ledger_params)
    print(f"Result Thought: {result['data']['thought']}")
    print(f"Suggested Reply: {result['data']['suggested_text']}")


if __name__ == "__main__":
    asyncio.run(test_social_logic())
