import asyncio
from lib.router_logic import find_next_step

# Mock Context Data
context_data = {"sentiment": "negative", "total_spend": 1500, "user_name": "Alice"}

# Mock Routes Configuration
routes = [
    {
        "condition": {
            "variable": "{{sentiment}}",
            "operator": "==",
            "value": "positive",
        },
        "next_node_id": "step_thank_you",
    },
    {
        "condition": {
            "variable": "{{sentiment}}",
            "operator": "==",
            "value": "negative",
        },
        "next_node_id": "step_support_alert",
    },
    {
        "condition": {"variable": "{{total_spend}}", "operator": ">", "value": 1000},
        "next_node_id": "step_vip_promo",
    },
]

print("-" * 60)
print("🧪 Testing Router Logic")
print(f"📊 Context: {context_data}")
print("-" * 60)

# Test 1: Should match 'negative' sentiment
next_step = find_next_step(routes, context_data)
print(f"Test 1 (Sentiment=Negative): Expected 'step_support_alert', Got '{next_step}'")
assert next_step == "step_support_alert"

# Test 2: Change context to positive
context_data["sentiment"] = "positive"
next_step = find_next_step(routes, context_data)
print(f"Test 2 (Sentiment=Positive): Expected 'step_thank_you', Got '{next_step}'")
assert next_step == "step_thank_you"

# Test 3: Change context to neutral (should fall through to VIP check)
context_data["sentiment"] = "neutral"
next_step = find_next_step(routes, context_data)
print(
    f"Test 3 (Sentiment=Neutral, Spend>1000): Expected 'step_vip_promo', Got '{next_step}'"
)
assert next_step == "step_vip_promo"

print("\n✅ All manual routing tests passed!")
