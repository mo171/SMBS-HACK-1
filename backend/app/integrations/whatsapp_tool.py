import os
import asyncio
from datetime import datetime
from twilio.rest import Client
from .base import BaseTool

# Default values if frontend doesn't provide them
DEFAULT_FALLBACK_PHONE = "9867020608"
DEFAULT_FALLBACK_MESSAGE = "Hi! This is an automated message from your workflow. Some configuration was missing, so this default was sent."
DEFAULT_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"


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
                link=params.get("payment_link"),
            )

        if task == "send_message":
            return await self.send_message(
                to_phone=params.get("phone"), body=params.get("message")
            )

        return {"status": "error", "message": f"Task {task} not found"}

    async def _log_fallback_to_sheets(self, detail: str, original_params: dict):
        """Helper to log fallback events to Google Sheets"""
        try:
            from .sheets_tool import GoogleSheetsTool

            sheets = GoogleSheetsTool()
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "service": "whatsapp",
                "event": "fallback_triggered",
                "detail": detail,
                "original_params": str(original_params),
            }
            # Avoid awaiting here or handle it gracefully to not block the main flow
            # though usually it's better to await in this engine flow.
            await sheets.append_row(
                spreadsheet_id=DEFAULT_SPREADSHEET_ID, sheet_name="Logs", data=log_data
            )
            print(f"📊 [WhatsAppTool] Logged fallback to sheets: {detail}")
        except Exception as e:
            print(f"❌ [WhatsAppTool] Failed to log to sheets: {e}")

    # --- YOUR ORIGINAL LOGIC STARTS HERE ---
    async def send_payment_reminder(
        self, to_phone: str, customer_name: str, amount: str, link: str = None
    ):
        fallback_used = False
        if not to_phone:
            print(
                f"⚠️ [WhatsAppTool] Missing phone number. Using fallback: {DEFAULT_FALLBACK_PHONE}"
            )
            to_phone = DEFAULT_FALLBACK_PHONE
            fallback_used = True

        if not self.from_number:
            return {
                "status": "error",
                "message": "Missing sender phone number (TWILIO_WHATSAPP_NUMBER)",
            }

        # Ensure correct prefix for WhatsApp
        from_num = (
            self.from_number
            if self.from_number.startswith("whatsapp:")
            else f"whatsapp:{self.from_number}"
        )
        to_num = (
            to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        )

        message_body = (
            f"Hi {customer_name or 'there'}! 👋\n\n"
            f"This is a friendly reminder regarding the pending payment of *₹{amount or '0'}*.\n"
        )
        if link:
            message_body += f"\nLink: {link}\n"

        if fallback_used:
            await self._log_fallback_to_sheets(
                "Missing to_phone in payment reminder",
                {"customer_name": customer_name, "amount": amount},
            )

        try:
            message = self.client.messages.create(
                from_=from_num, body=message_body, to=to_num
            )
            return {
                "status": "success",
                "sid": message.sid,
                "fallback_used": fallback_used,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_message(self, to_phone: str, body: str):
        fallback_used = False
        fallback_reason = []

        if not to_phone:
            print(
                f"⚠️ [WhatsAppTool] Missing to_phone. Using fallback: {DEFAULT_FALLBACK_PHONE}"
            )
            to_phone = DEFAULT_FALLBACK_PHONE
            fallback_used = True
            fallback_reason.append("phone_missing")

        if not body:
            print(f"⚠️ [WhatsAppTool] Missing message body. Using fallback.")
            body = DEFAULT_FALLBACK_MESSAGE
            fallback_used = True
            fallback_reason.append("body_missing")

        if not self.from_number:
            return {
                "status": "error",
                "message": "Missing sender phone number (TWILIO_WHATSAPP_NUMBER)",
            }

        # Ensure correct prefix for WhatsApp
        from_num = (
            self.from_number
            if self.from_number.startswith("whatsapp:")
            else f"whatsapp:{self.from_number}"
        )
        to_num = (
            to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        )

        if fallback_used:
            await self._log_fallback_to_sheets(
                f"Fallbacks triggered: {', '.join(fallback_reason)}",
                {"to_phone": to_phone, "original_body": body},
            )

        try:
            message = self.client.messages.create(from_=from_num, body=body, to=to_num)
            return {
                "status": "success",
                "sid": message.sid,
                "fallback_used": fallback_used,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
