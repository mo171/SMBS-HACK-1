"""
- Intent Service
- THIS TAKES IN THE TRANSCRIPTION OF THE USER'S MESSAGE
- RETURNS A JSON SCHEMA OF THE INTENT
- NOT WORKING ON EVERY INTENT YET
  * CREATE_INVOICE
  * PAYMENT_REMINDER
  * CHECK_STOCK
"""

import os
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize client with key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- SCHEMA DEFINITIONS ---
class InvoiceItem(BaseModel):
    name: str = Field(description="The specific product or service name (in English)")
    quantity: float = Field(default=1.0, description="The numerical quantity")
    price: Optional[float] = Field(
        default=None, description="The price per unit. Leave None if not mentioned."
    )


class CreateInvoiceIntent(BaseModel):
    customer_name: str = Field(description="The full name of the customer")
    items: List[InvoiceItem] = Field(
        description="List of items to be billed. Ensure names are detailed (e.g., 'Paint Bucket (Red)')"
    )
    # Changed default to None to distinguish between 'paid 0' and 'unknown'
    amount_paid: Optional[float] = Field(
        default=None,
        description="The amount the customer paid upfront. None if unknown.",
    )


class PaymentReminderIntent(BaseModel):
    customer_name: str
    amount_due: Optional[float] = None


class CheckStockIntent(BaseModel):
    product_name: str = Field(
        description="The name of the item to look up in inventory"
    )


class RecordPaymentIntent(BaseModel):
    customer_name: str
    amount: float
    payment_mode: Optional[str] = "Cash"


class GenerateReportIntent(BaseModel):
    report_type: str = Field(
        default="inventory",
        description="The type of report: 'inventory', 'sales', etc.",
    )


# Update UserIntent to include the new data type
class UserIntent(BaseModel):
    internal_thought: str = Field(
        description="Your step-by-step reasoning about the business task. Analyze what you know and what is missing specifically (e.g., 'I have the customer name and payment, but No items yet')."
    )
    intent_type: str = Field(
        description="CREATE_INVOICE, PAYMENT_REMINDER, CHECK_STOCK, RECORD_PAYMENT, GENERATE_REPORT, or GENERAL"
    )
    confidence: float
    data: Optional[
        Union[
            CreateInvoiceIntent,
            PaymentReminderIntent,
            CheckStockIntent,
            RecordPaymentIntent,
            GenerateReportIntent,
        ]
    ] = None
    missing_info: List[str]
    response_text: str


# --- SESSION MANAGER ---
class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, UserIntent] = {}

    def save_session(self, session_id: str, intent: UserIntent):
        self._sessions[session_id] = intent

    def get_session(self, session_id: str) -> Optional[UserIntent]:
        return self._sessions.get(session_id)

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


session_manager = SessionManager()


# --- SERVICE LOGIC ---
class IntentService:
    def __init__(self):
        self.system_instruction = (
            "You are a sophisticated AI Business Agent for Indian merchants. Your goal is to manage the shop's ledger and inventory through natural conversation. "
            "You will receive 'Existing Memory' (current state) and 'New Voice' (new input). "
            "1. REASONING: Use 'internal_thought' to analyze the business state. Compare New Voice with Existing Memory. "
            "2. BE AGENTIC: Identify what is missing to complete the task (Customer, Items, or Total Amount). "
            "3. NO PRICE NEEDED: Do NOT ask for individual product prices if the user has provided a total amount or if they just want to record what was sold. "
            "4. CONTEXT MERGING: Always MERGE New Voice into Existing Memory. NEVER lose existing data (like customer name, items, or payments) unless the user explicitly changes them. If New Voice is just '1000 rupees' and Existing Memory has 'Rajesh' and 'Paint', your new state should have all three. "
            "5. RESPONSE: Speak naturally in the requested language. "
            "6. COMPLETION: Only when you have at least Customer, Product Name, and an Amount Paid should you set 'missing_info' to an empty list."
            "7. REPORTS: If the user wants to download, export, or see a report/excel of their stock or products, "
            "set intent_type to 'GENERATE_REPORT'."
        )

    async def parse_message(self, text, language):
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"{self.system_instruction}\n\nIMPORTANT: Speak ONLY in English or Hinglish.",
                },
                {"role": "user", "content": text},
            ],
            response_format=UserIntent,
        )

        return completion.choices[0].message.parsed


intent_service = IntentService()
