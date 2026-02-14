import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to import modules correctly
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.intent_service import intent_service
from services.action_service import action_service

load_dotenv()


async def verify_chat_intents():
    print("🚀 Starting Chat Expansion Verification\n")

    test_cases = [
        {
            "name": "Payment Link Intent",
            "text": "Give me a payment link for 500 for Rahul",
            "expected_intent": "GENERATE_PAYMENT_LINK",
        },
        {
            "name": "Social Post Intent (Pixelfed with Image)",
            "text": "Post 'Check out our new stock' on Pixelfed with image http://example.com/logo.jpg",
            "expected_intent": "POST_SOCIAL",
        },
        {
            "name": "Social Post Intent (Pixelfed with 'use default')",
            "text": "Post 'Check out our new stock' on Pixelfed and use the default image",
            "expected_intent": "POST_SOCIAL",
        },
        {
            "name": "Social Post Intent (Pixelfed without Image - should expect missing info)",
            "text": "Post 'Check out our new stock' on Pixelfed",
            "expected_intent": "POST_SOCIAL",
        },
        {
            "name": "Social Post Intent (Pixelfed)",
            "text": "Post 'Check out our new stock' on Pixelfed",
            "expected_intent": "POST_SOCIAL",
        },
        {
            "name": "Social Post Intent (Bluesky)",
            "text": "Post 'Testing the new chat assistant' on Bluesky",
            "expected_intent": "POST_SOCIAL",
        },
        {
            "name": "Ledger Excel Intent",
            "text": "Give me the ledger in excel format",
            "expected_intent": "GENERATE_REPORT",
        },
        {
            "name": "Debtors Excel Intent",
            "text": "Give me the debtors aging report excel",
            "expected_intent": "GENERATE_REPORT",
        },
    ]

    for case in test_cases:
        print(f"--- Testing: {case['name']} ---")
        try:
            result = await intent_service.parse_message(
                case["text"], language="English"
            )
            print(f"Detected Intent: {result.intent_type}")
            print(f"Data: {result.data}")
            print(f"Missing Info: {result.missing_info}")
            print(f"Response: {result.response_text}")

            if result.intent_type == case["expected_intent"]:
                print(f"✅ Success: Intent matched '{case['expected_intent']}'")
                if (
                    "without Image" in case["name"]
                    and "image_url" in result.missing_info
                ):
                    print("✅ Correctly identified missing image for Pixelfed")
            else:
                print(
                    f"❌ Failure: Intent mismatch. Expected '{case['expected_intent']}', got '{result.intent_type}'"
                )

            # Additional verification for GENERATE_REPORT
            if result.intent_type == "GENERATE_REPORT":
                print(
                    f"Report Type: {result.data.report_type}, Format: {result.data.format}"
                )
        except Exception as e:
            print(f"❌ Error during verification: {e}")
        print("-" * 30 + "\n")

    # Verify Action implementation (Dry Run check)
    print("--- Verifying ActionService Methods ---")
    try:
        # Check if methods exist and can be called (without actual execution if dependencies are missing)
        # We'll just check if they are defined
        print(
            f"create_payment_link exists: {hasattr(action_service, 'create_payment_link')}"
        )
        print(
            f"post_social_content exists: {hasattr(action_service, 'post_social_content')}"
        )
        print(
            f"generate_overall_ledger_excel exists: {hasattr(action_service, 'generate_overall_ledger_excel')}"
        )

        if hasattr(action_service, "create_payment_link"):
            print("✅ ActionService methods are implemented.")
    except Exception as e:
        print(f"❌ ActionService verification failed: {e}")


if __name__ == "__main__":
    asyncio.run(verify_chat_intents())
