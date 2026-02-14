"""
- Intent Service
- THIS TAKES IN THE TRANSCRIPTION OF THE USER'S MESSAGE
- RETURNS A JSON SCHEMA OF THE INTENT
- NOT WORKING ON EVERY INTENT YET
  * CREATE_INVOICE
  * PAYMENT_REMINDER
  * CHECK_STOCK
"""

# imports
import os
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# config
load_dotenv()
# Initialize client with key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- SCHEMA DEFINITIONS ---
"""
 -SCHEMA IS THE CORE OF INTENT SPECIFIER
 -HELPS TO TAKE UN-ORGANIZED DATA AND ORGANIZE IT
"""


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
        description="The amount the customer paid upfront. None if unknown/full payment.",
    )
    discount_applied: Optional[bool] = Field(
        default=False,
        description="True if the user explicitly mentions a discount was given.",
    )
    is_due: Optional[bool] = Field(
        default=False,
        description="True if the user explicitly mentions the remaining amount is due/credit.",
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
        description="The type of report: 'inventory', 'ledger', 'debtors', etc.",
    )
    format: Optional[str] = Field(
        default="excel", description="The format: 'excel' or 'pdf'."
    )


class GeneratePaymentLinkIntent(BaseModel):
    customer_name: str = Field(description="The full name of the customer")
    amount: float = Field(description="The amount for the payment link")
    description: Optional[str] = Field(
        default="Payment Request", description="Purpose of the payment"
    )


class PostSocialIntent(BaseModel):
    platform: str = Field(
        description="The platform: 'pixelfed', 'bluesky', or 'instagram'"
    )
    content: str = Field(description="The text content/caption for the post")
    image_url: Optional[str] = Field(
        default=None, description="URL of the image to include in the post"
    )


# Update UserIntent to include the new data type
# MOST IMPORTANT SCHEMA OF INTENT SPECIFIER
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
            GeneratePaymentLinkIntent,
            PostSocialIntent,
        ]
    ] = None
    missing_info: List[str]
    response_text: str


# --- SESSION MANAGER ---
"""
 -THIS STORES THE CONTEXT FOR FURTHER CHAT FOR A SHORT TIME
 -DONT TRY TO KNOW HOW THIS WORKS
 -THIS WORKS USE IT
"""


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
"""
 -LLM WHICH TAKES UN-ORGANIZE DATA AND GENERATES ORGANIZE DATA ACCORDING TO SCHEMA
 -GIVES COMMAND(INTENT) TO RUN PARTICULAR COMMAND
"""


class IntentService:
    def __init__(self):
        self.system_instruction = (
            "You will receive 'Existing Memory' (current state) and 'New Voice' (new input). "
            "1. REASONING: Use 'internal_thought' to analyze the business state. Compare New Voice with Existing Memory. "
            "2. BE AGENTIC: Identify what is missing to complete the task (Customer and Items/Products are priority). "
            "3. NO PRICE NEEDED: Do NOT ask for individual product prices. The system will index them from the database. "
            "   - CRITICAL: If you have Item Name + Quantity, that is ENOUGH. Do NOT set 'missing_info' for Price or Total Amount. "
            "4. CONTEXT MERGING: Always MERGE New Voice into Existing Memory. NEVER lose existing data (like customer name, items, or payments) unless the user explicitly changes them. "
            "5. DUES/CREDIT LOGIC: If the user says 'Remaining 500 is due' or 'Balance 500', and matches it with a Total, implies Paid = Total - Due. Calculate it! "
            "   - Example: 'Total 900, remaining 500 due' -> Amount Paid = 400. set is_due=True. "
            "6. DISCOUNT LOGIC: If the user says 'Give 100rs discount' or 'Final price is 800 (for a 900 item)', set discount_applied=True. "
            "7. RESPONSE: Speak naturally in the requested language. "
            "8. COMPLETION: When you have Customer and at least one Item (with quantity), you can set 'missing_info' to an empty list. Don't wait for payment info unless it's explicitly missing or unclear."
            "9. REPORTS: If the user wants to download, export, or see a report/excel of their stock, ledger, or debtors, set intent_type to 'GENERATE_REPORT'. "
            "   - If they specify 'ledger', set report_type='ledger'. "
            "   - If they specify 'debtors' or 'aging', set report_type='debtors'. "
            "   - Default format is 'excel' unless 'pdf' is mentioned. "
            "10. CHECK STOCK: If user asks about 'stock', 'inventory', 'how much', or 'quantity' of an item, use 'CHECK_STOCK'. Even if the spelling looks wrong (e.g. 'pcv pipe'), pass it as the product_name. "
            "11. GLOBAL DUES: If the user asks for 'Who owes money', 'list of debtors', or 'pending payments list', set intent_type to 'PAYMENT_REMINDER' and set customer_name to 'ALL'. "
            "12. PAYMENT LINKS: If the user asks to 'generate a link', 'payment link', 'razorpay link', or 'ask for money via link', set intent_type to 'GENERATE_PAYMENT_LINK'. Extract customer_name and amount. "
            "13. SOCIAL POSTING: If the user says 'post this', 'post on pixel', 'post on blusky', or 'upload status', set intent_type to 'POST_SOCIAL'. Extract the platform and content. "
            "   - CRITICAL: Pixelfed is a photo-sharing platform and REQUIRES an image. If the user wants to post on Pixelfed but hasn't provided an image URL or mentioned an image, add 'image_url' to 'missing_info'. "
            "   - TIP: If the user explicitly asks to 'use default', 'use original', or 'default image', set image_url to 'default' and do NOT mark it as missing info."
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

    """
    DEBUGGING: JSON Structure returned by parse_message (UserIntent)
    
    {
      "internal_thought": "Analysis of the user input...",
      "intent_type": "CREATE_INVOICE" | "CHECK_STOCK" | "RECORD_PAYMENT" | "GENERATE_REPORT" | "PAYMENT_REMINDER" | "GENERATE_PAYMENT_LINK" | "POST_SOCIAL" | "GENERAL",
      "confidence": 0.95,
      "data": {
        // Depends on intent_type. Example for CREATE_INVOICE:
        "customer_name": "John Doe",
        "items": [
           { "name": "Product A", "quantity": 2.0, "price": 100.0 }
        ],
        "amount_paid": 500.0
      },
      "missing_info": ["item name"] | [],
      "response_text": "Response to the user"
    }
    """


intent_service = IntentService()
