import logging
from typing import Any, Dict
from .base import BaseTool
from ..services.social_service import social_service
from ..services.action_service import action_service

logger = logging.getLogger(__name__)


class SocialLogicTool(BaseTool):
    @property
    def service_name(self) -> str:
        return "social_logic"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if task == "draft_reply":
            return await self.execute_draft_reply(params)

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def execute_draft_reply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Drafts a reply based on mention text and optional specific context.
        Params:
          - mention: {platform, author, text, ...}
          - context_type: 'stock' | 'ledger' | None
          - product_name: (if stock)
          - customer_name: (if ledger)
        """
        mention = params.get("mention", {})
        context_type = params.get("context_type")
        context_data = ""

        # Fetch Context if requested
        if context_type == "stock" and params.get("product_name"):
            stock_res = await action_service.get_stock(params.get("product_name"))
            if stock_res["found"]:
                context_data = (
                    f"Product: {stock_res['name']}, Current Stock: {stock_res['stock']}"
                )
            else:
                context_data = (
                    f"Product '{params.get('product_name')}' not found in inventory."
                )

        elif context_type == "ledger" and params.get("customer_name"):
            ledger_res = await action_service.get_customer_ledger(
                params.get("customer_name")
            )
            if ledger_res["status"] == "success":
                context_data = f"Customer: {ledger_res['customer']}, Balance Due: {ledger_res['balance_due']}"

        # Draft the reply using SocialService
        reply = await social_service.draft_reply(mention, business_context=context_data)

        return {
            "status": "success",
            "data": {
                "thought": reply.thought,
                "suggested_text": reply.suggested_text,
                "needs_approval": reply.needs_human_approval,
                "reply_to": {
                    "root": {"uri": mention.get("uri"), "cid": mention.get("cid")},
                    "parent": {"uri": mention.get("uri"), "cid": mention.get("cid")},
                },
            },
        }
