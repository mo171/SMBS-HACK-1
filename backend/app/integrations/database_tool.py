"""
Database Tool for querying Supabase tables in workflows.

Allows workflows to query user data and use results in automation.
Example: Query unpaid users, then send reminders.
"""

from supabase import create_client
import os
from typing import Dict, Any, List, Optional
from .base import BaseTool


class DatabaseTool(BaseTool):
    def __init__(self):
        """Initialize Supabase client for database queries."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("⚠️ [DatabaseTool] Warning: Supabase credentials not set")
            self.supabase = None
        else:
            self.supabase = create_client(supabase_url, supabase_key)
            print("✅ [DatabaseTool] Initialized")

    @property
    def service_name(self) -> str:
        return "database"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database task based on task name."""
        print(f"\n🗄️ [DatabaseTool] Executing task: {task}")
        print(f"📊 [DatabaseTool] Parameters: {params}")

        if not self.supabase:
            return {
                "status": "error",
                "message": "Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY",
            }

        try:
            if task == "query_table":
                results = await self.query_table(
                    table=params.get("table"),
                    filters=params.get("filters"),
                    select=params.get("select", "*"),
                    limit=params.get("limit", 100),
                )
                return {"status": "success", "results": results, "count": len(results)}
            else:
                return {"status": "error", "message": f"Unknown task: {task}"}

        except Exception as e:
            print(f"❌ [DatabaseTool] Execution error: {e}")
            return {"status": "error", "message": str(e)}

    async def query_table(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        select: str = "*",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query a Supabase table with optional filters.

        Args:
            table: Table name to query
            filters: Dict of column:value filters (e.g., {"status": "unpaid"})
            select: Columns to select (default: "*")
            limit: Maximum rows to return (default: 100)

        Returns:
            List of matching rows
        """
        print(f"🔍 [DatabaseTool] Querying table: {table}")
        print(f"📊 [DatabaseTool] Filters: {filters}")
        print(f"📋 [DatabaseTool] Select: {select}")

        try:
            # Start query
            query = self.supabase.table(table).select(select)

            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            # Apply limit
            query = query.limit(limit)

            # Execute
            result = query.execute()

            print(f"✅ [DatabaseTool] Found {len(result.data)} rows")
            return result.data

        except Exception as e:
            print(f"❌ [DatabaseTool] Query error: {e}")
            raise Exception(f"Database query failed: {str(e)}")
