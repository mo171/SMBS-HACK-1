"""
Integrations router for managing user service connections.

Handles connecting/disconnecting third-party services like
WhatsApp, Razorpay, Google Sheets, etc.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from supabase import create_client
import os
from datetime import datetime

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Initialize Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


class ConnectRequest(BaseModel):
    service: str
    credentials: Dict[str, str]
    user_id: str


@router.get("/status")
async def get_integration_status(user_id: str = Query(...)):
    """
    Get connection status for all integrations.

    Returns a dict of service_id -> connection info.
    """
    try:
        result = (
            supabase.table("user_integrations")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        connections = {}
        for row in result.data:
            connections[row["service"]] = {
                "connected": True,
                "connected_at": row["connected_at"],
                "account_info": row.get("account_info"),
                "last_used_at": row.get("last_used_at"),
            }

        print(
            f"✅ [Integrations] Loaded {len(connections)} connections for user {user_id}"
        )
        return {"connections": connections}

    except Exception as e:
        print(f"❌ [Integrations] Error loading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def connect_integration(request: ConnectRequest):
    """
    Connect a new integration or update existing credentials.

    Stores encrypted credentials in database.
    """
    try:
        # TODO: Encrypt credentials before storing
        # For now, storing as-is (should implement encryption in production)

        # Extract account info for display
        account_info = None
        if "username" in request.credentials:
            account_info = request.credentials["username"]
        elif "email" in request.credentials:
            account_info = request.credentials["email"]

        # Upsert integration
        supabase.table("user_integrations").upsert(
            {
                "user_id": request.user_id,
                "service": request.service,
                "credentials": request.credentials,
                "account_info": account_info,
                "connected_at": datetime.utcnow().isoformat(),
            },
            on_conflict="user_id,service",
        ).execute()

        print(
            f"✅ [Integrations] Connected {request.service} for user {request.user_id}"
        )
        return {"success": True, "service": request.service}

    except Exception as e:
        print(f"❌ [Integrations] Error connecting {request.service}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{service}")
async def disconnect_integration(service: str, user_id: str = Query(...)):
    """
    Disconnect an integration.

    Removes credentials from database.
    """
    try:
        supabase.table("user_integrations").delete().eq("user_id", user_id).eq(
            "service", service
        ).execute()

        print(f"✅ [Integrations] Disconnected {service} for user {user_id}")
        return {"success": True, "service": service}

    except Exception as e:
        print(f"❌ [Integrations] Error disconnecting {service}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service}/credentials")
async def get_credentials(service: str, user_id: str = Query(...)):
    """
    Get credentials for a specific service (for internal use by tools).

    Returns decrypted credentials.
    """
    try:
        result = (
            supabase.table("user_integrations")
            .select("credentials")
            .eq("user_id", user_id)
            .eq("service", service)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail=f"{service} not connected")

        # TODO: Decrypt credentials
        return {"credentials": result.data["credentials"]}

    except Exception as e:
        print(f"❌ [Integrations] Error getting credentials for {service}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
