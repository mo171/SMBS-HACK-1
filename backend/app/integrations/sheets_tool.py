import os
import gspread
from .base import BaseTool


class GoogleSheetsTool(BaseTool):
    service_name = "google_sheets"

    def __init__(self):
        # We assume you have a service_account.json from Google Cloud Console
        # Or you can use environment variables for the credentials
        try:
            # Use absolute path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "service_account.json")
            self.gc = gspread.service_account(filename=json_path)
        except Exception as e:
            print(f"Sheets Auth Error: {e}")
            self.gc = None

    async def execute(self, task: str, params: dict):
        if not self.gc:
            return {"status": "error", "message": "Google Sheets not authenticated"}

        if task in ["append_row", "append_data"]:
            return await self.append_row(
                spreadsheet_id=params.get("spreadsheet_id"),
                sheet_name=params.get("sheet_name", "Sheet1"),
                data=params.get("row_data") or params.get("data"),
            )

        return {"status": "error", "message": f"Task {task} not found"}

    async def append_row(self, spreadsheet_id, sheet_name, data):
        import json

        try:
            sh = self.gc.open_by_key(spreadsheet_id)
            worksheet = sh.worksheet(sheet_name)

            row = []

            # 1. Handle stringified JSON
            if isinstance(data, str):
                data_trimmed = data.strip()
                if (data_trimmed.startswith("[") and data_trimmed.endswith("]")) or (
                    data_trimmed.startswith("{") and data_trimmed.endswith("}")
                ):
                    try:
                        data = json.loads(data_trimmed)
                        print(f"📊 [GoogleSheetsTool] Parsed JSON data: {data}")
                    except json.JSONDecodeError:
                        print(
                            f"⚠️ [GoogleSheetsTool] Failed to parse data as JSON, using as raw string"
                        )

            # 2. Convert different types to a flat list for append_row
            if isinstance(data, list):
                # If it's a list of lists like [[a, b]], take the first sublist
                if len(data) > 0 and isinstance(data[0], list):
                    row = data[0]
                    print(
                        f"📊 [GoogleSheetsTool] Extracted first row from nested list: {row}"
                    )
                else:
                    row = data
            elif isinstance(data, dict):
                row = list(data.values())
                print(f"📊 [GoogleSheetsTool] Converted dict to row: {row}")
            else:
                # Wrap scalar value in a list
                row = [data]
                print(f"📊 [GoogleSheetsTool] Wrapped scalar data in list: {row}")

            print(f"🚀 [GoogleSheetsTool] Appending row: {row}")
            worksheet.append_row(row)
            return {"status": "success", "message": "Row added to sheets"}
        except Exception as e:
            print(f"❌ [GoogleSheetsTool] Error appending row: {e}")
            return {"status": "error", "message": str(e)}
