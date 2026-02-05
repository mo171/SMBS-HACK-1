import asyncio
from typing import Any, Dict
from .base import BaseTool


class TimerTool(BaseTool):
    @property
    def service_name(self) -> str:
        return "timer"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        duration = params.get("duration", 2)  # Default 2 seconds

        print(f"⏳ [TimerTool] Sleeping for {duration} seconds...")
        await asyncio.sleep(float(duration))

        return {
            "status": "success",
            "message": f"Timer finished after {duration} seconds",
            "duration": duration,
        }
