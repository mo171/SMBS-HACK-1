from .whatsapp_tool import WhatsAppTool
from .sheets_tool import GoogleSheetsTool
from .razorpay_tool import RazorpayTool
from .timer_tool import TimerTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
    "razorpay": RazorpayTool(),
    "timer": TimerTool(),
}
