import os
import sys
import unittest

# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.variable_resolver import resolve_variables, resolve_recursive


class TestEngineFixes(unittest.TestCase):
    def setUp(self):
        # Sample context with "new" trigger data style (unwrapped)
        self.context = {
            "razorpay_1": {
                "id": "pay_123",
                "amount": 500.0,
                "phone": "+919867020608",
                "customer": "John Doe",
            },
            "gpt_1": {
                "processed_text": "Hello John, your payment of 500.00 is confirmed."
            },
        }

    def test_direct_trigger_access(self):
        """Test that we can access trigger data directly without .data prefix"""
        template = "Phone: {{razorpay_1.phone}}, Amount: ₹{{razorpay_1.amount}}"
        expected = "Phone: +919867020608, Amount: ₹500.00"
        resolved = resolve_variables(template, self.context)
        self.assertEqual(resolved, expected)

    def test_service_aliasing(self):
        """Test that we can access node data via its service name alias"""
        # Context simulated from engine aliasing
        context_with_alias = {
            "RPAY_1": self.context["razorpay_1"],
            "razorpay": self.context["razorpay_1"],
        }
        template = "Alias: {{razorpay.amount}}"
        expected = "Alias: 500.00"
        resolved = resolve_variables(template, context_with_alias)
        self.assertEqual(resolved, expected)

    def test_recursive_resolution_dict(self):
        """Test that variables inside dictionaries are resolved"""
        params = {
            "message": "Hi {{razorpay_1.customer}}!",
            "phone": "{{razorpay_1.phone}}",
            "metadata": {
                "invoice": "INV-{{razorpay_1.id}}",
                "tags": ["urgent", "{{razorpay_1.customer}}"],
            },
        }

        expected = {
            "message": "Hi John Doe!",
            "phone": "+919867020608",
            "metadata": {"invoice": "INV-pay_123", "tags": ["urgent", "John Doe"]},
        }

        resolved = resolve_recursive(params, self.context)
        self.assertEqual(resolved, expected)

    def test_recursive_resolution_list(self):
        """Test that variables inside lists are resolved"""
        params = ["{{razorpay_1.customer}}", "Amount: {{razorpay_1.amount}}"]
        expected = ["John Doe", "Amount: 500.00"]
        resolved = resolve_recursive(params, self.context)
        self.assertEqual(resolved, expected)


if __name__ == "__main__":
    unittest.main()
