from .whatsapp_tool import WhatsAppTool
from .sheets_tool import GoogleSheetsTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
}
