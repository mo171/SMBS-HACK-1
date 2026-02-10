import os
import logging
from typing import Any, Dict
from atproto import Client
from .base import BaseTool

logger = logging.getLogger(__name__)


class BlueskyTool(BaseTool):
    def __init__(self):
        self.handle = os.getenv("BLUESKY_HANDLE")
        self.app_password = os.getenv("BLUESKY_APP_PASSWORD")
        self.client = Client()
        self._logged_in = False

    @property
    def service_name(self) -> str:
        return "bluesky"

    async def _authenticate(self):
        """Standard Bluesky login using handle and app password"""
        if self._logged_in:
            return True

        if not self.handle or not self.app_password:
            logger.warning(
                "Bluesky credentials (handle/app_password) missing in environment"
            )
            return False

        try:
            # atproto client.login is synchronous but we can call it in a thread if needed
            # for now we call it directly as it's typically fast
            self.client.login(self.handle, self.app_password)
            self._logged_in = True
            return True
        except Exception as e:
            logger.error(f"Bluesky auth failed: {e}")
        return False

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self._logged_in:
            success = await self._authenticate()
            if not success:
                return {
                    "status": "error",
                    "message": "Bluesky authentication failed. Check credentials.",
                }

        if task == "post_content":
            return await self.post_content(params)
        elif task == "read_notifications":
            return await self.read_notifications(params)

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def post_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Posts text content to Bluesky. Supports optional threaded replies."""
        text = params.get("text")
        reply_to = params.get(
            "reply_to"
        )  # Expected dict: {"root": {"uri": "...", "cid": "..."}, "parent": {...}}

        if not text:
            return {"status": "error", "message": "No text provided for post"}

        try:
            post = self.client.send_post(text=text, reply_to=reply_to)
            return {"status": "success", "uri": post.uri, "cid": post.cid}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def read_notifications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches unread notifications/mentions"""
        try:
            notifications = self.client.app.bsky.notification.list_notifications()
            return {
                "status": "success",
                "notifications": [
                    {
                        "uri": n.uri,
                        "cid": n.cid,
                        "author": n.author.handle,
                        "reason": n.reason,
                        "text": n.record.text if hasattr(n.record, "text") else "",
                    }
                    for n in notifications.notifications
                    if not n.is_read
                ],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
