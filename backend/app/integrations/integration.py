import razorpay
from .base import BaseTool

class RazorpayTool(BaseTool):
    def __init__(self):
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )
    
    @property
    def service_name(self) -> str:
        return "razorpay"
    
    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if task == "create_payment_link":
            payment_link = self.client.payment_link.create({
                "amount": int(params["amount"]) * 100,  # Convert to paise
                "currency": params.get("currency", "INR"),
                "description": params.get("description", "Payment"),
                "customer": {
                    "name": params.get("customer_name", "Customer"),
                    "email": params.get("customer_email"),
                    "contact": params.get("customer_phone"),
                }
            })
            return {"status": "success", "payment_link": payment_link}
        
        return {"status": "error", "message": f"Unknown task: {task}"}