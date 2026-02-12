from fastapi import APIRouter, Request, Query
import os
import logging
from lib.supabase_lib import supabase, get_active_workflows_by_trigger
from workflows.engine import inngest_client
from inngest import Event

from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class TakeoverRequest(BaseModel):
    platform: str
    external_id: str
    active: bool


@router.get("/webhooks/instagram")
async def instagram_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Meta Webhook Verification (Handshake)"""
    verify_token = os.getenv("IG_VERIFY_TOKEN")
    if hub_mode == "subscribe" and hub_challenge:
        if hub_verify_token == verify_token:
            return int(hub_challenge)
    return "Verification failed"


@router.post("/webhooks/instagram")
async def instagram_webhook(request: Request):
    """Processes incoming Instagram events (DMs, Comments)"""
    payload = await request.json()

    # Meta sends events in an 'entry' list
    for entry in payload.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            message_text = messaging_event.get("message", {}).get("text")

            if sender_id and message_text:
                # 1. Get or Create Session (UPSERT) to ensure we have an ID
                session_data = {
                    "platform": "instagram",
                    "external_id": sender_id,
                    # Default to active if new
                }
                session_res = (
                    supabase.table("sessions")
                    .upsert(session_data, on_conflict="platform, external_id")
                    .execute()
                )

                # Check if we got data back; sometimes upsert might not return if not specified,
                # but supabase-py usually returns the row if we don't say count='exact'.
                # Better to select it if upsert return is iffy, but let's try assuming it returns.
                # Actually, let's play it safe and just select it if we need, or trust the upsert return.
                # For safety/simplicity in this step, let's just use the returned data.

                if session_res.data:
                    session_id = session_res.data[0]["id"]
                    is_active = session_res.data[0].get("is_bot_active", True)
                else:
                    # Fallback fetch if upsert didn't return (shouldn't happen with standard config)
                    session_fetch = (
                        supabase.table("sessions")
                        .select("*")
                        .eq("platform", "instagram")
                        .eq("external_id", sender_id)
                        .single()
                        .execute()
                    )
                    session_id = session_fetch.data["id"]
                    is_active = session_fetch.data.get("is_bot_active", True)

                # 2. Log to Unified Messages (The "Single Pane of Glass")
                supabase.table("unified_messages").insert(
                    {
                        "session_id": session_id,
                        "platform": "instagram",
                        "direction": "inbound",
                        "content": message_text,
                        "external_id": None,  # Meta message ID not captured yet, optional
                        "sender_handle": sender_id,  # Using ID as handle for now
                        "status": "received",
                    }
                ).execute()

                if not is_active:
                    logger.info(
                        f"Bot is SILENCED for Instagram user {sender_id}. Ignoring."
                    )
                    continue

                # 2. Trigger active workflows
                blueprints = get_active_workflows_by_trigger("instagram")
                for bp in blueprints:
                    await inngest_client.send(
                        Event(
                            name="workflow/run_requested",
                            data={
                                "blueprint": bp,
                                "payload": {
                                    "author": sender_id,
                                    "text": message_text,
                                    "platform": "instagram",
                                    "external_id": sender_id,
                                },
                            },
                        )
                    )


@router.post("/social/takeover")
async def social_takeover(req: TakeoverRequest):
    """Silences or activates the bot for a specific user thread."""
    supabase.table("sessions").upsert(
        {
            "platform": req.platform,
            "external_id": req.external_id,
            "is_bot_active": req.active,
            "updated_at": "now()",
        },
        on_conflict="platform, external_id",
    ).execute()

    status = "Silenced" if not req.active else "Activated"
    return {"status": "success", "message": f"AI {status} for {req.external_id}"}
