from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from lib.supabase_lib import supabase
from integrations.instagram_tool import InstagramTool
from integrations.bluesky_tool import BlueskyTool
from integrations.pixelfed_tool import PixelfedTool
from services.sync_service import sync_service

router = APIRouter()


@router.get("/api/messages/sessions")
async def get_message_sessions():
    """FETCH list of active chat sessions with latest message preview"""
    try:
        # Fetch sessions ordered by most recent activity
        sessions = (
            supabase.table("sessions")
            .select("*")
            .order("updated_at", desc=True)
            .execute()
        )

        result = []
        if sessions.data:
            for sess in sessions.data:
                # Basic preview fetch (N+1 query, okay for MVP scale)
                last_msg_res = (
                    supabase.table("unified_messages")
                    .select("content, created_at, sender_handle")
                    .eq("session_id", sess["id"])
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )

                if last_msg_res.data:
                    last_msg = last_msg_res.data[0]
                    sess["last_message"] = last_msg.get("content", "Media/Unknown")
                    sess["sender_handle"] = last_msg.get(
                        "sender_handle", sess["external_id"]
                    )
                    sess["last_active"] = last_msg.get("created_at")
                else:
                    sess["last_message"] = "No messages yet"

                result.append(sess)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/messages/{session_id}")
async def get_session_messages(session_id: str):
    """FETCH full chat history for a specific session"""
    try:
        messages = (
            supabase.table("unified_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )

        return {"status": "success", "data": messages.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/messages/whatsapp/all")
async def get_all_whatsapp_messages():
    """FETCH all WhatsApp messages across all sessions for aggregate view"""
    try:
        # Get all WhatsApp sessions
        sessions = (
            supabase.table("sessions").select("id").eq("platform", "whatsapp").execute()
        )

        if not sessions.data:
            return {"status": "success", "data": []}

        # Get all session IDs
        session_ids = [s["id"] for s in sessions.data]

        # Fetch all messages from these sessions
        messages = (
            supabase.table("unified_messages")
            .select("*")
            .in_("session_id", session_ids)
            .order("created_at", desc=False)
            .execute()
        )

        return {"status": "success", "data": messages.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/messages/sync")
async def sync_messages():
    """Trigger manual sync for Bluesky and Pixelfed"""
    try:
        await sync_service.sync_all()
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SendMessageRequest(BaseModel):
    session_id: str
    text: str
    reply_to_id: str = None  # Optional database ID of the message being replied to


@router.get("/api/messages/sessions/{session_id}/detail")
async def get_session_detail(session_id: str):
    """Fetch session details including bot status"""
    try:
        res = (
            supabase.table("sessions")
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(404, "Session not found")
        return {"status": "success", "data": res.data}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post("/api/messages/sessions/{session_id}/toggle-bot")
async def toggle_session_bot(session_id: str):
    """Toggle the is_bot_active flag for a session"""
    try:
        # Get current status
        current = (
            supabase.table("sessions")
            .select("is_bot_active")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not current.data:
            raise HTTPException(404, "Session not found")

        new_status = not current.data.get("is_bot_active", True)
        res = (
            supabase.table("sessions")
            .update({"is_bot_active": new_status})
            .eq("id", session_id)
            .execute()
        )
        return {"status": "success", "is_bot_active": new_status}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post("/api/messages/send")
async def send_message(req: SendMessageRequest):
    """Wait for manual/AI reply to be sent"""
    try:
        # 1. Get session details
        session_res = (
            supabase.table("sessions")
            .select("*")
            .eq("id", req.session_id)
            .single()
            .execute()
        )
        if not session_res.data:
            raise HTTPException(404, "Session not found")

        session = session_res.data
        platform = session["platform"]
        external_id = session["external_id"]  # Instagram ID or Bluesky DID

        # 2. Select Tool
        if platform == "instagram":
            tool = InstagramTool()
            # The tool itself handles logging to DB now
            res = await tool.execute(
                "send_dm", {"recipient_id": external_id, "text": req.text}
            )

            if res.get("status") == "error":
                raise HTTPException(500, f"Instagram Error: {res.get('message')}")

            return res

        elif platform == "bluesky":
            tool = BlueskyTool()

            # 1. Fetch convo_id from session metadata
            convo_id = session.get("metadata", {}).get("convo_id")

            if not convo_id:
                # If metadata is missing, we can try to find the convo by other user's handle?
                # For now, if it's missing, it's an error or we need to look it up.
                # But sync should have populated it.
                raise HTTPException(400, "Missing convo_id in session metadata")

            res = await tool.execute(
                "send_dm", {"convo_id": convo_id, "text": req.text}
            )

            # 2. Manually sync to DB for Bluesky
            if res.get("status") == "success":
                supabase.table("unified_messages").insert(
                    {
                        "session_id": req.session_id,
                        "platform": "bluesky",
                        "direction": "outbound",
                        "content": req.text,
                        "sender_handle": "AI Assistant",
                        "status": "sent",
                        "external_id": res.get("id"),  # DM message ID
                    }
                ).execute()

            return res

        elif platform == "pixelfed":
            tool = PixelfedTool()
            in_reply_to_id = None

            if req.reply_to_id:
                msg_res = (
                    supabase.table("unified_messages")
                    .select("external_id")
                    .eq("id", req.reply_to_id)
                    .single()
                    .execute()
                )
                if msg_res.data:
                    in_reply_to_id = msg_res.data["external_id"]

            if not in_reply_to_id:
                # Fallback to latest inbound
                last_inbound = (
                    supabase.table("unified_messages")
                    .select("external_id")
                    .eq("session_id", req.session_id)
                    .eq("direction", "inbound")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                in_reply_to_id = (
                    last_inbound.data[0]["external_id"] if last_inbound.data else None
                )

            res = await tool.execute(
                "post_reply", {"in_reply_to_id": in_reply_to_id, "text": req.text}
            )

            if res.get("status") == "success":
                supabase.table("unified_messages").insert(
                    {
                        "session_id": req.session_id,
                        "platform": "pixelfed",
                        "direction": "outbound",
                        "content": req.text,
                        "sender_handle": "AI Assistant",
                        "status": "sent",
                        "external_id": str(res.get("data", {}).get("id")),
                    }
                ).execute()

            return res

        else:
            raise HTTPException(
                400, f"Platform {platform} not supported for manual reply"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
