'''
  - Intent Service
  - THIS TAKES IN THE TRANSCRIPTION OF THE USER'S MESSAGE
  - RETURNS A JSON SCHEMA OF THE INTENT
  - NOT WORKING ON EVERY INTENT YET
    * CREATE_INVOICE
    * PAYMENT_REMINDER
    * CHECK_STOCK
'''
import os
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
import google.generativeai as genai

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

class UserIntent(BaseModel):
    intent_type: str = Field(description="CREATE_INVOICE, PAYMENT_REMINDER, CHECK_STOCK, or GENERAL")
    confidence: float = Field(description="Score between 0-1")
    data: Optional[Union[CreateInvoiceIntent, PaymentReminderIntent]] = None
    missing_info: List[str] = Field(description="Fields like 'price' or 'customer_name' that are still needed")
    response_text: str = Field(description="A natural response in the user's local language asking for missing info or confirming success")

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
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are an expert Business Agent for Indian merchants. "
                "You will receive transcripts in various Indian languages (Marathi, Hindi, etc.). "
                "TASK: 1. Extract data into English for the JSON schema. "
                "2. Write the 'response_text' ONLY in the user's native language. "
                "3. If info is missing, ask for it politely in that native language. "
                "4. Use 'Existing Data' to avoid repeating questions."
            )
        )

    async def parse_message(self, text: str, language: str) -> UserIntent:
        prompt = f"User Language: {language}\nInput: {text}"
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=UserIntent
            )
        )
        
        try:
            return UserIntent.model_validate_json(response.text)
        except Exception as e:
            return UserIntent(intent_type="GENERAL", confidence=0.0, missing_info=["error"], response_text="Error processing request.")

intent_service = IntentService()