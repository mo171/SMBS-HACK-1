import re
from typing import Any, Dict, Union


def resolve_variables(text: str, context: Dict[str, Any]) -> str:
    """
    Highly efficient variable resolver using a single regex pass.
    Supports deep nested paths: trigger_data.payload.payment.entity.amount
    """
    pattern = r"\{\{(.*?)\}\}"

    def get_value_from_path(path: str, data: Dict[str, Any]) -> Any:
        keys = path.strip().split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None  # Path doesn't exist
        return current

    def replace(match):
        path = match.group(1)
        value = get_value_from_path(path, context)

        if value is None:
            return f"[{path} not found]"  # Useful for debugging during dev

        # Handle decimal/float formatting (common for payments)
        if isinstance(value, float):
            return f"{value:.2f}"

        return str(value)

    return re.sub(pattern, replace, text)
