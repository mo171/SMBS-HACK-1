import asyncio
import os
import sys
import pandas as pd
from io import BytesIO
from unittest.mock import MagicMock, patch

# Add the backend directory to sys.path
backend_path = r"C:\movin\programing\3_projects\SMBS-HACK-1\backend\app"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from services.action_service import action_service


async def test_dynamic_excel():
    print("Testing Dynamic Excel Logic...")

    # 1. Test Inventory Export (Drop Price if all zero)
    mock_products = [
        {"id": 1, "name": "Prod A", "base_price": 0, "current_stock": 10},
        {"id": 2, "name": "Prod B", "base_price": 0, "current_stock": 5},
    ]

    with patch.object(action_service.supabase, "table") as mock_table:
        mock_table.return_value.select.return_value.execute.return_value.data = (
            mock_products
        )

        print(
            "Running generate_inventory_excel (expecting base_price to be dropped)..."
        )
        excel_bytes = await action_service.generate_inventory_excel()
        df = pd.read_excel(BytesIO(excel_bytes))
        print(f"Inventory Columns: {df.columns.tolist()}")
        if "base_price" not in df.columns:
            print("SUCCESS: base_price column dropped as expected.")
        else:
            print("FAILURE: base_price column still present.")

    # 2. Test Invoice Excel Export
    mock_inv = {
        "id": "test-inv-id",
        "customer_id": "cust-id",
        "total_amount": 1000.0,
        "created_at": "2023-10-27T10:00:00Z",
        "customers": {"full_name": "Test Customer"},
    }

    mock_items = [
        {"description": "Product A", "quantity": 2, "unit_price": 500},
    ]

    with patch.object(action_service.supabase, "table") as mock_table:

        def side_effect(table_name):
            m = MagicMock()
            if table_name == "invoices":
                m.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_inv
            elif table_name == "invoice_items":
                m.select.return_value.eq.return_value.execute.return_value.data = (
                    mock_items
                )
            elif table_name == "payments":
                m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            return m

        mock_table.side_effect = side_effect

        print("Running generate_invoice_excel...")
        excel_bytes = await action_service.generate_invoice_excel("test-inv-id")
        print(f"Generated Invoice Excel size: {len(excel_bytes)} bytes")
        df = pd.read_excel(BytesIO(excel_bytes), skiprows=4)
        print(f"Invoice Table Columns: {df.columns.tolist()}")
        if "Unit Price" in df.columns:
            print("SUCCESS: Unit Price column present.")
        else:
            print("FAILURE: Unit Price column missing.")

    print("DONE: Dynamic Excel logic verified.")


if __name__ == "__main__":
    asyncio.run(test_dynamic_excel())
