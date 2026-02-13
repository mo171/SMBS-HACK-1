from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class NodeParams(BaseModel):
    """Flexible parameters for workflow nodes. Can contain any key-value pairs."""

    model_config = ConfigDict(extra="allow")


class NodeData(BaseModel):
    service: str
    task: str
    # Use a concrete dict for params with default automation values
    params: Dict[str, Any] = Field(default_factory=dict)

    # Optional fields for better organization
    label: Optional[str] = None
    description: Optional[str] = None


class WorkflowNode(BaseModel):
    id: str
    type: str = "action"  # Default type
    data: NodeData
    # React Flow MUST have position
    position: Dict[str, int] = Field(default={"x": 250, "y": 250})


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "smoothstep"  # Default edge type


class WorkflowBlueprint(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]

    # Optional metadata
    name: Optional[str] = None
    description: Optional[str] = None
    loop_seconds: Optional[int] = 0  # 0 means run once, >0 means loop every X seconds
