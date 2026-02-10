from .whatsapp_tool import WhatsAppTool
from .sheets_tool import GoogleSheetsTool
from .razorpay_tool import RazorpayTool
from .timer_tool import TimerTool
from .shiprocket_tool import ShiprocketTool
from .bluesky_tool import BlueskyTool
from .social_logic_tool import SocialLogicTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
    "razorpay": RazorpayTool(),
    "timer": TimerTool(),
    "shiprocket": ShiprocketTool(),
    "bluesky": BlueskyTool(),
    "social_logic": SocialLogicTool(),
}
