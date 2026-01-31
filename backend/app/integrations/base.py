from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @property
    @abstractmethod
    def service_name(self) -> str:
        """The name of the service (e.g., 'whatsapp')"""
        pass

    @abstractmethod
    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main entry point for the engine.
        Every tool must implement this to handle its own tasks.
        """
        pass