import asyncio
import os
import sys
import json

# Add the backend/app directory to sys.path to import integrations
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "app"))
)

from integrations.sheets_tool import GoogleSheetsTool


async def test_sheets_parsing():
    print("🚀 Testing Google Sheets Data Parsing...")
    tool = GoogleSheetsTool()

    # Mocking self.gc and other methods to avoid real API calls for logic testing
    class MockWorksheet:
        def append_row(self, row):
            print(f"✅ append_row called with: {row}")

    class MockSpreadsheet:
        def worksheet(self, name):
            return MockWorksheet()

    class MockGC:
        def open_by_key(self, key):
            return MockSpreadsheet()

    tool.gc = MockGC()

    spreadsheet_id = "test_id"
    sheet_name = "Sheet1"

    # Test 1: JSON String (Nested List)
    print("\n--- Test 1: JSON String (Nested List) ---")
    data1 = '[["Test Customer", "test@example.com", "TEST12345"]]'
    await tool.append_row(spreadsheet_id, sheet_name, data1)

    # Test 2: JSON String (Flat List)
    print("\n--- Test 2: JSON String (Flat List) ---")
    data2 = '["Single", "Row", "Data"]'
    await tool.append_row(spreadsheet_id, sheet_name, data2)

    # Test 3: Raw List
    print("\n--- Test 3: Raw List ---")
    data3 = ["Raw", "List", "Data"]
    await tool.append_row(spreadsheet_id, sheet_name, data3)

    # Test 4: Dict
    print("\n--- Test 4: Dict ---")
    data4 = {"name": "Test", "email": "test@test.com"}
    await tool.append_row(spreadsheet_id, sheet_name, data4)


if __name__ == "__main__":
    asyncio.run(test_sheets_parsing())
