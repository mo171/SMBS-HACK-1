from .whatsapp_tool import WhatsAppTool
from .sheets_tool import GoogleSheetsTool
from .razorpay_tool import RazorpayTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
    "razorpay": RazorpayTool(),
}
