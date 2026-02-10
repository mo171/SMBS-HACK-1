import os
import gspread
import sys
from dotenv import load_dotenv

# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
load_dotenv()


def debug_sheets():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust path if needed
    json_path = os.path.join(
        os.path.dirname(base_dir), "integrations", "service_account.json"
    )

    print(f"Checking credentials at: {json_path}")
    if not os.path.exists(json_path):
        print("❌ service_account.json not found!")
        return

    try:
        gc = gspread.service_account(filename=json_path)
        spreadsheet_id = os.getenv("DEFAULT_SPREADSHEET_ID")

        if not spreadsheet_id:
            print("❌ DEFAULT_SPREADSHEET_ID not set in .env")
            return

        print(f"Opening spreadsheet: {spreadsheet_id}")
        sh = gc.open_by_key(spreadsheet_id)

        print(f"✅ Success! Spreadsheet title: {sh.title}")
        print("Available worksheets:")
        worksheets = sh.worksheets()
        for ws in worksheets:
            print(f" - {ws.title}")

        found_logs = any(ws.title == "Logs" for ws in worksheets)
        if not found_logs:
            print("\n⚠️  The worksheet 'Logs' was NOT found.")
            print(
                "Please create a sheet named 'Logs' (case sensitive) in your spreadsheet."
            )

    except gspread.exceptions.SpreadsheetNotFound:
        print(
            "❌ Spreadsheet not found. Double check your ID and ensure the spreadsheet is shared with the service account email."
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_sheets()
