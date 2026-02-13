"""
Database Tool for querying Supabase tables in workflows.

Allows workflows to query user data and use results in automation.
Example: Query unpaid users, then send reminders.
"""

from supabase import create_client
import os
from typing import Dict, Any, List, Optional


class DatabaseTool:
    def __init__(self):
        """Initialize Supabase client for database queries."""
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        )
        print("✅ [DatabaseTool] Initialized")

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

        Example:
            results = await query_table(
                table="users",
                filters={"payment_status": "unpaid"},
                select="name, email, phone, amount_due"
            )
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


# Export for tool registry
__all__ = ["DatabaseTool"]
