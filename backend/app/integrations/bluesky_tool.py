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
        elif task == "get_author_feed":
            return await self.get_author_feed(params)
        elif task == "get_post":
            return await self.get_post(params)
        elif task == "post_reply":
            return await self.post_content(params)
        elif task == "list_convos":
            return await self.list_convos(params)
        elif task == "get_convo_messages":
            return await self.get_convo_messages(params)
        elif task == "send_dm":
            return await self.send_dm(params)

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def list_convos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List DM conversations"""
        try:
            chat_client = self.client.with_bsky_chat_proxy()
            res = chat_client.chat.bsky.convo.list_convos(params)
            convos = []
            for convo in res.convos:
                convos.append(
                    {
                        "id": convo.id,
                        "members": [m.handle for m in convo.members],
                        "unread_count": convo.unread_count,
                        "last_message": convo.last_message.text
                        if hasattr(convo.last_message, "text")
                        else None,
                    }
                )
            return {"status": "success", "convos": convos}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_convo_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch messages for a specific conversation"""
        convo_id = params.get("convo_id")
        limit = params.get("limit", 20)
        if not convo_id:
            return {"status": "error", "message": "Missing convo_id"}
        try:
            chat_client = self.client.with_bsky_chat_proxy()
            res = chat_client.chat.bsky.convo.get_messages(
                {"convo_id": convo_id, "limit": limit}
            )
            messages = []
            for msg in res.messages:
                if hasattr(msg, "text"):
                    messages.append(
                        {
                            "id": msg.id,
                            "rev": msg.rev,
                            "text": msg.text,
                            "sender_did": msg.sender.did
                            if hasattr(msg, "sender")
                            else None,
                            "created_at": msg.sent_at,
                        }
                    )
            return {"status": "success", "messages": messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_dm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a conversation"""
        convo_id = params.get("convo_id")
        text = params.get("text")
        if not convo_id or not text:
            return {"status": "error", "message": "Missing convo_id or text"}
        try:
            chat_client = self.client.with_bsky_chat_proxy()
            res = chat_client.chat.bsky.convo.send_message(
                {"convo_id": convo_id, "message": {"text": text}}
            )
            return {"status": "success", "id": res.id, "rev": res.rev}
        except Exception as e:
            return {"status": "error", "message": str(e)}

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
        """Fetches notifications/mentions with thread context"""
        try:
            notifications = self.client.app.bsky.notification.list_notifications()
            results = []
            for n in notifications.notifications:
                item = {
                    "uri": n.uri,
                    "cid": n.cid,
                    "author": n.author.handle,
                    "reason": n.reason,
                    "text": n.record.text if hasattr(n.record, "text") else "",
                }
                # Check for reply threading
                if hasattr(n.record, "reply") and n.record.reply:
                    item["parent_uri"] = n.record.reply.parent.uri
                    item["root_uri"] = n.record.reply.root.uri
                results.append(item)

            return {
                "status": "success",
                "notifications": results,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_author_feed(self, params: Dict[str, Any]):
        """Fetch the author's own posts and replies"""
        try:
            feed = self.client.app.bsky.feed.get_author_feed(
                {"actor": self.client.me.handle}
            )
            results = []
            for item in feed.feed:
                post = item.post
                res = {
                    "uri": post.uri,
                    "cid": post.cid,
                    "author": post.author.handle,
                    "text": post.record.text if hasattr(post.record, "text") else "",
                    "created_at": post.record.created_at
                    if hasattr(post.record, "created_at")
                    else None,
                }
                # Check if it's a reply
                if hasattr(post.record, "reply") and post.record.reply:
                    res["parent_uri"] = post.record.reply.parent.uri
                    res["root_uri"] = post.record.reply.root.uri
                results.append(res)

            return {"status": "success", "feed": results}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches a single post by URI"""
        uri = params.get("uri")
        if not uri:
            return {"status": "error", "message": "Missing uri"}
        try:
            res = self.client.app.bsky.feed.get_posts({"uris": [uri]})
            if res.posts:
                post = res.posts[0]
                return {
                    "status": "success",
                    "author": post.author.handle,
                    "text": post.record.text,
                }
            return {"status": "error", "message": "Post not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
