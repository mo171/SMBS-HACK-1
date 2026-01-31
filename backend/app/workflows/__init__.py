# integrations/__init__.py
from .whatsapp_tool import WhatsAppTool
from .google_sheets import GoogleSheetsTool

TOOL_REGISTRY = {
    "whatsapp": WhatsAppTool(),
    "google_sheets": GoogleSheetsTool(),
}
