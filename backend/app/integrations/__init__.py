from .whatsapp_tool import WhatsAppTool
from .sheets_tool import GoogleSheetsTool
from .razorpay_tool import RazorpayTool
from .timer_tool import TimerTool
from .shiprocket_tool import ShiprocketTool
from .bluesky_tool import BlueskyTool
from .social_logic_tool import SocialLogicTool
from .instagram_tool import InstagramTool
from .pixelfed_tool import PixelfedTool
from tools.database_tool import DatabaseTool
from tools.gpt_tool import GPTTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
    "razorpay": RazorpayTool(),
    "timer": TimerTool(),
    "shiprocket": ShiprocketTool(),
    "bluesky": BlueskyTool(),
    "social_logic": SocialLogicTool(),
    "pixelfed": PixelfedTool(),  # New: Pixelfed integration
    "instagram": InstagramTool(),  # Kept for backward compatibility
    "database": DatabaseTool(),  # New: Database query integration
    "gpt": GPTTool(),  # New: AI/LLM processing
}
