import gspread
from .base import BaseTool

class GoogleSheetsTool(BaseTool):
    service_name = "google_sheets"

    def __init__(self):
        # We assume you have a service_account.json from Google Cloud Console
        # Or you can use environment variables for the credentials
        try:
            self.gc = gspread.service_account(filename='service_account.json')
        except Exception as e:
            print(f"Sheets Auth Error: {e}")
            self.gc = None

    async def execute(self, task: str, params: dict):
        if not self.gc:
            return {"status": "error", "message": "Google Sheets not authenticated"}

        if task == "append_row":
            return await self.append_row(
                spreadsheet_id=params.get("spreadsheet_id"),
                sheet_name=params.get("sheet_name", "Sheet1"),
                data=params.get("row_data") # Expecting a list or dict
            )
        
        return {"status": "error", "message": f"Task {task} not found"}

    async def append_row(self, spreadsheet_id, sheet_name, data):
        try:
            sh = self.gc.open_by_key(spreadsheet_id)
            worksheet = sh.worksheet(sheet_name)
            
            # If data is a dict, we convert it to a list or handle it as a row
            if isinstance(data, dict):
                row = list(data.values())
            else:
                row = data

            worksheet.append_row(row)
            return {"status": "success", "message": "Row added to sheets"}
        except Exception as e:
            return {"status": "error", "message": str(e)}