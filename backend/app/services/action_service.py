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

            # Record amount_paid for later (Rejection logic)
            amount_paid_val = getattr(intent_data, "amount_paid", 0.0) or 0.0

            # Create Invoice Header
            inv_res = (
                self.supabase.table("invoices")
                .insert(
                    {
                        "customer_id": customer_id,
                        "status": "pending",
                        "total_amount": final_total_amt,
                        "amount_paid": amount_paid_val,  # NEW COLUMN
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

            # --- PERSISTENT DEBT SYNC ---
            # Balance = Total - Paid
            balance_change = float(final_total_amt) - float(amount_paid or 0)
            if balance_change != 0:
                # We update the customers' total_debt column
                # Note: This is an additive update.
                # We first get current, then add.
                cust_data = (
                    self.supabase.table("customers")
                    .select("total_debt")
                    .eq("id", customer_id)
                    .single()
                    .execute()
                )
                current_debt = float(cust_data.data.get("total_debt") or 0)
                new_debt = current_debt + balance_change
                self.supabase.table("customers").update({"total_debt": new_debt}).eq(
                    "id", customer_id
                ).execute()
                print(f"DEBUG: Updated Customer Debt: {current_debt} -> {new_debt}")

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

            # --- PERSISTENT DEBT SYNC ---
            cust_data = (
                self.supabase.table("customers")
                .select("total_debt")
                .eq("id", customer_id)
                .single()
                .execute()
            )
            current_debt = float(cust_data.data.get("total_debt") or 0)
            new_debt = current_debt - float(amount)
            self.supabase.table("customers").update({"total_debt": new_debt}).eq(
                "id", customer_id
            ).execute()
            print(
                f"DEBUG: Payment Recorded. Updated Debt: {current_debt} -> {new_debt}"
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

    async def get_all_debtors(self):
        """Returns a list of all customers who owe money (> 0)."""
        try:
            res = (
                self.supabase.table("customers")
                .select("full_name, total_debt")
                .gt("total_debt", 0)
                .order("total_debt", desc=True)
                .execute()
            )
            return {"status": "success", "data": res.data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_overall_ledger(self):
        """Calculates overall business totals: Total Billed, Total Paid, Balance Due."""
        try:
            # Sum ALL Invoices
            inv_data = self.supabase.table("invoices").select("total_amount").execute()
            total_billed = sum(
                float(row.get("total_amount") or 0) for row in inv_data.data
            )

            # Sum ALL Payments
            pay_data = (
                self.supabase.table("payments").select("amount_received").execute()
            )
            total_paid = sum(
                float(row.get("amount_received") or 0) for row in pay_data.data
            )

            return {
                "status": "success",
                "total_billed": total_billed,
                "total_paid": total_paid,
                "balance_due": total_billed - total_paid,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def generate_overall_ledger_pdf(self):
        """Generates a detailed PDF of all transactions (Invoices and Payments)."""
        try:
            # 1. Fetch Invoices
            inv_res = (
                self.supabase.table("invoices")
                .select("*, customers(full_name)")
                .order("created_at", desc=False)
                .execute()
            )
            invoices = inv_res.data

            # 2. Fetch Payments
            pay_res = (
                self.supabase.table("payments")
                .select("*, customers(full_name)")
                .order("created_at", desc=False)
                .execute()
            )
            payments = pay_res.data

            # 3. Combine and Sort by Date
            transactions = []
            for inv in invoices:
                transactions.append(
                    {
                        "date": inv["created_at"],
                        "name": inv.get("customers", {}).get("full_name", "N/A"),
                        "type": "Invoice",
                        "ref": inv["id"][:8],
                        "debit": float(inv["total_amount"]),
                        "credit": 0.0,
                    }
                )
            for pay in payments:
                transactions.append(
                    {
                        "date": pay["created_at"],
                        "name": pay.get("customers", {}).get("full_name", "N/A"),
                        "type": "Payment",
                        "ref": pay["id"][:8],
                        "debit": 0.0,
                        "credit": float(pay["amount_received"]),
                    }
                )

            # Sort by date
            transactions.sort(key=lambda x: x["date"])

            # 4. Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Times", "B", 18)
            pdf.cell(
                0,
                15,
                "OVERALL BUSINESS LEDGER",
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
            )
            pdf.set_font("Times", "", 10)

            # Use socket.gethostname() for Windows compatibility
            import socket

            hostname = socket.gethostname()
            pdf.cell(
                0,
                7,
                f"Run Date: {hostname}",
                new_x="LMARGIN",
                new_y="NEXT",
                align="R",
            )
            pdf.ln(5)

            # Table Header
            pdf.set_font("Times", "B", 10)
            pdf.set_fill_color(240, 240, 240)
            headers = [
                "Date",
                "Customer / Description",
                "Type",
                "Ref",
                "Debit (+)",
                "Credit (-)",
            ]
            widths = [25, 65, 20, 20, 30, 30]

            for i in range(len(headers)):
                pdf.cell(widths[i], 10, headers[i], 1, 0, "C", True)
            pdf.ln()

            # Table Content
            pdf.set_font("Times", "", 9)
            running_balance = 0.0
            for tx in transactions:
                running_balance += tx["debit"] - tx["credit"]

                # Ensure name is string and handle potential encoding issues
                cust_name = (
                    str(tx["name"]).encode("latin-1", "replace").decode("latin-1")
                )

                pdf.cell(widths[0], 8, str(tx["date"])[:10], 1)
                pdf.cell(widths[1], 8, cust_name, 1)
                pdf.cell(widths[2], 8, tx["type"], 1, 0, "C")
                pdf.cell(widths[3], 8, tx["ref"], 1, 0, "C")
                pdf.cell(
                    widths[4],
                    8,
                    f"{tx['debit']:,.2f}" if tx["debit"] > 0 else "-",
                    1,
                    0,
                    "R",
                )
                pdf.cell(
                    widths[5],
                    8,
                    f"{tx['credit']:,.2f}" if tx["credit"] > 0 else "-",
                    1,
                    1,
                    "R",
                )

            # Final Summary
            pdf.ln(5)
            pdf.set_font("Times", "B", 11)
            total_billed = sum(t["debit"] for t in transactions)
            total_paid = sum(t["credit"] for t in transactions)

            pdf.cell(130, 10, "Total Billed Amount:", 0, 0, "R")
            pdf.cell(60, 10, f"Rs. {total_billed:,.2f}", 1, 1, "R")
            pdf.cell(130, 10, "Total Received Amount:", 0, 0, "R")
            pdf.cell(60, 10, f"Rs. {total_paid:,.2f}", 1, 1, "R")
            pdf.set_text_color(200, 0, 0)
            pdf.cell(130, 10, "NET OUTSTANDING BALANCE:", 0, 0, "R")
            pdf.cell(60, 10, f"Rs. {total_billed - total_paid:,.2f}", 1, 1, "R")

            return bytes(pdf.output())
        except Exception as e:
            print(f"!!! Error generating overall ledger PDF: {e}")
            raise e

    async def generate_aging_debtors_excel(self):
        """Generates Aging Report: Categorizes debt by days (0-30, 31-60, etc.)"""
        try:
            # 1. Fetch Invoices and Payments to calculate aging
            # Simpler approach: Use the total_debt already calculated in 'customers' table
            # But the user might want it "by invoice age".
            # To be accurate, we'd need to look at 'invoices' where 'status=pending'.

            inv_res = (
                self.supabase.table("invoices")
                .select("*, customers(full_name)")
                .neq("status", "paid")  # Assuming status might be 'paid' eventually
                .execute()
            )

            aging_data = []
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)

            for inv in inv_res.data:
                total = float(inv["total_amount"] or 0)
                paid = float(inv["amount_paid"] or 0)
                due = total - paid

                if due > 0:
                    created_at = datetime.fromisoformat(
                        inv["created_at"].replace("Z", "+00:00")
                    )
                    days_old = (now - created_at).days

                    row = {
                        "Customer": inv.get("customers", {}).get("full_name", "N/A"),
                        "Invoice ID": inv["id"][:8],
                        "Date": inv["created_at"][:10],
                        "Amount Due": due,
                        "0-30 Days": due if days_old <= 30 else 0,
                        "31-60 Days": due if 30 < days_old <= 60 else 0,
                        "61-90 Days": due if 60 < days_old <= 90 else 0,
                        "90+ Days": due if days_old > 90 else 0,
                    }
                    aging_data.append(row)

            df = pd.DataFrame(aging_data)

            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Aging Debtors")

            output.seek(0)
            return output.read()
        except Exception as e:
            print(f"!!! Error generating aging debtors excel: {e}")
            raise e


action_service = ActionService()
