import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to sys.path to allow imports from integrations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.whatsapp_tool import WhatsAppTool
from integrations.sheets_tool import GoogleSheetsTool
from integrations.timer_tool import TimerTool
from integrations.razorpay_tool import RazorpayTool

# Load environment variables
load_dotenv()


async def test_whatsapp():
    print("\n--- Testing WhatsAppTool ---")
    tool = WhatsAppTool()

    # Simulate dynamic values that would come from a workflow payload
    dynamic_payload = {
        "customer_name": "Test User",
        "order_amount": "500",
        "phone": os.getenv("DEFAULT_WHATSAPP_PHONE", "9867020608"),
    }

    params = {
        "phone": dynamic_payload["phone"],
        "message": f"Hello {dynamic_payload['customer_name']}, this is a test from Bharat Biz-Agent! Amount: ₹{dynamic_payload['order_amount']}",
    }

    print(f"Executing 'send_message' with params: {params}")
    result = await tool.execute("send_message", params)
    print(f"Result: {result}")


async def test_sheets():
    print("\n--- Testing GoogleSheetsTool ---")
    tool = GoogleSheetsTool()

    spreadsheet_id = os.getenv("DEFAULT_SPREADSHEET_ID")
    if not spreadsheet_id:
        print("⚠️ Skipping Sheets test: DEFAULT_SPREADSHEET_ID not set in .env")
        return

    # Simulate structured data representing a workflow event
    log_data = {
        "timestamp": "2026-02-10T20:30:00",
        "event": "automation_test",
        "user": "Developer",
        "status": "Success",
    }

    params = {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": "Sheet1",
        "data": log_data,
    }

    print(f"Executing 'append_row' with params: {params}")
    result = await tool.execute("append_row", params)
    print(f"Result: {result}")


async def test_timer():
    print("\n--- Testing TimerTool ---")
    tool = TimerTool()

    params = {"duration": 3}
    print(f"Executing 'execute' with params: {params}")
    result = await tool.execute(
        "run", params
    )  # Note: TimerTool execute doesn't switch on task, it just runs
    print(f"Result: {result}")


async def test_razorpay():
    print("\n--- Testing RazorpayTool ---")
    tool = RazorpayTool()

    params = {
        "amount": 100,
        "currency": "INR",
        "customer_name": "Test User",
        "description": "Integration Test Payment",
    }

    print(f"Executing 'create_payment_link' with params: {params}")
    result = await tool.execute("create_payment_link", params)
    print(f"Result: {result}")


async def run_all_tests():
    print("🚀 Starting Integration Tests...")

    # run timer first as it's fastest/simplest
    # await test_timer()

    # run razorpay
    # await test_razorpay()

    # run sheets
    await test_sheets()

    # run whatsapp
    # await test_whatsapp()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
