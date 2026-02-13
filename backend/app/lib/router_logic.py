import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def evaluate_condition(variable_value: Any, operator: str, target_value: Any) -> bool:
    """
    Evaluates a single condition: variable_value [operator] target_value
    Supported operators: ==, !=, >, <, >=, <=, contains, matches
    """
    try:
        # Normalize types for comparison
        if isinstance(target_value, (int, float)) and isinstance(
            variable_value, (str, int, float)
        ):
            try:
                variable_value = float(variable_value)
                target_value = float(target_value)
            except ValueError:
                pass  # Keep as original types if conversion fails

        if operator == "==":
            return variable_value == target_value
        elif operator == "!=":
            return variable_value != target_value
        elif operator == ">":
            return variable_value > target_value
        elif operator == "<":
            return variable_value < target_value
        elif operator == ">=":
            return variable_value >= target_value
        elif operator == "<=":
            return variable_value <= target_value
        elif operator == "contains":
            return str(target_value).lower() in str(variable_value).lower()
        elif operator == "matches":
            return bool(re.search(str(target_value), str(variable_value)))
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False

    except Exception as e:
        logger.error(
            f"Error checking condition {variable_value} {operator} {target_value}: {e}"
        )
        return False


def find_next_step(routes: List[Dict], context_data: Dict) -> str:
    """
    Evaluates a list of routes and returns the next_node_id for the first matching route.
    Each route should look like:
    {
        "condition": {
            "variable": "{{sentiment}}",
            "operator": "==",
            "value": "negative"
        },
        "next_node_id": "step_slack_alert"
    }

    Returns 'default_next_node_id' if no conditions match (if provided in routes as a fallback).
    """
    from lib.variable_resolver import resolve_variables

    for route in routes:
        # Check if this is a default/fallback route (no condition)
        if "condition" not in route or not route["condition"]:
            return route.get("next_node_id")

        condition = route["condition"]
        raw_variable = condition.get("variable")
        operator = condition.get("operator")
        target_value = condition.get("value")

        # Resolve the variable from context (e.g., "{{sentiment}}" -> "negative")
        resolved_variable = resolve_variables(raw_variable, context_data)

        if evaluate_condition(resolved_variable, operator, target_value):
            return route.get("next_node_id")

    return None
