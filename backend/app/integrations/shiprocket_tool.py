import httpx
import os
import logging
from typing import Any, Dict
from .base import BaseTool

logger = logging.getLogger(__name__)


class ShiprocketTool(BaseTool):
    def __init__(self):
        self.base_url = "https://apiv2.shiprocket.in/v1/external"
        self.email = os.getenv("SHIPROCKET_EMAIL")
        self.password = os.getenv("SHIPROCKET_PASSWORD")
        self.token = os.getenv("SHIPROCKET_JWT_TOKEN")

    @property
    def service_name(self) -> str:
        return "shiprocket"

    async def _authenticate(self):
        """Get JWT token from Shiprocket. Prioritizes static token from env."""
        if self.token:
            return True

        if not self.email or not self.password:
            logger.warning("Shiprocket credentials (email/pass) missing in environment")
            return False

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"email": self.email, "password": self.password},
                )
                if resp.status_code == 200:
                    self.token = resp.json().get("token")
                    return True
                else:
                    logger.error(f"Shiprocket auth failed: {resp.text}")
        except Exception as e:
            logger.error(f"Shiprocket auth exception: {e}")
        return False

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Handle auth first
        if not self.token:
            success = await self._authenticate()
            if not success:
                return {
                    "status": "error",
                    "message": "Shiprocket authentication failed. Check credentials.",
                }

        # Map tasks
        if task == "create_order":
            return await self.create_order(params)
        elif task == "get_tracking":
            return await self.get_tracking(params)

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def create_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an adhoc order in Shiprocket"""
        # Build the Shiprocket Order Payload
        # We use smart defaults but allow overrides via params
        order_payload = {
            "order_id": params.get("order_id", f"ORD-{os.urandom(2).hex().upper()}"),
            "order_date": params.get("order_date", "2026-02-10"),  # ISO format
            "pickup_location": params.get("pickup_location", "Primary"),
            "billing_customer_name": params.get("customer_name", "N/A"),
            "billing_last_name": "",
            "billing_address": params.get("address", "N/A"),
            "billing_city": params.get("city", "N/A"),
            "billing_pincode": params.get("pincode", "110001"),
            "billing_state": params.get("state", "Delhi"),
            "billing_country": "India",
            "billing_email": params.get("email", "customer@example.com"),
            "billing_phone": params.get("phone", "9999999999"),
            "shipping_is_billing": True,
            "order_items": params.get(
                "items",
                [
                    {
                        "name": "General Merchandize",
                        "sku": "SKU-001",
                        "units": 1,
                        "selling_price": params.get("amount", 0),
                    }
                ],
            ),
            "payment_method": "Prepaid",
            "sub_total": params.get("amount", 0),
            "length": 10,
            "breadth": 10,
            "height": 10,
            "weight": 0.5,
        }

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/orders/create/adhoc",
                    json=order_payload,
                    headers=headers,
                )
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    return {
                        "status": "success",
                        "shiprocket_order_id": data.get("order_id"),
                        "shipment_id": data.get("shipment_id"),
                        "status_text": data.get("status"),
                    }
                else:
                    return {"status": "error", "message": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_tracking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track order using AWB number"""
        awb = params.get("awb")
        if not awb:
            return {"status": "error", "message": "AWB number missing"}

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/courier/track/awb/{awb}", headers=headers
                )
                return {"status": "success", "data": resp.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}
