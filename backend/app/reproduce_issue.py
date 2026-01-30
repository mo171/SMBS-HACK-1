from services.intent_service import UserIntent, PaymentReminderIntent
import json

# Simulate what Gemini might return
json_response = """
{
    "intent_type": "PAYMENT_REMINDER",
    "confidence": 0.9,
    "response_text": "Calculating...",
    "data": {
        "customer_name": "Rajesh"
    },
    "missing_info": []
}
"""

try:
    print("Attempting to parse JSON...")
    intent = UserIntent.model_validate_json(json_response)
    print(f"Parsed Successfully: {intent}")
    print(f"Data Type: {type(intent.data)}")

    if intent.data:
        print(f"Customer Name: {getattr(intent.data, 'customer_name', 'MISSING')}")
    else:
        print("Data is None!")

except Exception as e:
    print(f"Validation Failed: {e}")
