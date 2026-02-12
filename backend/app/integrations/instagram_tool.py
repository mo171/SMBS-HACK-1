import os
import httpx
import logging
from typing import Any, Dict
from .base import BaseTool
from lib.supabase_lib import supabase

logger = logging.getLogger(__name__)


class InstagramTool(BaseTool):
    def __init__(self):
        self.business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
        self.access_token = os.getenv("IG_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v19.0"

    @property
    def service_name(self) -> str:
        return "instagram"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.business_id or not self.access_token:
            return {
                "status": "error",
                "message": "Instagram credentials missing in .env",
            }

        if task == "publish_post":
            return await self.publish_post(params)
        elif task == "send_dm":
            return await self.send_dm(params)
        elif task == "get_conversations":
            return await self.get_conversations(params)

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def publish_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publishes a single image post to the IG Grid (Two-Step Process)"""
        image_url = params.get("image_url")
        caption = params.get("caption", "")

        if not image_url:
            return {"status": "error", "message": "Missing image_url"}

        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Create Media Container
                container_url = f"{self.base_url}/{self.business_id}/media"
                container_payload = {
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                }
                c_resp = await client.post(container_url, json=container_payload)
                if c_resp.status_code != 200:
                    return {
                        "status": "error",
                        "message": f"Container creation failed: {c_resp.text}",
                    }

                creation_id = c_resp.json().get("id")

                # Step 2: Publish Media
                publish_url = f"{self.base_url}/{self.business_id}/media_publish"
                publish_payload = {
                    "creation_id": creation_id,
                    "access_token": self.access_token,
                }
                p_resp = await client.post(publish_url, json=publish_payload)
                if p_resp.status_code == 200:
                    return {"status": "success", "post_id": p_resp.json().get("id")}
                return {
                    "status": "error",
                    "message": f"Publishing failed: {p_resp.text}",
                }
        except Exception as e:
            logger.error(f"Instagram publish error: {e}")
            return {"status": "error", "message": str(e)}

    async def send_dm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a direct message to a specific recipient ID"""
        recipient_id = params.get("recipient_id")
        text = params.get("text")

        if not recipient_id or not text:
            return {"status": "error", "message": "Missing recipient_id or text"}

        url = f"{self.base_url}/{self.business_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "access_token": self.access_token,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    # Sync to Unified Messages (Outbound)
                    try:
                        session_res = (
                            supabase.table("sessions")
                            .select("id")
                            .eq("platform", "instagram")
                            .eq("external_id", recipient_id)
                            .single()
                            .execute()
                        )
                        if session_res.data:
                            session_id = session_res.data["id"]
                            supabase.table("unified_messages").insert(
                                {
                                    "session_id": session_id,
                                    "platform": "instagram",
                                    "direction": "outbound",
                                    "content": text,
                                    "sender_handle": "AI Assistant",
                                    "status": "sent",
                                }
                            ).execute()
                    except Exception as log_e:
                        logger.error(f"Failed to sync outbound message: {log_e}")

                    return {"status": "success", "data": resp.json()}
                return {"status": "error", "message": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches recent conversation threads"""
        url = f"{self.base_url}/{self.business_id}/conversations"
        params_api = {
            "fields": "participants,messages{message,from,created_time}",
            "access_token": self.access_token,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, params=params_api)
                if resp.status_code == 200:
                    return {"status": "success", "data": resp.json()}
                return {"status": "error", "message": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
