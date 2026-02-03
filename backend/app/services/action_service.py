"""
ActionService handles core business logic for the application, specifically interacting with Supabase.

Key Functions:
- create_invoice_record: Inserts a new invoice record into the database.
- add_invoice_items: Adds line items to an existing invoice.
- generate_pdf: Generates a PDF invoice using FPDF.
- upload_pdf: Uploads the generated PDF to Supabase storage.
- get_or_create_customer: Searches for a customer by name (case-insensitive) or creates a new entry if not found.
- execute_invoice: Orchestrates the invoice creation process, including customer resolution, total amount calculation, and database insertion.
"""

# imports
import os
from supabase import create_client, Client
from io import BytesIO
from fpdf import FPDF
import pandas as pd
from .intent_service import CreateInvoiceIntent
from dotenv import load_dotenv

# load env variables
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


class ActionService:
    """Handles core business logic for the application, specifically interacting with Supabase."""

    def __init__(self):
        self.supabase = supabase

    # --- CUSTOMER HELPERS ---
    async def get_or_create_customer(self, name: str):
        """Finds a customer by name or creates a new one."""
        res = (
            self.supabase.table("customers")
            .select("id")
            .ilike("full_name", f"%{name}%")
            .execute()
        )
        if res.data:
            return res.data[0]["id"]

        new_cust = (
            self.supabase.table("customers").insert({"full_name": name}).execute()
        )
        return new_cust.data[0]["id"]

    # --- INVOICE & STOCK LOGIC (The "X") ---
    async def calculate_potential_total(self, items):
        """
        Calculates the expected total amount based on DB prices.
        Returns: { "total": float, "details": list }
        """
        total = 0.0
        details = []

        print(f"--- DEBUG: Calculating Potential Total for {len(items)} items ---")

        for item in items:
            # Strategy:
            # 1. Exact Match (ilike name) - Best confidence
            # 2. Contains Match (ilike %name%) - Good confidence
            # 3. Fuzzy/Words Match (ilike %word%) - Fallback

            clean_name = item.name.strip()
            found_price = 0.0
            found_name = clean_name
            match_method = "None"

            # 1. Exact-ish Match
            res = (
                self.supabase.table("products")
                .select("name, base_price")
                .ilike("name", clean_name)
                .execute()
            )

            if res.data:
                match_method = "Exact"
                found_price = float(res.data[0].get("base_price", 0) or 0)
                found_name = res.data[0]["name"]

            # 2. Contains Match (if exact failed)
            if match_method == "None":
                res = (
                    self.supabase.table("products")
                    .select("name, base_price")
                    .ilike("name", f"%{clean_name}%")
                    .execute()
                )
                if res.data:
                    match_method = "Contains"
                    found_price = float(res.data[0].get("base_price", 0) or 0)
                    found_name = res.data[0]["name"]

            # 3. Fuzzy Words Match (if contains failed)
            if match_method == "None":
                words = clean_name.split()
                if len(words) > 1:
                    or_filter = ",".join([f"name.ilike.%{word}%" for word in words])
                    res = (
                        self.supabase.table("products")
                        .select("name, base_price")
                        .or_(or_filter)
                        .execute()
                    )
                    if res.data:
                        match_method = "Fuzzy"
                        found_price = float(res.data[0].get("base_price", 0) or 0)
                        found_name = res.data[0]["name"]

            print(
                f"DEBUG: Item '{clean_name}' -> Match: {match_method}, Price: {found_price}, Name: {found_name}"
            )

            line_total = found_price * item.quantity
            total += line_total
            details.append(
                {
                    "name": found_name,
                    "original_input": item.name,
                    "quantity": item.quantity,
                    "unit_price": found_price,
                    "line_total": line_total,
                }
            )

        print(f"--- DEBUG: Total Amount Calculated: {total} ---")
        return {"total": total, "details": details}

    async def execute_invoice(self, intent_data: CreateInvoiceIntent):
        """Orchestrates the invoice creation process, including customer resolution, total amount calculation, and database insertion."""
        try:
            customer_id = await self.get_or_create_customer(intent_data.customer_name)

            # 1. Calculate Total Amount Logic
            # STRATEGY:
            # - If is_due=True: Total = Calculated(DB) or explicitly inferred from "Paid + Due" (if user said so).
            #   But best is to rely on DB prices as the source of truth for "Total Bill".
            # - If discount_applied=True: We accept 'amount_paid' (if present) as the Total Bill (effective price).
            # - Default: Try DB prices.

            # Get DB estimates first
            calc_result = await self.calculate_potential_total(intent_data.items)
            db_total = calc_result["total"]

            # Decide on Final Total Amount
            final_total_amt = 0.0

            if intent_data.discount_applied and intent_data.amount_paid is not None:
                # User says "Discount given, final price 800".
                final_total_amt = intent_data.amount_paid
            elif intent_data.is_due and intent_data.amount_paid is not None:
                # User says "Paid 400, rest due". Implies Total is likely the DB Total (or user mentioned total).
                # If DB found prices, use them.
                if db_total > 0:
                    final_total_amt = db_total
                else:
                    # Fallback: We don't know total.
                    # Complex case. If user said "Total 900, paid 400", amount_paid=400.
                    # We might need to assume Total = Paid + Due if we had a "amount_due" field, but we don't in CreateInvoice.
                    # For now, default to (Paid + 0) which is wrong for Due.
                    # Lets assume for now DB always has price or we rely on logic upstream.
                    final_total_amt = (
                        db_total if db_total > 0 else intent_data.amount_paid
                    )  # Fallback
            else:
                # Standard Case
                if db_total > 0:
                    final_total_amt = db_total
                else:
                    final_total_amt = intent_data.amount_paid or 0

            # Create Invoice Header
            inv_res = (
                self.supabase.table("invoices")
                .insert(
                    {
                        "customer_id": customer_id,
                        "status": "pending",
                        "total_amount": final_total_amt,
                    }
                )
                .execute()
            )

            invoice_id = inv_res.data[0]["id"]

            # Insert Line Items
            line_items = []
            for i, item in enumerate(intent_data.items):
                # Match logic with calc_result to get unit price
                # We can try to look up key in calc_result details
                # Simple list index match since ordered

                u_price = 0.0
                if i < len(calc_result["details"]):
                    u_price = calc_result["details"][i]["unit_price"]

                # If we applied a generic discount (Total = Paid), we need to adjust unit prices to match Total?
                # Or just put u_price and let the sum mismatch?
                # Better to scale unit price if discount applied.
                if intent_data.discount_applied and db_total > 0:
                    ratio = final_total_amt / db_total
                    u_price = u_price * ratio

                line_items.append(
                    {
                        "invoice_id": invoice_id,
                        "description": item.name,
                        "quantity": item.quantity,
                        "unit_price": u_price,
                    }
                )

            self.supabase.table("invoice_items").insert(line_items).execute()

            # Record Payment (Full or Partial)
            amount_paid = getattr(intent_data, "amount_paid", None)

            # Logic: If 'is_due' is True, use the explicit amount_paid.
            # If 'is_due' is False and 'amount_paid' is None -> Assume Full Payment
            if amount_paid is None and not intent_data.is_due:
                amount_paid = final_total_amt
            elif amount_paid is None and intent_data.is_due:
                amount_paid = 0  # "Remaining 500 is due" -> implies X paid? Or 0 paid? usually means partial.
                # If user said "Total 900, remaining 500 due", prompt logic says Paid=400. So we are good.

            if amount_paid and amount_paid > 0:
                self.supabase.table("payments").insert(
                    {
                        "customer_id": customer_id,
                        "amount_received": amount_paid,
                        "payment_mode": "Cash",
                    }
                ).execute()

            # Construct enriched items list for Frontend
            enriched_items = []
            for i, item in enumerate(intent_data.items):
                u_price = 0.0
                line_total = 0.0
                # Try to grab from calc_result again or line_items
                # Simplified: just grab from the 'line_items' dict we built for SQL
                if i < len(line_items):
                    u_price = line_items[i]["unit_price"]
                    line_total = u_price * item.quantity

                enriched_items.append(
                    {
                        "name": item.name,
                        "quantity": item.quantity,
                        "price": u_price,  # Frontend expects 'price'
                        "total": line_total,
                    }
                )

            return {
                "status": "success",
                "invoice_id": invoice_id,
                "amount": final_total_amt,
                "amount_paid": amount_paid or 0,
                "items": enriched_items,  # RETURN THIS!
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_stock(self, product_name: str):
        """Fetches current inventory level with robust matching."""
        # 1. Try exact/partial string match first
        res = (
            self.supabase.table("products")
            .select("name, current_stock")
            .ilike("name", f"%{product_name}%")
            .execute()
        )
        if res.data:
            return {
                "found": True,
                "name": res.data[0]["name"],
                "stock": res.data[0]["current_stock"],
            }

        # 2. Fallback: Split words and find the best match
        # e.g., "pcv pipe" -> "pipe" matches "PVC Pipe"
        # method 1 should work most of the time this is just for fallback generated by a.i
        words = product_name.split()
        if len(words) > 1:
            # Get all products that match ANY of the words
            # Supabase doesn't support "OR" easily in one ilike chain without "or" filter syntax
            # We'll use the 'or' filter string format: name.ilike.%word1%,name.ilike.%word2%
            or_filter = ",".join([f"name.ilike.%{word}%" for word in words])

            res = (
                self.supabase.table("products")
                .select("name, current_stock")
                .or_(or_filter)
                .execute()
            )

            if res.data:
                # Find the result that matches the most words
                # Simple heuristic: Just take the first one for now, or refine if needed
                # Ideally, we'd score them. But for "pcv pipe", "pipe" returns "PVC Pipe".
                return {
                    "found": True,
                    "name": res.data[0]["name"],
                    "stock": res.data[0]["current_stock"],
                }

        return {"found": False}

    # --- PAYMENT & LEDGER LOGIC (The "Y") ---
    async def record_payment(self, customer_name: str, amount: float):
        """Records a cash/UPI payment from a customer."""
        try:
            customer_id = await self.get_or_create_customer(customer_name)
            res = (
                self.supabase.table("payments")
                .insert({"customer_id": customer_id, "amount_received": amount})
                .execute()
            )
            return {"status": "success", "data": res.data[0]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def generate_invoice_pdf(self, invoice_id: str):
        """Fetches invoice details and creates a PDF in memory."""
        # 1. Fetch data from Supabase
        inv = (
            self.supabase.table("invoices")
            .select("*, customers(full_name)")
            .eq("id", invoice_id)
            .single()
            .execute()
        )
        items_res = (
            self.supabase.table("invoice_items")
            .select("*")
            .eq("invoice_id", invoice_id)
            .execute()
        )

        data = inv.data
        items = items_res.data
        customer_id = data["customer_id"]

        # Fetch the potential payment recorded during invoice creation
        # We look for a payment by this customer created around the same time
        payment_res = (
            self.supabase.table("payments")
            .select("amount_received")
            .eq("customer_id", customer_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        amount_paid = payment_res.data[0]["amount_received"] if payment_res.data else 0

        # Check if we should show price columns
        has_prices = any(float(item.get("unit_price") or 0) > 0 for item in items)

        # 2. Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", "B", 18)
        pdf.cell(0, 15, "INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Times", "", 11)
        pdf.cell(0, 7, f"Invoice ID: {invoice_id}", new_x="LMARGIN", new_y="NEXT")

        # Safe access to customer name
        cust_name = data.get("customers", {}).get("full_name", "N/A")
        pdf.cell(
            0,
            7,
            f"Customer: {cust_name}",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # Safe access to created_at
        created_at = data.get("created_at", "")
        date_str = created_at[:10] if created_at else "N/A"
        pdf.cell(
            0,
            7,
            f"Date: {date_str}",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(10)

        # Table Header logic
        pdf.set_font("Times", "B", 12)
        pdf.set_fill_color(240, 240, 240)

        if has_prices:
            # 4 columns: Item, Qty, Price, Total
            col_widths = [80, 20, 30, 40]
            headers = ["Item", "Qty", "Price", "Total"]
        else:
            # 2 columns: Item, Qty
            col_widths = [140, 30]
            headers = ["Item", "Qty"]

        for i in range(len(headers)):
            pdf.cell(
                col_widths[i],
                10,
                headers[i],
                1,
                0 if i < len(headers) - 1 else 1,
                "C",
                True,
            )

        # Table Content
        pdf.set_font("Times", "", 12)
        for item in items:
            desc = str(item["description"])
            qty = float(item["quantity"] or 0)
            price = float(item["unit_price"] or 0)

            if has_prices:
                total = qty * price
                pdf.cell(col_widths[0], 10, desc, 1)
                pdf.cell(
                    col_widths[1],
                    10,
                    str(int(qty) if qty.is_integer() else qty),
                    1,
                    0,
                    "C",
                )
                pdf.cell(col_widths[2], 10, f"{price:.2f}", 1, 0, "R")
                pdf.cell(col_widths[3], 10, f"{total:.2f}", 1, 1, "R")
            else:
                pdf.cell(col_widths[0], 10, desc, 1)
                pdf.cell(
                    col_widths[1],
                    10,
                    str(int(qty) if qty.is_integer() else qty),
                    1,
                    1,
                    "C",
                )

        pdf.ln(10)

        # Summary Section
        pdf.set_font("Times", "B", 12)
        # Total Amount
        pdf.cell(130, 10, "Total Amount:", 0, 0, "R")
        pdf.cell(40, 10, f"{data['total_amount']:.2f}", 1, 1, "R")

        # Amount Paid (Optional)
        if amount_paid > 0:
            pdf.cell(130, 10, "Amount Paid:", 0, 0, "R")
            pdf.set_text_color(0, 128, 0)
            pdf.cell(40, 10, f"{amount_paid:.2f}", 1, 1, "R")
            pdf.set_text_color(0, 0, 0)

            balance = data["total_amount"] - amount_paid
            if balance > 0:
                pdf.cell(130, 10, "Balance Due:", 0, 0, "R")
                pdf.set_text_color(200, 0, 0)
                pdf.cell(40, 10, f"{balance:.2f}", 1, 1, "R")
                pdf.set_text_color(0, 0, 0)

        return bytes(pdf.output())

    async def generate_inventory_excel(self):
        """Exports the products table to an Excel buffer, hiding empty columns."""
        res = self.supabase.table("products").select("*").execute()
        # takes the prodcut table(thats only important) a.i generated codes convert it into excel and sends
        df = pd.DataFrame(res.data)

        # Drop columns that are completely null or zero across all rows
        # For numeric columns like 'base_price', 'current_stock'
        cols_to_check = ["base_price", "current_stock"]
        for col in cols_to_check:
            if col in df.columns:
                if (df[col].isna().all()) or (df[col] == 0).all():
                    df = df.drop(columns=[col])

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Inventory")

        output.seek(0)
        return output.read()

    async def generate_invoice_excel(self, invoice_id: str):
        """Generates a dynamic Excel report for a specific invoice."""
        # Fetch data (Similar to PDF logic)
        inv = (
            self.supabase.table("invoices")
            .select("*, customers(full_name)")
            .eq("id", invoice_id)
            .single()
            .execute()
        )
        items_res = (
            self.supabase.table("invoice_items")
            .select("*")
            .eq("invoice_id", invoice_id)
            .execute()
        )

        data = inv.data
        items = items_res.data
        customer_id = data.get("customer_id")

        # Fetch payment
        payment_res = (
            self.supabase.table("payments")
            .select("amount_received")
            .eq("customer_id", customer_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        amount_paid = payment_res.data[0]["amount_received"] if payment_res.data else 0

        # Build DataFrame for items
        rows = []
        has_prices = any(float(item.get("unit_price") or 0) > 0 for item in items)

        for item in items:
            row = {"Item": item.get("description"), "Quantity": item.get("quantity")}
            if has_prices:
                price = float(item.get("unit_price") or 0)
                qty = float(item.get("quantity") or 0)
                row["Unit Price"] = price
                row["Total"] = price * qty
            rows.append(row)

        df = pd.DataFrame(rows)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Invoice Details", startrow=4)
            sheet = writer.sheets["Invoice Details"]

            # Add Header Metadata
            sheet["A1"] = "INVOICE REPORT"
            sheet["A2"] = f"Invoice ID: {invoice_id}"
            sheet["A3"] = (
                f"Customer: {data.get('customers', {}).get('full_name', 'N/A')}"
            )
            sheet["A4"] = f"Date: {data.get('created_at', '')[:10]}"

            # Add Summary Section after the table
            summary_start_row = len(rows) + 6
            sheet.cell(row=summary_start_row, column=1, value="Summary:")
            sheet.cell(row=summary_start_row + 1, column=1, value="Total Amount:")
            sheet.cell(
                row=summary_start_row + 1, column=2, value=data.get("total_amount", 0)
            )

            if amount_paid > 0:
                sheet.cell(row=summary_start_row + 2, column=1, value="Amount Paid:")
                sheet.cell(row=summary_start_row + 2, column=2, value=amount_paid)

                balance = float(data.get("total_amount", 0)) - float(amount_paid)
                sheet.cell(row=summary_start_row + 3, column=1, value="Balance Due:")
                sheet.cell(row=summary_start_row + 3, column=2, value=max(0, balance))

        output.seek(0)
        return output.read()

    async def get_customer_ledger(self, customer_name: str):
        """Calculates X (Invoices) - Y (Payments) = Balance."""
        try:
            customer_id = await self.get_or_create_customer(customer_name)

            # Sum Invoices
            inv_data = (
                self.supabase.table("invoices")
                .select("total_amount")
                .eq("customer_id", customer_id)
                .execute()
            )
            total_x = sum(row["total_amount"] for row in inv_data.data)

            # Sum Payments
            pay_data = (
                self.supabase.table("payments")
                .select("amount_received")
                .eq("customer_id", customer_id)
                .execute()
            )
            total_y = sum(row["amount_received"] for row in pay_data.data)

            return {
                "status": "success",
                "customer": customer_name,
                "total_billed": total_x,
                "total_paid": total_y,
                "balance_due": total_x - total_y,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


action_service = ActionService()
