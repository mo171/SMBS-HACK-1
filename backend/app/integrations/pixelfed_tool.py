import os
import httpx
import logging
from typing import Any, Dict
from .base import BaseTool

logger = logging.getLogger(__name__)


class PixelfedTool(BaseTool):
    """
    Pixelfed Integration Tool

    Pixelfed is an open-source, federated photo-sharing platform (like Instagram but decentralized).
    Uses Mastodon-compatible API - much simpler than Instagram's Graph API.

    Features:
    - Single-step posting (vs Instagram's 2-step container + publish)
    - Personal Access Token authentication (no complex OAuth)
    - No rate limits or app review required
    - Can interact with Mastodon users too (federated)
    """

    def __init__(self):
        self.instance_url = os.getenv(
            "PIXELFED_INSTANCE_URL", "https://pixelfed.social"
        )
        self.access_token = os.getenv("PIXELFED_ACCESS_TOKEN")
        self.api_base = f"{self.instance_url}/api/v1"

        if not self.access_token:
            logger.warning("⚠️ [PixelfedTool] Access token not found in .env")
        else:
            logger.info(
                f"✅ [PixelfedTool] Initialized for instance: {self.instance_url}"
            )

    @property
    def service_name(self) -> str:
        return "pixelfed"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Pixelfed task"""
        logger.info(f"🔵 [PixelfedTool] Executing task: {task}")

        if not self.access_token:
            return {
                "status": "error",
                "message": "Pixelfed access token missing in .env. Generate one at Settings → Applications → Personal Access Tokens",
            }

        if task == "publish_post":
            return await self.publish_post(params)
        elif task == "upload_media":
            return await self.upload_media(params)
        elif task == "get_notifications":
            return await self.get_notifications(params)
        elif task == "post_reply":
            return await self.post_reply(params)
        elif task == "verify_credentials":
            return await self.verify_credentials()

        return {"status": "error", "message": f"Unknown task: {task}"}

    async def verify_credentials(self) -> Dict[str, Any]:
        """Verify that the access token is valid"""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_base}/accounts/verify_credentials", headers=headers
                )

                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "success",
                        "username": data.get("username"),
                        "display_name": data.get("display_name"),
                        "followers_count": data.get("followers_count"),
                        "following_count": data.get("following_count"),
                    }
                return {"status": "error", "message": f"Auth failed: {resp.text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def publish_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a post to Pixelfed (single-step, much simpler than Instagram!)

        Params:
        - caption (str): Text caption for the post
        - media_ids (list): List of uploaded media IDs
        - image_url (str): Direct image URL (will be uploaded automatically)
        - visibility (str): 'public', 'unlisted', 'private', 'direct' (default: public)
        """
        caption = params.get("caption", "")
        media_ids = params.get("media_ids", [])
        image_url = params.get("image_url")
        visibility = params.get("visibility", "public")

        # If image_url provided, upload it first
        if image_url and not media_ids:
            logger.info(f"📤 [PixelfedTool] Uploading image from URL: {image_url}")
            upload_result = await self.upload_media({"image_url": image_url})
            if upload_result.get("status") == "success":
                media_ids = [upload_result["media_id"]]
            else:
                return upload_result

        if not media_ids:
            return {
                "status": "error",
                "message": "No media provided. Include either 'media_ids' or 'image_url'",
            }

        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"status": caption, "media_ids": media_ids, "visibility": visibility}

        logger.info(f"📸 [PixelfedTool] Publishing post with {len(media_ids)} media")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.api_base}/statuses", headers=headers, json=payload
                )

                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"✅ [PixelfedTool] Post published: {data.get('url')}")
                    return {
                        "status": "success",
                        "post_id": data.get("id"),
                        "url": data.get("url"),
                        "created_at": data.get("created_at"),
                        "visibility": data.get("visibility"),
                    }

                logger.error(f"❌ [PixelfedTool] Post failed: {resp.text}")
                return {
                    "status": "error",
                    "message": f"Post failed (HTTP {resp.status_code}): {resp.text}",
                }
        except Exception as e:
            logger.error(f"❌ [PixelfedTool] Exception: {e}")
            return {"status": "error", "message": str(e)}

    async def upload_media(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload media file to Pixelfed

        Params:
        - image_url (str): URL of image to download and upload
        - file_path (str): Local file path to upload
        - description (str): Alt text for accessibility
        """
        image_url = params.get("image_url")
        file_path = params.get("file_path")
        description = params.get("description", "")

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = None

                if image_url:
                    logger.info(f"⬇️ [PixelfedTool] Downloading image from: {image_url}")
                    # Download image first
                    img_resp = await client.get(image_url)
                    if img_resp.status_code != 200:
                        return {
                            "status": "error",
                            "message": f"Failed to download image: {img_resp.status_code}",
                        }

                    files = {"file": ("image.jpg", img_resp.content, "image/jpeg")}

                elif file_path:
                    logger.info(f"📁 [PixelfedTool] Uploading from file: {file_path}")
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    files = {"file": (os.path.basename(file_path), file_content)}
                else:
                    return {
                        "status": "error",
                        "message": "No image_url or file_path provided",
                    }

                # Add description if provided
                data = {}
                if description:
                    data["description"] = description

                logger.info("📤 [PixelfedTool] Uploading media to Pixelfed...")
                resp = await client.post(
                    f"{self.api_base}/media", headers=headers, files=files, data=data
                )

                if resp.status_code == 200:
                    media_data = resp.json()
                    logger.info(
                        f"✅ [PixelfedTool] Media uploaded: {media_data.get('id')}"
                    )
                    return {
                        "status": "success",
                        "media_id": media_data.get("id"),
                        "url": media_data.get("url"),
                        "preview_url": media_data.get("preview_url"),
                    }

                logger.error(f"❌ [PixelfedTool] Upload failed: {resp.text}")
                return {
                    "status": "error",
                    "message": f"Upload failed (HTTP {resp.status_code}): {resp.text}",
                }
        except Exception as e:
            logger.error(f"❌ [PixelfedTool] Exception: {e}")
            return {"status": "error", "message": str(e)}

    async def get_notifications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recent notifications (mentions, likes, follows, etc.)

        Params:
        - limit (int): Number of notifications to fetch (default: 20)
        """
        limit = params.get("limit", 20)
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_base}/notifications",
                    headers=headers,
                    params={"limit": limit},
                )

                if resp.status_code == 200:
                    notifications = resp.json()
                    logger.info(
                        f"✅ [PixelfedTool] Fetched {len(notifications)} notifications"
                    )
                    return {
                        "status": "success",
                        "count": len(notifications),
                        "notifications": notifications,
                    }
                return {
                    "status": "error",
                    "message": f"Failed to fetch notifications: {resp.text}",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def post_reply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reply to a Pixelfed post/mention
        Params:
        - in_reply_to_id (str): The ID of the post to reply to
        - text (str): The text content for the reply
        """
        in_reply_to_id = params.get("in_reply_to_id")
        text = params.get("text")

        if not in_reply_to_id or not text:
            return {"status": "error", "message": "Missing in_reply_to_id or text"}

        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
            "status": text,
            "in_reply_to_id": in_reply_to_id,
            "visibility": "public",
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base}/statuses", headers=headers, json=payload
                )

                if resp.status_code == 200:
                    return {"status": "success", "data": resp.json()}
                return {"status": "error", "message": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
