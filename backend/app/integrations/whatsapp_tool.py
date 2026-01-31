import os
from twilio.rest import Client
from .base import BaseTool

class WhatsAppTool(BaseTool):
    service_name = "whatsapp"

    def __init__(self):
        # Keep your existing initialization!
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.client = Client(self.account_sid, self.auth_token)

    async def execute(self, task: str, params: dict):
        """This is the 'Adapter' that lets the Engine talk to Twilio"""
        if task == "send_payment_reminder":
            return await self.send_payment_reminder(
                to_phone=params.get("phone"),
                customer_name=params.get("name"),
                amount=params.get("amount"),
                link=params.get("payment_link")
            )
        
        if task == "send_message":
            return await self.send_message(
                to_phone=params.get("phone"),
                body=params.get("message")
            )

        return {"status": "error", "message": f"Task {task} not found"}

    # --- YOUR ORIGINAL LOGIC STARTS HERE ---
    async def send_payment_reminder(self, to_phone: str, customer_name: str, amount: str, link: str = None):
        message_body = (
            f"Hi {customer_name}! 👋\n\n"
            f"This is a friendly reminder regarding the pending payment of *₹{amount}*.\n"
        )
        if link: message_body += f"\nLink: {link}\n"
        
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                body=message_body,
                to=f"whatsapp:{to_phone}"
            )
            return {"status": "success", "sid": message.sid}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_message(self, to_phone: str, body: str):
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                body=body,
                to=f"whatsapp:{to_phone}"
            )
            return {"status": "success", "sid": message.sid}
        except Exception as e:
            return {"status": "error", "message": str(e)}