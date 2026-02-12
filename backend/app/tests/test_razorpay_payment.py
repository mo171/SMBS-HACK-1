"""
Direct Razorpay test - creates ₹1 payment link
"""

import asyncio
import os
import razorpay
from dotenv import load_dotenv

load_dotenv()


async def create_test_payment():
    print("\n" + "=" * 60)
    print("🧪 CREATING ₹1 TEST PAYMENT LINK")
    print("=" * 60)

    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret or "your_razorpay" in key_id:
        print("❌ Razorpay credentials not configured in .env")
        print(f"   Key ID: {key_id}")
        return

    print(f"✓ Using Key ID: {key_id[:15]}...")

    client = razorpay.Client(auth=(key_id, key_secret))

    payment_link_data = {
        "amount": 100,  # ₹1 in paise
        "currency": "INR",
        "description": "Webhook Test - ₹1",
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "contact": "9876543210",
        },
        "notify": {"sms": False, "email": False},
        "reminder_enable": False,
    }

    print("\n📤 Creating payment link...")

    try:
        payment_link = client.payment_link.create(payment_link_data)

        print("\n✅ SUCCESS! Payment link created:")
        print(f"\n🔗 Payment URL: {payment_link['short_url']}")
        print(f"💳 Payment Link ID: {payment_link['id']}")
        print(f"💰 Amount: ₹1")

        print("\n" + "=" * 60)
        print("📋 TESTING STEPS:")
        print("=" * 60)
        print("1. Copy the payment URL above")
        print("2. Open it in your browser")
        print("3. Complete the ₹1 payment")
        print("4. Watch your backend terminal for webhook logs")
        print("5. Check Inngest dev server for workflow execution")

        print("\n� WHAT TO LOOK FOR:")
        print("=" * 60)
        print("✓ Backend logs: 'POST /webhooks/generic/razorpay'")
        print("✓ Inngest logs: 'workflow/run_requested' event")
        print("✓ Workflow execution in Inngest dashboard")

        print("\n💡 Keep your terminals open to see the webhook!")

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid API credentials")
        print("- Network connectivity")
        print("- Razorpay account not activated")


if __name__ == "__main__":
    asyncio.run(create_test_payment())
