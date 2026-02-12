from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from lib.supabase_lib import supabase
from integrations.instagram_tool import InstagramTool
from integrations.bluesky_tool import BlueskyTool

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


class SendMessageRequest(BaseModel):
    session_id: str
    text: str


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
            # Fallback: Just post to timeline mentioning them since we don't have thread context
            # Or reply if external_id happens to be a DID we can use?
            # Bluesky needs a full "reply_to" object.
            # Simplified: just create a new post tagging them.
            # Convert DID to handle if possible? external_id stores what?

            # Assuming external_id is a handle or DID.
            # Let's try to post a mention.
            post_text = f"@{external_id} {req.text}"
            res = await tool.execute("post_content", {"text": post_text})

            # Manually sync to DB for Bluesky since tool doesn't do it automatically here
            if res.get("status") == "success":
                supabase.table("unified_messages").insert(
                    {
                        "session_id": req.session_id,
                        "platform": "bluesky",
                        "direction": "outbound",
                        "content": req.text,
                        "sender_handle": "AI Assistant",
                        "status": "sent",
                    }
                ).execute()

            return res

        else:
            raise HTTPException(
                400, f"Platform {platform} not supported for manual reply"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
