import os
from supabase import create_client, Client

# from intent_service import CreateInvoiceIntent
from .intent_service import CreateInvoiceIntent
from dotenv import load_dotenv

load_dotenv()


class ActionService:
    def __init__(self):
        # Ensure these are in your .env file
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

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
    async def execute_invoice(self, intent_data: CreateInvoiceIntent):
        """Saves a new invoice and its line items."""
        try:
            customer_id = await self.get_or_create_customer(intent_data.customer_name)

            # Insert Header
            total_amt = sum(item.quantity * item.price for item in intent_data.items)
            inv_res = (
                self.supabase.table("invoices")
                .insert(
                    {
                        "customer_id": customer_id,
                        "status": "pending",
                        "total_amount": total_amt,
                    }
                )
                .execute()
            )

            invoice_id = inv_res.data[0]["id"]

            # Insert Line Items (Triggers stock reduction automatically in DB)
            line_items = [
                {
                    "invoice_id": invoice_id,
                    "description": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.price,
                }
                for item in intent_data.items
            ]
            self.supabase.table("invoice_items").insert(line_items).execute()

            return {"status": "success", "invoice_id": invoice_id, "amount": total_amt}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_stock(self, product_name: str):
        """Fetches current inventory level."""
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
