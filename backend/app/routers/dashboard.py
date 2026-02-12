from fastapi import APIRouter, HTTPException
from lib.supabase_lib import supabase
from services.action_service import action_service
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """FETCH overall stats for the dashboard"""
    try:
        # 1. Get Financial Stats from ActionService
        ledger = await action_service.get_overall_ledger()
        debtors = await action_service.get_all_debtors()

        if ledger.get("status") == "error":
            raise HTTPException(500, detail=ledger.get("message"))

        # 2. Get Engagement Stats (Message counts per day for last 7 days)
        # We query unified_messages and aggregate by day
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

        msg_res = (
            supabase.table("unified_messages")
            .select("created_at, platform")
            .gte("created_at", seven_days_ago)
            .execute()
        )

        # Basic aggregation logic
        engagement_data = []
        days_map = {}

        # Initialize days
        for i in range(7):
            date_str = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
            days_map[date_str] = {
                "date": date_str,
                "whatsapp": 0,
                "instagram": 0,
                "bluesky": 0,
                "pixelfed": 0,
            }

        for msg in msg_res.data:
            date_str = msg["created_at"][:10]
            platform = msg["platform"]
            if date_str in days_map:
                days_map[date_str][platform] = days_map[date_str].get(platform, 0) + 1

        engagement_data = sorted(days_map.values(), key=lambda x: x["date"])

        return {
            "status": "success",
            "data": {
                "financials": {
                    "total_billed": ledger.get("total_billed", 0),
                    "total_paid": ledger.get("total_paid", 0),
                    "balance_due": ledger.get("balance_due", 0),
                },
                "debtors_count": len(debtors.get("data", [])),
                "debtors": debtors.get("data", []),
                "engagement": engagement_data,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
