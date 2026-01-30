"""
- Intent Service
- THIS TAKES IN THE TRANSCRIPTION OF THE USER'S MESSAGE
- RETURNS A JSON SCHEMA OF THE INTENT
- NOT WORKING ON EVERY INTENT YET
  * CREATE_INVOICE
  * PAYMENT_REMINDER
  * CHECK_STOCK
"""


from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
import os

# Initialize client with key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- SCHEMA DEFINITIONS ---
class InvoiceItem(BaseModel):
    name: str = Field(description="The specific product or service name (in English)")
    quantity: float = Field(description="The numerical quantity")
    price: float = Field(description="The price per unit")


class CreateInvoiceIntent(BaseModel):
    customer_name: str = Field(description="The full name of the customer")
    items: List[InvoiceItem] = Field(description="List of items to be billed")


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


# Update UserIntent to include the new data type
class UserIntent(BaseModel):
    intent_type: str = Field(
        description="CREATE_INVOICE, PAYMENT_REMINDER, CHECK_STOCK,RECORD_PAYMENT or GENERAL"
    )
    confidence: float
    # Now includes CheckStockIntent
    data: Optional[
        Union[
            CreateInvoiceIntent,
            PaymentReminderIntent,
            CheckStockIntent,
            RecordPaymentIntent,
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
            "You are an expert Business Agent for Indian merchants. "
            "You will receive transcripts data "
            "TASK: 1. Extract data into English for the JSON schema. "
            "2. Write the 'response_text' ONLY in the user's native language. "
            "3. If info is missing, ask for it politely in that native language. "
            "4. Use 'Existing Data' to avoid repeating questions."
        )

    async def parse_message(self, text, language):
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": text},
            ],
            response_format=UserIntent,
        )

        return completion.choices[0].message.parsed


intent_service = IntentService()
