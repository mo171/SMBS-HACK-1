import razorpay
import os
import time
from typing import Any, Dict
from .base import BaseTool


class RazorpayTool(BaseTool):
    def __init__(self):
        # Initialize Razorpay client
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not key_id or not key_secret:
            print("⚠️ [RazorpayTool] Warning: Razorpay credentials not found in environment")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(key_id, key_secret))
            print("✅ [RazorpayTool] Razorpay client initialized successfully")

    @property
    def service_name(self) -> str:
        return "razorpay"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n🔵 [RazorpayTool] Executing task: {task}")
        print(f"📊 [RazorpayTool] Parameters: {params}")

        if not self.client:
            error_msg = "Razorpay client not initialized. Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET"
            print(f"❌ [RazorpayTool] {error_msg}")
            return {"status": "error", "message": error_msg}

        try:
            if task == "create_payment_link":
                return await self._create_payment_link(params)
            elif task == "create_order":
                return await self._create_order(params)
            elif task == "capture_payment":
                return await self._capture_payment(params)
            else:
                error_msg = f"Unknown task: {task}"
                print(f"❌ [RazorpayTool] {error_msg}")
                return {"status": "error", "message": error_msg}

        except Exception as e:
            error_msg = f"Razorpay operation failed: {str(e)}"
            print(f"❌ [RazorpayTool] {error_msg}")
            return {"status": "error", "message": error_msg}

    async def _create_payment_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Razorpay payment link"""
        print("💳 [RazorpayTool] Creating payment link")
        
        # Convert amount to paise (Razorpay uses smallest currency unit)
        amount_paise = int(float(params.get("amount", 0))) * 100
        
        payment_link_data = {
            "amount": amount_paise,
            "currency": params.get("currency", "INR"),
            "description": params.get("description", "Payment Request"),
            "customer": {
                "name": params.get("customer_name", "Customer"),
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "callback_url": params.get("callback_url", ""),
            "callback_method": "get"
        }
        
        # Add optional customer details
        if params.get("customer_email"):
            payment_link_data["customer"]["email"] = params["customer_email"]
        if params.get("customer_phone"):
            payment_link_data["customer"]["contact"] = params["customer_phone"]
        
        print(f"📤 [RazorpayTool] Payment link data: {payment_link_data}")
        
        payment_link = self.client.payment_link.create(payment_link_data)
        
        print(f"✅ [RazorpayTool] Payment link created: {payment_link['id']}")
        print(f"🔗 [RazorpayTool] Payment URL: {payment_link['short_url']}")
        
        return {
            "status": "success",
            "payment_link_id": payment_link["id"],
            "payment_url": payment_link["short_url"],
            "amount": params.get("amount"),
            "currency": payment_link["currency"],
            "customer_name": params.get("customer_name"),
            "description": payment_link["description"]
        }

    async def _create_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Razorpay order"""
        print("📋 [RazorpayTool] Creating order")
        
        amount_paise = int(float(params.get("amount", 0))) * 100
        
        order_data = {
            "amount": amount_paise,
            "currency": params.get("currency", "INR"),
            "receipt": params.get("receipt", f"order_{int(time.time())}"),
            "payment_capture": params.get("payment_capture", 1)
        }
        
        order = self.client.order.create(order_data)
        
        print(f"✅ [RazorpayTool] Order created: {order['id']}")
        
        return {
            "status": "success",
            "order_id": order["id"],
            "amount": params.get("amount"),
            "currency": order["currency"],
            "receipt": order["receipt"]
        }

    async def _capture_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a payment"""
        print("💰 [RazorpayTool] Capturing payment")
        
        payment_id = params.get("payment_id")
        amount_paise = int(float(params.get("amount", 0))) * 100
        
        if not payment_id:
            return {"status": "error", "message": "payment_id is required"}
        
        capture_data = {"amount": amount_paise}
        payment = self.client.payment.capture(payment_id, capture_data)
        
        print(f"✅ [RazorpayTool] Payment captured: {payment['id']}")
        
        return {
            "status": "success",
            "payment_id": payment["id"],
            "amount": params.get("amount"),
            "status": payment["status"]
        }