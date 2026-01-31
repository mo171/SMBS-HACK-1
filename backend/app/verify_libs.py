import asyncio
import os
import pandas as pd
from fpdf import FPDF
from io import BytesIO


async def test_pdf_gen():
    print("Testing PDF generation with fpdf2...")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", "B", 16)
        pdf.cell(0, 10, "TEST INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.output("test_invoice.pdf")
        print("PDF generated successfully: test_invoice.pdf")
        if os.path.exists("test_invoice.pdf"):
            os.remove("test_invoice.pdf")
    except Exception as e:
        print(f"PDF Error: {e}")


async def test_excel_gen():
    print("Testing Excel generation with pandas and openpyxl...")
    try:
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Test")
        data = output.getvalue()
        print(f"Excel generated successfully: {len(data)} bytes")
    except Exception as e:
        print(f"Excel Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_pdf_gen())
    asyncio.run(test_excel_gen())
