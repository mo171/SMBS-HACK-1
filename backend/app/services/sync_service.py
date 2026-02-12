import logging
from typing import Dict, Any
from integrations.bluesky_tool import BlueskyTool
from integrations.pixelfed_tool import PixelfedTool
from lib.supabase_lib import supabase, get_active_workflows_by_trigger
from workflows.engine import inngest_client
from inngest import Event

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self):
        self.bluesky = BlueskyTool()
        self.pixelfed = PixelfedTool()

    async def sync_all(self):
        """Main entry point to sync all platforms"""
        await self.sync_bluesky()
        await self.sync_pixelfed()

    async def sync_bluesky(self):
        logger.info("🔄 Syncing Bluesky DMs...")
        await self.bluesky._authenticate()
        my_handle = self.bluesky.handle

        # 1. List conversations
        convo_res = await self.bluesky.execute("list_convos", {})
        if convo_res.get("status") != "success":
            logger.error(f"Failed to list Bluesky convos: {convo_res.get('message')}")
            return

        for convo in convo_res.get("convos", []):
            convo_id = convo["id"]
            # Find the other member's handle
            other_members = [m for m in convo["members"] if m != my_handle]
            if not other_members:
                # Could be a chat with yourself
                other_handle = my_handle
            else:
                other_handle = other_members[0]

            # 2. Fetch messages for this convo
            msg_res = await self.bluesky.execute(
                "get_convo_messages", {"convo_id": convo_id, "limit": 20}
            )
            if msg_res.get("status") == "success":
                for msg in msg_res.get("messages", []):
                    # We don't have sender handle in msg objects from get_messages easily,
                    # but we have sender_did.
                    # For simplicity, if we are syncign we can just use the other_handle for the session.
                    # _ingest_message upserts based on platform + external_id (other_handle).

                    # We need to know who sent it.
                    # In atproto, msg.sender is a MessageViewSender with 'did'.
                    # We can't easily get handle from DID without another lookup,
                    # but we know it's either us or the 'other_handle'.

                    # For now, let's assume if it's not our DID, it's from the other_handle.
                    # We need our own DID.
                    my_did = self.bluesky.client.me.did

                    is_me = msg["sender_did"] == my_did
                    direction = "outbound" if is_me else "inbound"
                    sender_handle = my_handle if is_me else other_handle

                    await self._ingest_message(
                        platform="bluesky",
                        external_id=other_handle,
                        content=msg["text"],
                        sender_handle=sender_handle,
                        msg_external_id=msg["id"],
                        metadata={"convo_id": convo_id},
                        direction=direction,
                    )

            # Update session metadata if needed
            supabase.table("sessions").update({"metadata": {"convo_id": convo_id}}).eq(
                "platform", "bluesky"
            ).eq("external_id", other_handle).execute()

    async def sync_pixelfed(self):
        logger.info("🔄 Syncing Pixelfed notifications...")
        res = await self.pixelfed.execute("get_notifications", {})
        if res.get("status") == "success":
            for note in res.get("notifications", []):
                if note.get("type") == "mention":
                    status = note.get("status", {})
                    account = note.get("account", {})
                    await self._ingest_message(
                        platform="pixelfed",
                        external_id=account.get("username"),
                        content=status.get(
                            "content", ""
                        ),  # Pixelfed content might be HTML
                        sender_handle=account.get("username"),
                        msg_external_id=str(status.get("id")),
                        metadata={"status_id": status.get("id")},
                    )

    async def _ingest_message(
        self,
        platform: str,
        external_id: str,
        content: str,
        sender_handle: str,
        msg_external_id: str,
        metadata: Dict[str, Any] = None,
        direction: str = "inbound",
    ):
        try:
            # 1. UPSERT Session
            session_payload = {
                "platform": platform,
                "external_id": external_id,
                "updated_at": "now()",
            }
            session_res = (
                supabase.table("sessions")
                .upsert(session_payload, on_conflict="platform, external_id")
                .execute()
            )

            if not session_res.data:
                return

            session_id = session_res.data[0]["id"]
            is_bot_active = session_res.data[0].get("is_bot_active", True)

            # 2. Check if message already exists to avoid duplicates
            existing = (
                supabase.table("unified_messages")
                .select("id")
                .eq("external_id", msg_external_id)
                .execute()
            )
            if existing.data:
                return

            # 3. Insert Message
            display_content = content
            if metadata and metadata.get("parent_content"):
                parent_preview = metadata["parent_content"][:50]
                if len(metadata["parent_content"]) > 50:
                    parent_preview += "..."
                display_content = f'💬 [Replying to: "{parent_preview}"]\n\n{content}'

            supabase.table("unified_messages").insert(
                {
                    "session_id": session_id,
                    "platform": platform,
                    "direction": direction,
                    "content": display_content,
                    "external_id": msg_external_id,
                    "sender_handle": sender_handle,
                    "status": "received" if direction == "inbound" else "sent",
                }
            ).execute()

            logger.info(f"✅ Ingested {platform} message from {sender_handle}")

            # 4. Trigger Workflows if bot is active
            if is_bot_active:
                blueprints = get_active_workflows_by_trigger(platform)
                for bp in blueprints:
                    await inngest_client.send(
                        Event(
                            name="workflow/run_requested",
                            data={
                                "blueprint": bp,
                                "payload": {
                                    "author": sender_handle,
                                    "text": content,
                                    "platform": platform,
                                    "external_id": external_id,
                                    "metadata": metadata,
                                },
                            },
                        )
                    )
        except Exception as e:
            logger.error(f"❌ Error ingesting {platform} message: {e}")


sync_service = SyncService()
