import os
import sys

# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.variable_resolver import resolve_variables


def test_resolution():
    print("🧪 Starting Variable Resolution Simulation...\n")

    # 1. MOCK TRIGGER PAYLOAD (What comes from a Webhook/Frontend)
    trigger_payload = {
        "customer_name": "Yash",
        "customer_phone": "+919867020608",
        "order_id": "BIZ-12345",
        "amount": 999.50,
    }

    # 2. MOCK PREVIOUS NODE RESULTS (What Razorpay node might return)
    node_results = {
        "razorpay_1": {
            "status": "success",
            "payment_url": "https://rzp.io/l/test_link",
            "amount": "999.50",
        }
    }

    # 3. CONTEXT (This is how the Engine builds the context)
    context_data = {"trigger_data": trigger_payload, **node_results}

    # 4. TEST CASES (Mapping dynamic values)
    test_cases = [
        {
            "name": "WhatsApp Message Resolution",
            "template": "Hi {{trigger_data.customer_name}}! Pay here: {{razorpay_1.payment_url}}",
            "expected": "Hi Yash! Pay here: https://rzp.io/l/test_link",
        },
        {
            "name": "WhatsApp Phone Resolution",
            "template": "{{trigger_data.customer_phone}}",
            "expected": "+919867020608",
        },
        {
            "name": "Google Sheets Data Resolution",
            "template": "Order {{trigger_data.order_id}} was paid: ₹{{razorpay_1.amount}}",
            "expected": "Order BIZ-12345 was paid: ₹999.50",
        },
    ]

    # 5. EXECUTION
    all_passed = True
    for test in test_cases:
        resolved = resolve_variables(test["template"], context_data)
        print(f"Node: {test['name']}")
        print(f"  Template: {test['template']}")
        print(f"  Resolved: {resolved}")

        if resolved == test["expected"]:
            print("  ✅ Match!")
        else:
            print(f"  ❌ FAILED! Expected: {test['expected']}")
            all_passed = False
        print("-" * 30)

    if all_passed:
        print(
            "\n🏆 Logic Verified: The backend correctly resolves dynamic values from both Triggers and Nodes!"
        )
    else:
        print("\n⚠️  Logic Error: Some variables did not resolve as expected.")


if __name__ == "__main__":
    test_resolution()
